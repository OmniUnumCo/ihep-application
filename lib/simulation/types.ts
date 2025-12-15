/**
 * Type definitions for 2D robot simulation with EKF and CBF
 */

export interface Vector2D {
  x: number;
  y: number;
}

export interface RobotState {
  p: Vector2D;  // position
  v: Vector2D;  // velocity
}

export interface EstimateState {
  x: Float64Array;  // [px, py, vx, vy]
}

export interface Target {
  x: number;
  y: number;
}

export interface Obstacle {
  c: Vector2D;  // center
  r: number;    // radius
}

export interface SimulationParams {
  biasx: number;
  biasy: number;
  noisep: number;
  speed: number;
  tol: number;
  eps: number;
  lc_gain: number;
}

export type Matrix = number[][];
export type Vector = Float64Array;

export type FailureType = 'near-collision' | 'success' | 'off-track' | null;
