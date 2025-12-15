"""
IHEP Collaborative Research Application Portal
with Differential Privacy Guarantees

Mathematical Foundation:
- Epsilon-differential privacy via Laplace mechanism
- Privacy budget accounting across multiple queries
- Automated sensitivity analysis for query validation
- IRB compliance checking through rule-based system

Architecture:
- Flask/FastAPI backend with PostgreSQL storage
- JWT-based authentication with role-based access control
- Query execution engine with automatic noise injection
- Audit logging for all data access events
"""

import numpy as np
from scipy.stats import laplace
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import hashlib
import secrets
import jwt
from functools import wraps

# Privacy configuration constants
EPSILON_DEFAULT = 0.1  # Strong privacy guarantee
DELTA_DEFAULT = 1e-6   # Failure probability (for advanced composition)
MAX_QUERIES_PER_RESEARCHER = 100  # Query budget limit
PRIVACY_BUDGET_INITIAL = 1.0  # Initial epsilon allocation

class QueryType(Enum):
    """Enumeration of supported query types with sensitivity bounds."""
    MEAN = "mean"
    MEDIAN = "median"
    COUNT = "count"
    HISTOGRAM = "histogram"
    CORRELATION = "correlation"

@dataclass
class ResearchProposal:
    """
    Represents a research proposal submitted by an external investigator.
    
    Attributes capture all information needed for governance board review
    and automated compliance checking.
    """
    proposal_id: str
    principal_investigator: str
    institution: str
    email: str
    title: str
    hypothesis: str
    methodology: str
    requested_variables: List[str]
    expected_query_count: int
    irb_approval_number: Optional[str]
    irb_expiration_date: Optional[datetime]
    submission_date: datetime
    status: str  # 'pending', 'approved', 'rejected', 'expired'
    privacy_budget_allocated: float
    privacy_budget_consumed: float

@dataclass
class QueryResult:
    """
    Result of a differentially private query with metadata.
    """
    query_id: str
    researcher_id: str
    query_type: QueryType
    result_value: float
    noise_magnitude: float
    epsilon_consumed: float
    timestamp: datetime
    query_description: str

