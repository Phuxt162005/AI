"""Tests for the self-built Tensor foundation."""

import unittest
from self_built.tensor import Tensor, ones, zeros

class TensorConstructionTests(unittest.TestCase):
    def test_scalar(self):
        tensor = Tensor(5)
        self.assertEqual(tensor.shape, ())
        self.assertEqual(tensor.ndim, 0)
        self.assertEqual(tensor.size, 1)
        self.assertEqual(tensor.tolist(), 5)

    def test_vector(self):
        tensor = Tensor([1, 2, 3])
        self.assertEqual(tensor.shape, (3,))
        self.assertEqual(tensor.ndim, 1)
        self.assertEqual(tensor.dtype, int)

    def test_matrix(self):
        tensor = Tensor([[1, 2], [3, 4]])
        self.assertEqual(tensor.shape, (2, 2))
        self.assertEqual(tensor.tolist(), [[1, 2], [3, 4]])

    def test_higher_dimensional_tensor(self):
        tensor = Tensor([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
        self.assertEqual(tensor.shape, (2, 2, 2))
        self.assertEqual(tensor.size, 8)

    def test_ragged_data_is_rejected(self):
        with self.assertRaises(ValueError):
            Tensor([[1, 2], [3]])

    def test_explicit_shape(self):
        tensor = Tensor([1, 2, 3, 4], shape=(2, 2))
        self.assertEqual(tensor.tolist(), [[1, 2], [3, 4]])

class TensorIndexingTests(unittest.TestCase):
    def setUp(self):
        self.tensor = Tensor([[1, 2], [3, 4]])

    def test_indexing(self):
        self.assertEqual(self.tensor[0, 1], 2)
        self.assertEqual(self.tensor[-1, -1], 4)

    def test_assignment(self):
        self.tensor[1, 0] = 9
        self.assertEqual(self.tensor[1, 0], 9)

    def test_invalid_index_count(self):
        with self.assertRaises(IndexError):
            _ = self.tensor[0]


class TensorShapeOperationTests(unittest.TestCase):
    def test_reshape(self):
        tensor = Tensor([[1, 2], [3, 4]])
        reshaped = tensor.reshape(4)
        self.assertEqual(reshaped.shape, (4,))
        self.assertEqual(reshaped.tolist(), [1, 2, 3, 4])

    def test_invalid_reshape(self):
        tensor = Tensor([1, 2, 3])
        with self.assertRaises(ValueError):
            tensor.reshape(2, 2)

    def test_transpose_matrix(self):
        tensor = Tensor([[1, 2, 3], [4, 5, 6]])
        transposed = tensor.transpose()
        self.assertEqual(transposed.shape, (3, 2))
        self.assertEqual(transposed.tolist(), [[1, 4], [2, 5], [3, 6]])

    def test_transpose_higher_dimensional_tensor(self):
        tensor = Tensor([[[1, 2], [3, 4]]])
        transposed = tensor.transpose()
        self.assertEqual(transposed.shape, (1, 2, 2))
        self.assertEqual(transposed.tolist(), [[[1, 3], [2, 4]]])

class TensorArithmeticTests(unittest.TestCase):
    def setUp(self):
        self.left = Tensor([[1, 2], [3, 4]])
        self.right = Tensor([[5, 6], [7, 8]])

    def test_add_tensor(self):
        self.assertEqual((self.left + self.right).tolist(), [[6, 8], [10, 12]])

    def test_sub_tensor(self):
        self.assertEqual((self.right - self.left).tolist(), [[4, 4], [4, 4]])

    def test_mul_tensor(self):
        self.assertEqual((self.left * self.right).tolist(), [[5, 12], [21, 32]])

    def test_div_tensor(self):
        self.assertEqual((self.right / self.left).tolist(), [[5.0, 3.0], [7 / 3, 2.0]])

    def test_scalar_operations(self):
        self.assertEqual((self.left + 1).tolist(), [[2, 3], [4, 5]])
        self.assertEqual((self.left - 1).tolist(), [[0, 1], [2, 3]])
        self.assertEqual((self.left * 2).tolist(), [[2, 4], [6, 8]])
        self.assertEqual((self.left / 2).tolist(), [[0.5, 1.0], [1.5, 2.0]])

    def test_shape_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            _ = self.left + Tensor([1, 2])

    def test_division_by_zero_is_rejected(self):
        with self.assertRaises(ZeroDivisionError):
            _ = self.left / 0

class TensorMatrixTests(unittest.TestCase):
    def test_matrix_multiplication(self):
        left = Tensor([[1, 2, 3], [4, 5, 6]])
        right = Tensor([[7, 8], [9, 10], [11, 12]])
        result = left @ right
        self.assertEqual(result.shape, (2, 2))
        self.assertEqual(result.tolist(), [[58, 64], [139, 154]])

    def test_invalid_matrix_shapes(self):
        with self.assertRaises(ValueError):
            _ = Tensor([[1, 2]]) @ Tensor([[1, 2]])

    def test_non_matrix_matmul_is_rejected(self):
        with self.assertRaises(ValueError):
            _ = Tensor([1, 2]) @ Tensor([[1], [2]])

class TensorReductionAndFactoryTests(unittest.TestCase):
    def test_sum(self):
        self.assertEqual(Tensor([[1, 2], [3, 4]]).sum(), 10)

    def test_mean(self):
        self.assertEqual(Tensor([[1, 2], [3, 4]]).mean(), 2.5)

    def test_zeros(self):
        tensor = zeros(2, 3)
        self.assertEqual(tensor.shape, (2, 3))
        self.assertEqual(tensor.tolist(), [[0, 0, 0], [0, 0, 0]])

    def test_ones(self):
        tensor = ones((2, 2))
        self.assertEqual(tensor.tolist(), [[1, 1], [1, 1]])

    def test_empty_dimension(self):
        tensor = zeros(0, 3)
        self.assertEqual(tensor.shape, (0, 3))
        self.assertEqual(tensor.size, 0)

if __name__ == "__main__":
    unittest.main()