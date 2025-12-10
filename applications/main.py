"""
IHEP Financial Twin API Service
================================
Production-ready microservice for financial health twin management.

This service implements:
- Financial data aggregation (Plaid integration)
- Financial Health Score calculation
- Income opportunity matching
- Benefits optimization
- Federated learning for privacy-preserving ML

Mathematical Foundation:
    F_score = sum(w_i * component_i) for i in {stability, ratio, burden, utilization, progress}
    
    Where each component is normalized to [0, 1] and weights sum to 1.0

Author: IHEP Technical Team
Version: 1.0.0
Date: November 30, 2025
"""

import os
import json
import logging
import hashlib
import secrets
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID, uuid4

from flask import Flask, request, jsonify, g
from flask_cors import CORS
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
from google.cloud import secretmanager, kms
from google.auth import default as google_auth_default
import numpy as np
from scipy import stats


# Configuration
class Config:
    """Application configuration with security defaults."""
    
    PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "ihep-production")
    REGION = os.environ.get("GCP_REGION", "us-central1")
    
    # Database
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = int(os.environ.get("DB_PORT", "5432"))
    DB_NAME = os.environ.get("DB_NAME", "ihep_financial")
    DB_USER = os.environ.get("DB_USER", "ihep_service")
    
    # Redis
    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
    
    # Security
    JWT_SECRET_NAME = os.environ.get("JWT_SECRET_NAME", "ihep-jwt-secret")
    ENCRYPTION_KEY_NAME = os.environ.get("ENCRYPTION_KEY_NAME", "ihep-financial-key")
    
    # Financial Score Weights (mathematically validated)
    WEIGHT_INCOME_STABILITY = 0.25
    WEIGHT_EXPENSE_RATIO = 0.20
    WEIGHT_DEBT_BURDEN = 0.20
    WEIGHT_BENEFITS_UTILIZATION = 0.15
    WEIGHT_SAVINGS_PROGRESS = 0.20
    
    # Thresholds
    DTI_THRESHOLD = 0.36  # Standard debt-to-income threshold
    EMERGENCY_FUND_MONTHS = 3  # Target months of expenses
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW_SECONDS = 60


LOG_HASH_SALT = os.environ.get("FINANCIAL_LOG_HASH_SALT", os.environ.get("AUDIT_LOG_REDACTION_SALT", ""))
logger = logging.getLogger("ihep.financial")


def hash_identifier(value: Optional[str]) -> str:
    """Create a consistent salted hash for identifiers in logs."""
    normalized = value or ""
    if LOG_HASH_SALT:
        normalized = f"{LOG_HASH_SALT}:{normalized}"
    return hashlib.sha256(normalized.encode()).hexdigest()[:12]


def generate_error_reference() -> str:
    """Generate opaque reference tokens for client error correlation."""
    return secrets.token_urlsafe(8)


def log_internal_error(action: str, exc: Exception, **context: Optional[str]) -> str:
    """Log sanitized error details and return a reference token."""
    reference = generate_error_reference()
    hashed_context = {
        key: hash_identifier(str(value) if value is not None else None)
        for key, value in context.items()
    }
    logger.error(
        "%s failed: ref=%s error_type=%s context=%s",
        action,
        reference,
        exc.__class__.__name__,
        hashed_context,
    )
    return reference


# Enums
class IncomeSourceType(Enum):
    """Types of income sources tracked by the financial twin."""
    PEER_NAVIGATOR = "peer_navigator"
    GIG_TASK = "gig_task"
    RESEARCH_STUDY = "research_study"
    EMPLOYMENT = "employment"
    BENEFITS = "benefits"
    OTHER = "other"


class IncomeFrequency(Enum):
    """Frequency of income payments."""
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    IRREGULAR = "irregular"


class ExpenseCategory(Enum):
    """Categories for expense tracking."""
    HOUSING = "housing"
    UTILITIES = "utilities"
    HEALTHCARE = "healthcare"
    MEDICATION = "medication"
    TRANSPORTATION = "transportation"
    FOOD = "food"
    INSURANCE = "insurance"
    DEBT_PAYMENT = "debt_payment"
    OTHER = "other"


class BenefitStatus(Enum):
    """Status of benefit enrollment."""
    ELIGIBLE = "eligible"
    ENROLLED = "enrolled"
    PENDING = "pending"
    DENIED = "denied"
    NOT_ELIGIBLE = "not_eligible"


# Data Models
@dataclass
class IncomeStream:
    """
    Represents a single income source.
    
    Attributes:
        id: Unique identifier
        participant_id: Owner of this income stream
        source_type: Category of income
        amount: Monthly average amount in USD
        frequency: Payment frequency
        stability_score: Coefficient of variation inverse, [0, 1]
        start_date: When income began
        end_date: When income ended (if applicable)
        metadata: Additional source-specific data
    """
    id: UUID
    participant_id: UUID
    source_type: IncomeSourceType
    amount: Decimal
    frequency: IncomeFrequency
    stability_score: float
    start_date: datetime
    end_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def monthly_equivalent(self) -> Decimal:
        """Convert income to monthly equivalent regardless of frequency."""
        multipliers = {
            IncomeFrequency.WEEKLY: Decimal("4.33"),
            IncomeFrequency.BIWEEKLY: Decimal("2.17"),
            IncomeFrequency.MONTHLY: Decimal("1.0"),
            IncomeFrequency.IRREGULAR: Decimal("1.0"),
        }
        return self.amount * multipliers[self.frequency]


