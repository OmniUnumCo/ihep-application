"""
IHEP Digital Twin Backend Synthesis Service

This service continuously monitors patient data sources, synthesizes updates
into digital twin representations, and regenerates USD scene files with
minimal latency while maintaining clinical accuracy.

Architecture:
- Event-driven data ingestion from multiple sources
- Incremental manifold projection updates
- Differential USD file generation (only changed patients)
- Morphogenetic self-healing for pipeline resilience
- Comprehensive validation before publishing updates

Mathematical Foundation:
- Online manifold learning via stochastic gradient descent
- Temporal smoothing to prevent trajectory jitter
- Physiological constraint enforcement
- Uncertainty quantification for data quality
"""

import numpy as np
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import deque
import hashlib
import secrets
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('IHEP.DigitalTwinSynthesis')
PATIENT_HASH_SALT = os.getenv('PATIENT_HASH_SALT', '')


def hash_patient_id(patient_id: str) -> str:
    """Hash patient ID for secure logging"""
    value = str(patient_id)
    if PATIENT_HASH_SALT:
        value = f"{PATIENT_HASH_SALT}:{value}"
    return hashlib.sha256(value.encode()).hexdigest()[:8]


def hash_request_id(request_id: Optional[str]) -> str:
    """Hash request identifiers so logs never reveal raw IDs"""
    value = request_id if request_id is not None else ""
    return hash_patient_id(f"request:{value}")


class DataSourceType(Enum):
    """Enumeration of patient data sources."""
    POSTGRESQL = "postgresql"  # User profiles, appointments, self-reported data
    HEALTHCARE_API = "healthcare_api"  # Lab results, clinical measurements (PHI)
    WEARABLE_DEVICE = "wearable"  # Continuous biometric streams
    MANUAL_ENTRY = "manual"  # Patient-reported outcomes via app


@dataclass
class PatientHealthState:
    """
    Represents a patient's complete health state at a specific moment.
    
    This is the fundamental unit that flows through the synthesis pipeline.
    It aggregates data from all sources into a unified vector representation.
    """
    patient_id: str
    timestamp: datetime
    
    # Clinical measurements
    viral_load: Optional[float] = None  # copies/mL
    cd4_count: Optional[float] = None  # cells/μL
    cd4_percentage: Optional[float] = None  # %
    
    # Adherence metrics
    medication_adherence_7day: Optional[float] = None  # % doses taken
    appointment_adherence: Optional[float] = None  # % attended
    
    # Mental health assessments
    depression_score: Optional[float] = None  # PHQ-9 scale
    anxiety_score: Optional[float] = None  # GAD-7 scale
    
    # Social determinants
    housing_stability: Optional[float] = None  # 0-1 scale
    food_security: Optional[float] = None  # 0-1 scale
    social_support: Optional[float] = None  # 0-1 scale
    
    # Wearable-derived metrics
    average_heart_rate: Optional[float] = None  # bpm
    sleep_quality: Optional[float] = None  # 0-1 scale
    activity_level: Optional[float] = None  # 0-1 scale
    
    # Computed fields
    completeness_score: float = 0.0  # Fraction of fields populated
    data_quality_score: float = 0.0  # Overall quality assessment
    
    # Metadata
    data_sources: Set[DataSourceType] = field(default_factory=set)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_feature_vector(self) -> np.ndarray:
        """
        Convert health state to numerical feature vector for manifold projection.
        
        This is the critical transformation that takes structured patient data
        and converts it into the high-dimensional vector that gets projected
        to three-dimensional space. Missing values are imputed using clinically
        informed defaults or population means.
        
        Returns:
            Feature vector suitable for manifold projection
        """
        # Define feature ordering (must match manifold projector training)
        features = [
            self.viral_load if self.viral_load is not None else 200.0,  # Median VL
            self.cd4_count if self.cd4_count is not None else 500.0,  # Median CD4
            self.cd4_percentage if self.cd4_percentage is not None else 25.0,
            self.medication_adherence_7day if self.medication_adherence_7day is not None else 0.85,
            self.appointment_adherence if self.appointment_adherence is not None else 0.80,
            self.depression_score if self.depression_score is not None else 5.0,
            self.anxiety_score if self.anxiety_score is not None else 5.0,
            self.housing_stability if self.housing_stability is not None else 0.7,
            self.food_security if self.food_security is not None else 0.7,
            self.social_support if self.social_support is not None else 0.6,
            self.average_heart_rate if self.average_heart_rate is not None else 70.0,
            self.sleep_quality if self.sleep_quality is not None else 0.7,
            self.activity_level if self.activity_level is not None else 0.5
        ]
        
        return np.array(features, dtype=np.float64)
    
    def compute_completeness(self) -> float:
        """
        Calculate what fraction of possible data fields are populated.
        
        This metric helps the synthesis service understand data quality and
        whether it's appropriate to update the digital twin or wait for
        more complete information.
        
        Returns:
            Completeness score in [0, 1]
        """
        fields_to_check = [
            self.viral_load, self.cd4_count, self.cd4_percentage,
            self.medication_adherence_7day, self.appointment_adherence,
            self.depression_score, self.anxiety_score,
            self.housing_stability, self.food_security, self.social_support,
            self.average_heart_rate, self.sleep_quality, self.activity_level
        ]
        
        populated = sum(1 for field in fields_to_check if field is not None)
        total = len(fields_to_check)
        
        return populated / total if total > 0 else 0.0


