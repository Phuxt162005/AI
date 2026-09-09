"""Tests for ProjectAI model and training loop."""

import unittest

from self_built.layers import Linear
from self_built.losses import MSELoss
from self_built.model import Model
from self_built.network import Sequential
from self_built.optimizers import SGD
from self_built.tensor import Tensor
from training.loop import TrainingLoop


class ModelTrainingTests(unittest.TestCase):
    def create_model(self) -> Model:
        network = Sequential(Linear(1, 1, seed=1))
        return Model(network, MSELoss(), SGD(network.parameters(), learning_rate=0.01))

    def test_model_forward(self):
        model = self.create_model()
        result = model.forward(Tensor([[1.0], [2.0]]))
        self.assertEqual(result.shape, (2, 1))

    def test_model_predict(self):
        model = self.create_model()
        result = model.predict(Tensor([[1.0]]))
        self.assertEqual(result.shape, (1, 1))
        self.assertFalse(model.network.training)

    def test_training_loop_returns_history(self):
        model = self.create_model()
        loop = TrainingLoop(model)
        history = loop.fit(Tensor([[1.0], [2.0], [3.0]]), Tensor([[2.0], [4.0], [6.0]]), epochs=5)
        self.assertEqual(len(history.losses), 5)
        self.assertTrue(all(isinstance(value, float) for value in history.losses))

    def test_training_reduces_loss(self):
        model = self.create_model()
        loop = TrainingLoop(model)
        inputs = Tensor([[1.0], [2.0], [3.0]])
        targets = Tensor([[2.0], [4.0], [6.0]])
        history = loop.fit(inputs, targets, epochs=100)
        self.assertLess(history.losses[-1], history.losses[0])

    def test_train_batch(self):
        model = self.create_model()
        loop = TrainingLoop(model)
        loss = loop.train_batch(Tensor([[1.0], [2.0]]), Tensor([[2.0], [4.0]]))
        self.assertIsInstance(loss, float)

    def test_invalid_epochs(self):
        model = self.create_model()
        loop = TrainingLoop(model)
        with self.assertRaises(ValueError):
            loop.fit(Tensor([[1.0]]), Tensor([[2.0]]), epochs=0)


if __name__ == "__main__":
    unittest.main()