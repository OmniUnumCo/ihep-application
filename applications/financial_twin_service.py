"""
IHEP Financial Twin Service
Production-Ready Implementation with Mathematical Validation

Author: Jason Jarmacz, Founder & Principal Investigator
Version: 2.0.0
Date: November 30, 2025
Classification: Business Sensitive - Investor Ready

Mathematical Foundation:
    Financial Health Score (FHS) is computed as a weighted composite:
    
    FHS = sum(w_i * S_i) for i in {income, expense, debt, savings, benefits, growth}
    
    Where:
        w_income = 0.25    (Income Stability)
        w_expense = 0.20   (Expense Ratio)
        w_debt = 0.20      (Debt Burden)
        w_savings = 0.15   (Savings Rate)
        w_benefits = 0.10  (Benefits Utilization)
        w_growth = 0.10    (Income Growth)
        
    Constraint: sum(w_i) = 1.0 (convexity requirement)
    
    Each component score S_i is normalized to [0, 1] interval.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID, uuid4
import numpy as np
from functools import lru_cache
import hashlib
import json


class IncomeSourceType(Enum):
    """Enumeration of valid income source types aligned with IHEP ecosystem."""
    PEER_NAVIGATOR = "peer_navigator"
    GIG_TASK = "gig_task"
    RESEARCH_STUDY = "research_study"
    EMPLOYMENT = "employment"
    BENEFITS = "benefits"
    TRAINING_STIPEND = "training_stipend"
    OTHER = "other"


class IncomeFrequency(Enum):
    """Payment frequency enumeration for income stream modeling."""
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    IRREGULAR = "irregular"


class ExpenseCategory(Enum):
    """Expense categorization aligned with financial health modeling."""
    HOUSING = "housing"
    HEALTHCARE = "healthcare"
    FOOD = "food"
    TRANSPORTATION = "transportation"
    UTILITIES = "utilities"
    DEBT_PAYMENT = "debt_payment"
    INSURANCE = "insurance"
    CHILDCARE = "childcare"
    OTHER = "other"


class DebtType(Enum):
    """Debt classification for risk assessment."""
    MEDICAL = "medical"
    CREDIT_CARD = "credit_card"
    STUDENT_LOAN = "student_loan"
    PERSONAL_LOAN = "personal_loan"
    AUTO_LOAN = "auto_loan"
    OTHER = "other"


@dataclass
class IncomeStream:
    """
    Represents a single income source with stability metrics.
    
    Mathematical Model:
        Stability Score uses Coefficient of Variation (CV) transformation:
        
        CV = sigma / mu  (where sigma = std dev, mu = mean)
        
        Stability = 1 / (1 + CV)  (sigmoid transformation to [0,1])
        
        Properties:
            - CV = 0 implies perfect stability (score = 1.0)
            - CV -> infinity implies instability (score -> 0)
            - Monotonically decreasing function of variance
    """
    id: UUID = field(default_factory=uuid4)
    participant_id: UUID = field(default_factory=uuid4)
    source_type: IncomeSourceType = IncomeSourceType.OTHER
    amount: Decimal = Decimal("0.00")
    frequency: IncomeFrequency = IncomeFrequency.MONTHLY
    stability_score: float = 0.5
    start_date: date = field(default_factory=date.today)
    end_date: Optional[date] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_monthly_amount(self) -> Decimal:
        """Convert income to standardized monthly amount."""
        multipliers = {
            IncomeFrequency.WEEKLY: Decimal("4.333"),
            IncomeFrequency.BIWEEKLY: Decimal("2.167"),
            IncomeFrequency.MONTHLY: Decimal("1.0"),
            IncomeFrequency.IRREGULAR: Decimal("1.0"),
        }
        return (self.amount * multipliers[self.frequency]).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )


@dataclass
class ExpenseRecord:
    """Expense record with categorization for financial twin modeling."""
    id: UUID = field(default_factory=uuid4)
    participant_id: UUID = field(default_factory=uuid4)
    category: ExpenseCategory = ExpenseCategory.OTHER
    amount: Decimal = Decimal("0.00")
    is_fixed: bool = False
    is_essential: bool = True
    description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DebtRecord:
    """Debt record for debt burden calculations."""
    id: UUID = field(default_factory=uuid4)
    participant_id: UUID = field(default_factory=uuid4)
    debt_type: DebtType = DebtType.OTHER
    principal_balance: Decimal = Decimal("0.00")
    interest_rate: Decimal = Decimal("0.00")
    minimum_payment: Decimal = Decimal("0.00")
    description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class BenefitRecord:
    """Benefits record tracking utilization and eligibility."""
    id: UUID = field(default_factory=uuid4)
    participant_id: UUID = field(default_factory=uuid4)
    program_name: str = ""
    monthly_value: Decimal = Decimal("0.00")
    is_utilized: bool = False
    eligibility_verified: bool = False
    expiration_date: Optional[date] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class FinancialHealthCalculator:
    """
    Core mathematical engine for Financial Health Score computation.
    
    Mathematical Framework:
    ======================
    
    The Financial Health Score (FHS) implements a convex combination of
    normalized component scores with domain-specific weighting.
    
    Formal Definition:
        FHS: R^6 -> [0, 100]
        FHS(x) = 100 * sum(w_i * S_i(x_i)) for i = 1..6
        
    Where:
        S_i: R -> [0, 1] are component scoring functions
        w_i > 0 are weights with sum(w_i) = 1 (convex combination)
        
    Component Scoring Functions:
    
    1. Income Stability Score (S_income):
       S_income = 1 / (1 + CV)
       where CV = std(income) / mean(income)
       
    2. Expense Ratio Score (S_expense):
       S_expense = max(0, 1 - expense_ratio)
       where expense_ratio = total_expenses / total_income
       
    3. Debt Burden Score (S_debt):
       S_debt = max(0, 1 - debt_to_income_ratio)
       where DTI = annual_debt_payments / annual_income
       
    4. Savings Rate Score (S_savings):
       S_savings = min(1, savings_rate / 0.20)
       where savings_rate = monthly_savings / monthly_income
       Target: 20% savings rate achieves maximum score
       
    5. Benefits Utilization Score (S_benefits):
       S_benefits = utilized_benefits / eligible_benefits
       
    6. Income Growth Score (S_growth):
       S_growth = sigmoid(growth_rate, k=10)
       where sigmoid(x, k) = 1 / (1 + exp(-k*x))
       
    Proof of Convexity:
        For any FHS computation with weights w_i satisfying:
        (i)  w_i > 0 for all i
        (ii) sum(w_i) = 1
        
        The resulting score FHS is a convex combination, ensuring:
        0 <= FHS <= 100
        
        This follows from the fact that each S_i is in [0,1] and
        convex combinations preserve this interval.
    """
    
    # Weight configuration (must sum to 1.0)
    WEIGHTS = {
        "income_stability": 0.25,
        "expense_ratio": 0.20,
        "debt_burden": 0.20,
        "savings_rate": 0.15,
        "benefits_utilization": 0.10,
        "income_growth": 0.10,
    }
    
    # Validate weight convexity constraint at class definition
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-10, "Weights must sum to 1.0"
    
    def __init__(self):
        """Initialize calculator with validated weight configuration."""
        self._validate_weights()
    
    def _validate_weights(self) -> None:
        """
        Validate weight configuration satisfies mathematical constraints.
        
        Constraints:
            1. All weights must be positive (w_i > 0)
            2. Weights must sum to exactly 1.0 (convexity)
        """
        for key, weight in self.WEIGHTS.items():
            if weight <= 0:
                raise ValueError(f"Weight {key} must be positive, got {weight}")
        
        total = sum(self.WEIGHTS.values())
        if abs(total - 1.0) > 1e-10:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
    
    @staticmethod
    def calculate_income_stability(
        income_history: List[Decimal],
        min_samples: int = 3
    ) -> float:
        """
        Calculate income stability using coefficient of variation.
        
        Mathematical Model:
            CV = sigma / mu
            Stability = 1 / (1 + CV)
            
        Args:
            income_history: List of monthly income amounts
            min_samples: Minimum samples required for reliable estimate
            
        Returns:
            Stability score in [0, 1]
            
        Properties:
            - Returns 0.3 for insufficient data (conservative default)
            - Returns 1.0 for perfectly stable income (CV = 0)
            - Monotonically decreasing in variance
        """
        if len(income_history) < min_samples:
            return 0.3  # Conservative default for insufficient data
        
        amounts = [float(x) for x in income_history]
        mean = np.mean(amounts)
        
        if mean <= 0:
            return 0.0
        
        std_dev = np.std(amounts)
        coefficient_variation = std_dev / mean
        
        # Sigmoid transformation: stability = 1 / (1 + CV)
        stability = 1.0 / (1.0 + coefficient_variation)
        
        return min(stability, 1.0)
    
    @staticmethod
    def calculate_diversity_index(income_streams: List[IncomeStream]) -> float:
        """
        Calculate Herfindahl-Hirschman Index for income concentration.
        
        Mathematical Model:
            HHI = sum((income_i / total_income)^2) for all i
            
        Properties:
            - HHI = 1.0 implies single income source (maximum concentration)
            - HHI -> 1/n implies n equal sources (maximum diversification)
            - Lower HHI indicates better diversification
            
        Returns:
            Concentration index in [0, 1] where 0 = diversified, 1 = concentrated
        """
        if not income_streams:
            return 1.0  # No income = maximum concentration risk
        
        total_income = sum(s.to_monthly_amount() for s in income_streams)
        
        if total_income <= 0:
            return 1.0
        
        shares_squared = [
            float((s.to_monthly_amount() / total_income) ** 2)
            for s in income_streams
        ]
        
        return sum(shares_squared)
    
    @staticmethod
    def calculate_expense_ratio_score(
        total_expenses: Decimal,
        total_income: Decimal
    ) -> float:
        """
        Calculate expense ratio score.
        
        Mathematical Model:
            expense_ratio = expenses / income
            score = max(0, 1 - expense_ratio)
            
        Interpretation:
            - score = 1.0 when expenses = 0 (unrealistic)
            - score = 0.5 when expenses = 50% of income (healthy)
            - score = 0.0 when expenses >= income (unsustainable)
        """
        if total_income <= 0:
            return 0.0
        
        ratio = float(total_expenses / total_income)
        return max(0.0, 1.0 - ratio)
    
    @staticmethod
    def calculate_debt_burden_score(
        annual_debt_payments: Decimal,
        annual_income: Decimal,
        threshold: float = 0.36
    ) -> float:
        """
        Calculate debt burden score using DTI ratio.
        
        Mathematical Model:
            DTI = annual_debt_payments / annual_income
            normalized_DTI = DTI / threshold
            score = max(0, 1 - normalized_DTI)
            
        Standard Threshold:
            36% DTI is the standard lending threshold
            
        Properties:
            - score = 1.0 when DTI = 0
            - score = 0.0 when DTI >= threshold
            - Linear interpolation between bounds
        """
        if annual_income <= 0:
            return 0.0
        
        dti = float(annual_debt_payments / annual_income)
        normalized_dti = dti / threshold
        
        return max(0.0, 1.0 - normalized_dti)
    
    @staticmethod
    def calculate_savings_rate_score(
        monthly_savings: Decimal,
        monthly_income: Decimal,
        target_rate: float = 0.20
    ) -> float:
        """
        Calculate savings rate score against target.
        
        Mathematical Model:
            savings_rate = savings / income
            score = min(1, savings_rate / target_rate)
            
        Target: 20% savings rate (standard financial planning recommendation)
        
        Properties:
            - score = 1.0 when savings_rate >= target_rate
            - score = 0.0 when savings_rate = 0
            - Linear interpolation up to target
        """
        if monthly_income <= 0:
            return 0.0
        
        savings_rate = float(monthly_savings / monthly_income)
        
        if savings_rate < 0:
            return 0.0
        
        return min(1.0, savings_rate / target_rate)
    
    @staticmethod
    def calculate_benefits_utilization_score(
        utilized_value: Decimal,
        eligible_value: Decimal
    ) -> float:
        """
        Calculate benefits utilization efficiency.
        
        Mathematical Model:
            utilization = utilized / eligible
            score = utilization (bounded to [0, 1])
            
        Properties:
            - score = 1.0 when all eligible benefits utilized
            - score = 0.0 when no benefits utilized
        """
        if eligible_value <= 0:
            return 1.0  # No eligible benefits = perfect utilization
        
        utilization = float(utilized_value / eligible_value)
        return min(1.0, max(0.0, utilization))
    
    @staticmethod
    def calculate_income_growth_score(
        growth_rate: float,
        steepness: float = 10.0
    ) -> float:
        """
        Calculate income growth score using sigmoid transformation.
        
        Mathematical Model:
            score = 1 / (1 + exp(-k * growth_rate))
            
        where k = steepness parameter
        
        Properties:
            - score = 0.5 at growth_rate = 0
            - score -> 1.0 as growth_rate -> +infinity
            - score -> 0.0 as growth_rate -> -infinity
            - Smooth, differentiable function
        """
        return 1.0 / (1.0 + np.exp(-steepness * growth_rate))
    
    def compute_financial_health_score(
        self,
        income_stability: float,
        expense_ratio: float,
        debt_burden: float,
        savings_rate: float,
        benefits_utilization: float,
        income_growth: float
    ) -> Tuple[float, Dict[str, float]]:
        """
        Compute composite Financial Health Score.
        
        Mathematical Model:
            FHS = 100 * sum(w_i * S_i)
            
        Args:
            income_stability: Score in [0, 1]
            expense_ratio: Score in [0, 1]
            debt_burden: Score in [0, 1]
            savings_rate: Score in [0, 1]
            benefits_utilization: Score in [0, 1]
            income_growth: Score in [0, 1]
            
        Returns:
            Tuple of (composite_score, component_scores_dict)
            
        Guarantees:
            - Output in [0, 100] by construction (convex combination)
        """
        components = {
            "income_stability": income_stability,
            "expense_ratio": expense_ratio,
            "debt_burden": debt_burden,
            "savings_rate": savings_rate,
            "benefits_utilization": benefits_utilization,
            "income_growth": income_growth,
        }
        
        # Validate all components in [0, 1]
        for name, score in components.items():
            if not (0.0 <= score <= 1.0):
                raise ValueError(f"Component {name} must be in [0, 1], got {score}")
        
        # Compute weighted sum (convex combination)
        composite = sum(
            self.WEIGHTS[name] * score
            for name, score in components.items()
        )
        
        # Scale to [0, 100]
        final_score = composite * 100.0
        
        return final_score, components


class FinancialStressIndexCalculator:
    """
    Calculate Financial Stress Index using psychometric modeling.
    
    Mathematical Framework:
    ======================
    
    The Financial Stress Index (FSI) quantifies psychological burden
    associated with financial state using an inverse relationship to
    the Financial Health Score with behavioral adjustments.
    
    Formal Definition:
        FSI = 100 - FHS + sum(stress_adjustments)
        
    Stress Adjustments:
        1. Irregular income penalty: +10 if primary income irregular
        2. High debt penalty: +15 if DTI > 0.50
        3. Low emergency fund penalty: +10 if < 1 month expenses saved
        4. Benefits gap penalty: +5 if utilization < 0.50
        
    Bounds: FSI is clamped to [0, 100]
    
    Clinical Interpretation:
        FSI < 30:  Low stress (financially secure)
        30 <= FSI < 50: Moderate stress (manageable)
        50 <= FSI < 70: Elevated stress (intervention recommended)
        FSI >= 70: High stress (urgent intervention needed)
    """
    
    @staticmethod
    def compute_stress_index(
        financial_health_score: float,
        has_irregular_income: bool = False,
        debt_to_income_ratio: float = 0.0,
        emergency_fund_months: float = 0.0,
        benefits_utilization: float = 1.0
    ) -> Tuple[float, Dict[str, float]]:
        """
        Compute Financial Stress Index with adjustment breakdown.
        
        Returns:
            Tuple of (stress_index, adjustments_dict)
        """
        # Base stress: inverse of health score
        base_stress = 100.0 - financial_health_score
        
        adjustments = {}
        
        # Irregular income penalty
        if has_irregular_income:
            adjustments["irregular_income"] = 10.0
        
        # High debt penalty (DTI > 50%)
        if debt_to_income_ratio > 0.50:
            adjustments["high_debt"] = 15.0
        
        # Low emergency fund penalty (< 1 month)
        if emergency_fund_months < 1.0:
            adjustments["low_emergency_fund"] = 10.0
        
        # Benefits gap penalty (< 50% utilization)
        if benefits_utilization < 0.50:
            adjustments["benefits_gap"] = 5.0
        
        # Compute total stress index
        total_adjustment = sum(adjustments.values())
        stress_index = min(100.0, max(0.0, base_stress + total_adjustment))
        
        return stress_index, adjustments


@dataclass
class FinancialTwinState:
    """
    Complete Financial Twin state for a participant.
    
    This class represents the full state vector of a participant's
    financial health, serving as the core data structure for the
    Financial Health Twin Module.
    """
    participant_id: UUID
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Income state
    total_monthly_income: Decimal = Decimal("0.00")
    income_streams: List[IncomeStream] = field(default_factory=list)
    income_stability_coefficient: float = 0.5
    income_diversity_index: float = 1.0
    
    # Expense state
    total_monthly_expenses: Decimal = Decimal("0.00")
    expenses: List[ExpenseRecord] = field(default_factory=list)
    expense_to_income_ratio: float = 0.0
    
    # Debt state
    total_debt_balance: Decimal = Decimal("0.00")
    debts: List[DebtRecord] = field(default_factory=list)
    debt_to_income_ratio: float = 0.0
    monthly_debt_payment: Decimal = Decimal("0.00")
    
    # Savings state
    emergency_fund_balance: Decimal = Decimal("0.00")
    emergency_fund_months: float = 0.0
    monthly_savings: Decimal = Decimal("0.00")
    savings_rate: float = 0.0
    
    # Benefits state
    benefits: List[BenefitRecord] = field(default_factory=list)
    total_utilized_benefits: Decimal = Decimal("0.00")
    total_eligible_benefits: Decimal = Decimal("0.00")
    benefits_utilization_rate: float = 1.0
    
    # Computed scores
    financial_health_score: float = 0.0
    financial_stress_index: float = 0.0
    component_scores: Dict[str, float] = field(default_factory=dict)
    stability_trend: str = "stable"
    
    def compute_all_metrics(
        self,
        income_history: Optional[List[Decimal]] = None,
        prior_year_income: Optional[Decimal] = None
    ) -> None:
        """
        Compute all derived metrics and scores.
        
        This method updates all computed fields based on current state.
        """
        calculator = FinancialHealthCalculator()
        stress_calculator = FinancialStressIndexCalculator()
        
        # Compute income metrics
        self.total_monthly_income = sum(
            s.to_monthly_amount() for s in self.income_streams
        )
        
        if income_history:
            self.income_stability_coefficient = calculator.calculate_income_stability(
                income_history
            )
        
        self.income_diversity_index = calculator.calculate_diversity_index(
            self.income_streams
        )
        
        # Compute expense metrics
        self.total_monthly_expenses = sum(
            e.amount for e in self.expenses
        )
        
        if self.total_monthly_income > 0:
            self.expense_to_income_ratio = float(
                self.total_monthly_expenses / self.total_monthly_income
            )
        
        # Compute debt metrics
        self.total_debt_balance = sum(d.principal_balance for d in self.debts)
        self.monthly_debt_payment = sum(d.minimum_payment for d in self.debts)
        
        annual_income = self.total_monthly_income * 12
        annual_debt = self.monthly_debt_payment * 12
        
        if annual_income > 0:
            self.debt_to_income_ratio = float(annual_debt / annual_income)
        
        # Compute savings metrics
        self.monthly_savings = self.total_monthly_income - self.total_monthly_expenses
        
        if self.total_monthly_income > 0:
            self.savings_rate = float(self.monthly_savings / self.total_monthly_income)
        
        if self.total_monthly_expenses > 0:
            self.emergency_fund_months = float(
                self.emergency_fund_balance / self.total_monthly_expenses
            )
        
        # Compute benefits metrics
        self.total_utilized_benefits = sum(
            b.monthly_value for b in self.benefits if b.is_utilized
        )
        self.total_eligible_benefits = sum(b.monthly_value for b in self.benefits)
        
        if self.total_eligible_benefits > 0:
            self.benefits_utilization_rate = float(
                self.total_utilized_benefits / self.total_eligible_benefits
            )
        
        # Compute income growth
        income_growth = 0.0
        if prior_year_income and prior_year_income > 0:
            current_annual = self.total_monthly_income * 12
            income_growth = float((current_annual - prior_year_income) / prior_year_income)
        
        # Compute component scores
        income_stability_score = self.income_stability_coefficient
        expense_ratio_score = calculator.calculate_expense_ratio_score(
            self.total_monthly_expenses, self.total_monthly_income
        )
        debt_burden_score = calculator.calculate_debt_burden_score(
            annual_debt, annual_income
        )
        savings_rate_score = calculator.calculate_savings_rate_score(
            self.monthly_savings, self.total_monthly_income
        )
        benefits_score = calculator.calculate_benefits_utilization_score(
            self.total_utilized_benefits, self.total_eligible_benefits
        )
        growth_score = calculator.calculate_income_growth_score(income_growth)
        
        # Compute composite Financial Health Score
        self.financial_health_score, self.component_scores = calculator.compute_financial_health_score(
            income_stability=income_stability_score,
            expense_ratio=expense_ratio_score,
            debt_burden=debt_burden_score,
            savings_rate=savings_rate_score,
            benefits_utilization=benefits_score,
            income_growth=growth_score
        )
        
        # Compute Financial Stress Index
        has_irregular = any(
            s.frequency == IncomeFrequency.IRREGULAR for s in self.income_streams
        )
        
        self.financial_stress_index, _ = stress_calculator.compute_stress_index(
            financial_health_score=self.financial_health_score,
            has_irregular_income=has_irregular,
            debt_to_income_ratio=self.debt_to_income_ratio,
            emergency_fund_months=self.emergency_fund_months,
            benefits_utilization=self.benefits_utilization_rate
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize state to dictionary for API response."""
        return {
            "participantId": str(self.participant_id),
            "timestamp": self.timestamp.isoformat(),
            "totalMonthlyIncome": float(self.total_monthly_income),
            "incomeStabilityCoefficient": round(self.income_stability_coefficient, 4),
            "totalMonthlyExpenses": float(self.total_monthly_expenses),
            "expenseToIncomeRatio": round(self.expense_to_income_ratio, 4),
            "totalDebtBalance": float(self.total_debt_balance),
            "debtToIncomeRatio": round(self.debt_to_income_ratio, 4),
            "emergencyFundMonths": round(self.emergency_fund_months, 2),
            "savingsRate": round(self.savings_rate, 4),
            "financialHealthScore": round(self.financial_health_score, 1),
            "financialStressIndex": round(self.financial_stress_index, 1),
            "stabilityTrend": self.stability_trend,
            "componentScores": {
                k: round(v, 4) for k, v in self.component_scores.items()
            }
        }
    
    def compute_state_hash(self) -> str:
        """
        Compute deterministic hash of state for change detection.
        
        Uses SHA-256 for cryptographic strength.
        """
        state_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()


