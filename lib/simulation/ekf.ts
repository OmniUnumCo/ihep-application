/**
 * Extended Kalman Filter for state estimation
 */

import type { Vector, Matrix } from './types';
import { matAdd, matMul, matT, matSub, matInv2, matEye } from './math';

// Time step for integration
const dt = 1 / 60;

/**
 * System dynamics model: x = [px, py, vx, vy]
 * Predicts next state given current state and control input
 * @param x - Current state [px, py, vx, vy]
 * @param a - Control acceleration [ax, ay]
 * @returns Next predicted state
 */
export function dynamics(x: Vector, a: number[]): Vector {
  const px = x[0];
  const py = x[1];
  const vx = x[2];
  const vy = x[3];

  return new Float64Array([
    px + vx * dt + 0.5 * a[0] * dt * dt,
    py + vy * dt + 0.5 * a[1] * dt * dt,
    vx + a[0] * dt,
    vy + a[1] * dt,
  ]);
}

/**
 * Jacobian of the dynamics model (state transition matrix)
 * @returns F matrix (4x4)
 */
export function F_jac(): Matrix {
  return [
    [1, 0, dt, 0],
    [0, 1, 0, dt],
    [0, 0, 1, 0],
    [0, 0, 0, 1],
  ];
}

/**
 * Measurement matrix (observes position only)
 */
export const H_meas: Matrix = [
  [1, 0, 0, 0],
  [0, 1, 0, 0],
];

/**
 * Process noise covariance
 */
export const Q: Matrix = [
  [2, 0, 0, 0],
  [0, 2, 0, 0],
  [0, 0, 6, 0],
  [0, 0, 0, 6],
];

/**
 * Measurement noise covariance
 */
export const R: Matrix = [
  [30, 0],
  [0, 30],
];

export interface EKFState {
  x: Vector;        // State estimate [px, py, vx, vy]
  P: Matrix;        // Covariance matrix
  innovation: Vector; // Last measurement innovation
}

/**
 * Perform one EKF prediction and update step
 * @param state - Current EKF state
 * @param a - Control input [ax, ay]
 * @param z - Measurement [px_measured, py_measured]
 * @returns Updated EKF state
 */
export function ekfStep(
  state: EKFState,
  a: number[],
  z: Vector
): EKFState {
  const { x: x_curr, P: P_curr } = state;

  // --- PREDICT ---
  const xpred = dynamics(x_curr, a);
  const F = F_jac();
  const Ppred = matAdd(matMul(matMul(F, P_curr), matT(F)), Q);

  // --- UPDATE ---
  // Innovation (measurement residual)
  const zhat = [xpred[0], xpred[1]];
  const y = new Float64Array([z[0] - zhat[0], z[1] - zhat[1]]);

  // Innovation covariance
  const S = matAdd(matMul(matMul(H_meas, Ppred), matT(H_meas)), R);
  const S_inv = matInv2(S);

  // Kalman gain
  const K = matMul(matMul(Ppred, matT(H_meas)), S_inv); // 4x2

  // Update state: x_new = xpred + K * y
  const Ky = new Float64Array(4);
  for (let i = 0; i < 4; i++) {
    Ky[i] = K[i][0] * y[0] + K[i][1] * y[1];
  }

  const xnew = new Float64Array(4);
  for (let i = 0; i < 4; i++) {
    xnew[i] = xpred[i] + Ky[i];
  }

  // Update covariance: P_new = (I - K*H) * Ppred
  const I = matEye(4);
  const KH = matMul(K, H_meas);
  const IKH = matSub(I, KH);
  const Pnew = matMul(IKH, Ppred);

  return {
    x: xnew,
    P: Pnew,
    innovation: y,
  };
}

/**
 * Initialize EKF state
 * @param initialState - Initial state vector [px, py, vx, vy]
 * @param initialCovariance - Initial uncertainty (scalar for diagonal)
 * @returns Initialized EKF state
 */
export function initEKF(
  initialState: Vector,
  initialCovariance: number = 200
): EKFState {
  return {
    x: initialState,
    P: matEye(4, initialCovariance),
    innovation: new Float64Array([0, 0]),
  };
}
