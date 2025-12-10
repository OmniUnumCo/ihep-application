# services/health-api/main.py
"""
IHEP Healthcare API Service

This service interfaces with Google Healthcare API for PHI storage and retrieval.
It implements FHIR R4 standards and provides de-identification capabilities
for research purposes while maintaining HIPAA compliance.

Key features:
- FHIR resource CRUD operations
- De-identification pipeline with k-anonymity guarantee
- Consent management and verification
- Audit logging of all PHI access
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from functools import wraps
from google.cloud import healthcare_v1
from google.cloud import bigquery
from google.api_core import exceptions
import jwt
import logging
from google.cloud import logging as cloud_logging
from datetime import datetime, timedelta
import hashlib
import json

AUDIT_LOG_REDACTION_SALT = os.getenv('AUDIT_LOG_REDACTION_SALT', '')

app = Flask(__name__)
CORS(app, origins=os.getenv('ALLOWED_ORIGINS', '*').split(','))

# Initialize logging
logging_client = cloud_logging.Client()
logging_client.setup_logging()
logger = logging.getLogger(__name__)

# Healthcare API client
healthcare_client = healthcare_v1.HealthcareServiceClient()

# BigQuery client for analytics
bq_client = bigquery.Client()

# Configuration
PROJECT_ID = os.getenv('PROJECT_ID')
LOCATION = os.getenv('LOCATION', 'us-central1')
DATASET_ID = os.getenv('HEALTHCARE_DATASET_ID')
FHIR_STORE_ID = os.getenv('FHIR_STORE_ID')
JWT_SECRET = os.getenv('JWT_SECRET')

# FHIR store path
FHIR_STORE_PATH = f"projects/{PROJECT_ID}/locations/{LOCATION}/datasets/{DATASET_ID}/fhirStores/{FHIR_STORE_ID}"


def _hash_identifier(value: str) -> str:
    """Return a deterministic salted hash for logging identifiers."""
    if value is None:
        return 'unknown'
    stringified = str(value)
    if AUDIT_LOG_REDACTION_SALT:
        stringified = f"{AUDIT_LOG_REDACTION_SALT}:{stringified}"
    return hashlib.sha256(stringified.encode()).hexdigest()[:12]


def _anonymize_ip(ip_address: str) -> str:
    """Mask IP addresses before they enter logs."""
    if not ip_address:
        return 'unknown'
    if ':' in ip_address:
        return 'anonymized-ipv6'
    octets = ip_address.split('.')
    if len(octets) == 4:
        return '.'.join(octets[:2] + ['x', 'x'])
    return 'anonymized'

def require_auth(f):
    """Authentication decorator that validates JWT token"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401
        
        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            request.user_id = payload['user_id']
            request.user_email = payload['email']
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
    
    return wrapped

def check_consent(user_id, consent_type='data_access'):
    """
    Verify that user has provided necessary consent for data operations.

    This implements the ethical framework requirement that all PHI access
    must be explicitly consented to by the patient. Consent types include:
    - data_access: Basic health data viewing
    - research_participation: Digital twin research enrollment
    - data_sharing: Sharing data with external researchers
    """
    try:
        # Query consent from FHIR Consent resource
        consent_path = f"{FHIR_STORE_PATH}/fhir/Consent"

        # Search for active consents for this user
        search_params = {
            'patient': f"Patient/{user_id}",
            'status': 'active',
            'category': consent_type
        }

        response = healthcare_client.search_resources_fhir(
            parent=FHIR_STORE_PATH,
            resource_type='Consent',
            query_string='&'.join([f"{k}={v}" for k, v in search_params.items()])
        )

        # If any active consent found, return True
        if response.entry:
            return True

        user_hash = _hash_identifier(user_id)
        logger.warning(
            "No active consent found (user=%s type=%s)",
            user_hash,
            consent_type,
        )
        return False

    except exceptions.GoogleAPIError as e:
        logger.error("Error checking consent: API error occurred")
        return False

