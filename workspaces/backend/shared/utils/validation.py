"""
Rate Limiting and Validation Utilities
"""

import re
from functools import wraps
from flask import request, jsonify
from typing import Callable
import redis
import os

# Redis client for rate limiting
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)


def rate_limit(limit: int, per: int):
    """
    Rate limit decorator using token bucket algorithm
    
    Args:
        limit: Number of requests allowed
        per: Time period in seconds
    
    Example:
        @rate_limit(limit=100, per=60)  # 100 requests per minute
    """
    def decorator(f: Callable):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier (IP address)
            client_id = request.remote_addr
            key = f"rate_limit:{f.__name__}:{client_id}"
            
            # Get current count
            current = redis_client.get(key)
            
            if current is None:
                # First request - set key with expiration
                redis_client.setex(key, per, 1)
                return f(*args, **kwargs)
            
            current = int(current)
            
            if current >= limit:
                # Rate limit exceeded
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'limit': limit,
                    'period': per
                }), 429
            
            # Increment counter
            redis_client.incr(key)
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_email(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
    
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> bool:
    """
    Validate password strength
    
    Requirements:
    - Minimum 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        password: Password to validate
    
    Returns:
        True if strong enough, False otherwise
    """
    if len(password) < 12:
        return False
    
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    
    return all([has_upper, has_lower, has_digit, has_special])


def validate_fhir_resource(resource: dict, resource_type: str) -> bool:
    """
    Validate FHIR resource structure
    
    Args:
        resource: FHIR resource dictionary
        resource_type: Expected resource type (e.g., 'Patient', 'Observation')
    
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(resource, dict):
        return False
    
    if resource.get('resourceType') != resource_type:
        return False
    
    # Basic validation - in production, use full FHIR validator
    return True
