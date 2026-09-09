"""Tests for ProjectAI model and training loop."""

import unittest

from self_built.layers import Linear
from self_built.losses import MSELoss
from self_built.model import Model
from self_built.network import Sequential
from self_built.optimizers import SGD
from self_built.tensor import Tensor


class ModelTests(unittest.TestCase):
    def test_forward(self):
        network = Sequential(Linear(2, 1, seed=1))
        model = Model(network, MSELoss(), SGD(network.parameters(), learning_rate=0.1))
        result = model.forward(Tensor([[1.0, 2.0]]))
        self.assertEqual(result.shape, (1, 1))

    def test_predict(self):
        network = Sequential(Linear(2, 1, seed=1))
        model = Model(network, MSELoss(), SGD(network.parameters(), learning_rate=0.1))
        result = model.predict(Tensor([[1.0, 2.0]]))
        self.assertEqual(result.shape, (1, 1))
        self.assertFalse(network.training)

    def test_train_and_eval(self):
        network = Sequential(Linear(2, 1, seed=1))
        model = Model(network, MSELoss(), SGD(network.parameters(), learning_rate=0.1))
        model.eval()
        self.assertFalse(network.training)
        model.train()
        self.assertTrue(network.training)

    def test_fit_returns_history(self):
        network = Sequential(Linear(1, 1, seed=1))
        model = Model(network, MSELoss(), SGD(network.parameters(), learning_rate=0.1))
        history = model.fit(Tensor([[1.0], [2.0], [3.0]]), Tensor([[2.0], [4.0], [6.0]]), epochs=5)
        self.assertEqual(len(history.losses), 5)
        self.assertTrue(all(isinstance(value, float) for value in history.losses))

    def test_training_reduces_loss(self):
        network = Sequential(Linear(1, 1, seed=1))
        model = Model(network, MSELoss(), SGD(network.parameters(), learning_rate=0.01))
        inputs = Tensor([[1.0], [2.0], [3.0]])
        targets = Tensor([[2.0], [4.0], [6.0]])
        history = model.fit(inputs, targets, epochs=100)
        self.assertLess(history.losses[-1], history.losses[0])

    def test_invalid_epochs(self):
        network = Sequential(Linear(1, 1, seed=1))
        model = Model(network, MSELoss(), SGD(network.parameters(), learning_rate=0.01))
        with self.assertRaises(ValueError):
            model.fit(Tensor([[1.0]]), Tensor([[2.0]]), epochs=0)

    def test_parameters(self):
        network = Sequential(Linear(2, 3), Linear(3, 1))
        model = Model(network, MSELoss(), SGD(network.parameters()))
        self.assertEqual(len(model.parameters()), 4)


if __name__ == "__main__":
    unittest.main()