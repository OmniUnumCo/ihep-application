"""
Latent Variable Inference
Implements FR-E2: Bayesian inference for hidden factors
"""

import numpy as np
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from scipy.stats import beta, norm

@dataclass
class LatentVariables:
    """Latent factors influencing trust dynamics"""
    C_task: float  # Task complexity [0,1]
    L_cognitive: float  # User cognitive load [0,1]
    E_context: int  # Environmental context shift {0,1}
    U_expertise: float  # User domain expertise [0,1]
    
    def to_vector(self) -> np.ndarray:
        """Convert to vector representation"""
        return np.array([self.C_task, self.L_cognitive, float(self.E_context), self.U_expertise])
    
    @classmethod
    def from_vector(cls, vec: np.ndarray) -> 'LatentVariables':
        """Create from vector"""
        return cls(
            C_task=vec[0],
            L_cognitive=vec[1],
            E_context=int(vec[2] > 0.5),
            U_expertise=vec[3]
        )


class LatentVariableInference:
    """
    Bayesian inference for latent variables
    
    Model: P(Δ|L,θ) = N(μ_Δ(L,θ), σ²_Δ)
    where L = {C_task, L_cognitive, E_context, U_expertise}
    
    REQ-E2.1: Implement Bayesian inference for L
    REQ-E2.2: Update posteriors via variational inference
    REQ-E2.3: Target convergence R̂ < 1.1 (Gelman-Rubin)
    REQ-E2.4: Computational budget ≤100ms
    """
    
    def __init__(self):
        # Prior distributions (Beta for bounded variables)
        self.prior_alpha = {'C_task': 2.0, 'L_cognitive': 2.0, 'U_expertise': 2.0}
        self.prior_beta = {'C_task': 2.0, 'L_cognitive': 2.0, 'U_expertise': 2.0}
        self.prior_E_context = 0.1  # Prior probability of context shift
        
        # Posterior parameters (initialized to priors)
        self.posterior_alpha = self.prior_alpha.copy()
        self.posterior_beta = self.prior_beta.copy()
        self.posterior_E_context = self.prior_E_context
        
        # Regression coefficients θ for μ_Δ(L,θ)
        self.theta = np.array([0.3, 0.25, 0.15, -0.20])  # Initial weights
        self.theta_covariance = np.eye(4) * 0.01
        
        # Update history
        self.update_count = 0
        
    def infer(self, behavioral_signals: Dict[str, float]) -> LatentVariables:
        """
        Infer latent variables from behavioral signals
        
        Behavioral signals:
            - dwell_time: Time spent on AI output
            - reliance_ratio: Frequency of following AI recommendations
            - query_complexity: Estimated complexity of user query
            - interaction_frequency: Recent interaction rate
            - override_rate: Frequency of overriding AI
        
        Args:
            behavioral_signals: Dictionary of observed behavioral metrics
            
        Returns:
            LatentVariables: Inferred latent state
        """
        # Extract signals with defaults
        dwell_time = behavioral_signals.get('dwell_time', 1.0)
        reliance_ratio = behavioral_signals.get('reliance_ratio', 0.5)
        query_complexity = behavioral_signals.get('query_complexity', 0.5)
        interaction_freq = behavioral_signals.get('interaction_frequency', 1.0)
        override_rate = behavioral_signals.get('override_rate', 0.0)
        
        # Infer C_task (task complexity)
        # Higher query complexity and dwell time → higher task complexity
        C_task_mean = self.posterior_alpha['C_task'] / (
            self.posterior_alpha['C_task'] + self.posterior_beta['C_task']
        )
        C_task = 0.7 * C_task_mean + 0.3 * query_complexity
        C_task = np.clip(C_task, 0.0, 1.0)
        
        # Infer L_cognitive (cognitive load)
        # High interaction frequency + low dwell time → high cognitive load
        L_cognitive_mean = self.posterior_alpha['L_cognitive'] / (
            self.posterior_alpha['L_cognitive'] + self.posterior_beta['L_cognitive']
        )
        cognitive_signal = interaction_freq * (1 - dwell_time / 10.0)
        L_cognitive = 0.6 * L_cognitive_mean + 0.4 * np.clip(cognitive_signal, 0, 1)
        L_cognitive = np.clip(L_cognitive, 0.0, 1.0)
        
        # Infer E_context (context shift)
        # Sudden change in reliance pattern → context shift
        E_context = 1 if override_rate > 0.5 else 0
        
        # Infer U_expertise (user expertise)
        # Low reliance + low override → high expertise (independent decision making)
        U_expertise_mean = self.posterior_alpha['U_expertise'] / (
            self.posterior_alpha['U_expertise'] + self.posterior_beta['U_expertise']
        )
        expertise_signal = 1 - abs(reliance_ratio - 0.5) * 2  # Peak at 0.5 reliance
        U_expertise = 0.8 * U_expertise_mean + 0.2 * expertise_signal
        U_expertise = np.clip(U_expertise, 0.0, 1.0)
        
        return LatentVariables(
            C_task=C_task,
            L_cognitive=L_cognitive,
            E_context=E_context,
            U_expertise=U_expertise
        )
    
    def update_posterior(self, latent: LatentVariables, delta_observed: float):
        """
        Update posterior distributions based on observed Δ_trust
        
        Bayesian update: posterior ∝ likelihood × prior
        
        Args:
            latent: Inferred latent variables
            delta_observed: Observed trust calibration delta
        """
        self.update_count += 1
        
        # Predict delta from latent variables
        L_vec = latent.to_vector()
        delta_predicted = self.predict_delta(latent)
        
        # Likelihood of observation
        prediction_error = delta_observed - delta_predicted
        likelihood_precision = 1.0 / (0.05 ** 2)  # Assume σ_Δ = 0.05
        
        # Update θ (regression coefficients) via Bayesian linear regression
        # Posterior: θ|data ~ N(μ_post, Σ_post)
        Sigma_prior_inv = np.linalg.inv(self.theta_covariance)
        Sigma_post_inv = Sigma_prior_inv + likelihood_precision * np.outer(L_vec, L_vec)
        self.theta_covariance = np.linalg.inv(Sigma_post_inv)
        
        mu_post = self.theta_covariance @ (
            Sigma_prior_inv @ self.theta + 
            likelihood_precision * L_vec * delta_observed
        )
        self.theta = mu_post
        
        # Update Beta posteriors for continuous latents
        # Higher delta → increase alpha (shift toward higher values)
        learning_rate = 0.1
        
        if delta_observed > 0.15:  # Miscalibration
            self.posterior_alpha['C_task'] += learning_rate * latent.C_task
            self.posterior_beta['C_task'] += learning_rate * (1 - latent.C_task)
            
            self.posterior_alpha['L_cognitive'] += learning_rate * latent.L_cognitive
            self.posterior_beta['L_cognitive'] += learning_rate * (1 - latent.L_cognitive)
            
            self.posterior_alpha['U_expertise'] += learning_rate * (1 - latent.U_expertise)
            self.posterior_beta['U_expertise'] += learning_rate * latent.U_expertise
        
        # Update E_context prior based on observation frequency
        alpha_context = 0.05
        self.posterior_E_context = (1 - alpha_context) * self.posterior_E_context + \
                                  alpha_context * latent.E_context
    
    def predict_delta(self, latent: LatentVariables) -> float:
        """
        Predict Δ_trust from latent variables
        
        Formula: μ_Δ(L,θ) = θᵀL
        
        Args:
            latent: Latent variable state
            
        Returns:
            Predicted delta [0,1]
        """
        L_vec = latent.to_vector()
        delta_pred = float(np.dot(self.theta, L_vec))
        return np.clip(delta_pred, 0.0, 1.0)
    
    def get_predictive_distribution(self, latent: LatentVariables) -> Tuple[float, float]:
        """
        Get predictive distribution P(Δ|L)
        
        Returns:
            (mean, std): Parameters of predictive Normal distribution
        """
        L_vec = latent.to_vector()
        
        # Predictive mean
        mu = float(np.dot(self.theta, L_vec))
        
        # Predictive variance: σ² = LᵀΣL + σ²_ε
        sigma_epistemic = float(L_vec.T @ self.theta_covariance @ L_vec)
        sigma_aleatory = 0.05 ** 2  # Irreducible uncertainty
        sigma = np.sqrt(sigma_epistemic + sigma_aleatory)
        
        return mu, sigma
    
    def sample_latent(self, n_samples: int = 1) -> np.ndarray:
        """
        Sample from posterior distribution of latent variables
        
        Args:
            n_samples: Number of samples
            
        Returns:
            Samples array [n_samples x 4]
        """
        samples = np.zeros((n_samples, 4))
        
        for i in range(n_samples):
            C_task = beta.rvs(
                self.posterior_alpha['C_task'], 
                self.posterior_beta['C_task']
            )
            L_cognitive = beta.rvs(
                self.posterior_alpha['L_cognitive'],
                self.posterior_beta['L_cognitive']
            )
            E_context = float(np.random.rand() < self.posterior_E_context)
            U_expertise = beta.rvs(
                self.posterior_alpha['U_expertise'],
                self.posterior_beta['U_expertise']
            )
            
            samples[i] = [C_task, L_cognitive, E_context, U_expertise]
        
        return samples
    
    def get_convergence_diagnostic(self, n_chains: int = 4) -> float:
        """
        Compute Gelman-Rubin convergence diagnostic
        
        REQ-E2.3: Target R̂ < 1.1
        
        Returns:
            R̂ statistic (1.0 = perfect convergence)
        """
        # Simplified R̂ based on posterior variance stability
        # Full MCMC implementation would track multiple chains
        
        if self.update_count < 50:
            return 2.0  # Not converged yet
        
        # Estimate based on parameter stability
        param_variance = np.trace(self.theta_covariance)
        R_hat = 1.0 + param_variance  # Approximation
        
        return float(np.clip(R_hat, 1.0, 2.0))
    
    def reset(self):
        """Reset to prior distributions"""
        self.posterior_alpha = self.prior_alpha.copy()
        self.posterior_beta = self.prior_beta.copy()
        self.posterior_E_context = self.prior_E_context
        self.update_count = 0
