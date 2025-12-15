from pxr import Usd, UsdGeom, Sdf, Gf
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import hashlib

class DigitalTwinUSDGenerator:
    """
    Generates OpenUSD scene descriptions for patient digital twins.
    
    Architecture:
    - Hierarchical scene graph: Stage > Patient Xforms > Geometry
    - Time-sampled attributes for health trajectory animation
    - Composition arcs for separating PHI from geometry
    - Validation layer ensuring physiological coherence
    """
    
    def __init__(self, stage_path: str, manifold_projector):
        """
        Initialize USD generator.
        
        Args:
            stage_path: File path for the root USD stage
            manifold_projector: Fitted ClinicalManifoldProjector instance
        """
        self.stage_path = stage_path
        self.projector = manifold_projector
        self.stage = None
        self.patient_prims = {}  # Maps patient_id to USD prim path
        
    def create_stage(self):
        """
        Create the root USD stage and define coordinate system.
        """
        # Create new stage
        self.stage = Usd.Stage.CreateNew(self.stage_path)
        
        # Define metadata
        self.stage.SetMetadata('comment', 
            'IHEP Digital Twin Ecosystem - Patient Health Trajectories')
        self.stage.SetMetadata('upAxis', UsdGeom.Tokens.z)
        
        # Set time codes for animation (days since program start)
        self.stage.SetStartTimeCode(0)
        self.stage.SetEndTimeCode(365)  # One year of data
        
        # Create root transform for entire patient population
        root_xform = UsdGeom.Xform.Define(self.stage, '/DigitalTwins')
        
        return self.stage
    
    def _hash_patient_id(self, patient_id: str) -> str:
        """
        Create a de-identified hash of patient ID for USD paths.
        
        This ensures USD files contain no PHI while maintaining consistency
        for tracking individual patients across updates.
        """
        hash_object = hashlib.sha256(patient_id.encode())
        return hash_object.hexdigest()[:16]
    
    def add_patient_twin(self, 
                        patient_id: str,
                        health_states: np.ndarray,
                        timestamps: List[datetime],
                        metadata: Dict = None):
        """
        Add a patient's digital twin to the USD stage.
        
        Args:
            patient_id: Original patient identifier (will be hashed)
            health_states: (T, D) array of health vectors at T time points
            timestamps: List of datetime objects for each health state
            metadata: Optional dict of non-PHI attributes (age_group, etc.)
        """
        if self.stage is None:
            raise ValueError("Must call create_stage() first")
        
        # Generate de-identified patient path
        patient_hash = self._hash_patient_id(patient_id)
        patient_path = f'/DigitalTwins/Patient_{patient_hash}'
        
        # Create patient transform node
        patient_xform = UsdGeom.Xform.Define(self.stage, patient_path)
        
        # Add non-PHI metadata as custom attributes
        prim = patient_xform.GetPrim()
        if metadata:
            for key, value in metadata.items():
                attr = prim.CreateAttribute(
                    f'ihep:{key}', 
                    Sdf.ValueTypeNames.String
                )
                attr.Set(str(value))
        
        # Store mapping for later updates
        self.patient_prims[patient_id] = patient_path
        
        # Add trajectory geometry
        self._add_trajectory_curve(
            patient_path, health_states, timestamps
        )
        
        # Add biometric indicator spheres
        self._add_biometric_indicators(
            patient_path, health_states, timestamps
        )
        
        return patient_path
    
    def _add_trajectory_curve(self,
                             patient_path: str,
                             health_states: np.ndarray,
                             timestamps: List[datetime]):
        """
        Create a curve geometry showing patient trajectory through health space.
        
        Mathematical foundation: The curve is a parameterized path through
        3D projection space, where each point corresponds to a health state
        at a specific time.
        """
        # Project health states to 3D
        positions_3d = self.projector.transform(health_states)
        
        # Convert timestamps to time codes (days since first timestamp)
        t0 = timestamps[0]
        time_codes = [(t - t0).days for t in timestamps]
        
        # Create basis curves (spline connecting trajectory points)
        curve_path = f'{patient_path}/Trajectory'
        curve = UsdGeom.BasisCurves.Define(self.stage, curve_path)
        
        # Set curve topology (single curve with N control points)
        N = len(positions_3d)
        curve.CreateCurveVertexCountsAttr([N])
        curve.CreateTypeAttr(UsdGeom.Tokens.cubic)  # Smooth cubic spline
        curve.CreateBasisAttr(UsdGeom.Tokens.bspline)
        
        # Set time-sampled positions
        points_attr = curve.CreatePointsAttr()
        for i, (pos, tc) in enumerate(zip(positions_3d, time_codes)):
            # Convert numpy array to USD vector
            gf_vec = Gf.Vec3f(float(pos[0]), float(pos[1]), float(pos[2]))
            
            # Set position at this time code
            # Store entire trajectory at each time (showing history)
            full_trajectory = [
                Gf.Vec3f(float(p[0]), float(p[1]), float(p[2]))
                for p in positions_3d[:i+1]
            ]
            points_attr.Set(full_trajectory, time=tc)
        
        # Set curve width (thickness of line)
        curve.CreateWidthsAttr([0.02])  # Thin line
        
        # Set color based on viral suppression status
        # (This is where clinical data informs visual encoding)
        color_attr = curve.CreateDisplayColorAttr()
        # Green = suppressed, Red = unsuppressed, gradient between
        # Assuming viral load is feature 0 in health_states
        avg_viral_load = np.mean(health_states[:, 0])
        if avg_viral_load < 50:  # Suppressed threshold
            color = Gf.Vec3f(0.0, 1.0, 0.0)  # Green
        elif avg_viral_load > 1000:  # High viremia
            color = Gf.Vec3f(1.0, 0.0, 0.0)  # Red
        else:  # Intermediate
            color = Gf.Vec3f(1.0, 1.0, 0.0)  # Yellow
        color_attr.Set([color])
        
    def _add_biometric_indicators(self,
                                  patient_path: str,
                                  health_states: np.ndarray,
                                  timestamps: List[datetime]):
        """
        Add sphere geometry that encodes key biometric values.
        
        Visual encoding rules:
        - Sphere size encodes CD4 count (larger = higher count)
        - Sphere color encodes viral load (green = suppressed)
        - Sphere position follows trajectory endpoint
        """
        # Project health states to 3D
        positions_3d = self.projector.transform(health_states)
        
        # Time codes
        t0 = timestamps[0]
        time_codes = [(t - t0).days for t in timestamps]
        
        # Create sphere at trajectory endpoint for each time
        sphere_path = f'{patient_path}/BiometricIndicator'
        sphere = UsdGeom.Sphere.Define(self.stage, sphere_path)
        
        # Time-sampled radius based on CD4 count
        # Assuming CD4 is feature index 1, normalized to [0, 1500] cells/μL
        radius_attr = sphere.CreateRadiusAttr()
        for i, (state, tc) in enumerate(zip(health_states, time_codes)):
            cd4_count = state[1]  # Adjust index based on your feature order
            # Map CD4 [0, 1500] to radius [0.05, 0.20]
            radius = 0.05 + 0.15 * (cd4_count / 1500.0)
            radius_attr.Set(max(0.05, min(0.20, radius)), time=tc)
        
        # Time-sampled position (follows trajectory endpoint)
        translate_op = sphere.AddTranslateOp()
        for i, (pos, tc) in enumerate(zip(positions_3d, time_codes)):
            gf_vec = Gf.Vec3d(float(pos[0]), float(pos[1]), float(pos[2]))
            translate_op.Set(gf_vec, time=tc)
        
        # Time-sampled color based on viral load
        color_attr = sphere.CreateDisplayColorAttr()
        for i, (state, tc) in enumerate(zip(health_states, time_codes)):
            viral_load = state[0]  # Adjust index based on your features
            if viral_load < 50:
                color = Gf.Vec3f(0.0, 1.0, 0.0)  # Suppressed
            elif viral_load > 1000:
                color = Gf.Vec3f(1.0, 0.0, 0.0)  # High viremia
            else:
                # Linear interpolation between yellow and green
                t = (viral_load - 50) / 950.0
                color = Gf.Vec3f(1.0 - 0.5*t, 1.0, 0.0)
            color_attr.Set([color], time=tc)
    
    def add_population_reference_frame(self,
                                       all_positions: np.ndarray,
                                       percentile_markers: List[float] = [25, 50, 75]):
        """
        Add reference geometry showing population distribution.
        
        Creates concentric ellipsoids at specified percentiles to show
        where the population clusters in health space. This provides
        visual context for interpreting individual trajectories.
        
        Args:
            all_positions: (N, 3) array of all patient positions
            percentile_markers: Which percentiles to visualize
        """
        # Compute covariance of population positions
        mean_pos = np.mean(all_positions, axis=0)
        cov_matrix = np.cov(all_positions.T)
        
        # Eigen decomposition gives ellipsoid principal axes
        eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)
        
        for percentile in percentile_markers:
            # Chi-squared statistic for 3D at this percentile
            # determines ellipsoid scale
            from scipy.stats import chi2
            scale = np.sqrt(chi2.ppf(percentile / 100.0, df=3))
            
            # Create ellipsoid mesh
            ellipsoid_path = f'/DigitalTwins/PopulationPercentile_{percentile}'
            sphere = UsdGeom.Sphere.Define(self.stage, ellipsoid_path)
            
            # Set radius to 1.0 (will be scaled by transform)
            sphere.CreateRadiusAttr().Set(1.0)
            
            # Apply transform: translate to mean, rotate by eigenvectors,
            # scale by eigenvalues
            xform = UsdGeom.Xform.Get(self.stage, ellipsoid_path)
            
            # Translation
            translate_op = xform.AddTranslateOp()
            gf_mean = Gf.Vec3d(float(mean_pos[0]), 
                              float(mean_pos[1]), 
                              float(mean_pos[2]))
            translate_op.Set(gf_mean)
            
            # Scale by eigenvalues
            scale_op = xform.AddScaleOp()
            gf_scale = Gf.Vec3f(
                float(scale * np.sqrt(eigenvalues[0])),
                float(scale * np.sqrt(eigenvalues[1])),
                float(scale * np.sqrt(eigenvalues[2]))
            )
            scale_op.Set(gf_scale)
            
            # Make semi-transparent
            color_attr = sphere.CreateDisplayColorAttr()
            opacity_attr = sphere.CreateDisplayOpacityAttr()
            
            # Color by percentile (blue gradient)
            intensity = percentile / 100.0
            color_attr.Set([Gf.Vec3f(0.0, 0.0, intensity)])
            opacity_attr.Set([0.1])  # Very transparent
    
    def validate_and_save(self) -> Tuple[bool, List[str]]:
        """
        Validate USD scene for clinical coherence and save to disk.
        
        Returns:
            (is_valid, error_messages) tuple
        """
        errors = []
        
        # Validation checks
        if not self.stage:
            errors.append("Stage not created")
            return False, errors
        
        # Check for NaN in geometry
        for prim in self.stage.Traverse():
            if prim.IsA(UsdGeom.Curve) or prim.IsA(UsdGeom.Sphere):
                geom = UsdGeom.Imageable(prim)
                if prim.HasAttribute('points'):
                    points_attr = prim.GetAttribute('points')
                    for time in range(int(self.stage.GetStartTimeCode()),
                                    int(self.stage.GetEndTimeCode()) + 1):
                        points = points_attr.Get(time=time)
                        if points:
                            for point in points:
                                if any(np.isnan([point[0], point[1], point[2]])):
                                    errors.append(
                                        f"NaN detected in {prim.GetPath()} at time {time}"
                                    )
        
        # Check for temporal discontinuities
        # (Large jumps in position between time samples that violate
        # physiological constraints)
        max_daily_displacement = 0.5  # Maximum position change per day
        for patient_id, prim_path in self.patient_prims.items():
            trajectory_path = f'{prim_path}/Trajectory'
            if not self.stage.GetPrimAtPath(trajectory_path):
                continue
                
            curve_prim = self.stage.GetPrimAtPath(trajectory_path)
            points_attr = curve_prim.GetAttribute('points')
            
            prev_pos = None
            prev_time = None
            for time in range(int(self.stage.GetStartTimeCode()),
                            int(self.stage.GetEndTimeCode()) + 1):
                points = points_attr.Get(time=time)
                if points and len(points) > 0:
                    current_pos = points[-1]  # Last point in trajectory
                    
                    if prev_pos is not None:
                        displacement = np.sqrt(
                            (current_pos[0] - prev_pos[0])**2 +
                            (current_pos[1] - prev_pos[1])**2 +
                            (current_pos[2] - prev_pos[2])**2
                        )
                        time_delta = time - prev_time
                        
                        if displacement / time_delta > max_daily_displacement:
                            errors.append(
                                f"Discontinuity in {prim_path}: "
                                f"displacement {displacement:.3f} over "
                                f"{time_delta} days exceeds maximum"
                            )
                    
                    prev_pos = current_pos
                    prev_time = time
        
        # If validation passes, save
        if len(errors) == 0:
            self.stage.GetRootLayer().Save()
            return True, []
        else:
            return False, errors


