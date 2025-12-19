"""
Trust Calibration State Tracker
Implements temporal state tracking with sliding window history (FR-E1)
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from collections import deque
from datetime import datetime

@dataclass
class TrustState:
    """State vector: [T_user, R_actual, Δ_trust]"""
    timestamp: datetime
    T_user: float  # User trust level [0,1]
    R_actual: float  # AI actual reliability [0,1]
    delta_trust: float  # Trust calibration delta
    behavioral_signals: Dict[str, float] = field(default_factory=dict)
    
    def to_vector(self) -> np.ndarray:
        """Convert to state vector representation"""
        return np.array([self.T_user, self.R_actual, self.delta_trust])
    
    def __post_init__(self):
        """Validate state bounds"""
        assert 0 <= self.T_user <= 1, f"T_user out of bounds: {self.T_user}"
        assert 0 <= self.R_actual <= 1, f"R_actual out of bounds: {self.R_actual}"
        self.delta_trust = abs(self.T_user - self.R_actual)


class StateTracker:
    """
    Maintains sliding window history of trust states
    REQ-E1.1: Window size W=20 interactions
    REQ-E1.4: State update latency < 50ms
    """
    
    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self.history: deque[TrustState] = deque(maxlen=window_size)
        self.interaction_count = 0
        
    def update(self, T_user: float, R_actual: float, 
               behavioral_signals: Optional[Dict[str, float]] = None) -> TrustState:
        """
        Update state with new observation
        Returns: Updated TrustState
        """
        state = TrustState(
            timestamp=datetime.now(),
            T_user=T_user,
            R_actual=R_actual,
            delta_trust=abs(T_user - R_actual),
            behavioral_signals=behavioral_signals or {}
        )
        
        self.history.append(state)
        self.interaction_count += 1
        
        return state
    
    def get_current_state(self) -> Optional[TrustState]:
        """Return most recent state"""
        return self.history[-1] if self.history else None
    
    def get_state_trajectory(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Extract state trajectories: T_user(t), R_actual(t), Δ_trust(t)
        Returns: (T_user_array, R_actual_array, delta_array)
        """
        if not self.history:
            return np.array([]), np.array([]), np.array([])
        
        T_user = np.array([s.T_user for s in self.history])
        R_actual = np.array([s.R_actual for s in self.history])
        delta = np.array([s.delta_trust for s in self.history])
        
        return T_user, R_actual, delta
    
    def get_state_matrix(self) -> np.ndarray:
        """
        Return state history as matrix [N x 3]
        Columns: [T_user, R_actual, Δ_trust]
        """
        if not self.history:
            return np.array([]).reshape(0, 3)
        
        return np.array([s.to_vector() for s in self.history])
    
    def get_behavioral_signals(self, signal_name: str) -> np.ndarray:
        """Extract specific behavioral signal trajectory"""
        return np.array([
            s.behavioral_signals.get(signal_name, 0.0) 
            for s in self.history
        ])
    
    def compute_statistics(self) -> Dict[str, float]:
        """Compute trajectory statistics"""
        if len(self.history) < 2:
            return {}
        
        T_user, R_actual, delta = self.get_state_trajectory()
        
        return {
            'mean_delta': float(np.mean(delta)),
            'std_delta': float(np.std(delta)),
            'max_delta': float(np.max(delta)),
            'mean_T_user': float(np.mean(T_user)),
            'mean_R_actual': float(np.mean(R_actual)),
            'delta_trend': float(np.polyfit(range(len(delta)), delta, 1)[0]),
            'reliability_drift': float(np.polyfit(range(len(R_actual)), R_actual, 1)[0])
        }
    
    def is_miscalibrated(self, threshold: float = 0.15) -> bool:
        """Check if current state exceeds calibration threshold"""
        current = self.get_current_state()
        return current.delta_trust > threshold if current else False
    
    def clear(self):
        """Clear all history"""
        self.history.clear()
        self.interaction_count = 0