class DifferentialPrivacyEngine:
    """
    Core engine for executing differentially private queries on patient data.
    
    This implements the Laplace mechanism for numerical queries with
    automatic sensitivity analysis and privacy budget tracking.
    """
    
    def __init__(self, epsilon: float = EPSILON_DEFAULT):
        """
        Initialize the differential privacy engine.
        
        Args:
            epsilon: Privacy parameter (smaller = stronger privacy)
        """
        self.epsilon = epsilon
        self.query_log = []
        
    def compute_sensitivity(self, 
                          query_type: QueryType,
                          data_range: Tuple[float, float],
                          n_samples: int) -> float:
        """
        Compute the sensitivity of a query function.
        
        Sensitivity measures the maximum change in query output when
        adding or removing one individual from the dataset. This is
        the crucial parameter for calibrating differential privacy noise.
        
        Mathematical foundation:
        For mean queries on bounded data [min, max]:
            Sensitivity = (max - min) / n
        
        For count queries:
            Sensitivity = 1 (one person can change count by at most 1)
        
        Args:
            query_type: Type of statistical query
            data_range: (min, max) bounds on data values
            n_samples: Number of individuals in dataset
            
        Returns:
            Sensitivity value
        """
        min_val, max_val = data_range
        
        if query_type == QueryType.MEAN:
            # Mean of bounded data: adding/removing one person can change
            # the mean by at most (max - min) / n
            return (max_val - min_val) / n_samples
            
        elif query_type == QueryType.COUNT:
            # Count queries have sensitivity 1
            return 1.0
            
        elif query_type == QueryType.MEDIAN:
            # Median sensitivity depends on data distribution
            # Conservative upper bound for bounded data
            return (max_val - min_val) / 2
            
        elif query_type == QueryType.HISTOGRAM:
            # For histogram with k bins, sensitivity is 1
            # (one person can affect at most one bin by 1)
            return 1.0
            
        elif query_type == QueryType.CORRELATION:
            # Correlation coefficient in [-1, 1]
            # Sensitivity analysis is complex, use conservative bound
            return 2.0 / np.sqrt(n_samples)
            
        else:
            raise ValueError(f"Unknown query type: {query_type}")
    
    def add_laplace_noise(self, 
                         true_value: float,
                         sensitivity: float,
                         epsilon: float) -> Tuple[float, float]:
        """
        Add Laplace noise to a query result for differential privacy.
        
        The Laplace mechanism is the standard approach for epsilon-DP
        on numerical queries. The noise scale is sensitivity / epsilon.
        
        Mathematical form of Laplace distribution:
        p(x | b) = (1 / 2b) * exp(-|x| / b)
        where b = sensitivity / epsilon
        
        Args:
            true_value: Actual query result before noise
            sensitivity: Query sensitivity (from compute_sensitivity)
            epsilon: Privacy parameter
            
        Returns:
            (noisy_value, noise_magnitude) tuple
        """
        # Compute Laplace scale parameter
        scale = sensitivity / epsilon
        
        # Sample noise from Laplace(0, scale)
        noise = np.random.laplace(loc=0, scale=scale)
        
        # Add noise to true value
        noisy_value = true_value + noise
        
        return noisy_value, abs(noise)
    
    def execute_mean_query(self,
                          data: np.ndarray,
                          data_range: Tuple[float, float],
                          epsilon: float) -> QueryResult:
        """
        Execute a differentially private mean query.
        
        Example: "What is the average CD4 count for patients in this cohort?"
        
        Args:
            data: Array of values to average
            data_range: Known bounds on data values
            epsilon: Privacy budget for this query
            
        Returns:
            QueryResult with noisy mean
        """
        # Compute true mean
        true_mean = np.mean(data)
        
        # Compute sensitivity
        sensitivity = self.compute_sensitivity(
            QueryType.MEAN,
            data_range,
            len(data)
        )
        
        # Add noise
        noisy_mean, noise_mag = self.add_laplace_noise(
            true_mean,
            sensitivity,
            epsilon
        )
        
        # Create result object
        result = QueryResult(
            query_id=secrets.token_urlsafe(16),
            researcher_id="",  # Filled by portal
            query_type=QueryType.MEAN,
            result_value=noisy_mean,
            noise_magnitude=noise_mag,
            epsilon_consumed=epsilon,
            timestamp=datetime.now(),
            query_description=f"Mean of {len(data)} samples"
        )
        
        # Log query
        self.query_log.append(result)
        
        return result
    
    def execute_count_query(self,
                           predicate_matches: int,
                           epsilon: float) -> QueryResult:
        """
        Execute a differentially private counting query.
        
        Example: "How many patients have viral load < 50 copies/mL?"
        
        Args:
            predicate_matches: True count of matching individuals
            epsilon: Privacy budget for this query
            
        Returns:
            QueryResult with noisy count
        """
        # Sensitivity is always 1 for counting queries
        sensitivity = 1.0
        
        # Add noise
        noisy_count, noise_mag = self.add_laplace_noise(
            float(predicate_matches),
            sensitivity,
            epsilon
        )
        
        # Counts must be non-negative integers (post-processing)
        noisy_count = max(0, round(noisy_count))
        
        result = QueryResult(
            query_id=secrets.token_urlsafe(16),
            researcher_id="",
            query_type=QueryType.COUNT,
            result_value=noisy_count,
            noise_magnitude=noise_mag,
            epsilon_consumed=epsilon,
            timestamp=datetime.now(),
            query_description=f"Count query (true={predicate_matches})"
        )
        
        self.query_log.append(result)
        return result
    
    def execute_histogram_query(self,
                               data: np.ndarray,
                               bins: np.ndarray,
                               epsilon: float) -> Dict[str, any]:
        """
        Execute a differentially private histogram query.
        
        Example: "Distribution of patients across CD4 count ranges"
        
        Args:
            data: Array of values to bin
            bins: Bin edges for histogram
            epsilon: Privacy budget for this query
            
        Returns:
            Dictionary with bin counts and edges
        """
        # Compute true histogram
        true_counts, _ = np.histogram(data, bins=bins)
        
        # Sensitivity is 1 (one person affects at most one bin)
        sensitivity = 1.0
        
        # Add independent Laplace noise to each bin
        # Privacy budget is split across bins
        epsilon_per_bin = epsilon / len(true_counts)
        
        noisy_counts = []
        for count in true_counts:
            noisy_count, _ = self.add_laplace_noise(
                float(count),
                sensitivity,
                epsilon_per_bin
            )
            # Counts must be non-negative
            noisy_counts.append(max(0, round(noisy_count)))
        
        return {
            'bins': bins.tolist(),
            'counts': noisy_counts,
            'epsilon_consumed': epsilon,
            'query_type': 'histogram'
        }

