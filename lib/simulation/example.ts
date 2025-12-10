/**
 * Example usage of the simulation library
 *
 * This demonstrates a complete control loop with:
 * - Extended Kalman Filter for state estimation
 * - Control Barrier Function for safety
 * - Simple proportional controller
 */

import {
  initEKF,
  ekfStep,
  cbfAdjust,
  isSafe,
  type RobotState,
  type Obstacle,
  type EKFState,
} from './index';

// Simulation parameters
const dt = 1 / 60; // 60 Hz
const maxSteps = 1000;

// Setup scenario
const obstacle: Obstacle = {
  c: { x: 150, y: 100 },
  r: 30,
};

const target = { x: 250, y: 100 };
const safetyMargin = 20;

// Initialize true state (what actually happens in the world)
let trueState: RobotState = {
  p: { x: 50, y: 50 },
  v: { x: 0, y: 0 },
};

// Initialize EKF state (our estimate with some initial error)
let ekfState: EKFState = initEKF(
  new Float64Array([52, 48, 0, 0]), // Slightly wrong initial estimate
  150 // Initial uncertainty
);

console.log('Starting simulation...');
console.log(`Target: (${target.x}, ${target.y})`);
console.log(`Obstacle: center=(${obstacle.c.x}, ${obstacle.c.y}), radius=${obstacle.r}`);
console.log('---');

// Statistics
let safetyViolations = 0;
let cbfActivations = 0;

// Main control loop
for (let step = 0; step < maxSteps; step++) {
  // 1. Compute control based on EKF estimate
  const dx = target.x - ekfState.x[0];
  const dy = target.y - ekfState.x[1];
  const distToTarget = Math.hypot(dx, dy);

  // Stop if we reached the target
  if (distToTarget < 10) {
    console.log(`\n✅ Reached target in ${step} steps!`);
    break;
  }

  // Simple proportional-derivative controller
  const speed = 30;
  const a_nom = [
    (dx / distToTarget) * speed - 1.5 * ekfState.x[2],
    (dy / distToTarget) * speed - 1.5 * ekfState.x[3],
  ];

  // 2. Apply CBF for safety
  const cbfResult = cbfAdjust(a_nom, trueState, obstacle, safetyMargin, 4.0);

  if (cbfResult.active) {
    cbfActivations++;
  }

  // 3. Integrate true state dynamics
  trueState.p.x += trueState.v.x * dt + 0.5 * cbfResult.a[0] * dt * dt;
  trueState.p.y += trueState.v.y * dt + 0.5 * cbfResult.a[1] * dt * dt;
  trueState.v.x += cbfResult.a[0] * dt;
  trueState.v.y += cbfResult.a[1] * dt;

  // 4. Check safety
  if (!isSafe(trueState, obstacle, safetyMargin)) {
    safetyViolations++;
  }

  // 5. Get noisy measurement (simulating sensor)
  const measurementNoise = 3;
  const z = new Float64Array([
    trueState.p.x + (Math.random() - 0.5) * measurementNoise * 2,
    trueState.p.y + (Math.random() - 0.5) * measurementNoise * 2,
  ]);

  // 6. Update EKF with measurement
  ekfState = ekfStep(ekfState, cbfResult.a, z);

  // Print progress every 100 steps
  if (step % 100 === 0) {
    const estError = Math.hypot(
      ekfState.x[0] - trueState.p.x,
      ekfState.x[1] - trueState.p.y
    );

    console.log(`Step ${step}:`);
    console.log(`  True position: (${trueState.p.x.toFixed(1)}, ${trueState.p.y.toFixed(1)})`);
    console.log(`  Estimated position: (${ekfState.x[0].toFixed(1)}, ${ekfState.x[1].toFixed(1)})`);
    console.log(`  Estimation error: ${estError.toFixed(2)}`);
    console.log(`  Distance to target: ${distToTarget.toFixed(1)}`);
    console.log(`  CBF active: ${cbfResult.active ? 'YES' : 'NO'}`);
    console.log('---');
  }
}

// Final statistics
console.log('\n📊 Simulation Statistics:');
console.log(`Total steps: ${maxSteps}`);
console.log(`CBF activations: ${cbfActivations}`);
console.log(`Safety violations: ${safetyViolations}`);

const finalDist = Math.hypot(
  trueState.p.x - target.x,
  trueState.p.y - target.y
);
console.log(`Final distance to target: ${finalDist.toFixed(1)}`);

const finalError = Math.hypot(
  ekfState.x[0] - trueState.p.x,
  ekfState.x[1] - trueState.p.y
);
console.log(`Final estimation error: ${finalError.toFixed(2)}`);

// Evaluate performance
console.log('\n🎯 Performance:');
if (safetyViolations === 0) {
  console.log('✅ SAFE - No safety violations detected');
} else {
  console.log(`⚠️  WARNING - ${safetyViolations} safety violations occurred`);
}

if (finalError < 5) {
  console.log('✅ ACCURATE - EKF tracking is excellent');
} else if (finalError < 15) {
  console.log('✓ GOOD - EKF tracking is acceptable');
} else {
  console.log('⚠️  WARNING - EKF tracking error is high');
}

if (cbfActivations > 0) {
  console.log(`✓ CBF intervened ${cbfActivations} times to maintain safety`);
}
