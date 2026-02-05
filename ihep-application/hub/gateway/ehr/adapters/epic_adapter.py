"""
Epic Systems EHR Adapter

SMART on FHIR integration with Epic App Orchard.
Supports OAuth 2.0 + PKCE authentication and FHIR R4 API.

Epic Market Share: 31% of hospital EHR market
Patient Records: 305+ million via App Orchard

Requirements:
- Epic App Orchard registration and validation
- SMART on FHIR app approval (2-3 months sandbox + 2-3 weeks review)
- Production credentials from each healthcare system

Author: Jason M Jarmacz | Evolution Strategist | jason@ihep.app
Co-Author: Claude by Anthropic
"""

import base64
import hashlib
import logging
import secrets
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlencode

import requests

from .base_adapter import (
    AdapterConfig,
    BaseEHRAdapter,
    ConnectionStatus,
    EHRVendor,
    FHIRResource,
    SyncResult,
)

logger = logging.getLogger(__name__)


class EpicAdapter(BaseEHRAdapter):
    """
    Epic Systems adapter using SMART on FHIR protocol.

    Authentication Flow:
    1. Generate PKCE code verifier and challenge
    2. Redirect user to Epic authorization endpoint
    3. Exchange authorization code for access token
    4. Use access token for FHIR API calls
    5. Refresh token before expiry

    Supported FHIR Resources:
    - Patient (R4)
    - Observation (R4)
    - Appointment (R4)
    - CarePlan (R4)
    - Condition (R4)
    - MedicationStatement (R4)
    - AllergyIntolerance (R4)
    - Immunization (R4)

    Rate Limits:
    - 100 requests per minute (standard)
    - Bulk operations have separate limits
    """

    # Epic FHIR endpoint paths
    FHIR_VERSION = "R4"
    METADATA_PATH = "/metadata"

    # Default scopes for IHEP integration
    DEFAULT_SCOPES = [
        "patient/Patient.read",
        "patient/Observation.read",
        "patient/Observation.write",
        "patient/Appointment.read",
        "patient/CarePlan.read",
        "patient/Condition.read",
        "patient/MedicationStatement.read",
        "patient/AllergyIntolerance.read",
        "launch/patient",
        "openid",
        "fhirUser",
    ]

    # LOINC codes for common observations
    VITAL_SIGNS_CODES = {
        "heart_rate": "8867-4",
        "blood_pressure_systolic": "8480-6",
        "blood_pressure_diastolic": "8462-4",
        "oxygen_saturation": "2708-6",
        "body_temperature": "8310-5",
        "body_weight": "29463-7",
        "body_height": "8302-2",
        "bmi": "39156-5",
        "respiratory_rate": "9279-1",
    }

    def __init__(
        self,
        config: AdapterConfig,
        audit_logger: Optional[Callable] = None
    ):
        """
        Initialize Epic adapter.

        Args:
            config: Adapter configuration with Epic credentials
            audit_logger: Optional audit logging callback
        """
        super().__init__(config, audit_logger)

        # Validate Epic-specific configuration
        if not config.base_url:
            raise ValueError("Epic base_url is required")
        if not config.client_id:
            raise ValueError("Epic client_id is required")

        # Set default scopes if not provided
        if not config.scopes:
            config.scopes = self.DEFAULT_SCOPES

        # PKCE state
        self._code_verifier: Optional[str] = None
        self._code_challenge: Optional[str] = None
        self._state: Optional[str] = None

        # Token storage
        self._refresh_token: Optional[str] = None
        self._patient_id: Optional[str] = None

        # Discover endpoints from metadata
        self._auth_url: Optional[str] = None
        self._token_url: Optional[str] = None

    def _generate_pkce_pair(self) -> tuple:
        """
        Generate PKCE code verifier and challenge.

        PKCE (Proof Key for Code Exchange) prevents authorization code
        interception attacks.

        Returns:
            Tuple of (code_verifier, code_challenge)
        """
        # Generate 32-byte random verifier (43 chars base64url)
        code_verifier = secrets.token_urlsafe(32)

        # Create SHA256 hash and base64url encode
        digest = hashlib.sha256(code_verifier.encode()).digest()
        code_challenge = base64.urlsafe_b64encode(digest).decode().rstrip('=')

        return code_verifier, code_challenge

    def _discover_endpoints(self) -> bool:
        """
        Discover OAuth endpoints from FHIR metadata.

        Epic provides authorization URLs in the CapabilityStatement.

        Returns:
            True if endpoints discovered successfully
        """
        try:
            metadata_url = f"{self.config.base_url}{self.METADATA_PATH}"
            response = requests.get(
                metadata_url,
                headers={"Accept": "application/fhir+json"},
                timeout=self.config.timeout_seconds
            )
            response.raise_for_status()

            metadata = response.json()

            # Extract OAuth endpoints from security extension
            for rest in metadata.get("rest", []):
                security = rest.get("security", {})
                for extension in security.get("extension", []):
                    if extension.get("url") == "http://fhir-registry.smarthealthit.org/StructureDefinition/oauth-uris":
                        for ext in extension.get("extension", []):
                            if ext.get("url") == "authorize":
                                self._auth_url = ext.get("valueUri")
                            elif ext.get("url") == "token":
                                self._token_url = ext.get("valueUri")

            if not self._auth_url or not self._token_url:
                logger.error("OAuth endpoints not found in Epic metadata")
                return False

            logger.info(f"Discovered Epic OAuth endpoints for {self.config.partner_id}")
            return True

        except requests.RequestException as e:
            logger.error(f"Failed to discover Epic endpoints: {e}")
            return False

    def get_authorization_url(self, redirect_uri: str) -> str:
        """
        Generate Epic authorization URL for OAuth flow.

        Args:
            redirect_uri: URL to redirect after authorization

        Returns:
            Authorization URL to redirect user to
        """
        if not self._auth_url:
            if not self._discover_endpoints():
                raise ConnectionError("Unable to discover Epic OAuth endpoints")

        # Generate PKCE pair
        self._code_verifier, self._code_challenge = self._generate_pkce_pair()
        self._state = secrets.token_urlsafe(16)

        params = {
            "response_type": "code",
            "client_id": self.config.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(self.config.scopes),
            "state": self._state,
            "aud": self.config.base_url,
            "code_challenge": self._code_challenge,
            "code_challenge_method": "S256",
        }

        return f"{self._auth_url}?{urlencode(params)}"

    def authenticate(self, authorization_code: Optional[str] = None, redirect_uri: Optional[str] = None) -> bool:
        """
        Complete OAuth authentication with Epic.

        For backend-only auth (client credentials), call without parameters.
        For user auth (authorization code), provide code and redirect_uri.

        Args:
            authorization_code: OAuth authorization code from redirect
            redirect_uri: Redirect URI used in authorization request

        Returns:
            True if authentication successful
        """
        self._status = ConnectionStatus.CONNECTING

        try:
            # Discover endpoints if not already done
            if not self._token_url:
                if not self._discover_endpoints():
                    self._status = ConnectionStatus.ERROR
                    return False

            # Prepare token request
            if authorization_code and redirect_uri:
                # Authorization code flow
                if not self._code_verifier:
                    logger.error("PKCE code verifier not found")
                    self._status = ConnectionStatus.ERROR
                    return False

                data = {
                    "grant_type": "authorization_code",
                    "code": authorization_code,
                    "redirect_uri": redirect_uri,
                    "client_id": self.config.client_id,
                    "code_verifier": self._code_verifier,
                }
            else:
                # Client credentials flow (backend-only)
                data = {
                    "grant_type": "client_credentials",
                    "client_id": self.config.client_id,
                    "scope": " ".join(self.config.scopes),
                }

            # Add client secret if available
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            if self.config.client_secret:
                # Use Basic auth for client secret
                credentials = base64.b64encode(
                    f"{self.config.client_id}:{self.config.client_secret}".encode()
                ).decode()
                headers["Authorization"] = f"Basic {credentials}"

            response = requests.post(
                self._token_url,
                data=data,
                headers=headers,
                timeout=self.config.timeout_seconds
            )

            if response.status_code != 200:
                logger.error(f"Epic token request failed: {response.status_code} - {response.text}")
                self._status = ConnectionStatus.ERROR
                return False

            token_data = response.json()

            self._access_token = token_data.get("access_token")
            self._refresh_token = token_data.get("refresh_token")
            self._patient_id = token_data.get("patient")

            # Calculate token expiry
            expires_in = token_data.get("expires_in", 3600)
            self._token_expiry = datetime.utcnow() + timedelta(seconds=expires_in - 60)

            self._status = ConnectionStatus.CONNECTED
            self._log_audit("AUTHENTICATE", "OAuth", success=True)

            logger.info(f"Successfully authenticated with Epic for {self.config.partner_id}")
            return True

        except Exception as e:
            logger.error(f"Epic authentication failed: {e}")
            self._status = ConnectionStatus.ERROR
            self._log_audit("AUTHENTICATE", "OAuth", success=False, details={"error": str(e)})
            return False

    def refresh_token(self) -> bool:
        """
        Refresh OAuth access token.

        Returns:
            True if token refreshed successfully
        """
        if not self._refresh_token:
            logger.warning("No refresh token available")
            return self.authenticate()

        try:
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token,
                "client_id": self.config.client_id,
            }

            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            if self.config.client_secret:
                credentials = base64.b64encode(
                    f"{self.config.client_id}:{self.config.client_secret}".encode()
                ).decode()
                headers["Authorization"] = f"Basic {credentials}"

            response = requests.post(
                self._token_url,
                data=data,
                headers=headers,
                timeout=self.config.timeout_seconds
            )

            if response.status_code != 200:
                logger.error(f"Epic token refresh failed: {response.status_code}")
                return False

            token_data = response.json()
            self._access_token = token_data.get("access_token")
            self._refresh_token = token_data.get("refresh_token", self._refresh_token)

            expires_in = token_data.get("expires_in", 3600)
            self._token_expiry = datetime.utcnow() + timedelta(seconds=expires_in - 60)

            logger.info("Successfully refreshed Epic access token")
            return True

        except Exception as e:
            logger.error(f"Epic token refresh failed: {e}")
            return False

    def _ensure_authenticated(self) -> None:
        """Ensure we have a valid access token."""
        if not self._access_token:
            raise ConnectionError("Not authenticated with Epic")

        if self._token_expiry and datetime.utcnow() >= self._token_expiry:
            if not self.refresh_token():
                raise ConnectionError("Failed to refresh Epic access token")

    def _extract_error_summary(self, response) -> str:
        """
        Extract error summary from FHIR response without exposing PHI.

        Returns only the error code and type from OperationOutcome,
        never patient data or detailed error messages that may contain PHI.
        """
        try:
            data = response.json()
            if data.get("resourceType") == "OperationOutcome":
                issues = data.get("issue", [])
                if issues:
                    # Only extract severity and code, not diagnostics which may contain PHI
                    first_issue = issues[0]
                    severity = first_issue.get("severity", "unknown")
                    code = first_issue.get("code", "unknown")
                    return f"OperationOutcome: {severity}/{code}"
            return f"HTTP {response.status_code}"
        except Exception:
            return f"HTTP {response.status_code}"

    def _fhir_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict] = None,
        json_body: Optional[Dict] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Make authenticated FHIR API request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: FHIR resource path
            params: Query parameters
            json_body: JSON request body

        Returns:
            Response JSON or None if failed
        """
        self._ensure_authenticated()

        url = f"{self.config.base_url}{path}"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Accept": "application/fhir+json",
            "Content-Type": "application/fhir+json",
        }
        headers.update(self.config.custom_headers)

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_body,
                timeout=self.config.timeout_seconds
            )

            if response.status_code == 429:
                # Rate limited
                self._status = ConnectionStatus.RATE_LIMITED
                retry_after = response.headers.get("Retry-After", 60)
                logger.warning(f"Epic rate limited, retry after {retry_after}s")
                return None

            if response.status_code == 401:
                # Token expired, try refresh
                if self.refresh_token():
                    return self._fhir_request(method, path, params, json_body)
                return None

            if response.status_code >= 400:
                # Log error without exposing potential PHI in response body
                # Extract only the error code/type from FHIR OperationOutcome if present
                error_summary = self._extract_error_summary(response)
                logger.error(f"Epic FHIR request failed: {response.status_code} - {error_summary}")
                return None

            if response.status_code == 204:
                return {}

            return response.json()

        except requests.RequestException as e:
            logger.error(f"Epic FHIR request error: {e}")
            return None

    def _parse_bundle(self, bundle: Dict[str, Any], resource_type: str) -> List[FHIRResource]:
        """Parse FHIR Bundle into list of FHIRResource objects."""
        resources = []
        for entry in bundle.get("entry", []):
            resource = entry.get("resource", {})
            if resource.get("resourceType") == resource_type:
                resources.append(FHIRResource(
                    resource_type=resource_type,
                    resource_id=resource.get("id", ""),
                    data=resource,
                    source_system=f"epic:{self.config.partner_id}",
                    version_id=resource.get("meta", {}).get("versionId"),
                    last_updated=resource.get("meta", {}).get("lastUpdated"),
                ))
        return resources

    # === Patient Operations ===

    def fetch_patient(self, patient_id: str) -> Optional[FHIRResource]:
        """Retrieve patient by ID."""
        self._log_audit("FETCH_PATIENT", "Patient", patient_id)

        response = self._fhir_request("GET", f"/Patient/{patient_id}")
        if not response:
            return None

        return FHIRResource(
            resource_type="Patient",
            resource_id=response.get("id", patient_id),
            data=response,
            source_system=f"epic:{self.config.partner_id}",
            version_id=response.get("meta", {}).get("versionId"),
        )

    def search_patients(
        self,
        family_name: Optional[str] = None,
        given_name: Optional[str] = None,
        birthdate: Optional[str] = None,
        identifier: Optional[str] = None,
        limit: int = 100
    ) -> List[FHIRResource]:
        """Search for patients."""
        params = {"_count": min(limit, 100)}

        if family_name:
            params["family"] = family_name
        if given_name:
            params["given"] = given_name
        if birthdate:
            params["birthdate"] = birthdate
        if identifier:
            params["identifier"] = identifier

        self._log_audit("SEARCH_PATIENTS", "Patient", details={"params": params})

        response = self._fhir_request("GET", "/Patient", params=params)
        if not response:
            return []

        return self._parse_bundle(response, "Patient")

    # === Observation Operations ===

    def fetch_observations(
        self,
        patient_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        category: Optional[str] = None,
        codes: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[FHIRResource]:
        """Retrieve patient observations."""
        params = {
            "patient": patient_id,
            "_count": min(limit, 100),
            "_sort": "-date",
        }

        if start_date:
            params["date"] = f"ge{start_date}"
        if end_date:
            params["date"] = params.get("date", "") + f"&date=le{end_date}" if "date" in params else f"le{end_date}"
        if category:
            params["category"] = category
        if codes:
            params["code"] = ",".join(codes)

        self._log_audit("FETCH_OBSERVATIONS", "Observation", patient_id, details={"params": params})

        response = self._fhir_request("GET", "/Observation", params=params)
        if not response:
            return []

        return self._parse_bundle(response, "Observation")

    def push_observation(self, patient_id: str, observation: Dict[str, Any]) -> Optional[str]:
        """Write observation to Epic."""
        # Ensure patient reference
        observation["subject"] = {"reference": f"Patient/{patient_id}"}

        self._log_audit("PUSH_OBSERVATION", "Observation", patient_id)

        response = self._fhir_request("POST", "/Observation", json_body=observation)
        if not response:
            return None

        return response.get("id")

    # === Appointment Operations ===

    def fetch_appointments(
        self,
        patient_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[FHIRResource]:
        """Retrieve patient appointments."""
        params = {
            "patient": patient_id,
            "_count": min(limit, 100),
            "_sort": "date",
        }

        if start_date:
            params["date"] = f"ge{start_date}"
        if end_date:
            if "date" in params:
                params["date"] += f"&date=le{end_date}"
            else:
                params["date"] = f"le{end_date}"
        if status:
            params["status"] = status

        self._log_audit("FETCH_APPOINTMENTS", "Appointment", patient_id)

        response = self._fhir_request("GET", "/Appointment", params=params)
        if not response:
            return []

        return self._parse_bundle(response, "Appointment")

    def create_appointment(self, appointment: Dict[str, Any]) -> Optional[str]:
        """Create appointment in Epic."""
        self._log_audit("CREATE_APPOINTMENT", "Appointment")

        response = self._fhir_request("POST", "/Appointment", json_body=appointment)
        if not response:
            return None

        return response.get("id")

    # === Care Plan Operations ===

    def fetch_care_plans(
        self,
        patient_id: str,
        status: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[FHIRResource]:
        """Retrieve patient care plans."""
        params = {"patient": patient_id}

        if status:
            params["status"] = status
        if category:
            params["category"] = category

        self._log_audit("FETCH_CARE_PLANS", "CarePlan", patient_id)

        response = self._fhir_request("GET", "/CarePlan", params=params)
        if not response:
            return []

        return self._parse_bundle(response, "CarePlan")

    # === Condition Operations ===

    def fetch_conditions(
        self,
        patient_id: str,
        clinical_status: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[FHIRResource]:
        """Retrieve patient conditions."""
        params = {"patient": patient_id}

        if clinical_status:
            params["clinical-status"] = clinical_status
        if category:
            params["category"] = category

        self._log_audit("FETCH_CONDITIONS", "Condition", patient_id)

        response = self._fhir_request("GET", "/Condition", params=params)
        if not response:
            return []

        return self._parse_bundle(response, "Condition")

    # === Medication Operations ===

    def fetch_medications(
        self,
        patient_id: str,
        status: Optional[str] = None
    ) -> List[FHIRResource]:
        """Retrieve patient medications."""
        params = {"patient": patient_id}

        if status:
            params["status"] = status

        self._log_audit("FETCH_MEDICATIONS", "MedicationStatement", patient_id)

        response = self._fhir_request("GET", "/MedicationStatement", params=params)
        if not response:
            return []

        return self._parse_bundle(response, "MedicationStatement")

    # === Subscription Operations ===

    def subscribe_to_events(
        self,
        event_types: List[str],
        webhook_url: str,
        patient_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Create FHIR Subscription for real-time events.

        Note: Epic subscription support varies by implementation.
        """
        subscription = {
            "resourceType": "Subscription",
            "status": "requested",
            "reason": "IHEP real-time integration",
            "channel": {
                "type": "rest-hook",
                "endpoint": webhook_url,
                "payload": "application/fhir+json",
            },
            "criteria": "",
        }

        # Build criteria based on event types
        criteria_parts = []
        for event_type in event_types:
            if event_type == "patient-update":
                criteria_parts.append("Patient?")
            elif event_type == "observation-create":
                criteria_parts.append("Observation?")
            elif event_type == "appointment-create":
                criteria_parts.append("Appointment?")

        if patient_id:
            criteria_parts = [f"{c}patient={patient_id}" for c in criteria_parts]

        subscription["criteria"] = criteria_parts[0] if criteria_parts else "Patient?"

        self._log_audit("SUBSCRIBE", "Subscription", details={"event_types": event_types})

        response = self._fhir_request("POST", "/Subscription", json_body=subscription)
        if not response:
            return None

        return response.get("id")

    def unsubscribe(self, subscription_id: str) -> bool:
        """Remove subscription."""
        self._log_audit("UNSUBSCRIBE", "Subscription", subscription_id)

        response = self._fhir_request("DELETE", f"/Subscription/{subscription_id}")
        return response is not None

    # === Bulk Operations ===

    def bulk_fetch(
        self,
        resource_type: str,
        since: Optional[datetime] = None,
        patient_ids: Optional[List[str]] = None
    ) -> SyncResult:
        """
        Bulk fetch resources using Epic's bulk data export.

        Note: Requires backend services authorization.
        """
        start_time = time.time()
        result = SyncResult(success=False)

        try:
            params = {"_count": 1000}
            if since:
                params["_lastUpdated"] = f"ge{since.isoformat()}Z"

            all_resources = []
            next_url = f"/{resource_type}"

            while next_url:
                response = self._fhir_request("GET", next_url, params=params if "/" not in next_url else None)
                if not response:
                    break

                resources = self._parse_bundle(response, resource_type)
                all_resources.extend(resources)
                result.records_processed += len(resources)

                # Check for next page
                next_link = next(
                    (link for link in response.get("link", []) if link.get("relation") == "next"),
                    None
                )
                next_url = next_link.get("url") if next_link else None
                params = {}  # Params included in next URL

            result.success = True
            result.records_created = len(all_resources)

        except Exception as e:
            result.errors.append(str(e))
            logger.error(f"Epic bulk fetch failed: {e}")

        result.duration_ms = int((time.time() - start_time) * 1000)
        self._log_audit("BULK_FETCH", resource_type, details={
            "records": result.records_processed,
            "duration_ms": result.duration_ms
        })

        return result

    # === Health Check ===

    def health_check(self) -> Dict[str, Any]:
        """Check Epic connection health."""
        result = {
            "vendor": "epic",
            "partner_id": self.config.partner_id,
            "status": self._status.value,
            "connected": self.is_connected,
            "token_valid": False,
            "metadata_accessible": False,
            "latency_ms": None,
        }

        try:
            # Check token validity
            if self._access_token and self._token_expiry:
                result["token_valid"] = datetime.utcnow() < self._token_expiry

            # Check metadata endpoint
            start = time.time()
            response = requests.get(
                f"{self.config.base_url}{self.METADATA_PATH}",
                headers={"Accept": "application/fhir+json"},
                timeout=10
            )
            latency = int((time.time() - start) * 1000)

            result["metadata_accessible"] = response.status_code == 200
            result["latency_ms"] = latency

        except Exception as e:
            result["error"] = str(e)

        return result
