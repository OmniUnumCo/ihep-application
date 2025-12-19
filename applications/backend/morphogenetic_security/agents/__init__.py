#!/usr/bin/env python3
"""
IHEP Morphogenetic Security - Agent System

Double-Pass Recursion Detection:
- Catches dormant threats off-guard
- Randomized second pass (~0.2s ± variance)
- Behavioral change analysis
- Automated threat escalation
"""

from .double_pass_recursion import (
    DoublePassRecursion,
    DoublePassResult,
    PassObservation,
    BehaviorChange,
    DormancyIndicator
)

from .double_pass_coordinator import (
    DoublePassCoordinator,
    integrate_double_pass
)

__all__ = [
    'DoublePassRecursion',
    'DoublePassResult',
    'PassObservation',
    'BehaviorChange',
    'DormancyIndicator',
    'DoublePassCoordinator',
    'integrate_double_pass'
]