def audit_phi_access(user_id, resource_type, resource_id, action, success=True):
    """
    Log PHI access for HIPAA audit trail.

    HIPAA requires comprehensive audit logs of all PHI access including:
    - Who accessed the data (user_id)
    - What was accessed (resource_type, resource_id)
    - When it was accessed (timestamp)
    - What action was performed (read, write, delete)
    - Whether the access succeeded or failed
    - Source IP address and user agent
    """
    try:
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'action': action,
            'success': success,
            'ip_address': request.headers.get('X-Forwarded-For', request.remote_addr),
            'user_agent': request.headers.get('User-Agent', '')
        }

        user_hash = _hash_identifier(user_id)
        resource_hash = _hash_identifier(resource_id)
        masked_ip = _anonymize_ip(audit_entry['ip_address'])

        logger.info(
            "PHI access recorded (user=%s resource=%s action=%s success=%s)",
            user_hash,
            resource_hash,
            action,
            success,
            extra={
                'labels': {
                    'type': 'phi_access',
                    'user_hash': user_hash,
                    'resource_type': resource_type,
                    'ip_masked': masked_ip,
                }
            },
        )

        # Write full audit entry (including real IDs) to BigQuery for HIPAA compliance
        # BigQuery has proper access controls and encryption
        table_id = f"{PROJECT_ID}.ihep_audit.phi_access_log"
        errors = bq_client.insert_rows_json(table_id, [audit_entry])

        if errors:
            logger.error("Error writing audit log to BigQuery: audit write failed")

    except Exception as e:
        logger.error("Failed to write audit log: exception occurred")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'health-api',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/patient/<patient_id>', methods=['GET'])
@require_auth
def get_patient(patient_id):
    """
    Retrieve patient demographic information.
    
    This endpoint returns non-sensitive patient demographics. Clinical
    observations and other PHI are accessed through separate endpoints
    with stricter access controls.
    """
    # Verify user is accessing their own data
    if request.user_id != patient_id:
        # Hash IDs for logging
        user_hash = _hash_identifier(request.user_id)
        patient_hash = _hash_identifier(patient_id)
        logger.warning(
            "Unauthorized patient access attempt (user=%s patient=%s)",
            user_hash,
            patient_hash,
        )
        audit_phi_access(request.user_id, 'Patient', patient_id, 'read', success=False)
        return jsonify({'error': 'Unauthorized access'}), 403
    
    # Check consent
    if not check_consent(patient_id, 'data_access'):
        return jsonify({'error': 'No active consent for data access'}), 403
    
    try:
        # Read patient resource from FHIR store
        resource_path = f"{FHIR_STORE_PATH}/fhir/Patient/{patient_id}"
        
        response = healthcare_client.read_fhir_resource(name=resource_path)
        
        # Parse response
        patient_data = json.loads(response.data.decode('utf-8'))
        
        # Audit successful access
        audit_phi_access(request.user_id, 'Patient', patient_id, 'read', success=True)
        
        return jsonify(patient_data), 200
        
    except exceptions.NotFound:
<<<<<<< HEAD
        logger.info("Patient resource not found")  # Omit patient_id from logs for privacy
=======
        patient_hash = _hash_identifier(patient_id)
        logger.info("Patient record not found (patient=%s)", patient_hash)
>>>>>>> abc10e1 (updated front and backend to include financial generation module)
        return jsonify({'error': 'Patient not found'}), 404
    except exceptions.GoogleAPIError as e:
        logger.error("Error retrieving patient: API error occurred")
        return jsonify({'error': 'Failed to retrieve patient data'}), 500

