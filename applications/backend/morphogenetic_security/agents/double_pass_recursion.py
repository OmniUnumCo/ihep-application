#!/usr/bin/env python3
"""
Double-Pass Recursion Anomaly Detection
Catches dormant threats off-guard with randomized re-inspection.

Technique:
1. First Pass: Detect potentially dormant anomaly
2. Wait: Random delay (~0.2s ± variance)
3. Second Pass: Re-inspect to catch behavioral changes
4. Compare: Detect if threat "woke up" or changed behavior

Use Cases:
- Time-delayed malware (sleeps before execution)
- Sandbox-aware exploits (wait to evade detection)
- Slow-burn attacks (gradual escalation)
- APT reconnaissance (dormant then active)
"""

import time
import random
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json

logging.basicConfig(level=logging.INFO)
logging.getLogger("urllib3").setLevel(logging.WARNING)  # Suppress urllib3 debug logs
logger = logging.getLogger(__name__)


class DormancyIndicator(Enum):
    """Indicators that suggest dormant behavior"""
    NO_ACTIVITY = "no_network_activity"
    WAITING = "appears_waiting"
    SLEEPING = "sleep_pattern_detected"
    TIME_CHECK = "checking_system_time"
    ENVIRONMENT_PROBE = "probing_environment"
    DELAYED_EXECUTION = "execution_delayed"
    SANDBOX_EVASION = "sandbox_evasion_attempt"


class BehaviorChange(Enum):
    """Types of behavioral changes between passes"""
    ACTIVATED = "threat_activated"
    ESCALATED = "privilege_escalation"
    NETWORK_ACTIVITY = "network_connection_initiated"
    FILE_MANIPULATION = "file_modification_detected"
    PROCESS_SPAWN = "new_process_spawned"
    PERSISTENCE = "persistence_mechanism_created"
    DATA_EXFILTRATION = "data_exfiltration_attempt"
    NO_CHANGE = "no_behavioral_change"


@dataclass
class PassObservation:
    """Observation from a single pass"""
    pass_number: int  # 1 or 2
    timestamp: str
    event_snapshot: Dict[str, Any]
    behavior_signature: str  # Hash of behavioral state
    network_connections: List[str] = field(default_factory=list)
    file_operations: List[str] = field(default_factory=list)
    process_activity: List[str] = field(default_factory=list)
    memory_state: Dict[str, Any] = field(default_factory=dict)
    system_calls: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'pass_number': self.pass_number,
            'timestamp': self.timestamp,
            'event_snapshot': self.event_snapshot,
            'behavior_signature': self.behavior_signature,
            'network_connections': self.network_connections,
            'file_operations': self.file_operations,
            'process_activity': self.process_activity,
            'system_calls': self.system_calls
        }


@dataclass
class DoublePassResult:
    """Result of double-pass inspection"""
    event_id: str
    first_pass: PassObservation
    second_pass: PassObservation
    delay_seconds: float
    behavior_changed: bool
    changes_detected: List[BehaviorChange]
    threat_level_change: str  # 'escalated', 'same', 'deescalated'
    recommendation: str  # 'block', 'sandbox', 'monitor', 'allow'
    confidence: float  # 0.0 to 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'first_pass': self.first_pass.to_dict(),
            'second_pass': self.second_pass.to_dict(),
            'delay_seconds': self.delay_seconds,
            'behavior_changed': self.behavior_changed,
            'changes_detected': [c.value for c in self.changes_detected],
            'threat_level_change': self.threat_level_change,
            'recommendation': self.recommendation,
            'confidence': self.confidence
        }


