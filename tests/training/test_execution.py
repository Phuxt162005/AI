from data.dataset.dataset import (
    DatasetRecord,
    TrainingDataset,
)
from self_built.tensor import Tensor
from training import (
    TrainingConfiguration,
    TrainingExecutor,
    TrainingLoop,
)

dataset = TrainingDataset(
    name="toy-regression",
    version="1.0.0",
    dataset_type="instruction",
    records=[
        DatasetRecord(
            record_id="sample-001",
            input="0.0",
            output="0.0",
        ),
        DatasetRecord(
            record_id="sample-002",
            input="1.0",
            output="2.0",
        ),
    ],
)

def encode_batch(batch):
    inputs = Tensor(
        [[float(value)] for value in batch.inputs]
    )
    targets = Tensor(
        [[float(value)] for value in batch.outputs]
    )
    return inputs, targets

configuration = TrainingConfiguration(
    epochs=5,
    batch_size=2,
    shuffle=True,
    gradient_accumulation_steps=1,
    dataset_name="toy-regression",
    dataset_version="1.0.0",
    dataset_type="instruction",
)

# model phải là một Model đã được khởi tạo
# với network, loss và optimizer tương thích.
loop = TrainingLoop(
    model=model,
    configuration=configuration,
)

executor = TrainingExecutor(
    training_loop=loop,
    dataset=dataset,
    batch_encoder=encode_batch,
)

history = executor.run()
print(history.losses)