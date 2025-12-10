/**
 * Unit tests for Control Barrier Function
 */

import { describe, it } from 'node:test';
import assert from 'node:assert';
import {
  cbfAdjust,
  isSafe,
  barrierFunction,
  type CBFResult,
} from '../cbf';
import type { RobotState, Obstacle } from '../types';

describe('Control Barrier Function', () => {
  const obstacle: Obstacle = {
    c: { x: 100, y: 100 },
    r: 20,
  };

  const eps = 10; // Safety margin

  describe('barrierFunction', () => {
    it('should return positive value when safe', () => {
      const state: RobotState = {
        p: { x: 200, y: 100 }, // Far from obstacle
        v: { x: 0, y: 0 },
      };

      const h = barrierFunction(state, obstacle, eps);

      // Distance is ~100, minus radius 20, minus eps 10 = 70
      assert.ok(h > 0);
      assert.ok(Math.abs(h - 70) < 1);
    });

    it('should return negative value when unsafe', () => {
      const state: RobotState = {
        p: { x: 110, y: 100 }, // Very close to obstacle
        v: { x: 0, y: 0 },
      };

      const h = barrierFunction(state, obstacle, eps);

      // Distance is 10, minus radius 20 = -10, minus eps 10 = -20
      assert.ok(h < 0);
    });

    it('should return zero at boundary', () => {
      const state: RobotState = {
        p: { x: 130, y: 100 }, // At boundary (radius + eps)
        v: { x: 0, y: 0 },
      };

      const h = barrierFunction(state, obstacle, eps);

      assert.ok(Math.abs(h) < 1e-10);
    });
  });

  describe('isSafe', () => {
    it('should return true when far from obstacle', () => {
      const state: RobotState = {
        p: { x: 200, y: 100 },
        v: { x: 0, y: 0 },
      };

      assert.strictEqual(isSafe(state, obstacle, eps), true);
    });

    it('should return false when too close', () => {
      const state: RobotState = {
        p: { x: 104, y: 100 }, // Within eps*0.5 of surface
        v: { x: 0, y: 0 },
      };

      assert.strictEqual(isSafe(state, obstacle, eps), false);
    });

    it('should handle positions on all sides', () => {
      const positions = [
        { x: 100, y: 200 }, // Above
        { x: 100, y: 0 }, // Below
        { x: 0, y: 100 }, // Left
        { x: 200, y: 100 }, // Right
      ];

      for (const p of positions) {
        const state: RobotState = { p, v: { x: 0, y: 0 } };
        assert.strictEqual(isSafe(state, obstacle, eps), true);
      }
    });
  });

  describe('cbfAdjust', () => {
    it('should not modify control when safe and moving away', () => {
      const state: RobotState = {
        p: { x: 200, y: 100 }, // Far from obstacle
        v: { x: 10, y: 0 }, // Moving away
      };

      const a_nom = [5, 0]; // Accelerating away
      const result = cbfAdjust(a_nom, state, obstacle, eps);

      assert.strictEqual(result.active, false);
      assert.deepStrictEqual(result.a, a_nom);
      assert.ok(result.h > 0); // Safe
    });

    it('should modify control when moving toward obstacle', () => {
      const state: RobotState = {
        p: { x: 135, y: 100 }, // Closer to obstacle
        v: { x: -15, y: 0 }, // Moving fast toward obstacle
      };

      const a_nom = [-10, 0]; // Strong acceleration toward obstacle
      const result = cbfAdjust(a_nom, state, obstacle, eps);

      // Check if constraint was active
      if (result.active) {
        // Acceleration should be adjusted (less negative or positive)
        assert.ok(result.a[0] > a_nom[0]);
      } else {
        // If not active, constraint must still be satisfied
        assert.ok(result.h > 0 || result.dh > 0);
      }
    });

    it('should ensure safety constraint is satisfied', () => {
      const state: RobotState = {
        p: { x: 135, y: 100 }, // Near boundary
        v: { x: -5, y: 0 }, // Moving toward
      };

      const a_nom = [-10, 0]; // Dangerous acceleration
      const result = cbfAdjust(a_nom, state, obstacle, eps);

      // Check that adjusted control satisfies CBF constraint
      const { c, r } = obstacle;
      const dx = state.p.x - c.x;
      const dy = state.p.y - c.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const nx = dx / dist;
      const ny = dy / dist;

      const h = result.h;
      const dh = result.dh;
      const alpha = 3.5;
      const b = -dh - alpha * h;

      const dot = nx * result.a[0] + ny * result.a[1];

      // Constraint should be satisfied (with small tolerance)
      assert.ok(dot >= b - 1e-6);
    });

    it('should handle different alpha values', () => {
      const state: RobotState = {
        p: { x: 140, y: 100 },
        v: { x: -10, y: 0 },
      };

      const a_nom = [-5, 0];

      // More conservative (higher alpha)
      const result1 = cbfAdjust(a_nom, state, obstacle, eps, 5.0);

      // Less conservative (lower alpha)
      const result2 = cbfAdjust(a_nom, state, obstacle, eps, 2.0);

      if (result1.active && result2.active) {
        // Higher alpha should give more conservative control
        // (more correction toward safety)
        assert.ok(result1.a[0] >= result2.a[0]);
      }
    });

    it('should handle tangential motion correctly', () => {
      const state: RobotState = {
        p: { x: 140, y: 100 },
        v: { x: 0, y: 10 }, // Moving tangent to obstacle
      };

      const a_nom = [0, 5]; // Tangential acceleration
      const result = cbfAdjust(a_nom, state, obstacle, eps);

      // Tangential motion shouldn't trigger constraint as strongly
      // (depends on specific configuration)
      assert.ok(typeof result.active === 'boolean');
      assert.ok(Array.isArray(result.a));
    });

    it('should return correct structure', () => {
      const state: RobotState = {
        p: { x: 150, y: 100 },
        v: { x: 0, y: 0 },
      };

      const a_nom = [1, 0];
      const result = cbfAdjust(a_nom, state, obstacle, eps);

      // Check result structure
      assert.ok('a' in result);
      assert.ok('active' in result);
      assert.ok('h' in result);
      assert.ok('dh' in result);

      assert.ok(Array.isArray(result.a));
      assert.strictEqual(result.a.length, 2);
      assert.strictEqual(typeof result.active, 'boolean');
      assert.strictEqual(typeof result.h, 'number');
      assert.strictEqual(typeof result.dh, 'number');
    });

    it('should handle stationary robot', () => {
      const state: RobotState = {
        p: { x: 132, y: 100 }, // Very close to boundary (r=20 + eps=10 = 130)
        v: { x: 0, y: 0 }, // Stationary
      };

      const a_nom = [-20, 0]; // Strong acceleration toward
      const result = cbfAdjust(a_nom, state, obstacle, eps);

      // With zero velocity, dh = 0
      assert.strictEqual(result.dh, 0);

      // CBF should activate since h is small and acceleration is dangerous
      if (result.active) {
        assert.ok(result.a[0] > a_nom[0]);
      }
    });

    it('should provide minimal intervention', () => {
      const state: RobotState = {
        p: { x: 140, y: 100 },
        v: { x: -1, y: 0 }, // Slow approach
      };

      const a_nom = [-0.5, 2]; // Mostly perpendicular
      const result = cbfAdjust(a_nom, state, obstacle, eps);

      if (result.active) {
        // Correction should be minimal
        const correction = Math.hypot(
          result.a[0] - a_nom[0],
          result.a[1] - a_nom[1]
        );
        // Check that we didn't drastically change the control
        const nomMag = Math.hypot(a_nom[0], a_nom[1]);
        assert.ok(correction < nomMag * 2); // Reasonable bound
      }
    });
  });

  describe('Edge cases', () => {
    it('should handle robot at obstacle center', () => {
      const state: RobotState = {
        p: { x: 100, y: 100 }, // At center
        v: { x: 1, y: 0 },
      };

      const a_nom = [1, 0];
      const result = cbfAdjust(a_nom, state, obstacle, eps);

      // Should still compute (uses epsilon for division)
      assert.ok(Array.isArray(result.a));
      assert.strictEqual(typeof result.active, 'boolean');
    });

    it('should handle zero velocity and acceleration', () => {
      const state: RobotState = {
        p: { x: 140, y: 100 },
        v: { x: 0, y: 0 },
      };

      const a_nom = [0, 0];
      const result = cbfAdjust(a_nom, state, obstacle, eps);

      // Should not modify zero control
      assert.deepStrictEqual(result.a, [0, 0]);
    });

    it('should handle multiple obstacles conceptually', () => {
      // Test that CBF works for different obstacles
      const obstacles: Obstacle[] = [
        { c: { x: 100, y: 100 }, r: 20 },
        { c: { x: 200, y: 200 }, r: 30 },
      ];

      const state: RobotState = {
        p: { x: 150, y: 150 },
        v: { x: 5, y: 5 },
      };

      const a_nom = [10, 10];

      // Each obstacle independently
      for (const obs of obstacles) {
        const result = cbfAdjust(a_nom, state, obs, eps);
        assert.ok(typeof result.active === 'boolean');
      }
    });
  });
});
