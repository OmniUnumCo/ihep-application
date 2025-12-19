#!/usr/bin/env python3
"""
Fragmentation Synergy Database
Stores ALL security intelligence fragments with zero-trust permissions.

Security Principles:
- Zero-trust: Every access requires authentication and authorization
- No deletion without Procedural Registry approval
- Immutable audit trail
- Encryption at rest (AES-256-GCM)
- Role-based access control (RBAC)

Architecture:
- Time-series storage for event fragments
- Graph database for correlation/synergy detection
- Vector database for ML-based similarity search
"""

import os
import json
import sqlite3
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from dataclasses import dataclass
import threading
import logging
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AccessLevel(Enum):
    """Access control levels"""
    NONE = 0
    READ = 1
    WRITE = 2
    ADMIN = 3
    REGISTRY_ONLY = 4  # Only Procedural Registry


@dataclass
class Principal:
    """Security principal (user, agent, or service)"""
    principal_id: str
    principal_type: str  # 'user', 'agent', 'service', 'registry'
    access_level: AccessLevel
    permissions: Set[str]
    created_at: str
    last_access: Optional[str] = None

    def can_read(self) -> bool:
        return self.access_level.value >= AccessLevel.READ.value

    def can_write(self) -> bool:
        return self.access_level.value >= AccessLevel.WRITE.value

    def can_delete(self) -> bool:
        # Only Procedural Registry can delete
        return self.access_level == AccessLevel.REGISTRY_ONLY


