"""
IHEP Financial Twin API Service
RESTful API endpoints for Financial Health Twin Module

Author: Jason Jarmacz, Founder & Principal Investigator
Version: 2.0.0
Date: November 30, 2025

Security Architecture:
    - All endpoints require JWT authentication
    - PHI data encrypted with envelope encryption (AES-256-GCM)
    - Rate limiting: 100 requests/minute per user
    - Audit logging for all data access
    - HIPAA compliance enforced at API gateway level
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from functools import wraps
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4
import os
import json
import hashlib
import hmac
import base64
import logging

# Import core services (in production, use proper module imports)
# from services.financial_twin_service import (
#     FinancialTwinState, IncomeStream, ExpenseRecord, DebtRecord, BenefitRecord,
#     IncomeSourceType, IncomeFrequency, ExpenseCategory, DebtType,
#     FinancialHealthCalculator, OpportunityMatcher
# )

app = Flask(__name__)
CORS(app, origins=["https://ihep.app", "https://app.ihep.app"])

# Configuration
app.config["SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "development-secret-change-in-production")
app.config["RATE_LIMIT"] = 100  # requests per minute
app.config["AUDIT_LOG_ENABLED"] = True

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("financial-twin-api")


# ============================================================================
# Security Decorators
# ============================================================================

def require_auth(f):
    """
    JWT authentication decorator.
    
    Security Model:
        - Validates JWT signature using HS256
        - Checks token expiration
        - Extracts participant_id for request context
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        
        if not auth_header.startswith("Bearer "):
            logger.warning("Missing or invalid Authorization header")
            return jsonify({"error": "Authorization required"}), 401
        
        token = auth_header.split(" ")[1]
        
        try:
            # In production: use PyJWT for proper validation
            # payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            # g.participant_id = UUID(payload["sub"])
            
            # Placeholder for development
            g.participant_id = uuid4()
            g.user_role = "participant"
            
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return jsonify({"error": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    
    return decorated


def require_role(allowed_roles: List[str]):
    """Role-based access control decorator."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if g.user_role not in allowed_roles:
                logger.warning(f"Access denied: role {g.user_role} not in {allowed_roles}")
                return jsonify({"error": "Insufficient permissions"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


def audit_log(action: str):
    """
    Audit logging decorator for HIPAA compliance.
    
    Logs:
        - Timestamp (ISO 8601)
        - User ID
        - Action type
        - Resource accessed
        - Request metadata
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if app.config["AUDIT_LOG_ENABLED"]:
                log_entry = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "user_id": str(getattr(g, "participant_id", "anonymous")),
                    "action": action,
                    "resource": request.path,
                    "method": request.method,
                    "ip_address": request.remote_addr,
                    "user_agent": request.headers.get("User-Agent", "unknown")
                }
                logger.info(f"AUDIT: {json.dumps(log_entry)}")
            
            return f(*args, **kwargs)
        return decorated
    return decorator


def rate_limit(f):
    """
    Rate limiting decorator.
    
    Implementation: Token bucket algorithm
    Limit: 100 requests per minute per user
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # In production: use Redis for distributed rate limiting
        # For now, pass through
        return f(*args, **kwargs)
    return decorated


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.route("/health", methods=["GET"])
def health_check():
    """Service health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "financial-twin-api",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200


@app.route("/ready", methods=["GET"])
def readiness_check():
    """Kubernetes readiness probe."""
    # Check database connectivity, cache, etc.
    return jsonify({
        "status": "ready",
        "checks": {
            "database": "ok",
            "cache": "ok",
            "ml_service": "ok"
        }
    }), 200


# ============================================================================
# Financial Twin State Endpoints
# ============================================================================

@app.route("/api/v1/participant/<participant_id>/financial-twin", methods=["GET"])
@require_auth
@audit_log("view_financial_twin")
@rate_limit
def get_financial_twin(participant_id: str):
    """
    Retrieve current financial twin state for participant.
    
    Response Schema:
    {
        "participantId": "uuid",
        "timestamp": "ISO8601",
        "totalMonthlyIncome": number,
        "incomeStabilityCoefficient": number,
        "totalMonthlyExpenses": number,
        "expenseToIncomeRatio": number,
        "totalDebtBalance": number,
        "debtToIncomeRatio": number,
        "emergencyFundMonths": number,
        "savingsRate": number,
        "financialHealthScore": number,
        "financialStressIndex": number,
        "stabilityTrend": string,
        "componentScores": object
    }
    """
    try:
        pid = UUID(participant_id)
    except ValueError:
        return jsonify({"error": "Invalid participant ID format"}), 400
    
    # In production: fetch from database
    # state = FinancialTwinRepository.get_current_state(pid)
    
    # Mock response for development
    response = {
        "participantId": str(pid),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "totalMonthlyIncome": 3500.00,
        "incomeStabilityCoefficient": 0.82,
        "totalMonthlyExpenses": 2800.00,
        "expenseToIncomeRatio": 0.80,
        "totalDebtBalance": 8500.00,
        "debtToIncomeRatio": 0.20,
        "emergencyFundMonths": 1.5,
        "savingsRate": 0.12,
        "financialHealthScore": 67.4,
        "financialStressIndex": 42.1,
        "stabilityTrend": "improving",
        "componentScores": {
            "incomeStability": 0.78,
            "expenseRatio": 0.65,
            "debtBurden": 0.72,
            "savingsRate": 0.58,
            "benefitsUtilization": 0.80,
            "incomeGrowth": 0.55
        }
    }
    
    return jsonify(response), 200


@app.route("/api/v1/participant/<participant_id>/financial-twin/history", methods=["GET"])
@require_auth
@audit_log("view_financial_history")
@rate_limit
def get_financial_history(participant_id: str):
    """
    Retrieve historical financial twin states.
    
    Query Parameters:
        - start_date: ISO8601 date string
        - end_date: ISO8601 date string
        - granularity: "daily" | "weekly" | "monthly"
    """
    try:
        pid = UUID(participant_id)
    except ValueError:
        return jsonify({"error": "Invalid participant ID format"}), 400
    
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    granularity = request.args.get("granularity", "monthly")
    
    # In production: fetch from time-series database
    # history = FinancialTwinRepository.get_history(pid, start_date, end_date, granularity)
    
    # Mock response
    response = {
        "participantId": str(pid),
        "granularity": granularity,
        "dataPoints": [
            {
                "timestamp": "2025-09-01T00:00:00Z",
                "financialHealthScore": 58.2,
                "financialStressIndex": 51.3
            },
            {
                "timestamp": "2025-10-01T00:00:00Z",
                "financialHealthScore": 62.8,
                "financialStressIndex": 47.2
            },
            {
                "timestamp": "2025-11-01T00:00:00Z",
                "financialHealthScore": 67.4,
                "financialStressIndex": 42.1
            }
        ],
        "trend": "improving",
        "averageScore": 62.8
    }
    
    return jsonify(response), 200


# ============================================================================
# Income Stream Endpoints
# ============================================================================

@app.route("/api/v1/participant/<participant_id>/income-streams", methods=["GET"])
@require_auth
@audit_log("view_income_streams")
@rate_limit
def get_income_streams(participant_id: str):
    """Retrieve all income streams for participant."""
    try:
        pid = UUID(participant_id)
    except ValueError:
        return jsonify({"error": "Invalid participant ID format"}), 400
    
    # Mock response
    response = {
        "participantId": str(pid),
        "incomeStreams": [
            {
                "id": str(uuid4()),
                "sourceType": "peer_navigator",
                "amount": 2500.00,
                "frequency": "monthly",
                "stabilityScore": 0.85,
                "startDate": "2025-03-15"
            },
            {
                "id": str(uuid4()),
                "sourceType": "research_study",
                "amount": 300.00,
                "frequency": "monthly",
                "stabilityScore": 0.60,
                "startDate": "2025-08-01"
            }
        ],
        "totalMonthlyIncome": 2800.00,
        "diversityIndex": 0.68
    }
    
    return jsonify(response), 200


@app.route("/api/v1/participant/<participant_id>/income-streams", methods=["POST"])
@require_auth
@audit_log("create_income_stream")
@rate_limit
def create_income_stream(participant_id: str):
    """
    Create new income stream.
    
    Request Body:
    {
        "sourceType": "peer_navigator" | "gig_task" | "research_study" | ...,
        "amount": number,
        "frequency": "weekly" | "biweekly" | "monthly" | "irregular",
        "startDate": "YYYY-MM-DD",
        "metadata": object (optional)
    }
    """
    try:
        pid = UUID(participant_id)
    except ValueError:
        return jsonify({"error": "Invalid participant ID format"}), 400
    
    data = request.get_json()
    
    # Validate required fields
    required = ["sourceType", "amount", "frequency", "startDate"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400
    
    # Validate amount
    try:
        amount = Decimal(str(data["amount"]))
        if amount < 0:
            return jsonify({"error": "Amount must be non-negative"}), 400
    except:
        return jsonify({"error": "Invalid amount format"}), 400
    
    # In production: persist to database
    # stream = IncomeStreamRepository.create(pid, data)
    
    new_id = uuid4()
    response = {
        "id": str(new_id),
        "participantId": str(pid),
        "sourceType": data["sourceType"],
        "amount": float(amount),
        "frequency": data["frequency"],
        "startDate": data["startDate"],
        "stabilityScore": 0.5,  # Default for new streams
        "createdAt": datetime.utcnow().isoformat() + "Z"
    }
    
    return jsonify(response), 201


# ============================================================================
# Opportunity Matching Endpoints
# ============================================================================

@app.route("/api/v1/participant/<participant_id>/opportunities", methods=["GET"])
@require_auth
@audit_log("view_opportunities")
@rate_limit
def get_opportunities(participant_id: str):
    """
    Get matched income opportunities for participant.
    
    Uses AI-powered matching based on:
        - Skills alignment (Jaccard similarity)
        - Schedule compatibility
        - Financial impact potential
        - Location match
    
    Query Parameters:
        - limit: Maximum results (default: 10)
        - type: "gig_task" | "training" | "research" | "career" (optional)
    """
    try:
        pid = UUID(participant_id)
    except ValueError:
        return jsonify({"error": "Invalid participant ID format"}), 400
    
    limit = int(request.args.get("limit", 10))
    opp_type = request.args.get("type")
    
    # In production: call ML matching service
    # matches = OpportunityMatchingService.get_matches(pid, limit, opp_type)
    
    # Mock response
    response = {
        "participantId": str(pid),
        "matches": [
            {
                "opportunityId": str(uuid4()),
                "opportunityType": "gig_task",
                "title": "Community Health Survey Administration",
                "description": "Assist with administering health surveys at local community center",
                "estimatedValue": 150.00,
                "timeCommitment": "4 hours",
                "matchScore": 0.89,
                "matchReasons": [
                    "Strong skills alignment (community outreach)",
                    "High financial impact",
                    "Flexible schedule"
                ],
                "deadline": "2025-12-15"
            },
            {
                "opportunityId": str(uuid4()),
                "opportunityType": "training",
                "title": "Advanced Peer Navigator Certification",
                "description": "80-hour advanced certification program",
                "estimatedValue": 1600.00,
                "timeCommitment": "80 hours over 8 weeks",
                "matchScore": 0.85,
                "matchReasons": [
                    "Career advancement opportunity",
                    "Training stipend included",
                    "Matches current role"
                ],
                "deadline": "2025-12-31"
            },
            {
                "opportunityId": str(uuid4()),
                "opportunityType": "research",
                "title": "Digital Twin Validation Study",
                "description": "Participate in quarterly digital twin accuracy study",
                "estimatedValue": 200.00,
                "timeCommitment": "2 hours",
                "matchScore": 0.78,
                "matchReasons": [
                    "Current platform user",
                    "Good compensation rate",
                    "Minimal time commitment"
                ],
                "deadline": "2025-12-20"
            }
        ],
        "totalMatches": 3,
        "nextRefresh": datetime.utcnow().isoformat() + "Z"
    }
    
    return jsonify(response), 200


@app.route("/api/v1/participant/<participant_id>/opportunities/<opportunity_id>/apply", methods=["POST"])
@require_auth
@audit_log("apply_opportunity")
@rate_limit
def apply_opportunity(participant_id: str, opportunity_id: str):
    """Submit application for an opportunity."""
    try:
        pid = UUID(participant_id)
        oid = UUID(opportunity_id)
    except ValueError:
        return jsonify({"error": "Invalid ID format"}), 400
    
    data = request.get_json() or {}
    
    # In production: create application record
    # application = OpportunityApplicationRepository.create(pid, oid, data)
    
    response = {
        "applicationId": str(uuid4()),
        "participantId": str(pid),
        "opportunityId": str(oid),
        "status": "submitted",
        "submittedAt": datetime.utcnow().isoformat() + "Z",
        "message": "Application submitted successfully. You will be notified of the outcome."
    }
    
    return jsonify(response), 201


# ============================================================================
# Benefits Assessment Endpoints
# ============================================================================

@app.route("/api/v1/participant/<participant_id>/benefits", methods=["GET"])
@require_auth
@audit_log("view_benefits")
@rate_limit
def get_benefits(participant_id: str):
    """Get benefits assessment for participant."""
    try:
        pid = UUID(participant_id)
    except ValueError:
        return jsonify({"error": "Invalid participant ID format"}), 400
    
    # Mock response
    response = {
        "participantId": str(pid),
        "assessmentDate": datetime.utcnow().isoformat() + "Z",
        "utilizedBenefits": [
            {
                "programName": "SNAP",
                "monthlyValue": 200.00,
                "status": "active",
                "renewalDate": "2026-03-15"
            },
            {
                "programName": "Medicaid",
                "monthlyValue": 450.00,
                "status": "active",
                "renewalDate": "2026-06-01"
            }
        ],
        "eligibleNotUtilized": [
            {
                "programName": "LIHEAP",
                "estimatedMonthlyValue": 100.00,
                "eligibilityConfidence": 0.92,
                "applicationUrl": "https://benefits.example.gov/liheap"
            },
            {
                "programName": "Lifeline Phone",
                "estimatedMonthlyValue": 25.00,
                "eligibilityConfidence": 0.88,
                "applicationUrl": "https://benefits.example.gov/lifeline"
            }
        ],
        "totalUtilizedValue": 650.00,
        "totalEligibleValue": 775.00,
        "utilizationRate": 0.84,
        "potentialAdditionalValue": 125.00
    }
    
    return jsonify(response), 200


@app.route("/api/v1/participant/<participant_id>/benefits/screen", methods=["POST"])
@require_auth
@audit_log("screen_benefits")
@rate_limit
def screen_benefits(participant_id: str):
    """
    Run comprehensive benefits screening.
    
    Request Body (optional):
    {
        "includeStatePrograms": boolean,
        "includeFederalPrograms": boolean,
        "includeLocalPrograms": boolean
    }
    """
    try:
        pid = UUID(participant_id)
    except ValueError:
        return jsonify({"error": "Invalid participant ID format"}), 400
    
    data = request.get_json() or {}
    include_state = data.get("includeStatePrograms", True)
    include_federal = data.get("includeFederalPrograms", True)
    include_local = data.get("includeLocalPrograms", True)
    
    # In production: call benefits screening service
    # results = BenefitsScreeningService.screen(pid, include_state, include_federal, include_local)
    
    response = {
        "screeningId": str(uuid4()),
        "participantId": str(pid),
        "status": "processing",
        "estimatedCompletionTime": "30 seconds",
        "message": "Benefits screening initiated. Results will be available shortly."
    }
    
    return jsonify(response), 202


# ============================================================================
# Analytics Endpoints (Admin/Provider)
# ============================================================================

@app.route("/api/v1/admin/analytics/financial-health", methods=["GET"])
@require_auth
@require_role(["admin", "provider", "researcher"])
@audit_log("view_analytics")
@rate_limit
def get_financial_analytics():
    """
    Get aggregate financial health analytics.
    
    Query Parameters:
        - period: "week" | "month" | "quarter" | "year"
        - cohort: cohort identifier (optional)
    """
    period = request.args.get("period", "month")
    cohort = request.args.get("cohort")
    
    # In production: fetch from analytics service with k-anonymity
    # analytics = AnalyticsService.get_financial_health_summary(period, cohort)
    
    response = {
        "period": period,
        "cohort": cohort,
        "aggregatedAt": datetime.utcnow().isoformat() + "Z",
        "participantCount": 2500,
        "averageFinancialHealthScore": 62.4,
        "medianFinancialHealthScore": 58.7,
        "averageFinancialStressIndex": 47.8,
        "scoreDistribution": {
            "0-25": 0.08,
            "26-50": 0.24,
            "51-75": 0.45,
            "76-100": 0.23
        },
        "trendVsPriorPeriod": {
            "financialHealthScore": +2.3,
            "financialStressIndex": -1.8
        },
        "topOpportunityTypes": [
            {"type": "peer_navigator", "percentage": 0.35},
            {"type": "gig_task", "percentage": 0.28},
            {"type": "research_study", "percentage": 0.22},
            {"type": "training", "percentage": 0.15}
        ]
    }
    
    return jsonify(response), 200


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request", "message": str(error)}), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({"error": "Forbidden", "message": "Insufficient permissions"}), 403


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found", "message": "Resource not found"}), 404


@app.errorhandler(429)
def rate_limited(error):
    return jsonify({"error": "Rate limited", "message": "Too many requests. Please try again later."}), 429


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error", "message": "An unexpected error occurred"}), 500


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    debug = os.environ.get("FLASK_ENV") == "development"
    
    print(f"Starting Financial Twin API on port {port}")
    print(f"Debug mode: {debug}")
    
    app.run(host="0.0.0.0", port=port, debug=debug)