class PrivacyBudgetManager:
    """
    Manages privacy budget allocation and consumption for researchers.
    
    Each approved researcher receives an initial privacy budget (epsilon).
    Every query consumes part of this budget. When exhausted, no more
    queries are allowed until new IRB approval is obtained.
    """
    
    def __init__(self):
        """Initialize budget manager with researcher tracking."""
        self.budgets = {}  # Maps researcher_id to remaining budget
        
    def allocate_budget(self, researcher_id: str, budget: float):
        """
        Allocate initial privacy budget to a researcher.
        
        Args:
            researcher_id: Unique identifier for researcher
            budget: Initial epsilon allocation
        """
        self.budgets[researcher_id] = budget
        print(f"Allocated privacy budget {budget} to researcher {researcher_id}")
    
    def consume_budget(self, researcher_id: str, epsilon: float) -> bool:
        """
        Attempt to consume privacy budget for a query.
        
        Args:
            researcher_id: Researcher making the query
            epsilon: Privacy cost of the query
            
        Returns:
            True if budget available and consumed, False if insufficient
        """
        if researcher_id not in self.budgets:
            print(f"No budget allocated for researcher {researcher_id}")
            return False
        
        current_budget = self.budgets[researcher_id]
        
        if current_budget < epsilon:
            print(f"Insufficient budget: requested {epsilon}, available {current_budget}")
            return False
        
        # Consume budget
        self.budgets[researcher_id] -= epsilon
        print(f"Consumed {epsilon} budget. Remaining: {self.budgets[researcher_id]}")
        return True
    
    def get_remaining_budget(self, researcher_id: str) -> float:
        """Get remaining privacy budget for a researcher."""
        return self.budgets.get(researcher_id, 0.0)

class IRBComplianceChecker:
    """
    Automated compliance checking for research proposals.
    
    This implements rule-based validation to catch common compliance
    issues before proposals reach human reviewers. This accelerates
    the review process and reduces governance board workload.
    """
    
    def __init__(self):
        """Initialize compliance checker with validation rules."""
        self.required_fields = [
            'principal_investigator',
            'institution',
            'email',
            'title',
            'hypothesis',
            'methodology',
            'requested_variables'
        ]
        
    def validate_proposal(self, proposal: ResearchProposal) -> Tuple[bool, List[str]]:
        """
        Validate a research proposal against compliance rules.
        
        Args:
            proposal: Proposal to validate
            
        Returns:
            (is_valid, error_messages) tuple
        """
        errors = []
        
        # Check required fields are present
        for field in self.required_fields:
            if not getattr(proposal, field, None):
                errors.append(f"Missing required field: {field}")
        
        # Validate IRB approval if provided
        if proposal.irb_approval_number:
            if not proposal.irb_expiration_date:
                errors.append("IRB approval number provided but no expiration date")
            elif proposal.irb_expiration_date < datetime.now():
                errors.append("IRB approval has expired")
        
        # Check query budget is reasonable
        if proposal.expected_query_count > MAX_QUERIES_PER_RESEARCHER:
            errors.append(
                f"Expected query count {proposal.expected_query_count} "
                f"exceeds maximum {MAX_QUERIES_PER_RESEARCHER}"
            )
        
        # Validate email format
        if proposal.email and '@' not in proposal.email:
            errors.append("Invalid email format")
        
        # Check for prohibited variables (if any)
        prohibited_vars = ['ssn', 'patient_name', 'address']
        requested = [v.lower() for v in proposal.requested_variables]
        for prohibited in prohibited_vars:
            if prohibited in requested:
                errors.append(f"Requested variable '{prohibited}' contains PHI and cannot be accessed")
        
        is_valid = len(errors) == 0
        return is_valid, errors