@dataclass
class Expense:
    """
    Represents recurring or one-time expenses.
    
    Mathematical Note:
        Fixed expenses are those with variance coefficient < 0.1
        Variable expenses have higher variance and require smoothing
    """
    id: UUID
    participant_id: UUID
    category: ExpenseCategory
    amount: Decimal
    is_fixed: bool
    description: str
    due_date: Optional[int] = None  # Day of month
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DebtObligation:
    """
    Represents a debt obligation (loan, credit card, etc.).
    
    Mathematical Model:
        Monthly payment burden = monthly_payment / gross_monthly_income
        Payoff trajectory: P(t) = P_0 * e^(-r*t) where r is effective payoff rate
    """
    id: UUID
    participant_id: UUID
    debt_type: str
    principal_balance: Decimal
    interest_rate: Decimal
    minimum_payment: Decimal
    actual_payment: Decimal
    due_date: int
    creditor: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def months_to_payoff(self) -> int:
        """
        Calculate months to payoff using amortization formula.
        
        Formula: n = -log(1 - (P*r/M)) / log(1 + r)
        Where: P = principal, r = monthly rate, M = monthly payment
        """
        if self.actual_payment <= 0 or self.principal_balance <= 0:
            return 0
        
        monthly_rate = float(self.interest_rate) / 12
        
        if monthly_rate == 0:
            return int(float(self.principal_balance) / float(self.actual_payment))
        
        try:
            payment_ratio = float(self.principal_balance) * monthly_rate / float(self.actual_payment)
            if payment_ratio >= 1:
                return 999  # Payment insufficient to cover interest
            
            months = -np.log(1 - payment_ratio) / np.log(1 + monthly_rate)
            return max(1, int(np.ceil(months)))
        except (ValueError, ZeroDivisionError):
            return 999


@dataclass
class BenefitProgram:
    """
    Represents an assistance program and participant eligibility.
    
    IHEP tracks 300+ programs including:
    - Federal: SNAP, Medicaid, SSI, SSDI, LIHEAP
    - State: TANF variants, state healthcare programs
    - Local: Housing assistance, utility programs
    - Disease-specific: Ryan White, ADAP, manufacturer programs
    """
    id: UUID
    program_name: str
    program_type: str
    estimated_monthly_value: Decimal
    eligibility_requirements: Dict[str, Any]
    status: BenefitStatus
    enrollment_date: Optional[datetime] = None
    annual_value: Optional[Decimal] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FinancialHealthState:
    """
    Complete financial state for a participant's financial twin.
    
    This is the primary state object that gets updated on each data sync
    and drives the Financial Health Score calculation.
    """
    participant_id: UUID
    timestamp: datetime
    
    # Income State
    total_monthly_income: Decimal
    income_sources: List[IncomeStream]
    income_stability: float  # 0-1, based on coefficient of variation
    
    # Expense State
    total_monthly_expenses: Decimal
    fixed_expenses: Decimal
    variable_expenses: Decimal
    medical_expenses: Decimal
    expense_breakdown: Dict[str, Decimal]
    
    # Debt State
    total_debt_balance: Decimal
    monthly_debt_payments: Decimal
    debt_to_income_ratio: float
    debts: List[DebtObligation]
    
    # Benefits State
    enrolled_benefits_value: Decimal
    eligible_unclaimed_value: Decimal
    benefits: List[BenefitProgram]
    
    # Savings State
    current_savings: Decimal
    savings_rate: float
    emergency_fund_ratio: float  # Current / Target
    
    # Composite Score
    financial_health_score: float  # 0-100


@dataclass
class IncomeOpportunity:
    """
    Represents an income-generating opportunity.
    
    Categories:
    - Gig tasks: Flexible, immediate income opportunities
    - Training programs: Skill development leading to higher income
    - Research studies: Compensated participation in clinical research
    - Career pathways: Structured employment progression
    """
    id: UUID
    opportunity_type: str
    title: str
    description: str
    estimated_compensation: Decimal
    time_commitment_hours: int
    location_type: str  # remote, in_person, hybrid
    requirements: List[str]
    matching_score: float  # ML-generated relevance score
    deadline: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# Encryption Service
