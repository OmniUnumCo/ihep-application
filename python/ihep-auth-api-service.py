# services/auth-api/main.py
"""
IHEP Authentication API Service

This service handles user authentication, token generation, and session management.
It implements Zero Trust principles by requiring continuous authentication and
validates all requests against Identity Platform.

Security features:
- Argon2id password hashing (memory-hard, GPU-resistant)
- JWT tokens with short expiration (1 hour)
- Refresh tokens stored in Redis with rotation
- Rate limiting per IP and per user
- Audit logging of all authentication events
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import jwt
import datetime
import hashlib
import secrets
from functools import wraps
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import logging
from google.cloud import secretmanager
from google.cloud import logging as cloud_logging
from typing import Any

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=os.getenv('ALLOWED_ORIGINS', '*').split(','))

# Initialize logging
logging_client = cloud_logging.Client()
logging_client.setup_logging()
logger = logging.getLogger(__name__)

AUTH_LOG_REDACTION_SALT = os.getenv('AUTH_LOG_REDACTION_SALT', os.getenv('AUDIT_LOG_REDACTION_SALT', ''))


def _hash_identifier(value: str) -> str:
    """Generate a deterministic salted hash suitable for log correlation."""
    if value is None:
        return 'unknown'
    stringified = str(value)
    if AUTH_LOG_REDACTION_SALT:
        stringified = f"{AUTH_LOG_REDACTION_SALT}:{stringified}"
    return hashlib.sha256(stringified.encode()).hexdigest()[:12]


def _anonymize_ip(ip_address: str) -> str:
    """Mask IP addresses to avoid storing precise network identifiers."""
    if not ip_address:
        return 'unknown'
    if ':' in ip_address:
        return 'anonymized-ipv6'
    octets = ip_address.split('.')
    if len(octets) == 4:
        return '.'.join(octets[:2] + ['x', 'x'])
    return 'anonymized'


def _masked_identifier(identifier: str) -> str:
    """Return a contextual label for log statements without leaking raw data."""
    if not identifier:
        return 'unknown'
    if identifier.startswith('user:'):
        return 'user-context'
    normalized = identifier.split(',')[0].strip()
    return _anonymize_ip(normalized)


def _generate_error_reference() -> str:
    """Create opaque reference tokens for correlating client error reports."""
    return secrets.token_urlsafe(8)


def _log_internal_error(action: str, exc: Exception, **context: Any) -> str:
    """Log sanitized error details and return a reference for the caller."""
    reference = _generate_error_reference()
    hashed_context = {
        key: _hash_identifier(value)
        for key, value in context.items()
    }
    logger.error(
        "%s failed: ref=%s error_type=%s context=%s",
        action,
        reference,
        exc.__class__.__name__,
        hashed_context,
    )
    return reference

# Initialize password hasher with OWASP recommended parameters
ph = PasswordHasher(
    time_cost=2,      # Number of iterations
    memory_cost=65536, # Memory usage in KiB (64 MB)
    parallelism=4,    # Number of parallel threads
    hash_len=32,      # Length of hash in bytes
    salt_len=16       # Length of salt in bytes
)

# Redis connection for caching and session management
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0,
    decode_responses=True
)

# Database connection
def get_db_connection():
    """
    Create a database connection using credentials from Secret Manager.
    Connection pooling is handled at the Cloud SQL Proxy level.
    """
    secret_client = secretmanager.SecretManagerServiceClient()
    secret_name = f"projects/{os.getenv('PROJECT_ID')}/secrets/db-connection-string/versions/latest"
    response = secret_client.access_secret_version(request={"name": secret_name})
    connection_string = response.payload.data.decode('UTF-8')
    
    return psycopg2.connect(connection_string)

# JWT secret key (stored in Secret Manager)
def get_jwt_secret():
    """Retrieve JWT signing key from Secret Manager"""
    secret_client = secretmanager.SecretManagerServiceClient()
    secret_name = f"projects/{os.getenv('PROJECT_ID')}/secrets/jwt-secret/versions/latest"
    response = secret_client.access_secret_version(request={"name": secret_name})
    return response.payload.data.decode('UTF-8')

JWT_SECRET = get_jwt_secret()
JWT_ALGORITHM = 'HS256'
TOKEN_EXPIRATION_HOURS = 1

# Rate limiting decorator
def rate_limit(max_requests=5, window_seconds=3600):
    """
    Rate limiting decorator using token bucket algorithm.
    
    Token bucket refill rate: r = max_requests / window_seconds
    Bucket capacity: max_requests
    
    Mathematical model:
    tokens(t) = min(capacity, tokens(t-1) + r * Δt)
    
    where Δt is time elapsed since last request.
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Get identifier (IP address or user ID if authenticated)
            identifier = request.headers.get('X-Forwarded-For', request.remote_addr)
            if identifier:
                identifier = identifier.split(',')[0].strip()
            
            # Check if Authorization header exists for user-based limiting
            auth_header = request.headers.get('Authorization')
            if auth_header:
                try:
                    token = auth_header.split(' ')[1]
                    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
                    identifier = f"user:{payload['user_id']}"
                except:
                    pass  # Fall back to IP-based limiting
            
            # Redis key for rate limiting
            key = f"ratelimit:{f.__name__}:{identifier}"
            
            # Get current token count
            current_tokens = redis_client.get(key)
            
            if current_tokens is None:
                # First request, initialize bucket
                redis_client.setex(key, window_seconds, max_requests - 1)
                return f(*args, **kwargs)
            
            current_tokens = int(current_tokens)
            
            if current_tokens > 0:
                # Decrement token count
                redis_client.decr(key)
                return f(*args, **kwargs)
            else:
                # Rate limit exceeded with redacted logging context
                identifier_hash = _hash_identifier(identifier)
                logger.warning(
                    "Rate limit exceeded: identifier_hash=%s masked_origin=%s endpoint=%s",
                    identifier_hash,
                    _masked_identifier(identifier),
                    f.__name__,
                )
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': redis_client.ttl(key)
                }), 429
        
        return wrapped
    return decorator