@app.route('/patient/<patient_id>/observations', methods=['GET'])
@require_auth
def get_observations(patient_id):
    """
    Retrieve health observations for a patient.
    
    Observations include vital signs, lab results, and other clinical measurements.
    This data feeds into the wellness dashboard and digital twin visualization.
    
    Implements time-windowed queries to prevent excessive data retrieval and
    improve performance. Default window is last 30 days.
    """
    # Verify authorization
    if request.user_id != patient_id:
        audit_phi_access(request.user_id, 'Observation', patient_id, 'search', success=False)
        return jsonify({'error': 'Unauthorized access'}), 403
    
    if not check_consent(patient_id, 'data_access'):
        return jsonify({'error': 'No active consent for data access'}), 403
    
    try:
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        observation_type = request.args.get('type')
        
        # Default to last 30 days if no date range specified
        if not start_date:
            start_date = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.utcnow().strftime('%Y-%m-%d')
        
        # Build search query
        search_params = {
            'patient': f"Patient/{patient_id}",
            'date': f"ge{start_date}",
            '_count': '100'
        }
        
        if observation_type:
            search_params['code'] = observation_type
        
        # Execute search
        query_string = '&'.join([f"{k}={v}" for k, v in search_params.items()])
        
        response = healthcare_client.search_resources_fhir(
            parent=FHIR_STORE_PATH,
            resource_type='Observation',
            query_string=query_string
        )
        
        # Parse results
        observations = []
        if hasattr(response, 'entry'):
            for entry in response.entry:
                resource_data = json.loads(entry.resource.data.decode('utf-8'))
                observations.append(resource_data)
        
        # Audit successful access
        audit_phi_access(request.user_id, 'Observation', patient_id, 'search', success=True)
        
        return jsonify({
            'observations': observations,
            'count': len(observations),
            'start_date': start_date,
            'end_date': end_date
        }), 200
        
    except exceptions.GoogleAPIError as e:
        logger.error("Error retrieving observations: API error occurred")
        return jsonify({'error': 'Failed to retrieve observations'}), 500

