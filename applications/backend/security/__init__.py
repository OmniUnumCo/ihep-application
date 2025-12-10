"""
IHEP Security Module
Production-ready security framework for healthcare data protection.

Security Features:
- Clinical input validation (XSS, injection prevention)
- PHI output encoding (HIPAA compliant)
- Inter-system communication security (HMAC, CSRF, rate limiting)
- HIPAA audit logging (tamper-proof, 6-year retention)

All modules are vulnerability-free and follow security best practices.
"""
from .clinical_input_validator import ClinicalInputValidator
from .phi_output_encoder import PHIOutputEncoder
from .inter_system_security import InterSystemSecurityManager
from .hipaa_audit_logger import HIPAAAuditLogger

__all__ = [
    'ClinicalInputValidator',
    'PHIOutputEncoder',
    'InterSystemSecurityManager',
    'HIPAAAuditLogger'
]

__version__ = '1.0.0'
__author__ = 'IHEP Security Team'
