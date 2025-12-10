#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MORPHOGENETIC FRAMEWORK - PYTHON IMPLEMENTATION
UTF-8 Clean - No Emojis - Production Ready
Version: 3.0
Date: November 10, 2025
"""

import json
import math
import time
from collections import deque
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum


# ============================================================================
# SIGNAL DEFINITIONS
# ============================================================================

@dataclass
class SignalState:
    """Normalized signal state [0, 1]"""
    E: float  # Error rate
    L: float  # Latency
    S: float  # Spare capacity
    timestamp: float


class SignalNormalizer:
    """Normalize raw measurements to [0, 1]"""
    
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.E_history = deque(maxlen=window_size)
        self.L_history = deque(maxlen=window_size)
        self.S_history = deque(maxlen=window_size)
        self.E_baseline = 0.0
        self.L_baseline = 0.0
    
    def normalize_error(self, E_raw: float, E_max: float = 0.10) -> float:
        """Normalize error rate to [0, 1]"""
        E_normalized = min(E_raw / E_max, 1.0)
        return max(0.0, E_normalized)
    
    def normalize_latency(self, L_raw: float, L_slo: float) -> float:
        """Normalize latency to [0, 1]"""
        L_normalized = min((L_raw / L_slo) / 5.0, 1.0)
        return max(0.0, L_normalized)
    
    def normalize_capacity(self, S_raw: float) -> float:
        """Capacity already in [0, 1]"""
        return max(0.0, min(S_raw, 1.0))
    
    def get_percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile (0-100)"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100.0)
        return sorted_data[min(index, len(sorted_data) - 1)]


# ============================================================================
# FIELD DYNAMICS
# ============================================================================

class FieldDynamics:
    """Morphogenetic field computation: inject + diffuse + decay"""
    
    def __init__(self, num_nodes: int, adjacency_matrix: List[List[int]]):
        self.num_nodes = num_nodes
        self.A = adjacency_matrix  # Adjacency matrix
        self.D_matrix = self._compute_degree_matrix()
        self.L_norm = self._compute_normalized_laplacian()
        self.phi_E = [0.0] * num_nodes
        self.phi_L = [0.0] * num_nodes
        self.phi_S = [0.0] * num_nodes
        
        # Constants
        self.beta = 0.2  # Decay factor
        self.k_inject = {'E': 1.0, 'L': 0.8, 'S': 0.6}
        self.lambda_decay = {'E': 0.05, 'L': 0.08, 'S': 0.03}
        
        # Cross-coupling
        self.kappa_LE = 0.15  # Error -> Latency
        self.kappa_SE = 0.10  # Error -> Capacity
        
        # Diffusion
        self.deg_max = max([sum(row) for row in adjacency_matrix])
        self.D_base = {'E': 0.15, 'L': 0.20, 'S': 0.10}
        self.D = self._compute_safe_diffusion()
    
    def _compute_degree_matrix(self) -> List[List[float]]:
        """Compute degree matrix D"""
        D = [[0.0] * self.num_nodes for _ in range(self.num_nodes)]
        for i in range(self.num_nodes):
            degree = sum(self.A[i])
            if degree > 0:
                D[i][i] = float(degree)
        return D
    
    def _compute_normalized_laplacian(self) -> List[List[float]]:
        """Compute L_norm = I - D^(-1/2) * A * D^(-1/2)"""
        # Compute D^(-1/2)
        D_inv_sqrt = [[0.0] * self.num_nodes for _ in range(self.num_nodes)]
        for i in range(self.num_nodes):
            degree = self.D_matrix[i][i]
            if degree > 0:
                D_inv_sqrt[i][i] = 1.0 / math.sqrt(degree)
        
        # Compute D^(-1/2) * A
        temp = [[0.0] * self.num_nodes for _ in range(self.num_nodes)]
        for i in range(self.num_nodes):
            for j in range(self.num_nodes):
                for k in range(self.num_nodes):
                    temp[i][j] += D_inv_sqrt[i][k] * self.A[k][j]
        
        # Compute D^(-1/2) * A * D^(-1/2)
        DAD = [[0.0] * self.num_nodes for _ in range(self.num_nodes)]
        for i in range(self.num_nodes):
            for j in range(self.num_nodes):
                for k in range(self.num_nodes):
                    DAD[i][j] += temp[i][k] * D_inv_sqrt[k][j]
        
        # Compute L_norm = I - DAD
        L = [[0.0] * self.num_nodes for _ in range(self.num_nodes)]
        for i in range(self.num_nodes):
            for j in range(self.num_nodes):
                if i == j:
                    L[i][j] = 1.0 - DAD[i][j]
                else:
                    L[i][j] = -DAD[i][j]
        
        return L
    
    def _compute_safe_diffusion(self) -> Dict[str, float]:
        """Compute D_actual = min(D_base, 0.25 / deg_max)"""
        if self.deg_max < 1:
            self.deg_max = 1
        safe_cap = 0.25 / self.deg_max
        
        return {
            'E': min(self.D_base['E'], safe_cap),
            'L': min(self.D_base['L'], safe_cap),
            'S': min(self.D_base['S'], safe_cap)
        }
    
    def _matrix_vector_mult(self, matrix: List[List[float]], vector: List[float]) -> List[float]:
        """Multiply matrix * vector"""
        result = [0.0] * len(vector)
        for i in range(len(vector)):
            for j in range(len(vector)):
                result[i] += matrix[i][j] * vector[j]
        return result
    
    def _decay_exp(self, phi: List[float], lambda_val: float, dt: float = 1.0) -> List[float]:
        """Apply exponential decay: phi * exp(-lambda * dt)"""
        decay_factor = math.exp(-lambda_val * dt)
        return [p * decay_factor for p in phi]
    
    def update(self, signal: Dict[str, float], source: Dict[str, List[float]]) -> None:
        """
        Update fields: phi(t+1) = (1-beta)*phi(t) + alpha*source + D*L_norm*phi + cross_coupling
        
        Args:
            signal: Current signal values (E, L, S)
            source: Source field for each node (E, L, S lists)
        """
        
        # Inject new signals
        phi_E_inject = [self.k_inject['E'] * s for s in source['E']]
        phi_L_inject = [self.k_inject['L'] * s for s in source['L']]
        phi_S_inject = [self.k_inject['S'] * s for s in source['S']]
        
        # Diffusion
        phi_E_diffuse = self._matrix_vector_mult(self.L_norm, self.phi_E)
        phi_E_diffuse = [self.D['E'] * p for p in phi_E_diffuse]
        
        phi_L_diffuse = self._matrix_vector_mult(self.L_norm, self.phi_L)
        phi_L_diffuse = [self.D['L'] * p for p in phi_L_diffuse]
        
        phi_S_diffuse = self._matrix_vector_mult(self.L_norm, self.phi_S)
        phi_S_diffuse = [self.D['S'] * p for p in phi_S_diffuse]
        
        # Decay
        phi_E_decay = self._decay_exp(self.phi_E, self.lambda_decay['E'])
        phi_L_decay = self._decay_exp(self.phi_L, self.lambda_decay['L'])
        phi_S_decay = self._decay_exp(self.phi_S, self.lambda_decay['S'])
        
        # Cross-coupling: L += kappa_LE * E, S -= kappa_SE * E
        E_avg = sum(self.phi_E) / len(self.phi_E) if self.phi_E else 0.0
        phi_L_coupling = [self.kappa_LE * E_avg] * self.num_nodes
        phi_S_coupling = [-self.kappa_SE * E_avg] * self.num_nodes
        
        # Update: phi(t+1) = (1-beta)*phi(t) + inject + diffuse + decay + coupling
        persistence_E = [(1 - self.beta) * p for p in self.phi_E]
        persistence_L = [(1 - self.beta) * p for p in self.phi_L]
        persistence_S = [(1 - self.beta) * p for p in self.phi_S]
        
        self.phi_E = [
            max(0.0, min(1.0, 
            persistence_E[i] + phi_E_inject[i] + phi_E_diffuse[i] + phi_E_decay[i]))
            for i in range(self.num_nodes)
        ]
        
        self.phi_L = [
            max(0.0, min(1.0,
            persistence_L[i] + phi_L_inject[i] + phi_L_diffuse[i] + phi_L_decay[i] + phi_L_coupling[i]))
            for i in range(self.num_nodes)
        ]
        
        self.phi_S = [
            max(0.0, min(1.0,
            persistence_S[i] + phi_S_inject[i] + phi_S_diffuse[i] + phi_S_decay[i] + phi_S_coupling[i]))
            for i in range(self.num_nodes)
        ]


# ============================================================================
# AGENT TRIGGER DETECTION
# ============================================================================

class ThresholdDetector:
    """Detect agent trigger conditions"""
    
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.hot_history = deque(maxlen=window_size)
        self.very_hot_history = deque(maxlen=window_size)
    
    def detect_hot(self, phi: List[float], theta: float, consecutive: int = 3) -> bool:
        """Detect hot state: > threshold for N consecutive ticks"""
        avg_phi = sum(phi) / len(phi) if phi else 0.0
        is_hot = avg_phi > theta
        self.hot_history.append(is_hot)
        
        if len(self.hot_history) < consecutive:
            return False
        
        recent = list(self.hot_history)[-consecutive:]
        return all(recent)
    
    def detect_very_hot(self, phi: List[float], theta: float, consecutive: int = 2) -> bool:
        """Detect very hot state"""
        avg_phi = sum(phi) / len(phi) if phi else 0.0
        is_very_hot = avg_phi > theta
        self.very_hot_history.append(is_very_hot)
        
        if len(self.very_hot_history) < consecutive:
            return False
        
        recent = list(self.very_hot_history)[-consecutive:]
        return all(recent)


# ============================================================================
# OPERATIONAL AGENTS
# ============================================================================

class WeaverAgent:
    """Traffic engineering - reroute to lower latency paths"""
    
    def __init__(self, cooldown_ticks: int = 10):
        self.cooldown_ticks = cooldown_ticks
        self.cooldown_remaining = 0
        self.last_action_time = None
    
    def check_trigger(self, L_current: float, theta_L_hot: float,
                     S_alt: float, S_current: float, min_delta_S: float = 0.1) -> bool:
        """Check if reroute should be triggered"""
        if self.cooldown_remaining > 0:
            self.cooldown_remaining -= 1
            return False
        
        L_condition = L_current > theta_L_hot
        S_condition = (S_alt - S_current) >= min_delta_S
        
        return L_condition and S_condition
    
    def execute(self, shift_fraction: float = 0.15) -> Dict:
        """Execute load shift"""
        self.cooldown_remaining = self.cooldown_ticks
        self.last_action_time = time.time()
        
        return {
            'agent': 'weaver',
            'action': 'shift_ecmp_weights',
            'shift_fraction': shift_fraction,
            'timestamp': self.last_action_time
        }


class BuilderAgent:
    """Capacity expansion - bring up additional resources"""
    
    def __init__(self, rate_limit: int = 1, window_seconds: int = 60):
        self.rate_limit = rate_limit
        self.window_seconds = window_seconds
        self.expansion_times = deque(maxlen=rate_limit)
        self.cooldown_remaining = 0
    
    def check_trigger(self, E_current: float, theta_E_hot: float,
                     S_current: float, theta_S_high: float,
                     neighbor_quorum: float = 0.6, budget_available: bool = True) -> bool:
        """Check if expansion should be triggered"""
        if self.cooldown_remaining > 0:
            self.cooldown_remaining -= 1
            return False
        
        E_condition = E_current > theta_E_hot
        S_condition = S_current > theta_S_high
        quorum_condition = neighbor_quorum >= 0.6
        
        return E_condition and S_condition and quorum_condition and budget_available
    
    def execute(self, capacity_increment: int = 2) -> Dict:
        """Execute capacity expansion"""
        current_time = time.time()
        self.expansion_times.append(current_time)
        
        # Check if at rate limit
        if len(self.expansion_times) >= self.rate_limit:
            oldest = self.expansion_times[0]
            if current_time - oldest < self.window_seconds:
                self.cooldown_remaining = 30
        
        return {
            'agent': 'builder',
            'action': 'expand_capacity',
            'capacity_increment': capacity_increment,
            'timestamp': current_time
        }


class ScavengerAgent:
    """Link isolation - quarantine failing links"""
    
    class CircuitBreakerState(Enum):
        CLOSED = "closed"
        OPEN = "open"
        HALF_OPEN = "half_open"
    
    def __init__(self, initial_backoff: float = 30.0):
        self.state = self.CircuitBreakerState.CLOSED
        self.state_time = time.time()
        self.initial_backoff = initial_backoff
        self.backoff_multiplier = 2.0
        self.max_backoff = 300.0
        self.attempt_count = 0
    
    def check_trigger(self, E_current: float, theta_E_very_hot: float,
                     S_current: float, theta_S_low: float) -> bool:
        """Check if quarantine should be triggered"""
        E_condition = E_current > 2.0 * theta_E_very_hot
        S_condition = S_current < theta_S_low
        
        return E_condition and S_condition
    
    def execute(self) -> Dict:
        """Execute link isolation"""
        if self.state == self.CircuitBreakerState.CLOSED:
            self.state = self.CircuitBreakerState.OPEN
            self.state_time = time.time()
            self.attempt_count = 0
            
            return {
                'agent': 'scavenger',
                'action': 'quarantine_link',
                'state': 'OPEN',
                'timestamp': self.state_time
            }
        
        return {'agent': 'scavenger', 'action': 'none'}
    
    def get_backoff_time(self) -> float:
        """Calculate exponential backoff time"""
        return min(
            self.initial_backoff * (self.backoff_multiplier ** self.attempt_count),
            self.max_backoff
        )


# ============================================================================
# MAIN FRAMEWORK
# ============================================================================

class MorphogeneticFramework:
    """Main orchestration of morphogenetic framework"""
    
    def __init__(self, num_nodes: int, adjacency_matrix: List[List[int]]):
        self.num_nodes = num_nodes
        self.tick = 0
        self.fields = FieldDynamics(num_nodes, adjacency_matrix)
        self.normalizer = SignalNormalizer()
        self.detector = ThresholdDetector()
        self.weaver = WeaverAgent()
        self.builder = BuilderAgent()
        self.scavenger = ScavengerAgent()
        self.audit_log = []
    
    def run_tick(self, E_raw_list: List[float], L_raw_list: List[float],
                S_raw_list: List[float]) -> Dict:
        """Execute one framework tick (1 second)"""
        
        # Normalize signals
        E_normalized = [self.normalizer.normalize_error(e) for e in E_raw_list]
        L_normalized = [self.normalizer.normalize_latency(l, 200.0) for l in L_raw_list]
        S_normalized = [self.normalizer.normalize_capacity(s) for s in S_raw_list]
        
        # Update fields
        source = {'E': E_normalized, 'L': L_normalized, 'S': S_normalized}
        self.fields.update({}, source)
        
        # Detect trigger conditions
        E_avg = sum(self.fields.phi_E) / len(self.fields.phi_E)
        L_avg = sum(self.fields.phi_L) / len(self.fields.phi_L)
        S_avg = sum(self.fields.phi_S) / len(self.fields.phi_S)
        
        E_hot = self.detector.detect_hot(self.fields.phi_E, 0.020, 3)
        L_hot = self.detector.detect_hot(self.fields.phi_L, 0.50, 3)
        E_very_hot = self.detector.detect_very_hot(self.fields.phi_E, 0.050, 2)
        
        # Execute agents
        actions = []
        
        if self.weaver.check_trigger(L_avg, 0.50, S_avg + 0.1, S_avg):
            action = self.weaver.execute()
            actions.append(action)
            self._audit_log(action)
        
        if self.builder.check_trigger(E_avg, 0.020, S_avg, 0.70, 0.6, True):
            action = self.builder.execute()
            actions.append(action)
            self._audit_log(action)
        
        if self.scavenger.check_trigger(E_avg, 0.050, S_avg, 0.20):
            action = self.scavenger.execute()
            actions.append(action)
            self._audit_log(action)
        
        self.tick += 1
        
        return {
            'tick': self.tick,
            'signals': {
                'E': E_avg,
                'L': L_avg,
                'S': S_avg
            },
            'fields': {
                'phi_E': E_avg,
                'phi_L': L_avg,
                'phi_S': S_avg
            },
            'actions': actions
        }
    
    def _audit_log(self, action: Dict) -> None:
        """Log action to audit trail"""
        log_entry = {
            'timestamp': time.time(),
            'tick': self.tick,
            **action
        }
        self.audit_log.append(log_entry)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    # Create simple 5-node ring topology
    adjacency = [
        [0, 1, 0, 0, 1],
        [1, 0, 1, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 1, 0, 1],
        [1, 0, 0, 1, 0]
    ]
    
    framework = MorphogeneticFramework(5, adjacency)
    
    print("MORPHOGENETIC FRAMEWORK - SIMULATION START")
    print("[OUTPUT] Framework initialized with 5 nodes")
    
    # Run 10 ticks
    for i in range(10):
        # Simulate sensor data
        E_raw = [0.002 + (0.001 if j == 2 else 0.0) for j in range(5)]
        L_raw = [150.0 + (50.0 if j == 2 else 0.0) for j in range(5)]
        S_raw = [0.6 + (0.1 if j == 2 else 0.0) for j in range(5)]
        
        result = framework.run_tick(E_raw, L_raw, S_raw)
        
        print("[TICK {}] E={:.3f} L={:.3f} S={:.3f}".format(
            result['tick'],
            result['signals']['E'],
            result['signals']['L'],
            result['signals']['S']
        ))
        
        if result['actions']:
            for action in result['actions']:
                print("[ACTION] {}: {}".format(action['agent'].upper(), action['action']))
        
        time.sleep(0.1)
    
    print("[OUTPUT] Simulation complete")
    print("[OUTPUT] Total actions: {}".format(len(framework.audit_log)))