"""Tests for ProjectAI neural network layers."""

import math
import unittest

from self_built.layers import Linear, ReLU, Sigmoid, Tanh
from self_built.network import Sequential
from self_built.tensor import Tensor


class LinearTests(unittest.TestCase):
    def test_forward_vector(self):
        layer = Linear(2, 2, seed=1)
        layer.weight = Tensor([[1.0, 2.0], [3.0, 4.0]])
        layer.bias = Tensor([0.5, -0.5])
        result = layer.forward(Tensor([2.0, 3.0]))
        self.assertEqual(result.shape, (2,))
        self.assertEqual(result.tolist(), [11.5, 15.5])

    def test_forward_batch(self):
        layer = Linear(2, 1, seed=1)
        layer.weight = Tensor([[2.0], [3.0]])
        layer.bias = Tensor([1.0])
        result = layer.forward(Tensor([[1.0, 2.0], [3.0, 4.0]]))
        self.assertEqual(result.tolist(), [[9.0], [19.0]])

    def test_backward(self):
        layer = Linear(2, 1, seed=1)
        layer.weight = Tensor([[2.0], [3.0]])
        layer.bias = Tensor([1.0])
        layer.forward(Tensor([[1.0, 2.0], [3.0, 4.0]]))
        grad_input = layer.backward(Tensor([[1.0], [2.0]]))
        self.assertEqual(grad_input.tolist(), [[2.0, 3.0], [4.0, 6.0]])
        self.assertEqual(layer.grad_weight.tolist(), [[7.0], [10.0]])
        self.assertEqual(layer.grad_bias.tolist(), [3.0])

    def test_invalid_input_shape(self):
        layer = Linear(3, 2)
        with self.assertRaises(ValueError):
            layer.forward(Tensor([1.0, 2.0]))


class ActivationTests(unittest.TestCase):
    def test_relu_forward(self):
        result = ReLU().forward(Tensor([-2.0, 0.0, 3.0]))
        self.assertEqual(result.tolist(), [0.0, 0.0, 3.0])

    def test_relu_backward(self):
        layer = ReLU()
        layer.forward(Tensor([-2.0, 2.0]))
        result = layer.backward(Tensor([5.0, 5.0]))
        self.assertEqual(result.tolist(), [0.0, 5.0])

    def test_sigmoid_forward(self):
        result = Sigmoid().forward(Tensor([0.0]))
        self.assertAlmostEqual(result[0], 0.5)

    def test_sigmoid_backward(self):
        layer = Sigmoid()
        layer.forward(Tensor([0.0]))
        result = layer.backward(Tensor([1.0]))
        self.assertAlmostEqual(result[0], 0.25)

    def test_tanh_forward(self):
        result = Tanh().forward(Tensor([0.0, 1.0]))
        self.assertAlmostEqual(result[0], 0.0)
        self.assertAlmostEqual(result[1], math.tanh(1.0), places=6)


class SequentialTests(unittest.TestCase):
    def test_forward(self):
        model = Sequential(Linear(2, 3, seed=1), ReLU(), Linear(3, 1, seed=2))
        result = model.forward(Tensor([[1.0, 2.0], [3.0, 4.0]]))
        self.assertEqual(result.shape, (2, 1))

    def test_backward(self):
        model = Sequential(Linear(2, 2, seed=1), ReLU(), Linear(2, 1, seed=2))
        model.forward(Tensor([[1.0, 2.0]]))
        result = model.backward(Tensor([[1.0]]))
        self.assertEqual(result.shape, (1, 2))

    def test_parameters_and_gradients(self):
        model = Sequential(Linear(2, 3), ReLU(), Linear(3, 1))
        self.assertEqual(len(model.parameters()), 4)
        self.assertEqual(len(model.gradients()), 4)

    def test_train_eval(self):
        model = Sequential(Linear(2, 2), ReLU())
        model.eval()
        self.assertFalse(model.training)
        self.assertTrue(all(not layer.training for layer in model.layers))
        model.train()
        self.assertTrue(model.training)
        self.assertTrue(all(layer.training for layer in model.layers))


if __name__ == "__main__":
    unittest.main()