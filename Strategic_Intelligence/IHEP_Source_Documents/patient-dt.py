import numpy as np
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class PatientState:
    viral_load_log: float
    adherence_score: float  # 0.0 to 1.0
    psychosocial_stress: float  # 0.0 to 1.0
    system_engagement: float # 0.0 to 1.0

class DigitalTwin:
    def __init__(self, patient_id: str, initial_state: PatientState):
        self.patient_id = patient_id
        self.state = initial_state
        # Diffusion coefficient for risk propagation (D in the math model)
        self.risk_diffusion_rate = 0.15 
        # Decay rate for intervention effects (lambda in the math model)
        self.intervention_decay = 0.05

    def calculate_trajectory(self, time_step_days: int, intervention: float = 0.0) -> float:
        """
        Predicts the health trajectory (phi) using a discretized 
        Reaction-Diffusion approach.
        
        dphi/dt = D * grad(phi) + f(phi) - lambda * phi
        """
        
        # Current composite risk score (phi)
        # Higher score = Higher risk of dropout/failure
        phi = (0.4 * self.state.viral_load_log) + \
              (0.3 * (1.0 - self.state.adherence_score)) + \
              (0.3 * self.state.psychosocial_stress)

        # Reaction component (f(phi)): System engagement reduces risk non-linearly
        reaction = -1.0 * (self.state.system_engagement ** 2)
        
        # Diffusion component (simplified for 1D time-series): 
        # Volatility in adherence increases future risk
        diffusion = self.risk_diffusion_rate * np.var([self.state.adherence_score])
        
        # Rate of change
        dphi_dt = diffusion + reaction - (self.intervention_decay * intervention)
        
        # Project future risk
        future_risk = phi + (dphi_dt * time_step_days)
        return max(0.0, min(1.0, future_risk))

# Example Usage
initial = PatientState(viral_load_log=2.3, adherence_score=0.85, psychosocial_stress=0.6, system_engagement=0.4)
twin = DigitalTwin("PT-10249", initial)

# Predict risk 30 days out without intervention
risk_no_action = twin.calculate_trajectory(30, intervention=0.0)

# Predict risk 30 days out WITH nurse intervention
risk_with_action = twin.calculate_trajectory(30, intervention=0.8)

print(f"Projected Risk (No Action): {risk_no_action:.4f}")
print(f"Projected Risk (Intervention): {risk_with_action:.4f}")