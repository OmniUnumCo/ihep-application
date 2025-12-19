"""
Reliability Drift Detection (CUSUM)
Implements FR-E4: System Evolution Adaptation
"""

import numpy as np
from typing import Optional, Tuple, List
from dataclasses import dataclass
from collections import deque

@dataclass
class DriftSignal:
    """Drift detection signal"""
    detected: bool
    S_t: float  # CUSUM statistic
    change_point: Optional[int]
    confidence: float
    

class CUSUMDriftDetector:
    """
    Cumulative Sum (CUSUM) control chart for reliability drift detection
    
    Formula: S_t = max(0, S_{t-1} + (R_actual(t) - μ_R - ε))
    
    REQ-E4.1: Detect systematic changes in R_actual(t)
    REQ-E4.2: Signal when S_t > h_threshold
    """
    
    def __init__(self, 
                 mu_baseline: float = 0.85,
                 sigma_baseline: float = 0.10,
                 epsilon_factor: float = 0.5,
                 h_factor: float = 5.0,
                 window_size: int = 50):
        """
        Initialize CUSUM detector
        
        Args:
            mu_baseline: Baseline mean reliability
            sigma_baseline: Baseline std deviation
            epsilon_factor: Allowable deviation (as multiple of sigma)
            h_factor: Threshold (as multiple of sigma)
            window_size: History window for change point detection
        """
        self.mu_baseline = mu_baseline
        self.sigma_baseline = sigma_baseline
        self.epsilon = epsilon_factor * sigma_baseline
        self.h_threshold = h_factor * sigma_baseline
        
        self.S_t = 0.0  # CUSUM statistic
        self.history: deque[float] = deque(maxlen=window_size)
        self.cusum_history: deque[float] = deque(maxlen=window_size)
        self.drift_detected = False
        self.change_point: Optional[int] = None
        self.t = 0
        
    def update(self, R_actual: float) -> DriftSignal:
        """
        Update CUSUM with new reliability observation
        
        Args:
            R_actual: Observed reliability [0,1]
            
        Returns:
            DriftSignal with detection status
        """
        # CUSUM update: S_t = max(0, S_{t-1} + (R_actual - μ - ε))
        deviation = R_actual - self.mu_baseline - self.epsilon
        self.S_t = max(0.0, self.S_t + deviation)
        
        # Store history
        self.history.append(R_actual)
        self.cusum_history.append(self.S_t)
        self.t += 1
        
        # Check for drift
        if self.S_t > self.h_threshold and not self.drift_detected:
            self.drift_detected = True
            self.change_point = self._estimate_change_point()
            
            return DriftSignal(
                detected=True,
                S_t=self.S_t,
                change_point=self.change_point,
                confidence=self._compute_confidence()
            )
        
        return DriftSignal(
            detected=False,
            S_t=self.S_t,
            change_point=None,
            confidence=0.0
        )
    
    def _estimate_change_point(self) -> int:
        """
        Estimate the time point where drift began
        Uses maximum likelihood approach
        
        Returns: Estimated change point index
        """
        if len(self.cusum_history) < 5:
            return max(0, self.t - 5)
        
        # Find the point where CUSUM started increasing rapidly
        cusum_array = np.array(list(self.cusum_history))
        gradients = np.gradient(cusum_array)
        
        # Change point is where gradient exceeds threshold
        threshold = np.mean(gradients) + 2 * np.std(gradients)
        candidates = np.where(gradients > threshold)[0]
        
        if len(candidates) > 0:
            # Return earliest candidate in recent window
            return max(0, self.t - len(self.cusum_history) + candidates[0])
        
        return max(0, self.t - 10)  # Default to 10 steps ago
    
    def _compute_confidence(self) -> float:
        """
        Compute confidence in drift detection
        
        Returns: Confidence score [0,1]
        """
        # Confidence based on how far S_t exceeds threshold
        excess = (self.S_t - self.h_threshold) / self.h_threshold
        confidence = min(1.0, 0.5 + 0.5 * excess)
        
        return confidence
    
    def reset(self):
        """Reset detector after recalibration"""
        self.S_t = 0.0
        self.drift_detected = False
        self.change_point = None
        # Keep history for analysis
    
    def get_statistics(self) -> dict:
        """Compute drift detection statistics"""
        if not self.history:
            return {}
        
        R_array = np.array(list(self.history))
        
        return {
            'current_S_t': self.S_t,
            'threshold': self.h_threshold,
            'drift_detected': self.drift_detected,
            'change_point': self.change_point,
            'mean_reliability': float(np.mean(R_array)),
            'std_reliability': float(np.std(R_array)),
            'baseline_deviation': float(np.mean(R_array) - self.mu_baseline),
            'observations': len(self.history)
        }


class BayesianChangePointDetector:
    """
    Bayesian change point detection for reliability shifts
    More sophisticated alternative to CUSUM
    """
    
    def __init__(self, prior_lambda: float = 0.01):
        """
        Initialize Bayesian change point detector
        
        Args:
            prior_lambda: Prior probability of change at any time step
        """
        self.prior_lambda = prior_lambda
        self.observations: List[float] = []
        self.change_probabilities: List[float] = []
        
    def update(self, R_actual: float) -> Tuple[float, Optional[int]]:
        """
        Update with new observation and compute change point probability
        
        Args:
            R_actual: New reliability observation
            
        Returns:
            (max_probability, most_likely_change_point)
        """
        self.observations.append(R_actual)
        n = len(self.observations)
        
        if n < 10:  # Need minimum data
            return 0.0, None
        
        # Compute posterior probabilities for each potential change point
        probs = []
        for tau in range(5, n-5):  # Avoid edges
            # Compute likelihood of change at tau
            before = self.observations[:tau]
            after = self.observations[tau:]
            
            # Log-likelihood ratio test
            mu_before = np.mean(before)
            mu_after = np.mean(after)
            sigma_pooled = np.std(self.observations)
            
            if sigma_pooled > 0:
                z_score = abs(mu_after - mu_before) / (sigma_pooled / np.sqrt(len(after)))
                prob = 1 / (1 + np.exp(-z_score))  # Sigmoid
            else:
                prob = 0.0
            
            probs.append(prob * self.prior_lambda)
        
        if probs:
            max_prob = max(probs)
            change_point = probs.index(max_prob) + 5
            self.change_probabilities.append(max_prob)
            return max_prob, change_point
        
        return 0.0, None
    
    def clear(self):
        """Clear observation history"""
        self.observations.clear()
        self.change_probabilities.clear()