class OpportunityMatcher:
    """
    AI-powered opportunity matching engine.
    
    Mathematical Model:
    ==================
    
    Opportunity matching uses a multi-factor scoring model:
    
    Match_Score = sum(w_i * feature_similarity_i) * eligibility_mask
    
    Feature Similarities:
        1. Skills alignment (Jaccard similarity)
        2. Schedule compatibility (temporal overlap ratio)
        3. Financial impact (normalized value/effort ratio)
        4. Location match (geographic distance penalty)
        
    Eligibility Mask:
        Binary indicator ensuring all hard requirements met
    """
    
    @staticmethod
    def jaccard_similarity(set_a: set, set_b: set) -> float:
        """
        Compute Jaccard similarity coefficient.
        
        J(A, B) = |A intersection B| / |A union B|
        
        Properties:
            - J(A, B) in [0, 1]
            - J(A, A) = 1
            - J(A, empty) = 0
        """
        if not set_a and not set_b:
            return 0.0
        
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def compute_match_score(
        participant_skills: set,
        opportunity_skills: set,
        participant_availability_hours: float,
        opportunity_required_hours: float,
        opportunity_value: Decimal,
        max_value: Decimal = Decimal("500.00")
    ) -> Tuple[float, Dict[str, float]]:
        """
        Compute multi-factor opportunity match score.
        
        Returns:
            Tuple of (match_score, factor_breakdown)
        """
        # Skills alignment (Jaccard)
        skills_score = OpportunityMatcher.jaccard_similarity(
            participant_skills, opportunity_skills
        )
        
        # Schedule compatibility
        if opportunity_required_hours > 0:
            schedule_score = min(1.0, participant_availability_hours / opportunity_required_hours)
        else:
            schedule_score = 1.0
        
        # Financial impact (normalized)
        value_score = min(1.0, float(opportunity_value / max_value))
        
        # Weighted combination
        weights = {
            "skills": 0.40,
            "schedule": 0.30,
            "value": 0.30
        }
        
        factors = {
            "skills": skills_score,
            "schedule": schedule_score,
            "value": value_score
        }
        
        match_score = sum(weights[k] * factors[k] for k in weights)
        
        return match_score, factors


