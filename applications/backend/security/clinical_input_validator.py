#!/usr/bin/env python3
"""
Clinical Input Validator Module
Validates all clinical data before entering the Twin Sync system.
Security: No eval/exec, all input validated, prevents XSS/injection attacks
"""
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class ClinicalInputValidator:
    """
    Validates clinical data according to healthcare standards.
    Prevents malicious input, garbage data, and invalid formats.

    Security Features:
    - No code execution (no eval/exec)
    - Regex-based pattern matching only
    - Input length limits
    - Type checking
    - Range validation for clinical values
    """

    def __init__(self):
        self.config = {
            'max_text_length': 100000,
            'max_file_size': 100 * 1024 * 1024,  # 100MB
            'allowed_file_types': [
                'application/pdf',
                'image/dicom',
                'image/jpeg',
                'image/png'
            ],
            'lab_value_ranges': {
                'cd4_count': {'min': 0, 'max': 2000, 'unit': 'cells/µL'},
                'viral_load': {'min': 0, 'max': 10000000, 'unit': 'copies/mL'},
                'hemoglobin': {'min': 5.0, 'max': 20.0, 'unit': 'g/dL'},
                'glucose': {'min': 20, 'max': 600, 'unit': 'mg/dL'},
                'blood_pressure_systolic': {'min': 60, 'max': 250, 'unit': 'mmHg'},
                'blood_pressure_diastolic': {'min': 40, 'max': 150, 'unit': 'mmHg'},
                'heart_rate': {'min': 30, 'max': 250, 'unit': 'bpm'},
                'respiratory_rate': {'min': 8, 'max': 60, 'unit': 'breaths/min'},
                'temperature': {'min': 95.0, 'max': 107.0, 'unit': '°F'},
                'oxygen_saturation': {'min': 50, 'max': 100, 'unit': '%'}
            }
        }

        # Security: Forbidden patterns to prevent XSS, injection attacks
        self.forbidden_patterns = [
            r'<script',
            r'javascript:',
            r'on\w+\s*=',  # onclick=, onload=, etc.
            r'<iframe',
            r'<object',
            r'<embed',
            r'data:text/html',
            r'vbscript:',
            r'<form',
            r'<input',
            r'<link',
            r'<meta',
            r'document\.cookie',
            r'window\.location',
            r'eval\(',
            r'setTimeout\(',
            r'setInterval\('
        ]

    def validate_clinical_note(self, text: str) -> Dict[str, Any]:
        """
        Validate a clinical note for safety and quality.

        Args:
            text: Clinical note text

        Returns:
            Dict with keys: valid (bool), error (str), sanitized (str)

        Security:
            - Checks for XSS patterns
            - Enforces length limits
            - Sanitizes control characters
        """
        result = {'valid': False, 'error': None, 'sanitized': None}

        # Type validation
        if not isinstance(text, str):
            result['error'] = 'Clinical note must be text'
            logger.warning(f"Invalid type for clinical note: {type(text)}")
            return result

        # Length validation
        if len(text) > self.config['max_text_length']:
            result['error'] = f'Note too long. Max {self.config["max_text_length"]} chars'
            logger.warning(f"Clinical note too long: {len(text)} chars")
            return result

        # Empty text
        if not text.strip():
            result['error'] = 'Clinical note cannot be empty'
            return result

        # Security: Check for malicious patterns
        if self._contains_malicious_patterns(text):
            result['error'] = 'Note contains invalid patterns'
            logger.error(f"Malicious pattern detected in clinical note")
            return result

        # Sanitize and return
        result['sanitized'] = self._sanitize_text(text)
        result['valid'] = True
        return result

    def validate_lab_value(self, field: str, value: float) -> Dict[str, Any]:
        """
        Validate a lab value against medical ranges.

        Args:
            field: Lab test name (e.g., 'cd4_count')
            value: Numeric value

        Returns:
            Dict with keys: valid (bool), error (str), flagged (bool)

        Security:
            - Type checking
            - Range validation
            - No arithmetic on untrusted input
        """
        result = {'valid': False, 'error': None, 'flagged': False}

        # Type validation
        if not isinstance(value, (int, float)):
            result['error'] = f'Lab value must be numeric, got {type(value)}'
            return result

        # Check for NaN, Infinity
        if not (-float('inf') < value < float('inf')):
            result['error'] = 'Lab value must be finite number'
            return result

        # Field validation
        if field not in self.config['lab_value_ranges']:
            result['error'] = f'Unknown lab field: {field}'
            logger.warning(f"Validation attempted for unknown lab field: {field}")
            return result

        range_spec = self.config['lab_value_ranges'][field]

        # Range validation
        if value < range_spec['min'] or value > range_spec['max']:
            result['error'] = f'Out of range: {value} {range_spec["unit"]}'
            result['flagged'] = True  # Alert clinical team but don't reject
            logger.warning(f"Lab value out of range: {field}={value} {range_spec['unit']}")

        result['valid'] = True
        return result

    def validate_clinical_date(self, date_str: str) -> Dict[str, Any]:
        """
        Validate date is in ISO 8601 format and reasonable.

        Args:
            date_str: ISO 8601 date string

        Returns:
            Dict with keys: valid (bool), error (str), parsed (datetime)

        Security:
            - Uses standard library datetime (no eval)
            - Validates date ranges
            - Prevents future manipulation
        """
        result = {'valid': False, 'error': None, 'parsed': None}

        # Type validation
        if not isinstance(date_str, str):
            result['error'] = 'Date must be string'
            return result

        try:
            # Security: Use standard library parsing only
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))

            # No future dates > 30 days (prevents data manipulation)
            if dt > datetime.now(dt.tzinfo) + timedelta(days=30):
                result['error'] = 'Date too far in future'
                logger.warning(f"Future date rejected: {date_str}")
                return result

            # No dates > 10 years in past (data quality check)
            if dt < datetime.now(dt.tzinfo) - timedelta(days=3650):
                result['error'] = 'Date too old (data quality check)'
                result['valid'] = True  # Log warning but don't reject
                result['parsed'] = dt
                logger.warning(f"Very old date: {date_str}")
            else:
                result['valid'] = True
                result['parsed'] = dt

        except ValueError as e:
            result['error'] = f'Date must be ISO 8601 format: {str(e)}'
            logger.warning(f"Invalid date format: {date_str}")

        return result

    def validate_file_upload(self, filename: str, content_type: str,
                           file_size: int) -> Dict[str, Any]:
        """
        Validate clinical file upload.

        Args:
            filename: Original filename
            content_type: MIME type
            file_size: File size in bytes

        Returns:
            Dict with keys: valid (bool), error (str), sanitized_filename (str)

        Security:
            - Filename sanitization (prevents path traversal)
            - MIME type validation
            - File size limits
        """
        result = {'valid': False, 'error': None, 'sanitized_filename': None}

        # Size validation
        if file_size > self.config['max_file_size']:
            result['error'] = f'File too large. Max {self.config["max_file_size"] / (1024*1024):.0f}MB'
            return result

        # MIME type validation
        if content_type not in self.config['allowed_file_types']:
            result['error'] = f'File type not allowed: {content_type}'
            logger.warning(f"Rejected file type: {content_type}")
            return result

        # Filename sanitization (prevent path traversal)
        sanitized = self._sanitize_filename(filename)
        if not sanitized:
            result['error'] = 'Invalid filename'
            return result

        result['valid'] = True
        result['sanitized_filename'] = sanitized
        return result

    def _contains_malicious_patterns(self, text: str) -> bool:
        """
        Check for patterns that indicate attempted injection.

        Security:
            - Regex matching only (no code execution)
            - Case-insensitive matching
            - Returns boolean (safe)
        """
        return any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in self.forbidden_patterns
        )

    def _sanitize_text(self, text: str) -> str:
        """
        Remove control characters and normalize whitespace.

        Security:
            - Removes control characters (except \n, \t)
            - Normalizes whitespace
            - No code execution
        """
        # Remove control characters except newlines and tabs
        text = ''.join(c for c in text if ord(c) >= 32 or c in '\n\t')

        # Normalize whitespace (collapse multiple spaces)
        text = ' '.join(text.split())

        return text.strip()

    def _sanitize_filename(self, filename: str) -> Optional[str]:
        """
        Sanitize filename to prevent path traversal attacks.

        Security:
            - Removes path separators
            - Removes special characters
            - Limits length
        """
        if not filename:
            return None

        # Remove path separators
        filename = filename.replace('/', '').replace('\\', '').replace('..', '')

        # Remove non-alphanumeric except .-_
        filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)

        # Limit length
        if len(filename) > 255:
            filename = filename[:255]

        if not filename:
            return None

        return filename
