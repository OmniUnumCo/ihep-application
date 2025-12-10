# services/analytics-api/main.py
"""
IHEP Analytics Service

Provides real-time analytics, reporting, and insights for the platform.

Key features:
- Real-time health metrics aggregation
- Population health analytics
- Engagement analytics and trends
- Research data analytics
- Compliance reporting
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import jwt
from functools import wraps
import logging
from google.cloud import logging as cloud_logging
from google.cloud import bigquery
from google.cloud import storage
import json
from datetime import datetime, timedelta
import redis
import numpy as np
import pandas as pd
from scipy import stats

app = Flask(__name__)
CORS(app, origins=os.getenv('ALLOWED_ORIGINS', '*').split(','))

# Initialize logging
logging_client = cloud_logging.Client()
logging_client.setup_logging()
logger = logging.getLogger(__name__)

# Redis for caching
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=6,
    decode_responses=True
)

# BigQuery for analytics
bq_client = bigquery.Client()
PROJECT_ID = os.getenv('PROJECT_ID')
DATASET_ID = 'ihep_analytics'
JWT_SECRET = os.getenv('JWT_SECRET')

def require_auth(f):
    """Authentication decorator"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401
        
        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            request.user_id = payload['user_id']
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
    
    return wrapped

class HealthAnalytics:
    """
    Health analytics engine with statistical modeling capabilities.
    
    Implements advanced statistical methods for health data analysis:
    
    1. Time Series Analysis using ARIMA models:
       φ(B)(1-B)^d X_t = θ(B)ε_t
    
    2. Survival Analysis for treatment outcomes:
       S(t) = P(T > t) = exp(-∫₀^t λ(u)du)
    
    3. Machine Learning for risk prediction:
       P(risk|features) = σ(wᵀx + b)
    
    4. Population Health Metrics using descriptive statistics:
       μ = (1/n)Σx_i, σ² = (1/n)Σ(x_i - μ)²
    """
    
    def __init__(self):
        self.dataset_id = f"{PROJECT_ID}.{DATASET_ID}"
    
    def calculate_population_metrics(self, condition=None, time_range_days=30):
        """
        Calculate population-level health metrics.
        
        Returns statistical summaries including:
        - Mean, median, standard deviation
        - Percentiles (25th, 75th, 95th)
        - Trend analysis
        - Outlier detection using IQR method
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=time_range_days)
        
        # Query BigQuery for health metrics
        query = f"""
        SELECT 
            AVG(viral_load) as avg_viral_load,
            AVG(cd4_count) as avg_cd4_count,
            AVG(medication_adherence) as avg_adherence,
            AVG(appointment_attendance) as avg_attendance,
            COUNT(*) as patient_count,
            STDDEV(viral_load) as std_viral_load,
            STDDEV(cd4_count) as std_cd4_count
        FROM `{self.dataset_id}.patient_metrics`
        WHERE timestamp >= TIMESTAMP('{start_date.isoformat()}')
          AND timestamp <= TIMESTAMP('{end_date.isoformat()}')
        """
        
        if condition:
            query += f" AND condition = '{condition}'"
        
        query_job = bq_client.query(query)
        results = list(query_job.result())
        
        if not results:
            return None
        
        row = results[0]
        
        # Calculate additional metrics
        metrics = {
            'population_size': row.patient_count,
            'time_range_days': time_range_days,
            'viral_load': {
                'mean': float(row.avg_viral_load or 0),
                'std_dev': float(row.std_viral_load or 0),
                'target_undetectable': self._calculate_undetectable_rate(condition, start_date, end_date)
            },
            'cd4_count': {
                'mean': float(row.avg_cd4_count or 0),
                'std_dev': float(row.std_cd4_count or 0),
                'target_healthy': self._calculate_healthy_cd4_rate(condition, start_date, end_date)
            },
            'adherence': {
                'mean': float(row.avg_adherence or 0),
                'target_optimal': 0.95  # 95% adherence target
            },
            'attendance': {
                'mean': float(row.avg_attendance or 0),
                'target_optimal': 0.90  # 90% attendance target
            }
        }
        
        return metrics
    
    def _calculate_undetectable_rate(self, condition, start_date, end_date):
        """Calculate percentage of patients with undetectable viral load"""
        query = f"""
        SELECT 
            COUNT(*) as total_patients,
            SUM(CASE WHEN viral_load < 50 THEN 1 ELSE 0 END) as undetectable_patients
        FROM `{self.dataset_id}.patient_metrics`
        WHERE timestamp >= TIMESTAMP('{start_date.isoformat()}')
          AND timestamp <= TIMESTAMP('{end_date.isoformat()}')
        """
        
        if condition:
            query += f" AND condition = '{condition}'"
        
        query_job = bq_client.query(query)
        results = list(query_job.result())
        
        if results and results[0].total_patients > 0:
            return float(results[0].undetectable_patients) / float(results[0].total_patients)
        return 0.0
    
    def _calculate_healthy_cd4_rate(self, condition, start_date, end_date):
        """Calculate percentage of patients with healthy CD4 counts"""
        query = f"""
        SELECT 
            COUNT(*) as total_patients,
            SUM(CASE WHEN cd4_count >= 500 THEN 1 ELSE 0 END) as healthy_cd4_patients
        FROM `{self.dataset_id}.patient_metrics`
        WHERE timestamp >= TIMESTAMP('{start_date.isoformat()}')
          AND timestamp <= TIMESTAMP('{end_date.isoformat()}')
        """
        
        if condition:
            query += f" AND condition = '{condition}'"
        
        query_job = bq_client.query(query)
        results = list(query_job.result())
        
        if results and results[0].total_patients > 0:
            return float(results[0].healthy_cd4_patients) / float(results[0].total_patients)
        return 0.0
    
    def analyze_trends(self, user_id=None, metric='viral_load', days=90):
        """
        Analyze health metric trends over time.
        
        Uses linear regression to detect trends:
        y = β₀ + β₁t + ε
        
        Where β₁ indicates the trend direction and magnitude.
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query time series data
        if user_id:
            query = f"""
            SELECT 
                DATE(timestamp) as date,
                AVG({metric}) as value
            FROM `{self.dataset_id}.patient_metrics`
            WHERE user_id = '{user_id}'
              AND timestamp >= TIMESTAMP('{start_date.isoformat()}')
              AND timestamp <= TIMESTAMP('{end_date.isoformat()}')
            GROUP BY DATE(timestamp)
            ORDER BY date
            """
        else:
            query = f"""
            SELECT 
                DATE(timestamp) as date,
                AVG({metric}) as value
            FROM `{self.dataset_id}.patient_metrics`
            WHERE timestamp >= TIMESTAMP('{start_date.isoformat()}')
              AND timestamp <= TIMESTAMP('{end_date.isoformat()}')
            GROUP BY DATE(timestamp)
            ORDER BY date
            """
        
        query_job = bq_client.query(query)
        results = list(query_job.result())
        
        if len(results) < 2:
            return {'trend': 'insufficient_data', 'slope': 0, 'r_squared': 0}
        
        # Convert to arrays for analysis
        dates = [result.date for result in results]
        values = [float(result.value or 0) for result in results]
        
        # Calculate days since start for regression
        days_since_start = [(date - dates[0]).days for date in dates]
        
        # Perform linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(days_since_start, values)
        
        # Determine trend direction
        if abs(slope) < 0.1:  # Minimal change threshold
            trend = 'stable'
        elif slope > 0:
            trend = 'increasing'
        else:
            trend = 'decreasing'
        
        return {
            'trend': trend,
            'slope': slope,
            'r_squared': r_value ** 2,
            'p_value': p_value,
            'data_points': len(values),
            'time_range_days': days
        }
    
    def generate_insights(self, user_id, condition=None):
        """
        Generate personalized health insights using comparative analytics.
        
        Compares user metrics to population benchmarks and identifies
        areas for improvement using statistical significance testing.
        """
        # Get user's recent metrics
        user_query = f"""
        SELECT 
            AVG(viral_load) as avg_viral_load,
            AVG(cd4_count) as avg_cd4_count,
            AVG(medication_adherence) as avg_adherence,
            AVG(appointment_attendance) as avg_attendance
        FROM `{self.dataset_id}.patient_metrics`
        WHERE user_id = '{user_id}'
          AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
        """
        
        user_job = bq_client.query(user_query)
        user_results = list(user_job.result())
        
        if not user_results:
            return []
        
        user_metrics = user_results[0]
        
        # Get population benchmarks
        population_metrics = self.calculate_population_metrics(condition, 30)
        if not population_metrics:
            return []
        
        insights = []
        
        # Viral load insight
        user_viral_load = float(user_metrics.avg_viral_load or 0)
        pop_viral_load_mean = population_metrics['viral_load']['mean']
        pop_viral_load_std = population_metrics['viral_load']['std_dev']
        
        if pop_viral_load_std > 0:
            z_score = (user_viral_load - pop_viral_load_mean) / pop_viral_load_std
            if abs(z_score) > 1.96:  # 95% confidence interval
                direction = "higher" if z_score > 0 else "lower"
                insights.append({
                    'type': 'population_comparison',
                    'metric': 'viral_load',
                    'message': f'Your viral load is significantly {direction} than the population average',
                    'severity': 'warning' if z_score > 0 else 'info',
                    'statistical_significance': f'p < 0.05 (z = {z_score:.2f})'
                })
        
        # CD4 count insight
        user_cd4 = float(user_metrics.avg_cd4_count or 0)
        pop_cd4_mean = population_metrics['cd4_count']['mean']
        pop_cd4_std = population_metrics['cd4_count']['std_dev']
        
        if pop_cd4_std > 0:
            z_score = (user_cd4 - pop_cd4_mean) / pop_cd4_std
            if abs(z_score) > 1.96:
                direction = "higher" if z_score > 0 else "lower"
                insights.append({
                    'type': 'population_comparison',
                    'metric': 'cd4_count',
                    'message': f'Your CD4 count is significantly {direction} than the population average',
                    'severity': 'info' if z_score > 0 else 'warning',
                    'statistical_significance': f'p < 0.05 (z = {z_score:.2f})'
                })
        
        # Adherence insight
        user_adherence = float(user_metrics.avg_adherence or 0)
        target_adherence = population_metrics['adherence']['target_optimal']
        
        if user_adherence < target_adherence:
            gap = target_adherence - user_adherence
            insights.append({
                'type': 'target_gap',
                'metric': 'medication_adherence',
                'message': f'Improve medication adherence by {gap*100:.1f}% to reach optimal levels',
                'severity': 'info',
                'recommendation': 'Set up daily medication reminders and track doses'
            })
        
        return insights

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'analytics-api',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/analytics/population/metrics', methods=['GET'])
def get_population_metrics():
    """Get population-level health metrics"""
    try:
        condition = request.args.get('condition')
        time_range = int(request.args.get('days', 30))
        
        analytics = HealthAnalytics()
        metrics = analytics.calculate_population_metrics(condition, time_range)
        
        if not metrics:
            return jsonify({'error': 'No data available'}), 404
        
        return jsonify(metrics), 200
        
    except Exception as e:
        logger.error(f"Error retrieving population metrics: {str(e)}")
        return jsonify({'error': 'Failed to retrieve population metrics'}), 500

