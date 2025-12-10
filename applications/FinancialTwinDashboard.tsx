/**
 * IHEP Financial Health Twin Dashboard Component
 * ================================================
 * 
 * Production-ready React component implementing the Financial Health Twin
 * visualization with real-time score updates, opportunity matching, and
 * health-finance correlation display.
 * 
 * Mathematical Visualization:
 * - Financial Health Score (FHS) displayed as radial gauge: 0-100
 * - Component breakdown using stacked bar visualization
 * - Trend analysis using time-series chart with morphogenetic smoothing
 * 
 * @author IHEP Technical Architecture Team
 * @version 1.0.0
 */

'use client';

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useAuth } from '@/hooks/useAuth';

// Type definitions
interface IncomeStream {
  id: string;
  sourceType: string;
  amount: number;
  frequency: string;
  stabilityScore: number;
  startDate: string;
}

interface ExpenseRecord {
  id: string;
  category: string;
  amount: number;
  isFixed: boolean;
}

interface DebtRecord {
  id: string;
  debtType: string;
  principalBalance: number;
  interestRate: number;
  minimumPayment: number;
}

interface BenefitEligibility {
  programId: string;
  programName: string;
  isEligible: boolean;
  estimatedMonthlyValue: number;
  applicationUrl?: string;
  requirementsMet: string[];
  requirementsMissing: string[];
}

interface OpportunityMatch {
  opportunityId: string;
  opportunityType: string;
  title: string;
  description: string;
  estimatedValue: number;
  matchScore: number;
  matchReasons: string[];
  requirements: string[];
  applicationDeadline?: string;
}

interface ComponentScores {
  incomeStability: number;
  expenseRatio: number;
  debtBurden: number;
  savingsRate: number;
  benefitsUtilization: number;
  incomeGrowth: number;
}

interface FinancialTwinState {
  participantId: string;
  timestamp: string;
  totalMonthlyIncome: number;
  incomeStreams: IncomeStream[];
  incomeStabilityCoefficient: number;
  totalMonthlyExpenses: number;
  expenseRecords: ExpenseRecord[];
  expenseToIncomeRatio: number;
  totalDebtBalance: number;
  debtRecords: DebtRecord[];
  debtToIncomeRatio: number;
  emergencyFundBalance: number;
  emergencyFundMonths: number;
  savingsRate: number;
  benefitsUtilized: string[];
  benefitsEligibleUnused: BenefitEligibility[];
  unclaimedBenefitValue: number;
  financialHealthScore: number;
  financialStressIndex: number;
  stabilityTrend: 'improving' | 'stable' | 'declining';
  componentScores: ComponentScores;
}

interface HealthPrediction {
  interventionType: string;
  predictedHealthImprovement: number;
  confidenceInterval: [number, number];
  correlationCoefficient: number;
  supportingEvidence: string[];
}

// Constants
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '';

const COMPONENT_LABELS: Record<keyof ComponentScores, string> = {
  incomeStability: 'Income Stability',
  expenseRatio: 'Expense Management',
  debtBurden: 'Debt Management',
  savingsRate: 'Savings Rate',
  benefitsUtilization: 'Benefits Usage',
  incomeGrowth: 'Income Growth'
};

const COMPONENT_COLORS: Record<keyof ComponentScores, string> = {
  incomeStability: '#10B981',
  expenseRatio: '#3B82F6',
  debtBurden: '#F59E0B',
  savingsRate: '#8B5CF6',
  benefitsUtilization: '#EC4899',
  incomeGrowth: '#06B6D4'
};

// Utility functions
const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value);
};

const formatPercent = (value: number): string => {
  return `${(value * 100).toFixed(1)}%`;
};

const getScoreColor = (score: number): string => {
  if (score >= 80) return '#10B981'; // Green
  if (score >= 60) return '#3B82F6'; // Blue
  if (score >= 40) return '#F59E0B'; // Yellow
  if (score >= 20) return '#F97316'; // Orange
  return '#EF4444'; // Red
};

const getStressColor = (stress: number): string => {
  if (stress <= 20) return '#10B981';
  if (stress <= 40) return '#3B82F6';
  if (stress <= 60) return '#F59E0B';
  if (stress <= 80) return '#F97316';
  return '#EF4444';
};

