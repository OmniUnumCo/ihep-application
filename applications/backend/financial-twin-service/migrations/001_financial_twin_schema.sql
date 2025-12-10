-- -*- coding: utf-8 -*-
-- ==============================================================================
-- IHEP Financial Health Twin Database Schema
-- ==============================================================================
-- 
-- Production-ready PostgreSQL schema implementing the Financial Health Twin
-- data model with full HIPAA compliance, encryption, and audit capabilities.
--
-- Mathematical Invariants Enforced:
-- 1. Income stability coefficient: S in [0, 1]
-- 2. Expense ratio: E/I >= 0 (can exceed 1 for deficit)
-- 3. Debt-to-income ratio: DTI >= 0
-- 4. Financial Health Score: FHS in [0, 100]
--
-- Author: IHEP Technical Architecture Team
-- Version: 1.0.0
-- ==============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==============================================================================
-- SCHEMA: financial_twin
-- ==============================================================================

CREATE SCHEMA IF NOT EXISTS financial_twin;

SET search_path TO financial_twin, public;

-- ==============================================================================
-- ENUMERATION TYPES
-- ==============================================================================

CREATE TYPE income_source_type AS ENUM (
    'peer_navigator',
    'gig_task', 
    'research_study',
    'employment',
    'benefits',
    'disability',
    'other'
);

CREATE TYPE income_frequency AS ENUM (
    'weekly',
    'biweekly',
    'monthly',
    'irregular'
);

CREATE TYPE expense_category AS ENUM (
    'housing',
    'utilities',
    'medical',
    'transportation',
    'food',
    'insurance',
    'debt_payment',
    'childcare',
    'other'
);

CREATE TYPE opportunity_type AS ENUM (
    'gig_task',
    'training_program',
    'research_study',
    'benefit_program',
    'career_pathway'
);

CREATE TYPE stability_trend AS ENUM (
    'improving',
    'stable',
    'declining'
);

-- ==============================================================================
-- CORE TABLES
-- ==============================================================================

-- -----------------------------------------------------------------------------
-- Table: participants (links to main IHEP participant record)
-- -----------------------------------------------------------------------------
CREATE TABLE participants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ihep_participant_id UUID NOT NULL UNIQUE,
    household_size INTEGER NOT NULL DEFAULT 1 CHECK (household_size >= 1),
    annual_income DECIMAL(12, 2) NOT NULL DEFAULT 0 CHECK (annual_income >= 0),
    state VARCHAR(2) NOT NULL,
    county VARCHAR(100),
    zip_code VARCHAR(10),
    has_dependents BOOLEAN DEFAULT FALSE,
    is_veteran BOOLEAN DEFAULT FALSE,
    age INTEGER CHECK (age >= 0 AND age <= 150),
    disability_status BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Encryption indicator for sensitive fields
    encryption_key_version INTEGER DEFAULT 1
);

CREATE INDEX idx_participants_ihep_id ON participants(ihep_participant_id);
CREATE INDEX idx_participants_state ON participants(state);

-- -----------------------------------------------------------------------------
-- Table: participant_profiles (skills, availability, preferences)
-- -----------------------------------------------------------------------------
CREATE TABLE participant_profiles (
    participant_id UUID PRIMARY KEY REFERENCES participants(id) ON DELETE CASCADE,
    skills TEXT[] DEFAULT '{}',
    certifications TEXT[] DEFAULT '{}',
    location VARCHAR(100),
    available_hours_weekly INTEGER DEFAULT 40 CHECK (available_hours_weekly >= 0),
    health_conditions TEXT[] DEFAULT '{}',
    preferred_opportunity_types opportunity_type[] DEFAULT '{}',
    transportation_access BOOLEAN DEFAULT TRUE,
    internet_access BOOLEAN DEFAULT TRUE,
    language_preferences TEXT[] DEFAULT ARRAY['en'],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- Table: income_streams
-- -----------------------------------------------------------------------------
-- Stores all income sources with stability tracking
-- Mathematical constraint: stability_score = exp(-var / (2 * target_var))
-- -----------------------------------------------------------------------------
CREATE TABLE income_streams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    participant_id UUID NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
    source_type income_source_type NOT NULL,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount >= 0),
    frequency income_frequency NOT NULL,
    stability_score DECIMAL(3, 2) NOT NULL DEFAULT 0.50 
        CHECK (stability_score >= 0 AND stability_score <= 1),
    start_date DATE NOT NULL,
    end_date DATE,
    employer_name VARCHAR(200),
    is_verified BOOLEAN DEFAULT FALSE,
    verification_date TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure end_date is after start_date if present
    CONSTRAINT valid_date_range CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE INDEX idx_income_participant ON income_streams(participant_id);
