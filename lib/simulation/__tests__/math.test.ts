/**
 * Unit tests for mathematical utility functions
 */

import { describe, it } from 'node:test';
import assert from 'node:assert';
import {
  matEye,
  matAdd,
  matSub,
  matMul,
  matVec,
  matT,
  matInv2,
  hypot,
} from '../math';

describe('Math Utilities', () => {
  describe('matEye', () => {
    it('should create identity matrix', () => {
      const I = matEye(3);
      assert.deepStrictEqual(I, [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
      ]);
    });

    it('should create scaled identity matrix', () => {
      const I = matEye(2, 5);
      assert.deepStrictEqual(I, [
        [5, 0],
        [0, 5],
      ]);
    });
  });

  describe('matAdd', () => {
    it('should add two matrices', () => {
      const A = [
        [1, 2],
        [3, 4],
      ];
      const B = [
        [5, 6],
        [7, 8],
      ];
      const C = matAdd(A, B);
      assert.deepStrictEqual(C, [
        [6, 8],
        [10, 12],
      ]);
    });

    it('should handle zero matrices', () => {
      const A = [
        [1, 2],
        [3, 4],
      ];
      const Z = [
        [0, 0],
        [0, 0],
      ];
      const C = matAdd(A, Z);
      assert.deepStrictEqual(C, A);
    });
  });

  describe('matSub', () => {
    it('should subtract two matrices', () => {
      const A = [
        [5, 6],
        [7, 8],
      ];
      const B = [
        [1, 2],
        [3, 4],
      ];
      const C = matSub(A, B);
      assert.deepStrictEqual(C, [
        [4, 4],
        [4, 4],
      ]);
    });

    it('should return zero when subtracting same matrix', () => {
      const A = [
        [1, 2],
        [3, 4],
      ];
      const C = matSub(A, A);
      assert.deepStrictEqual(C, [
        [0, 0],
        [0, 0],
      ]);
    });
  });

  describe('matMul', () => {
    it('should multiply two matrices', () => {
      const A = [
        [1, 2],
        [3, 4],
      ];
      const B = [
        [2, 0],
        [1, 2],
      ];
      const C = matMul(A, B);
      assert.deepStrictEqual(C, [
        [4, 4],
        [10, 8],
      ]);
    });

    it('should multiply by identity', () => {
      const A = [
        [1, 2],
        [3, 4],
      ];
      const I = matEye(2);
      const C = matMul(A, I);
      assert.deepStrictEqual(C, A);
    });

    it('should handle non-square matrices', () => {
      const A = [[1, 2, 3]]; // 1x3
      const B = [
        [1],
        [2],
        [3],
      ]; // 3x1
      const C = matMul(A, B); // Should be 1x1
      assert.deepStrictEqual(C, [[14]]);
    });
  });

  describe('matVec', () => {
    it('should multiply matrix by vector', () => {
      const A = [
        [1, 2],
        [3, 4],
      ];
      const x = new Float64Array([2, 3]);
      const y = matVec(A, x);

      assert.strictEqual(y.length, 2);
      assert.strictEqual(y[0], 8); // 1*2 + 2*3
      assert.strictEqual(y[1], 18); // 3*2 + 4*3
    });

    it('should handle zero vector', () => {
      const A = [
        [1, 2],
        [3, 4],
      ];
      const x = new Float64Array([0, 0]);
      const y = matVec(A, x);

      assert.strictEqual(y[0], 0);
      assert.strictEqual(y[1], 0);
    });
  });

  describe('matT', () => {
    it('should transpose a matrix', () => {
      const A = [
        [1, 2, 3],
        [4, 5, 6],
      ];
      const AT = matT(A);
      assert.deepStrictEqual(AT, [
        [1, 4],
        [2, 5],
        [3, 6],
      ]);
    });

    it('should transpose identity to itself', () => {
      const I = matEye(3);
      const IT = matT(I);
      assert.deepStrictEqual(IT, I);
    });
  });

  describe('matInv2', () => {
    it('should invert a 2x2 matrix', () => {
      const A = [
        [4, 7],
        [2, 6],
      ];
      const Ainv = matInv2(A);

      // Check that A * Ainv = I
      const I = matMul(A, Ainv);

      // Allow small floating point errors
      assert.ok(Math.abs(I[0][0] - 1) < 1e-10);
      assert.ok(Math.abs(I[0][1]) < 1e-10);
      assert.ok(Math.abs(I[1][0]) < 1e-10);
      assert.ok(Math.abs(I[1][1] - 1) < 1e-10);
    });

    it('should handle identity matrix', () => {
      const I = [
        [1, 0],
        [0, 1],
      ];
      const Iinv = matInv2(I);

      // Check each element (handle -0 vs 0)
      assert.strictEqual(Math.abs(Iinv[0][0] - 1) < 1e-10, true);
      assert.strictEqual(Math.abs(Iinv[0][1]) < 1e-10, true);
      assert.strictEqual(Math.abs(Iinv[1][0]) < 1e-10, true);
      assert.strictEqual(Math.abs(Iinv[1][1] - 1) < 1e-10, true);
    });

    it('should handle near-singular matrices', () => {
      const A = [
        [1, 2],
        [2, 4.00001],
      ]; // Nearly singular
      const Ainv = matInv2(A);

      // Should not throw, uses 1e-9 epsilon
      assert.ok(Array.isArray(Ainv));
      assert.strictEqual(Ainv.length, 2);
    });
  });

  describe('hypot', () => {
    it('should compute Euclidean distance', () => {
      assert.strictEqual(hypot(3, 4), 5);
      assert.strictEqual(hypot(0, 0), 0);
    });

    it('should handle negative values', () => {
      assert.strictEqual(hypot(-3, -4), 5);
      assert.strictEqual(hypot(3, -4), 5);
    });

    it('should compute correct distance', () => {
      const dist = hypot(1, 1);
      assert.ok(Math.abs(dist - Math.SQRT2) < 1e-10);
    });
  });
});
