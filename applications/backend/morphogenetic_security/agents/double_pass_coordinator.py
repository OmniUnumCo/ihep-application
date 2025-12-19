#!/usr/bin/env python3
"""
Double-Pass Coordinator
Integrates double-pass recursion with morphogenetic engine and agent system.

Coordinates:
- First pass detection across all OSI layers
- Randomized second pass scheduling
- Cross-layer threat correlation
- Behavioral change analysis
- Automated response escalation
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from .double_pass_recursion import (
    DoublePassRecursion,
    DoublePassResult,
    BehaviorChange,
    DormancyIndicator
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DoublePassCoordinator:
    """
    Coordinates double-pass recursion across all security layers.

    Features:
    - Multi-layer dormancy detection
    - Cross-layer behavioral correlation
    - Automated threat escalation
    - Integration with morphogenetic engine
    """

    def __init__(self,
                 morphogenetic_engine,
                 fragmentation_db,
                 base_delay_ms: float = 200.0,
                 delay_variance_ms: float = 50.0):
        """
        Initialize double-pass coordinator.

        Args:
            morphogenetic_engine: Reference to morphogenetic engine
            fragmentation_db: Reference to fragmentation database
            base_delay_ms: Base delay for second pass (~200ms)
            delay_variance_ms: Random variance (±50ms)
        """
        self.engine = morphogenetic_engine
        self.fragmentation_db = fragmentation_db

        # Initialize double-pass system
        self.double_pass = DoublePassRecursion(
            base_delay_ms=base_delay_ms,
            delay_variance_ms=delay_variance_ms
        )

        # Track events under double-pass inspection
        self.active_inspections: Dict[str, Dict[str, Any]] = {}

        # Statistics
        self.stats = {
            'total_inspections': 0,
            'threats_caught': 0,
            'dormant_to_active': 0,
            'false_dormant': 0,
            'avg_activation_time_ms': 0.0
        }

        logger.info("Double-Pass Coordinator initialized")

    def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process event with potential double-pass inspection.

        Args:
            event: Security event from morphogenetic engine

        Returns:
            Processing decision
        """
        event_id = event.get('event_id')

        # Check if event shows dormant behavior
        is_dormant, indicators = self.double_pass.is_dormant(event)

        if not is_dormant:
            # Not dormant - process normally
            return {
                'double_pass_required': False,
                'decision': 'normal_processing',
                'dormant': False
            }

        # Event appears dormant - initiate double-pass
        logger.info(
            f"Initiating double-pass for event {event_id} "
            f"(dormancy indicators: {[i.value for i in indicators]})"
        )

        # Store in fragmentation database (ALWAYS retain)
        fragment_id = self.fragmentation_db.store_fragment({
            'type': 'double_pass_first',
            'event': event,
            'dormancy_indicators': [i.value for i in indicators],
            'timestamp': datetime.now().isoformat()
        }, principal_id='system')

        # Track active inspection
        self.active_inspections[event_id] = {
            'fragment_id': fragment_id,
            'first_pass_time': datetime.now(),
            'indicators': indicators,
            'event': event
        }

        # Schedule second pass with callback
        delay_seconds = self.double_pass.process_event(
            event,
            callback=lambda result: self._handle_second_pass_result(result)
        )

        self.stats['total_inspections'] += 1

        return {
            'double_pass_required': True,
            'decision': 'awaiting_second_pass',
            'dormant': True,
            'dormancy_indicators': [i.value for i in indicators],
            'second_pass_delay_ms': delay_seconds * 1000 if delay_seconds else 0,
            'fragment_id': fragment_id
        }

    def _handle_second_pass_result(self, result: DoublePassResult) -> None:
        """
        Handle result from second pass inspection.

        Args:
            result: DoublePassResult from double-pass system
        """
        event_id = result.event_id

        # Get inspection metadata
        inspection = self.active_inspections.get(event_id)
        if not inspection:
            logger.error(f"No inspection record for event {event_id}")
            return

        # Calculate activation time
        first_pass_time = inspection['first_pass_time']
        activation_time_ms = (datetime.now() - first_pass_time).total_seconds() * 1000

        # Update statistics
        if result.behavior_changed:
            self.stats['threats_caught'] += 1

            if result.threat_level_change == 'escalated':
                self.stats['dormant_to_active'] += 1

            # Update average activation time
            count = self.stats['dormant_to_active']
            prev_avg = self.stats['avg_activation_time_ms']
            new_avg = (prev_avg * (count - 1) + activation_time_ms) / count
            self.stats['avg_activation_time_ms'] = new_avg
        else:
            self.stats['false_dormant'] += 1

        # Store result in fragmentation database
        result_fragment_id = self.fragmentation_db.store_fragment({
            'type': 'double_pass_result',
            'event_id': event_id,
            'result': result.to_dict(),
            'activation_time_ms': activation_time_ms,
            'timestamp': datetime.now().isoformat()
        }, principal_id='system')

        # Create synergy link between first and second pass
        self.fragmentation_db.record_synergy(
            fragment_a_id=inspection['fragment_id'],
            fragment_b_id=result_fragment_id,
            synergy_type='double_pass_correlation',
            correlation_strength=1.0 if result.behavior_changed else 0.5,
            principal_id='system'
        )

        # Escalate to morphogenetic engine if threat activated
        if result.behavior_changed and result.recommendation in ['block', 'sandbox']:
            self._escalate_threat(event_id, result)

        # Clean up
        if event_id in self.active_inspections:
            del self.active_inspections[event_id]

        logger.info(
            f"Double-pass complete for event {event_id}: "
            f"changed={result.behavior_changed}, "
            f"recommendation={result.recommendation}, "
            f"activation_time={activation_time_ms:.1f}ms"
        )

    def _escalate_threat(self, event_id: str, result: DoublePassResult) -> None:
        """
        Escalate threat to morphogenetic engine for immediate action.

        Args:
            event_id: Event identifier
            result: DoublePassResult showing threat activation
        """
        logger.critical(
            f"THREAT ESCALATION: Event {event_id} activated on second pass. "
            f"Changes: {[c.value for c in result.changes_detected]}. "
            f"Action: {result.recommendation}"
        )

        # Create escalation event for morphogenetic engine
        escalation = {
            'event_id': event_id,
            'escalation_type': 'double_pass_activation',
            'original_event': result.second_pass.event_snapshot,
            'threat_level': 'CRITICAL' if result.threat_level_change == 'escalated' else 'HIGH',
            'changes_detected': [c.value for c in result.changes_detected],
            'recommendation': result.recommendation,
            'confidence': result.confidence,
            'timestamp': datetime.now().isoformat()
        }

        # Store escalation in fragmentation database
        self.fragmentation_db.store_fragment({
            'type': 'threat_escalation',
            'escalation': escalation,
            'timestamp': datetime.now().isoformat()
        }, principal_id='system')

        # Notify morphogenetic engine
        # (In production, would trigger immediate agent response)
        if result.recommendation == 'block':
            logger.critical(f"BLOCKING: Event {event_id} immediately blocked")
        elif result.recommendation == 'sandbox':
            logger.warning(f"SANDBOXING: Event {event_id} routed to honeypot")

    def get_statistics(self) -> Dict[str, Any]:
        """Get coordinator statistics"""
        return {
            'coordinator': self.stats.copy(),
            'double_pass_engine': self.double_pass.get_statistics(),
            'active_inspections': len(self.active_inspections)
        }

    def get_active_inspections(self) -> List[Dict[str, Any]]:
        """Get list of active double-pass inspections"""
        return [
            {
                'event_id': event_id,
                'first_pass_time': info['first_pass_time'].isoformat(),
                'dormancy_indicators': [i.value for i in info['indicators']],
                'fragment_id': info['fragment_id']
            }
            for event_id, info in self.active_inspections.items()
        ]


