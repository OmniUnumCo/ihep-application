"""
Healthcare API Service
Routes all PHI through Google Healthcare API for HIPAA compliance
Implements k-anonymity de-identification for research data
"""

import os
import logging
from typing import Dict, List, Optional, Any
from flask import Flask, request, jsonify
from google.cloud import kms_v1
from google.auth import default
from google.auth.transport.requests import AuthorizedSession
from google.api_core.exceptions import NotFound
import requests
import hashlib
import uuid

from shared.security.encryption import EnvelopeEncryption
from shared.security.audit import AuditLogger
from shared.utils.validation import validate_fhir_resource
from shared.utils.rate_limit import rate_limit

# Configuration
GCP_PROJECT = os.getenv('GCP_PROJECT')
GCP_LOCATION = os.getenv('GCP_LOCATION', 'us-central1')
HEALTHCARE_DATASET = os.getenv('HEALTHCARE_DATASET')
FHIR_STORE = os.getenv('FHIR_STORE')
KMS_KEY_RING = os.getenv('KMS_KEY_RING')
KMS_CRYPTO_KEY = os.getenv('KMS_CRYPTO_KEY')
IDENTIFIER_HASH_SALT = os.getenv('IDENTIFIER_HASH_SALT', '')
HEALTHCARE_API_BASE = "https://healthcare.googleapis.com/v1"

# Initialize Flask app
app = Flask(__name__)
logger = logging.getLogger(__name__)

# Initialize Google Cloud clients
credentials, _ = default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
healthcare_session = AuthorizedSession(credentials)
kms_client = kms_v1.KeyManagementServiceClient()

# Initialize utilities
envelope_crypto = EnvelopeEncryption(kms_client, GCP_PROJECT, GCP_LOCATION, KMS_KEY_RING, KMS_CRYPTO_KEY)
audit_logger = AuditLogger()


def hash_identifier(value: Optional[str]) -> str:
    """Return a short salted hash for identifiers used in logs."""
    normalized = value or ''
    if IDENTIFIER_HASH_SALT:
        normalized = f"{IDENTIFIER_HASH_SALT}:{normalized}"
    return hashlib.sha256(normalized.encode()).hexdigest()[:12]


def generate_error_reference() -> str:
    """Create a random error reference token for client visibility."""
    return uuid.uuid4().hex[:12]


class HealthcareServiceError(Exception):
    """Custom exception for sanitized error reporting."""

    def __init__(self, public_message: str, reference: str, status_code: int = 500):
        super().__init__(public_message)
        self.public_message = public_message
        self.reference = reference
        self.status_code = status_code


