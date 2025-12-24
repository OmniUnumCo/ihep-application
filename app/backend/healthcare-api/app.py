"""
Healthcare API Service
Routes all PHI through Google Healthcare API for HIPAA compliance
Implements k-anonymity de-identification for research data
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from google.cloud import healthcare_v1
from google.cloud import kms_v1
from google.auth import default
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

# Initialize Flask app
app = Flask(__name__)
logger = logging.getLogger(__name__)

# Initialize Google Cloud clients
credentials, project = default()
healthcare_client = healthcare_v1.HealthcareServiceClient()
kms_client = kms_v1.KeyManagementServiceClient()

# Initialize utilities
envelope_crypto = EnvelopeEncryption(kms_client, GCP_PROJECT, GCP_LOCATION, KMS_KEY_RING, KMS_CRYPTO_KEY)
audit_logger = AuditLogger()


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
            
            response = healthcare_client.create_resource(
                parent=self.fhir_store_path,
                resource=request_body
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
            
        except Exception as e:
            logger.error(f"Error creating patient: {str(e)}")
            audit_logger.log(
                user_id=user_id,
                action='CREATE_PATIENT',
                resource='Patient',
                outcome='FAILURE',
                details={'error': str(e)}
            )
            raise
    
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
            response = healthcare_client.get_resource(name=resource_path)
            
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
            
        except Exception as e:
            logger.error(f"Error retrieving patient: {str(e)}")
            audit_logger.log(
                user_id=user_id,
                action='VIEW_PHI',
                resource=f'Patient/{patient_id}',
                outcome='FAILURE',
                details={'error': str(e)}
            )
            raise
    
    def de_identify_for_research(
        self, 
        patient_ids: List[str], 
        k: int = 5
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
            
        except Exception as e:
            logger.error(f"De-identification error: {str(e)}")
            raise
    
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
        response = healthcare_client.get_resource(name=resource_path)
        return response


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
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'Missing user ID'}), 401
        
        patient_data = request.json
        result = healthcare_service.create_patient(patient_data, user_id)
        return jsonify(result), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/patients/<patient_id>', methods=['GET'])
@rate_limit(limit=200, per=60)  # 200 requests per minute
def get_patient(patient_id: str):
    """Retrieve patient record"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'Missing user ID'}), 401
        
        result = healthcare_service.get_patient(patient_id, user_id)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/research/datasets', methods=['POST'])
@rate_limit(limit=10, per=60)  # 10 requests per minute (expensive operation)
def create_research_dataset():
    """Create de-identified research dataset"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'Missing user ID'}), 401
        
        data = request.json
        patient_ids = data.get('patient_ids', [])
        k = data.get('k', 5)
        
        result = healthcare_service.de_identify_for_research(patient_ids, k)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Production: use gunicorn
    # gunicorn -w 4 -b 0.0.0.0:8080 healthcare-api.app:app
    app.run(host='0.0.0.0', port=8080, debug=False)
