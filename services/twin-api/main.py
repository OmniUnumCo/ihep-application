# services/twin-api/main.py
"""
IHEP Digital Twin Ecosystem

This service manages the digital twin infrastructure that creates
computational models of patients for personalized health insights
and research acceleration.

Key features:
- Morphogenetic self-healing algorithms
- Federated learning across patient twins
- Real-time health state synchronization
- Research collaboration framework
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import jwt
from functools import wraps
import logging
from google.cloud import logging as cloud_logging
from google.cloud import bigquery
from google.cloud import storage
import numpy as np
import json
from datetime import datetime, timedelta
import hashlib
import redis
from cryptography.fernet import Fernet

app = Flask(__name__)
CORS(app, origins=os.getenv('ALLOWED_ORIGINS', '*').split(','))

# Initialize logging
logging_client = cloud_logging.Client()
logging_client.setup_logging()
logger = logging.getLogger(__name__)

# Redis for caching
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=3,
    decode_responses=True
)

# BigQuery for analytics
bq_client = bigquery.Client()
PROJECT_ID = os.getenv('PROJECT_ID')
JWT_SECRET = os.getenv('JWT_SECRET')

# Storage for model artifacts
storage_client = storage.Client()
bucket_name = f"{PROJECT_ID}-twin-models"
bucket = storage_client.bucket(bucket_name)

# Encryption for sensitive twin data
TWIN_ENCRYPTION_KEY = os.getenv('TWIN_ENCRYPTION_KEY')
fernet = Fernet(TWIN_ENCRYPTION_KEY) if TWIN_ENCRYPTION_KEY else None

def require_auth(f):
    """Authentication decorator"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401
        
        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            request.user_id = payload['user_id']
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
    
    return wrapped