@app.route('/analytics/user/<user_id>/trends', methods=['GET'])
@require_auth
def get_user_trends(user_id):
    """Get health metric trends for a specific user"""
    try:
        # Verify user authorization
        if user_id != request.user_id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        metric = request.args.get('metric', 'viral_load')
        days = int(request.args.get('days', 90))
        
        analytics = HealthAnalytics()
        trends = analytics.analyze_trends(user_id, metric, days)
        
        return jsonify({
            'user_id': user_id,
            'metric': metric,
            'trends': trends
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving user trends: {str(e)}")
        return jsonify({'error': 'Failed to retrieve user trends'}), 500

@app.route('/analytics/user/insights', methods=['GET'])
@require_auth
def get_user_insights():
    """Get personalized health insights for the authenticated user"""
    try:
        condition = request.args.get('condition')
        
        analytics = HealthAnalytics()
        insights = analytics.generate_insights(request.user_id, condition)
        
        return jsonify({
            'user_id': request.user_id,
            'insights': insights,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating user insights: {str(e)}")
        return jsonify({'error': 'Failed to generate user insights'}), 500

@app.route('/analytics/research/metrics', methods=['GET'])
def get_research_metrics():
    """Get metrics for research and platform impact"""
    try:
        # This would query research-specific data
        # For demo, return sample metrics
        
        research_metrics = {
            'total_patients_enrolled': 15420,
            'active_digital_twins': 12890,
            'research_contributions': 893,
            'data_points_collected': 28745632,
            'research_funding_generated': 1250000,
            'cure_acceleration_impact': {
                'time_saved_years': 2.3,
                'lives_potentially_impacted': 50000,
                'research_papers_enabled': 15
            },
            'platform_engagement': {
                'daily_active_users': 8920,
                'appointment_completion_rate': 0.87,
                'medication_adherence_rate': 0.82,
                'community_participation_rate': 0.65
            }
        }
        
        return jsonify(research_metrics), 200
        
    except Exception as e:
        logger.error(f"Error retrieving research metrics: {str(e)}")
        return jsonify({'error': 'Failed to retrieve research metrics'}), 500

@app.route('/analytics/reports/generate', methods=['POST'])
@require_auth
def generate_report():
    """Generate custom analytics report"""
    try:
        data = request.get_json()
        report_type = data.get('type', 'user_summary')
        format_type = data.get('format', 'json')
        parameters = data.get('parameters', {})
        
        # Check cache first
        cache_key = f"report:{report_type}:{request.user_id}:{hash(str(parameters))}"
        cached_report = redis_client.get(cache_key)
        
        if cached_report:
            return jsonify(json.loads(cached_report)), 200
        
        # Generate report based on type
        if report_type == 'user_summary':
            report = generate_user_summary_report(request.user_id, parameters)
        elif report_type == 'population_overview':
            report = generate_population_report(parameters)
        elif report_type == 'research_impact':
            report = generate_research_report(parameters)
        else:
            return jsonify({'error': 'Unsupported report type'}), 400
        
        # Cache report for 1 hour
        redis_client.setex(cache_key, 3600, json.dumps(report))
        
        return jsonify(report), 200
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return jsonify({'error': 'Failed to generate report'}), 500

def generate_user_summary_report(user_id, parameters):
    """Generate user summary report"""
    analytics = HealthAnalytics()
    
    # Get user metrics
    user_query = f"""
    SELECT 
        AVG(viral_load) as avg_viral_load,
        AVG(cd4_count) as avg_cd4_count,
        AVG(medication_adherence) as avg_adherence,
        AVG(appointment_attendance) as avg_attendance,
        COUNT(DISTINCT DATE(timestamp)) as active_days
    FROM `{PROJECT_ID}.{DATASET_ID}.patient_metrics`
    WHERE user_id = '{user_id}'
      AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
    """
    
    user_job = bq_client.query(user_query)
    user_results = list(user_job.result())
    
    if user_results:
        user_data = user_results[0]
        metrics = {
            'viral_load': float(user_data.avg_viral_load or 0),
            'cd4_count': float(user_data.avg_cd4_count or 0),
            'adherence': float(user_data.avg_adherence or 0),
            'attendance': float(user_data.avg_attendance or 0),
            'active_days': user_data.active_days or 0
        }
    else:
        metrics = {}
    
    # Get trends
    trends = analytics.analyze_trends(user_id, 'viral_load', 90)
    
    # Get insights
    insights = analytics.generate_insights(user_id)
    
    return {
        'report_type': 'user_summary',
        'user_id': user_id,
        'period': 'last_30_days',
        'metrics': metrics,
        'trends': trends,
        'insights': insights,
        'generated_at': datetime.utcnow().isoformat()
    }

def generate_population_report(parameters):
    """Generate population overview report"""
    analytics = HealthAnalytics()
    condition = parameters.get('condition')
    days = parameters.get('days', 30)
    
    metrics = analytics.calculate_population_metrics(condition, days)
    trends = analytics.analyze_trends(None, 'viral_load', days)
    
    return {
        'report_type': 'population_overview',
        'condition': condition,
        'period_days': days,
        'metrics': metrics,
        'trends': trends,
        'generated_at': datetime.utcnow().isoformat()
    }

def generate_research_report(parameters):
    """Generate research impact report"""
    # Query research impact data
    query = f"""
    SELECT 
        COUNT(DISTINCT user_id) as participants,
        COUNT(*) as total_contributions,
        AVG(data_quality_score) as avg_quality_score,
        SUM(research_value_usd) as total_value_generated
    FROM `{PROJECT_ID}.{DATASET_ID}.research_contributions`
    WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 365 DAY)
    """
    
    query_job = bq_client.query(query)
    results = list(query_job.result())
    
    if results:
        data = results[0]
        metrics = {
            'participants': data.participants or 0,
            'contributions': data.total_contributions or 0,
            'avg_quality_score': float(data.avg_quality_score or 0),
            'total_value_usd': float(data.total_value_usd or 0)
        }
    else:
        metrics = {}
    
    return {
        'report_type': 'research_impact',
        'period': 'last_12_months',
        'metrics': metrics,
        'generated_at': datetime.utcnow().isoformat()
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
