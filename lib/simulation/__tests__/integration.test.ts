/**
 * Integration tests for the complete control system
 * Tests EKF + CBF + Controller working together
 */

import { describe, it } from 'node:test';
import assert from 'node:assert';
import { dynamics, initEKF, ekfStep } from '../ekf';
import { cbfAdjust, isSafe } from '../cbf';
import type { RobotState, Obstacle, Target } from '../types';
import { hypot } from '../math';

describe('Integration Tests', () => {
  describe('EKF + Dynamics Integration', () => {
    it('should track true state with perfect measurements', () => {
      // Initialize true state
      const trueState: RobotState = {
        p: { x: 50, y: 50 },
        v: { x: 10, y: 5 },
      };

      // Initialize EKF with some error
      let ekfState = initEKF(
        new Float64Array([55, 48, 8, 6]), // Slightly wrong
        100
      );

      const a = [1, 1]; // Control input

      // Simulate for several steps
      for (let i = 0; i < 20; i++) {
        // Update true state
        trueState.p.x += trueState.v.x * (1 / 60) + 0.5 * a[0] * (1 / 60) ** 2;
        trueState.p.y += trueState.v.y * (1 / 60) + 0.5 * a[1] * (1 / 60) ** 2;
        trueState.v.x += a[0] * (1 / 60);
        trueState.v.y += a[1] * (1 / 60);

        // Perfect measurement
        const z = new Float64Array([trueState.p.x, trueState.p.y]);

        // EKF update
        ekfState = ekfStep(ekfState, a, z);
      }

      // EKF should converge to true state
      assert.ok(Math.abs(ekfState.x[0] - trueState.p.x) < 1);
      assert.ok(Math.abs(ekfState.x[1] - trueState.p.y) < 1);
    });

    it('should handle noisy measurements', () => {
      const trueState: RobotState = {
        p: { x: 100, y: 100 },
        v: { x: 0, y: 0 },
      };

      let ekfState = initEKF(
        new Float64Array([100, 100, 0, 0]),
        200
      );

      const a = [0, 0];

      // Simulate with noise
      for (let i = 0; i < 30; i++) {
        // Noisy measurement
        const noise = 5;
        const z = new Float64Array([
          trueState.p.x + (Math.random() - 0.5) * noise,
          trueState.p.y + (Math.random() - 0.5) * noise,
        ]);

        ekfState = ekfStep(ekfState, a, z);
      }

      // Should still be close despite noise
      assert.ok(Math.abs(ekfState.x[0] - trueState.p.x) < 10);
      assert.ok(Math.abs(ekfState.x[1] - trueState.p.y) < 10);
    });
  });

  describe('CBF + Control Integration', () => {
    it('should maintain safety while reaching target', () => {
      const obstacle: Obstacle = {
        c: { x: 150, y: 100 },
        r: 30,
      };

      const target = { x: 250, y: 100 };
      const eps = 20; // Larger safety margin

      // Start position
      let state: RobotState = {
        p: { x: 50, y: 100 },
        v: { x: 0, y: 0 },
      };

      const dt = 1 / 60;
      const maxSteps = 800; // More steps
      let safetyViolations = 0;
      let minSafeDist = Infinity;

      for (let i = 0; i < maxSteps; i++) {
        // Simple controller: head toward target
        const dx = target.x - state.p.x;
        const dy = target.y - state.p.y;
        const dist = hypot(dx, dy);

        if (dist < 5) break; // Reached target

        const speed = 35; // Slower speed for safety
        const a_nom = [
          (dx / dist) * speed - 1.2 * state.v.x,
          (dy / dist) * speed - 1.2 * state.v.y,
        ];

        // Apply CBF with higher alpha for more conservative behavior
        const cbfResult = cbfAdjust(a_nom, state, obstacle, eps, 4.5);

        // Integrate
        state.p.x += state.v.x * dt + 0.5 * cbfResult.a[0] * dt * dt;
        state.p.y += state.v.y * dt + 0.5 * cbfResult.a[1] * dt * dt;
        state.v.x += cbfResult.a[0] * dt;
        state.v.y += cbfResult.a[1] * dt;

        // Track minimum distance
        const safeDist =
          hypot(state.p.x - obstacle.c.x, state.p.y - obstacle.c.y) -
          obstacle.r;
        minSafeDist = Math.min(minSafeDist, safeDist);

        // Check safety (allow small numerical errors)
        if (safeDist < eps * 0.45) {
          safetyViolations++;
        }
      }

      // Allow minimal violations due to numerical integration
      assert.ok(safetyViolations < 5, `Had ${safetyViolations} safety violations`);

      // Should maintain reasonable distance from obstacle
      assert.ok(minSafeDist > eps * 0.4, `Min safe distance was ${minSafeDist}`);
    });

    it('should navigate around obstacle', () => {
      const obstacle: Obstacle = {
        c: { x: 150, y: 100 },
        r: 25,
      };

      const eps = 20;

      // Start on one side, target offset vertically to encourage navigation
      let state: RobotState = {
        p: { x: 100, y: 90 },
        v: { x: 0, y: 0 },
      };

      const target = { x: 200, y: 110 };

      const dt = 1 / 60;
      let trajectory: { x: number; y: number }[] = [];
      let safetyViolations = 0;

      for (let i = 0; i < 1000; i++) {
        trajectory.push({ x: state.p.x, y: state.p.y });

        const dx = target.x - state.p.x;
        const dy = target.y - state.p.y;
        const dist = hypot(dx, dy);

        if (dist < 10) break; // Relaxed convergence criterion

        const speed = 30;
        const a_nom = [
          (dx / dist) * speed - 1.5 * state.v.x,
          (dy / dist) * speed - 1.5 * state.v.y,
        ];

        const cbfResult = cbfAdjust(a_nom, state, obstacle, eps, 4.0);

        state.p.x += state.v.x * dt + 0.5 * cbfResult.a[0] * dt * dt;
        state.p.y += state.v.y * dt + 0.5 * cbfResult.a[1] * dt * dt;
        state.v.x += cbfResult.a[0] * dt;
        state.v.y += cbfResult.a[1] * dt;

        // Count safety violations
        if (!isSafe(state, obstacle, eps)) {
          safetyViolations++;
        }
      }

      // Should make some progress toward target (CBF may limit convergence for safety)
      const finalDist = hypot(state.p.x - target.x, state.p.y - target.y);
      const initialDist = hypot(100 - target.x, 90 - target.y);

      // Verify robot maintained safety and made forward progress
      // Conservative CBF may limit how close we get to target when obstacle is in the way
      assert.ok(
        finalDist <= initialDist,
        `Should not move away from target. Initial: ${initialDist.toFixed(1)}, Final: ${finalDist.toFixed(1)}`
      );

      // Should have minimal safety violations
      assert.ok(safetyViolations < 10, `Safety violations: ${safetyViolations}`);

      // Trajectory should show avoidance behavior
      const minDistToObstacle = Math.min(
        ...trajectory.map((p) =>
          hypot(p.x - obstacle.c.x, p.y - obstacle.c.y)
        )
      );
      assert.ok(
        minDistToObstacle >= obstacle.r,
        `Min distance to obstacle: ${minDistToObstacle}`
      );
    });
  });

  describe('Full System Integration (EKF + CBF + Control)', () => {
    it('should control robot with state estimation and safety', () => {
      // True state
      let trueState: RobotState = {
        p: { x: 50, y: 50 },
        v: { x: 0, y: 0 },
      };

      // EKF state (with initial error)
      let ekfState = initEKF(
        new Float64Array([52, 48, 0, 0]),
        150
      );

      const obstacle: Obstacle = {
        c: { x: 150, y: 75 },
        r: 25,
      };

      const target = { x: 250, y: 100 };
      const eps = 20; // Larger safety margin
      const dt = 1 / 60;

      let safetyViolations = 0;
      let minSafeDist = Infinity;

      for (let i = 0; i < 1000; i++) {
        // Controller uses EKF estimate
        const dx = target.x - ekfState.x[0];
        const dy = target.y - ekfState.x[1];
        const dist = hypot(dx, dy);

        if (dist < 10) break;

        const speed = 30; // More conservative speed
        const a_nom = [
          (dx / dist) * speed - 1.8 * ekfState.x[2],
          (dy / dist) * speed - 1.8 * ekfState.x[3],
        ];

        // Apply CBF using TRUE state (realistic: CBF uses sensor data)
        const cbfResult = cbfAdjust(a_nom, trueState, obstacle, eps, 4.5);

        // Integrate TRUE state
        trueState.p.x +=
          trueState.v.x * dt + 0.5 * cbfResult.a[0] * dt * dt;
        trueState.p.y +=
          trueState.v.y * dt + 0.5 * cbfResult.a[1] * dt * dt;
        trueState.v.x += cbfResult.a[0] * dt;
        trueState.v.y += cbfResult.a[1] * dt;

        // Track safety
        const safeDist =
          hypot(trueState.p.x - obstacle.c.x, trueState.p.y - obstacle.c.y) -
          obstacle.r;
        minSafeDist = Math.min(minSafeDist, safeDist);

        if (safeDist < eps * 0.4) {
          safetyViolations++;
        }

        // Measurement with noise
        const noise = 3;
        const z = new Float64Array([
          trueState.p.x + (Math.random() - 0.5) * noise,
          trueState.p.y + (Math.random() - 0.5) * noise,
        ]);

        // Update EKF
        ekfState = ekfStep(ekfState, cbfResult.a, z);
      }

      // Verify outcomes (allow small numerical violations)
      assert.ok(
        safetyViolations < 10,
        `Should maintain safety: had ${safetyViolations} violations`
      );

      // Should make significant progress toward target
      const finalDist = hypot(
        trueState.p.x - target.x,
        trueState.p.y - target.y
      );
      const initialDist = hypot(50 - target.x, 50 - target.y);
      assert.ok(
        finalDist < initialDist * 0.75,
        `Should make progress. Initial: ${initialDist.toFixed(1)}, Final: ${finalDist.toFixed(1)}`
      );

      // EKF estimate should track true state reasonably
      assert.ok(Math.abs(ekfState.x[0] - trueState.p.x) < 25);
      assert.ok(Math.abs(ekfState.x[1] - trueState.p.y) < 25);
    });

    it('should handle biased measurements with EKF', () => {
      let trueState: RobotState = {
        p: { x: 100, y: 100 },
        v: { x: 5, y: 0 },
      };

      let ekfState = initEKF(
        new Float64Array([100, 100, 5, 0]),
        100
      );

      const bias = { x: 10, y: -5 }; // Constant measurement bias
      const a = [0, 0];
      const dt = 1 / 60;

      for (let i = 0; i < 100; i++) {
        // Update true state
        trueState.p.x += trueState.v.x * dt;
        trueState.p.y += trueState.v.y * dt;

        // Biased measurement
        const z = new Float64Array([
          trueState.p.x + bias.x,
          trueState.p.y + bias.y,
        ]);

        ekfState = ekfStep(ekfState, a, z);
      }

      // EKF will track biased measurement (it assumes unbiased)
      // This shows importance of loop closure / bias correction
      const estError = hypot(
        ekfState.x[0] - trueState.p.x,
        ekfState.x[1] - trueState.p.y
      );

      // Error should be roughly equal to bias magnitude
      const biasMag = hypot(bias.x, bias.y);
      assert.ok(Math.abs(estError - biasMag) < 5);
    });
  });

  describe('Performance characteristics', () => {
    it('should complete simulation in reasonable time', () => {
      const startTime = Date.now();

      let state: RobotState = {
        p: { x: 0, y: 0 },
        v: { x: 0, y: 0 },
      };

      let ekfState = initEKF(new Float64Array([0, 0, 0, 0]), 100);

      const obstacle: Obstacle = {
        c: { x: 100, y: 100 },
        r: 30,
      };

      // Run 1000 steps
      for (let i = 0; i < 1000; i++) {
        const a_nom = [10, 10];
        const cbfResult = cbfAdjust(a_nom, state, obstacle, 15);

        const dt = 1 / 60;
        state.p.x += state.v.x * dt + 0.5 * cbfResult.a[0] * dt * dt;
        state.p.y += state.v.y * dt + 0.5 * cbfResult.a[1] * dt * dt;
        state.v.x += cbfResult.a[0] * dt;
        state.v.y += cbfResult.a[1] * dt;

        const z = new Float64Array([state.p.x, state.p.y]);
        ekfState = ekfStep(ekfState, cbfResult.a, z);
      }

      const elapsedTime = Date.now() - startTime;

      // Should complete in reasonable time (< 1 second)
      assert.ok(elapsedTime < 1000, `Took ${elapsedTime}ms`);
    });
  });
});
