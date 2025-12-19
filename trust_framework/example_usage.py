"""
Trust Calibration Framework - Complete Usage Examples
Demonstrates all framework capabilities with realistic scenarios
"""

import numpy as np
import sys
sys.path.insert(0, '/home/claude/trust_calibration_framework')

from trust_calibration_framework import TrustCalibrationFramework

def example_1_basic_usage():
    """
    Example 1: Basic Trust Calibration
    Single interaction processing
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Usage")
    print("="*60)
    
    framework = TrustCalibrationFramework()
    
    # Single interaction
    status = framework.update(
        T_user=0.80,
        R_actual=0.85,
        behavioral_signals={
            'dwell_time': 2.5,
            'reliance_ratio': 0.75,
            'query_complexity': 0.6,
            'interaction_frequency': 1.2,
            'override_rate': 0.1
        }
    )
    
    print(f"\nCurrent State:")
    print(f"  T_user: {status['T_user']:.3f}")
    print(f"  R_actual: {status['R_actual']:.3f}")
    print(f"  Δ_trust: {status['delta_trust']:.3f}")
    print(f"  Miscalibrated: {status['miscalibrated']}")
    print(f"  Latency: {status['latency_ms']:.2f}ms")
    
    print(f"\nLatent Variables:")
    for var, val in status['latent'].items():
        print(f"  {var}: {val:.3f}")


def example_2_drift_detection():
    """
    Example 2: Drift Detection and Recalibration
    Simulates reliability degradation
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Drift Detection")
    print("="*60)
    
    framework = TrustCalibrationFramework()
    
    print("\nPhase 1: Baseline Operation (R=0.85)")
    for t in range(30):
        R = 0.85 + np.random.normal(0, 0.03)
        T = 0.80 + np.random.normal(0, 0.05)
        
        status = framework.update(T, R)
        
        if t % 10 == 0:
            print(f"  t={t}: R={R:.3f}, Δ={status['delta_trust']:.3f}, "
                  f"CUSUM={status['drift']['S_t']:.3f}")
    
    print("\nPhase 2: Injecting Drift (R degrades to 0.65)")
    for t in range(30, 60):
        R = 0.65 + np.random.normal(0, 0.03)  # Degraded performance
        T = 0.78 + np.random.normal(0, 0.05)
        
        status = framework.update(T, R)
        
        if status['drift']['detected']:
            print(f"\n⚠ DRIFT DETECTED at t={t}")
            print(f"  S_t: {status['drift']['S_t']:.3f}")
            print(f"  Threshold: {status['drift']['threshold']:.3f}")
            print(f"  Change Point: {status['drift']['change_point']}")
            print(f"  [System automatically recalibrated]")
            break


