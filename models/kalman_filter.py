"""
Kalman Filter for Trust Dynamics
Implements optimal state estimation with prediction capability (Section 3.2)
"""

import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass

@dataclass
class KalmanState:
    """Kalman filter state representation"""
    x_hat: np.ndarray  # State estimate [3x1]
    P: np.ndarray      # Covariance matrix [3x3]
    
    
class TrustKalmanFilter:
    """
    Kalman Filter for trust calibration state estimation
    
    State space model:
        x(t+1) = Ax(t) + Bu(t) + w(t)
        z(t) = Cx(t) + v(t)
    
    State vector x = [T_user, R_actual, Δ_trust]ᵀ
    """
    
    def __init__(self, 
                 dt: float = 1.0,
                 process_noise_std: float = 0.05,
                 measurement_noise_std: float = 0.10):
        """
        Initialize Kalman filter
        
        Args:
            dt: Time step
            process_noise_std: Process noise standard deviation
            measurement_noise_std: Measurement noise standard deviation
        """
        # State transition matrix A [3x3]
        # Simple persistence model with drift
        self.A = np.array([
            [0.95, 0.0, 0.0],   # T_user persists with slight decay
            [0.0, 0.98, 0.0],   # R_actual persists (slower decay)
            [0.0, 0.0, 0.90]    # Δ_trust decays faster (auto-correction)
        ])
        
        # Control matrix B [3x1] - for interventions
        self.B = np.array([
            [0.05],  # Intervention affects T_user
            [0.0],   # No direct effect on R_actual
            [-0.10]  # Direct reduction in Δ_trust
        ])
        
        # Observation matrix C [3x3] - identity (full observation)
        self.C = np.eye(3)
        
        # Process noise covariance Q [3x3]
        q_var = process_noise_std ** 2
        self.Q = np.diag([q_var, q_var * 0.5, q_var * 1.5])
        
        # Measurement noise covariance R [3x3]
        r_var = measurement_noise_std ** 2
        self.R = np.diag([r_var, r_var * 0.8, r_var * 0.3])
        
        # Initial state estimate
        self.x_hat = np.array([0.5, 0.5, 0.0])  # Neutral initial state
        
        # Initial covariance P [3x3]
        self.P = np.eye(3) * 0.1
        
    def predict(self, u: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prediction step: x̂(t+1|t) = Ax̂(t|t) + Bu(t)
        
        Args:
            u: Control input (intervention) [1x1] or None
            
        Returns:
            (x_hat_pred, P_pred): Predicted state and covariance
        """
        # State prediction
        if u is not None:
            self.x_hat = self.A @ self.x_hat + self.B @ u
        else:
            self.x_hat = self.A @ self.x_hat
        
        # Covariance prediction: P(t+1|t) = AP(t|t)Aᵀ + Q
        self.P = self.A @ self.P @ self.A.T + self.Q
        
        return self.x_hat.copy(), self.P.copy()
    
    def update(self, z: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Update step: x̂(t|t) = x̂(t|t-1) + K(t)y(t)
        
        Args:
            z: Measurement vector [3x1]
            
        Returns:
            (x_hat_updated, P_updated): Updated state and covariance
        """
        # Innovation: y(t) = z(t) - Cx̂(t|t-1)
        y = z - self.C @ self.x_hat
        
        # Innovation covariance: S = CP(t|t-1)Cᵀ + R
        S = self.C @ self.P @ self.C.T + self.R
        
        # Kalman gain: K(t) = P(t|t-1)Cᵀ S⁻¹
        K = self.P @ self.C.T @ np.linalg.inv(S)
        
        # State update
        self.x_hat = self.x_hat + K @ y
        
        # Covariance update: P(t|t) = (I - KC)P(t|t-1)
        I = np.eye(3)
        self.P = (I - K @ self.C) @ self.P
        
        return self.x_hat.copy(), self.P.copy()
    
    def forecast(self, k: int, u_sequence: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Multi-step ahead prediction
        
        Args:
            k: Forecast horizon (number of steps)
            u_sequence: Control inputs [k x 1] or None
            
        Returns:
            (x_forecast, P_forecast_list): 
                x_forecast [k x 3] - predicted states
                P_forecast_list [k x 3 x 3] - predicted covariances
        """
        x_forecast = np.zeros((k, 3))
        P_forecast_list = np.zeros((k, 3, 3))
        
        # Save current state
        x_current = self.x_hat.copy()
        P_current = self.P.copy()
        
        for i in range(k):
            u = u_sequence[i] if u_sequence is not None else None
            x_pred, P_pred = self.predict(u)
            
            x_forecast[i] = x_pred
            P_forecast_list[i] = P_pred
        
        # Restore current state
        self.x_hat = x_current
        self.P = P_current
        
        return x_forecast, P_forecast_list
    
    def get_prediction_interval(self, x_pred: np.ndarray, P_pred: np.ndarray, 
                               alpha: float = 0.05) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute prediction interval
        
        Args:
            x_pred: Predicted state [3x1]
            P_pred: Predicted covariance [3x3]
            alpha: Significance level (default 0.05 for 95% CI)
            
        Returns:
            (lower_bound, upper_bound): Prediction interval bounds
        """
        from scipy.stats import norm
        z_score = norm.ppf(1 - alpha/2)  # 1.96 for 95%
        
        std = np.sqrt(np.diag(P_pred))
        lower = x_pred - z_score * std
        upper = x_pred + z_score * std
        
        return lower, upper
    
    def reset(self):
        """Reset filter to initial state"""
        self.x_hat = np.array([0.5, 0.5, 0.0])
        self.P = np.eye(3) * 0.1
    
    def get_state(self) -> KalmanState:
        """Return current filter state"""
        return KalmanState(x_hat=self.x_hat.copy(), P=self.P.copy())
    
    def set_state(self, state: KalmanState):
        """Set filter state"""
        self.x_hat = state.x_hat.copy()
        self.P = state.P.copy()


def compute_innovation_likelihood(innovation: np.ndarray, S: np.ndarray) -> float:
    """
    Compute likelihood of innovation (for outlier detection)
    
    Returns: Log-likelihood (higher is more consistent with model)
    """
    det_S = np.linalg.det(S)
    inv_S = np.linalg.inv(S)
    
    log_likelihood = -0.5 * (
        innovation.T @ inv_S @ innovation + 
        np.log(det_S) + 
        3 * np.log(2 * np.pi)
    )
    
    return float(log_likelihood)