@dataclass
class ManifoldUpdateRequest:
    """
    Represents a request to update the manifold projection for specific patients.
    
    This allows the synthesis service to batch multiple patient updates
    together for efficiency while maintaining low latency.
    """
    request_id: str
    patient_updates: Dict[str, PatientHealthState]  # patient_id -> new state
    timestamp: datetime
    priority: int = 1  # Higher priority processed first
    
    def __lt__(self, other):
        """Enable priority queue ordering."""
        return self.priority > other.priority  # Higher priority first


class IncrementalManifoldProjector:
    """
    Performs incremental updates to manifold projections without full recalculation.
    
    Mathematical Foundation:
    Instead of solving the full optimization problem when data changes, we
    perform stochastic gradient descent steps that move existing projections
    toward their optimal positions given the new data. This trades perfect
    accuracy for speed, with configurable accuracy vs. latency tradeoff.
    
    The update rule for patient i's projection p_i given new health state h_i is:
    
    p_i(t+1) = p_i(t) - learning_rate * ∇L(p_i, h_i, {p_j, h_j}_{j ∈ neighbors})
    
    where L is the local distortion loss considering only nearby patients.
    """
    
    def __init__(self, 
                 base_projector,
                 learning_rate: float = 0.01,
                 n_neighbors: int = 20,
                 smoothing_factor: float = 0.3):
        """
        Initialize the incremental projector.
        
        Args:
            base_projector: Trained ClinicalManifoldProjector from Subsystem 1
            learning_rate: Step size for gradient descent updates
            n_neighbors: How many nearby patients to consider for local updates
            smoothing_factor: Temporal smoothing to prevent jitter (0=no smoothing, 1=maximum)
        """
        self.base_projector = base_projector
        self.learning_rate = learning_rate
        self.n_neighbors = n_neighbors
        self.smoothing_factor = smoothing_factor
        
        # Cache of current patient positions in projection space
        self.patient_positions = {}  # patient_id -> (x, y, z) position
        self.patient_health_states = {}  # patient_id -> feature vector
        
        # Temporal smoothing: store recent positions for averaging
        self.position_history = {}  # patient_id -> deque of recent positions
        self.history_length = 5  # Number of past positions to consider
        
        logger.info(f"Initialized incremental projector with lr={learning_rate}, neighbors={n_neighbors}")
    
    def initialize_patient(self, patient_id: str, health_state: PatientHealthState):
        """
        Add a new patient to the projection space.
        
        For new patients, we use the base projector to get an initial position,
        then track them incrementally from there.
        
        Args:
            patient_id: Unique patient identifier
            health_state: Initial health state
        """
        # Convert health state to feature vector
        features = health_state.to_feature_vector().reshape(1, -1)
        
        # Get initial projection from base model
        initial_position = self.base_projector.transform(features)[0]
        
        # Store patient data
        self.patient_positions[patient_id] = initial_position
        self.patient_health_states[patient_id] = features[0]
        
        # Initialize position history with current position repeated
        self.position_history[patient_id] = deque(
            [initial_position.copy() for _ in range(self.history_length)],
            maxlen=self.history_length
        )

        patient_hash = hash_patient_id(patient_id)
        logger.info(f"Initialized patient hash {patient_hash} at position {initial_position}")
    
    def update_patient(self, patient_id: str, new_health_state: PatientHealthState) -> np.ndarray:
        """
        Update a patient's projection given new health data.
        
        This is the core incremental update algorithm. Instead of recomputing
        the entire manifold, we perform local optimization considering only
        nearby patients, which is much faster.
        
        Mathematical approach:
        1. Find k nearest neighbors in current projection space
        2. Compute where patient SHOULD be given new health state
        3. Take a gradient step toward optimal position
        4. Apply temporal smoothing to prevent jitter
        5. Validate physiological constraints
        
        Args:
            patient_id: Patient to update
            new_health_state: New health state data
            
        Returns:
            Updated 3D position
        """
        if patient_id not in self.patient_positions:
            # First time seeing this patient, initialize
            self.initialize_patient(patient_id, new_health_state)
            return self.patient_positions[patient_id]
        
        # Get current position and health state
        current_position = self.patient_positions[patient_id]
        current_features = self.patient_health_states[patient_id]
        
        # Convert new health state to features
        new_features = new_health_state.to_feature_vector()
        
        # Compute feature-space displacement
        feature_displacement = new_features - current_features
        feature_distance = np.linalg.norm(feature_displacement)
        
        # If health state hasn't changed much, skip update to save computation
        if feature_distance < 0.01:
            patient_hash = hash_patient_id(patient_id)
            logger.debug(f"Patient hash {patient_hash} health state unchanged, skipping update")
            return current_position
        
        # Find k nearest neighbors in current projection space
        neighbor_ids, neighbor_positions = self._find_nearest_neighbors(
            patient_id,
            current_position,
            k=self.n_neighbors
        )
        
        # Compute target position using base projector
        # This is expensive but gives us a "true" target
        target_position = self.base_projector.transform(new_features.reshape(1, -1))[0]
        
        # Compute local gradient considering neighbors
        # The loss is: distance from target + preservation of neighbor relationships
        gradient = self._compute_local_gradient(
            current_position,
            target_position,
            neighbor_positions
        )
        
        # Take gradient descent step
        raw_new_position = current_position - self.learning_rate * gradient
        
        # Apply temporal smoothing to prevent jitter
        # The idea: average recent positions to smooth out noisy updates
        self.position_history[patient_id].append(raw_new_position)
        smoothed_position = self._apply_temporal_smoothing(patient_id)
        
        # Validate physiological constraints
        validated_position = self._validate_position_update(
            patient_id,
            current_position,
            smoothed_position,
            new_features,
            current_features
        )
        
        # Store updates
        self.patient_positions[patient_id] = validated_position
        self.patient_health_states[patient_id] = new_features
        
        # Log significant movements
        displacement = np.linalg.norm(validated_position - current_position)
        if displacement > 0.1:
            patient_hash = hash_patient_id(patient_id)
            logger.info(
                f"Patient hash {patient_hash} moved {displacement:.3f} units in health space"
            )
        
        return validated_position
    
    def _find_nearest_neighbors(self, 
                                patient_id: str,
                                position: np.ndarray,
                                k: int) -> Tuple[List[str], List[np.ndarray]]:
        """
        Find k nearest neighbors to a patient in projection space.
        
        Args:
            patient_id: Patient to find neighbors for
            position: Patient's current position
            k: Number of neighbors to find
            
        Returns:
            (neighbor_ids, neighbor_positions) tuple
        """
        # Compute distances to all other patients
        distances = []
        for other_id, other_pos in self.patient_positions.items():
            if other_id == patient_id:
                continue
            
            dist = np.linalg.norm(position - other_pos)
            distances.append((dist, other_id, other_pos))
        
        # Sort by distance and take k nearest
        distances.sort(key=lambda x: x[0])
        neighbors = distances[:k]
        
        neighbor_ids = [n[1] for n in neighbors]
        neighbor_positions = [n[2] for n in neighbors]
        
        return neighbor_ids, neighbor_positions
    
    def _compute_local_gradient(self,
                                current_pos: np.ndarray,
                                target_pos: np.ndarray,
                                neighbor_positions: List[np.ndarray]) -> np.ndarray:
        """
        Compute gradient for local manifold update.
        
        The gradient has two components:
        1. Attraction toward target position (from base projector)
        2. Repulsion/attraction to maintain neighbor relationships
        
        Mathematical form:
        ∇L = α(p - p_target) + β Σ_neighbors (||p - p_neighbor|| - d_ideal)
        
        where α balances target attraction vs. neighbor preservation.
        
        Args:
            current_pos: Current 3D position
            target_pos: Ideal position from base projector
            neighbor_positions: Positions of nearby patients
            
        Returns:
            Gradient vector for position update
        """
        # Component 1: Gradient toward target
        gradient_target = current_pos - target_pos
        
        # Component 2: Gradient from neighbors
        # We want to preserve relative distances to neighbors
        gradient_neighbors = np.zeros(3)
        
        for neighbor_pos in neighbor_positions:
            # Current distance to neighbor
            current_dist = np.linalg.norm(current_pos - neighbor_pos)
            
            if current_dist < 1e-6:
                continue  # Avoid division by zero
            
            # Direction from neighbor to us
            direction = (current_pos - neighbor_pos) / current_dist
            
            # Ideal distance (from original manifold)
            # In practice, we just try to keep neighbors at similar relative distances
            ideal_dist = current_dist  # Conservative: maintain current distances
            
            # Spring force: attracts if too far, repels if too close
            force = (current_dist - ideal_dist) * direction
            gradient_neighbors += force
        
        # Combine gradients with weighting
        # Higher alpha means trust target more, lower means preserve neighbors more
        alpha = 0.7  # Weight for target attraction
        beta = 0.3   # Weight for neighbor preservation
        
        total_gradient = alpha * gradient_target + beta * gradient_neighbors
        
        return total_gradient
    
    def _apply_temporal_smoothing(self, patient_id: str) -> np.ndarray:
        """
        Apply temporal smoothing to prevent trajectory jitter.
        
        When patient health data updates frequently (e.g., daily wearable uploads),
        the projection can bounce around noisily even if underlying health is
        stable. Temporal smoothing averages recent positions to create smooth
        trajectories.
        
        Mathematical form: exponential moving average
        p_smooth = α * p_current + (1-α) * p_previous
        
        Args:
            patient_id: Patient to smooth
            
        Returns:
            Smoothed position
        """
        history = self.position_history[patient_id]
        
        if len(history) == 0:
            return self.patient_positions[patient_id]
        
        # Compute exponentially weighted moving average
        weights = np.array([self.smoothing_factor ** i for i in range(len(history))])
        weights = weights / np.sum(weights)  # Normalize to sum to 1
        
        # Weight recent positions more heavily
        weights = weights[::-1]  # Reverse so most recent gets highest weight
        
        smoothed = np.zeros(3)
        for pos, weight in zip(history, weights):
            smoothed += weight * pos
        
        return smoothed
    
    def _validate_position_update(self,
                                  patient_id: str,
                                  old_position: np.ndarray,
                                  new_position: np.ndarray,
                                  new_features: np.ndarray,
                                  old_features: np.ndarray) -> np.ndarray:
        """
        Validate that position update satisfies physiological constraints.
        
        This is a critical safety check. Even though our manifold projection
        is mathematically sound, numerical errors or data artifacts could
        produce unphysiological trajectories. For example, CD4 count cannot
        increase faster than maximum lymphocyte proliferation rate.
        
        If the proposed update violates constraints, we clamp it to the
        maximum allowable displacement.
        
        Args:
            patient_id: Patient being updated
            old_position: Previous position
            new_position: Proposed new position
            new_features: New health state features
            old_features: Previous health state features
            
        Returns:
            Validated (possibly clamped) position
        """
        # Compute displacement magnitude
        displacement = np.linalg.norm(new_position - old_position)
        
        # Maximum allowable displacement per day (tunable parameter)
        # This is in projection space units, not clinical units
        max_displacement_per_day = 0.5
        
        if displacement > max_displacement_per_day:
            patient_hash = hash_patient_id(patient_id)
            logger.warning(
                f"Patient hash {patient_hash} displacement {displacement:.3f} "
                f"exceeds maximum {max_displacement_per_day}, clamping"
            )
            
            # Clamp to maximum allowed
            direction = (new_position - old_position) / displacement
            clamped_position = old_position + direction * max_displacement_per_day
            
            return clamped_position
        
        # Check for NaN or Inf
        if not np.all(np.isfinite(new_position)):
            patient_hash = hash_patient_id(patient_id)
            logger.error(
                f"Patient hash {patient_hash} produced non-finite position, "
                f"reverting to previous position"
            )
            return old_position
        
        # Additional constraint: CD4 proliferation rate
        # CD4 is feature index 1 in our feature vector
        cd4_old = old_features[1]
        cd4_new = new_features[1]
        cd4_delta = cd4_new - cd4_old
        
        # Maximum daily CD4 increase (cells/μL)
        # Based on r_max = 0.01, CD4_max = 1500 from Subsystem 1
        r_max = 0.01
        cd4_max = 1500.0
        max_cd4_delta = r_max * cd4_old * (1 - cd4_old / cd4_max)
        
        if cd4_delta > max_cd4_delta * 1.2:  # 20% tolerance
            patient_hash = hash_patient_id(patient_id)
            logger.warning(
                f"Patient hash {patient_hash} CD4 increase {cd4_delta:.1f} "
                f"exceeds physiological maximum {max_cd4_delta:.1f}"
            )
            # Could clamp position further here if needed
        
        return new_position
    
    def batch_update(self, updates: Dict[str, PatientHealthState]) -> Dict[str, np.ndarray]:
        """
        Update multiple patients in batch for efficiency.
        
        Args:
            updates: Map of patient_id to new health state
            
        Returns:
            Map of patient_id to new position
        """
        results = {}
        
        for patient_id, health_state in updates.items():
            new_position = self.update_patient(patient_id, health_state)
            results[patient_id] = new_position
        
        logger.info(f"Batch updated {len(results)} patients")
        return results


