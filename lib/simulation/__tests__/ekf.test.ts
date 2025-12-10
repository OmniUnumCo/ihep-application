/**
 * Unit tests for Extended Kalman Filter
 */

import { describe, it } from 'node:test';
import assert from 'node:assert';
import { dynamics, F_jac, H_meas, Q, R, ekfStep, initEKF } from '../ekf';

describe('Extended Kalman Filter', () => {
  describe('dynamics', () => {
    it('should predict next state with zero control', () => {
      const x = new Float64Array([10, 20, 5, 3]); // [px, py, vx, vy]
      const a = [0, 0]; // No acceleration

      const x_next = dynamics(x, a);

      // With dt = 1/60, position should update by velocity * dt
      const dt = 1 / 60;
      assert.ok(Math.abs(x_next[0] - (10 + 5 * dt)) < 1e-10);
      assert.ok(Math.abs(x_next[1] - (20 + 3 * dt)) < 1e-10);
      assert.strictEqual(x_next[2], 5); // Velocity unchanged
      assert.strictEqual(x_next[3], 3);
    });

    it('should integrate acceleration correctly', () => {
      const x = new Float64Array([0, 0, 0, 0]);
      const a = [10, 20]; // Constant acceleration

      const x_next = dynamics(x, a);

      const dt = 1 / 60;
      // Position: 0.5 * a * dt^2
      assert.ok(Math.abs(x_next[0] - 0.5 * 10 * dt * dt) < 1e-10);
      assert.ok(Math.abs(x_next[1] - 0.5 * 20 * dt * dt) < 1e-10);
      // Velocity: a * dt
      assert.ok(Math.abs(x_next[2] - 10 * dt) < 1e-10);
      assert.ok(Math.abs(x_next[3] - 20 * dt) < 1e-10);
    });

    it('should handle negative velocities and accelerations', () => {
      const x = new Float64Array([100, 100, -10, -5]);
      const a = [-20, -10];

      const x_next = dynamics(x, a);

      // Should move in negative direction
      assert.ok(x_next[0] < 100);
      assert.ok(x_next[1] < 100);
      assert.ok(x_next[2] < -10); // Velocity should decrease further
      assert.ok(x_next[3] < -5);
    });
  });

  describe('F_jac', () => {
    it('should return correct Jacobian structure', () => {
      const F = F_jac();
      const dt = 1 / 60;

      assert.strictEqual(F.length, 4);
      assert.strictEqual(F[0].length, 4);

      // Check structure
      assert.deepStrictEqual(F, [
        [1, 0, dt, 0],
        [0, 1, 0, dt],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
      ]);
    });
  });

  describe('Measurement matrix', () => {
    it('should observe position only', () => {
      assert.deepStrictEqual(H_meas, [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
      ]);
    });
  });

  describe('Noise covariances', () => {
    it('should have valid process noise Q', () => {
      assert.strictEqual(Q.length, 4);
      assert.strictEqual(Q[0].length, 4);
      // Check diagonal
      assert.strictEqual(Q[0][0], 2);
      assert.strictEqual(Q[1][1], 2);
      assert.strictEqual(Q[2][2], 6);
      assert.strictEqual(Q[3][3], 6);
    });

    it('should have valid measurement noise R', () => {
      assert.strictEqual(R.length, 2);
      assert.strictEqual(R[0].length, 2);
      assert.strictEqual(R[0][0], 30);
      assert.strictEqual(R[1][1], 30);
    });
  });

  describe('initEKF', () => {
    it('should initialize EKF state', () => {
      const x0 = new Float64Array([10, 20, 0, 0]);
      const state = initEKF(x0, 100);

      assert.deepStrictEqual(state.x, x0);
      assert.strictEqual(state.P.length, 4);
      assert.strictEqual(state.P[0][0], 100);
      assert.strictEqual(state.innovation.length, 2);
    });

    it('should use default covariance', () => {
      const x0 = new Float64Array([0, 0, 0, 0]);
      const state = initEKF(x0);

      assert.strictEqual(state.P[0][0], 200);
      assert.strictEqual(state.P[1][1], 200);
    });
  });

  describe('ekfStep', () => {
    it('should perform predict step correctly', () => {
      const x0 = new Float64Array([10, 20, 5, 3]);
      const state = initEKF(x0, 100);

      const a = [0, 0];
      const z = new Float64Array([10, 20]); // Perfect measurement

      const newState = ekfStep(state, a, z);

      // State should be updated
      assert.ok(newState.x instanceof Float64Array);
      assert.strictEqual(newState.x.length, 4);

      // Covariance should be updated
      assert.ok(Array.isArray(newState.P));
      assert.strictEqual(newState.P.length, 4);

      // Innovation should be computed
      assert.ok(newState.innovation instanceof Float64Array);
      assert.strictEqual(newState.innovation.length, 2);
    });

    it('should update with noisy measurement', () => {
      const x0 = new Float64Array([100, 100, 0, 0]);
      const state = initEKF(x0, 200);

      const a = [0, 0];
      // Measurement has error
      const z = new Float64Array([105, 98]);

      const newState = ekfStep(state, a, z);

      // State estimate should move towards measurement
      // but not exactly to it (due to uncertainty balance)
      assert.ok(newState.x[0] > 100);
      assert.ok(newState.x[0] < 105);
      assert.ok(newState.x[1] < 100);
      assert.ok(newState.x[1] > 98);

      // Innovation should capture measurement error
      assert.ok(Math.abs(newState.innovation[0]) > 0);
      assert.ok(Math.abs(newState.innovation[1]) > 0);
    });

    it('should maintain state dimension', () => {
      const x0 = new Float64Array([0, 0, 0, 0]);
      let state = initEKF(x0, 100);

      // Run multiple steps
      for (let i = 0; i < 10; i++) {
        const a = [1, 1];
        const z = new Float64Array([i, i]);
        state = ekfStep(state, a, z);

        assert.strictEqual(state.x.length, 4);
        assert.strictEqual(state.P.length, 4);
        assert.strictEqual(state.P[0].length, 4);
      }
    });

    it('should reduce uncertainty with measurements', () => {
      const x0 = new Float64Array([0, 0, 0, 0]);
      const state = initEKF(x0, 200);

      const initialTrace =
        state.P[0][0] + state.P[1][1] + state.P[2][2] + state.P[3][3];

      // Apply multiple measurements
      let currentState = state;
      for (let i = 0; i < 5; i++) {
        const a = [0, 0];
        const z = new Float64Array([1, 1]);
        currentState = ekfStep(currentState, a, z);
      }

      const finalTrace =
        currentState.P[0][0] +
        currentState.P[1][1] +
        currentState.P[2][2] +
        currentState.P[3][3];

      // Uncertainty (trace of P) should decrease
      assert.ok(finalTrace < initialTrace);
    });

    it('should handle control input', () => {
      const x0 = new Float64Array([0, 0, 0, 0]);
      const state = initEKF(x0, 100);

      const a = [100, 50]; // Strong acceleration
      const z = new Float64Array([0, 0]);

      const newState = ekfStep(state, a, z);

      // Velocity should increase due to acceleration
      assert.ok(newState.x[2] > 0);
      assert.ok(newState.x[3] > 0);
    });
  });
});