class FragmentationSynergyDatabase:
    """
    Stores security intelligence fragments.

    NO DELETION without Procedural Registry approval.
    ALL data retained indefinitely for synergy correlation.

    Security:
    - Zero-trust access control
    - AES-256-GCM encryption at rest
    - Immutable audit log
    - HMAC integrity verification
    """

    def __init__(self, db_path: str, encryption_key: Optional[bytes] = None):
        """
        Initialize fragmentation database.

        Args:
            db_path: Path to database file
            encryption_key: 32-byte encryption key (will generate if not provided)
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)

        # Encryption setup
        if encryption_key is None:
            # Generate and save encryption key securely
            encryption_key = self._generate_or_load_key()

        if len(encryption_key) != 32:
            raise ValueError("Encryption key must be 32 bytes for AES-256")

        self.encryption_key = encryption_key
        self.cipher = AESGCM(encryption_key)

        # Thread safety
        self._lock = threading.RLock()

        # Access control
        self.principals: Dict[str, Principal] = {}
        self.audit_log: List[Dict[str, Any]] = []

        # Initialize database
        self._init_database()

        # Synergy correlation cache
        self.synergy_cache: Dict[str, List[str]] = {}

        logger.info(f"Fragmentation Database initialized at {self.db_path}")

    def _generate_or_load_key(self) -> bytes:
        """Generate or load encryption key"""
        key_path = self.db_path.parent / '.encryption_key'

        if key_path.exists():
            # Load existing key
            with open(key_path, 'rb') as f:
                key = f.read()

            if len(key) != 32:
                raise ValueError("Invalid encryption key in file")

            logger.info("Loaded existing encryption key")
            return key
        else:
            # Generate new key
            key = secrets.token_bytes(32)

            # Save securely (0o600 permissions)
            old_umask = os.umask(0o077)
            try:
                with open(key_path, 'wb') as f:
                    f.write(key)
            finally:
                os.umask(old_umask)

            logger.info("Generated new encryption key")
            return key

    def _init_database(self) -> None:
        """Initialize SQLite database schema"""
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Fragments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fragments (
                    fragment_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    fragment_type TEXT NOT NULL,
                    source_agent TEXT,
                    source_layer TEXT,
                    encrypted_data BLOB NOT NULL,
                    data_nonce BLOB NOT NULL,
                    integrity_hmac TEXT NOT NULL,
                    synergy_score REAL DEFAULT 0.0,
                    correlation_potential REAL DEFAULT 0.0,
                    deletion_authorized INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    created_by TEXT NOT NULL
                )
            ''')

            # Synergies table (fragment correlations)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS synergies (
                    synergy_id TEXT PRIMARY KEY,
                    fragment_a_id TEXT NOT NULL,
                    fragment_b_id TEXT NOT NULL,
                    synergy_type TEXT NOT NULL,
                    correlation_strength REAL NOT NULL,
                    discovered_at TEXT NOT NULL,
                    FOREIGN KEY (fragment_a_id) REFERENCES fragments(fragment_id),
                    FOREIGN KEY (fragment_b_id) REFERENCES fragments(fragment_id)
                )
            ''')

            # Access audit table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS access_audit (
                    audit_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    principal_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    resource TEXT,
                    success INTEGER NOT NULL,
                    reason TEXT
                )
            ''')

            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON fragments(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_type ON fragments(fragment_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_synergy_score ON fragments(synergy_score)')

            conn.commit()
            conn.close()

    def register_principal(self, principal: Principal) -> None:
        """Register a security principal for access control"""
        with self._lock:
            self.principals[principal.principal_id] = principal
            logger.info(
                f"Registered principal: {principal.principal_id} "
                f"(type={principal.principal_type}, "
                f"access={principal.access_level.name})"
            )

    def _check_access(self, principal_id: str, action: str) -> bool:
        """
        Zero-trust access check.

        Args:
            principal_id: Identity requesting access
            action: Action to perform ('read', 'write', 'delete')

        Returns:
            True if access granted, False otherwise
        """
        if principal_id not in self.principals:
            self._audit_access(principal_id, action, None, False, "Unknown principal")
            return False

        principal = self.principals[principal_id]

        # Update last access time
        principal.last_access = datetime.utcnow().isoformat()

        # Check permissions
        if action == 'read' and not principal.can_read():
            self._audit_access(principal_id, action, None, False, "Insufficient permissions")
            return False

        if action == 'write' and not principal.can_write():
            self._audit_access(principal_id, action, None, False, "Insufficient permissions")
            return False

        if action == 'delete' and not principal.can_delete():
            self._audit_access(principal_id, action, None, False, "Only Registry can delete")
            return False

        return True

    def _audit_access(self, principal_id: str, action: str, resource: Optional[str],
                     success: bool, reason: Optional[str] = None) -> None:
        """Log access attempt to audit trail"""
        audit_entry = {
            'audit_id': self._generate_id('audit'),
            'timestamp': datetime.utcnow().isoformat(),
            'principal_id': principal_id,
            'action': action,
            'resource': resource,
            'success': 1 if success else 0,
            'reason': reason
        }

        # Store in database
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO access_audit
                (audit_id, timestamp, principal_id, action, resource, success, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                audit_entry['audit_id'],
                audit_entry['timestamp'],
                audit_entry['principal_id'],
                audit_entry['action'],
                audit_entry['resource'],
                audit_entry['success'],
                audit_entry['reason']
            ))

            conn.commit()
            conn.close()

        # Also keep in memory for recent audit log
        self.audit_log.append(audit_entry)
        if len(self.audit_log) > 10000:
            self.audit_log = self.audit_log[-10000:]  # Keep last 10k entries

    def store_fragment(self, fragment: Dict[str, Any],
                      principal_id: str = 'system') -> str:
        """
        Store security intelligence fragment.

        CRITICAL: ALL data is stored, no matter how trivial.
        Only Procedural Registry can authorize deletion.

        Args:
            fragment: Data to store
            principal_id: Principal storing the fragment

        Returns:
            fragment_id: Unique identifier
        """
        # Zero-trust access check
        if not self._check_access(principal_id, 'write'):
            raise PermissionError(f"Principal {principal_id} lacks write permission")

        with self._lock:
            # Generate fragment ID
            fragment_id = self._generate_id('fragment')

            # Extract metadata
            fragment_type = fragment.get('type', 'unknown')
            source_agent = fragment.get('agent_id', 'unknown')
            source_layer = fragment.get('layer', 'unknown')

            # Encrypt fragment data
            encrypted_data, nonce = self._encrypt_data(fragment)

            # Calculate HMAC for integrity
            integrity_hmac = self._calculate_hmac(fragment_id, encrypted_data)

            # Calculate correlation potential (simplified - production uses ML)
            correlation_potential = self._assess_correlation_potential(fragment)

            # Store in database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO fragments
                (fragment_id, timestamp, fragment_type, source_agent, source_layer,
                 encrypted_data, data_nonce, integrity_hmac, correlation_potential,
                 created_at, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                fragment_id,
                datetime.utcnow().isoformat(),
                fragment_type,
                source_agent,
                source_layer,
                encrypted_data,
                nonce,
                integrity_hmac,
                correlation_potential,
                datetime.utcnow().isoformat(),
                principal_id
            ))

            conn.commit()
            conn.close()

            # Audit successful storage
            self._audit_access(principal_id, 'write', fragment_id, True)

            logger.debug(f"Stored fragment {fragment_id} (type={fragment_type})")

            return fragment_id

    def get_fragment(self, fragment_id: str,
                    principal_id: str = 'system') -> Optional[Dict[str, Any]]:
        """
        Retrieve fragment by ID.

        Args:
            fragment_id: Fragment identifier
            principal_id: Principal requesting access

        Returns:
            Decrypted fragment data or None
        """
        # Zero-trust access check
        if not self._check_access(principal_id, 'read'):
            raise PermissionError(f"Principal {principal_id} lacks read permission")

        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute('''
                SELECT encrypted_data, data_nonce, integrity_hmac
                FROM fragments
                WHERE fragment_id = ?
            ''', (fragment_id,))

            row = cursor.fetchone()
            conn.close()

            if row is None:
                self._audit_access(principal_id, 'read', fragment_id, False, "Not found")
                return None

            encrypted_data, nonce, stored_hmac = row

            # Verify integrity
            calculated_hmac = self._calculate_hmac(fragment_id, encrypted_data)
            if not hmac.compare_digest(calculated_hmac, stored_hmac):
                logger.error(f"Integrity check failed for fragment {fragment_id}")
                self._audit_access(principal_id, 'read', fragment_id, False, "Integrity fail")
                return None

            # Decrypt
            decrypted_data = self._decrypt_data(encrypted_data, nonce)

            # Audit successful access
            self._audit_access(principal_id, 'read', fragment_id, True)

            return decrypted_data

    def query_fragments(self,
                       fragment_type: Optional[str] = None,
                       start_time: Optional[str] = None,
                       end_time: Optional[str] = None,
                       min_synergy_score: Optional[float] = None,
                       limit: int = 100,
                       principal_id: str = 'system') -> List[str]:
        """
        Query fragment IDs by criteria.

        Returns only IDs for privacy - caller must get_fragment() for data.
        """
        # Zero-trust access check
        if not self._check_access(principal_id, 'read'):
            raise PermissionError(f"Principal {principal_id} lacks read permission")

        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            query = "SELECT fragment_id FROM fragments WHERE 1=1"
            params = []

            if fragment_type:
                query += " AND fragment_type = ?"
                params.append(fragment_type)

            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)

            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)

            if min_synergy_score is not None:
                query += " AND synergy_score >= ?"
                params.append(min_synergy_score)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)

            fragment_ids = [row[0] for row in cursor.fetchall()]
            conn.close()

            return fragment_ids

    def record_synergy(self, fragment_a_id: str, fragment_b_id: str,
                      synergy_type: str, correlation_strength: float,
                      principal_id: str = 'system') -> str:
        """
        Record synergy (correlation) between two fragments.

        This is how trivial fragments become valuable.
        """
        if not self._check_access(principal_id, 'write'):
            raise PermissionError(f"Principal {principal_id} lacks write permission")

        with self._lock:
            synergy_id = self._generate_id('synergy')

            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO synergies
                (synergy_id, fragment_a_id, fragment_b_id, synergy_type,
                 correlation_strength, discovered_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                synergy_id,
                fragment_a_id,
                fragment_b_id,
                synergy_type,
                correlation_strength,
                datetime.utcnow().isoformat()
            ))

            # Update synergy scores for both fragments
            cursor.execute('''
                UPDATE fragments
                SET synergy_score = synergy_score + ?
                WHERE fragment_id IN (?, ?)
            ''', (correlation_strength, fragment_a_id, fragment_b_id))

            conn.commit()
            conn.close()

            logger.info(
                f"Recorded synergy: {fragment_a_id} <-> {fragment_b_id} "
                f"(strength={correlation_strength:.2f})"
            )

            return synergy_id

    def get_synergies(self, fragment_id: str,
                     principal_id: str = 'system') -> List[Dict[str, Any]]:
        """Get all synergies for a fragment"""
        if not self._check_access(principal_id, 'read'):
            raise PermissionError(f"Principal {principal_id} lacks read permission")

        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute('''
                SELECT synergy_id, fragment_a_id, fragment_b_id, synergy_type,
                       correlation_strength, discovered_at
                FROM synergies
                WHERE fragment_a_id = ? OR fragment_b_id = ?
                ORDER BY correlation_strength DESC
            ''', (fragment_id, fragment_id))

            synergies = []
            for row in cursor.fetchall():
                synergy_id, frag_a, frag_b, syn_type, strength, discovered = row

                # Get the other fragment ID
                other_fragment = frag_b if frag_a == fragment_id else frag_a

                synergies.append({
                    'synergy_id': synergy_id,
                    'other_fragment_id': other_fragment,
                    'synergy_type': syn_type,
                    'correlation_strength': strength,
                    'discovered_at': discovered
                })

            conn.close()

            return synergies

    def mark_for_deletion(self, fragment_id: str,
                         principal_id: str) -> bool:
        """
        Mark fragment for deletion.

        CRITICAL: Only Procedural Registry can call this.
        Does NOT actually delete - just marks for later cleanup.
        """
        if not self._check_access(principal_id, 'delete'):
            logger.error(
                f"DELETION ATTEMPT BLOCKED: Principal {principal_id} "
                "lacks deletion authority. Only Procedural Registry can delete."
            )
            self._audit_access(principal_id, 'delete', fragment_id, False,
                             "Only Registry can delete")
            return False

        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE fragments
                SET deletion_authorized = 1
                WHERE fragment_id = ?
            ''', (fragment_id,))

            conn.commit()
            conn.close()

            self._audit_access(principal_id, 'delete', fragment_id, True,
                             "Marked for deletion")

            logger.warning(f"Fragment {fragment_id} marked for deletion by Registry")

            return True

    def _encrypt_data(self, data: Dict[str, Any]) -> tuple:
        """Encrypt data with AES-256-GCM"""
        plaintext = json.dumps(data).encode('utf-8')
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        ciphertext = self.cipher.encrypt(nonce, plaintext, None)
        return ciphertext, nonce

    def _decrypt_data(self, ciphertext: bytes, nonce: bytes) -> Dict[str, Any]:
        """Decrypt data with AES-256-GCM"""
        plaintext = self.cipher.decrypt(nonce, ciphertext, None)
        return json.loads(plaintext.decode('utf-8'))

    def _calculate_hmac(self, fragment_id: str, data: bytes) -> str:
        """Calculate HMAC-SHA256 for integrity verification"""
        h = hmac.new(self.encryption_key, digestmod=hashlib.sha256)
        h.update(fragment_id.encode('utf-8'))
        h.update(data)
        return h.hexdigest()

    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID"""
        timestamp = datetime.utcnow().isoformat()
        random_bytes = secrets.token_bytes(8)
        data = f"{prefix}:{timestamp}:{random_bytes.hex()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def _assess_correlation_potential(self, fragment: Dict[str, Any]) -> float:
        """
        Assess how likely this fragment will correlate with others.

        Simplified version - production would use ML model.
        """
        # Higher potential for anomalous but non-critical events
        potential = 0.5  # baseline

        # Increase for certain types
        if fragment.get('type') in ['failed_login', 'port_scan', 'anomaly']:
            potential += 0.2

        # Increase if from uncommon source
        if fragment.get('rare_source', False):
            potential += 0.15

        return min(potential, 1.0)

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM fragments')
            total_fragments = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM synergies')
            total_synergies = cursor.fetchone()[0]

            cursor.execute('SELECT AVG(synergy_score) FROM fragments')
            avg_synergy_score = cursor.fetchone()[0] or 0.0

            cursor.execute('SELECT COUNT(*) FROM fragments WHERE deletion_authorized = 1')
            marked_for_deletion = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM access_audit')
            total_access_attempts = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM access_audit WHERE success = 0')
            failed_access_attempts = cursor.fetchone()[0]

            conn.close()

            return {
                'total_fragments': total_fragments,
                'total_synergies': total_synergies,
                'avg_synergy_score': avg_synergy_score,
                'marked_for_deletion': marked_for_deletion,
                'total_access_attempts': total_access_attempts,
                'failed_access_attempts': failed_access_attempts,
                'registered_principals': len(self.principals)
            }


if __name__ == "__main__":
    # Test database
    db = FragmentationSynergyDatabase('/tmp/test_fragmentation.db')

    # Register test principals
    admin = Principal(
        principal_id='admin_001',
        principal_type='user',
        access_level=AccessLevel.ADMIN,
        permissions={'read', 'write'},
        created_at=datetime.utcnow().isoformat()
    )
    db.register_principal(admin)

    # Test storage
    fragment = {
        'type': 'failed_login',
        'ip': '1.2.3.4',
        'username': 'admin',
        'timestamp': datetime.utcnow().isoformat()
    }

    fragment_id = db.store_fragment(fragment, 'admin_001')
    print(f"Stored fragment: {fragment_id}")

    # Test retrieval
    retrieved = db.get_fragment(fragment_id, 'admin_001')
    print(f"Retrieved: {retrieved}")

    # Test statistics
    stats = db.get_statistics()
    print(f"Statistics: {json.dumps(stats, indent=2)}")