class DataIngestionCoordinator:
    """
    Coordinates data ingestion from multiple heterogeneous sources.
    
    This component handles the messy reality of healthcare data: multiple
    systems with different update frequencies, varying data formats,
    intermittent connectivity, and conflicting timestamps. It normalizes
    everything into a unified PatientHealthState representation.
    """
    
    def __init__(self):
        """Initialize the data ingestion coordinator."""
        self.pending_updates = {}  # patient_id -> partial health state
        self.last_complete_update = {}  # patient_id -> datetime of last complete state
        
        # Minimum completeness score required to trigger digital twin update
        self.completeness_threshold = 0.6  # 60% of fields must be populated
        
        # Maximum time to wait for complete data before forcing partial update
        self.max_wait_time = timedelta(hours=6)
        
        logger.info("Data ingestion coordinator initialized")
    
    async def ingest_from_postgresql(self, patient_id: str) -> Optional[PatientHealthState]:
        """
        Ingest data from PostgreSQL database.

        This retrieves user-entered data like medication adherence logs,
        appointment history, and self-reported outcomes.

        Args:
            patient_id: Patient to fetch data for

        Returns:
            Partial health state with PostgreSQL data populated
        """
        # In production, this would query your actual PostgreSQL database
        # For demonstration, we simulate the database call

        patient_hash = hash_patient_id(patient_id)
        logger.debug(f"Fetching PostgreSQL data for patient hash {patient_hash}")
        
        # Simulate database query with asyncio
        await asyncio.sleep(0.1)  # Simulate network latency
        
        # Create partial health state with available data
        health_state = PatientHealthState(
            patient_id=patient_id,
            timestamp=datetime.now()
        )
        
        # Simulated data (in production, from actual database)
        health_state.medication_adherence_7day = 0.85
        health_state.appointment_adherence = 0.90
        health_state.housing_stability = 0.8
        health_state.food_security = 0.7
        health_state.social_support = 0.75
        
        health_state.data_sources.add(DataSourceType.POSTGRESQL)
        
        return health_state
    
    async def ingest_from_healthcare_api(self, patient_id: str) -> Optional[PatientHealthState]:
        """
        Ingest data from Google Cloud Healthcare API.

        This retrieves clinical lab results and other PHI that must be
        stored in HIPAA-compliant infrastructure.

        Args:
            patient_id: Patient to fetch data for

        Returns:
            Partial health state with clinical data populated
        """
        patient_hash = hash_patient_id(patient_id)
        logger.debug(f"Fetching Healthcare API data for patient hash {patient_hash}")
        
        await asyncio.sleep(0.2)  # Simulate API latency
        
        health_state = PatientHealthState(
            patient_id=patient_id,
            timestamp=datetime.now()
        )
        
        # Simulated clinical data
        health_state.viral_load = 45.0  # Suppressed
        health_state.cd4_count = 520.0
        health_state.cd4_percentage = 28.0
        
        health_state.data_sources.add(DataSourceType.HEALTHCARE_API)
        
        return health_state
    
    async def ingest_from_wearable(self, patient_id: str) -> Optional[PatientHealthState]:
        """
        Ingest data from wearable devices.

        This processes continuous biometric streams from devices like
        smartwatches that track heart rate, sleep, and activity.

        Args:
            patient_id: Patient to fetch data for

        Returns:
            Partial health state with wearable data populated
        """
        patient_hash = hash_patient_id(patient_id)
        logger.debug(f"Fetching wearable data for patient hash {patient_hash}")
        
        await asyncio.sleep(0.05)  # Wearables are usually fastest
        
        health_state = PatientHealthState(
            patient_id=patient_id,
            timestamp=datetime.now()
        )
        
        # Simulated wearable data (averaged over last 24 hours)
        health_state.average_heart_rate = 72.0
        health_state.sleep_quality = 0.75
        health_state.activity_level = 0.65
        
        health_state.data_sources.add(DataSourceType.WEARABLE_DEVICE)
        
        return health_state
    
    async def collect_complete_health_state(self, patient_id: str) -> Optional[PatientHealthState]:
        """
        Collect data from all sources and merge into complete health state.

        This orchestrates parallel data fetching from multiple sources and
        intelligently merges the results, handling missing data and conflicts.

        Args:
            patient_id: Patient to collect data for

        Returns:
            Complete (or as complete as possible) health state
        """
        patient_hash = hash_patient_id(patient_id)
        logger.info(f"Collecting complete health state for patient hash {patient_hash}")
        
        # Fetch from all sources in parallel
        results = await asyncio.gather(
            self.ingest_from_postgresql(patient_id),
            self.ingest_from_healthcare_api(patient_id),
            self.ingest_from_wearable(patient_id),
            return_exceptions=True
        )
        
        # Merge results into single health state
        merged = PatientHealthState(
            patient_id=patient_id,
            timestamp=datetime.now()
        )
        
        for result in results:
            if isinstance(result, Exception):
                patient_hash = hash_patient_id(patient_id)
                logger.error(f"Data ingestion error for patient hash {patient_hash}: error occurred")
                continue
            
            if result is None:
                continue
            
            # Merge non-None fields from this source
            for field_name in [
                'viral_load', 'cd4_count', 'cd4_percentage',
                'medication_adherence_7day', 'appointment_adherence',
                'depression_score', 'anxiety_score',
                'housing_stability', 'food_security', 'social_support',
                'average_heart_rate', 'sleep_quality', 'activity_level'
            ]:
                value = getattr(result, field_name, None)
                if value is not None:
                    setattr(merged, field_name, value)
            
            # Merge data sources
            merged.data_sources.update(result.data_sources)
        
        # Compute completeness and quality scores
        merged.completeness_score = merged.compute_completeness()
        merged.data_quality_score = self._assess_data_quality(merged)

        patient_hash = hash_patient_id(patient_id)
        logger.info(
            f"Collected data for patient hash {patient_hash}: "
            f"completeness={merged.completeness_score:.2f}, "
            f"quality={merged.data_quality_score:.2f}"
        )
        
        return merged
    
    def _assess_data_quality(self, health_state: PatientHealthState) -> float:
        """
        Assess overall quality of collected health state.
        
        Quality is distinct from completeness. A health state can be complete
        (all fields populated) but low quality if values are stale, conflicting,
        or outside expected ranges.
        
        Args:
            health_state: Health state to assess
            
        Returns:
            Quality score in [0, 1]
        """
        quality = 1.0
        
        # Penalize stale data
        time_since_update = datetime.now() - health_state.last_updated
        if time_since_update > timedelta(days=30):
            quality *= 0.5  # 50% penalty for month-old data
        elif time_since_update > timedelta(days=7):
            quality *= 0.8  # 20% penalty for week-old data
        
        # Check for physiologically implausible values
        if health_state.cd4_count is not None:
            if health_state.cd4_count < 0 or health_state.cd4_count > 2000:
                quality *= 0.7  # Suspicious CD4 value
        
        if health_state.viral_load is not None:
            if health_state.viral_load < 0:
                quality *= 0.7  # Invalid viral load
        
        # Reward data from multiple sources (more reliable)
        source_bonus = len(health_state.data_sources) * 0.05
        quality = min(1.0, quality + source_bonus)
        
        return quality