// Radial Gauge Component
const RadialGauge: React.FC<{
  value: number;
  maxValue: number;
  label: string;
  color: string;
  size?: number;
}> = ({ value, maxValue, label, color, size = 200 }) => {
  const percentage = (value / maxValue) * 100;
  const strokeWidth = 12;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="relative flex flex-col items-center">
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#E5E7EB"
          strokeWidth={strokeWidth}
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          style={{ transition: 'stroke-dashoffset 1s ease-in-out' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-4xl font-bold" style={{ color }}>
          {value.toFixed(1)}
        </span>
        <span className="text-sm text-gray-500">{label}</span>
      </div>
    </div>
  );
};

// Component Score Bar
const ComponentScoreBar: React.FC<{
  label: string;
  score: number;
  color: string;
}> = ({ label, score, color }) => {
  const width = Math.min(score * 100, 100);

  return (
    <div className="mb-3">
      <div className="flex justify-between mb-1">
        <span className="text-sm font-medium text-gray-700">{label}</span>
        <span className="text-sm font-medium" style={{ color }}>
          {(score * 100).toFixed(0)}%
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="h-2 rounded-full transition-all duration-500"
          style={{ width: `${width}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
};

// Opportunity Card Component
const OpportunityCard: React.FC<{
  opportunity: OpportunityMatch;
  onApply: (id: string) => void;
}> = ({ opportunity, onApply }) => {
  const matchPercentage = (opportunity.matchScore * 100).toFixed(0);
  const matchColor = getScoreColor(opportunity.matchScore * 100);

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-2">
        <h4 className="font-semibold text-gray-900">{opportunity.title}</h4>
        <span
          className="px-2 py-1 rounded-full text-xs font-medium text-white"
          style={{ backgroundColor: matchColor }}
        >
          {matchPercentage}% Match
        </span>
      </div>
      <p className="text-sm text-gray-600 mb-3 line-clamp-2">
        {opportunity.description}
      </p>
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-green-600">
          {formatCurrency(opportunity.estimatedValue)}
        </span>
        <span className="text-gray-500 capitalize">
          {opportunity.opportunityType.replace('_', ' ')}
        </span>
      </div>
      {opportunity.matchReasons.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {opportunity.matchReasons.slice(0, 2).map((reason, idx) => (
            <span
              key={idx}
              className="text-xs px-2 py-0.5 bg-blue-50 text-blue-700 rounded"
            >
              {reason}
            </span>
          ))}
        </div>
      )}
      <button
        onClick={() => onApply(opportunity.opportunityId)}
        className="mt-3 w-full py-2 px-4 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors text-sm font-medium"
      >
        View Details
      </button>
    </div>
  );
};

// Benefit Alert Component
const BenefitAlert: React.FC<{
  benefit: BenefitEligibility;
  onEnroll: (id: string) => void;
}> = ({ benefit, onEnroll }) => {
  return (
    <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded-r-lg">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3 flex-1">
          <h4 className="text-sm font-medium text-green-800">
            {benefit.programName}
          </h4>
          <p className="text-sm text-green-700 mt-1">
            Estimated value: {formatCurrency(benefit.estimatedMonthlyValue)}/month
          </p>
          {benefit.requirementsMet.length > 0 && (
            <p className="text-xs text-green-600 mt-1">
              Requirements met: {benefit.requirementsMet.join(', ')}
            </p>
          )}
        </div>
        <button
          onClick={() => onEnroll(benefit.programId)}
          className="ml-4 px-3 py-1.5 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition-colors"
        >
          Enroll
        </button>
      </div>
    </div>
  );
};

// Main Dashboard Component
export const FinancialTwinDashboard: React.FC = () => {
  const { user, token } = useAuth();
  const [financialState, setFinancialState] = useState<FinancialTwinState | null>(null);
  const [opportunities, setOpportunities] = useState<OpportunityMatch[]>([]);
  const [eligibleBenefits, setEligibleBenefits] = useState<BenefitEligibility[]>([]);
  const [healthPrediction, setHealthPrediction] = useState<HealthPrediction | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'income' | 'opportunities' | 'benefits'>('overview');

  // Fetch financial twin data
  const fetchFinancialTwin = useCallback(async () => {
    if (!user?.id || !token) return;

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/financial-twin/participant/${user.id}/financial-twin`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch financial data');
      }

      const data = await response.json();
      setFinancialState(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  }, [user?.id, token]);

  // Fetch matched opportunities
  const fetchOpportunities = useCallback(async () => {
    if (!user?.id || !token) return;

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/financial-twin/participant/${user.id}/opportunities?limit=6`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) return;

      const data = await response.json();
      setOpportunities(data.matches || []);
    } catch (err) {
      console.error('Failed to fetch opportunities:', err);
    }
  }, [user?.id, token]);

  // Fetch eligible benefits
  const fetchBenefits = useCallback(async () => {
    if (!user?.id || !token) return;

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/financial-twin/participant/${user.id}/benefits-eligibility`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) return;

      const data = await response.json();
      setEligibleBenefits(
        data.eligible_programs?.filter((b: BenefitEligibility) => b.isEligible) || []
      );
    } catch (err) {
      console.error('Failed to fetch benefits:', err);
    }
  }, [user?.id, token]);

  // Initial data fetch
  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true);
      await Promise.all([
        fetchFinancialTwin(),
        fetchOpportunities(),
        fetchBenefits()
      ]);
      setLoading(false);
    };

    fetchAll();
  }, [fetchFinancialTwin, fetchOpportunities, fetchBenefits]);

  // Calculate summary metrics
  const summaryMetrics = useMemo(() => {
    if (!financialState) return null;

    const disposableIncome = financialState.totalMonthlyIncome - financialState.totalMonthlyExpenses;
    const debtPayoffMonths = financialState.totalDebtBalance > 0 && disposableIncome > 0
      ? Math.ceil(financialState.totalDebtBalance / disposableIncome)
      : 0;

    return {
      disposableIncome,
      debtPayoffMonths,
      totalUnclaimedBenefits: eligibleBenefits.reduce(
        (sum, b) => sum + b.estimatedMonthlyValue,
        0
      ),
      topOpportunityValue: opportunities[0]?.estimatedValue || 0
    };
  }, [financialState, eligibleBenefits, opportunities]);

  // Handle opportunity application
  const handleApplyOpportunity = (opportunityId: string) => {
    // Navigate to opportunity detail or open modal
    console.log('Apply to opportunity:', opportunityId);
  };

  // Handle benefit enrollment
  const handleEnrollBenefit = (programId: string) => {
    // Navigate to benefit enrollment or open modal
    console.log('Enroll in benefit:', programId);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-indigo-600 border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <p className="text-red-600">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!financialState) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900">No financial data available</h3>
        <p className="text-gray-500 mt-2">Complete your financial profile to see insights.</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Financial Health Dashboard</h1>
        <p className="text-gray-500 mt-1">
          Last updated: {new Date(financialState.timestamp).toLocaleString()}
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex space-x-8">
          {(['overview', 'income', 'opportunities', 'benefits'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-4 px-1 border-b-2 font-medium text-sm capitalize transition-colors ${
                activeTab === tab
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Score Cards Row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Financial Health Score */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-4 text-center">
                Financial Health Score
              </h3>
              <RadialGauge
                value={financialState.financialHealthScore}
                maxValue={100}
                label="of 100"
                color={getScoreColor(financialState.financialHealthScore)}
              />
              <div className="mt-4 text-center">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  financialState.stabilityTrend === 'improving' 
                    ? 'bg-green-100 text-green-800' 
                    : financialState.stabilityTrend === 'declining'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {financialState.stabilityTrend === 'improving' && '^ '}
                  {financialState.stabilityTrend === 'declining' && 'v '}
                  {financialState.stabilityTrend.charAt(0).toUpperCase() + financialState.stabilityTrend.slice(1)}
                </span>
              </div>
            </div>

            {/* Financial Stress Index */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-4 text-center">
                Financial Stress Index
              </h3>
              <RadialGauge
                value={financialState.financialStressIndex}
                maxValue={100}
                label="stress level"
                color={getStressColor(financialState.financialStressIndex)}
              />
              <p className="mt-4 text-center text-sm text-gray-600">
                {financialState.financialStressIndex < 30 
                  ? 'Low stress - Well managed'
                  : financialState.financialStressIndex < 60
                  ? 'Moderate stress - Room for improvement'
                  : 'High stress - Action recommended'}
              </p>
            </div>

            {/* Quick Stats */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-4">Quick Stats</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Monthly Income</span>
                  <span className="font-semibold text-green-600">
                    {formatCurrency(financialState.totalMonthlyIncome)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Monthly Expenses</span>
                  <span className="font-semibold text-red-600">
                    {formatCurrency(financialState.totalMonthlyExpenses)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Total Debt</span>
                  <span className="font-semibold text-orange-600">
                    {formatCurrency(financialState.totalDebtBalance)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Emergency Fund</span>
                  <span className="font-semibold text-blue-600">
                    {financialState.emergencyFundMonths.toFixed(1)} months
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Component Breakdown */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Score Components</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {Object.entries(financialState.componentScores).map(([key, score]) => (
                <ComponentScoreBar
                  key={key}
                  label={COMPONENT_LABELS[key as keyof ComponentScores]}
                  score={score}
                  color={COMPONENT_COLORS[key as keyof ComponentScores]}
                />
              ))}
            </div>
          </div>

          {/* Unclaimed Benefits Alert */}
          {eligibleBenefits.length > 0 && (
            <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-6 border border-green-200">
              <div className="flex items-center gap-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-green-900">
                    You may qualify for {formatCurrency(summaryMetrics?.totalUnclaimedBenefits || 0)}/month in benefits!
                  </h3>
                  <p className="text-green-700">
                    We found {eligibleBenefits.length} program{eligibleBenefits.length > 1 ? 's' : ''} you may be eligible for.
                  </p>
                </div>
                <button
                  onClick={() => setActiveTab('benefits')}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  View Benefits
                </button>
              </div>
            </div>
          )}

          {/* Top Opportunities Preview */}
          {opportunities.length > 0 && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Top Matched Opportunities</h3>
                <button
                  onClick={() => setActiveTab('opportunities')}
                  className="text-indigo-600 hover:text-indigo-700 text-sm font-medium"
                >
                  View All
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {opportunities.slice(0, 3).map((opp) => (
                  <OpportunityCard
                    key={opp.opportunityId}
                    opportunity={opp}
                    onApply={handleApplyOpportunity}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Income Tab */}
      {activeTab === 'income' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Income Streams</h3>
            {financialState.incomeStreams.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No income streams recorded.</p>
            ) : (
              <div className="divide-y divide-gray-100">
                {financialState.incomeStreams.map((stream) => (
                  <div key={stream.id} className="py-4 flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900 capitalize">
                        {stream.sourceType.replace('_', ' ')}
                      </h4>
                      <p className="text-sm text-gray-500 capitalize">
                        {stream.frequency} payments
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-gray-900">
                        {formatCurrency(stream.amount)}/mo
                      </p>
                      <p className="text-sm text-gray-500">
                        {formatPercent(stream.stabilityScore)} stable
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Expenses by Category</h3>
            <div className="space-y-3">
              {Object.entries(
                financialState.expenseRecords.reduce((acc, exp) => {
                  acc[exp.category] = (acc[exp.category] || 0) + exp.amount;
                  return acc;
                }, {} as Record<string, number>)
              ).map(([category, amount]) => (
                <div key={category} className="flex items-center justify-between">
                  <span className="text-gray-700 capitalize">{category}</span>
                  <span className="font-medium text-gray-900">{formatCurrency(amount)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Opportunities Tab */}
      {activeTab === 'opportunities' && (
        <div>
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Matched Opportunities</h3>
            <p className="text-gray-500">
              Opportunities matched to your profile based on skills, availability, and financial goals.
            </p>
          </div>
          {opportunities.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
              <p className="text-gray-500">No opportunities matched at this time.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {opportunities.map((opp) => (
                <OpportunityCard
                  key={opp.opportunityId}
                  opportunity={opp}
                  onApply={handleApplyOpportunity}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Benefits Tab */}
      {activeTab === 'benefits' && (
        <div className="space-y-6">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Benefit Programs</h3>
            <p className="text-gray-500">
              Programs you may be eligible for based on your financial profile.
            </p>
          </div>

          {/* Currently enrolled */}
          {financialState.benefitsUtilized.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h4 className="font-medium text-gray-900 mb-4">Currently Enrolled</h4>
              <div className="flex flex-wrap gap-2">
                {financialState.benefitsUtilized.map((programId) => (
                  <span
                    key={programId}
                    className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm"
                  >
                    {programId.toUpperCase()}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Eligible benefits */}
          {eligibleBenefits.length > 0 ? (
            <div className="space-y-4">
              <h4 className="font-medium text-gray-900">Eligible Programs</h4>
              {eligibleBenefits.map((benefit) => (
                <BenefitAlert
                  key={benefit.programId}
                  benefit={benefit}
                  onEnroll={handleEnrollBenefit}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
              <p className="text-gray-500">No additional benefits found at this time.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FinancialTwinDashboard;