# Demonstration of USD generation pipeline
def demo_usd_generation():
    """
    Complete demonstration of USD scene generation for digital twins.
    """
    # Generate synthetic patient data
    np.random.seed(42)
    N_patients = 50
    N_features = 50
    N_timepoints = 12  # Monthly measurements for one year
    
    # Create synthetic health trajectories
    patients_data = []
    for patient_idx in range(N_patients):
        # Generate trajectory with trend (improving health over time)
        base_state = np.random.randn(N_features)
        improvement_rate = np.random.uniform(0.01, 0.05, N_features)
        
        health_states = []
        timestamps = []
        start_date = datetime(2024, 1, 1)
        
        for t in range(N_timepoints):
            # Health improves each month with some noise
            current_state = (base_state + 
                           t * improvement_rate + 
                           0.1 * np.random.randn(N_features))
            health_states.append(current_state)
            timestamps.append(start_date + timedelta(days=30*t))
        
        patients_data.append({
            'id': f'PATIENT_{patient_idx:04d}',
            'states': np.array(health_states),
            'timestamps': timestamps,
            'metadata': {'age_group': '30-40' if patient_idx % 2 == 0 else '40-50'}
        })
    
    # Create manifold projector and fit to all patient data
    all_states = np.vstack([p['states'] for p in patients_data])
    
    clinical_domains = {
        'immune_function': [1, 2, 3],
        'viral_control': [0, 4, 5],
        'quality_of_life': [6, 7, 8]
    }
    
    projector = ClinicalManifoldProjector(
        sigma=1.0,
        lambda_interpretability=0.2,
        clinical_domains=clinical_domains
    )
    projector.fit(all_states)
    
    # Create USD generator
    generator = DigitalTwinUSDGenerator(
        stage_path='ihep_digital_twins.usda',
        manifold_projector=projector
    )
    generator.create_stage()
    
    # Add each patient's digital twin
    all_positions = []
    for patient_data in patients_data:
        generator.add_patient_twin(
            patient_id=patient_data['id'],
            health_states=patient_data['states'],
            timestamps=patient_data['timestamps'],
            metadata=patient_data['metadata']
        )
        
        # Collect positions for population reference frame
        positions = projector.transform(patient_data['states'])
        all_positions.append(positions)
    
    # Add population reference ellipsoids
    all_positions_array = np.vstack(all_positions)
    generator.add_population_reference_frame(
        all_positions_array,
        percentile_markers=[25, 50, 75, 90]
    )
    
    # Validate and save
    is_valid, errors = generator.validate_and_save()
    
    if is_valid:
        print("USD scene generated successfully: ihep_digital_twins.usda")
        print(f"Added {N_patients} patient digital twins")
    else:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
    
    return generator

# Execute demonstration
if __name__ == "__main__":
    generator = demo_usd_generation()