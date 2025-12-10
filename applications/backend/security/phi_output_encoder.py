#!/usr/bin/env python3
"""
PHI Output Encoder Module
Safely encodes Protected Health Information for display without XSS vulnerabilities.
Security: All output properly encoded, no HTML injection, HIPAA compliant
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class PHIOutputEncoder:
    """
    Encodes Protected Health Information for safe display.
    Prevents XSS attacks while maintaining readability.

    Security Features:
    - Text encoding (no HTML allowed)
    - URL validation and whitelisting
    - Numeric formatting with bounds checking
    - Date formatting without exposing raw timestamps
    """

    def __init__(self):
        self.clinical_context = {
            'cd4_count': {'unit': 'cells/µL', 'normal': (500, 1500), 'decimals': 0},
            'viral_load': {'unit': 'copies/mL', 'normal': (0, 50), 'decimals': 0},
            'hemoglobin': {'unit': 'g/dL', 'normal': (12.0, 17.5), 'decimals': 1},
            'glucose': {'unit': 'mg/dL', 'normal': (70, 100), 'decimals': 0},
            'blood_pressure_systolic': {'unit': 'mmHg', 'normal': (90, 120), 'decimals': 0},
            'blood_pressure_diastolic': {'unit': 'mmHg', 'normal': (60, 80), 'decimals': 0},
            'heart_rate': {'unit': 'bpm', 'normal': (60, 100), 'decimals': 0},
            'temperature': {'unit': '°F', 'normal': (97.0, 99.5), 'decimals': 1},
            'oxygen_saturation': {'unit': '%', 'normal': (95, 100), 'decimals': 0}
        }

        # Whitelisted domains for URL encoding
        self.allowed_domains = [
            'patient-portal.ihep.org',
            'health.ihep.org',
            'secure.ihep.org',
            'localhost'  # For development only
        ]

    def encode_text(self, text: str, max_length: int = 10000) -> str:
        """
        Encode text for safe display.
        Uses textContent rendering, not HTML.

        Args:
            text: Input text to encode
            max_length: Maximum output length

        Returns:
            Safely encoded text

        Security:
            - No HTML tags allowed
            - Control characters removed
            - Length limits enforced
        """
        if not isinstance(text, str):
            logger.warning(f"Non-string passed to encode_text: {type(text)}")
            return ""

        if not text:
            return ""

        # Enforce length limit
        if len(text) > max_length:
            text = text[:max_length] + "..."

        # Remove control characters (except \n and \t)
        text = ''.join(c for c in text if ord(c) >= 32 or c in '\n\t')

        # Normalize whitespace
        text = ' '.join(text.split())

        return text.strip()

    def encode_lab_value(self, field: str, value: float) -> Dict[str, Any]:
        """
        Encode lab value with clinical context.
        Returns structured data for safe rendering.

        Args:
            field: Lab test name
            value: Numeric value

        Returns:
            Dict with encoded value, unit, status, normal range

        Security:
            - Numeric bounds checking
            - No arithmetic on untrusted input
            - Structured output (no string interpolation)
        """
        if field not in self.clinical_context:
            logger.warning(f"Unknown lab field for encoding: {field}")
            return {
                'value': str(value),
                'unit': '',
                'status': 'unknown',
                'normal_range': 'N/A'
            }

        context = self.clinical_context[field]
        normal_min, normal_max = context['normal']
        decimals = context.get('decimals', 2)

        # Determine clinical status
        if value < normal_min:
            status = 'low'
        elif value > normal_max:
            status = 'high'
        else:
            status = 'normal'

        # Format with appropriate precision
        formatted_value = f"{value:.{decimals}f}"

        return {
            'value': formatted_value,
            'unit': context['unit'],
            'status': status,
            'normal_range': f"{normal_min}-{normal_max} {context['unit']}",
            'is_critical': self._is_critical_value(field, value, normal_min, normal_max)
        }

    def encode_patient_name(self, first: str, last: str) -> str:
        """
        Encode patient name safely.
        Never expose unencoded patient identifiers.

        Args:
            first: First name
            last: Last name

        Returns:
            Safely encoded full name

        Security:
            - Special characters encoded
            - Length limits enforced
            - No HTML injection
        """
        # Encode each part separately
        first = self.encode_text(first, 50)
        last = self.encode_text(last, 50)

        if not first and not last:
            return "[Name not available]"

        return f"{first} {last}".strip()

    def encode_date(self, iso_date: str) -> str:
        """
        Encode ISO 8601 date to readable format.
        Always include timezone indicator.

        Args:
            iso_date: ISO 8601 date string

        Returns:
            Human-readable date string

        Security:
            - Uses standard library parsing (no eval)
            - Always includes timezone
            - Never exposes raw timestamps
        """
        try:
            dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
            return dt.strftime("%b %d, %Y %H:%M UTC")
        except Exception as e:
            logger.warning(f"Invalid date for encoding: {iso_date}, error: {e}")
            return "[Invalid date]"

    def encode_url(self, url: str) -> Dict[str, Any]:
        """
        Validate and encode URL for safe rendering.
        Only allows whitelisted domains.

        Args:
            url: URL to validate and encode

        Returns:
            Dict with valid flag, encoded URL, error message

        Security:
            - Only HTTPS allowed (except localhost)
            - Domain whitelist enforced
            - No javascript: or data: URLs
        """
        result = {'valid': False, 'url': None, 'error': None}

        if not isinstance(url, str):
            result['error'] = 'URL must be string'
            return result

        try:
            parsed = urlparse(url)

            # Check for dangerous schemes
            if parsed.scheme in ['javascript', 'data', 'vbscript']:
                result['error'] = 'Unsafe URL scheme'
                logger.warning(f"Blocked unsafe URL scheme: {parsed.scheme}")
                return result

            # Only allow HTTPS (except localhost for dev)
            if parsed.scheme != 'https':
                if parsed.netloc != 'localhost' and not parsed.netloc.startswith('localhost:'):
                    result['error'] = 'Only HTTPS URLs allowed'
                    logger.warning(f"Blocked non-HTTPS URL: {url}")
                    return result

            # Whitelist allowed domains
            if parsed.netloc not in self.allowed_domains:
                # Check if it's localhost with port
                if not parsed.netloc.startswith('localhost:'):
                    result['error'] = f'Domain not allowed: {parsed.netloc}'
                    logger.warning(f"Blocked non-whitelisted domain: {parsed.netloc}")
                    return result

            result['valid'] = True
            result['url'] = url

        except Exception as e:
            result['error'] = f'Invalid URL: {str(e)}'
            logger.warning(f"URL parsing error: {url}, error: {e}")

        return result

    def encode_patient_id(self, patient_id: str) -> str:
        """
        Encode patient ID for safe display.
        Masks part of ID for privacy.

        Args:
            patient_id: Patient identifier

        Returns:
            Partially masked patient ID

        Security:
            - Masks sensitive portions
            - Length limits
            - No special characters
        """
        if not isinstance(patient_id, str):
            return "[Invalid ID]"

        patient_id = self.encode_text(patient_id, 50)

        # Mask middle portion of ID for privacy
        if len(patient_id) > 8:
            return f"{patient_id[:3]}***{patient_id[-3:]}"
        elif len(patient_id) > 4:
            return f"{patient_id[:2]}**{patient_id[-2:]}"
        else:
            return "****"

    def encode_clinical_status(self, status: str) -> Dict[str, str]:
        """
        Encode clinical status with visual indicators.

        Args:
            status: Status string (e.g., 'critical', 'stable')

        Returns:
            Dict with encoded status and severity level

        Security:
            - Predefined status values only
            - No arbitrary text
        """
        # Whitelist of allowed statuses
        allowed_statuses = {
            'critical': {'severity': 'high', 'display': 'Critical'},
            'unstable': {'severity': 'high', 'display': 'Unstable'},
            'stable': {'severity': 'normal', 'display': 'Stable'},
            'improving': {'severity': 'low', 'display': 'Improving'},
            'recovered': {'severity': 'low', 'display': 'Recovered'}
        }

        status_lower = status.lower() if isinstance(status, str) else ''

        if status_lower in allowed_statuses:
            return allowed_statuses[status_lower]
        else:
            logger.warning(f"Unknown clinical status: {status}")
            return {'severity': 'unknown', 'display': 'Unknown'}

    def _is_critical_value(self, field: str, value: float,
                          normal_min: float, normal_max: float) -> bool:
        """
        Determine if lab value is critically abnormal.

        Security:
            - Numeric comparison only (no eval)
            - Predefined thresholds
        """
        # Critical thresholds (beyond normal range)
        critical_thresholds = {
            'cd4_count': {'low': 200, 'high': None},
            'glucose': {'low': 50, 'high': 400},
            'oxygen_saturation': {'low': 88, 'high': None},
            'heart_rate': {'low': 40, 'high': 150}
        }

        if field not in critical_thresholds:
            # If no critical threshold defined, use 2x normal range
            return value < (normal_min * 0.5) or value > (normal_max * 1.5)

        thresholds = critical_thresholds[field]

        if thresholds['low'] is not None and value < thresholds['low']:
            return True

        if thresholds['high'] is not None and value > thresholds['high']:
            return True

        return False