# Integration with morphogenetic engine
def integrate_double_pass(engine, fragmentation_db,
                         base_delay_ms: float = 200.0,
                         delay_variance_ms: float = 50.0):
    """
    Integrate double-pass recursion with morphogenetic engine.

    Args:
        engine: MorphogeneticEngine instance
        fragmentation_db: FragmentationSynergyDatabase instance
        base_delay_ms: Base delay for second pass
        delay_variance_ms: Random variance

    Returns:
        DoublePassCoordinator instance
    """
    coordinator = DoublePassCoordinator(
        morphogenetic_engine=engine,
        fragmentation_db=fragmentation_db,
        base_delay_ms=base_delay_ms,
        delay_variance_ms=delay_variance_ms
    )

    logger.info(
        "Double-pass recursion integrated with morphogenetic engine. "
        f"Delay: {base_delay_ms}ms ± {delay_variance_ms}ms"
    )

    return coordinator


if __name__ == "__main__":
    print("Double-Pass Coordinator Test")
    print("=" * 60)
    print("\nUse integrate_double_pass() to integrate with morphogenetic engine")
    print("\nExample:")
    print("  from morphogenetic_security import get_engine")
    print("  from agents.double_pass_coordinator import integrate_double_pass")
    print("")
    print("  engine = get_engine()")
    print("  coordinator = integrate_double_pass(engine, engine.fragmentation_db)")
    print("=" * 60)