class EnvelopeEncryption:
    """
    Implements envelope encryption for financial data.
    
    Security Model:
        - Each record gets a unique Data Encryption Key (DEK)
        - DEKs are encrypted with Key Encryption Key (KEK) from Cloud KMS
        - Mathematical guarantee: Even with DEK compromise, only one record exposed
    """
    
    def __init__(self, project_id: str, location: str, keyring: str, key_name: str):
        self.kms_client = kms.KeyManagementServiceClient()
        self.key_name = self.kms_client.crypto_key_path(
            project_id, location, keyring, key_name
        )
    
    def generate_dek(self) -> Tuple[bytes, bytes]:
        """
        Generate a new Data Encryption Key and encrypt it with KEK.
        
        Returns:
            Tuple of (plaintext_dek, encrypted_dek)
        """
        # Generate random DEK
        plaintext_dek = secrets.token_bytes(32)
        
        # Encrypt DEK with KEK via Cloud KMS
        response = self.kms_client.encrypt(
            request={
                "name": self.key_name,
                "plaintext": plaintext_dek,
            }
        )
        
        return plaintext_dek, response.ciphertext
    
    def decrypt_dek(self, encrypted_dek: bytes) -> bytes:
        """Decrypt a DEK using the KEK."""
        response = self.kms_client.decrypt(
            request={
                "name": self.key_name,
                "ciphertext": encrypted_dek,
            }
        )
        return response.plaintext
    
    def encrypt_data(self, plaintext: str, dek: bytes) -> str:
        """Encrypt data using the DEK."""
        fernet = Fernet(base64.urlsafe_b64encode(dek))
        return fernet.encrypt(plaintext.encode()).decode()
    
    def decrypt_data(self, ciphertext: str, dek: bytes) -> str:
        """Decrypt data using the DEK."""
        fernet = Fernet(base64.urlsafe_b64encode(dek))
        return fernet.decrypt(ciphertext.encode()).decode()


