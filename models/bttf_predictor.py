"""
Bayesian Trust Trajectory Forecasting (BTTF)
Implements FR-E3: Predictive Forecasting System (Section 5.1)
"""

import numpy as np
from typing import Tuple, List, Optional, Dict
from dataclasses import dataclass
from scipy.stats import norm

from .kalman_filter import TrustKalmanFilter
from .latent_inference import LatentVariableInference, LatentVariables

@dataclass
class ForecastResult:
    """Multi-step forecast result"""
    horizon: int
    means: np.ndarray  # [k x 3] predicted states
    stds: np.ndarray   # [k x 3] prediction uncertainties
    delta_means: np.ndarray  # [k] predicted Δ_trust
    delta_stds: np.ndarray   # [k] Δ_trust uncertainties
    intervention_trigger: Optional[int]  # Time step to trigger intervention
    confidence: float  # Confidence in prediction
    
    def get_prediction_intervals(self, alpha: float = 0.05) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute prediction intervals for Δ_trust
        
        Args:
            alpha: Significance level (0.05 for 95% CI)
            
        Returns:
            (lower_bounds, upper_bounds): [k] arrays
        """
        z_score = norm.ppf(1 - alpha/2)  # 1.96 for 95%
        
        lower = self.delta_means - z_score * self.delta_stds
        upper = self.delta_means + z_score * self.delta_stds
        
        return lower, upper
    
    def get_miscalibration_probability(self, threshold: float = 0.15) -> np.ndarray:
        """
        Compute P(Δ(t+k) > threshold) for each k
        
        Args:
            threshold: Miscalibration threshold
            
        Returns:
            probabilities: [k] array of probabilities
        """
        # P(Δ > threshold) = 1 - Φ((threshold - μ) / σ)
        z_scores = (threshold - self.delta_means) / self.delta_stds
        probabilities = 1 - norm.cdf(z_scores)
        
        return probabilities


class BTTFPredictor:
    """
    Bayesian Trust Trajectory Forecasting
    
    Algorithm: BTTF(x(t), L(t), k)
    
    REQ-E3.1: k-step ahead predictions (k ∈ [1,5])
    REQ-E3.2: Provide 95% prediction intervals
    REQ-E3.3: Trigger intervention if P(Δ(t+k) > 0.15) > 0.85
    REQ-E3.4: Forecast accuracy target MAPE ≤ 15%
    """
    
    def __init__(self, 
                 kalman_filter: TrustKalmanFilter,
                 latent_inference: LatentVariableInference,
                 intervention_threshold: float = 0.15,
                 intervention_confidence: float = 0.85):
        """
        Initialize BTTF predictor
        
        Args:
            kalman_filter: Kalman filter for state estimation
            latent_inference: Latent variable inference module
            intervention_threshold: Δ_trust threshold for intervention
            intervention_confidence: Confidence threshold for triggering
        """
        self.kf = kalman_filter
        self.latent_inf = latent_inference
        self.intervention_threshold = intervention_threshold
        self.intervention_confidence = intervention_confidence
        
        # Performance tracking
        self.predictions: List[ForecastResult] = []
        self.actuals: List[float] = []
        
    def forecast(self, 
                 x_current: np.ndarray,
                 latent: LatentVariables,
                 k: int = 3,
                 u_sequence: Optional[np.ndarray] = None) -> ForecastResult:
        """
        Execute BTTF forecasting algorithm
        
        Algorithm:
        1. Initialize state prediction using Kalman filter
        2. For each horizon i=1 to k:
           a. Predict state x̂(t+i|t)
           b. Compute μ_Δ(i) conditioned on latent variables
           c. Check confidence gate: P(Δ(t+i) > 0.15 | μ, σ²) > 0.85
           d. If triggered, return early with intervention signal
           e. Propagate state forward
        3. Return forecast trajectory
        
        Args:
            x_current: Current state [T_user, R_actual, Δ_trust]
            latent: Inferred latent variables
            k: Forecast horizon (1-5)
            u_sequence: Control inputs [k x 1] or None
            
        Returns:
            ForecastResult with predictions and intervention signal
        """
        # Initialize storage
        x_forecast = np.zeros((k, 3))
        P_forecast = np.zeros((k, 3, 3))
        delta_means = np.zeros(k)
        delta_stds = np.zeros(k)
        
        # Save Kalman filter state
        kf_state_backup = self.kf.get_state()
        
        # Set current state
        self.kf.x_hat = x_current.copy()
        
        intervention_trigger = None
        
        for i in range(k):
            # Get control input for this step
            u = u_sequence[i] if u_sequence is not None else None
            
            # Kalman prediction step
            x_pred, P_pred = self.kf.predict(u)
            
            # Store predictions
            x_forecast[i] = x_pred
            P_forecast[i] = P_pred
            
            # Latent-conditioned delta prediction
            mu_delta_latent, sigma_delta_latent = self.latent_inf.get_predictive_distribution(latent)
            
            # Combine Kalman and latent predictions
            # Kalman gives x_pred[2] = Δ_trust from state dynamics
            # Latent model gives μ_Δ from hidden factors
            # Weighted combination
            w_kalman = 0.6
            w_latent = 0.4
            
            mu_delta = w_kalman * x_pred[2] + w_latent * mu_delta_latent
            
            # Combined uncertainty (variance addition)
            sigma_kalman = np.sqrt(P_pred[2, 2])
            sigma_delta = np.sqrt(
                (w_kalman * sigma_kalman) ** 2 + 
                (w_latent * sigma_delta_latent) ** 2
            )
            
            delta_means[i] = mu_delta
            delta_stds[i] = sigma_delta
            
            # Confidence gate: P(Δ(t+i) > threshold) > confidence_threshold
            prob_miscalibration = 1 - norm.cdf(
                (self.intervention_threshold - mu_delta) / sigma_delta
            )
            
            if prob_miscalibration > self.intervention_confidence:
                intervention_trigger = i + 1  # Trigger at step i+1
                break  # Early stopping
        
        # Restore Kalman filter state
        self.kf.set_state(kf_state_backup)
        
        # Compute overall forecast confidence
        confidence = self._compute_forecast_confidence(delta_stds)
        
        result = ForecastResult(
            horizon=k,
            means=x_forecast,
            stds=np.sqrt(np.array([np.diag(P) for P in P_forecast])),
            delta_means=delta_means,
            delta_stds=delta_stds,
            intervention_trigger=intervention_trigger,
            confidence=confidence
        )
        
        self.predictions.append(result)
        
        return result
    
    def _compute_forecast_confidence(self, stds: np.ndarray) -> float:
        """
        Compute overall confidence in forecast
        
        Lower uncertainty → higher confidence
        
        Args:
            stds: Standard deviations across horizon
            
        Returns:
            Confidence score [0,1]
        """
        # Average relative uncertainty
        mean_std = np.mean(stds)
        
        # Confidence decreases with uncertainty
        # σ=0 → conf=1.0, σ=0.2 → conf=0.5, σ→∞ → conf=0
        confidence = np.exp(-5 * mean_std)
        
        return float(np.clip(confidence, 0.0, 1.0))
    
    def evaluate_forecast(self, actual_delta: float) -> Dict[str, float]:
        """
        Evaluate forecast accuracy against actual observation
        
        Computes:
        - Absolute error
        - Percentage error
        - Whether actual fell within prediction interval
        - Calibration score
        
        Args:
            actual_delta: Observed Δ_trust
            
        Returns:
            Evaluation metrics dictionary
        """
        if not self.predictions:
            return {}
        
        self.actuals.append(actual_delta)
        
        # Get most recent 1-step forecast
        last_forecast = self.predictions[-1]
        predicted_delta = last_forecast.delta_means[0]
        predicted_std = last_forecast.delta_stds[0]
        
        # Absolute error
        abs_error = abs(actual_delta - predicted_delta)
        
        # Percentage error
        pct_error = abs_error / max(actual_delta, 0.01) * 100
        
        # Within prediction interval?
        lower, upper = last_forecast.get_prediction_intervals(alpha=0.05)
        within_interval = lower[0] <= actual_delta <= upper[0]
        
        # Standardized residual (for calibration check)
        z_score = (actual_delta - predicted_delta) / predicted_std if predicted_std > 0 else 0
        
        return {
            'absolute_error': abs_error,
            'percentage_error': pct_error,
            'within_95_interval': within_interval,
            'z_score': z_score,
            'predicted': predicted_delta,
            'actual': actual_delta
        }
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """
        Compute aggregate performance metrics
        
        REQ-E3.4: MAPE ≤ 15%
        
        Returns:
            Performance metrics dictionary
        """
        if len(self.actuals) < 5:
            return {'status': 'insufficient_data'}
        
        # Compute metrics over all predictions
        errors = []
        pct_errors = []
        within_interval_count = 0
        
        for i, (pred, actual) in enumerate(zip(self.predictions[-len(self.actuals):], self.actuals)):
            pred_delta = pred.delta_means[0]
            abs_err = abs(actual - pred_delta)
            pct_err = abs_err / max(actual, 0.01) * 100
            
            errors.append(abs_err)
            pct_errors.append(pct_err)
            
            lower, upper = pred.get_prediction_intervals()
            if lower[0] <= actual <= upper[0]:
                within_interval_count += 1
        
        # Mean Absolute Error
        mae = np.mean(errors)
        
        # Mean Absolute Percentage Error
        mape = np.mean(pct_errors)
        
        # Root Mean Squared Error
        rmse = np.sqrt(np.mean(np.array(errors) ** 2))
        
        # Forecast Accuracy (REQ metric)
        fa = 1 - (mape / 100)
        
        # Coverage (should be ~95% for well-calibrated intervals)
        coverage = within_interval_count / len(self.actuals)
        
        return {
            'mae': float(mae),
            'mape': float(mape),
            'rmse': float(rmse),
            'forecast_accuracy': float(fa),
            'interval_coverage': float(coverage),
            'n_predictions': len(self.actuals),
            'target_mape': 15.0,
            'target_fa': 0.75,
            'meets_target': fa >= 0.75
        }
    
    def clear_history(self):
        """Clear prediction history"""
        self.predictions.clear()
        self.actuals.clear()


class InterventionGateController:
    """
    Controls when to trigger proactive interventions
    
    REQ-E3.3: Trigger if P(Δ(t+k) > 0.15) > 0.85
    """
    
    def __init__(self, 
                 threshold: float = 0.15,
                 confidence: float = 0.85,
                 cooldown_steps: int = 10):
        """
        Initialize intervention gate
        
        Args:
            threshold: Δ_trust threshold
            confidence: Probability threshold for triggering
            cooldown_steps: Minimum steps between interventions
        """
        self.threshold = threshold
        self.confidence = confidence
        self.cooldown_steps = cooldown_steps
        self.steps_since_intervention = cooldown_steps  # Start ready
        
    def should_intervene(self, forecast: ForecastResult) -> Tuple[bool, str]:
        """
        Determine if intervention should be triggered
        
        Args:
            forecast: Forecast result from BTTF
            
        Returns:
            (should_trigger, reason): Intervention decision and explanation
        """
        # Check cooldown
        if self.steps_since_intervention < self.cooldown_steps:
            self.steps_since_intervention += 1
            return False, f"cooldown_{self.steps_since_intervention}/{self.cooldown_steps}"
        
        # Check if forecast triggered intervention
        if forecast.intervention_trigger is not None:
            self.steps_since_intervention = 0
            horizon = forecast.intervention_trigger
            prob = forecast.get_miscalibration_probability(self.threshold)[horizon - 1]
            return True, f"predicted_miscalibration_k={horizon}_p={prob:.3f}"
        
        self.steps_since_intervention += 1
        return False, "no_threat_detected"
    
    def reset_cooldown(self):
        """Reset intervention cooldown"""
        self.steps_since_intervention = self.cooldown_steps
