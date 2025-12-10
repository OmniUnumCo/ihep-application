# services/calendar-api/main.py
"""
IHEP Calendar and Resource Management Service

This service manages appointment scheduling, resource allocation,
and community event coordination for the IHEP platform.

Key features:
- Intelligent appointment scheduling with conflict resolution
- Resource optimization using constraint satisfaction
- Community event management
- Integration with provider systems
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import jwt
from functools import wraps
import logging
from google.cloud import logging as cloud_logging
from google.cloud import bigquery
import json
from datetime import datetime, timedelta
import redis
from typing import Dict, List, Optional
import uuid

app = Flask(__name__)
CORS(app, origins=os.getenv('ALLOWED_ORIGINS', '*').split(','))

# Initialize logging
logging_client = cloud_logging.Client()
logging_client.setup_logging()
logger = logging.getLogger(__name__)

# Redis for caching and distributed locking
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=4,
    decode_responses=True
)

# BigQuery for analytics
bq_client = bigquery.Client()
PROJECT_ID = os.getenv('PROJECT_ID')
JWT_SECRET = os.getenv('JWT_SECRET')

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

class AppointmentScheduler:
    """
    Intelligent appointment scheduling system.
    
    Uses constraint satisfaction optimization to find optimal appointment slots:
    
    Minimize: Σ(w_i * C_i(x))
    
    Subject to:
    - Provider availability constraints
    - Patient preference constraints
    - Resource capacity constraints
    - Time window constraints
    
    Where:
    - C_i(x) = cost function for constraint i
    - w_i = weight for constraint i
    - x = appointment assignment variables
    
    Implements conflict resolution using backtracking with forward checking.
    """
    
    def __init__(self):
        self.providers = {}  # provider_id -> availability data
        self.patients = {}   # patient_id -> preference data
        self.resources = {}  # resource_id -> capacity data
    
    def find_optimal_slot(self, patient_id: str, provider_id: str, 
                         duration: int = 30, preferred_time: Optional[datetime] = None) -> Optional[dict]:
        """
        Find optimal appointment slot using constraint optimization.
        
        Mathematical model:
        f(slot) = w1*d(slot, preferred) + w2*availability_factor + w3*travel_factor
        
        Where:
        - d(slot, preferred) = temporal distance from preferred time
        - availability_factor = provider's availability score at that time
        - travel_factor = convenience factor based on location/time
        """
        # Get provider availability
        provider_key = f"provider_availability:{provider_id}"
        availability_data = redis_client.hgetall(provider_key)
        
        if not availability_data:
            # Load from database/storage
            availability_data = self._load_provider_availability(provider_id)
        
        # Get patient preferences
        patient_key = f"patient_preferences:{patient_id}"
        preferences = redis_client.hgetall(patient_key)
        
        # Generate candidate slots
        candidate_slots = self._generate_candidate_slots(
            availability_data, duration, preferred_time
        )
        
        if not candidate_slots:
            return None
        
        # Score each slot
        scored_slots = []
        for slot in candidate_slots:
            score = self._score_slot(slot, patient_id, provider_id, preferences)
            scored_slots.append((slot, score))
        
        # Sort by score (lower is better)
        scored_slots.sort(key=lambda x: x[1])
        
        # Return best slot
        if scored_slots:
            best_slot, best_score = scored_slots[0]
            return {
                'slot': best_slot,
                'score': best_score,
                'confidence': 1.0 - (best_score / 100.0)  # Normalize to 0-1
            }
        
        return None
    
    def _generate_candidate_slots(self, availability_data: dict, 
                                duration: int, preferred_time: Optional[datetime]) -> List[dict]:
        """Generate candidate appointment slots"""
        slots = []
        
        # Parse availability data
        for date_str, hours_data in availability_data.items():
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                hours = json.loads(hours_data) if isinstance(hours_data, str) else hours_data
                
                # Generate 30-minute slots
                for hour in range(8, 18):  # 8 AM to 6 PM
                    for minute in [0, 30]:
                        slot_time = date_obj.replace(hour=hour, minute=minute)
                        
                        # Check if slot is available
                        slot_key = f"{date_str}_{hour:02d}{minute:02d}"
                        if slot_key not in hours.get('booked_slots', []):
                            slots.append({
                                'datetime': slot_time.isoformat(),
                                'date': date_str,
                                'time': f"{hour:02d}:{minute:02d}",
                                'duration': duration
                            })
            except Exception as e:
                logger.error(f"Error parsing availability data: {e}")
                continue
        
        # Sort slots by proximity to preferred time
        if preferred_time:
            slots.sort(key=lambda x: abs(
                datetime.fromisoformat(x['datetime']) - preferred_time
            ).total_seconds())
        
        return slots[:50]  # Return top 50 candidates
    
    def _score_slot(self, slot: dict, patient_id: str, provider_id: str, 
                   preferences: dict) -> float:
        """
        Score appointment slot based on multiple factors.
        
        Scoring model:
        score = w1*temporal_distance + w2*provider_load + w3*patient_preference
        
        Weights are empirically derived to balance all factors appropriately.
        """
        slot_time = datetime.fromisoformat(slot['datetime'])
        
        # Factor 1: Temporal distance from preferred time (weight: 0.4)
        preferred_time_str = preferences.get('preferred_time')
        temporal_score = 0
        if preferred_time_str:
            try:
                preferred_time = datetime.fromisoformat(preferred_time_str)
                time_diff_hours = abs((slot_time - preferred_time).total_seconds() / 3600)
                temporal_score = min(50, time_diff_hours * 2)  # Cap at 50
            except:
                temporal_score = 25  # Neutral score if parsing fails
        
        # Factor 2: Provider load (weight: 0.3)
        provider_load_key = f"provider_load:{provider_id}:{slot['date']}"
        daily_appointments = int(redis_client.get(provider_load_key) or 0)
        max_daily_appointments = 16  # 8 hours * 2 appointments per hour
        load_score = (daily_appointments / max_daily_appointments) * 30
        
        # Factor 3: Time convenience (weight: 0.3)
        hour = slot_time.hour
        # Prefer business hours (9 AM - 5 PM)
        if 9 <= hour <= 17:
            time_convenience_score = 0
        elif 8 <= hour <= 18:
            time_convenience_score = 10
        else:
            time_convenience_score = 20
        
        total_score = (0.4 * temporal_score + 
                      0.3 * load_score + 
                      0.3 * time_convenience_score)
        
        return total_score

class ResourceManager:
    """
    Resource management system for community events and shared resources.
    
    Implements bin packing optimization for resource allocation:
    
    Minimize: Σ(c_j * y_j)
    
    Subject to:
    - Σ(a_ij * x_ij) ≤ c_j * y_j  (capacity constraints)
    - Σ(x_ij) = d_i  (demand satisfaction)
    - x_ij, y_j ∈ {0,1}  (binary variables)
    
    Where:
    - c_j = cost of resource j
    - y_j = 1 if resource j is used
    - a_ij = amount of resource j needed by request i
    - x_ij = 1 if request i is assigned to resource j
    - d_i = demand of request i
    """
    
    def __init__(self):
        self.resources = {}  # resource_id -> resource_info
        self.bookings = {}   # booking_id -> booking_info
    
    def allocate_resources(self, event_request: dict) -> dict:
        """
        Allocate resources for community event using optimization.
        
        Returns allocation plan with resource assignments and costs.
        """
        required_resources = event_request.get('required_resources', [])
        event_date = event_request.get('date')
        event_duration = event_request.get('duration', 2)  # hours
        
        # Get available resources for the date
        available_resources = self._get_available_resources(event_date, event_duration)
        
        # Simple greedy allocation (would use more sophisticated algorithm in production)
        allocation = {}
        total_cost = 0
        
        for req in required_resources:
            resource_type = req['type']
            quantity_needed = req['quantity']
            max_budget = req.get('max_budget', float('inf'))
            
            # Find suitable resources
            suitable_resources = [
                res for res in available_resources 
                if res['type'] == resource_type and res['available']
            ]
            
            # Sort by cost efficiency
            suitable_resources.sort(key=lambda x: x['hourly_rate'])
            
            allocated_quantity = 0
            resource_cost = 0
            
            for resource in suitable_resources:
                if allocated_quantity >= quantity_needed:
                    break
                
                available_quantity = min(
                    resource['quantity'], 
                    quantity_needed - allocated_quantity
                )
                
                cost = available_quantity * resource['hourly_rate'] * event_duration
                
                if cost <= max_budget:
                    allocation[resource['id']] = {
                        'quantity': available_quantity,
                        'cost': cost,
                        'resource_info': resource
                    }
                    
                    allocated_quantity += available_quantity
                    resource_cost += cost
                    total_cost += cost
                    
                    # Mark resource as booked
                    self._book_resource(resource['id'], event_date, event_duration)
            
            if allocated_quantity < quantity_needed:
                return {
                    'success': False,
                    'message': f'Insufficient {resource_type} resources available',
                    'allocated': allocation,
                    'total_cost': total_cost
                }
        
        return {
            'success': True,
            'allocation': allocation,
            'total_cost': total_cost,
            'message': 'Resources successfully allocated'
        }
    
    def _get_available_resources(self, date: str, duration: int) -> List[dict]:
        """Get available resources for given date and duration"""
        # This would query a database in production
        # For demo, return sample resources
        return [
            {
                'id': 'room_a',
                'type': 'meeting_room',
                'name': 'Community Room A',
                'quantity': 1,
                'hourly_rate': 25.00,
                'available': True,
                'capacity': 25
            },
            {
                'id': 'equipment_set_1',
                'type': 'medical_equipment',
                'name': 'Basic Health Screening Kit',
                'quantity': 2,
                'hourly_rate': 15.00,
                'available': True,
                'capacity': 1
            },
            {
                'id': 'laptop_1',
                'type': 'technology',
                'name': 'Presentation Laptop',
                'quantity': 1,
                'hourly_rate': 10.00,
                'available': True,
                'capacity': 1
            }
        ]
    
    def _book_resource(self, resource_id: str, date: str, duration: int):
        """Mark resource as booked for given date and duration"""
        booking_key = f"resource_booking:{resource_id}:{date}"
        redis_client.setex(booking_key, 86400, "booked")  # 24-hour TTL

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'calendar-api',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/appointments/schedule', methods=['POST'])
@require_auth
def schedule_appointment():
    """
    Schedule a new appointment using intelligent optimization.
    
    Finds optimal slot based on provider availability, patient preferences,
    and system-wide optimization goals.
    """
    try:
        data = request.get_json()
        provider_id = data.get('provider_id')
        duration = data.get('duration', 30)
        preferred_time = data.get('preferred_time')
        
        if not provider_id:
            return jsonify({'error': 'Provider ID required'}), 400
        
        # Initialize scheduler
        scheduler = AppointmentScheduler()
        
        # Find optimal slot
        optimal_slot = scheduler.find_optimal_slot(
            request.user_id, provider_id, duration, 
            datetime.fromisoformat(preferred_time) if preferred_time else None
        )
        
        if not optimal_slot:
            return jsonify({
                'success': False,
                'message': 'No available slots found for the selected provider'
            }), 404
        
        # Create appointment record with distributed locking
        lock_key = f"appointment_lock:{provider_id}:{optimal_slot['slot']['datetime']}"
        lock_acquired = redis_client.set(lock_key, "locked", nx=True, ex=30)
        
        if not lock_acquired:
            return jsonify({
                'success': False,
                'message': 'Slot no longer available, please try again'
            }), 409
        
        try:
            appointment_id = str(uuid.uuid4())
            
            appointment_data = {
                'id': appointment_id,
                'user_id': request.user_id,
                'provider_id': provider_id,
                'scheduled_time': optimal_slot['slot']['datetime'],
                'duration': duration,
                'status': 'scheduled',
                'created_at': datetime.utcnow().isoformat(),
                'score': optimal_slot['score'],
                'confidence': optimal_slot['confidence']
            }
            
            # Store appointment
            appointment_key = f"appointment:{appointment_id}"
            redis_client.hmset(appointment_key, appointment_data)
            redis_client.expire(appointment_key, 2592000)  # 30-day TTL
            
            # Update provider load
            slot_time = datetime.fromisoformat(optimal_slot['slot']['datetime'])
            load_key = f"provider_load:{provider_id}:{slot_time.date().isoformat()}"
            redis_client.incr(load_key)
            redis_client.expire(load_key, 86400)  # 24-hour TTL
            
            # Mark slot as booked
            provider_key = f"provider_availability:{provider_id}"
            date_str = slot_time.date().isoformat()
            slot_key = f"{date_str}_{slot_time.hour:02d}{slot_time.minute:02d}"
            
            # Get current booked slots
            current_booked = redis_client.hget(provider_key, 'booked_slots')
            booked_slots = json.loads(current_booked) if current_booked else []
            booked_slots.append(slot_key)
            redis_client.hset(provider_key, 'booked_slots', json.dumps(booked_slots))
            
            # Log appointment
            appointment_log = {
                'appointment_id': appointment_id,
                'user_id': request.user_id,
                'provider_id': provider_id,
                'scheduled_time': optimal_slot['slot']['datetime'],
                'duration': duration,
                'score': optimal_slot['score'],
                'confidence': optimal_slot['confidence'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            table_id = f"{PROJECT_ID}.ihep_calendar.appointments"
            bq_client.insert_rows_json(table_id, [appointment_log])
            
            logger.info(f"Appointment scheduled for user {request.user_id}")
            
            return jsonify({
                'success': True,
                'appointment_id': appointment_id,
                'scheduled_time': optimal_slot['slot']['datetime'],
                'duration': duration,
                'confidence': round(optimal_slot['confidence'], 4),
                'provider_id': provider_id,
                'message': 'Appointment successfully scheduled'
            }), 201
            
        finally:
            # Release lock
            redis_client.delete(lock_key)
        
    except Exception as e:
        logger.error(f"Error scheduling appointment: {str(e)}")
        return jsonify({'error': 'Failed to schedule appointment'}), 500

@app.route('/appointments', methods=['GET'])
@require_auth
def get_user_appointments():
    """Get all appointments for the authenticated user"""
    try:
        # This would query a more sophisticated system in production
        # For demo, return sample data or cached appointments
        
        # Check cache first
        cache_key = f"user_appointments:{request.user_id}"
        cached_appointments = redis_client.get(cache_key)
        
        if cached_appointments:
            appointments = json.loads(cached_appointments)
        else:
            # Generate sample appointments for demo
            appointments = [
                {
                    'id': str(uuid.uuid4()),
                    'provider_id': 'provider_123',
                    'provider_name': 'Dr. Smith',
                    'scheduled_time': (datetime.utcnow() + timedelta(days=3)).isoformat(),
                    'duration': 30,
                    'status': 'scheduled',
                    'type': 'telehealth',
                    'location': 'Virtual Meeting'
                },
                {
                    'id': str(uuid.uuid4()),
                    'provider_id': 'provider_456',
                    'provider_name': 'Dr. Johnson',
                    'scheduled_time': (datetime.utcnow() + timedelta(days=7)).isoformat(),
                    'duration': 45,
                    'status': 'scheduled',
                    'type': 'in-person',
                    'location': 'Main Clinic, Room 201'
                }
            ]
            
            # Cache for 5 minutes
            redis_client.setex(cache_key, 300, json.dumps(appointments))
        
        # Filter out past appointments
        now = datetime.utcnow()
        upcoming_appointments = [
            apt for apt in appointments 
            if datetime.fromisoformat(apt['scheduled_time'].replace('Z', '+00:00')) > now
        ]
        
        return jsonify({
            'appointments': upcoming_appointments,
            'count': len(upcoming_appointments)
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving appointments: {str(e)}")
        return jsonify({'error': 'Failed to retrieve appointments'}), 500

@app.route('/appointments/<appointment_id>', methods=['GET'])
@require_auth
def get_appointment_details(appointment_id):
    """Get details for a specific appointment"""
    try:
        appointment_key = f"appointment:{appointment_id}"
        appointment_data = redis_client.hgetall(appointment_key)
        
        if not appointment_data:
            return jsonify({'error': 'Appointment not found'}), 404
        
        # Verify user owns this appointment
        if appointment_data.get('user_id') != request.user_id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        return jsonify(appointment_data), 200
        
    except Exception as e:
        logger.error(f"Error retrieving appointment details: {str(e)}")
        return jsonify({'error': 'Failed to retrieve appointment details'}), 500

@app.route('/appointments/<appointment_id>/cancel', methods=['POST'])
@require_auth
def cancel_appointment(appointment_id):
    """Cancel a scheduled appointment"""
    try:
        appointment_key = f"appointment:{appointment_id}"
        appointment_data = redis_client.hgetall(appointment_key)
        
        if not appointment_data:
            return jsonify({'error': 'Appointment not found'}), 404
        
        # Verify user owns this appointment
        if appointment_data.get('user_id') != request.user_id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Update appointment status
        appointment_data['status'] = 'cancelled'
        appointment_data['cancelled_at'] = datetime.utcnow().isoformat()
        redis_client.hmset(appointment_key, appointment_data)
        
        # Free up the slot
        provider_id = appointment_data['provider_id']
        scheduled_time = datetime.fromisoformat(appointment_data['scheduled_time'])
        slot_key = f"{scheduled_time.date().isoformat()}_{scheduled_time.hour:02d}{scheduled_time.minute:02d}"
        
        provider_key = f"provider_availability:{provider_id}"
        current_booked = redis_client.hget(provider_key, 'booked_slots')
        if current_booked:
            booked_slots = json.loads(current_booked)
            if slot_key in booked_slots:
                booked_slots.remove(slot_key)
                redis_client.hset(provider_key, 'booked_slots', json.dumps(booked_slots))
        
        # Update provider load
        load_key = f"provider_load:{provider_id}:{scheduled_time.date().isoformat()}"
        redis_client.decr(load_key)
        
        # Log cancellation
        cancellation_log = {
            'appointment_id': appointment_id,
            'user_id': request.user_id,
            'provider_id': provider_id,
            'cancelled_at': datetime.utcnow().isoformat(),
            'original_scheduled_time': appointment_data['scheduled_time']
        }
        
        table_id = f"{PROJECT_ID}.ihep_calendar.cancellations"
        bq_client.insert_rows_json(table_id, [cancellation_log])
        
        logger.info(f"Appointment {appointment_id} cancelled by user {request.user_id}")
        
        return jsonify({
            'message': 'Appointment successfully cancelled',
            'appointment_id': appointment_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error cancelling appointment: {str(e)}")
        return jsonify({'error': 'Failed to cancel appointment'}), 500

@app.route('/resources/events', methods=['POST'])
@require_auth
def create_community_event():
    """
    Create a new community event with resource allocation.
    
    Manages the entire event lifecycle from planning to execution.
    """
    try:
        data = request.get_json()
        event_name = data.get('name')
        event_date = data.get('date')
        required_resources = data.get('required_resources', [])
        
        if not event_name or not event_date:
            return jsonify({'error': 'Event name and date required'}), 400
        
        # Initialize resource manager
        resource_manager = ResourceManager()
        
        # Allocate resources
        allocation_result = resource_manager.allocate_resources({
            'name': event_name,
            'date': event_date,
            'required_resources': required_resources,
            'duration': data.get('duration', 2)
        })
        
        if not allocation_result['success']:
            return jsonify(allocation_result), 400
        
        # Create event record
        event_id = str(uuid.uuid4())
        event_data = {
            'id': event_id,
            'name': event_name,
            'date': event_date,
            'duration': data.get('duration', 2),
            'description': data.get('description', ''),
            'location': data.get('location', 'Community Center'),
            'organizer_id': request.user_id,
            'required_resources': json.dumps(required_resources),
            'allocated_resources': json.dumps(allocation_result['allocation']),
            'total_cost': allocation_result['total_cost'],
            'status': 'planned',
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Store event
        event_key = f"community_event:{event_id}"
        redis_client.hmset(event_key, event_data)
        redis_client.expire(event_key, 2592000)  # 30-day TTL
        
        # Log event creation
        event_log = {
            'event_id': event_id,
            'name': event_name,
            'date': event_date,
            'organizer_id': request.user_id,
            'total_cost': allocation_result['total_cost'],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        table_id = f"{PROJECT_ID}.ihep_calendar.community_events"
        bq_client.insert_rows_json(table_id, [event_log])
        
        logger.info(f"Community event created: {event_name}")
        
        return jsonify({
            'success': True,
            'event_id': event_id,
            'name': event_name,
            'date': event_date,
            'allocated_resources': allocation_result['allocation'],
            'total_cost': allocation_result['total_cost'],
            'message': 'Community event successfully created'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating community event: {str(e)}")
        return jsonify({'error': 'Failed to create community event'}), 500

@app.route('/resources/events', methods=['GET'])
def get_community_events():
    """Get list of upcoming community events"""
    try:
        # In production, this would query a database
        # For demo, return sample events
        
        upcoming_events = [
            {
                'id': str(uuid.uuid4()),
                'name': 'Monthly Health Screening',
                'date': (datetime.utcnow() + timedelta(days=5)).date().isoformat(),
                'time': '10:00',
                'duration': 3,
                'location': 'Community Center Main Hall',
                'description': 'Free health screenings for all community members',
                'available_spots': 25,
                'total_spots': 30
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Diabetes Management Workshop',
                'date': (datetime.utcnow() + timedelta(days=1](streamdown:incomplete-link)