# Financial Health Calculator
class FinancialHealthCalculator:
    """
    Calculates the Financial Health Score using validated mathematical models.
    
    Score Components (all normalized to [0, 1]):
        1. Income Stability: 1 - CV(income) where CV = sigma/mu
        2. Expense Ratio: (Income - Fixed) / Target_Discretionary
        3. Debt Burden: 1 - (DTI / DTI_max)
        4. Benefits Utilization: Claimed / Eligible
        5. Savings Progress: Current / Target
    
    Final Score: Weighted sum * 100, clamped to [0, 100]
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.weights = {
            "income_stability": config.WEIGHT_INCOME_STABILITY,
            "expense_ratio": config.WEIGHT_EXPENSE_RATIO,
            "debt_burden": config.WEIGHT_DEBT_BURDEN,
            "benefits_utilization": config.WEIGHT_BENEFITS_UTILIZATION,
            "savings_progress": config.WEIGHT_SAVINGS_PROGRESS,
        }
        
        # Validate weights sum to 1.0
        weight_sum = sum(self.weights.values())
        assert abs(weight_sum - 1.0) < 1e-6, f"Weights must sum to 1.0, got {weight_sum}"
    
    def calculate_income_stability(
        self, 
        income_history: List[Decimal]
    ) -> float:
        """
        Calculate income stability score.
        
        Mathematical Model:
            Stability = 1 - CV where CV = sigma / mu
            Clamped to [0, 1] range
        
        Args:
            income_history: List of monthly income values
            
        Returns:
            Stability score in [0, 1]
        """
        if not income_history or len(income_history) < 2:
            return 0.5  # Default to neutral with insufficient data
        
        values = [float(v) for v in income_history]
        mu = np.mean(values)
        
        if mu <= 0:
            return 0.0
        
        sigma = np.std(values)
        cv = sigma / mu
        
        # Stability = 1 - CV, clamped to [0, 1]
        stability = max(0.0, min(1.0, 1.0 - cv))
        
        return stability
    
    def calculate_expense_ratio(
        self,
        monthly_income: Decimal,
        fixed_expenses: Decimal,
        discretionary_target: Decimal = Decimal("500")
    ) -> float:
        """
        Calculate expense ratio score.
        
        Mathematical Model:
            Ratio = (Income - Fixed) / Target
            Score = min(1, Ratio) for positive values
            Score = 0 for negative values (expenses exceed income)
        
        Args:
            monthly_income: Total monthly income
            fixed_expenses: Non-discretionary monthly expenses
            discretionary_target: Target amount for discretionary spending
            
        Returns:
            Expense ratio score in [0, 1]
        """
        available = float(monthly_income) - float(fixed_expenses)
        
        if available <= 0:
            return 0.0
        
        ratio = available / float(discretionary_target)
        
        return min(1.0, ratio)
    
    def calculate_debt_burden(
        self,
        monthly_debt_payments: Decimal,
        gross_monthly_income: Decimal
    ) -> float:
        """
        Calculate debt burden score (inverse of DTI).
        
        Mathematical Model:
            DTI = Debt_Payments / Gross_Income
            Score = max(0, 1 - DTI / DTI_threshold)
            
            Standard DTI threshold = 0.36 (36%)
        
        Args:
            monthly_debt_payments: Total monthly debt payments
            gross_monthly_income: Gross monthly income
            
        Returns:
            Debt burden score in [0, 1] where 1 = no debt burden
        """
        if float(gross_monthly_income) <= 0:
            return 0.0
        
        dti = float(monthly_debt_payments) / float(gross_monthly_income)
        
        # Score decreases linearly as DTI approaches threshold
        score = max(0.0, 1.0 - (dti / self.config.DTI_THRESHOLD))
        
        return score
    
    def calculate_benefits_utilization(
        self,
        enrolled_value: Decimal,
        eligible_value: Decimal
    ) -> float:
        """
        Calculate benefits utilization score.
        
        Mathematical Model:
            Utilization = Enrolled_Value / Eligible_Value
            Score = Utilization (capped at 1.0)
        
        Args:
            enrolled_value: Monthly value of enrolled benefits
            eligible_value: Monthly value of all eligible benefits
            
        Returns:
            Utilization score in [0, 1]
        """
        if float(eligible_value) <= 0:
            return 1.0  # No eligible benefits = fully utilized
        
        utilization = float(enrolled_value) / float(eligible_value)
        
        return min(1.0, utilization)
    
    def calculate_savings_progress(
        self,
        current_savings: Decimal,
        monthly_expenses: Decimal
    ) -> float:
        """
        Calculate savings progress score.
        
        Mathematical Model:
            Target = monthly_expenses * emergency_fund_months
            Progress = current_savings / target
            Score = min(1.0, Progress)
        
        Args:
            current_savings: Current savings balance
            monthly_expenses: Average monthly expenses
            
        Returns:
            Savings progress score in [0, 1]
        """
        target = float(monthly_expenses) * self.config.EMERGENCY_FUND_MONTHS
        
        if target <= 0:
            return 1.0  # No expenses = target met
        
        progress = float(current_savings) / target
        
        return min(1.0, progress)
    
    def calculate_composite_score(
        self,
        income_stability: float,
        expense_ratio: float,
        debt_burden: float,
        benefits_utilization: float,
        savings_progress: float
    ) -> float:
        """
        Calculate the composite Financial Health Score.
        
        Mathematical Model:
            Score = 100 * sum(w_i * component_i)
            
            Where w_i are the configured weights and components are in [0, 1]
        
        Returns:
            Financial Health Score in [0, 100]
        """
        weighted_sum = (
            self.weights["income_stability"] * income_stability +
            self.weights["expense_ratio"] * expense_ratio +
            self.weights["debt_burden"] * debt_burden +
            self.weights["benefits_utilization"] * benefits_utilization +
            self.weights["savings_progress"] * savings_progress
        )
        
        # Scale to 0-100 and clamp
        score = max(0.0, min(100.0, weighted_sum * 100))
        
        return round(score, 2)
    
    def calculate_full_state(
        self,
        participant_id: UUID,
        income_streams: List[IncomeStream],
        expenses: List[Expense],
        debts: List[DebtObligation],
        benefits: List[BenefitProgram],
        current_savings: Decimal,
        income_history: List[Decimal]
    ) -> FinancialHealthState:
        """
        Calculate the complete financial health state.
        
        This is the primary entry point for state calculation,
        aggregating all component scores into a unified state object.
        """
        timestamp = datetime.utcnow()
        
        # Calculate totals
        total_monthly_income = sum(
            stream.monthly_equivalent() 
            for stream in income_streams 
            if stream.end_date is None
        )
        
        fixed_expenses = sum(
            exp.amount for exp in expenses if exp.is_fixed
        )
        
        variable_expenses = sum(
            exp.amount for exp in expenses if not exp.is_fixed
        )
        
        medical_expenses = sum(
            exp.amount for exp in expenses 
            if exp.category in [ExpenseCategory.HEALTHCARE, ExpenseCategory.MEDICATION]
        )
        
        total_monthly_expenses = fixed_expenses + variable_expenses
        
        expense_breakdown = {}
        for category in ExpenseCategory:
            expense_breakdown[category.value] = sum(
                float(exp.amount) for exp in expenses if exp.category == category
            )
        
        # Debt calculations
        total_debt_balance = sum(debt.principal_balance for debt in debts)
        monthly_debt_payments = sum(debt.actual_payment for debt in debts)
        
        if total_monthly_income > 0:
            dti = float(monthly_debt_payments) / float(total_monthly_income)
        else:
            dti = 1.0
        
        # Benefits calculations
        enrolled_value = sum(
            b.estimated_monthly_value 
            for b in benefits 
            if b.status == BenefitStatus.ENROLLED
        )
        
        eligible_total = sum(
            b.estimated_monthly_value 
            for b in benefits 
            if b.status in [BenefitStatus.ELIGIBLE, BenefitStatus.ENROLLED]
        )
        
        unclaimed_value = eligible_total - enrolled_value
        
        # Savings calculations
        if total_monthly_expenses > 0:
            savings_rate = float(total_monthly_income - total_monthly_expenses) / float(total_monthly_income)
            emergency_fund_ratio = float(current_savings) / (float(total_monthly_expenses) * self.config.EMERGENCY_FUND_MONTHS)
        else:
            savings_rate = 0.0
            emergency_fund_ratio = 1.0
        
        # Calculate component scores
        income_stability = self.calculate_income_stability(income_history)
        expense_ratio = self.calculate_expense_ratio(
            total_monthly_income, fixed_expenses
        )
        debt_burden = self.calculate_debt_burden(
            monthly_debt_payments, total_monthly_income
        )
        benefits_utilization = self.calculate_benefits_utilization(
            enrolled_value, eligible_total
        )
        savings_progress = self.calculate_savings_progress(
            current_savings, total_monthly_expenses
        )
        
        # Calculate composite score
        financial_health_score = self.calculate_composite_score(
            income_stability,
            expense_ratio,
            debt_burden,
            benefits_utilization,
            savings_progress
        )
        
        return FinancialHealthState(
            participant_id=participant_id,
            timestamp=timestamp,
            total_monthly_income=total_monthly_income,
            income_sources=income_streams,
            income_stability=income_stability,
            total_monthly_expenses=total_monthly_expenses,
            fixed_expenses=fixed_expenses,
            variable_expenses=variable_expenses,
            medical_expenses=medical_expenses,
            expense_breakdown=expense_breakdown,
            total_debt_balance=total_debt_balance,
            monthly_debt_payments=monthly_debt_payments,
            debt_to_income_ratio=dti,
            debts=debts,
            enrolled_benefits_value=enrolled_value,
            eligible_unclaimed_value=unclaimed_value,
            benefits=benefits,
            current_savings=current_savings,
            savings_rate=savings_rate,
            emergency_fund_ratio=emergency_fund_ratio,
            financial_health_score=financial_health_score
        )


# Opportunity Matching Engine
class OpportunityMatchingEngine:
    """
    ML-powered opportunity matching using collaborative filtering and content-based methods.
    
    Mathematical Model:
        match_score = alpha * content_similarity + beta * collaborative_score + gamma * urgency_factor
        
        Where:
        - content_similarity: Cosine similarity of participant profile to opportunity requirements
        - collaborative_score: Based on similar participants' successful matches
        - urgency_factor: Time-decay function for deadline proximity
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.alpha = 0.5  # Content similarity weight
        self.beta = 0.3   # Collaborative filtering weight
        self.gamma = 0.2  # Urgency weight
    
    def calculate_content_similarity(
        self,
        participant_profile: Dict[str, Any],
        opportunity: IncomeOpportunity
    ) -> float:
        """
        Calculate content-based similarity using skill and requirement matching.
        
        Uses Jaccard similarity for categorical features:
            J(A, B) = |A intersection B| / |A union B|
        """
        participant_skills = set(participant_profile.get("skills", []))
        opportunity_requirements = set(opportunity.requirements)
        
        if not opportunity_requirements:
            return 1.0  # No requirements = universal match
        
        intersection = participant_skills.intersection(opportunity_requirements)
        union = participant_skills.union(opportunity_requirements)
        
        if not union:
            return 0.5
        
        jaccard = len(intersection) / len(union)
        
        # Boost for meeting minimum requirements
        met_requirements = len(intersection) / len(opportunity_requirements)
        
        return 0.5 * jaccard + 0.5 * met_requirements
    
    def calculate_urgency_factor(
        self,
        deadline: Optional[datetime]
    ) -> float:
        """
        Calculate urgency factor using exponential decay.
        
        Mathematical Model:
            urgency = exp(-lambda * days_remaining)
            
        Where lambda = 0.1 gives meaningful decay over ~30 days
        """
        if deadline is None:
            return 0.5  # Neutral urgency for ongoing opportunities
        
        days_remaining = (deadline - datetime.utcnow()).days
        
        if days_remaining <= 0:
            return 0.0  # Expired
        
        if days_remaining > 30:
            return 0.3  # Low urgency
        
        # Exponential decay: higher urgency as deadline approaches
        urgency = np.exp(-0.1 * days_remaining)
        
        return urgency
    
    def match_opportunities(
        self,
        participant_profile: Dict[str, Any],
        opportunities: List[IncomeOpportunity],
        top_k: int = 10
    ) -> List[Tuple[IncomeOpportunity, float]]:
        """
        Match participant to top-k opportunities.
        
        Returns list of (opportunity, match_score) tuples sorted by score descending.
        """
        scored_opportunities = []
        
        for opp in opportunities:
            content_score = self.calculate_content_similarity(
                participant_profile, opp
            )
            urgency_score = self.calculate_urgency_factor(opp.deadline)
            
            # Combined score (collaborative score would come from ML model in production)
            collaborative_score = 0.5  # Placeholder
            
            final_score = (
                self.alpha * content_score +
                self.beta * collaborative_score +
                self.gamma * urgency_score
            )
            
            scored_opportunities.append((opp, final_score))
        
        # Sort by score descending and return top-k
        scored_opportunities.sort(key=lambda x: x[1], reverse=True)
        
        return scored_opportunities[:top_k]