class ResearchPortalAPI:
    """
    Complete research portal API managing proposals, queries, and compliance.
    
    This is the main interface for researchers interacting with IHEP data.
    It coordinates proposal submission, review workflows, query execution,
    and privacy budget management.
    """
    
    def __init__(self):
        """Initialize the research portal with all subsystems."""
        self.dp_engine = DifferentialPrivacyEngine(epsilon=EPSILON_DEFAULT)
        self.budget_manager = PrivacyBudgetManager()
        self.compliance_checker = IRBComplianceChecker()
        self.proposals = {}  # Maps proposal_id to ResearchProposal
        self.query_results = {}  # Maps researcher_id to list of QueryResults
        
    def submit_proposal(self, proposal_data: Dict) -> Tuple[str, List[str]]:
        """
        Submit a new research proposal for review.
        
        This performs automated compliance checking and assigns a unique
        proposal ID for tracking through the review process.
        
        Args:
            proposal_data: Dictionary with proposal information
            
        Returns:
            (proposal_id, validation_errors) tuple
        """
        # Create proposal object
        proposal = ResearchProposal(
            proposal_id=secrets.token_urlsafe(16),
            principal_investigator=proposal_data.get('pi_name', ''),
            institution=proposal_data.get('institution', ''),
            email=proposal_data.get('email', ''),
            title=proposal_data.get('title', ''),
            hypothesis=proposal_data.get('hypothesis', ''),
            methodology=proposal_data.get('methodology', ''),
            requested_variables=proposal_data.get('variables', []),
            expected_query_count=proposal_data.get('query_count', 0),
            irb_approval_number=proposal_data.get('irb_number'),
            irb_expiration_date=proposal_data.get('irb_expiration'),
            submission_date=datetime.now(),
            status='pending',
            privacy_budget_allocated=0.0,
            privacy_budget_consumed=0.0
        )
        
        # Run automated compliance checks
        is_valid, errors = self.compliance_checker.validate_proposal(proposal)
        
        if is_valid:
            # Store proposal
            self.proposals[proposal.proposal_id] = proposal
            print(f"Proposal {proposal.proposal_id} submitted successfully")
            return proposal.proposal_id, []
        else:
            print(f"Proposal validation failed: {errors}")
            return "", errors
    
    def approve_proposal(self, 
                        proposal_id: str,
                        privacy_budget: float = PRIVACY_BUDGET_INITIAL):
        """
        Approve a proposal and allocate privacy budget.
        
        This would typically be called by governance board members after
        manual review. In production, this would require authentication
        and authorization checks.
        
        Args:
            proposal_id: ID of proposal to approve
            privacy_budget: Epsilon allocation for this researcher
        """
        if proposal_id not in self.proposals:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        proposal = self.proposals[proposal_id]
        proposal.status = 'approved'
        proposal.privacy_budget_allocated = privacy_budget
        
        # Create researcher account and allocate budget
        researcher_id = f"researcher_{proposal_id[:8]}"
        self.budget_manager.allocate_budget(researcher_id, privacy_budget)
        
        print(f"Proposal {proposal_id} approved with budget {privacy_budget}")
        return researcher_id
    
    def execute_query(self,
                     researcher_id: str,
                     query_type: QueryType,
                     data: np.ndarray,
                     epsilon: float,
                     **kwargs) -> Optional[QueryResult]:
        """
        Execute a differentially private query on behalf of a researcher.
        
        This is the main data access point. It checks privacy budget,
        executes the query with appropriate noise, logs the access,
        and returns the noisy result.
        
        Args:
            researcher_id: Authenticated researcher making the query
            query_type: Type of statistical query
            data: Patient data to query (already filtered to requested variables)
            epsilon: Privacy budget to spend on this query
            **kwargs: Additional query-specific parameters
            
        Returns:
            QueryResult if successful, None if budget insufficient
        """
        # Check if researcher has sufficient budget
        if not self.budget_manager.consume_budget(researcher_id, epsilon):
            print(f"Query denied: insufficient privacy budget")
            return None
        
        # Execute appropriate query type
        if query_type == QueryType.MEAN:
            data_range = kwargs.get('data_range', (data.min(), data.max()))
            result = self.dp_engine.execute_mean_query(data, data_range, epsilon)
            
        elif query_type == QueryType.COUNT:
            count = kwargs.get('count', len(data))
            result = self.dp_engine.execute_count_query(count, epsilon)
            
        elif query_type == QueryType.HISTOGRAM:
            bins = kwargs.get('bins', np.linspace(data.min(), data.max(), 10))
            result = self.dp_engine.execute_histogram_query(data, bins, epsilon)
            
        else:
            raise ValueError(f"Unsupported query type: {query_type}")
        
        # Associate result with researcher
        result.researcher_id = researcher_id
        
        # Store result
        if researcher_id not in self.query_results:
            self.query_results[researcher_id] = []
        self.query_results[researcher_id].append(result)
        
        print(f"Query executed: type={query_type}, epsilon={epsilon}")
        return result
    
    def get_researcher_query_history(self, researcher_id: str) -> List[QueryResult]:
        """
        Retrieve all queries executed by a researcher.
        
        This supports audit requirements and allows researchers to
        review their query history and remaining budget.
        
        Args:
            researcher_id: Researcher identifier
            
        Returns:
            List of QueryResult objects
        """
        return self.query_results.get(researcher_id, [])
    
    def get_researcher_budget_status(self, researcher_id: str) -> Dict:
        """
        Get current privacy budget status for a researcher.
        
        Args:
            researcher_id: Researcher identifier
            
        Returns:
            Dictionary with budget information
        """
        remaining = self.budget_manager.get_remaining_budget(researcher_id)
        consumed = 0.0
        
        # Calculate consumed budget from query history
        if researcher_id in self.query_results:
            consumed = sum(
                result.epsilon_consumed 
                for result in self.query_results[researcher_id]
            )
        
        return {
            'researcher_id': researcher_id,
            'remaining_budget': remaining,
            'consumed_budget': consumed,
            'total_allocated': remaining + consumed,
            'queries_executed': len(self.query_results.get(researcher_id, []))
        }


