import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.optimize import minimize
from sklearn.preprocessing import StandardScaler

class ClinicalManifoldProjector:
    """
    Projects high-dimensional patient health states to 3D space while
    preserving clinical interpretability and topological structure.
    
    Mathematical Foundation:
    - Constrained manifold learning with interpretability regularization
    - Gaussian kernel for neighborhood weighting
    - Clinical composite enforcement via projection constraints
    """
    
    def __init__(self, sigma=1.0, lambda_interpretability=0.2, 
                 clinical_domains=None):
        """
        Initialize the manifold projector.
        
        Args:
            sigma: Gaussian kernel bandwidth for neighborhood weights
            lambda_interpretability: Regularization strength for clinical
                                     composite enforcement
            clinical_domains: Dictionary mapping domain names to lists of
                              feature indices comprising that domain
        """
        self.sigma = sigma
        self.lambda_interp = lambda_interpretability
        self.clinical_domains = clinical_domains or {}
        self.projection_matrix = None
        self.feature_scaler = StandardScaler()
        
    def _compute_neighbor_weights(self, X):
        """
        Compute Gaussian kernel weights encoding patient similarity.
        
        Mathematical form: w_ij = exp(-||x_i - x_j||^2 / (2*sigma^2))
        
        Args:
            X: (N, D) array of patient health states
            
        Returns:
            W: (N, N) symmetric weight matrix
        """
        # Compute pairwise squared Euclidean distances
        distances_squared = squareform(pdist(X, metric='sqeuclidean'))
        
        # Apply Gaussian kernel
        W = np.exp(-distances_squared / (2 * self.sigma**2))
        
        # Zero out self-connections
        np.fill_diagonal(W, 0)
        
        return W
    
    def _compute_clinical_composites(self, X):
        """
        Compute interpretable clinical domain composite scores.
        
        Each composite is the weighted average of features in that domain,
        providing a single summary score for immune function, viral control,
        quality of life, etc.
        
        Args:
            X: (N, D) array of patient health states
            
        Returns:
            composites: (N, K) array where K is number of clinical domains
        """
        N = X.shape[0]
        K = len(self.clinical_domains)
        composites = np.zeros((N, K))
        
        for k, (domain_name, feature_indices) in enumerate(
            self.clinical_domains.items()
        ):
            # Extract features for this clinical domain
            domain_features = X[:, feature_indices]
            
            # Compute mean (could be weighted if domain expertise available)
            composites[:, k] = np.mean(domain_features, axis=1)
            
        return composites
    
    def _distortion_loss(self, P, X, W):
        """
        Compute the distortion loss: weighted difference between original
        and projected distances.
        
        L = sum_ij [ (d_original_ij - d_projected_ij)^2 * w_ij ]
        
        Args:
            P: (N*3,) flattened array of 3D projected positions
            X: (N, D) array of original health states
            W: (N, N) weight matrix
            
        Returns:
            Scalar distortion loss
        """
        N = X.shape[0]
        P_reshaped = P.reshape(N, 3)
        
        # Original space distances
        d_original = squareform(pdist(X, metric='euclidean'))
        
        # Projected space distances
        d_projected = squareform(pdist(P_reshaped, metric='euclidean'))
        
        # Weighted squared difference
        diff = (d_original - d_projected)**2
        loss = np.sum(W * diff)
        
        return loss
    
    def _interpretability_loss(self, P, composites):
        """
        Compute interpretability regularization: penalize projections that
        cannot be expressed as linear combinations of clinical composites.
        
        For each projection axis k, we fit: P[:,k] ≈ composites @ alpha_k
        and penalize the residual.
        
        Args:
            P: (N, 3) array of projected positions
            composites: (N, K) array of clinical domain scores
            
        Returns:
            Scalar interpretability loss
        """
        loss = 0.0
        
        for k in range(3):  # For each projection axis
            # Solve least squares: composites @ alpha = P[:,k]
            alpha, residuals, _, _ = np.linalg.lstsq(
                composites, P[:, k], rcond=None
            )
            
            # Penalize residual (how poorly composites explain this axis)
            if len(residuals) > 0:
                loss += residuals[0]
            else:
                # If exact solution exists, residual is zero
                loss += 0.0
                
        return loss
    
    def _combined_loss(self, P_flat, X, W, composites):
        """
        Combined objective: distortion + lambda * interpretability
        """
        N = X.shape[0]
        P = P_flat.reshape(N, 3)
        
        L_distortion = self._distortion_loss(P_flat, X, W)
        L_interp = self._interpretability_loss(P, composites)
        
        return L_distortion + self.lambda_interp * L_interp
    
    def fit(self, X):
        """
        Fit the manifold projection to patient health data.
        
        Args:
            X: (N, D) array where N is number of patients, D is feature dimension
            
        Returns:
            self
        """
        # Standardize features to prevent scale dominance
        X_scaled = self.feature_scaler.fit_transform(X)
        
        # Compute patient similarity weights
        W = self._compute_neighbor_weights(X_scaled)
        
        # Compute clinical composites for interpretability
        composites = self._compute_clinical_composites(X_scaled)
        
        # Initialize projection with PCA for warm start
        from sklearn.decomposition import PCA
        pca = PCA(n_components=3)
        P_init = pca.fit_transform(X_scaled)
        
        # Optimize projection
        result = minimize(
            fun=self._combined_loss,
            x0=P_init.flatten(),
            args=(X_scaled, W, composites),
            method='L-BFGS-B',
            options={'maxiter': 1000, 'ftol': 1e-6}
        )
        
        # Store optimized projection as a transformation matrix
        P_optimal = result.x.reshape(-1, 3)
        
        # Compute projection matrix via least squares
        # (for out-of-sample projection)
        self.projection_matrix, _, _, _ = np.linalg.lstsq(
            X_scaled, P_optimal, rcond=None
        )
        
        return self
    
    def transform(self, X):
        """
        Project new patient data to 3D space using fitted manifold.
        
        Args:
            X: (M, D) array of new patient health states
            
        Returns:
            P: (M, 3) array of projected 3D positions
        """
        if self.projection_matrix is None:
            raise ValueError("Must call fit() before transform()")
            
        X_scaled = self.feature_scaler.transform(X)
        P = X_scaled @ self.projection_matrix
        
        return P
    
    def validate_physiological_constraints(self, X, P):
        """
        Validate that projected trajectories satisfy physiological constraints.
        
        For example, CD4 count cannot increase faster than maximum cell
        proliferation rate: dCD4/dt <= r_max * CD4 * (1 - CD4/CD4_max)
        
        Args:
            X: (N, D) original health states
            P: (N, 3) projected positions
            
        Returns:
            violations: List of (patient_idx, constraint_name) tuples
        """
        violations = []
        
        # Example constraint: CD4 proliferation rate
        # Assuming CD4 count is feature index 1 (adjust based on your data)
        cd4_idx = 1
        r_max = 0.01  # Maximum daily proliferation rate
        cd4_max = 1500  # Physiological ceiling (cells/μL)
        
        N = X.shape[0]
        for i in range(N - 1):
            cd4_current = X[i, cd4_idx]
            cd4_next = X[i + 1, cd4_idx]
            
            # Compute observed rate
            delta_cd4 = cd4_next - cd4_current
            
            # Compute maximum allowable rate
            max_delta = r_max * cd4_current * (1 - cd4_current / cd4_max)
            
            if delta_cd4 > max_delta * 1.1:  # 10% tolerance
                violations.append((i, 'cd4_proliferation_rate'))
                
        return violations