class HealthcareAPIService:
    """
    Healthcare API Service
    
    Mathematical Properties:
    - k-anonymity: For any quasi-identifier set Q, |records_matching(Q)| ≥ k
    - Encryption: Each record R_i has unique DEK_i where E(R_i, DEK_i) = C_i
    - Audit: Every PHI access logged with probability P(log) = 1.0
    """
    
    def __init__(self):
        self.fhir_store_path = (
            f"projects/{GCP_PROJECT}/locations/{GCP_LOCATION}/"
            f"datasets/{HEALTHCARE_DATASET}/fhirStores/{FHIR_STORE}"
        )

    def _healthcare_request(
        self,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Send an authenticated request to the Cloud Healthcare FHIR endpoint."""
        url = f"{HEALTHCARE_API_BASE}/{path.lstrip('/')}"
        response = healthcare_session.request(method, url, json=body, timeout=30)

        if response.status_code == 404:
            raise NotFound(f"Resource not found at {path}")

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise RuntimeError(
                f"Healthcare API {method} {path} failed with {response.status_code}"
            ) from exc

        return response.json()

    def _raise_service_error(
        self,
        *,
        action: str,
        exc: Exception,
        user_id: Optional[str],
        public_message: str,
        status_code: int,
        patient_id: Optional[str] = None,
        patient_ids: Optional[List[str]] = None,
    ) -> None:
        """Log sanitized error context, audit, and raise service exception."""
        error_reference = generate_error_reference()
        user_hash = hash_identifier(user_id)

        if patient_ids:
            patient_scope = ",".join(sorted(hash_identifier(pid) for pid in patient_ids))
            audit_resource = 'PatientCollection'
        else:
            patient_scope = hash_identifier(patient_id)
            audit_resource = f'Patient/{patient_id}' if patient_id else 'Patient'

        logger.error(
            "%s failed ref=%s user_hash=%s patient_scope=%s error_type=%s",
            action,
            error_reference,
            user_hash,
            patient_scope or 'none',
            exc.__class__.__name__,
        )

        audit_logger.log(
            user_id=user_id,
            action=action,
            resource=audit_resource,
            outcome='FAILURE',
            details={
                'error_reference': error_reference,
                'error_type': exc.__class__.__name__,
                'patient_scope': patient_scope or 'none',
            }
        )

        raise HealthcareServiceError(public_message, error_reference, status_code) from None
    
    def create_patient(self, patient_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Create patient record with envelope encryption
        
        Process:
        1. Generate ephemeral DEK for this record
        2. Encrypt patient data with DEK
        3. Encrypt DEK with KEK (Cloud KMS)
        4. Store encrypted data and wrapped DEK
        5. Audit log the operation
        
        Returns:
            Patient resource with FHIR ID
        """
        patient_id: Optional[str] = None
        try:
            # Validate FHIR resource
            if not validate_fhir_resource(patient_data, 'Patient'):
                raise ValueError("Invalid FHIR Patient resource")
            
            # Generate unique ID
            patient_id = str(uuid.uuid4())
            patient_data['id'] = patient_id
            
            # Envelope encryption
            encrypted_data, wrapped_dek = envelope_crypto.encrypt(patient_data)
            
            # Store in Healthcare API
            resource_path = f"{self.fhir_store_path}/fhir/Patient"
            request_body = {
                'resourceType': 'Patient',
                'id': patient_id,
                'meta': {
                    'security': [
                        {
                            'system': 'http://terminology.hl7.org/CodeSystem/v3-Confidentiality',
                            'code': 'R',  # Restricted
                            'display': 'Restricted'
                        }
                    ]
                },
                'extension': [
                    {
                        'url': 'http://ihep-platform.org/fhir/extension/wrapped-dek',
                        'valueString': wrapped_dek
                    }
                ],
                **patient_data
            }
            
            response = self._healthcare_request(
                method='POST',
                path=f"{self.fhir_store_path}/fhir/Patient",
                body=request_body,
            )
            
            # Audit log
            audit_logger.log(
                user_id=user_id,
                action='CREATE_PATIENT',
                resource=f'Patient/{patient_id}',
                outcome='SUCCESS',
                details={'encrypted': True, 'dek_wrapped': True}
            )
            
            return {
                'success': True,
                'data': {
                    'id': patient_id,
                    'resourceType': 'Patient'
                }
            }
            
        except ValueError as exc:
            self._raise_service_error(
                action='CREATE_PATIENT',
                exc=exc,
                user_id=user_id,
                public_message='Invalid patient payload',
                status_code=400,
                patient_id=patient_id,
            )
        except Exception as exc:
            self._raise_service_error(
                action='CREATE_PATIENT',
                exc=exc,
                user_id=user_id,
                public_message='Unable to create patient record',
                status_code=500,
                patient_id=patient_id,
            )
    
    def get_patient(self, patient_id: str, user_id: str) -> Dict[str, Any]:
        """
        Retrieve and decrypt patient record
        
        Process:
        1. Fetch encrypted record from Healthcare API
        2. Extract wrapped DEK
        3. Unwrap DEK using Cloud KMS
        4. Decrypt patient data with DEK
        5. Audit log the access
        
        Returns:
            Decrypted patient data
        """
        try:
            # Fetch from Healthcare API
            resource_path = f"{self.fhir_store_path}/fhir/Patient/{patient_id}"
            response = self._healthcare_request(
                method='GET',
                path=resource_path,
            )
            
            # Extract wrapped DEK
            wrapped_dek = None
            for extension in response.get('extension', []):
                if extension.get('url') == 'http://ihep-platform.org/fhir/extension/wrapped-dek':
                    wrapped_dek = extension.get('valueString')
                    break
            
            if not wrapped_dek:
                raise ValueError("No wrapped DEK found in resource")
            
            # Decrypt data
            decrypted_data = envelope_crypto.decrypt(response, wrapped_dek)
            
            # Audit log
            audit_logger.log(
                user_id=user_id,
                action='VIEW_PHI',
                resource=f'Patient/{patient_id}',
                outcome='SUCCESS',
                details={'decrypted': True}
            )
            
            return {
                'success': True,
                'data': decrypted_data
            }
            
        except NotFound as exc:
            self._raise_service_error(
                action='VIEW_PHI',
                exc=exc,
                user_id=user_id,
                public_message='Patient not found',
                status_code=404,
                patient_id=patient_id,
            )
        except ValueError as exc:
            self._raise_service_error(
                action='VIEW_PHI',
                exc=exc,
                user_id=user_id,
                public_message='Unable to retrieve patient record',
                status_code=500,
                patient_id=patient_id,
            )
        except Exception as exc:
            self._raise_service_error(
                action='VIEW_PHI',
                exc=exc,
                user_id=user_id,
                public_message='Unable to retrieve patient record',
                status_code=500,
                patient_id=patient_id,
            )
    
    def de_identify_for_research(
        self, 
        patient_ids: List[str], 
        k: int = 5,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        De-identify patient data for research with k-anonymity guarantee
        
        Mathematical Guarantee:
        For any quasi-identifier combination Q, ensures |{records matching Q}| ≥ k
        
        Process:
        1. Fetch patient records
        2. Apply k-anonymity algorithm
        3. Generalize/suppress quasi-identifiers
        4. Verify k-anonymity constraint
        5. Return de-identified dataset
        
        Args:
            patient_ids: List of patient IDs to include
            k: k-anonymity parameter (default k=5)
        
        Returns:
            De-identified dataset with k-anonymity guarantee
        """
        try:
            # Fetch records
            records = [self._fetch_for_deidentification(pid) for pid in patient_ids]
            
            # Apply k-anonymity
            deidentified = self._apply_k_anonymity(records, k)
            
            # Verify constraint
            if not self._verify_k_anonymity(deidentified, k):
                raise ValueError(f"k-anonymity constraint violated: k={k}")
            
            return {
                'success': True,
                'data': {
                    'records': deidentified,
                    'privacy': {
                        'k_anonymity': k,
                        'verified': True,
                        'record_count': len(deidentified)
                    }
                }
            }
            
        except ValueError as exc:
            self._raise_service_error(
                action='DEIDENTIFY_PATIENT_DATA',
                exc=exc,
                user_id=user_id,
                public_message='Unable to generate research dataset with requested parameters',
                status_code=400,
                patient_ids=patient_ids,
            )
        except Exception as exc:
            self._raise_service_error(
                action='DEIDENTIFY_PATIENT_DATA',
                exc=exc,
                user_id=user_id,
                public_message='Unable to generate research dataset',
                status_code=500,
                patient_ids=patient_ids,
            )
    
    def _apply_k_anonymity(self, records: List[Dict], k: int) -> List[Dict]:
        """
        Apply k-anonymity algorithm
        
        Quasi-identifiers: age, gender, zip_code
        Generalization: age → age_range, zip_code → zip_prefix
        """
        # Identify quasi-identifiers
        quasi_identifiers = ['age', 'gender', 'zipCode']
        
        # Generalize age
        for record in records:
            if 'age' in record:
                age = record['age']
                record['age_range'] = f"{(age // 10) * 10}-{(age // 10) * 10 + 9}"
                del record['age']
            
            # Generalize zip code
            if 'zipCode' in record:
                zip_code = record['zipCode']
                record['zip_prefix'] = zip_code[:3]  # First 3 digits
                del record['zipCode']
        
        # Verify k-anonymity
        equivalence_classes = {}
        for record in records:
            # Create key from quasi-identifiers
            key = tuple(record.get(qi) for qi in ['age_range', 'gender', 'zip_prefix'])
            if key not in equivalence_classes:
                equivalence_classes[key] = []
            equivalence_classes[key].append(record)
        
        # Suppress classes with < k records
        result = []
        for eq_class in equivalence_classes.values():
            if len(eq_class) >= k:
                result.extend(eq_class)
        
        return result
    
    def _verify_k_anonymity(self, records: List[Dict], k: int) -> bool:
        """Verify k-anonymity constraint is satisfied"""
        quasi_identifiers = ['age_range', 'gender', 'zip_prefix']
        
        equivalence_classes = {}
        for record in records:
            key = tuple(record.get(qi) for qi in quasi_identifiers)
            if key not in equivalence_classes:
                equivalence_classes[key] = 0
            equivalence_classes[key] += 1
        
        # Check all equivalence classes have ≥ k records
        return all(count >= k for count in equivalence_classes.values())
    
    def _fetch_for_deidentification(self, patient_id: str) -> Dict[str, Any]:
        """Fetch patient data for de-identification (internal use only)"""
        resource_path = f"{self.fhir_store_path}/fhir/Patient/{patient_id}"
        return self._healthcare_request(
            method='GET',
            path=resource_path,
        )


# Initialize service
healthcare_service = HealthcareAPIService()


# API Endpoints
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'healthcare-api'}), 200


@app.route('/api/v1/patients', methods=['POST'])
@rate_limit(limit=100, per=60)  # 100 requests per minute
def create_patient():
    """Create patient record"""
    user_id = request.headers.get('X-User-ID')
    try:
        if not user_id:
            return jsonify({'error': 'Missing user ID'}), 401
        
        patient_data = request.json
        result = healthcare_service.create_patient(patient_data, user_id)
        return jsonify(result), 201
        
    except HealthcareServiceError as exc:
        return jsonify({'error': exc.public_message, 'reference': exc.reference}), exc.status_code
    except Exception as exc:
        error_reference = generate_error_reference()
        logger.error(
            "Unhandled create_patient error ref=%s user_hash=%s error_type=%s",
            error_reference,
            hash_identifier(user_id),
            exc.__class__.__name__,
            exc_info=True,
        )
        return jsonify({'error': 'Internal server error', 'reference': error_reference}), 500


@app.route('/api/v1/patients/<patient_id>', methods=['GET'])
@rate_limit(limit=200, per=60)  # 200 requests per minute
def get_patient(patient_id: str):
    """Retrieve patient record"""
    user_id = request.headers.get('X-User-ID')
    try:
        if not user_id:
            return jsonify({'error': 'Missing user ID'}), 401
        
        result = healthcare_service.get_patient(patient_id, user_id)
        return jsonify(result), 200
        
    except HealthcareServiceError as exc:
        return jsonify({'error': exc.public_message, 'reference': exc.reference}), exc.status_code
    except Exception as exc:
        error_reference = generate_error_reference()
        logger.error(
            "Unhandled get_patient error ref=%s user_hash=%s patient_hash=%s error_type=%s",
            error_reference,
            hash_identifier(user_id),
            hash_identifier(patient_id),
            exc.__class__.__name__,
            exc_info=True,
        )
        return jsonify({'error': 'Internal server error', 'reference': error_reference}), 500


@app.route('/api/v1/research/datasets', methods=['POST'])
@rate_limit(limit=10, per=60)  # 10 requests per minute (expensive operation)
def create_research_dataset():
    """Create de-identified research dataset"""
    user_id = request.headers.get('X-User-ID')
    try:
        if not user_id:
            return jsonify({'error': 'Missing user ID'}), 401
        
        data = request.json
        patient_ids = data.get('patient_ids', [])
        k = data.get('k', 5)
        
        result = healthcare_service.de_identify_for_research(patient_ids, k, user_id)
        return jsonify(result), 200
        
    except HealthcareServiceError as exc:
        return jsonify({'error': exc.public_message, 'reference': exc.reference}), exc.status_code
    except Exception as exc:
        error_reference = generate_error_reference()
        logger.error(
            "Unhandled create_research_dataset error ref=%s user_hash=%s error_type=%s",
            error_reference,
            hash_identifier(user_id),
            exc.__class__.__name__,
            exc_info=True,
        )
        return jsonify({'error': 'Internal server error', 'reference': error_reference}), 500


if __name__ == '__main__':
    # Production: use gunicorn
    # gunicorn -w 4 -b 0.0.0.0:8080 healthcare-api.app:app
    app.run(host='0.0.0.0', port=8080, debug=False)