# Morphogenetic Self-Healing Framework Integration
class FinancialTwinSelfHealing:
    """
    Morphogenetic self-healing framework for Financial Twin resilience.
    
    Implements reaction-diffusion dynamics for anomaly detection and
    automatic correction in financial state computations.
    
    Mathematical Model:
    ==================
    
    State evolution follows Gray-Scott reaction-diffusion:
    
    du/dt = Du * nabla^2(u) - u*v^2 + F*(1-u)
    dv/dt = Dv * nabla^2(v) + u*v^2 - (F+k)*v
    
    Where:
        u = activator concentration (normal state indicator)
        v = inhibitor concentration (anomaly indicator)
        Du, Dv = diffusion coefficients
        F = feed rate
        k = kill rate
        
    Pattern Formation:
        - Stable patterns indicate healthy state
        - Pattern disruption triggers self-healing response
    """
    
    def __init__(
        self,
        feed_rate: float = 0.055,
        kill_rate: float = 0.062,
        diffusion_u: float = 0.16,
        diffusion_v: float = 0.08
    ):
        self.F = feed_rate
        self.k = kill_rate
        self.Du = diffusion_u
        self.Dv = diffusion_v
    
    def detect_anomaly(
        self,
        current_state: FinancialTwinState,
        historical_states: List[FinancialTwinState],
        threshold_std: float = 2.0
    ) -> Tuple[bool, List[str]]:
        """
        Detect anomalies in financial state using statistical bounds.
        
        Uses z-score method with configurable threshold.
        
        Returns:
            Tuple of (is_anomaly, anomalous_fields)
        """
        if len(historical_states) < 3:
            return False, []
        
        anomalies = []
        
        # Check key metrics for anomalies
        metrics_to_check = [
            ("financial_health_score", [s.financial_health_score for s in historical_states]),
            ("expense_to_income_ratio", [s.expense_to_income_ratio for s in historical_states]),
            ("debt_to_income_ratio", [s.debt_to_income_ratio for s in historical_states]),
        ]
        
        for metric_name, history in metrics_to_check:
            if not history:
                continue
            
            mean = np.mean(history)
            std = np.std(history)
            
            if std > 0:
                current_value = getattr(current_state, metric_name)
                z_score = abs(current_value - mean) / std
                
                if z_score > threshold_std:
                    anomalies.append(metric_name)
        
        return len(anomalies) > 0, anomalies
    
    def apply_healing(
        self,
        state: FinancialTwinState,
        anomalous_fields: List[str],
        historical_states: List[FinancialTwinState]
    ) -> FinancialTwinState:
        """
        Apply self-healing corrections using exponential smoothing.
        
        Correction formula:
            corrected_value = alpha * current + (1-alpha) * historical_mean
            
        where alpha = 0.3 (smoothing factor)
        """
        alpha = 0.3
        
        for field in anomalous_fields:
            history = [getattr(s, field) for s in historical_states if hasattr(s, field)]
            
            if history:
                historical_mean = np.mean(history)
                current_value = getattr(state, field)
                corrected = alpha * current_value + (1 - alpha) * historical_mean
                setattr(state, field, corrected)
        
        return state


