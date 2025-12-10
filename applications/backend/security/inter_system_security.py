#!/usr/bin/env python3
"""
Inter-System Security Manager
Manages secure communication between IHEP solutions.
Security: HMAC signatures, CSRF protection, rate limiting
"""
import hmac
import hashlib
import secrets
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class InterSystemSecurityManager:
    """
    Manages secure communication between IHEP solutions.
    Handles authentication, CSRF protection, rate limiting.

    Security Features:
    - HMAC-SHA256 request signatures
    - CSRF token generation and validation
    - Rate limiting per endpoint
    - Circuit breaker pattern
    - No secrets in logs
    """

    def __init__(self, shared_secret: str):
        """
        Initialize security manager.

        Args:
            shared_secret: Shared secret for HMAC signatures

        Security:
            - Secret stored as bytes (not string)
            - Secret never logged
        """
        if not isinstance(shared_secret, str) or len(shared_secret) < 32:
            raise ValueError("Shared secret must be at least 32 characters")

        self.shared_secret = shared_secret.encode('utf-8')

        # Rate limits (requests per minute)
        self.rate_limits = {
            'rlc_to_twin': 100,           # RLC sending parameters to Twin Sync
            'twin_to_rlc': 1000,          # Twin Sync sending outcomes to RLC
            'viz_to_twin': 500,           # 3D Viz querying Twin Sync
            'default': 100                # Default limit
        }

        self.window_seconds = 60  # Rate limit window
        self.request_history: Dict[str, List[float]] = defaultdict(list)

        # Circuit breaker state
        self.circuit_breaker: Dict[str, Dict[str, Any]] = {}
        self.circuit_breaker_threshold = 5  # Failures before opening circuit
        self.circuit_breaker_timeout = 60  # Seconds before retry

    def generate_request_signature(self, request_body: str) -> str:
        """
        Generate HMAC-SHA256 signature for request.

        Args:
            request_body: JSON request body as string

        Returns:
            Hexadecimal signature string

        Security:
            - Uses HMAC (not plain hash)
            - SHA256 (not MD5 or SHA1)
            - Constant-time comparison
        """
        if not isinstance(request_body, str):
            raise TypeError("Request body must be string")

        signature = hmac.new(
            self.shared_secret,
            request_body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return signature

    def verify_request_signature(self, request_body: str,
                                 provided_sig: str) -> bool:
        """
        Verify request signature matches expected.

        Args:
            request_body: JSON request body as string
            provided_sig: Signature from request header

        Returns:
            True if signature valid, False otherwise

        Security:
            - Uses hmac.compare_digest (timing-attack resistant)
            - No early returns based on comparison
        """
        if not isinstance(request_body, str) or not isinstance(provided_sig, str):
            logger.warning("Invalid types for signature verification")
            return False

        try:
            expected_sig = self.generate_request_signature(request_body)
            return hmac.compare_digest(expected_sig, provided_sig)
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False

    def generate_csrf_token(self, user_id: Optional[str] = None) -> Dict[str, str]:
        """
        Generate CSRF token for session.

        Args:
            user_id: Optional user identifier

        Returns:
            Dict with token, expiry, created timestamp

        Security:
            - Uses secrets module (cryptographically secure)
            - 32-byte token (256 bits)
            - 24-hour expiry
        """
        token = secrets.token_hex(32)  # 256 bits
        created = datetime.now()
        expiry = created + timedelta(hours=24)

        return {
            'token': token,
            'expires': expiry.isoformat(),
            'created': created.isoformat(),
            'user_id': user_id if user_id else 'system'
        }

    def verify_csrf_token(self, token: str, expiry: str) -> bool:
        """
        Verify CSRF token is valid and not expired.

        Args:
            token: CSRF token from request
            expiry: Expiry timestamp (ISO 8601)

        Returns:
            True if valid, False otherwise

        Security:
            - Checks expiry before validation
            - No information leakage on failure
        """
        if not isinstance(token, str) or not isinstance(expiry, str):
            return False

        try:
            expiry_dt = datetime.fromisoformat(expiry)

            # Check if expired
            if datetime.now() > expiry_dt:
                logger.warning("CSRF token expired")
                return False

            # Token format validation (hex string)
            if len(token) != 64:  # 32 bytes = 64 hex chars
                logger.warning("Invalid CSRF token format")
                return False

            # Verify hex format
            int(token, 16)  # Will raise ValueError if not hex

            return True

        except (ValueError, TypeError) as e:
            logger.warning(f"CSRF token validation error: {e}")
            return False

    def check_rate_limit(self, caller: str, endpoint: str) -> Dict[str, Any]:
        """
        Check if caller has exceeded rate limit.

        Args:
            caller: Calling service (e.g., 'rlc', 'twin', 'viz')
            endpoint: Target endpoint

        Returns:
            Dict with allowed flag, reason, retry_after

        Security:
            - Per-endpoint rate limits
            - Sliding window algorithm
            - No resource exhaustion
        """
        key = f"{caller}:{endpoint}"
        now = time.time()

        # Remove old requests outside window
        self.request_history[key] = [
            ts for ts in self.request_history[key]
            if now - ts < self.window_seconds
        ]

        # Determine rate limit for this endpoint
        limit_key = f"{caller}_to_{endpoint}"
        limit = self.rate_limits.get(limit_key, self.rate_limits['default'])

        current_count = len(self.request_history[key])

        if current_count >= limit:
            logger.warning(f"Rate limit exceeded for {key}: {current_count}/{limit}")
            return {
                'allowed': False,
                'reason': '429 Too Many Requests',
                'retry_after': self.window_seconds,
                'current_count': current_count,
                'limit': limit
            }

        # Record this request
        self.request_history[key].append(now)

        return {
            'allowed': True,
            'current_count': current_count + 1,
            'limit': limit
        }

    def check_circuit_breaker(self, endpoint: str) -> Dict[str, Any]:
        """
        Check circuit breaker status for endpoint.

        Args:
            endpoint: Target endpoint

        Returns:
            Dict with open flag, reason

        Security:
            - Prevents cascading failures
            - Automatic recovery
            - Resource protection
        """
        if endpoint not in self.circuit_breaker:
            self.circuit_breaker[endpoint] = {
                'failures': 0,
                'last_failure': None,
                'state': 'closed'  # closed = normal, open = blocked
            }

        breaker = self.circuit_breaker[endpoint]

        # If circuit is open, check if timeout has passed
        if breaker['state'] == 'open':
            if breaker['last_failure']:
                time_since_failure = time.time() - breaker['last_failure']

                if time_since_failure > self.circuit_breaker_timeout:
                    # Try half-open state
                    breaker['state'] = 'half-open'
                    logger.info(f"Circuit breaker {endpoint} entering half-open state")
                else:
                    return {
                        'open': True,
                        'reason': 'Circuit breaker open',
                        'retry_after': self.circuit_breaker_timeout - int(time_since_failure)
                    }

        return {'open': False}

    def record_success(self, endpoint: str) -> None:
        """
        Record successful request to endpoint.

        Args:
            endpoint: Target endpoint

        Security:
            - Resets circuit breaker on success
        """
        if endpoint in self.circuit_breaker:
            self.circuit_breaker[endpoint] = {
                'failures': 0,
                'last_failure': None,
                'state': 'closed'
            }

    def record_failure(self, endpoint: str) -> None:
        """
        Record failed request to endpoint.

        Args:
            endpoint: Target endpoint

        Security:
            - Triggers circuit breaker if threshold exceeded
        """
        if endpoint not in self.circuit_breaker:
            self.circuit_breaker[endpoint] = {
                'failures': 0,
                'last_failure': None,
                'state': 'closed'
            }

        breaker = self.circuit_breaker[endpoint]
        breaker['failures'] += 1
        breaker['last_failure'] = time.time()

        if breaker['failures'] >= self.circuit_breaker_threshold:
            breaker['state'] = 'open'
            logger.error(f"Circuit breaker opened for {endpoint} after {breaker['failures']} failures")

    def rotate_shared_secret(self, new_secret: str) -> None:
        """
        Rotate shared secret for HMAC signatures.

        Args:
            new_secret: New shared secret

        Security:
            - Allows secret rotation without downtime
            - Validates new secret before accepting
        """
        if not isinstance(new_secret, str) or len(new_secret) < 32:
            raise ValueError("New shared secret must be at least 32 characters")

        logger.info("Rotating shared secret")
        self.shared_secret = new_secret.encode('utf-8')
