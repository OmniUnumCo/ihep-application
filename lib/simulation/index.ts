/**
 * Simulation Library - Main Exports
 *
 * A comprehensive 2D robot simulation library with:
 * - Extended Kalman Filter (EKF) for state estimation
 * - Control Barrier Function (CBF) for safety-critical control
 * - Mathematical utilities for matrix operations
 */

// Type definitions
export type {
  Vector2D,
  RobotState,
  EstimateState,
  Target,
  Obstacle,
  SimulationParams,
  Matrix,
  Vector,
  FailureType,
} from './types';

// Mathematical utilities
export {
  matEye,
  matAdd,
  matSub,
  matMul,
  matVec,
  matT,
  matInv2,
  hypot,
} from './math';

// Extended Kalman Filter
export {
  dynamics,
  F_jac,
  H_meas,
  Q,
  R,
  ekfStep,
  initEKF,
  type EKFState,
} from './ekf';

// Control Barrier Function
export {
  cbfAdjust,
  isSafe,
  barrierFunction,
  type CBFResult,
} from './cbf';