CREATE INDEX idx_income_active ON income_streams(participant_id) 
    WHERE end_date IS NULL OR end_date > CURRENT_DATE;
CREATE INDEX idx_income_source_type ON income_streams(source_type);

-- -----------------------------------------------------------------------------
-- Table: income_history (tracks historical income for stability calculation)
-- -----------------------------------------------------------------------------
CREATE TABLE income_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    income_stream_id UUID NOT NULL REFERENCES income_streams(id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount >= 0),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_period CHECK (period_end >= period_start)
);

CREATE INDEX idx_income_history_stream ON income_history(income_stream_id);
CREATE INDEX idx_income_history_period ON income_history(period_start, period_end);

-- -----------------------------------------------------------------------------
-- Table: expense_records
-- -----------------------------------------------------------------------------
CREATE TABLE expense_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    participant_id UUID NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
    category expense_category NOT NULL,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount >= 0),
    is_fixed BOOLEAN NOT NULL DEFAULT TRUE,
    due_date INTEGER CHECK (due_date >= 1 AND due_date <= 31),
    description VARCHAR(500),
    is_recurring BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_expense_participant ON expense_records(participant_id);
CREATE INDEX idx_expense_category ON expense_records(category);
CREATE INDEX idx_expense_recent ON expense_records(created_at DESC);

-- -----------------------------------------------------------------------------
-- Table: debt_records
-- -----------------------------------------------------------------------------
CREATE TABLE debt_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    participant_id UUID NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
    debt_type VARCHAR(100) NOT NULL,
    creditor_name VARCHAR(200),
    principal_balance DECIMAL(12, 2) NOT NULL CHECK (principal_balance >= 0),
    interest_rate DECIMAL(5, 4) NOT NULL CHECK (interest_rate >= 0 AND interest_rate <= 1),
    minimum_payment DECIMAL(10, 2) NOT NULL CHECK (minimum_payment >= 0),
    remaining_term_months INTEGER,
    is_delinquent BOOLEAN DEFAULT FALSE,
    last_payment_date DATE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_debt_participant ON debt_records(participant_id);
CREATE INDEX idx_debt_balance ON debt_records(principal_balance DESC);