# Example usage demonstrating the complete pipeline
def demo_manifold_projection():
    """
    Demonstrates the manifold projection with synthetic patient data.
    """
    # Generate synthetic patient data (replace with real IHEP data)
    np.random.seed(42)
    N_patients = 100
    N_features = 50
    
    # Simulate health states with structure (HIV-related correlations)
    X = np.random.randn(N_patients, N_features)
    
    # Induce correlation between viral load (feature 0) and CD4 (feature 1)
    X[:, 1] = -0.7 * X[:, 0] + 0.3 * np.random.randn(N_patients)
    
    # Define clinical domains for interpretability
    clinical_domains = {
        'immune_function': [1, 2, 3],  # CD4, CD4%, CD8 activation
        'viral_control': [0, 4, 5],     # Viral load, resistance, adherence
        'quality_of_life': [6, 7, 8]   # Mental health, social support, function
    }
    
    # Create and fit projector
    projector = ClinicalManifoldProjector(
        sigma=1.0,
        lambda_interpretability=0.2,
        clinical_domains=clinical_domains
    )
    
    projector.fit(X)
    
    # Project to 3D
    P = projector.transform(X)
    
    # Validate physiological constraints
    violations = projector.validate_physiological_constraints(X, P)
    
    print(f"Projected {N_patients} patients to 3D space")
    print(f"Projection shape: {P.shape}")
    print(f"Physiological constraint violations: {len(violations)}")
    
    return projector, P

# Execute demonstration
if __name__ == "__main__":
    projector, projections = demo_manifold_projection()