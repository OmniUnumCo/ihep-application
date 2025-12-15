/**
 * Mathematical utilities for matrix operations
 */

import type { Matrix, Vector } from './types';

/**
 * Create an identity matrix of size n x n
 * @param n - Size of the matrix
 * @param s - Scale factor for diagonal elements
 * @returns Identity matrix scaled by s
 */
export function matEye(n: number, s: number = 1): Matrix {
  const M: Matrix = Array(n)
    .fill(0)
    .map(() => Array(n).fill(0));
  for (let i = 0; i < n; i++) {
    M[i][i] = s;
  }
  return M;
}

/**
 * Add two matrices
 * @param A - First matrix
 * @param B - Second matrix
 * @returns Sum of A and B
 */
export function matAdd(A: Matrix, B: Matrix): Matrix {
  return A.map((r, i) => r.map((v, j) => v + B[i][j]));
}

/**
 * Subtract two matrices
 * @param A - First matrix
 * @param B - Second matrix
 * @returns Difference A - B
 */
export function matSub(A: Matrix, B: Matrix): Matrix {
  return A.map((r, i) => r.map((v, j) => v - B[i][j]));
}

/**
 * Multiply two matrices
 * @param A - First matrix (m x k)
 * @param B - Second matrix (k x n)
 * @returns Product matrix (m x n)
 */
export function matMul(A: Matrix, B: Matrix): Matrix {
  const m = A.length;
  const n = B[0].length;
  const k = B.length;
  const C: Matrix = Array(m)
    .fill(0)
    .map(() => Array(n).fill(0));

  for (let i = 0; i < m; i++) {
    for (let j = 0; j < n; j++) {
      let s = 0;
      for (let t = 0; t < k; t++) {
        s += A[i][t] * B[t][j];
      }
      C[i][j] = s;
    }
  }
  return C;
}

/**
 * Multiply matrix by vector
 * @param A - Matrix (m x n)
 * @param x - Vector (length n)
 * @returns Result vector (length m)
 */
export function matVec(A: Matrix, x: Vector): Vector {
  const y = new Float64Array(A.length);
  for (let i = 0; i < A.length; i++) {
    let s = 0;
    for (let j = 0; j < x.length; j++) {
      s += A[i][j] * x[j];
    }
    y[i] = s;
  }
  return y;
}

/**
 * Transpose a matrix
 * @param A - Input matrix (m x n)
 * @returns Transposed matrix (n x m)
 */
export function matT(A: Matrix): Matrix {
  const m = A.length;
  const n = A[0].length;
  const T: Matrix = Array(n)
    .fill(0)
    .map(() => Array(m).fill(0));

  for (let i = 0; i < m; i++) {
    for (let j = 0; j < n; j++) {
      T[j][i] = A[i][j];
    }
  }
  return T;
}

/**
 * Compute inverse of 2x2 matrix
 * @param A - 2x2 matrix
 * @returns Inverse of A
 */
export function matInv2(A: Matrix): Matrix {
  const [a, b] = A[0];
  const [c, d] = A[1];
  const det = a * d - b * c || 1e-9;
  return [
    [d / det, -b / det],
    [-c / det, a / det],
  ];
}

/**
 * Safe hypot function for distance calculation
 * @param x - X component
 * @param y - Y component
 * @returns Euclidean distance sqrt(x^2 + y^2)
 */
export function hypot(x: number, y: number): number {
  return Math.sqrt(x * x + y * y);
}
