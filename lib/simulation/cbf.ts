/**
 * Control Barrier Function (CBF) for safety-critical control
 * Ensures the robot maintains a safe distance from obstacles
 */

import type { RobotState, Obstacle } from './types';
import { hypot } from './math';

export interface CBFResult {
  a: number[];     // Adjusted acceleration
  active: boolean; // Whether CBF constraint was active
  h: number;       // Barrier function value
  dh: number;      // Barrier function derivative
}

/**
 * Apply Control Barrier Function to ensure obstacle avoidance
 *
 * The CBF ensures safety by enforcing the constraint:
 *   h(x) >= 0  (safe set)
 *   dh/dt >= -alpha * h  (ensures h stays positive)
 *
 * Where h is the barrier function representing signed distance to obstacle minus safety margin
 *
 * @param a_nom - Nominal (desired) acceleration [ax, ay]
 * @param state - Current robot state
 * @param obstacle - Obstacle to avoid
 * @param eps - Safety margin around obstacle
 * @param alpha - CBF aggressiveness parameter (higher = more conservative)
 * @returns Adjusted acceleration and CBF status
 */
export function cbfAdjust(
  a_nom: number[],
  state: RobotState,
  obstacle: Obstacle,
  eps: number,
  alpha: number = 3.5
): CBFResult {
  const { p, v } = state;
  const { c, r } = obstacle;

  // Compute relative position to obstacle center
  const dx = p.x - c.x;
  const dy = p.y - c.y;
  const dist = hypot(dx, dy);

  // Signed distance to obstacle surface
  const d = dist - r;

  // Barrier function: distance minus safety margin (must be >= 0)
  const h = d - eps;

  // Normal vector pointing away from obstacle
  const nx = dx / (dist + 1e-9);
  const ny = dy / (dist + 1e-9);

  // Time derivative of barrier function
  const dh = nx * v.x + ny * v.y;

  // CBF constraint: n · a >= b where b = -dh - alpha*h
  const b = -dh - alpha * h;

  // Check if nominal control satisfies constraint
  let a = [...a_nom];
  let active = false;

  const dot = nx * a[0] + ny * a[1];

  if (dot < b) {
    // Constraint violated - project acceleration to satisfy constraint
    // Find minimum correction to make n · a = b
    const denom = nx * nx + ny * ny + 1e-9;
    const corr = (b - dot) / denom;

    a[0] += nx * corr;
    a[1] += ny * corr;
    active = true;
  }

  return { a, active, h, dh };
}

/**
 * Check if current state is safe (not in collision)
 * @param state - Current robot state
 * @param obstacle - Obstacle to check against
 * @param eps - Safety margin
 * @returns True if state is safe
 */
export function isSafe(
  state: RobotState,
  obstacle: Obstacle,
  eps: number
): boolean {
  const { p } = state;
  const { c, r } = obstacle;

  const dx = p.x - c.x;
  const dy = p.y - c.y;
  const dist = hypot(dx, dy);

  return dist - r >= eps * 0.5;
}

/**
 * Compute barrier function value
 * @param state - Current robot state
 * @param obstacle - Obstacle
 * @param eps - Safety margin
 * @returns Barrier function value (positive = safe, negative = unsafe)
 */
export function barrierFunction(
  state: RobotState,
  obstacle: Obstacle,
  eps: number
): number {
  const { p } = state;
  const { c, r } = obstacle;

  const dx = p.x - c.x;
  const dy = p.y - c.y;
  const dist = hypot(dx, dy);

  const d = dist - r;
  return d - eps;
}
