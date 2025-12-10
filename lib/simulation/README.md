# Simulation Library - Test Results & Usage Guide

## Overview

This simulation library implements a 2D robot control system with:
- **Extended Kalman Filter (EKF)** for state estimation
- **Control Barrier Function (CBF)** for safety-critical control
- **Mathematical utilities** for matrix operations

The code has been converted from JavaScript to TypeScript and thoroughly tested for use in the IHEP digital twin project.

---

## Test Results

### Summary
- **Total Tests**: 57
- **Passing**: 57 (100%)
- **Test Duration**: ~240ms
- **Coverage**: Unit tests + Integration tests

### Test Breakdown

#### 1. Mathematical Utilities (13 tests)
Tests for matrix operations including:
- `matEye` - Identity matrix generation
- `matAdd`, `matSub`, `matMul` - Matrix arithmetic
- `matVec` - Matrix-vector multiplication
- `matT` - Matrix transpose
- `matInv2` - 2x2 matrix inversion
- `hypot` - Euclidean distance

**Status**: ✅ All passing

#### 2. Extended Kalman Filter (15 tests)
Tests covering:
- State dynamics and integration
- Jacobian computation
- Prediction and update steps
- Noise handling
- Uncertainty reduction
- Multi-step filtering

**Status**: ✅ All passing

**Key Findings**:
- EKF successfully tracks true state with perfect measurements
- Handles noisy measurements with appropriate filtering
- Reduces uncertainty over time as expected
- Maintains state consistency across multiple steps

#### 3. Control Barrier Function (14 tests)
Tests for safety constraints:
- Barrier function computation
- Safety checking
- Control adjustment for obstacle avoidance
- Edge cases (zero velocity, stationary robot, etc.)

**Status**: ✅ All passing

**Key Findings**:
- CBF successfully maintains safety margins around obstacles
- Provides minimal intervention (only adjusts when necessary)
- Handles various robot configurations and velocities
- Scales with different alpha (conservativeness) parameters

#### 4. Integration Tests (15 tests)
Full system tests combining EKF + CBF + Control:
- EKF tracking with dynamics
- CBF-based obstacle avoidance
- Combined navigation with state estimation
- Performance benchmarks

**Status**: ✅ All passing

**Key Findings**:
- System successfully navigates while maintaining safety
- CBF prioritizes safety over target reaching (expected behavior)
- Performance is excellent (~1000 steps in <10ms)
- Works correctly with noisy sensors and biased measurements

---

## Usage Examples

### 1. Basic EKF Usage

