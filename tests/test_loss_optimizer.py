"""Tests for ProjectAI loss functions and optimizers."""

import math
import unittest

from self_built.losses import BinaryCrossEntropyLoss, MSELoss
from self_built.optimizers import SGD
from self_built.tensor import Tensor


class MSELossTests(unittest.TestCase):
    def test_forward(self):
        loss = MSELoss()
        result = loss.forward(Tensor([1.0, 3.0]), Tensor([2.0, 1.0]))
        self.assertAlmostEqual(result, 2.5)

    def test_backward(self):
        loss = MSELoss()
        loss.forward(Tensor([1.0, 3.0]), Tensor([2.0, 1.0]))
        result = loss.backward()
        self.assertEqual(result.tolist(), [-1.0, 2.0])

    def test_shape_mismatch(self):
        loss = MSELoss()
        with self.assertRaises(ValueError):
            loss.forward(Tensor([1.0, 2.0]), Tensor([1.0]))

    def test_backward_before_forward(self):
        with self.assertRaises(RuntimeError):
            MSELoss().backward()


class BinaryCrossEntropyLossTests(unittest.TestCase):
    def test_forward(self):
        loss = BinaryCrossEntropyLoss()
        result = loss.forward(Tensor([0.8, 0.2]), Tensor([1.0, 0.0]))
        expected = -(math.log(0.8) + math.log(0.8)) / 2
        self.assertAlmostEqual(result, expected)

    def test_backward(self):
        loss = BinaryCrossEntropyLoss()
        loss.forward(Tensor([0.8]), Tensor([1.0]))
        result = loss.backward()
        expected = (0.8 - 1.0) / (0.8 * 0.2)
        self.assertAlmostEqual(result[0], expected)

    def test_invalid_probability(self):
        loss = BinaryCrossEntropyLoss()
        with self.assertRaises(ValueError):
            loss.forward(Tensor([0.0]), Tensor([1.0]))

    def test_invalid_target(self):
        loss = BinaryCrossEntropyLoss()
        with self.assertRaises(ValueError):
            loss.forward(Tensor([0.5]), Tensor([2.0]))


class SGDTests(unittest.TestCase):
    def test_step(self):
        parameter = Tensor([1.0, 2.0])
        optimizer = SGD([parameter], learning_rate=0.1)
        optimizer.step([Tensor([0.5, -1.0])])
        self.assertEqual(parameter.tolist(), [0.95, 2.1])

    def test_multiple_parameters(self):
        first = Tensor([1.0, 2.0])
        second = Tensor([[3.0, 4.0]])
        optimizer = SGD([first, second], learning_rate=0.1)
        optimizer.step([Tensor([1.0, 1.0]), Tensor([[2.0, 4.0]])])
        self.assertEqual(first.tolist(), [0.9, 1.9])
        self.assertEqual(second.tolist(), [[2.8, 3.6]])

    def test_shape_mismatch(self):
        parameter = Tensor([1.0, 2.0])
        optimizer = SGD([parameter])
        with self.assertRaises(ValueError):
            optimizer.step([Tensor([1.0])])

    def test_gradient_count_mismatch(self):
        parameter = Tensor([1.0, 2.0])
        optimizer = SGD([parameter])
        with self.assertRaises(ValueError):
            optimizer.step([])

    def test_learning_rate_validation(self):
        with self.assertRaises(ValueError):
            SGD([Tensor([1.0])], learning_rate=0.0)

    def test_zero_grad(self):
        parameter = Tensor([1.0, 2.0])
        optimizer = SGD([parameter])
        optimizer.zero_grad()
        self.assertEqual(parameter.tolist(), [0.0, 0.0])


if __name__ == "__main__":
    unittest.main()