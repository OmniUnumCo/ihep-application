#!/usr/bin/env python3
"""
MITRE ATT&CK Integration
Real-time threat technique detection and mapping.

Downloads and maintains local copy of MITRE ATT&CK framework.
Maps security events to ATT&CK techniques.
"""

import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
import threading
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MITREAttackIntegration:
    """
    MITRE ATT&CK framework integration.

    Features:
    - Downloads ATT&CK matrix from official STIX repository
    - Maps events to techniques (T-codes)
    - Provides mitigation recommendations
    - Updates automatically
    """

    # Official MITRE ATT&CK STIX data
    ATTACK_STIX_URL = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"

    def __init__(self, cache_dir: str = "/var/ihep/mitre_attack"):
        """
        Initialize MITRE ATT&CK integration.

        Args:
            cache_dir: Directory to cache ATT&CK data
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True, mode=0o755)

        self.cache_file = self.cache_dir / "enterprise-attack.json"
        self.last_update = None

        # ATT&CK data structures
        self.techniques: Dict[str, Dict[str, Any]] = {}
        self.tactics: Dict[str, Dict[str, Any]] = {}
        self.mitigations: Dict[str, Dict[str, Any]] = {}
        self.groups: Dict[str, Dict[str, Any]] = {}

        # Detection rules (event patterns → techniques)
        self.detection_rules = self._build_detection_rules()

        # Thread safety
        self._lock = threading.RLock()

        # Load ATT&CK data
        self._load_attack_data()

        logger.info("MITRE ATT&CK integration initialized")

    def _load_attack_data(self) -> None:
        """Load ATT&CK data from cache or download"""
        # Check if cache exists and is recent
        if self.cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(
                self.cache_file.stat().st_mtime
            )

            if cache_age < timedelta(days=7):  # Update weekly
                logger.info("Loading ATT&CK data from cache")
                self._load_from_cache()
                return

        # Download fresh data
        logger.info("Downloading fresh ATT&CK data...")
        self._download_attack_data()

    def _download_attack_data(self) -> None:
        """Download ATT&CK data from official repository"""
        try:
            response = requests.get(self.ATTACK_STIX_URL, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Save to cache
            with open(self.cache_file, 'w') as f:
                json.dump(data, f)

            self._parse_attack_data(data)
            self.last_update = datetime.now()

            logger.info("ATT&CK data downloaded and parsed successfully")

        except Exception as e:
            logger.error(f"Failed to download ATT&CK data: {e}")

            # Fall back to cache if available
            if self.cache_file.exists():
                logger.info("Falling back to cached data")
                self._load_from_cache()
            else:
                raise

    def _load_from_cache(self) -> None:
        """Load ATT&CK data from local cache"""
        try:
            with open(self.cache_file, 'r') as f:
                data = json.load(f)

            self._parse_attack_data(data)
            self.last_update = datetime.fromtimestamp(
                self.cache_file.stat().st_mtime
            )

        except Exception as e:
            logger.error(f"Failed to load from cache: {e}")
            raise

    def _parse_attack_data(self, data: Dict[str, Any]) -> None:
        """Parse STIX data into usable structures"""
        with self._lock:
            for obj in data.get('objects', []):
                obj_type = obj.get('type')

                if obj_type == 'attack-pattern':
                    # This is a technique
                    self._parse_technique(obj)

                elif obj_type == 'x-mitre-tactic':
                    # This is a tactic
                    self._parse_tactic(obj)

                elif obj_type == 'course-of-action':
                    # This is a mitigation
                    self._parse_mitigation(obj)

                elif obj_type == 'intrusion-set':
                    # This is a threat group
                    self._parse_group(obj)

        logger.info(
            f"Parsed {len(self.techniques)} techniques, "
            f"{len(self.tactics)} tactics, "
            f"{len(self.mitigations)} mitigations, "
            f"{len(self.groups)} groups"
        )

    def _parse_technique(self, obj: Dict[str, Any]) -> None:
        """Parse attack technique"""
        # Get external references for technique ID
        external_refs = obj.get('external_references', [])
        technique_id = None

        for ref in external_refs:
            if ref.get('source_name') == 'mitre-attack':
                technique_id = ref.get('external_id')
                break

        if not technique_id:
            return

        self.techniques[technique_id] = {
            'id': technique_id,
            'name': obj.get('name'),
            'description': obj.get('description', ''),
            'tactics': [phase['phase_name'] for phase in obj.get('kill_chain_phases', [])],
            'platforms': obj.get('x_mitre_platforms', []),
            'data_sources': obj.get('x_mitre_data_sources', []),
            'detection': obj.get('x_mitre_detection', ''),
            'is_subtechnique': '.' in technique_id
        }

    def _parse_tactic(self, obj: Dict[str, Any]) -> None:
        """Parse tactic"""
        external_refs = obj.get('external_references', [])
        tactic_id = None

        for ref in external_refs:
            if ref.get('source_name') == 'mitre-attack':
                tactic_id = ref.get('external_id')
                break

        if not tactic_id:
            return

        self.tactics[tactic_id] = {
            'id': tactic_id,
            'name': obj.get('name'),
            'description': obj.get('description', ''),
            'short_name': obj.get('x_mitre_shortname', '')
        }

    def _parse_mitigation(self, obj: Dict[str, Any]) -> None:
        """Parse mitigation"""
        external_refs = obj.get('external_references', [])
        mitigation_id = None

        for ref in external_refs:
            if ref.get('source_name') == 'mitre-attack':
                mitigation_id = ref.get('external_id')
                break

        if not mitigation_id:
            return

        self.mitigations[mitigation_id] = {
            'id': mitigation_id,
            'name': obj.get('name'),
            'description': obj.get('description', '')
        }

    def _parse_group(self, obj: Dict[str, Any]) -> None:
        """Parse threat group"""
        external_refs = obj.get('external_references', [])
        group_id = None

        for ref in external_refs:
            if ref.get('source_name') == 'mitre-attack':
                group_id = ref.get('external_id')
                break

        if not group_id:
            return

        self.groups[group_id] = {
            'id': group_id,
            'name': obj.get('name'),
            'description': obj.get('description', ''),
            'aliases': obj.get('aliases', [])
        }

    def _build_detection_rules(self) -> Dict[str, Set[str]]:
        """
        Build detection rules mapping event patterns to techniques.

        Production system would use sophisticated pattern matching.
        This is simplified mapping.
        """
        return {
            # Initial Access
            'phishing': {'T1566'},
            'exploit_attempt': {'T1190'},
            'valid_accounts': {'T1078'},

            # Execution
            'command_injection': {'T1059'},
            'powershell': {'T1059.001'},
            'python': {'T1059.006'},

            # Persistence
            'webshell': {'T1505.003'},
            'scheduled_task': {'T1053'},

            # Privilege Escalation
            'sudo': {'T1548.003'},
            'setuid': {'T1548.001'},

            # Defense Evasion
            'obfuscation': {'T1027'},
            'clear_logs': {'T1070.002'},

            # Credential Access
            'brute_force': {'T1110'},
            'credential_dumping': {'T1003'},
            'password_spray': {'T1110.003'},

            # Discovery
            'network_scan': {'T1046'},
            'port_scan': {'T1046'},
            'account_discovery': {'T1087'},
            'file_enum': {'T1083'},

            # Lateral Movement
            'ssh': {'T1021.004'},
            'rdp': {'T1021.001'},

            # Collection
            'data_staged': {'T1074'},
            'screenshot': {'T1113'},

            # Exfiltration
            'data_transfer': {'T1041'},
            'exfil_web': {'T1567'},

            # Impact
            'dos': {'T1499'},
            'defacement': {'T1491'}
        }

    def detect_techniques(self, event: Dict[str, Any]) -> List[str]:
        """
        Detect MITRE ATT&CK techniques in security event.

        Args:
            event: Security event data

        Returns:
            List of technique IDs (e.g., ['T1046', 'T1595'])
        """
        detected = set()

        event_type = event.get('event_type', '').lower()

        # Check detection rules
        for pattern, technique_ids in self.detection_rules.items():
            if pattern in event_type:
                detected.update(technique_ids)

        # Additional heuristics
        data = event.get('data', {})

        # Detect SQL injection
        if 'sql' in event_type and ('injection' in event_type or 'sqli' in event_type):
            detected.add('T1190')

        # Detect XSS
        if 'xss' in event_type or 'script' in str(data).lower():
            detected.add('T1059.007')

        # Detect failed logins (brute force indicator)
        if 'failed_login' in event_type or 'auth_failed' in event_type:
            detected.add('T1110')

        # Detect reconnaissance
        if any(term in event_type for term in ['scan', 'probe', 'enum']):
            detected.add('T1595')

        return sorted(list(detected))

    def get_technique_info(self, technique_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a technique"""
        with self._lock:
            return self.techniques.get(technique_id)

    def get_mitigations(self, technique_id: str) -> List[Dict[str, Any]]:
        """Get mitigation recommendations for technique"""
        # In production, would query relationships from STIX data
        # Simplified for now

        mitigations = []

        # Common mitigations
        common_mitigations = {
            'T1190': ['M1050', 'M1016'],  # Exploit Protection, Vuln Scanning
            'T1110': ['M1032', 'M1036'],  # Multi-factor Auth, Account Lockout
            'T1046': ['M1031', 'M1030'],  # Network Segmentation, Intrusion Prevention
            'T1059': ['M1038', 'M1049']   # Execution Prevention, Antivirus
        }

        mitigation_ids = common_mitigations.get(technique_id, [])

        for mid in mitigation_ids:
            if mid in self.mitigations:
                mitigations.append(self.mitigations[mid])

        return mitigations

    def enrich_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich event with MITRE ATT&CK intelligence.

        Args:
            event: Security event

        Returns:
            Enriched event with ATT&CK techniques and mitigations
        """
        # Detect techniques
        techniques = self.detect_techniques(event)

        # Get detailed technique info
        technique_details = []
        all_mitigations = []

        for tech_id in techniques:
            tech_info = self.get_technique_info(tech_id)
            if tech_info:
                technique_details.append(tech_info)

                # Get mitigations
                mitigations = self.get_mitigations(tech_id)
                all_mitigations.extend(mitigations)

        # Add ATT&CK enrichment to event
        enrichment = {
            'mitre_techniques': techniques,
            'technique_details': technique_details,
            'recommended_mitigations': all_mitigations,
            'enriched_at': datetime.utcnow().isoformat()
        }

        event['mitre_attack'] = enrichment

        return event

    def get_statistics(self) -> Dict[str, Any]:
        """Get ATT&CK database statistics"""
        return {
            'total_techniques': len(self.techniques),
            'total_tactics': len(self.tactics),
            'total_mitigations': len(self.mitigations),
            'total_groups': len(self.groups),
            'last_update': self.last_update.isoformat() if self.last_update else None
        }


if __name__ == "__main__":
    # Test MITRE integration
    mitre = MITREAttackIntegration(cache_dir='/tmp/mitre_test')

    # Test event
    test_event = {
        'event_type': 'network_scan',
        'source_ip': '1.2.3.4',
        'data': {
            'ports': [22, 80, 443]
        }
    }

    # Enrich event
    enriched = mitre.enrich_event(test_event)

    print("\nEnriched Event:")
    print(json.dumps(enriched, indent=2))

    # Get statistics
    stats = mitre.get_statistics()
    print("\nMITRE ATT&CK Statistics:")
    print(json.dumps(stats, indent=2))