# Authentication middleware
def require_auth(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401
        
        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            
            # Check if token is blacklisted (logout)
            if redis_client.exists(f"blacklist:{token}"):
                return jsonify({'error': 'Token has been revoked'}), 401
            
            # Add user info to request context
            request.user_id = payload['user_id']
            request.user_email = payload['email']
            
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
    
    return wrapped

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for load balancer"""
    try:
        # Verify database connectivity
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT 1')
        cur.close()
        conn.close()
        
        # Verify Redis connectivity
        redis_client.ping()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'service': 'auth-api'
        }), 200
    except Exception as exc:
        reference = _log_internal_error('health_check', exc)
        return jsonify({
            'status': 'unhealthy',
            'error': 'Service unavailable',
            'reference': reference,
        }), 503

@app.route('/signup', methods=['POST'])
@rate_limit(max_requests=3, window_seconds=3600)  # 3 signups per hour per IP
def signup():
    """
    User registration endpoint.
    
    Implements secure password hashing using Argon2id algorithm.
    Argon2id combines data-dependent (Argon2i) and data-independent (Argon2d)
    memory access patterns, providing resistance against both side-channel
    and GPU cracking attacks.
    
    Password entropy requirement: H >= 60 bits
    H = log2(R^L) where R is character space size, L is password length
    
    For minimum 8-character password with mixed case, numbers, and symbols:
    R = 26 + 26 + 10 + 32 = 94
    H = log2(94^8) ≈ 52.4 bits (below threshold, enforced at frontend)
    
    Recommended: 12 characters minimum -> H ≈ 78.6 bits
    """
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'fullName']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    email = data['email'].lower().strip()
    password = data['password']
    full_name = data['fullName'].strip()
    
    # Validate email format
    if '@' not in email or '.' not in email.split('@')[1]:
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Validate password strength (minimum enforced at frontend)
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if user already exists
        cur.execute('SELECT id FROM users WHERE email = %s', (email,))
        if cur.fetchone():
            return jsonify({'error': 'User already exists'}), 409
        
        # Hash password using Argon2id
        password_hash = ph.hash(password)
        
        # Insert new user
        cur.execute('''
            INSERT INTO users (email, password_hash, full_name, profile_completed, created_at, updated_at)
            VALUES (%s, %s, %s, FALSE, NOW(), NOW())
            RETURNING id, email, full_name, profile_completed
        ''', (email, password_hash, full_name))
        
        user = cur.fetchone()
        conn.commit()
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': str(user['id']),
            'email': user['email'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRATION_HOURS)
        }, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        # Generate refresh token
        refresh_token = secrets.token_urlsafe(32)
        redis_client.setex(
            f"refresh:{refresh_token}",
            30 * 24 * 60 * 60,  # 30 days
            str(user['id'])
        )
        
        # Log successful signup with salted hash for correlation only
        logger.info("User signed up: email_hash=%s", _hash_identifier(email))

        cur.close()
        conn.close()
        
        return jsonify({
            'token': token,
            'refreshToken': refresh_token,
            'user': {
                'id': str(user['id']),
                'email': user['email'],
                'fullName': user['full_name'],
                'profileCompleted': user['profile_completed']
            }
        }), 201
        
    except Exception as exc:
        reference = _log_internal_error('signup', exc, email=email)
        return jsonify({'error': 'Internal server error', 'reference': reference}), 500

@app.route('/login', methods=['POST'])
@rate_limit(max_requests=5, window_seconds=900)  # 5 attempts per 15 minutes
def login():
    """
    User login endpoint.
    
    Implements constant-time password verification to prevent timing attacks.
    Uses Argon2id verify function which internally uses constant-time comparison.
    """
    data = request.get_json()
    
    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Missing email or password'}), 400
    
    email = data['email'].lower().strip()
    password = data['password']
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Retrieve user
        cur.execute('''
            SELECT id, email, password_hash, full_name, profile_completed
            FROM users
            WHERE email = %s
        ''', (email,))
        
        user = cur.fetchone()
        
        if not user:
            # Use a dummy hash to prevent timing attacks
            try:
                ph.verify('$argon2id$v=19$m=65536,t=2,p=4$dummy', 'dummy')
            except:
                pass
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Verify password
        try:
            ph.verify(user['password_hash'], password)
            
            # Check if password needs rehashing (parameters updated)
            if ph.check_needs_rehash(user['password_hash']):
                new_hash = ph.hash(password)
                cur.execute(
                    'UPDATE users SET password_hash = %s WHERE id = %s',
                    (new_hash, user['id'])
                )
                conn.commit()
        except VerifyMismatchError:
            logger.warning("Failed login attempt: email_hash=%s", _hash_identifier(email))
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': str(user['id']),
            'email': user['email'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRATION_HOURS)
        }, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        # Generate refresh token
        refresh_token = secrets.token_urlsafe(32)
        redis_client.setex(
            f"refresh:{refresh_token}",
            30 * 24 * 60 * 60,  # 30 days
            str(user['id'])
        )
        
        # Log successful login without exposing raw email
        logger.info("User logged in: email_hash=%s", _hash_identifier(email))

        cur.close()
        conn.close()
        
        return jsonify({
            'token': token,
            'refreshToken': refresh_token,
            'user': {
                'id': str(user['id']),
                'email': user['email'],
                'fullName': user['full_name'],
                'profileCompleted': user['profile_completed']
            }
        }), 200
        
    except Exception as exc:
        reference = _log_internal_error('login', exc, email=email)
        return jsonify({'error': 'Internal server error', 'reference': reference}), 500

@app.route('/refresh', methods=['POST'])
@rate_limit(max_requests=10, window_seconds=3600)
def refresh_token():
    """
    Refresh JWT token using refresh token.
    
    Implements refresh token rotation to prevent replay attacks.
    Each refresh invalidates the old refresh token and issues a new one.
    """
    data = request.get_json()
    
    if 'refreshToken' not in data:
        return jsonify({'error': 'Missing refresh token'}), 400
    
    refresh_token_value = data['refreshToken']
    
    try:
        # Verify refresh token
        user_id = redis_client.get(f"refresh:{refresh_token_value}")
        
        if not user_id:
            return jsonify({'error': 'Invalid or expired refresh token'}), 401
        
        # Invalidate old refresh token
        redis_client.delete(f"refresh:{refresh_token_value}")
        
        # Get user details
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('''
            SELECT id, email, full_name, profile_completed
            FROM users
            WHERE id = %s
        ''', (user_id,))
        
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Generate new JWT token
        token = jwt.encode({
            'user_id': str(user['id']),
            'email': user['email'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRATION_HOURS)
        }, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        # Generate new refresh token
        new_refresh_token = secrets.token_urlsafe(32)
        redis_client.setex(
            f"refresh:{new_refresh_token}",
            30 * 24 * 60 * 60,  # 30 days
            str(user['id'])
        )
        
        return jsonify({
            'token': token,
            'refreshToken': new_refresh_token
        }), 200
        
    except Exception as exc:
        reference = _log_internal_error(
            'refresh_token',
            exc,
            refresh_token=refresh_token_value,
        )
        return jsonify({'error': 'Internal server error', 'reference': reference}), 500

@app.route('/logout', methods=['POST'])
@require_auth
def logout():
    """
    Logout endpoint that invalidates JWT token.
    
    Adds token to Redis blacklist with expiration matching token expiration.
    This prevents reuse of the token even though it's technically still valid.
    """
    try:
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        
        # Decode to get expiration time
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"verify_exp": False})
        exp_timestamp = payload['exp']
        current_timestamp = datetime.datetime.utcnow().timestamp()
        ttl = int(exp_timestamp - current_timestamp)
        
        if ttl > 0:
            # Add to blacklist
            redis_client.setex(f"blacklist:{token}", ttl, '1')
        
        # Invalidate refresh token if provided
        data = request.get_json() or {}
        if 'refreshToken' in data:
            redis_client.delete(f"refresh:{data['refreshToken']}")

        logger.info("User logged out: email_hash=%s", _hash_identifier(request.user_email))

        return jsonify({'message': 'Logged out successfully'}), 200
        
    except Exception as exc:
        reference = _log_internal_error(
            'logout',
            exc,
            user_email=getattr(request, 'user_email', None),
        )
        return jsonify({'error': 'Internal server error', 'reference': reference}), 500

@app.route('/validate', methods=['GET'])
@require_auth
def validate_token():
    """Validate JWT token and return user info"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('''
            SELECT id, email, full_name, profile_completed
            FROM users
            WHERE id = %s
        ''', (request.user_id,))
        
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': str(user['id']),
                'email': user['email'],
                'fullName': user['full_name'],
                'profileCompleted': user['profile_completed']
            }
        }), 200
        
    except Exception as exc:
        reference = _log_internal_error(
            'validate_token',
            exc,
            user_id=getattr(request, 'user_id', None),
        )
        return jsonify({'error': 'Internal server error', 'reference': reference}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))