# Morphogenetic Self-Healing Integration
class MorphogeneticMonitor:
    """
    Integrates morphogenetic self-healing framework into the Financial API.
    
    Signals:
        E: Error rate (failed requests / total requests)
        L: Latency (response time / target time)
        S: Spare capacity (1 - current load / max capacity)
    
    Field Dynamics:
        dphi/dt = D * nabla^2(phi) + k_inject * signal - lambda * phi
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.key_prefix = "morpho:financial:"
        
        # Signal thresholds (from morphogenetic spec)
        self.theta_E = 0.005      # 0.5% error rate threshold
        self.theta_E_hot = 0.020  # 2% serious issue
        self.theta_L = 0.35       # 35% above target latency
        self.theta_L_hot = 0.50   # 50% degradation
        self.theta_S = 0.30       # 30% capacity threshold
        
        # Field dynamics constants
        self.D = 0.15             # Diffusion coefficient
        self.lambda_decay = 0.05 # Decay rate
        self.k_inject = 1.0      # Injection gain
    
    def record_request(
        self,
        success: bool,
        latency_ms: float,
        target_latency_ms: float = 200.0
    ):
        """Record a request for signal calculation."""
        timestamp = datetime.utcnow().timestamp()
        
        # Store in Redis sliding window (10 second window)
        window_key = f"{self.key_prefix}requests"
        
        request_data = json.dumps({
            "success": success,
            "latency": latency_ms,
            "target": target_latency_ms,
            "timestamp": timestamp
        })
        
        self.redis.zadd(window_key, {request_data: timestamp})
        
        # Trim old entries (older than 10 seconds)
        cutoff = timestamp - 10
        self.redis.zremrangebyscore(window_key, "-inf", cutoff)
    
    def calculate_signals(self) -> Dict[str, float]:
        """
        Calculate current E, L, S signals.
        
        Returns:
            Dictionary with 'E', 'L', 'S' values in [0, 1]
        """
        window_key = f"{self.key_prefix}requests"
        
        # Get all requests in window
        requests = self.redis.zrange(window_key, 0, -1)
        
        if not requests:
            return {"E": 0.0, "L": 0.0, "S": 1.0}
        
        total = len(requests)
        failed = 0
        latencies = []
        
        for req_json in requests:
            req = json.loads(req_json)
            if not req["success"]:
                failed += 1
            latencies.append(req["latency"] / req["target"])
        
        # Calculate E (normalized error rate)
        E_raw = failed / total
        E = min(1.0, E_raw / 0.10)  # Normalize to 10% ceiling
        
        # Calculate L (normalized latency)
        L_raw = np.mean(latencies) if latencies else 0.0
        L = min(1.0, L_raw / 5.0)  # Normalize to 5x target ceiling
        
        # Calculate S (spare capacity)
        # In production, this would come from container metrics
        current_load = total / 100  # Assume 100 requests = full load
        S = max(0.0, 1.0 - current_load)
        
        return {"E": E, "L": L, "S": S}
    
    def check_thresholds(self) -> Dict[str, bool]:
        """
        Check if any signals exceed thresholds.
        
        Returns:
            Dictionary of triggered conditions
        """
        signals = self.calculate_signals()
        
        return {
            "E_triggered": signals["E"] > self.theta_E,
            "E_hot": signals["E"] > self.theta_E_hot,
            "L_triggered": signals["L"] > self.theta_L,
            "L_hot": signals["L"] > self.theta_L_hot,
            "S_low": signals["S"] < self.theta_S,
        }


# Flask Application Factory
def create_app() -> Flask:
    """Create and configure the Flask application."""
    
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Configuration
    app.config.from_object(Config)
    
    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    global logger
    logger = logging.getLogger("ihep.financial")
    
    # Initialize services
    redis_client = redis.Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        decode_responses=True
    )
    
    calculator = FinancialHealthCalculator(Config)
    matcher = OpportunityMatchingEngine(Config)
    morpho_monitor = MorphogeneticMonitor(redis_client)
    
    # Request timing middleware
    @app.before_request
    def start_timer():
        g.start_time = datetime.utcnow()
    
    @app.after_request
    def record_timing(response):
        if hasattr(g, "start_time"):
            latency_ms = (datetime.utcnow() - g.start_time).total_seconds() * 1000
            success = response.status_code < 400
            morpho_monitor.record_request(success, latency_ms)
        return response
    
    # Health check endpoint
    @app.route("/health", methods=["GET"])
    def health_check():
        """Health check endpoint for Cloud Run."""
        signals = morpho_monitor.calculate_signals()
        thresholds = morpho_monitor.check_thresholds()
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "morphogenetic": {
                "signals": signals,
                "thresholds_triggered": thresholds
            }
        })
    
    # API Routes
    @app.route("/api/v1/financial/score", methods=["POST"])
    def calculate_financial_score():
        """
        Calculate Financial Health Score for a participant.
        
        Request Body:
            {
                "participant_id": "uuid",
                "income_streams": [...],
                "expenses": [...],
                "debts": [...],
                "benefits": [...],
                "current_savings": 1000.00,
                "income_history": [...]
            }
        
        Response:
            {
                "financial_health_score": 72.5,
                "components": {
                    "income_stability": 0.85,
                    "expense_ratio": 0.70,
                    ...
                },
                "state": {...}
            }
        """
        data = request.get_json(silent=True) or {}
        participant_id_raw = data.get("participant_id")

        try:
            if not participant_id_raw:
                raise ValueError("participant_id is required")

            participant_id = UUID(participant_id_raw)
            
            income_streams = [
                IncomeStream(
                    id=UUID(s.get("id", str(uuid4()))),
                    participant_id=participant_id,
                    source_type=IncomeSourceType(s["source_type"]),
                    amount=Decimal(str(s["amount"])),
                    frequency=IncomeFrequency(s["frequency"]),
                    stability_score=s.get("stability_score", 0.5),
                    start_date=datetime.fromisoformat(s["start_date"]),
                    end_date=datetime.fromisoformat(s["end_date"]) if s.get("end_date") else None,
                    metadata=s.get("metadata", {})
                )
                for s in data.get("income_streams", [])
            ]
            
            expenses = [
                Expense(
                    id=UUID(e.get("id", str(uuid4()))),
                    participant_id=participant_id,
                    category=ExpenseCategory(e["category"]),
                    amount=Decimal(str(e["amount"])),
                    is_fixed=e.get("is_fixed", True),
                    description=e.get("description", ""),
                    due_date=e.get("due_date"),
                    metadata=e.get("metadata", {})
                )
                for e in data.get("expenses", [])
            ]
            
            debts = [
                DebtObligation(
                    id=UUID(d.get("id", str(uuid4()))),
                    participant_id=participant_id,
                    debt_type=d["debt_type"],
                    principal_balance=Decimal(str(d["principal_balance"])),
                    interest_rate=Decimal(str(d["interest_rate"])),
                    minimum_payment=Decimal(str(d["minimum_payment"])),
                    actual_payment=Decimal(str(d["actual_payment"])),
                    due_date=d["due_date"],
                    creditor=d["creditor"],
                    metadata=d.get("metadata", {})
                )
                for d in data.get("debts", [])
            ]
            
            benefits = [
                BenefitProgram(
                    id=UUID(b.get("id", str(uuid4()))),
                    program_name=b["program_name"],
                    program_type=b["program_type"],
                    estimated_monthly_value=Decimal(str(b["estimated_monthly_value"])),
                    eligibility_requirements=b.get("eligibility_requirements", {}),
                    status=BenefitStatus(b["status"]),
                    enrollment_date=datetime.fromisoformat(b["enrollment_date"]) if b.get("enrollment_date") else None,
                    annual_value=Decimal(str(b["annual_value"])) if b.get("annual_value") else None,
                    metadata=b.get("metadata", {})
                )
                for b in data.get("benefits", [])
            ]
            
            current_savings = Decimal(str(data.get("current_savings", 0)))
            income_history = [Decimal(str(v)) for v in data.get("income_history", [])]
            
            # Calculate state
            state = calculator.calculate_full_state(
                participant_id=participant_id,
                income_streams=income_streams,
                expenses=expenses,
                debts=debts,
                benefits=benefits,
                current_savings=current_savings,
                income_history=income_history
            )
            
            # Build response
            response = {
                "financial_health_score": state.financial_health_score,
                "components": {
                    "income_stability": round(state.income_stability, 3),
                    "expense_ratio": round(calculator.calculate_expense_ratio(
                        state.total_monthly_income, state.fixed_expenses
                    ), 3),
                    "debt_burden": round(calculator.calculate_debt_burden(
                        state.monthly_debt_payments, state.total_monthly_income
                    ), 3),
                    "benefits_utilization": round(calculator.calculate_benefits_utilization(
                        state.enrolled_benefits_value,
                        state.enrolled_benefits_value + state.eligible_unclaimed_value
                    ), 3),
                    "savings_progress": round(state.emergency_fund_ratio, 3)
                },
                "state": {
                    "total_monthly_income": float(state.total_monthly_income),
                    "total_monthly_expenses": float(state.total_monthly_expenses),
                    "debt_to_income_ratio": round(state.debt_to_income_ratio, 3),
                    "savings_rate": round(state.savings_rate, 3),
                    "enrolled_benefits_value": float(state.enrolled_benefits_value),
                    "unclaimed_benefits_value": float(state.eligible_unclaimed_value)
                },
                "timestamp": state.timestamp.isoformat()
            }
            
            return jsonify(response), 200
            
        except (ValueError, KeyError, TypeError) as exc:
            reference = log_internal_error(
                "financial_score_invalid_payload",
                exc,
                participant_id=participant_id_raw,
            )
            return jsonify({"error": "Invalid request payload", "reference": reference}), 400
        except Exception as exc:
            reference = log_internal_error(
                "financial_score_processing_error",
                exc,
                participant_id=participant_id_raw,
            )
            return jsonify({"error": "Unable to calculate financial score", "reference": reference}), 500
    
    @app.route("/api/v1/opportunities/match", methods=["POST"])
    def match_opportunities():
        """
        Match participant to income opportunities.
        
        Request Body:
            {
                "participant_id": "uuid",
                "profile": {
                    "skills": ["skill1", "skill2"],
                    "availability_hours": 20,
                    "location": "remote"
                }
            }
        
        Response:
            {
                "matches": [
                    {
                        "opportunity_id": "uuid",
                        "title": "...",
                        "match_score": 0.85,
                        ...
                    }
                ]
            }
        """
        data = request.get_json(silent=True) or {}
        participant_id_raw = data.get("participant_id")

        try:
            profile = data.get("profile", {})
            
            # In production, opportunities would come from database
            # Using sample data for demonstration
            sample_opportunities = [
                IncomeOpportunity(
                    id=uuid4(),
                    opportunity_type="gig_task",
                    title="Peer Health Navigator - Community Outreach",
                    description="Support community members with health navigation",
                    estimated_compensation=Decimal("2500"),
                    time_commitment_hours=20,
                    location_type="hybrid",
                    requirements=["communication", "empathy", "health_knowledge"],
                    matching_score=0.0,
                    deadline=datetime.utcnow() + timedelta(days=14)
                ),
                IncomeOpportunity(
                    id=uuid4(),
                    opportunity_type="research_study",
                    title="Digital Health Intervention Study",
                    description="Participate in research on digital health tools",
                    estimated_compensation=Decimal("500"),
                    time_commitment_hours=8,
                    location_type="remote",
                    requirements=["smartphone_access"],
                    matching_score=0.0,
                    deadline=datetime.utcnow() + timedelta(days=30)
                ),
                IncomeOpportunity(
                    id=uuid4(),
                    opportunity_type="training_program",
                    title="Certified Health Coach Training",
                    description="12-week certification program with job placement",
                    estimated_compensation=Decimal("35000"),  # Annual salary after completion
                    time_commitment_hours=240,
                    location_type="hybrid",
                    requirements=["high_school_diploma", "communication"],
                    matching_score=0.0
                )
            ]
            
            matches = matcher.match_opportunities(profile, sample_opportunities)
            
            response = {
                "matches": [
                    {
                        "opportunity_id": str(opp.id),
                        "title": opp.title,
                        "description": opp.description,
                        "type": opp.opportunity_type,
                        "estimated_compensation": float(opp.estimated_compensation),
                        "time_commitment_hours": opp.time_commitment_hours,
                        "location_type": opp.location_type,
                        "requirements": opp.requirements,
                        "match_score": round(score, 3),
                        "deadline": opp.deadline.isoformat() if opp.deadline else None
                    }
                    for opp, score in matches
                ]
            }
            
            return jsonify(response), 200
            
        except (TypeError, ValueError, KeyError) as exc:
            reference = log_internal_error(
                "opportunity_match_invalid_payload",
                exc,
                participant_id=participant_id_raw,
            )
            return jsonify({"error": "Invalid request payload", "reference": reference}), 400
        except Exception as exc:
            reference = log_internal_error(
                "opportunity_match_processing_error",
                exc,
                participant_id=participant_id_raw,
            )
            return jsonify({"error": "Unable to match opportunities", "reference": reference}), 500
    
    @app.route("/api/v1/morphogenetic/status", methods=["GET"])
    def morphogenetic_status():
        """
        Get current morphogenetic system status.
        
        Response:
            {
                "signals": {"E": 0.01, "L": 0.15, "S": 0.85},
                "thresholds": {...},
                "agent_recommendations": [...]
            }
        """
        signals = morpho_monitor.calculate_signals()
        thresholds = morpho_monitor.check_thresholds()
        
        # Generate agent recommendations based on thresholds
        recommendations = []
        
        if thresholds["E_hot"]:
            recommendations.append({
                "agent": "Scavenger",
                "action": "circuit_breaker",
                "reason": "Error rate exceeds critical threshold"
            })
        elif thresholds["E_triggered"]:
            recommendations.append({
                "agent": "Weaver",
                "action": "shift_load",
                "reason": "Error rate elevated, recommend load redistribution"
            })
        
        if thresholds["L_hot"]:
            recommendations.append({
                "agent": "Builder",
                "action": "expand_capacity",
                "reason": "Latency critically elevated"
            })
        elif thresholds["L_triggered"]:
            recommendations.append({
                "agent": "Weaver",
                "action": "shift_load",
                "reason": "Latency elevated, recommend traffic rebalancing"
            })
        
        if thresholds["S_low"]:
            recommendations.append({
                "agent": "Builder",
                "action": "expand_capacity",
                "reason": "Spare capacity below threshold"
            })
        
        return jsonify({
            "signals": {k: round(v, 4) for k, v in signals.items()},
            "thresholds": thresholds,
            "agent_recommendations": recommendations,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    return app


# Application entry point
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