def example_3_proactive_intervention():
    """
    Example 3: Proactive Intervention
    Predicts and prevents miscalibration
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Proactive Intervention")
    print("="*60)
    
    framework = TrustCalibrationFramework(config={
        'enable_predictive': True,
        'forecast_horizon': 5,
        'forecast_interval': 3,
        'intervention_confidence': 0.85
    })
    
    # Simulate trend toward miscalibration
    np.random.seed(42)
    
    for t in range(50):
        # Gradually increasing miscalibration
        T = 0.85 + 0.002 * t + np.random.normal(0, 0.03)
        R = 0.75 - 0.001 * t + np.random.normal(0, 0.02)
        
        T = np.clip(T, 0, 1)
        R = np.clip(R, 0, 1)
        
        status = framework.update(T, R, behavioral_signals={
            'dwell_time': 2.0 + 0.05 * t,
            'reliance_ratio': T,
            'query_complexity': 0.5 + 0.01 * t,
            'interaction_frequency': 1.0,
            'override_rate': 0.1
        })
        
        # Check for proactive intervention
        if status['intervention']['proactive_recommended']:
            print(f"\n⚠ PROACTIVE INTERVENTION at t={t}")
            print(f"  Current Δ: {status['delta_trust']:.3f}")
            print(f"  Reason: {status['intervention']['reason']}")
            
            if status['forecast']:
                print(f"\n  Forecast (k={status['forecast']['horizon']}):")
                deltas = status['forecast']['delta_predictions']
                probs = status['forecast']['miscalibration_probabilities']
                
                for k in range(len(deltas)):
                    print(f"    t+{k+1}: Δ={deltas[k]:.3f}, "
                          f"P(Δ>0.15)={probs[k]:.2%}")
            break
    
    # Show metrics
    metrics = framework.get_metrics()
    print(f"\nFramework Metrics:")
    print(f"  Forecast Accuracy: {metrics.forecast_accuracy:.2%}")
    print(f"  Intervention Effectiveness: {metrics.intervention_effectiveness:.2%}")
    print(f"  Total Proactive: {framework.proactive_count}")
    print(f"  Total Reactive: {framework.reactive_count}")


def example_4_complete_episode():
    """
    Example 4: Complete Episode with All Features
    Comprehensive demonstration
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Complete Episode (100 interactions)")
    print("="*60)
    
    framework = TrustCalibrationFramework(config={
        'enable_predictive': True,
        'forecast_horizon': 3,
        'forecast_interval': 5
    })
    
    # Generate realistic episode
    np.random.seed(123)
    n_steps = 100
    
    # Realistic trajectories
    R_actual = np.zeros(n_steps)
    T_user = np.zeros(n_steps)
    
    # Base reliability with drift at t=60
    for t in range(n_steps):
        if t < 60:
            R_actual[t] = 0.85 + np.random.normal(0, 0.05)
        else:
            R_actual[t] = 0.70 + np.random.normal(0, 0.05)
        R_actual[t] = np.clip(R_actual[t], 0, 1)
    
    # User trust with lag
    T_user[0] = 0.80
    for t in range(1, n_steps):
        # Trust adapts with lag and noise
        T_user[t] = 0.7 * T_user[t-1] + 0.3 * R_actual[t-1] + np.random.normal(0, 0.05)
        T_user[t] = np.clip(T_user[t], 0, 1)
    
    # Run episode
    drift_detected_at = None
    proactive_interventions = []
    reactive_interventions = []
    
    for t in range(n_steps):
        signals = {
            'dwell_time': 2.0 + np.random.uniform(-0.5, 0.5),
            'reliance_ratio': T_user[t],
            'query_complexity': 0.5 + np.random.uniform(-0.2, 0.2),
            'interaction_frequency': 1.0,
            'override_rate': (1 - T_user[t]) * 0.3
        }
        
        status = framework.update(T_user[t], R_actual[t], signals)
        
        # Track events
        if status['drift']['detected'] and drift_detected_at is None:
            drift_detected_at = t
        
        if status['intervention']['proactive_recommended']:
            proactive_interventions.append(t)
        
        if status['intervention']['reactive_required']:
            reactive_interventions.append(t)
        
        # Periodic status
        if t % 20 == 0:
            print(f"\nt={t:3d}: R={R_actual[t]:.3f}, T={T_user[t]:.3f}, "
                  f"Δ={status['delta_trust']:.3f}")
    
    # Final report
    print(f"\n{'='*60}")
    print("EPISODE SUMMARY")
    print(f"{'='*60}")
    
    metrics = framework.get_metrics()
    
    print(f"\nPerformance Metrics:")
    print(f"  Trust Calibration Δ: {metrics.trust_calibration_delta:.4f} "
          f"{'✓' if metrics.trust_calibration_delta <= 0.15 else '✗'}")
    print(f"  Forecast Accuracy: {metrics.forecast_accuracy:.4f} "
          f"{'✓' if metrics.forecast_accuracy >= 0.75 else '✗'}")
    print(f"  False Positive Rate: {metrics.false_positive_rate:.4f} "
          f"{'✓' if metrics.false_positive_rate <= 0.05 else '✗'}")
    print(f"  Intervention Effectiveness: {metrics.intervention_effectiveness:.4f} "
          f"{'✓' if metrics.intervention_effectiveness >= 0.70 else '✗'}")
    print(f"  Computational Latency: {metrics.computational_latency_ms:.2f}ms "
          f"{'✓' if metrics.computational_latency_ms <= 200 else '✗'}")
    
    print(f"\nEvent Summary:")
    print(f"  Drift Detected: {'Yes at t=' + str(drift_detected_at) if drift_detected_at else 'No'}")
    print(f"  Proactive Interventions: {len(proactive_interventions)} at {proactive_interventions[:5]}")
    print(f"  Reactive Interventions: {len(reactive_interventions)} at {reactive_interventions[:5]}")
    
    print(f"\nRequirements Status:")
    print(f"  Meets All Requirements: {metrics.meets_requirements()} "
          f"{'✓ PASS' if metrics.meets_requirements() else '✗ FAIL'}")


def example_5_custom_configuration():
    """
    Example 5: Custom Configuration
    Tuning framework parameters
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: Custom Configuration")
    print("="*60)
    
    # Conservative configuration (low false positives)
    conservative_config = {
        'window_size': 30,
        'process_noise_std': 0.03,
        'measurement_noise_std': 0.08,
        'intervention_threshold': 0.18,
        'intervention_confidence': 0.90,
        'cooldown_steps': 15,
        'h_factor': 6.0
    }
    
    # Aggressive configuration (fast response)
    aggressive_config = {
        'window_size': 15,
        'process_noise_std': 0.07,
        'measurement_noise_std': 0.12,
        'intervention_threshold': 0.12,
        'intervention_confidence': 0.80,
        'cooldown_steps': 5,
        'h_factor': 3.0
    }
    
    print("\nConfiguration Comparison:")
    print("\n1. Conservative (Low FPR, High Precision):")
    framework_conservative = TrustCalibrationFramework(conservative_config)
    
    print("   - Larger window (30)")
    print("   - Higher intervention threshold (0.18)")
    print("   - Higher confidence requirement (0.90)")
    print("   - Longer cooldown (15 steps)")
    
    print("\n2. Aggressive (Fast Response, High Recall):")
    framework_aggressive = TrustCalibrationFramework(aggressive_config)
    
    print("   - Smaller window (15)")
    print("   - Lower intervention threshold (0.12)")
    print("   - Lower confidence requirement (0.80)")
    print("   - Shorter cooldown (5 steps)")
    
    print("\nUse Cases:")
    print("  Conservative: High-stakes applications (medical, financial)")
    print("  Aggressive: Rapid learning environments (gaming, education)")


def run_all_examples():
    """Run all usage examples"""
    print("\n" + "#"*60)
    print("# TRUST CALIBRATION FRAMEWORK - USAGE EXAMPLES")
    print("#"*60)
    
    example_1_basic_usage()
    example_2_drift_detection()
    example_3_proactive_intervention()
    example_4_complete_episode()
    example_5_custom_configuration()
    
    print("\n" + "#"*60)
    print("# ALL EXAMPLES COMPLETE")
    print("#"*60)
    print("\nNext Steps:")
    print("  1. Run validation: python tests/test_framework.py")
    print("  2. Review README.md for complete API documentation")
    print("  3. Integrate into your application")


if __name__ == "__main__":
    run_all_examples()