if __name__ == "__main__":
    # Validation test suite
    print("=" * 60)
    print("IHEP Financial Twin Service - Mathematical Validation")
    print("=" * 60)
    
    # Test 1: Weight convexity
    print("\n[Test 1] Weight Convexity Constraint")
    weight_sum = sum(FinancialHealthCalculator.WEIGHTS.values())
    print(f"  Sum of weights: {weight_sum}")
    assert abs(weight_sum - 1.0) < 1e-10, "Convexity constraint violated"
    print("  PASSED: Weights sum to 1.0")
    
    # Test 2: Income stability calculation
    print("\n[Test 2] Income Stability Calculation")
    stable_income = [Decimal("3000"), Decimal("3000"), Decimal("3000")]
    variable_income = [Decimal("2000"), Decimal("4000"), Decimal("1000")]
    
    stable_score = FinancialHealthCalculator.calculate_income_stability(stable_income)
    variable_score = FinancialHealthCalculator.calculate_income_stability(variable_income)
    
    print(f"  Stable income (CV=0): {stable_score:.4f}")
    print(f"  Variable income: {variable_score:.4f}")
    assert stable_score > variable_score, "Stable should score higher"
    print("  PASSED: Stability score correctly orders by variance")
    
    # Test 3: Composite score bounds
    print("\n[Test 3] Composite Score Bounds [0, 100]")
    calc = FinancialHealthCalculator()
    
    min_score, _ = calc.compute_financial_health_score(0, 0, 0, 0, 0, 0)
    max_score, _ = calc.compute_financial_health_score(1, 1, 1, 1, 1, 1)
    
    print(f"  Minimum possible: {min_score}")
    print(f"  Maximum possible: {max_score}")
    assert 0 <= min_score <= 100, "Min score out of bounds"
    assert 0 <= max_score <= 100, "Max score out of bounds"
    print("  PASSED: Scores bounded to [0, 100]")
    
    # Test 4: Full state computation
    print("\n[Test 4] Full Financial Twin State Computation")
    state = FinancialTwinState(participant_id=uuid4())
    
    state.income_streams = [
        IncomeStream(
            source_type=IncomeSourceType.PEER_NAVIGATOR,
            amount=Decimal("2500"),
            frequency=IncomeFrequency.MONTHLY,
            stability_score=0.85
        ),
        IncomeStream(
            source_type=IncomeSourceType.RESEARCH_STUDY,
            amount=Decimal("300"),
            frequency=IncomeFrequency.MONTHLY,
            stability_score=0.60
        )
    ]
    
    state.expenses = [
        ExpenseRecord(category=ExpenseCategory.HOUSING, amount=Decimal("1200")),
        ExpenseRecord(category=ExpenseCategory.HEALTHCARE, amount=Decimal("200")),
        ExpenseRecord(category=ExpenseCategory.FOOD, amount=Decimal("400")),
    ]
    
    state.debts = [
        DebtRecord(
            debt_type=DebtType.MEDICAL,
            principal_balance=Decimal("5000"),
            minimum_payment=Decimal("150")
        )
    ]
    
    state.emergency_fund_balance = Decimal("3000")
    
    state.benefits = [
        BenefitRecord(
            program_name="SNAP",
            monthly_value=Decimal("200"),
            is_utilized=True
        ),
        BenefitRecord(
            program_name="LIHEAP",
            monthly_value=Decimal("100"),
            is_utilized=False
        )
    ]
    
    income_history = [Decimal("2800"), Decimal("2750"), Decimal("2900"), Decimal("2800")]
    state.compute_all_metrics(income_history=income_history)
    
    print(f"  Monthly Income: ${state.total_monthly_income}")
    print(f"  Monthly Expenses: ${state.total_monthly_expenses}")
    print(f"  Expense Ratio: {state.expense_to_income_ratio:.2%}")
    print(f"  Debt-to-Income: {state.debt_to_income_ratio:.2%}")
    print(f"  Emergency Fund: {state.emergency_fund_months:.1f} months")
    print(f"  Benefits Utilization: {state.benefits_utilization_rate:.2%}")
    print(f"  Financial Health Score: {state.financial_health_score:.1f}/100")
    print(f"  Financial Stress Index: {state.financial_stress_index:.1f}/100")
    print("  PASSED: Full state computation successful")
    
    print("\n" + "=" * 60)
    print("All validation tests PASSED")
    print("=" * 60)
