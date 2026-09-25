"""Builder for ProjectAI internal training datasets."""

from __future__ import annotations

from typing import Any

from data.dataset.dataset import (
    DatasetRecord,
    TrainingDataset,
)
from data.sources.internal import (
    InternalDatasetSource,
)


class InternalDatasetBuilder:
    """Build a TrainingDataset from internal records."""

    def __init__(
        self,
        source: InternalDatasetSource,
        version: str | None = None,
    ) -> None:
        self.source = source
        dataset_version = (
            version
            if version is not None
            else source.version
        )
        self.dataset = TrainingDataset(
            name=source.name,
            version=dataset_version,
            dataset_type=source.dataset_type,
            metadata={
                "source_id": source.source_id,
                "source_type": "internal",
                "language": source.language,
                "local_path": source.local_path,
            },
        )

    def add(
        self,
        record_id: str,
        data: dict[str, Any],
    ) -> None:
        """Validate and add one internal dataset record."""

        if not record_id.strip():
            raise ValueError("record_id must not be empty")

        normalized = self._normalize_record(data)
        self.dataset.add_record(
            DatasetRecord(
                record_id=record_id,
                input=normalized["input"],
                output=normalized.get("output"),
                labels=normalized.get("labels", {}),
                metadata=normalized.get(
                    "metadata",
                    {},
                ),
            )
        )

    def add_many(
        self,
        records: list[dict[str, Any]],
    ) -> None:
        """Validate and add multiple records."""

        for index, record in enumerate(records):
            record_id = str(record.get("record_id", f"{self.source.dataset_id}_{index}"))
            data = dict(record)
            data.pop("record_id", None)
            self.add(record_id=record_id,data=data)

    def build(self) -> TrainingDataset:
        """Return the constructed internal dataset."""

        return self.dataset

    def _normalize_record(self, data: dict[str, Any]) -> dict[str, Any]:
        """Validate the structure for the dataset type."""

        if not isinstance(data, dict):
            raise TypeError("Internal dataset record must be a dictionary")

        if self.source.dataset_type == "instruction":
            return self._normalize_instruction(data)

        if self.source.dataset_type == "conversation":
            return self._normalize_conversation(data)

        if self.source.dataset_type == "personality":
            return self._normalize_personality(data)

        if self.source.dataset_type == "emotion":
            return self._normalize_emotion(data)

        if self.source.dataset_type == "preference":
            return self._normalize_preference(data)

        raise ValueError(
            f"Unsupported internal dataset type: "
            f"{self.source.dataset_type}"
        )

    @staticmethod
    def _normalize_instruction(data: dict[str, Any]) -> dict[str, Any]:
        """Normalize an instruction record."""

        instruction = data.get("instruction")
        input_text = data.get("input", "")
        output = data.get("expected_output")

        if not instruction:
            raise ValueError("Instruction record requires " "'instruction'")
        if not output:
            raise ValueError("Instruction record requires " "'expected_output'")

        return {
            "input": (
                f"{instruction}\n"
                f"{input_text}"
                if input_text
                else instruction
            ),
            "output": output,
            "labels": data.get("labels", {}),
            "metadata": data.get("metadata", {}),
        }

    @staticmethod
    def _normalize_conversation(data: dict[str, Any]) -> dict[str, Any]:
        """Normalize a conversation record."""

        messages = data.get("messages")

        if not isinstance(messages, list):
            raise ValueError(
                "Conversation record requires "
                "'messages' as a list"
            )
        if not messages:
            raise ValueError(
                "Conversation record must contain "
                "at least one message"
            )
        for message in messages:
            if not isinstance(message, dict):
                raise ValueError(
                    "Each conversation message "
                    "must be a dictionary"
                )

            if not message.get("role"):
                raise ValueError(
                    "Conversation message requires "
                    "'role'"
                )

            if "content" not in message:
                raise ValueError(
                    "Conversation message requires "
                    "'content'"
                )

        return {
            "input": messages,
            "output": data.get("expected_output"),
            "labels": data.get("labels", {}),
            "metadata": data.get("metadata", {}),
        }

    @staticmethod
    def _normalize_personality(data: dict[str, Any]) -> dict[str, Any]:
        """Normalize a personality record."""

        required = (
            "situation",
            "context",
            "desired_behavior",
            "expected_response",
        )

        for field_name in required:
            if not data.get(field_name):
                raise ValueError(
                    "Personality record requires "
                    f"'{field_name}'"
                )

        return {
            "input": (
                f"Situation: {data['situation']}\n"
                f"Context: {data['context']}"
            ),
            "output": data["expected_response"],
            "labels": {
                "desired_behavior": (data["desired_behavior"])
            },
            "metadata": data.get("metadata", {}),
        }

    @staticmethod
    def _normalize_emotion(data: dict[str, Any]) -> dict[str, Any]:
        """Normalize an emotion record."""

        required = (
            "input",
            "emotion",
            "expected_response",
        )

        for field_name in required:
            if not data.get(field_name):
                raise ValueError(
                    "Emotion record requires "
                    f"'{field_name}'"
                )

        labels = dict(data.get("labels", {}))
        labels["emotion"] = data["emotion"]

        if "emotion_intensity" in data:
            labels["emotion_intensity"] = (data["emotion_intensity"])

        return {
            "input": data["input"],
            "output": data["expected_response"],
            "labels": labels,
            "metadata": data.get("metadata", {}),
        }

    @staticmethod
    def _normalize_preference(data: dict[str, Any]) -> dict[str, Any]:
        """Normalize a preference record."""

        required = (
            "input",
            "chosen",
            "rejected",
        )

        for field_name in required:
            if not data.get(field_name):
                raise ValueError(
                    "Preference record requires "
                    f"'{field_name}'"
                )

        return {
            "input": data["input"],
            "output": data["chosen"],
            "labels": {"rejected": data["rejected"]},
            "metadata": data.get("metadata", {}),
        }