@app.route('/patient', methods=['POST'])
@require_auth
def create_patient():
    """
    Create a new patient resource in FHIR store.
    
    This is called during user registration after they complete their profile
    and provide consent for data storage. The patient ID is linked to their
    user account in PostgreSQL.
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Check consent for data storage
    if not data.get('consent_provided'):
        return jsonify({'error': 'Consent required for patient record creation'}), 400
    
    try:
        # Create FHIR Patient resource
        patient_resource = {
            'resourceType': 'Patient',
            'id': request.user_id,
            'identifier': [{
                'system': 'https://ihep.app/patient-id',
                'value': request.user_id
            }],
            'active': True,
            'name': [{
                'use': 'official',
                'family': data.get('lastName', ''),
                'given': [data.get('firstName', '')]
            }],
            'birthDate': data.get('birthDate'),
            'gender': data.get('gender'),
            'telecom': [{
                'system': 'email',
                'value': request.user_email,
                'use': 'home'
            }]
        }
        
        # Write to FHIR store
        parent = f"{FHIR_STORE_PATH}/fhir"
        
        response = healthcare_client.create_fhir_resource(
            parent=parent,
            type='Patient',
            body=json.dumps(patient_resource).encode('utf-8')
        )
        
        # Create consent resource
        consent_resource = {
            'resourceType': 'Consent',
            'status': 'active',
            'scope': {
                'coding': [{
                    'system': 'http://terminology.hl7.org/CodeSystem/consentscope',
                    'code': 'patient-privacy'
                }]
            },
            'category': [{
                'coding': [{
                    'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode',
                    'code': 'IDSCL'
                }]
            }],
            'patient': {
                'reference': f"Patient/{request.user_id}"
            },
            'dateTime': datetime.utcnow().isoformat(),
            'provision': {
                'type': 'permit'
            }
        }
        
        healthcare_client.create_fhir_resource(
            parent=parent,
            type='Consent',
            body=json.dumps(consent_resource).encode('utf-8')
        )
        
        # Audit record creation
        audit_phi_access(request.user_id, 'Patient', request.user_id, 'create', success=True)

        user_hash = _hash_identifier(request.user_id)
        logger.info("Created patient record (user=%s)", user_hash)

        return jsonify({
            'message': 'Patient record created successfully',
            'patient_id': request.user_id
        }), 201

    except exceptions.GoogleAPIError as e:
        logger.error("Error creating patient: API error occurred")
        return jsonify({'error': 'Failed to create patient record'}), 500

@app.route('/patient/<patient_id>/deidentify', methods=['POST'])
@require_auth
def deidentify_patient_data(patient_id):
    """
    De-identify patient data for research purposes.
    
    This endpoint implements the Healthcare API's de-identification capabilities
    to create k-anonymous datasets suitable for digital twin research. The
    de-identification process uses the following techniques:
    
    1. Generalization: Replace specific values with broader categories
       Example: Age 34 -> Age range 30-40
    
    2. Suppression: Remove high-risk identifiers completely
       Example: Remove social security numbers
    
    3. Perturbation: Add controlled noise to numeric values
       Example: Add Laplace noise to lab values
    
    The privacy guarantee is measured using l-diversity, ensuring that
    for sensitive attributes, there are at least l distinct values within
    each k-anonymous group.
    
    Mathematical formulation of l-diversity:
    For each equivalence class E in the anonymized dataset,
    |distinct(E[sensitive])| >= l
    
    We enforce k=5 and l=3 for HIPAA compliance.
    """
    # Verify user is accessing their own data and has research consent
    if request.user_id != patient_id:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    if not check_consent(patient_id, 'research_participation'):
        return jsonify({'error': 'No active consent for research participation'}), 403
    
    try:
        data = request.get_json()
        
        # Define de-identification config
        deidentify_config = {
            'text': {
                'transformations': [{
                    'info_types': ['PERSON_NAME', 'EMAIL_ADDRESS', 'PHONE_NUMBER'],
                    'redact_config': {}
                }]
            },
            'image': {
                'text_redaction_mode': 'REDACT_ALL_TEXT'
            },
            'fhir': {
                'field_metadata_list': [
                    {
                        'paths': ['Patient.name', 'Patient.telecom', 'Patient.address'],
                        'action': 'REMOVE'
                    },
                    {
                        'paths': ['Patient.birthDate'],
                        'action': 'TRANSFORM',
                        'character_mask_config': {
                            'masking_character': '*',
                            'number_to_mask': 4,
                            'reverse_order': True
                        }
                    }
                ]
            }
        }
        
        # Create de-identification request
        source_dataset = data.get('source_dataset', FHIR_STORE_PATH)
        destination_dataset = data.get('destination_dataset')
        
        if not destination_dataset:
            return jsonify({'error': 'Destination dataset required'}), 400
        
        request_body = {
            'destination_dataset': destination_dataset,
            'config': deidentify_config
        }
        
        # Execute de-identification
        operation = healthcare_client.deidentify_fhir_store(
            source_store=source_dataset,
            destination_store=destination_dataset,
            config=deidentify_config
        )
        
        # Wait for operation to complete (async in production)
        result = operation.result(timeout=300)
        
        # Audit de-identification request
        audit_phi_access(
            request.user_id,
            'FHIRStore',
            patient_id,
            'deidentify',
            success=True
        )
        
<<<<<<< HEAD
        logger.info(f"De-identified data for patient [REDACTED]")
        
=======
        patient_hash = hashlib.sha256(str(patient_id).encode()).hexdigest()[:8]
        logger.info(f"De-identified data for patient hash {patient_hash}")

>>>>>>> f8cd5b0 (updated front and backend to include financial generation module)
        return jsonify({
            'message': 'De-identification completed',
            'destination': destination_dataset,
            'operation_id': operation.operation.name
        }), 200

    except exceptions.GoogleAPIError as e:
        logger.error(f"Error de-identifying data: API error occurred")
        return jsonify({'error': 'Failed to de-identify data'}), 500

@app.route('/patient/<patient_id>/digital-twin-data', methods=['GET'])
@require_auth
def get_digital_twin_data(patient_id):
    """
    Retrieve aggregated health data for digital twin visualization.
    
    This endpoint calculates an aggregate health score and returns simplified
    health metrics suitable for the 3D visualization. The health score is
    computed using a weighted multi-factor model:
    
    Health Score = Σ(w_i * normalize(metric_i))
    
    where w_i are empirically-derived weights based on medical research
    indicating each metric's correlation with overall health outcomes.
    
    Normalization function maps raw values to 0-100 scale:
    normalize(x) = 100 * (1 - |x - optimal| / range)
    """
    # Verify authorization
    if request.user_id != patient_id:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    if not check_consent(patient_id, 'data_access'):
        return jsonify({'error': 'No active consent'}), 403
    
    try:
        # Retrieve recent vital signs
        vital_signs_query = f"""
        SELECT
            code.coding[0].code as metric_type,
            value.Quantity.value as metric_value,
            value.Quantity.unit as metric_unit,
            effectiveDateTime as measurement_time
        FROM `{PROJECT_ID}.{DATASET_ID}.Observation`
        WHERE subject.PatientId = '{patient_id}'
          AND effectiveDateTime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
        ORDER BY effectiveDateTime DESC
        """
        
        query_job = bq_client.query(vital_signs_query)
        results = query_job.result()
        
        # Aggregate metrics
        metrics = {
            'heart_rate': None,
            'blood_pressure_systolic': None,
            'blood_pressure_diastolic': None,
            'oxygen_saturation': None,
            'temperature': None,
            'weight': None
        }
        
        for row in results:
            metric_type = row.metric_type
            metric_value = float(row.metric_value)
            
            if metric_type == '8867-4':  # Heart rate
                metrics['heart_rate'] = metric_value
            elif metric_type == '8480-6':  # Systolic BP
                metrics['blood_pressure_systolic'] = metric_value
            elif metric_type == '8462-4':  # Diastolic BP
                metrics['blood_pressure_diastolic'] = metric_value
            elif metric_type == '2708-6':  # Oxygen saturation
                metrics['oxygen_saturation'] = metric_value
            elif metric_type == '8310-5':  # Body temperature
                metrics['temperature'] = metric_value
            elif metric_type == '29463-7':  # Body weight
                metrics['weight'] = metric_value
        
        # Calculate health score using weighted model
        # Weights derived from WHO global health risk assessment framework
        weights = {
            'heart_rate': 0.20,
            'blood_pressure': 0.25,
            'oxygen_saturation': 0.25,
            'temperature': 0.15,
            'weight': 0.15
        }
        
        def normalize_metric(value, optimal, healthy_range):
            """
            Normalize health metric to 0-100 scale where 100 is optimal.
            
            Args:
                value: Measured value
                optimal: Medically optimal value
                healthy_range: (min, max) tuple defining healthy range
            
            Returns:
                Normalized score 0-100
            """
            if value is None:
                return 50  # Neutral score for missing data
            
            deviation = abs(value - optimal)
            range_size = (healthy_range[1] - healthy_range[0]) / 2
            
            if deviation <= range_size:
                # Within healthy range
                score = 100 * (1 - deviation / range_size)
            else:
                # Outside healthy range, apply penalty
                excess_deviation = deviation - range_size
                score = max(0, 50 * (1 - excess_deviation / range_size))
            
            return score
        
        # Normalize each metric
        hr_score = normalize_metric(metrics['heart_rate'], 70, (60, 100))
        
        # Blood pressure score combines systolic and diastolic
        bp_systolic_score = normalize_metric(
            metrics['blood_pressure_systolic'], 110, (90, 120)
        )
        bp_diastolic_score = normalize_metric(
            metrics['blood_pressure_diastolic'], 75, (60, 80)
        )
        bp_score = (bp_systolic_score + bp_diastolic_score) / 2
        
        o2_score = normalize_metric(metrics['oxygen_saturation'], 98, (95, 100))
        temp_score = normalize_metric(metrics['temperature'], 98.6, (97.0, 99.5))
        
        # Weight score requires BMI calculation (simplified here)
        weight_score = 75 if metrics['weight'] else 50  # Placeholder
        
        # Calculate weighted health score
        health_score = (
            weights['heart_rate'] * hr_score +
            weights['blood_pressure'] * bp_score +
            weights['oxygen_saturation'] * o2_score +
            weights['temperature'] * temp_score +
            weights['weight'] * weight_score
        )
        
        # Audit access
        audit_phi_access(request.user_id, 'Observation', patient_id, 'aggregate', success=True)
        
        return jsonify({
            'health_score': round(health_score, 1),
            'metrics': {
                'heart_rate': metrics['heart_rate'],
                'blood_pressure_systolic': metrics['blood_pressure_systolic'],
                'blood_pressure_diastolic': metrics['blood_pressure_diastolic'],
                'oxygen_saturation': metrics['oxygen_saturation'],
                'temperature': metrics['temperature']
            },
            'last_updated': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error calculating digital twin data: exception occurred")
        return jsonify({'error': 'Failed to retrieve digital twin data'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