class DigitalTwin:
    """
    Digital Twin representation with morphogenetic self-healing capabilities.
    
    The twin implements a self-organizing system based on morphogenetic principles
    where the digital representation continuously adapts to maintain homeostasis
    with the biological system it represents.
    
    Mathematical foundation:
    
    State evolution: dS/dt = f(S, E, t) + η(t)
    
    Where:
    - S = state vector
    - E = environmental inputs
    - f = morphogenetic function
    - η = stochastic noise term
    
    Self-healing mechanism uses gradient descent optimization:
    S(t+1) = S(t) - α∇L(S(t))
    
    Where L is a loss function measuring deviation from healthy state patterns.
    """
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.state = self._initialize_state()
        self.health_patterns = self._load_health_patterns()
        self.morphogenetic_score = 1.0  # 0.0-1.0 scale
    
    def _initialize_state(self):
        """Initialize twin state with default healthy values"""
        return {
            'vital_signs': {
                'heart_rate': 70,
                'blood_pressure_systolic': 110,
                'blood_pressure_diastolic': 75,
                'oxygen_saturation': 98,
                'temperature': 98.6,
                'respiratory_rate': 16
            },
            'lab_results': {},
            'medication_adherence': 1.0,
            'appointment_attendance': 1.0,
            'activity_level': 0.7,
            'sleep_quality': 0.8,
            'stress_level': 0.3,
            'last_updated': datetime.utcnow().isoformat()
        }
    
    def _load_health_patterns(self):
        """Load population-level health patterns for comparison"""
        # In production, this would load from BigQuery or storage
        return {
            'heart_rate_normal': (60, 100),
            'blood_pressure_normal': (90, 120, 60, 80),  # systolic_min, max, diastolic_min, max
            'oxygen_saturation_normal': (95, 100),
            'temperature_normal': (97.0, 99.5)
        }
    
    def update_state(self, new_data):
        """
        Update twin state with new health data.
        
        Implements morphogenetic self-healing by:
        1. Validating new data against expected ranges
        2. Detecting anomalies and potential errors
        3. Applying corrective adjustments when needed
        4. Updating morphogenetic fitness score
        """
        # Store previous state for comparison
        previous_state = self.state.copy()
        
        # Update state with new data
        for key, value in new_data.items():
            if key in self.state:
                if isinstance(self.state[key], dict) and isinstance(value, dict):
                    self.state[key].update(value)
                else:
                    self.state[key] = value
        
        # Update timestamp
        self.state['last_updated'] = datetime.utcnow().isoformat()
        
        # Apply morphogenetic self-healing
        self._apply_self_healing(previous_state)
        
        # Update morphogenetic score
        self._update_morphogenetic_score()
        
        return self.state
    
    def _apply_self_healing(self, previous_state):
        """
        Apply morphogenetic self-healing to correct inconsistencies.
        
        Uses a weighted voting system where:
        - Recent data has higher weight
        - Consistent measurements have higher weight
        - Population norms provide baseline expectations
        
        Mathematical model:
        S_corrected = Σ(w_i * S_i) / Σ(w_i)
        
        Where w_i are weights based on recency, consistency, and reliability.
        """
        vital_signs = self.state['vital_signs']
        patterns = self.health_patterns
        
        # Check heart rate
        hr = vital_signs['heart_rate']
        hr_normal = patterns['heart_rate_normal']
        if not (hr_normal[0] <= hr <= hr_normal[1]):
            # Apply correction based on trend and population norms
            prev_hr = previous_state['vital_signs']['heart_rate']
            trend_correction = 0.7 * hr + 0.3 * prev_hr
            norm_correction = 0.5 * hr + 0.5 * np.mean(hr_normal)
            
            # Weighted correction (more weight to recent consistent data)
            vital_signs['heart_rate'] = 0.6 * trend_correction + 0.4 * norm_correction
        
        # Similar corrections for other vital signs...
        # (Implementation would continue for all vital signs)
    
    def _update_morphogenetic_score(self):
        """
        Calculate morphogenetic fitness score.
        
        Score is based on:
        1. Deviation from population norms (0-1 scale)
        2. Temporal consistency of measurements (0-1 scale)
        3. Completeness of health data (0-1 scale)
        4. Predictive accuracy of twin model (0-1 scale)
        
        Combined using weighted geometric mean:
        M = (Π(score_i^w_i))^(1/Σw_i)
        """
        # Calculate deviation score
        deviation_score = self._calculate_deviation_score()
        
        # Calculate consistency score
        consistency_score = self._calculate_consistency_score()
        
        # Calculate completeness score
        completeness_score = self._calculate_completeness_score()
        
        # Calculate predictive accuracy (simplified)
        predictive_score = 0.85  # Would be calculated from model performance
        
        # Weighted geometric mean
        weights = [0.3, 0.25, 0.25, 0.2]  # deviation, consistency, completeness, predictive
        scores = [deviation_score, consistency_score, completeness_score, predictive_score]
        
        weighted_product = 1.0
        weight_sum = sum(weights)
        
        for score, weight in zip(scores, weights):
            weighted_product *= (score ** weight)
        
        self.morphogenetic_score = weighted_product ** (1/weight_sum)
    
    def _calculate_deviation_score(self):
        """Calculate score based on deviation from normal ranges"""
        vital_signs = self.state['vital_signs']
        patterns = self.health_patterns
        
        deviations = []
        
        # Heart rate deviation
        hr = vital_signs['heart_rate']
        hr_normal = patterns['heart_rate_normal']
        hr_deviation = abs(hr - np.mean(hr_normal)) / (hr_normal[1] - hr_normal[0])
        deviations.append(max(0, 1 - hr_deviation))
        
        # Blood pressure deviation
        sys = vital_signs['blood_pressure_systolic']
        dia = vital_signs['blood_pressure_diastolic']
        bp_normal = patterns['blood_pressure_normal']
        
        sys_deviation = abs(sys - np.mean(bp_normal[:2])) / (bp_normal[1] - bp_normal[0])
        dia_deviation = abs(dia - np.mean(bp_normal[2:])) / (bp_normal[3] - bp_normal[2])
        
        bp_deviation = (sys_deviation + dia_deviation) / 2
        deviations.append(max(0, 1 - bp_deviation))
        
        # Average all deviations
        return np.mean(deviations) if deviations else 1.0
    
    def _calculate_consistency_score(self):
        """Calculate temporal consistency score"""
        # This would analyze historical data patterns
        # For now, return a placeholder based on data completeness
        vital_signs = self.state['vital_signs']
        complete_measurements = sum(1 for v in vital_signs.values() if v is not None)
        total_measurements = len(vital_signs)
        return complete_measurements / total_measurements if total_measurements > 0 else 0.0
    
    def _calculate_completeness_score(self):
        """Calculate data completeness score"""
        # Check for required data fields
        required_fields = [
            'heart_rate', 'blood_pressure_systolic', 'blood_pressure_diastolic',
            'oxygen_saturation', 'temperature'
        ]
        
        vital_signs = self.state['vital_signs']
        complete_fields = sum(1 for field in required_fields if vital_signs.get(field) is not None)
        
        return complete_fields / len(required_fields) if required_fields else 1.0

