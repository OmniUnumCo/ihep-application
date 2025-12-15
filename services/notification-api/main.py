# services/notification-api/main.py
"""
IHEP Notification Service

Handles all user notifications including appointment reminders,
health alerts, and community updates.

Key features:
- Multi-channel notifications (SMS, Email, Push)
- Priority-based delivery scheduling
- Delivery confirmation and retry logic
- Compliance with communication preferences
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import jwt
from functools import wraps
import logging
from google.cloud import logging as cloud_logging
from google.cloud import pubsub_v1
import json
from datetime import datetime, timedelta
import redis
from twilio.rest import Client
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)
CORS(app, origins=os.getenv('ALLOWED_ORIGINS', '*').split(','))

# Initialize logging
logging_client = cloud_logging.Client()
logging_client.setup_logging()
logger = logging.getLogger(__name__)

# Redis for queue management
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=5,
    decode_responses=True
)

# Notification clients
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID else None

# AWS SES for email
ses_client = boto3.client('ses', region_name=os.getenv('AWS_REGION', 'us-east-1'))

# Pub/Sub for event-driven notifications
publisher = pubsub_v1.PublisherClient()
PROJECT_ID = os.getenv('PROJECT_ID')
NOTIFICATION_TOPIC = f"projects/{PROJECT_ID}/topics/notifications"

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

class NotificationService:
    """
    Notification service with priority queuing and delivery optimization.
    
    Implements a priority queue system where:
    - High priority: Critical health alerts (immediate delivery)
    - Medium priority: Appointment reminders (24-48 hours advance)
    - Low priority: General updates (batch delivery)
    
    Delivery optimization uses exponential backoff:
    T_retry = T_base * (2^n) + random_jitter
    
    Where T_base = 60 seconds, n = retry attempt, jitter = 0-30 seconds
    """
    
    def __init__(self):
        self.notification_queue = "notification_queue"
        self.delivery_attempts = {}
    
    def send_notification(self, notification_data):
        """
        Send notification through appropriate channel based on user preferences.
        
        Mathematical model for delivery success optimization:
        P(success) = P(channel_works) * P_user_available(channel, time)
        
        Where P_user_available is learned from historical engagement data.
        """
        user_id = notification_data['user_id']
        channel = notification_data['channel']
        priority = notification_data.get('priority', 'medium')
        
        # Get user preferences
        preferences_key = f"user_preferences:{user_id}"
        preferences = redis_client.hgetall(preferences_key)
        
        # Check if user has enabled this channel
        channel_enabled = preferences.get(f"{channel}_enabled", "true") == "true"
        if not channel_enabled:
            logger.info(f"Notification channel {channel} disabled for user {user_id}")
            return False
        
        # Check delivery time preferences
        preferred_hours = preferences.get('preferred_hours', '9-17')
        if not self._is_preferred_time(preferred_hours):
            # Queue for later delivery
            self._queue_notification(notification_data)
            return True
        
        # Send notification
        success = False
        try:
            if channel == 'sms':
                success = self._send_sms(notification_data)
            elif channel == 'email':
                success = self._send_email(notification_data)
            elif channel == 'push':
                success = self._send_push(notification_data)
            
            if success:
                logger.info(f"Notification sent successfully to user {user_id} via {channel}")
                return True
            else:
                logger.warning(f"Failed to send notification to user {user_id} via {channel}")
                
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
        
        # Handle failure with retry logic
        if success:
            return True
        else:
            self._handle_delivery_failure(notification_data)
            return False
    
    def _send_sms(self, notification_data):
        """Send SMS notification"""
        if not twilio_client:
            logger.error("Twilio client not configured")
            return False
        
        try:
            message = twilio_client.messages.create(
                body=notification_data['message'],
                from_=os.getenv('TWILIO_PHONE_NUMBER'),
                to=notification_data['recipient']
            )
            
            # Log delivery
            delivery_log = {
                'notification_id': notification_data.get('id'),
                'user_id': notification_data['user_id'],
                'channel': 'sms',
                'recipient': notification_data['recipient'],
                'status': 'sent',
                'message_sid': message.sid,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            redis_client.lpush('delivery_logs', json.dumps(delivery_log))
            return True
            
        except Exception as e:
            logger.error(f"SMS delivery failed: {str(e)}")
            return False
    
    def _send_email(self, notification_data):
        """Send email notification"""
        try:
            response = ses_client.send_email(
                Source=os.getenv('EMAIL_SENDER'),
                Destination={
                    'ToAddresses': [notification_data['recipient']]
                },
                Message={
                    'Subject': {
                        'Data': notification_data.get('subject', 'IHEP Notification'),
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': notification_data['message'],
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
            
            # Log delivery
            delivery_log = {
                'notification_id': notification_data.get('id'),
                'user_id': notification_data['user_id'],
                'channel': 'email',
                'recipient': notification_data['recipient'],
                'status': 'sent',
                'message_id': response['MessageId'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            redis_client.lpush('delivery_logs', json.dumps(delivery_log))
            return True
            
        except ClientError as e:
            logger.error(f"Email delivery failed: {str(e)}")
            return False
    
    def _send_push(self, notification_data):
        """Send push notification (simplified)"""
        # In production, this would integrate with Firebase, APNs, etc.
        try:
            # Simulate push notification
            push_data = {
                'title': notification_data.get('title', 'IHEP Alert'),
                'body': notification_data['message'],
                'user_id': notification_data['user_id'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Log delivery
            delivery_log = {
                'notification_id': notification_data.get('id'),
                'user_id': notification_data['user_id'],
                'channel': 'push',
                'recipient': notification_data['recipient'],
                'status': 'sent',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            redis_client.lpush('delivery_logs', json.dumps(delivery_log))
            return True
            
        except Exception as e:
            logger.error(f"Push delivery failed: {str(e)}")
            return False
    
    def _is_preferred_time(self, preferred_hours):
        """Check if current time is within user's preferred hours"""
        try:
            current_hour = datetime.now().hour
            start_hour, end_hour = map(int, preferred_hours.split('-'))
            return start_hour <= current_hour <= end_hour
        except:
            return True  # Default to sending if parsing fails
    
    def _queue_notification(self, notification_data):
        """Queue notification for later delivery"""
        priority = notification_data.get('priority', 'medium')
        queue_key = f"notification_queue:{priority}"
        redis_client.lpush(queue_key, json.dumps(notification_data))
        logger.info(f"Notification queued for user {notification_data['user_id']} with priority {priority}")
    
    def _handle_delivery_failure(self, notification_data):
        """Handle notification delivery failure with retry logic"""
        notification_id = notification_data.get('id', str(hash(str(notification_data))))
        
        # Track delivery attempts
        attempt_key = f"delivery_attempts:{notification_id}"
        attempts = int(redis_client.get(attempt_key) or 0)
        
        if attempts < 3:  # Max 3 retry attempts
            # Calculate exponential backoff
            backoff_time = 60 * (2 ** attempts) + (hash(notification_id) % 30)
            
            # Increment attempt counter
            redis_client.incr(attempt_key)
            redis_client.expire(attempt_key, 86400)  # 24-hour expiry
            
            # Schedule retry
            retry_data = {
                **notification_data,
                'retry_attempt': attempts + 1
            }
            
            # Use Redis sorted set for delayed delivery
            retry_time = datetime.utcnow().timestamp() + backoff_time
            redis_client.zadd('retry_queue', {json.dumps(retry_data): retry_time})
            
            logger.info(f"Scheduled retry for notification {notification_id} in {backoff_time} seconds")
        else:
            # Max retries exceeded, mark as failed
            failure_log = {
                'notification_id': notification_id,
                'user_id': notification_data['user_id'],
                'status': 'failed',
                'attempts': attempts,
                'final_error': 'Max retry attempts exceeded',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            redis_client.lpush('delivery_failures', json.dumps(failure_log))
            logger.error(f"Notification delivery failed permanently for user {notification_data['user_id']}")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'notification-api',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/notifications/send', methods=['POST'])
@require_auth
def send_notification():
    """Send a notification to the authenticated user"""
    try:
        data = request.get_json()
        message = data.get('message')
        channel = data.get('channel', 'email')
        priority = data.get('priority', 'medium')
        
        if not message:
            return jsonify({'error': 'Message content required'}), 400
        
        # Get user contact information
        user_key = f"user_contact:{request.user_id}"
        user_contact = redis_client.hgetall(user_key)
        
        if not user_contact:
            return jsonify({'error': 'User contact information not found'}), 404
        
        recipient = None
        if channel == 'sms':
            recipient = user_contact.get('phone')
        elif channel in ['email', 'push']:
            recipient = user_contact.get('email')
        
        if not recipient:
            return jsonify({'error': f'No {channel} contact information found'}), 400
        
        # Create notification data
        notification_data = {
            'id': str(hash(f"{request.user_id}:{datetime.utcnow().isoformat()}")),
            'user_id': request.user_id,
            'recipient': recipient,
            'message': message,
            'channel': channel,
            'priority': priority,
            'subject': data.get('subject'),
            'title': data.get('title'),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Initialize notification service
        notification_service = NotificationService()
        
        # Send notification
        success = notification_service.send_notification(notification_data)
        
        if success:
            return jsonify({
                'message': 'Notification sent successfully',
                'notification_id': notification_data['id']
            }), 200
        else:
            return jsonify({'error': 'Failed to send notification'}), 500
        
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        return jsonify({'error': 'Failed to send notification'}), 500

@app.route('/notifications/preferences', methods=['GET'])
@require_auth
def get_notification_preferences():
    """Get user's notification preferences"""
    try:
        preferences_key = f"user_preferences:{request.user_id}"
        preferences = redis_client.hgetall(preferences_key)
        
        if not preferences:
            # Return default preferences
            preferences = {
                'sms_enabled': 'true',
                'email_enabled': 'true',
                'push_enabled': 'true',
                'preferred_hours': '9-17',
                'appointment_reminders': 'true',
                'health_alerts': 'true',
                'community_updates': 'false'
            }
        
        return jsonify(preferences), 200
        
    except Exception as e:
        logger.error(f"Error retrieving preferences: {str(e)}")
        return jsonify({'error': 'Failed to retrieve preferences'}), 500

@app.route('/notifications/preferences', methods=['PUT'])
@require_auth
def update_notification_preferences():
    """Update user's notification preferences"""
    try:
        data = request.get_json()
        
        preferences_key = f"user_preferences:{request.user_id}"
        redis_client.hmset(preferences_key, data)
        redis_client.expire(preferences_key, 2592000)  # 30-day TTL
        
        # Log preference update
        preference_log = {
            'user_id': request.user_id,
            'updated_preferences': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        redis_client.lpush('preference_updates', json.dumps(preference_log))
        
        logger.info(f"Notification preferences updated for user {request.user_id}")
        
        return jsonify({'message': 'Preferences updated successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        return jsonify({'error': 'Failed to update preferences'}), 500

# Background worker for processing notification queue
def process_notification_queue():
    """Background worker to process queued notifications"""
    notification_service = NotificationService()
    
    while True:
        try:
            # Check retry queue for delayed notifications
            current_time = datetime.utcnow().timestamp()
            retry_items = redis_client.zrangebyscore(
                'retry_queue', 0, current_time, withscores=False
            )
            
            for item in retry_items:
                notification_data = json.loads(item)
                notification_service.send_notification(notification_data)
                redis_client.zrem('retry_queue', item)
            
            # Process priority queues
            for priority in ['high', 'medium', 'low']:
                queue_key = f"notification_queue:{priority}"
                notification_item = redis_client.rpop(queue_key)
                
                if notification_item:
                    notification_data = json.loads(notification_item)
                    notification_service.send_notification(notification_data)
            
            # Sleep briefly to prevent excessive CPU usage
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Error processing notification queue: {str(e)}")
            time.sleep(5)  # Longer sleep on error

if __name__ == '__main__':
    import threading
    import time
    
    # Start background worker thread
    worker_thread = threading.Thread(target=process_notification_queue, daemon=True)
    worker_thread.start()
    
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