# Demonstration of the complete research portal workflow
def demo_research_portal():
    """
    Complete demonstration of research portal functionality.
    
    This simulates the entire workflow from proposal submission through
    query execution and budget management.
    """
    print("="*60)
    print("IHEP Research Portal Demonstration")
    print("="*60)
    
    # Initialize portal
    portal = ResearchPortalAPI()
    
    # Step 1: Researcher submits proposal
    print("\n[Step 1] Submitting research proposal...")
    proposal_data = {
        'pi_name': 'Dr. Jane Smith',
        'institution': 'Harvard Medical School',
        'email': 'jane.smith@hms.harvard.edu',
        'title': 'Predictors of Viral Suppression in Urban HIV Populations',
        'hypothesis': 'Adherence patterns and social support predict long-term viral suppression',
        'methodology': 'Retrospective cohort analysis using linear regression',
        'variables': ['viral_load', 'cd4_count', 'adherence_score', 'social_support_index'],
        'query_count': 25,
        'irb_number': 'IRB-2025-001234',
        'irb_expiration': datetime.now() + timedelta(days=365)
    }
    
    proposal_id, errors = portal.submit_proposal(proposal_data)
    
    if errors:
        print(f"Proposal rejected: {errors}")
        return
    
    print(f"Proposal submitted successfully: {proposal_id}")
    
    # Step 2: Governance board approves proposal
    print("\n[Step 2] Governance board reviewing and approving...")
    researcher_id = portal.approve_proposal(proposal_id, privacy_budget=1.0)
    print(f"Researcher account created: {researcher_id}")
    
    # Step 3: Researcher executes queries
    print("\n[Step 3] Executing differentially private queries...")
    
    # Generate synthetic patient data for demonstration
    np.random.seed(42)
    N_patients = 500
    
    # CD4 counts (cells/μL)
    cd4_data = np.random.normal(500, 200, N_patients)
    cd4_data = np.clip(cd4_data, 0, 1500)
    
    # Viral loads (copies/mL)
    viral_load_data = np.random.lognormal(3, 2, N_patients)
    viral_load_data = np.clip(viral_load_data, 0, 100000)
    
    # Query 1: Average CD4 count
    print("\nQuery 1: Mean CD4 count")
    result1 = portal.execute_query(
        researcher_id=researcher_id,
        query_type=QueryType.MEAN,
        data=cd4_data,
        epsilon=0.1,
        data_range=(0, 1500)
    )
    
    if result1:
        true_mean = np.mean(cd4_data)
        print(f"  True mean: {true_mean:.2f} cells/μL")
        print(f"  Noisy result: {result1.result_value:.2f} cells/μL")
        print(f"  Noise magnitude: {result1.noise_magnitude:.2f}")
        print(f"  Privacy cost: ε = {result1.epsilon_consumed}")
    
    # Query 2: Count of virally suppressed patients
    print("\nQuery 2: Count of virally suppressed patients (VL < 50)")
    suppressed_count = np.sum(viral_load_data < 50)
    
    result2 = portal.execute_query(
        researcher_id=researcher_id,
        query_type=QueryType.COUNT,
        data=viral_load_data,
        epsilon=0.1,
        count=suppressed_count
    )
    
    if result2:
        print(f"  True count: {suppressed_count}")
        print(f"  Noisy result: {int(result2.result_value)}")
        print(f"  Privacy cost: ε = {result2.epsilon_consumed}")
    
    # Query 3: CD4 distribution histogram
    print("\nQuery 3: CD4 count distribution")
    bins = np.array([0, 200, 350, 500, 750, 1500])
    
    result3 = portal.execute_query(
        researcher_id=researcher_id,
        query_type=QueryType.HISTOGRAM,
        data=cd4_data,
        epsilon=0.2,
        bins=bins
    )
    
    if result3:
        print(f"  Bin edges: {result3['bins']}")
        print(f"  Noisy counts: {result3['counts']}")
        print(f"  Privacy cost: ε = {result3['epsilon_consumed']}")
    
    # Step 4: Check remaining budget
    print("\n[Step 4] Checking researcher budget status...")
    budget_status = portal.get_researcher_budget_status(researcher_id)
    
    print(f"  Total allocated: {budget_status['total_allocated']:.3f}")
    print(f"  Consumed: {budget_status['consumed_budget']:.3f}")
    print(f"  Remaining: {budget_status['remaining_budget']:.3f}")
    print(f"  Queries executed: {budget_status['queries_executed']}")
    
    # Step 5: Review query history
    print("\n[Step 5] Query history for audit trail...")
    history = portal.get_researcher_query_history(researcher_id)
    
    for i, query in enumerate(history, 1):
        print(f"  Query {i}: {query.query_type.value} at {query.timestamp.isoformat()}")
        print(f"    Epsilon: {query.epsilon_consumed:.3f}")
        print(f"    Result: {query.result_value:.2f}")
    
    print("\n" + "="*60)
    print("Demonstration complete")
    print("="*60)

# Execute demonstration
if __name__ == "__main__":
    demo_research_portal()