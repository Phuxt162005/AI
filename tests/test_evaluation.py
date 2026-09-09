"""Evaluation tests for ProjectAI."""

import unittest

from evaluation.evaluate import evaluate_model
from self_built.layers import Linear, ReLU
from self_built.losses import BinaryCrossEntropyLoss, MSELoss
from self_built.model import Model
from self_built.network import Sequential
from self_built.optimizers import SGD
from self_built.tensor import Tensor
from training.loop import TrainingLoop


class EvaluationTests(unittest.TestCase):
    def create_model(self) -> Model:
        network = Sequential(Linear(1, 1, seed=1))
        return Model(network, MSELoss(), SGD(network.parameters(), learning_rate=0.01))

    def test_model_evaluation(self):
        model = self.create_model()
        inputs = Tensor([[1.0], [2.0], [3.0]])
        targets = Tensor([[2.0], [4.0], [6.0]])
        result = evaluate_model(model, inputs, targets)
        self.assertIn("loss", result)
        self.assertIsInstance(result["loss"], float)
        self.assertGreaterEqual(result["loss"], 0.0)

    def test_evaluation_does_not_train_model(self):
        model = self.create_model()
        inputs = Tensor([[1.0], [2.0]])
        targets = Tensor([[2.0], [4.0]])
        before = [parameter.data for parameter in model.parameters()]
        evaluate_model(model, inputs, targets)
        after = [parameter.data for parameter in model.parameters()]
        self.assertEqual(before, after)

    def test_training_improves_evaluation_loss(self):
        model = self.create_model()
        inputs = Tensor([[1.0], [2.0], [3.0]])
        targets = Tensor([[2.0], [4.0], [6.0]])
        before = evaluate_model(model, inputs, targets)["loss"]
        TrainingLoop(model).fit(inputs, targets, epochs=100)
        after = evaluate_model(model, inputs, targets)["loss"]
        self.assertLess(after, before)

    def test_relu_evaluation(self):
        network = Sequential(Linear(1, 2, seed=1), ReLU())
        model = Model(network, MSELoss(), SGD(network.parameters(), learning_rate=0.01))
        result = evaluate_model(model, Tensor([[1.0], [2.0]]), Tensor([[1.0, 1.0], [2.0, 2.0]]))
        self.assertGreaterEqual(result["loss"], 0.0)

    def test_binary_cross_entropy_evaluation(self):
        network = Sequential(Linear(1, 1, seed=1))
        model = Model(network, BinaryCrossEntropyLoss(), SGD(network.parameters(), learning_rate=0.01))
        inputs = Tensor([[0.0], [1.0]])
        targets = Tensor([[0.0], [1.0]])
        result = evaluate_model(model, inputs, targets)
        self.assertGreaterEqual(result["loss"], 0.0)


if __name__ == "__main__":
    unittest.main()