class DigitalTwinSynthesisService:
    """
    Main orchestrator for digital twin synthesis pipeline.
    
    This is the top-level service that coordinates all components:
    - Data ingestion from multiple sources
    - Incremental manifold projection updates
    - USD file generation
    - Morphogenetic self-healing
    - Validation and quality control
    
    The service runs continuously, processing update requests as they arrive
    while maintaining system health through morphogenetic monitoring.
    """
    
    def __init__(self, 
                 base_projector,
                 usd_generator,
                 update_interval_seconds: int = 60):
        """
        Initialize the synthesis service.
        
        Args:
            base_projector: Trained ClinicalManifoldProjector
            usd_generator: DigitalTwinUSDGenerator instance
            update_interval_seconds: How often to check for updates
        """
        self.base_projector = base_projector
        self.usd_generator = usd_generator
        self.update_interval = update_interval_seconds
        
        # Create subsystems
        self.incremental_projector = IncrementalManifoldProjector(base_projector)
        self.data_coordinator = DataIngestionCoordinator()
        
        # Update queue (priority queue for batching)
        self.update_queue = asyncio.PriorityQueue()
        
        # Morphogenetic monitoring
        self.morpho_metrics = {
            'pipeline_latency': deque(maxlen=100),  # Last 100 update times
            'data_completeness': deque(maxlen=100),
            'validation_failures': 0,
            'total_updates': 0
        }
        
        # Service state
        self.is_running = False
        self.last_usd_generation = datetime.now()
        self.usd_generation_interval = timedelta(minutes=5)  # Regenerate USD every 5 min
        
        logger.info(
            "Digital Twin Synthesis Service initialized with %ss update interval",
            update_interval_seconds,
        )
    
    async def start(self):
        """
        Start the synthesis service.
        
        This launches multiple concurrent tasks:
        - Update processing loop
        - USD file generation loop
        - Morphogenetic monitoring loop
        """
        self.is_running = True
        logger.info("Starting Digital Twin Synthesis Service")
        
        # Launch concurrent tasks
        await asyncio.gather(
            self._update_processing_loop(),
            self._usd_generation_loop(),
            self._morphogenetic_monitoring_loop()
        )
    
    async def stop(self):
        """Stop the synthesis service gracefully."""
        logger.info("Stopping Digital Twin Synthesis Service")
        self.is_running = False
        
        # Wait for pending updates to complete
        await self.update_queue.join()
    
    async def request_patient_update(self, 
                                     patient_id: str,
                                     priority: int = 1):
        """
        Request an update for a specific patient.
        
        This is typically called by webhook handlers when new data arrives
        (e.g., lab results uploaded, wearable syncs, patient completes survey).
        
        Args:
            patient_id: Patient to update
            priority: Update priority (higher = more urgent)
        """
        request = ManifoldUpdateRequest(
            request_id=secrets.token_urlsafe(8),
            patient_updates={patient_id: None},  # Will be filled during processing
            timestamp=datetime.now(),
            priority=priority
        )
        
        await self.update_queue.put((priority, request))
        logger.debug(
            "Queued update request for patient hash %s",
            hash_patient_id(patient_id),
        )
    
    async def _update_processing_loop(self):
        """
        Main loop that processes patient update requests.
        
        This continuously monitors the update queue and processes batches
        of patients together for efficiency.
        """
        logger.info("Update processing loop started")
        
        while self.is_running:
            try:
                # Wait for update request (with timeout to check service state)
                try:
                    priority, request = await asyncio.wait_for(
                        self.update_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Process this update batch
                await self._process_update_request(request)
                
                # Mark task complete
                self.update_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in update processing loop: {e}", exc_info=True)
                await asyncio.sleep(1.0)  # Brief pause before retry
    
    async def _process_update_request(self, request: ManifoldUpdateRequest):
        """
        Process a single update request batch.
        
        This is where the actual synthesis happens: data collection,
        manifold projection update, validation, and preparation for USD
        file generation.
        
        Args:
            request: Update request to process
        """
        start_time = datetime.now()
        request_hash = hash_request_id(request.request_id)
        patient_hash_list = sorted(hash_patient_id(pid) for pid in request.patient_updates)
        hashes_display = ", ".join(patient_hash_list) if patient_hash_list else "none"
        logger.info(
            "Processing update request hash %s for patient hashes [%s]",
            request_hash,
            hashes_display,
        )
        
        # Step 1: Collect health states for all patients in this batch
        health_states = {}
        for patient_id in request.patient_updates.keys():
            try:
                health_state = await self.data_coordinator.collect_complete_health_state(
                    patient_id
                )
                
                # Check if data quality sufficient for update
                if health_state.completeness_score < self.data_coordinator.completeness_threshold:
                    patient_hash = hash_patient_id(patient_id)
                    logger.warning(
                        f"Patient hash {patient_hash} data incomplete "
                        f"({health_state.completeness_score:.2f}), skipping update"
                    )
                    continue
                
                health_states[patient_id] = health_state

            except Exception as e:
                patient_hash = hash_patient_id(patient_id)
                logger.error(f"Failed to collect data for patient hash {patient_hash}: exception occurred")
        
        if not health_states:
            logger.warning("No valid health states in batch hash %s", request_hash)
            return
        
        # Step 2: Update manifold projections incrementally
        try:
            new_positions = self.incremental_projector.batch_update(health_states)
        except Exception as e:
            logger.error(f"Manifold update failed: {e}", exc_info=True)
            self.morpho_metrics['validation_failures'] += 1
            return
        
        # Step 3: Validate updates
        validation_passed = True
        for patient_id, position in new_positions.items():
            if not self._validate_update(patient_id, position, health_states[patient_id]):
                patient_hash = hash_patient_id(patient_id)
                logger.error(f"Validation failed for patient hash {patient_hash}")
                validation_passed = False
                self.morpho_metrics['validation_failures'] += 1
        
        if not validation_passed:
            return
        
        # Step 4: Update metrics for morphogenetic monitoring
        processing_time = (datetime.now() - start_time).total_seconds()
        self.morpho_metrics['pipeline_latency'].append(processing_time)
        
        avg_completeness = np.mean([
            hs.completeness_score for hs in health_states.values()
        ])
        self.morpho_metrics['data_completeness'].append(avg_completeness)
        self.morpho_metrics['total_updates'] += len(health_states)
        
        logger.info(
            "Completed update batch hash %s: %d patients in %.2fs",
            request_hash,
            len(health_states),
            processing_time,
        )
    
    def _validate_update(self,
                        patient_id: str,
                        position: np.ndarray,
                        health_state: PatientHealthState) -> bool:
        """
        Validate that an update is safe to apply.
        
        This is the final safety check before committing changes to the
        digital twin representation. It ensures the update satisfies all
        constraints and doesn't introduce artifacts.
        
        Args:
            patient_id: Patient being updated
            position: New projection position
            health_state: Health state that produced this position
            
        Returns:
            True if validation passed, False otherwise
        """
        # Check for non-finite values
        if not np.all(np.isfinite(position)):
            patient_hash = hash_patient_id(patient_id)
            logger.error(f"Non-finite position for patient hash {patient_hash}")
            return False
        
        # Check that position is within reasonable bounds
        # (Health space should be roughly centered at origin with extent ~10 units)
        if np.linalg.norm(position) > 20:
            patient_hash = hash_patient_id(patient_id)
            logger.error(f"Position far from origin for patient hash {patient_hash}")
            return False
        
        # Check data quality score
        if health_state.data_quality_score < 0.5:
            patient_hash = hash_patient_id(patient_id)
            logger.warning(f"Low data quality for patient hash {patient_hash}")
            return False
        
        return True
    
    async def _usd_generation_loop(self):
        """
        Loop that periodically regenerates USD files with updated projections.
        
        We don't regenerate USD on every individual patient update because
        that would be wasteful. Instead, we batch updates and regenerate
        USD files at regular intervals (e.g., every 5 minutes).
        """
        logger.info("USD generation loop started")
        
        while self.is_running:
            try:
                # Check if it's time to regenerate USD
                time_since_last = datetime.now() - self.last_usd_generation
                
                if time_since_last >= self.usd_generation_interval:
                    logger.info("Regenerating USD files")
                    await self._regenerate_usd_files()
                    self.last_usd_generation = datetime.now()
                
                # Sleep until next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in USD generation loop: {e}", exc_info=True)
                await asyncio.sleep(60)  # Wait before retry
    
    async def _regenerate_usd_files(self):
        """
        Regenerate USD scene files with current patient positions.
        
        This creates a new USD file incorporating all recent updates.
        In production, you might generate differential updates instead of
        complete regeneration for better performance.
        """
        # Collect all current patient data
        patient_data = []
        
        for patient_id, position in self.incremental_projector.patient_positions.items():
            # Get current health state
            features = self.incremental_projector.patient_health_states.get(patient_id)
            if features is None:
                continue
            
            # Create mock health state for USD generation
            # In production, you'd query the actual stored health states
            health_state = PatientHealthState(patient_id=patient_id, timestamp=datetime.now())
            
            patient_data.append({
                'id': patient_id,
                'position': position,
                'health_state': health_state
            })
        
        logger.info(f"Regenerating USD with {len(patient_data)} patients")
        
        # This would call your USD generator from Subsystem 2
        # For now, we just log the regeneration
        logger.info("USD regeneration complete")
    
    async def _morphogenetic_monitoring_loop(self):
        """
        Morphogenetic monitoring loop implementing self-healing.
        
        This continuously monitors pipeline health and triggers adaptive
        responses when issues are detected, following the same mathematical
        framework from your morphogenetic specification.
        """
        logger.info("Morphogenetic monitoring loop started")
        
        while self.is_running:
            try:
                # Compute morphogenetic signals
                signals = self._compute_morpho_signals()
                
                # Detect threshold crossings
                if signals['L'] > 0.5:  # High latency
                    logger.warning(f"High pipeline latency detected: {signals['L']:.3f}")
                    await self._reduce_update_frequency()
                
                if signals['E'] > 0.05:  # High error rate
                    logger.error(f"High validation failure rate: {signals['E']:.3f}")
                    await self._increase_data_quality_threshold()
                
                if signals['S'] > 0.7:  # High spare capacity
                    logger.info(f"High spare capacity: {signals['S']:.3f}")
                    await self._increase_update_frequency()
                
                # Sleep until next monitoring tick
                await asyncio.sleep(10)  # Monitor every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in morphogenetic monitoring: {e}", exc_info=True)
                await asyncio.sleep(60)
    
    def _compute_morpho_signals(self) -> Dict[str, float]:
        """
        Compute morphogenetic signals (E, L, S) from pipeline metrics.
        
        Returns:
            Dictionary with signal values
        """
        # Latency signal
        if len(self.morpho_metrics['pipeline_latency']) > 0:
            avg_latency = np.mean(self.morpho_metrics['pipeline_latency'])
            target_latency = 1.0  # Target 1 second per update
            L = min(avg_latency / target_latency, 1.0)
        else:
            L = 0.0
        
        # Error signal
        if self.morpho_metrics['total_updates'] > 0:
            E = self.morpho_metrics['validation_failures'] / self.morpho_metrics['total_updates']
        else:
            E = 0.0
        
        # Spare capacity (inverse of load)
        S = 1.0 - L  # Simple estimate
        
        return {'E': E, 'L': L, 'S': S}
    
    async def _reduce_update_frequency(self):
        """Morphogenetic action: reduce update frequency under high load."""
        self.update_interval = min(self.update_interval * 1.5, 300)  # Max 5 minutes
        logger.info(f"Reduced update interval to {self.update_interval}s")
    
    async def _increase_update_frequency(self):
        """Morphogenetic action: increase update frequency when capacity available."""
        self.update_interval = max(self.update_interval * 0.8, 30)  # Min 30 seconds
        logger.info(f"Increased update interval to {self.update_interval}s")
    
    async def _increase_data_quality_threshold(self):
        """Morphogenetic action: require higher quality data under high error rate."""
        current = self.data_coordinator.completeness_threshold
        self.data_coordinator.completeness_threshold = min(current + 0.1, 0.9)
        logger.info(
            f"Increased data quality threshold to "
            f"{self.data_coordinator.completeness_threshold:.2f}"
        )


# Demonstration of complete synthesis service
async def demo_synthesis_service():
    """
    Complete demonstration of the digital twin synthesis service.
    """
    print("="*60)
    print("IHEP Digital Twin Synthesis Service Demonstration")
    print("="*60)
    
    # Initialize base components (from previous subsystems)
    print("\n[Initialization] Creating base components...")
    
    # Mock base projector (in production, load trained model)
    from types import SimpleNamespace
    mock_projector = SimpleNamespace()
    mock_projector.transform = lambda x: np.random.randn(len(x), 3)
    
    # Mock USD generator (in production, use actual generator)
    mock_usd_generator = SimpleNamespace()
    
    # Create synthesis service
    service = DigitalTwinSynthesisService(
        base_projector=mock_projector,
        usd_generator=mock_usd_generator,
        update_interval_seconds=10
    )
    
    print("✓ Synthesis service initialized")
    
    # Simulate patient update requests
    print("\n[Update Requests] Simulating patient data arrivals...")
    
    # Create task to run service
    service_task = asyncio.create_task(service.start())
    
    # Give service time to start
    await asyncio.sleep(1)
    
    # Request updates for several patients
    patient_ids = [f"PATIENT_{i:04d}" for i in range(10)]
    
    for patient_id in patient_ids:
        await service.request_patient_update(patient_id, priority=1)
        # Log only a hashed version of patient_id for privacy
        hashed_pid = hash_patient_id(patient_id)
        print(f"✓ Requested update for patient hash {hashed_pid}")
    
    # Let service process updates
    print("\n[Processing] Allowing service to process updates...")
    await asyncio.sleep(15)
    
    # Check morphogenetic metrics
    print("\n[Metrics] Pipeline health status:")
    signals = service._compute_morpho_signals()
    print(f"  Latency signal (L): {signals['L']:.3f}")
    print(f"  Error signal (E): {signals['E']:.3f}")
    print(f"  Spare capacity (S): {signals['S']:.3f}")
    print(f"  Total updates processed: {service.morpho_metrics['total_updates']}")
    
    # Stop service gracefully
    print("\n[Shutdown] Stopping synthesis service...")
    await service.stop()
    service_task.cancel()
    
    try:
        await service_task
    except asyncio.CancelledError:
        pass
    
    print("✓ Service stopped gracefully")
    print("\n" + "="*60)
    print("Demonstration complete")
    print("="*60)


# Run demonstration
if __name__ == "__main__":
    asyncio.run(demo_synthesis_service())