class DoublePassRecursion:
    """
    Double-pass recursion system for catching dormant threats.

    Architecture:
    - First pass detects dormant behavior
    - Random delay (~0.2s ± variance)
    - Second pass re-inspects
    - Compare behavioral changes
    - Escalate if threat activates
    """

    def __init__(self,
                 base_delay_ms: float = 200.0,
                 delay_variance_ms: float = 50.0,
                 max_concurrent_passes: int = 100):
        """
        Initialize double-pass recursion system.

        Args:
            base_delay_ms: Base delay in milliseconds (~200ms)
            delay_variance_ms: Random variance (±50ms)
            max_concurrent_passes: Maximum concurrent second passes
        """
        self.base_delay_ms = base_delay_ms
        self.delay_variance_ms = delay_variance_ms
        self.max_concurrent_passes = max_concurrent_passes

        # Track active second passes
        self.active_passes: Dict[str, threading.Timer] = {}
        self._lock = threading.RLock()

        # Store first pass observations
        self.first_pass_cache: Dict[str, PassObservation] = {}

        # Results storage
        self.results: List[DoublePassResult] = []

        # Statistics
        self.stats = {
            'total_first_passes': 0,
            'total_second_passes': 0,
            'dormant_detected': 0,
            'threats_activated': 0,
            'false_positives': 0,
            'avg_delay_ms': 0.0
        }

        logger.info(
            f"Double-Pass Recursion initialized: "
            f"delay={base_delay_ms}ms±{delay_variance_ms}ms"
        )

    def is_dormant(self, event: Dict[str, Any]) -> tuple[bool, List[DormancyIndicator]]:
        """
        Detect if event shows dormant/suspicious behavior.

        Args:
            event: Security event to analyze

        Returns:
            (is_dormant, indicators) tuple
        """
        indicators = []

        event_type = event.get('event_type', '').lower()
        data = event.get('data', {})

        # Check for dormancy indicators

        # 1. No network activity (suspicious for network-based threat)
        if 'network' in event_type and len(data.get('connections', [])) == 0:
            indicators.append(DormancyIndicator.NO_ACTIVITY)

        # 2. Sleep/wait patterns
        if any(term in event_type for term in ['sleep', 'wait', 'delay', 'pause']):
            indicators.append(DormancyIndicator.SLEEPING)

        # 3. Time checking (malware often checks time before activating)
        if any(term in str(data).lower() for term in ['gettime', 'clock', 'timestamp']):
            indicators.append(DormancyIndicator.TIME_CHECK)

        # 4. Environment probing (sandbox detection)
        if any(term in event_type for term in ['probe', 'check', 'detect', 'scan']):
            indicators.append(DormancyIndicator.ENVIRONMENT_PROBE)

        # 5. Delayed execution indicators
        if data.get('execution_delayed', False) or 'scheduled' in event_type:
            indicators.append(DormancyIndicator.DELAYED_EXECUTION)

        # 6. Sandbox evasion techniques
        sandbox_indicators = [
            'vm_detection', 'sandbox_check', 'debugger_check',
            'hook_detection', 'virtual_machine'
        ]
        if any(ind in str(data).lower() for ind in sandbox_indicators):
            indicators.append(DormancyIndicator.SANDBOX_EVASION)

        # 7. Minimal resource usage (trying to appear benign)
        if data.get('cpu_usage', 100) < 5 and data.get('network_traffic', 100) < 10:
            indicators.append(DormancyIndicator.WAITING)

        is_dormant = len(indicators) >= 2  # Need at least 2 indicators

        return is_dormant, indicators

    def first_pass(self, event: Dict[str, Any]) -> Optional[PassObservation]:
        """
        Perform first pass inspection.

        Args:
            event: Security event to inspect

        Returns:
            PassObservation if dormant, None otherwise
        """
        # Check if event shows dormant behavior
        is_dormant, indicators = self.is_dormant(event)

        if not is_dormant:
            return None  # Not dormant, no second pass needed

        # Create observation
        observation = PassObservation(
            pass_number=1,
            timestamp=datetime.utcnow().isoformat(),
            event_snapshot=event.copy(),
            behavior_signature=self._calculate_behavior_signature(event),
            network_connections=event.get('data', {}).get('network_connections', []),
            file_operations=event.get('data', {}).get('file_ops', []),
            process_activity=event.get('data', {}).get('processes', []),
            memory_state=event.get('data', {}).get('memory', {}),
            system_calls=event.get('data', {}).get('syscalls', [])
        )

        # Store in cache for second pass comparison
        event_id = event.get('event_id')
        with self._lock:
            self.first_pass_cache[event_id] = observation
            self.stats['total_first_passes'] += 1
            self.stats['dormant_detected'] += 1

        logger.info(
            f"First pass: Event {event_id} appears dormant "
            f"(indicators: {[i.value for i in indicators]})"
        )

        return observation

    def schedule_second_pass(self, event: Dict[str, Any],
                            callback: Optional[Callable] = None) -> float:
        """
        Schedule second pass with randomized delay.

        Args:
            event: Security event to re-inspect
            callback: Optional callback when second pass completes

        Returns:
            Actual delay in seconds
        """
        event_id = event.get('event_id')

        # Check if we have room for more concurrent passes
        with self._lock:
            if len(self.active_passes) >= self.max_concurrent_passes:
                logger.warning(
                    f"Max concurrent passes ({self.max_concurrent_passes}) reached. "
                    "Skipping second pass."
                )
                return 0.0

        # Calculate randomized delay
        delay_ms = self.base_delay_ms + random.uniform(
            -self.delay_variance_ms,
            self.delay_variance_ms
        )
        delay_seconds = delay_ms / 1000.0

        # Schedule second pass
        timer = threading.Timer(
            delay_seconds,
            self._execute_second_pass,
            args=(event, delay_seconds, callback)
        )

        with self._lock:
            self.active_passes[event_id] = timer
            timer.start()

        logger.info(
            f"Second pass scheduled for event {event_id} "
            f"in {delay_ms:.1f}ms (randomized)"
        )

        return delay_seconds

    def _execute_second_pass(self, event: Dict[str, Any],
                            delay_seconds: float,
                            callback: Optional[Callable]) -> None:
        """
        Execute second pass inspection (called by timer).

        Args:
            event: Security event to re-inspect
            delay_seconds: Actual delay that was used
            callback: Optional callback
        """
        event_id = event.get('event_id')

        try:
            # Get first pass observation
            with self._lock:
                first_obs = self.first_pass_cache.get(event_id)

            if first_obs is None:
                logger.error(f"No first pass found for event {event_id}")
                return

            # Perform second inspection
            second_obs = PassObservation(
                pass_number=2,
                timestamp=datetime.utcnow().isoformat(),
                event_snapshot=event.copy(),
                behavior_signature=self._calculate_behavior_signature(event),
                network_connections=event.get('data', {}).get('network_connections', []),
                file_operations=event.get('data', {}).get('file_ops', []),
                process_activity=event.get('data', {}).get('processes', []),
                memory_state=event.get('data', {}).get('memory', {}),
                system_calls=event.get('data', {}).get('syscalls', [])
            )

            # Compare observations
            result = self._compare_passes(event_id, first_obs, second_obs, delay_seconds)

            # Store result
            with self._lock:
                self.results.append(result)
                self.stats['total_second_passes'] += 1

                if result.behavior_changed:
                    self.stats['threats_activated'] += 1

                # Update average delay
                total = self.stats['total_second_passes']
                prev_avg = self.stats['avg_delay_ms']
                new_avg = (prev_avg * (total - 1) + delay_seconds * 1000) / total
                self.stats['avg_delay_ms'] = new_avg

            # Log result
            if result.behavior_changed:
                logger.warning(
                    f"THREAT ACTIVATED: Event {event_id} changed behavior on second pass. "
                    f"Changes: {[c.value for c in result.changes_detected]}. "
                    f"Recommendation: {result.recommendation}"
                )
            else:
                logger.info(
                    f"Second pass: Event {event_id} behavior unchanged. "
                    f"Recommendation: {result.recommendation}"
                )

            # Call callback if provided
            if callback:
                callback(result)

        finally:
            # Clean up
            with self._lock:
                if event_id in self.active_passes:
                    del self.active_passes[event_id]
                if event_id in self.first_pass_cache:
                    del self.first_pass_cache[event_id]

    def _compare_passes(self, event_id: str,
                       first: PassObservation,
                       second: PassObservation,
                       delay_seconds: float) -> DoublePassResult:
        """
        Compare first and second pass observations.

        Args:
            event_id: Event identifier
            first: First pass observation
            second: Second pass observation
            delay_seconds: Delay between passes

        Returns:
            DoublePassResult with analysis
        """
        changes = []

        # 1. Check behavior signature change
        behavior_changed = first.behavior_signature != second.behavior_signature

        # 2. Check network activity change
        new_connections = set(second.network_connections) - set(first.network_connections)
        if new_connections:
            changes.append(BehaviorChange.NETWORK_ACTIVITY)

        # 3. Check file operations
        new_file_ops = set(second.file_operations) - set(first.file_operations)
        if new_file_ops:
            changes.append(BehaviorChange.FILE_MANIPULATION)

        # 4. Check process activity
        new_processes = set(second.process_activity) - set(first.process_activity)
        if new_processes:
            changes.append(BehaviorChange.PROCESS_SPAWN)

        # 5. Check system calls (privilege escalation indicators)
        first_syscalls = set(first.system_calls)
        second_syscalls = set(second.system_calls)
        privileged_syscalls = {'setuid', 'setgid', 'chmod', 'chown', 'mount'}

        if privileged_syscalls.intersection(second_syscalls - first_syscalls):
            changes.append(BehaviorChange.ESCALATED)

        # 6. Check for persistence mechanisms
        persistence_indicators = [
            'cron', 'systemd', 'autostart', 'registry', 'scheduled_task'
        ]
        if any(ind in str(second.event_snapshot).lower() for ind in persistence_indicators):
            if not any(ind in str(first.event_snapshot).lower() for ind in persistence_indicators):
                changes.append(BehaviorChange.PERSISTENCE)

        # 7. Check for data exfiltration
        if second.event_snapshot.get('data', {}).get('outbound_data_size', 0) > \
           first.event_snapshot.get('data', {}).get('outbound_data_size', 0):
            changes.append(BehaviorChange.DATA_EXFILTRATION)

        # No changes
        if not changes:
            changes.append(BehaviorChange.NO_CHANGE)

        # Determine threat level change
        threat_level_change = 'same'
        if BehaviorChange.ESCALATED in changes or BehaviorChange.DATA_EXFILTRATION in changes:
            threat_level_change = 'escalated'
        elif BehaviorChange.NO_CHANGE in changes:
            threat_level_change = 'same'

        # Determine recommendation
        recommendation = self._determine_recommendation(changes, threat_level_change)

        # Calculate confidence
        confidence = self._calculate_confidence(changes, behavior_changed)

        return DoublePassResult(
            event_id=event_id,
            first_pass=first,
            second_pass=second,
            delay_seconds=delay_seconds,
            behavior_changed=behavior_changed,
            changes_detected=changes,
            threat_level_change=threat_level_change,
            recommendation=recommendation,
            confidence=confidence
        )

    def _determine_recommendation(self, changes: List[BehaviorChange],
                                  threat_level: str) -> str:
        """Determine action recommendation based on changes"""
        # Block immediately if escalated or exfiltrating
        if BehaviorChange.ESCALATED in changes or \
           BehaviorChange.DATA_EXFILTRATION in changes:
            return 'block'

        # Sandbox if activated with network/process activity
        if BehaviorChange.NETWORK_ACTIVITY in changes or \
           BehaviorChange.PROCESS_SPAWN in changes:
            return 'sandbox'

        # Monitor if persistence mechanisms detected
        if BehaviorChange.PERSISTENCE in changes:
            return 'monitor'

        # Allow if no significant changes
        if BehaviorChange.NO_CHANGE in changes:
            return 'allow'

        # Default to sandbox for any other changes
        return 'sandbox'

    def _calculate_confidence(self, changes: List[BehaviorChange],
                             behavior_changed: bool) -> float:
        """Calculate confidence in threat assessment"""
        confidence = 0.5  # baseline

        # Increase confidence if behavior signature changed
        if behavior_changed:
            confidence += 0.2

        # Increase based on number of changes
        if len(changes) > 2:
            confidence += 0.2

        # High confidence for critical changes
        critical_changes = {
            BehaviorChange.ESCALATED,
            BehaviorChange.DATA_EXFILTRATION
        }
        if critical_changes.intersection(changes):
            confidence += 0.3

        return min(confidence, 1.0)

    def _calculate_behavior_signature(self, event: Dict[str, Any]) -> str:
        """
        Calculate behavioral signature hash.

        Uses key behavioral indicators to create a fingerprint.
        """
        # Extract behavioral features
        features = {
            'network': event.get('data', {}).get('network_connections', []),
            'files': event.get('data', {}).get('file_ops', []),
            'processes': event.get('data', {}).get('processes', []),
            'syscalls': event.get('data', {}).get('syscalls', []),
            'memory_usage': event.get('data', {}).get('memory', {}).get('usage', 0)
        }

        # Create deterministic hash
        signature_str = json.dumps(features, sort_keys=True)
        return hashlib.sha256(signature_str.encode()).hexdigest()[:16]

    def process_event(self, event: Dict[str, Any],
                     callback: Optional[Callable] = None) -> Optional[float]:
        """
        Process event with double-pass if dormant.

        Args:
            event: Security event to analyze
            callback: Optional callback for second pass result

        Returns:
            Delay in seconds if second pass scheduled, None otherwise
        """
        # First pass
        first_obs = self.first_pass(event)

        if first_obs is None:
            return None  # Not dormant, no second pass needed

        # Schedule second pass
        delay = self.schedule_second_pass(event, callback)

        return delay

    def get_result(self, event_id: str) -> Optional[DoublePassResult]:
        """Get double-pass result for event"""
        with self._lock:
            for result in self.results:
                if result.event_id == event_id:
                    return result
        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get double-pass statistics"""
        with self._lock:
            return self.stats.copy()

    def get_active_passes(self) -> int:
        """Get count of active second passes"""
        with self._lock:
            return len(self.active_passes)


if __name__ == "__main__":
    # Test double-pass recursion
    import time

    print("Testing Double-Pass Recursion System...")
    print("=" * 60)

    # Initialize system
    double_pass = DoublePassRecursion(
        base_delay_ms=200.0,
        delay_variance_ms=50.0
    )

    # Test event 1: Dormant threat (will activate on second pass)
    print("\n1. Testing dormant threat detection...")
    dormant_event = {
        'event_id': 'test_001',
        'event_type': 'process_execution',
        'data': {
            'execution_delayed': True,
            'sandbox_check': True,
            'network_connections': [],  # No network on first pass
            'processes': [],
            'syscalls': []
        }
    }

    def second_pass_callback(result):
        print(f"\n   Second pass completed for {result.event_id}")
        print(f"   Behavior changed: {result.behavior_changed}")
        print(f"   Changes: {[c.value for c in result.changes_detected]}")
        print(f"   Recommendation: {result.recommendation}")
        print(f"   Confidence: {result.confidence:.2f}")

    # Process event
    delay = double_pass.process_event(dormant_event, second_pass_callback)

    if delay:
        print(f"   ✓ Dormant behavior detected")
        print(f"   ✓ Second pass scheduled in {delay*1000:.1f}ms")

        # Simulate threat activation (modify event for second pass)
        time.sleep(0.1)  # Small delay before modification
        dormant_event['data']['network_connections'] = ['1.2.3.4:8080']
        dormant_event['data']['processes'] = ['malware.exe']
        dormant_event['data']['syscalls'] = ['setuid', 'socket']

        # Wait for second pass
        time.sleep(delay + 0.1)
    else:
        print("   ✗ Event not detected as dormant")

    # Get statistics
    print("\n2. Statistics:")
    stats = double_pass.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n" + "=" * 60)
    print("Double-Pass Recursion Test Complete")