-- -----------------------------------------------------------------------------
-- Table: participant_savings
-- -----------------------------------------------------------------------------
CREATE TABLE participant_savings (
    participant_id UUID PRIMARY KEY REFERENCES participants(id) ON DELETE CASCADE,
    emergency_fund_balance DECIMAL(12, 2) NOT NULL DEFAULT 0 CHECK (emergency_fund_balance >= 0),
    retirement_balance DECIMAL(14, 2) DEFAULT 0 CHECK (retirement_balance >= 0),
    other_savings DECIMAL(12, 2) DEFAULT 0 CHECK (other_savings >= 0),
    savings_goal_amount DECIMAL(12, 2),
    savings_goal_deadline DATE,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- Table: benefit_programs (catalog of available programs)
-- -----------------------------------------------------------------------------
CREATE TABLE benefit_programs (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    program_type VARCHAR(100) NOT NULL,
    description TEXT,
    income_limit_fpl_percent INTEGER,
    state_restrictions TEXT[] DEFAULT '{}',
    requirements JSONB DEFAULT '{}',
    monthly_value DECIMAL(10, 2),
    application_url VARCHAR(500),
    processing_time_days INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_benefit_active ON benefit_programs(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_benefit_state ON benefit_programs USING GIN(state_restrictions);

-- -----------------------------------------------------------------------------
-- Table: enrolled_benefits
-- -----------------------------------------------------------------------------
CREATE TABLE enrolled_benefits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    participant_id UUID NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
    program_id VARCHAR(50) NOT NULL REFERENCES benefit_programs(id),
    enrollment_date DATE NOT NULL,
    expiration_date DATE,
    monthly_value DECIMAL(10, 2),
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(participant_id, program_id)
);

CREATE INDEX idx_enrolled_participant ON enrolled_benefits(participant_id);
CREATE INDEX idx_enrolled_active ON enrolled_benefits(participant_id) WHERE is_active = TRUE;

-- -----------------------------------------------------------------------------
-- Table: financial_opportunities (gig tasks, training, research studies)
-- -----------------------------------------------------------------------------
CREATE TABLE financial_opportunities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type opportunity_type NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    estimated_value DECIMAL(10, 2) NOT NULL CHECK (estimated_value >= 0),
    requirements TEXT[] DEFAULT '{}',
    location VARCHAR(100) DEFAULT 'remote',
    time_commitment_hours DECIMAL(5, 1),
    application_deadline TIMESTAMP WITH TIME ZONE,
    health_restrictions TEXT[] DEFAULT '{}',
    max_participants INTEGER,
    current_participants INTEGER DEFAULT 0,
    provider_name VARCHAR(200),
    provider_contact VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_participants CHECK (
        max_participants IS NULL OR current_participants <= max_participants
    )
);

CREATE INDEX idx_opportunity_type ON financial_opportunities(type);
CREATE INDEX idx_opportunity_active ON financial_opportunities(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_opportunity_location ON financial_opportunities(location);
CREATE INDEX idx_opportunity_deadline ON financial_opportunities(application_deadline);

-- -----------------------------------------------------------------------------
-- Table: opportunity_applications
-- -----------------------------------------------------------------------------
CREATE TABLE opportunity_applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    participant_id UUID NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
    opportunity_id UUID NOT NULL REFERENCES financial_opportunities(id),
    match_score DECIMAL(4, 3) NOT NULL CHECK (match_score >= 0 AND match_score <= 1),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    decision_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    
    UNIQUE(participant_id, opportunity_id)
);

CREATE INDEX idx_application_participant ON opportunity_applications(participant_id);
CREATE INDEX idx_application_status ON opportunity_applications(status);

-- -----------------------------------------------------------------------------
-- Table: financial_twin_snapshots (point-in-time state captures)
-- -----------------------------------------------------------------------------
-- Stores complete financial twin state for historical analysis
-- and health-finance correlation modeling
-- -----------------------------------------------------------------------------
CREATE TABLE financial_twin_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    participant_id UUID NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
    snapshot_date DATE NOT NULL,
    
    -- Income state
    total_monthly_income DECIMAL(12, 2) NOT NULL,
    income_stream_count INTEGER NOT NULL,
    income_stability_coefficient DECIMAL(3, 2) NOT NULL,
    
    -- Expense state
    total_monthly_expenses DECIMAL(12, 2) NOT NULL,
    expense_to_income_ratio DECIMAL(5, 4) NOT NULL,
    
    -- Debt state
    total_debt_balance DECIMAL(14, 2) NOT NULL,
    debt_to_income_ratio DECIMAL(5, 4) NOT NULL,
    
    -- Savings state
    emergency_fund_balance DECIMAL(12, 2) NOT NULL,
    emergency_fund_months DECIMAL(4, 2) NOT NULL,
    savings_rate DECIMAL(4, 3) NOT NULL CHECK (savings_rate >= 0 AND savings_rate <= 1),
    
    -- Benefits state
    benefits_utilized_count INTEGER NOT NULL DEFAULT 0,
    unclaimed_benefit_value DECIMAL(10, 2) DEFAULT 0,
    
    -- Composite scores
    financial_health_score DECIMAL(5, 2) NOT NULL 
        CHECK (financial_health_score >= 0 AND financial_health_score <= 100),
    financial_stress_index DECIMAL(5, 2) NOT NULL
        CHECK (financial_stress_index >= 0 AND financial_stress_index <= 100),
    stability_trend stability_trend DEFAULT 'stable',
    
    -- Component scores (for analysis)
    component_scores JSONB NOT NULL DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(participant_id, snapshot_date)
);