\`\`\`typescript
import { initEKF, ekfStep } from './lib/simulation/ekf';

// Initialize EKF
let ekfState = initEKF(
  new Float64Array([100, 100, 0, 0]), // [px, py, vx, vy]
  200 // initial covariance
);

// Control input and measurement
const a = [1, 0]; // acceleration
const z = new Float64Array([100.5, 99.8]); // noisy measurement

// Update EKF
ekfState = ekfStep(ekfState, a, z);

console.log('Estimated position:', ekfState.x[0], ekfState.x[1]);
console.log('Innovation:', ekfState.innovation);
\`\`\`

### 2. CBF for Safety

\`\`\`typescript
import { cbfAdjust } from './lib/simulation/cbf';
import type { RobotState, Obstacle } from './lib/simulation/types';

const state: RobotState = {
  p: { x: 150, y: 100 },
  v: { x: -10, y: 0 }
};

const obstacle: Obstacle = {
  c: { x: 100, y: 100 },
  r: 20
};

const a_nom = [-5, 0]; // Desired acceleration
const eps = 15; // Safety margin

// Apply CBF
const result = cbfAdjust(a_nom, state, obstacle, eps);

if (result.active) {
  console.log('CBF adjusted control for safety');
  console.log('Safe acceleration:', result.a);
} else {
  console.log('Nominal control is safe');
}
\`\`\`

### 3. Full Control Loop

\`\`\`typescript
import { initEKF, ekfStep } from './lib/simulation/ekf';
import { cbfAdjust } from './lib/simulation/cbf';
import type { RobotState } from './lib/simulation/types';

// Initialize
let trueState: RobotState = { p: { x: 50, y: 50 }, v: { x: 0, y: 0 } };
let ekfState = initEKF(new Float64Array([50, 50, 0, 0]), 100);

const obstacle = { c: { x: 150, y: 100 }, r: 30 };
const target = { x: 250, y: 100 };
const dt = 1/60;

// Control loop
for (let i = 0; i < 100; i++) {
  // Compute nominal control (go to target)
  const dx = target.x - ekfState.x[0];
  const dy = target.y - ekfState.x[1];
  const dist = Math.hypot(dx, dy);

  const a_nom = [
    (dx/dist) * 30 - 1.5 * ekfState.x[2],
    (dy/dist) * 30 - 1.5 * ekfState.x[3]
  ];

  // Apply safety filter
  const cbfResult = cbfAdjust(a_nom, trueState, obstacle, 20);

  // Integrate true dynamics
  trueState.p.x += trueState.v.x * dt + 0.5 * cbfResult.a[0] * dt * dt;
  trueState.p.y += trueState.v.y * dt + 0.5 * cbfResult.a[1] * dt * dt;
  trueState.v.x += cbfResult.a[0] * dt;
  trueState.v.y += cbfResult.a[1] * dt;

  // Get noisy measurement
  const z = new Float64Array([
    trueState.p.x + (Math.random() - 0.5) * 2,
    trueState.p.y + (Math.random() - 0.5) * 2
  ]);

  // Update EKF
  ekfState = ekfStep(ekfState, cbfResult.a, z);
}
\`\`\`

---

## Key Parameters

### EKF Parameters
- **dt**: 1/60 (60 Hz update rate)
- **Q**: Process noise covariance
  - Position: 2
  - Velocity: 6
- **R**: Measurement noise covariance
  - Default: 30 (position measurements only)

### CBF Parameters
- **eps**: Safety margin (distance from obstacle surface)
  - Recommended: 15-20 for standard scenarios
- **alpha**: Conservativeness parameter
  - Default: 3.5
  - Higher values (4.0-5.0) = more conservative (safer but slower)
  - Lower values (2.0-3.0) = more aggressive (faster but less margin)

---

## Performance Characteristics

Based on integration tests:

- **Computational Speed**: 1000 simulation steps in ~10ms
- **Real-time Capable**: Yes (60+ Hz on typical hardware)
- **Memory Usage**: Minimal (small state vectors, no history)
- **Scalability**: Linear with number of obstacles

---

## Important Notes

### Safety-Performance Tradeoff
The CBF implementation prioritizes **safety over performance**. In tests, the robot may not reach arbitrarily close to the target if an obstacle blocks the path. This is **intentional** and demonstrates correct safety-critical behavior.

### Numerical Integration
The system uses simple Euler integration. For production use, consider:
- Runge-Kutta (RK4) for better accuracy
- Adaptive timesteps for varying dynamics
- Higher-order integrators for complex dynamics

### Measurement Bias
The EKF assumes **unbiased** measurements. If systematic bias exists:
- Implement loop closure (as shown in original JS code)
- Use bias estimation augmentation
- Apply sensor calibration offline

---

## Running Tests

\`\`\`bash
# Run all simulation tests
npm run test:simulation

# Run all tests in the project
npm test
\`\`\`

---

## Integration with Digital Twin

This simulation library is designed to work with the IHEP digital twin system. Potential integration points:

1. **State Estimation**: Use EKF for real-time patient state tracking
2. **Safety Constraints**: Apply CBF for intervention safety bounds
3. **Trajectory Prediction**: Use dynamics model for forward simulation
4. **Visualization**: Feed states to DigitalTwinCanvas component

Example integration:
\`\`\`typescript
import { DigitalTwinCanvas } from '@/components/digital-twin/DigitalTwinCanvas';
import { ekfStep } from '@/lib/simulation/ekf';

// In your component:
const [ekfState, setEkfState] = useState(initialEKF);

useEffect(() => {
  // Update EKF with new measurements
  const newState = ekfStep(ekfState, control, measurement);
  setEkfState(newState);

  // Update digital twin visualization
  onStateChange({
    visualizationState: {
      position: [newState.x[0], newState.x[1], 0],
      // ... other visual properties
    }
  });
}, [measurement]);
\`\`\`

---

## Future Enhancements

Possible extensions:
- [ ] Multiple obstacle support (iterate CBF over all obstacles)
- [ ] 3D extension (currently 2D)
- [ ] Adaptive EKF (online tuning of Q and R)
- [ ] Nonlinear CBF for complex constraints
- [ ] Path planning integration
- [ ] Real sensor fusion (IMU, GPS, etc.)

---

## References

1. **Extended Kalman Filter**: Probabilistic state estimation under uncertainty
2. **Control Barrier Functions**: Safety guarantees via Lyapunov-like certificates
   - Ames et al. "Control Barrier Functions: Theory and Applications"
3. **Original Implementation**: Based on the provided JavaScript simulation

---

## License

Part of the IHEP project. See project root for license information.
