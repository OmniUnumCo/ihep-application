"""
Audit Logging Utility
Logs all PHI access and security events to Google Cloud Logging
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from google.cloud import logging as cloud_logging
from flask import request


class AuditLogger:
    """
    Audit Logger for HIPAA Compliance
    
    Properties:
    - P(log) = 1.0 (every access logged)
    - Tamper-resistant (Cloud Logging immutable)
    - Retention: 7 years minimum
    """
    
    def __init__(self):
        self.client = cloud_logging.Client()
        self.logger = self.client.logger('ihep-audit-log')
        self.local_logger = logging.getLogger(__name__)
    
    def log(
        self,
        user_id: str,
        action: str,
        resource: str,
        outcome: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log audit event
        
        Args:
            user_id: ID of user performing action
            action: Action type (LOGIN, VIEW_PHI, UPDATE_PHI, etc.)
            resource: Resource accessed
            outcome: SUCCESS or FAILURE
            details: Additional context
        """
        ip_address = request.remote_addr if request else 'unknown'
        user_agent = request.headers.get('User-Agent', 'unknown') if request else 'unknown'
        
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'outcome': outcome,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'details': details or {}
        }
        
        # Log to Cloud Logging
        self.logger.log_struct(log_entry, severity='INFO')
        
        # Also log locally for development
        self.local_logger.info(f"AUDIT: {action} on {resource} by {user_id} - {outcome}")