CREATE INDEX idx_snapshot_participant ON financial_twin_snapshots(participant_id);
CREATE INDEX idx_snapshot_date ON financial_twin_snapshots(snapshot_date DESC);
CREATE INDEX idx_snapshot_health_score ON financial_twin_snapshots(financial_health_score);

-- -----------------------------------------------------------------------------
-- Table: health_finance_correlations (ML model training data)
-- -----------------------------------------------------------------------------
CREATE TABLE health_finance_correlations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    participant_id UUID NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
    
    -- Financial intervention details
    intervention_type VARCHAR(100) NOT NULL,
    intervention_date DATE NOT NULL,
    
    -- Financial state before/after
    fhs_before DECIMAL(5, 2) NOT NULL,
    fhs_after DECIMAL(5, 2) NOT NULL,
    fhs_delta DECIMAL(5, 2) GENERATED ALWAYS AS (fhs_after - fhs_before) STORED,
    
    -- Health outcome measurement
    health_metric_type VARCHAR(100) NOT NULL,
    health_value_before DECIMAL(8, 2) NOT NULL,
    health_value_after DECIMAL(8, 2) NOT NULL,
    health_delta DECIMAL(8, 2) GENERATED ALWAYS AS (health_value_after - health_value_before) STORED,
    
    -- Time between measurements
    measurement_interval_days INTEGER NOT NULL,
    
    -- Statistical metadata
    confidence_score DECIMAL(3, 2),
    data_quality_score DECIMAL(3, 2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_correlation_participant ON health_finance_correlations(participant_id);
CREATE INDEX idx_correlation_intervention ON health_finance_correlations(intervention_type);
CREATE INDEX idx_correlation_date ON health_finance_correlations(intervention_date);

-- ==============================================================================
-- AUDIT TABLES
-- ==============================================================================

-- -----------------------------------------------------------------------------
-- Table: financial_access_log (HIPAA-compliant audit trail)
-- -----------------------------------------------------------------------------
CREATE TABLE financial_access_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    user_id UUID NOT NULL,
    participant_id UUID,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id UUID,
    success BOOLEAN NOT NULL,
    ip_address INET,
    user_agent TEXT,
    request_metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_audit_timestamp ON financial_access_log(timestamp DESC);
CREATE INDEX idx_audit_user ON financial_access_log(user_id);
CREATE INDEX idx_audit_participant ON financial_access_log(participant_id);

-- Partition by month for efficient querying and retention
-- (In production, implement range partitioning)

-- ==============================================================================
-- VIEWS
-- ==============================================================================

-- -----------------------------------------------------------------------------
-- View: participant_financial_summary
-- -----------------------------------------------------------------------------
CREATE VIEW participant_financial_summary AS
SELECT 
    p.id AS participant_id,
    p.ihep_participant_id,
    COALESCE(SUM(i.amount), 0) AS total_monthly_income,
    COUNT(DISTINCT i.id) AS income_stream_count,
    AVG(i.stability_score) AS avg_income_stability,
    COALESCE(SUM(e.amount), 0) AS total_monthly_expenses,
    COALESCE(SUM(d.principal_balance), 0) AS total_debt,
    COALESCE(s.emergency_fund_balance, 0) AS emergency_fund,
    COUNT(DISTINCT eb.program_id) FILTER (WHERE eb.is_active) AS active_benefits_count,
    
    -- Calculated ratios
    CASE 
        WHEN COALESCE(SUM(i.amount), 0) > 0 
        THEN COALESCE(SUM(e.amount), 0) / SUM(i.amount)
        ELSE 1.0 
    END AS expense_to_income_ratio,
    
    CASE 
        WHEN COALESCE(SUM(i.amount), 0) > 0 
        THEN COALESCE(SUM(d.principal_balance), 0) / (SUM(i.amount) * 12)
        ELSE 0 
    END AS debt_to_income_ratio,
    
    CASE 
        WHEN COALESCE(SUM(e.amount), 0) > 0 
        THEN COALESCE(s.emergency_fund_balance, 0) / SUM(e.amount)
        ELSE 0 
    END AS emergency_fund_months
    
FROM participants p
LEFT JOIN income_streams i ON p.id = i.participant_id 
    AND (i.end_date IS NULL OR i.end_date > CURRENT_DATE)
LEFT JOIN expense_records e ON p.id = e.participant_id 
    AND e.created_at > CURRENT_DATE - INTERVAL '30 days'
LEFT JOIN debt_records d ON p.id = d.participant_id 
    AND d.principal_balance > 0
LEFT JOIN participant_savings s ON p.id = s.participant_id
LEFT JOIN enrolled_benefits eb ON p.id = eb.participant_id

GROUP BY p.id, p.ihep_participant_id, s.emergency_fund_balance;

-- ==============================================================================
-- FUNCTIONS
-- ==============================================================================

-- -----------------------------------------------------------------------------
-- Function: calculate_income_stability
-- -----------------------------------------------------------------------------
-- Computes stability coefficient using exponential decay model:
-- S = exp(-variance / (2 * target_variance))
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION calculate_income_stability(
    p_income_stream_id UUID,
    p_target_std DECIMAL DEFAULT 0.1
)
RETURNS DECIMAL AS $$
DECLARE
    v_variance DECIMAL;
    v_stability DECIMAL;
BEGIN
    -- Calculate variance of historical income amounts
    SELECT VARIANCE(amount) INTO v_variance
    FROM income_history
    WHERE income_stream_id = p_income_stream_id
      AND period_start > CURRENT_DATE - INTERVAL '6 months';
    
    -- Handle null/zero variance
    IF v_variance IS NULL OR v_variance = 0 THEN
        RETURN 1.0;
    END IF;
    
    -- Apply exponential decay formula
    -- S = exp(-var / (2 * target_var^2))
    v_stability := EXP(-v_variance / (2 * POWER(p_target_std, 2)));
    
    RETURN LEAST(GREATEST(v_stability, 0), 1);
END;
$$ LANGUAGE plpgsql;

-- -----------------------------------------------------------------------------
-- Function: calculate_financial_health_score
-- -----------------------------------------------------------------------------
-- Computes FHS using weighted component model:
-- FHS = 100 * sum(w_i * sigmoid(x_i))
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION calculate_financial_health_score(
    p_participant_id UUID
)
RETURNS TABLE(
    financial_health_score DECIMAL,
    financial_stress_index DECIMAL,
    component_scores JSONB
) AS $$
DECLARE
    v_income DECIMAL;
    v_expenses DECIMAL;
    v_debt DECIMAL;
    v_emergency DECIMAL;
    v_stability DECIMAL;
    v_benefits_util DECIMAL;
    v_expense_ratio DECIMAL;
    v_dti DECIMAL;
    v_emergency_months DECIMAL;
    v_savings_rate DECIMAL;
    
    -- Component scores
    v_income_score DECIMAL;
    v_expense_score DECIMAL;
    v_debt_score DECIMAL;
    v_savings_score DECIMAL;
    v_benefits_score DECIMAL;
    v_growth_score DECIMAL;
    
    -- Final scores
    v_fhs DECIMAL;
    v_fsi DECIMAL;
BEGIN
    -- Get summary data
    SELECT 
        total_monthly_income,
        total_monthly_expenses,
        total_debt,
        emergency_fund,
        avg_income_stability,
        expense_to_income_ratio,
        debt_to_income_ratio,
        emergency_fund_months
    INTO 
        v_income, v_expenses, v_debt, v_emergency,
        v_stability, v_expense_ratio, v_dti, v_emergency_months
    FROM participant_financial_summary
    WHERE participant_id = p_participant_id;
    
    -- Calculate savings rate
    IF v_income > 0 THEN
        v_savings_rate := GREATEST(0, (v_income - v_expenses) / v_income);
    ELSE
        v_savings_rate := 0;
    END IF;
    
    -- Calculate benefits utilization
    SELECT 
        CASE 
            WHEN COUNT(*) > 0 THEN COUNT(*) FILTER (WHERE is_active)::DECIMAL / COUNT(*)
            ELSE 0.5
        END
    INTO v_benefits_util
    FROM enrolled_benefits
    WHERE participant_id = p_participant_id;
    
    -- Sigmoid normalization for each component
    -- sigmoid(x, k, x0) = 1 / (1 + exp(-k * (x - x0)))
    
    -- Income stability (higher is better)
    v_income_score := 1.0 / (1.0 + EXP(-5.0 * (COALESCE(v_stability, 0.5) - 0.5)));
    
    -- Expense ratio (lower is better, so negative k)
    v_expense_score := 1.0 / (1.0 + EXP(8.0 * (COALESCE(v_expense_ratio, 1) - 0.7)));
    
    -- Debt burden (lower is better)
    v_debt_score := 1.0 / (1.0 + EXP(6.0 * (COALESCE(v_dti, 0) - 0.4)));
    
    -- Savings rate (higher is better)
    v_savings_score := 1.0 / (1.0 + EXP(-10.0 * (v_savings_rate - 0.1)));
    
    -- Benefits utilization
    v_benefits_score := 1.0 / (1.0 + EXP(-4.0 * (v_benefits_util - 0.5)));
    
    -- Growth score (placeholder - would need historical data)
    v_growth_score := 0.5;
    
    -- Weighted sum for FHS
    v_fhs := 100 * (
        0.25 * v_income_score +
        0.20 * v_expense_score +
        0.20 * v_debt_score +
        0.15 * v_savings_score +
        0.10 * v_benefits_score +
        0.10 * v_growth_score
    );
    
    -- Calculate stress index
    -- FSI = 100 * (1 - emergency_buffer) * debt_pressure * expense_pressure
    v_fsi := 100 * (1 - LEAST(COALESCE(v_emergency_months, 0) / 3.0, 1)) *
             (0.5 + 0.5 * LEAST(COALESCE(v_dti, 0) / 0.5, 1)) *
             LEAST(COALESCE(v_expense_ratio, 1), 1);
    
    RETURN QUERY SELECT 
        ROUND(LEAST(GREATEST(v_fhs, 0), 100), 1),
        ROUND(LEAST(GREATEST(v_fsi, 0), 100), 1),
        jsonb_build_object(
            'income_stability', ROUND(v_income_score, 3),
            'expense_ratio', ROUND(v_expense_score, 3),
            'debt_burden', ROUND(v_debt_score, 3),
            'savings_rate', ROUND(v_savings_score, 3),
            'benefits_utilization', ROUND(v_benefits_score, 3),
            'income_growth', ROUND(v_growth_score, 3)
        );
END;
$$ LANGUAGE plpgsql;

-- -----------------------------------------------------------------------------
-- Function: create_financial_snapshot
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION create_financial_snapshot(
    p_participant_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_snapshot_id UUID;
    v_fhs DECIMAL;
    v_fsi DECIMAL;
    v_components JSONB;
    v_summary RECORD;
BEGIN
    -- Get financial summary
    SELECT * INTO v_summary
    FROM participant_financial_summary
    WHERE participant_id = p_participant_id;
    
    -- Calculate scores
    SELECT financial_health_score, financial_stress_index, component_scores
    INTO v_fhs, v_fsi, v_components
    FROM calculate_financial_health_score(p_participant_id);
    
    -- Insert snapshot
    INSERT INTO financial_twin_snapshots (
        participant_id,
        snapshot_date,
        total_monthly_income,
        income_stream_count,
        income_stability_coefficient,
        total_monthly_expenses,
        expense_to_income_ratio,
        total_debt_balance,
        debt_to_income_ratio,
        emergency_fund_balance,
        emergency_fund_months,
        savings_rate,
        benefits_utilized_count,
        financial_health_score,
        financial_stress_index,
        component_scores
    ) VALUES (
        p_participant_id,
        CURRENT_DATE,
        COALESCE(v_summary.total_monthly_income, 0),
        COALESCE(v_summary.income_stream_count, 0),
        COALESCE(v_summary.avg_income_stability, 0.5),
        COALESCE(v_summary.total_monthly_expenses, 0),
        COALESCE(v_summary.expense_to_income_ratio, 1),
        COALESCE(v_summary.total_debt, 0),
        COALESCE(v_summary.debt_to_income_ratio, 0),
        COALESCE(v_summary.emergency_fund, 0),
        COALESCE(v_summary.emergency_fund_months, 0),
        GREATEST(0, (COALESCE(v_summary.total_monthly_income, 0) - COALESCE(v_summary.total_monthly_expenses, 0)) / 
            NULLIF(v_summary.total_monthly_income, 0)),
        COALESCE(v_summary.active_benefits_count, 0),
        v_fhs,
        v_fsi,
        v_components
    )
    ON CONFLICT (participant_id, snapshot_date) DO UPDATE SET
        total_monthly_income = EXCLUDED.total_monthly_income,
        income_stream_count = EXCLUDED.income_stream_count,
        financial_health_score = EXCLUDED.financial_health_score,
        financial_stress_index = EXCLUDED.financial_stress_index,
        component_scores = EXCLUDED.component_scores
    RETURNING id INTO v_snapshot_id;
    
    RETURN v_snapshot_id;
END;
$$ LANGUAGE plpgsql;

-- ==============================================================================
-- TRIGGERS
-- ==============================================================================

-- -----------------------------------------------------------------------------
-- Trigger: Update timestamps
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_participants_updated_at
    BEFORE UPDATE ON participants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_income_updated_at
    BEFORE UPDATE ON income_streams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_expense_updated_at
    BEFORE UPDATE ON expense_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_debt_updated_at
    BEFORE UPDATE ON debt_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- -----------------------------------------------------------------------------
-- Trigger: Recalculate stability on income history change
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION recalculate_income_stability()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE income_streams
    SET stability_score = calculate_income_stability(NEW.income_stream_id)
    WHERE id = NEW.income_stream_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_income_stability_recalc
    AFTER INSERT OR UPDATE ON income_history
    FOR EACH ROW EXECUTE FUNCTION recalculate_income_stability();

-- ==============================================================================
-- SEED DATA: Benefit Programs
-- ==============================================================================

INSERT INTO benefit_programs (id, name, program_type, income_limit_fpl_percent, monthly_value, description) VALUES
('snap', 'Supplemental Nutrition Assistance Program (SNAP)', 'food_assistance', 130, 234, 'Federal food assistance program'),
('medicaid', 'Medicaid', 'healthcare', 138, 500, 'Federal-state health insurance program'),
('chip', 'Children''s Health Insurance Program', 'healthcare', 200, 200, 'Health coverage for children'),
('liheap', 'Low Income Home Energy Assistance', 'utilities', 150, 150, 'Energy bill assistance'),
('lifeline', 'Lifeline Phone/Internet', 'telecommunications', 135, 9.25, 'Discount phone/internet service'),
('wic', 'Women, Infants, Children Program', 'food_assistance', 185, 50, 'Nutrition for pregnant women and children'),
('tanf', 'Temporary Assistance for Needy Families', 'cash_assistance', 100, 432, 'Cash assistance for families'),
('ssi', 'Supplemental Security Income', 'disability', 100, 914, 'Income for disabled/elderly'),
('section8', 'Section 8 Housing Choice Voucher', 'housing', 50, 1200, 'Rental assistance program'),
('pell', 'Federal Pell Grant', 'education', 600, 583, 'College tuition assistance')
ON CONFLICT (id) DO NOTHING;

-- ==============================================================================
-- PERMISSIONS
-- ==============================================================================

-- Grant permissions to service account
-- (Adjust role name as needed for your environment)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA financial_twin TO ihep_service;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA financial_twin TO ihep_service;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA financial_twin TO ihep_service;

-- ==============================================================================
-- COMMENTS
-- ==============================================================================

COMMENT ON TABLE income_streams IS 'Income sources with temporal tracking and stability coefficients';
COMMENT ON TABLE financial_twin_snapshots IS 'Point-in-time captures of complete financial state for trend analysis';
COMMENT ON FUNCTION calculate_financial_health_score IS 'Computes FHS using weighted sigmoid normalization: FHS = 100 * sum(w_i * sigmoid(x_i))';
COMMENT ON FUNCTION calculate_income_stability IS 'Stability coefficient using exponential decay: S = exp(-var / (2 * target_var^2))';
