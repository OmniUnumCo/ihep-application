#!/usr/bin/env python3
"""
Procedural Registry - Data Lifecycle Authority

ONLY authority that can authorize fragment deletion.

Principles:
- No agent can delete data autonomously
- All deletion requests must be evaluated
- Legal/compliance requirements take precedence
- Synergy value is protected
- Predictive value is considered
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeletionReason(Enum):
    """Reasons for denial/approval of deletion"""
    LEGAL_HOLD = "Fragment under legal/compliance hold"
    HIPAA_RETENTION = "HIPAA 6-year retention requirement"
    HIGH_SYNERGY = "High synergy value with other fragments"
    ACTIVE_CORRELATIONS = "Active correlations depend on this fragment"
    PREDICTED_VALUE = "ML predicts future value"
    STORAGE_NOT_CRITICAL = "Sufficient storage available"
    APPROVED = "All requirements met for deletion"


@dataclass
class DeletionRequest:
    """Deletion request record"""
    request_id: str
    fragment_id: str
    requesting_principal: str
    requested_at: str
    reason: str
    decision: Optional[str] = None  # 'deny', 'defer', 'approve'
    decision_reason: Optional[str] = None
    decided_at: Optional[str] = None


class ProceduralRegistry:
    """
    ONLY authority for data lifecycle decisions.

    Philosophy:
    - Retain by default
    - Delete only when absolutely necessary
    - Protect synergistic value
    - Respect legal/compliance requirements
    """

    def __init__(self, fragmentation_db, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Procedural Registry.

        Args:
            fragmentation_db: Reference to FragmentationSynergyDatabase
            config: Registry configuration
        """
        self.fragmentation_db = fragmentation_db
        self.config = config or self._default_config()

        # Decision log
        self.deletion_requests: List[DeletionRequest] = []

        # ML model for future value prediction (placeholder for now)
        self.value_predictor = None

        logger.info("Procedural Registry initialized")

    def _default_config(self) -> Dict[str, Any]:
        """Default registry configuration"""
        return {
            'retention_policies': {
                'hipaa_days': 6 * 365,  # 6 years
                'pci_days': 1 * 365,    # 1 year
                'default_days': 10 * 365  # 10 years default
            },
            'synergy_threshold': 0.7,  # Keep if synergy score > 70%
            'storage_quota_gb': 1000,  # 1TB default
            'storage_critical_threshold': 0.85,  # 85% usage triggers evaluation
            'legal_holds': [],  # Fragment IDs under legal hold
            'required_approvers': [
                'security_lead',
                'compliance_officer',
                'data_scientist'
            ]
        }

    def evaluate_deletion_request(self, fragment_id: str,
                                  requesting_principal: str,
                                  reason: str = "Storage optimization"
                                 ) -> Dict[str, Any]:
        """
        Evaluate deletion request.

        Almost always DENIES deletion to protect synergy value.

        Args:
            fragment_id: Fragment to potentially delete
            requesting_principal: Who is requesting deletion
            reason: Why deletion is requested

        Returns:
            Decision with detailed reasoning
        """
        # Create deletion request record
        request = DeletionRequest(
            request_id=self._generate_request_id(),
            fragment_id=fragment_id,
            requesting_principal=requesting_principal,
            requested_at=datetime.utcnow().isoformat(),
            reason=reason
        )

        # Get fragment metadata
        fragment = self.fragmentation_db.get_fragment(
            fragment_id,
            principal_id='registry'  # Registry has special access
        )

        if fragment is None:
            return self._deny(request, "FRAGMENT_NOT_FOUND",
                            "Fragment does not exist")

        # Run evaluation pipeline
        decision = self._run_evaluation_pipeline(request, fragment)

        # Record decision
        self.deletion_requests.append(request)

        return decision

    def _run_evaluation_pipeline(self, request: DeletionRequest,
                                 fragment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run evaluation pipeline with multiple checks.

        Pipeline:
        1. Legal/compliance hold check
        2. Retention policy check
        3. Synergy value check
        4. Active correlations check
        5. Predictive value check
        6. Storage criticality check
        """

        # 1. Legal hold check
        if fragment.get('fragment_id') in self.config['legal_holds']:
            return self._deny(request, DeletionReason.LEGAL_HOLD.name,
                            DeletionReason.LEGAL_HOLD.value)

        # 2. Retention policy check
        age_check = self._check_retention_policy(fragment)
        if not age_check['can_delete']:
            return self._deny(request, DeletionReason.HIPAA_RETENTION.name,
                            age_check['reason'])

        # 3. Synergy value check
        synergy_check = self._check_synergy_value(fragment)
        if not synergy_check['can_delete']:
            return self._deny(request, DeletionReason.HIGH_SYNERGY.name,
                            synergy_check['reason'])

        # 4. Active correlations check
        correlation_check = self._check_active_correlations(fragment)
        if not correlation_check['can_delete']:
            return self._deny(request, DeletionReason.ACTIVE_CORRELATIONS.name,
                            correlation_check['reason'])

        # 5. Predictive value check
        predictive_check = self._check_predictive_value(fragment)
        if not predictive_check['can_delete']:
            return self._deny(request, DeletionReason.PREDICTED_VALUE.name,
                            predictive_check['reason'])

        # 6. Storage criticality check
        storage_check = self._check_storage_criticality()
        if not storage_check['critical']:
            return self._defer(request, DeletionReason.STORAGE_NOT_CRITICAL.name,
                             storage_check['reason'])

        # If we reach here, deletion MAY be considered
        # But requires multi-approver sign-off
        return self._require_approval(request, fragment)

    def _check_retention_policy(self, fragment: Dict[str, Any]) -> Dict[str, Any]:
        """Check if fragment meets retention policy requirements"""
        # Calculate age
        created_at_str = fragment.get('created_at', fragment.get('timestamp'))
        if not created_at_str:
            return {
                'can_delete': False,
                'reason': 'Cannot determine fragment age'
            }

        try:
            created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            age_days = (datetime.utcnow() - created_at.replace(tzinfo=None)).days
        except Exception as e:
            logger.error(f"Error parsing timestamp: {e}")
            return {
                'can_delete': False,
                'reason': f'Invalid timestamp: {e}'
            }

        # Check HIPAA retention (6 years minimum for PHI)
        hipaa_retention = self.config['retention_policies']['hipaa_days']

        if age_days < hipaa_retention:
            return {
                'can_delete': False,
                'reason': (
                    f'HIPAA retention: Fragment is {age_days} days old, '
                    f'must be at least {hipaa_retention} days'
                )
            }

        return {
            'can_delete': True,
            'reason': f'Fragment age ({age_days} days) exceeds retention minimum'
        }

    def _check_synergy_value(self, fragment: Dict[str, Any]) -> Dict[str, Any]:
        """Check if fragment has high synergy value"""
        # Get synergy score from database metadata
        fragment_id = fragment.get('fragment_id')

        # Query database for synergy score
        # (In real implementation, would query from fragmentation_db)
        synergy_score = fragment.get('synergy_score', 0.0)

        threshold = self.config['synergy_threshold']

        if synergy_score > threshold:
            return {
                'can_delete': False,
                'reason': (
                    f'High synergy value: Score {synergy_score:.2f} '
                    f'exceeds threshold {threshold}'
                )
            }

        return {
            'can_delete': True,
            'reason': f'Synergy score {synergy_score:.2f} below threshold'
        }

    def _check_active_correlations(self, fragment: Dict[str, Any]) -> Dict[str, Any]:
        """Check if other fragments depend on this one"""
        fragment_id = fragment.get('fragment_id')

        # Get synergies from database
        try:
            synergies = self.fragmentation_db.get_synergies(
                fragment_id,
                principal_id='registry'
            )

            if len(synergies) > 0:
                return {
                    'can_delete': False,
                    'reason': (
                        f'{len(synergies)} active correlations depend on this fragment'
                    )
                }

            return {
                'can_delete': True,
                'reason': 'No active correlations'
            }

        except Exception as e:
            logger.error(f"Error checking correlations: {e}")
            # Fail safe - deny deletion if we can't check correlations
            return {
                'can_delete': False,
                'reason': f'Cannot verify correlations: {e}'
            }

    def _check_predictive_value(self, fragment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict if fragment will be valuable in future.

        Uses ML model to predict:
        - Will this correlate with future events?
        - Does this fit an emerging attack pattern?
        - Is this part of a slow APT campaign?
        """
        # Placeholder - production would use trained ML model
        # For now, use heuristics

        fragment_type = fragment.get('type', 'unknown')

        # Certain types have high predictive value
        high_value_types = [
            'failed_login',
            'port_scan',
            'anomaly',
            'reconnaissance',
            'unusual_access'
        ]

        if fragment_type in high_value_types:
            return {
                'can_delete': False,
                'reason': (
                    f'Type "{fragment_type}" has high predictive value '
                    'for future threat correlation'
                )
            }

        # Check if from rare source
        if fragment.get('rare_source', False):
            return {
                'can_delete': False,
                'reason': 'Fragment from rare source - high correlation potential'
            }

        return {
            'can_delete': True,
            'reason': 'Low predicted future value'
        }

    def _check_storage_criticality(self) -> Dict[str, Any]:
        """Check if storage is critically low"""
        # In production, would query actual storage usage
        # For now, assume storage is NOT critical

        # Get storage statistics
        stats = self.fragmentation_db.get_statistics()
        total_fragments = stats['total_fragments']

        # Estimate storage usage (simplified)
        # Assume ~1KB per fragment on average
        estimated_storage_mb = total_fragments * 1  # 1KB per fragment
        estimated_storage_gb = estimated_storage_mb / 1024

        quota_gb = self.config['storage_quota_gb']
        usage_ratio = estimated_storage_gb / quota_gb

        critical_threshold = self.config['storage_critical_threshold']

        if usage_ratio < critical_threshold:
            return {
                'critical': False,
                'reason': (
                    f'Storage not critical: {usage_ratio*100:.1f}% used '
                    f'({estimated_storage_gb:.1f}GB / {quota_gb}GB). '
                    'Retain fragment indefinitely.'
                )
            }

        return {
            'critical': True,
            'reason': (
                f'Storage critical: {usage_ratio*100:.1f}% used '
                f'({estimated_storage_gb:.1f}GB / {quota_gb}GB)'
            )
        }

    def _deny(self, request: DeletionRequest, reason_code: str,
             detail: str) -> Dict[str, Any]:
        """Deny deletion request"""
        request.decision = 'DENY'
        request.decision_reason = f"{reason_code}: {detail}"
        request.decided_at = datetime.utcnow().isoformat()

        decision = {
            'request_id': request.request_id,
            'fragment_id': request.fragment_id,
            'decision': 'DENY',
            'reason_code': reason_code,
            'detail': detail,
            'decided_at': request.decided_at
        }

        logger.info(
            f"DENIED deletion request {request.request_id}: "
            f"{reason_code} - {detail}"
        )

        return decision

    def _defer(self, request: DeletionRequest, reason_code: str,
              detail: str) -> Dict[str, Any]:
        """Defer deletion decision"""
        request.decision = 'DEFER'
        request.decision_reason = f"{reason_code}: {detail}"
        request.decided_at = datetime.utcnow().isoformat()

        # Review again in 1 year
        review_date = datetime.utcnow() + timedelta(days=365)

        decision = {
            'request_id': request.request_id,
            'fragment_id': request.fragment_id,
            'decision': 'DEFER',
            'reason_code': reason_code,
            'detail': detail,
            'review_again_at': review_date.isoformat(),
            'decided_at': request.decided_at
        }

        logger.info(
            f"DEFERRED deletion request {request.request_id}: "
            f"{reason_code} - Review at {review_date.date()}"
        )

        return decision

    def _require_approval(self, request: DeletionRequest,
                         fragment: Dict[str, Any]) -> Dict[str, Any]:
        """Require multi-approver sign-off for deletion"""
        request.decision = 'PENDING_APPROVAL'
        request.decided_at = datetime.utcnow().isoformat()

        decision = {
            'request_id': request.request_id,
            'fragment_id': request.fragment_id,
            'decision': 'PENDING_APPROVAL',
            'detail': (
                'Fragment meets deletion criteria, but requires approval from: '
                f"{', '.join(self.config['required_approvers'])}"
            ),
            'required_approvers': self.config['required_approvers'],
            'approvals_received': [],
            'decided_at': request.decided_at
        }

        logger.warning(
            f"Deletion request {request.request_id} requires approval from: "
            f"{self.config['required_approvers']}"
        )

        return decision

    def approve_deletion(self, request_id: str,
                        approvals: List[str]) -> Dict[str, Any]:
        """
        Approve deletion after multi-party sign-off.

        Args:
            request_id: Deletion request ID
            approvals: List of approver IDs

        Returns:
            Approval result
        """
        # Find request
        request = None
        for req in self.deletion_requests:
            if req.request_id == request_id:
                request = req
                break

        if request is None:
            return {
                'success': False,
                'error': 'Request not found'
            }

        if request.decision != 'PENDING_APPROVAL':
            return {
                'success': False,
                'error': f'Request status is {request.decision}, not PENDING_APPROVAL'
            }

        # Verify all required approvers have signed off
        required = set(self.config['required_approvers'])
        received = set(approvals)

        if not required.issubset(received):
            missing = required - received
            return {
                'success': False,
                'error': f'Missing approvals from: {missing}'
            }

        # All approvals received - authorize deletion
        success = self.fragmentation_db.mark_for_deletion(
            request.fragment_id,
            principal_id='registry'  # Only registry can delete
        )

        if success:
            request.decision = 'APPROVED'
            logger.critical(
                f"DELETION APPROVED for fragment {request.fragment_id} "
                f"with approvals from {approvals}"
            )

            return {
                'success': True,
                'request_id': request_id,
                'fragment_id': request.fragment_id,
                'approvals': approvals,
                'status': 'marked_for_deletion'
            }
        else:
            return {
                'success': False,
                'error': 'Failed to mark fragment for deletion'
            }

    def get_deletion_statistics(self) -> Dict[str, Any]:
        """Get deletion request statistics"""
        total_requests = len(self.deletion_requests)

        denied = sum(1 for r in self.deletion_requests if r.decision == 'DENY')
        deferred = sum(1 for r in self.deletion_requests if r.decision == 'DEFER')
        pending = sum(1 for r in self.deletion_requests if r.decision == 'PENDING_APPROVAL')
        approved = sum(1 for r in self.deletion_requests if r.decision == 'APPROVED')

        return {
            'total_deletion_requests': total_requests,
            'denied': denied,
            'deferred': deferred,
            'pending_approval': pending,
            'approved': approved,
            'denial_rate': denied / total_requests if total_requests > 0 else 0.0
        }

    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        import secrets
        timestamp = datetime.utcnow().isoformat()
        random = secrets.token_hex(4)
        return f"DEL_{timestamp}_{random}"


if __name__ == "__main__":
    # Test procedural registry
    from fragmentation_synergy_db import FragmentationSynergyDatabase, Principal, AccessLevel

    # Create database
    db = FragmentationSynergyDatabase('/tmp/test_registry.db')

    # Register registry principal with delete authority
    registry_principal = Principal(
        principal_id='registry',
        principal_type='registry',
        access_level=AccessLevel.REGISTRY_ONLY,
        permissions={'read', 'write', 'delete'},
        created_at=datetime.utcnow().isoformat()
    )
    db.register_principal(registry_principal)

    # Create registry
    registry = ProceduralRegistry(db)

    # Store test fragment
    test_fragment = {
        'type': 'failed_login',
        'ip': '1.2.3.4',
        'timestamp': datetime.utcnow().isoformat(),
        'created_at': (datetime.utcnow() - timedelta(days=1)).isoformat(),
        'synergy_score': 0.3
    }

    fragment_id = db.store_fragment(test_fragment, 'registry')
    print(f"Stored fragment: {fragment_id}")

    # Test deletion request (should be denied - HIPAA retention)
    decision = registry.evaluate_deletion_request(
        fragment_id,
        requesting_principal='agent_001',
        reason='Seems trivial'
    )

    print(f"\nDeletion decision: {json.dumps(decision, indent=2)}")

    # Get statistics
    stats = registry.get_deletion_statistics()
    print(f"\nRegistry statistics: {json.dumps(stats, indent=2)}")