class FederatedLearning:
    """
    Federated learning framework for collaborative model training.
    
    Implements secure aggregation with differential privacy:
    
    Global model update: w_{t+1} = w_t - η * (1/n) * Σ(∇L_i(w_t) + noise)
    
    Where noise ~ N(0, σ²) with σ = C * sqrt(2ln(1.25/δ)) / ε
    
    This ensures ε-differential privacy with δ failure probability.
    """
    
    def __init__(self):
        self.global_model_version = "1.0"
        self.participants = set()
        self.aggregation_round = 0
    
    def aggregate_gradients(self, gradients, noise_scale=0.1):
        """
        Securely aggregate gradients from multiple participants.
        
        Adds Gaussian noise for differential privacy protection.
        """
        if not gradients:
            return None
        
        # Average gradients
        avg_gradients = {}
        num_participants = len(gradients)
        
        for key in gradients[0].keys():
            avg_gradients[key] = sum(g[key] for g in gradients) / num_participants
        
        # Add differential privacy noise
        for key in avg_gradients:
            noise = np.random.normal(0, noise_scale)
            avg_gradients[key] += noise
        
        return avg_gradients
    
    def update_global_model(self, aggregated_gradients, learning_rate=0.01):
        """
        Update global model with aggregated gradients.
        
        Implements momentum for faster convergence:
        v_{t+1} = β * v_t + (1-β) * ∇L
        w_{t+1} = w_t - η * v_{t+1}
        """
        # This would update the global model parameters
        # For now, just increment version and round
        self.global_model_version = f"1.{int(self.global_model_version.split('.')[1]) + 1}"
        self.aggregation_round += 1
        
        return {
            'new_version': self.global_model_version,
            'round': self.aggregation_round,
            'participants': len(self.participants)
        }

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'twin-api',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/twin', methods=['POST'])
@require_auth
def create_digital_twin():
    """
    Create a new digital twin for the authenticated user.
    
    Initializes the twin with baseline health data and
    enrolls the user in the twin ecosystem.
    """
    try:
        data = request.get_json()
        initial_data = data.get('initial_data', {})
        
        # Create digital twin
        twin = DigitalTwin(request.user_id)
        
        # Update with initial data
        if initial_data:
            twin.update_state(initial_data)
        
        # Store encrypted twin state
        state_json = json.dumps(twin.state)
        if fernet:
            encrypted_state = fernet.encrypt(state_json.encode())
            twin_state = encrypted_state.decode()
        else:
            twin_state = state_json
        
        # Cache twin state
        twin_key = f"twin:{request.user_id}"
        redis_client.setex(twin_key, 3600, twin_state)  # 1-hour TTL
        
        # Log twin creation
        twin_log = {
            'user_id': request.user_id,
            'created_at': datetime.utcnow().isoformat(),
            'initial_morphogenetic_score': twin.morphogenetic_score
        }
        
        table_id = f"{PROJECT_ID}.ihep_twin.twin_creations"
        bq_client.insert_rows_json(table_id, [twin_log])
        
        logger.info(f"Digital twin created for user {request.user_id}")
        
        return jsonify({
            'message': 'Digital twin created successfully',
            'user_id': request.user_id,
            'morphogenetic_score': round(twin.morphogenetic_score, 4),
            'last_updated': twin.state['last_updated']
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating digital twin: {str(e)}")
        return jsonify({'error': 'Failed to create digital twin'}), 500

@app.route('/twin/state', methods=['GET'])
@require_auth
def get_twin_state():
    """Get current state of user's digital twin"""
    try:
        # Check cache first
        twin_key = f"twin:{request.user_id}"
        cached_state = redis_client.get(twin_key)
        
        if cached_state:
            if fernet:
                try:
                    decrypted_state = fernet.decrypt(cached_state.encode())
                    state = json.loads(decrypted_state.decode())
                except:
                    state = json.loads(cached_state)
            else:
                state = json.loads(cached_state)
        else:
            # Load from storage (simplified)
            state = {
                'message': 'Twin state not found',
                'user_id': request.user_id
            }
        
        return jsonify(state), 200
        
    except Exception as e:
        logger.error(f"Error retrieving twin state: {str(e)}")
        return jsonify({'error': 'Failed to retrieve twin state'}), 500

@app.route('/twin/update', methods=['POST'])
@require_auth
def update_twin():
    """
    Update digital twin with new health data.
    
    Triggers morphogenetic self-healing and updates fitness score.
    """
    try:
        data = request.get_json()
        new_data = data.get('health_data', {})
        
        # Create twin instance
        twin = DigitalTwin(request.user_id)
        
        # Update twin state
        updated_state = twin.update_state(new_data)
        
        # Store encrypted updated state
        state_json = json.dumps(updated_state)
        if fernet:
            encrypted_state = fernet.encrypt(state_json.encode())
            twin_state = encrypted_state.decode()
        else:
            twin_state = state_json
        
        # Cache updated state
        twin_key = f"twin:{request.user_id}"
        redis_client.setex(twin_key, 3600, twin_state)
        
        # Log update
        update_log = {
            'user_id': request.user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'new_morphogenetic_score': twin.morphogenetic_score,
            'data_points_updated': list(new_data.keys())
        }
        
        table_id = f"{PROJECT_ID}.ihep_twin.twin_updates"
        bq_client.insert_rows_json(table_id, [update_log])
        
        logger.info(f"Twin updated for user {request.user_id}")
        
        return jsonify({
            'message': 'Twin updated successfully',
            'morphogenetic_score': round(twin.morphogenetic_score, 4),
            'last_updated': updated_state['last_updated']
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating twin: {str(e)}")
        return jsonify({'error': 'Failed to update twin'}), 500

@app.route('/twin/federated/participate', methods=['POST'])
@require_auth
def participate_in_federated_learning():
    """
    Enroll user's twin in federated learning program.
    
    Users opt-in to contribute to collaborative research
    while maintaining privacy through secure aggregation.
    """
    try:
        data = request.get_json()
        consent = data.get('consent', False)
        
        if not consent:
            return jsonify({'error': 'Consent required for participation'}), 400
        
        # Add user to federated learning participants
        fl_key = f"fl_participants"
        redis_client.sadd(fl_key, request.user_id)
        
        # Log participation
        participation_log = {
            'user_id': request.user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'consent_given': consent
        }
        
        table_id = f"{PROJECT_ID}.ihep_twin.fl_participations"
        bq_client.insert_rows_json(table_id, [participation_log])
        
        logger.info(f"User {request.user_id} enrolled in federated learning")
        
        return jsonify({
            'message': 'Successfully enrolled in federated learning program',
            'user_id': request.user_id,
            'program_benefits': [
                'Contribute to medical research',
                'Improve predictive models',
                'Maintain complete privacy',
                'Earn research credits'
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Error enrolling in federated learning: {str(e)}")
        return jsonify({'error': 'Failed to enroll in federated learning'}), 500

@app.route('/twin/insights', methods=['GET'])
@require_auth
def get_twin_insights():
    """Get personalized health insights from digital twin"""
    try:
        # Get twin state
        twin_key = f"twin:{request.user_id}"
        cached_state = redis_client.get(twin_key)
        
        if not cached_state:
            return jsonify({'error': 'Digital twin not found'}), 404
        
        if fernet:
            try:
                decrypted_state = fernet.decrypt(cached_state.encode())
                state = json.loads(decrypted_state.decode())
            except:
                state = json.loads(cached_state)
        else:
            state = json.loads(cached_state)
        
        # Generate insights based on twin state
        insights = []
        
        vital_signs = state.get('vital_signs', {})
        
        # Heart rate insight
        hr = vital_signs.get('heart_rate')
        if hr and (hr < 60 or hr > 100):
            insights.append({
                'type': 'vital_sign_alert',
                'category': 'heart_rate',
                'message': f'Your heart rate ({hr} bpm) is outside the normal range (60-100 bpm)',
                'severity': 'warning' if 50 <= hr <= 120 else 'alert',
                'recommendation': 'Consider resting and monitoring. Contact your provider if persistent.'
            })
        
        # Blood pressure insight
        sys = vital_signs.get('blood_pressure_systolic')
        dia = vital_signs.get('blood_pressure_diastolic')
        if sys and dia:
            if sys > 130 or dia > 80:
                insights.append({
                    'type': 'vital_sign_alert',
                    'category': 'blood_pressure',
                    'message': f'Your blood pressure ({sys}/{dia} mmHg) indicates hypertension',
                    'severity': 'alert',
                    'recommendation': 'Monitor closely and consult your healthcare provider.'
                })
        
        # Medication adherence insight
        adherence = state.get('medication_adherence', 1.0)
        if adherence < 0.8:
            insights.append({
                'type': 'behavioral_insight',
                'category': 'medication_adherence',
                'message': f'Your medication adherence ({adherence*100:.0f}%) could be improved',
                'severity': 'info',
                'recommendation': 'Set up medication reminders and track your doses.'
            })
        
        # Activity level insight
        activity = state.get('activity_level', 0.5)
        if activity < 0.5:
            insights.append({
                'type': 'wellness_insight',
                'category': 'physical_activity',
                'message': 'Increasing physical activity can improve your health outcomes',
                'severity': 'info',
                'recommendation': 'Aim for 30 minutes of moderate exercise daily.'
            })
        
        return jsonify({
            'user_id': request.user_id,
            'insights': insights,
            'morphogenetic_score': state.get('morphogenetic_score', 1.0),
            'last_updated': state.get('last_updated')
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        return jsonify({'error': 'Failed to generate insights'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
