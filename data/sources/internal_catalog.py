"""ProjectAI internal dataset catalog."""

from __future__ import annotations

from data.sources.internal import (
    InternalDatasetSource,
)


INTERNAL_DATASETS = {
    "instruction": InternalDatasetSource(
        dataset_id="projectai_instruction",
        name="ProjectAI Internal Instruction Dataset",
        dataset_type="instruction",
        local_path=(
            r"C:\DATA\AIDATA\raw\internal"
            r"\instruction"
        ),
        description=(
            "Vietnamese instruction data created "
            "specifically for ProjectAI."
        ),
    ),
    "conversation": InternalDatasetSource(
        dataset_id="projectai_conversation",
        name="ProjectAI Internal Conversation Dataset",
        dataset_type="conversation",
        local_path=(
            r"C:\DATA\AIDATA\raw\internal"
            r"\conversation"
        ),
        description=(
            "Vietnamese multi-turn conversations "
            "created for ProjectAI."
        ),
    ),
    "personality": InternalDatasetSource(
        dataset_id="projectai_personality",
        name="ProjectAI Internal Personality Dataset",
        dataset_type="personality",
        local_path=(
            r"C:\DATA\AIDATA\raw\internal"
            r"\personality"
        ),
        description=(
            "Behavior and response-style examples "
            "for ProjectAI Personality."
        ),
    ),
    "emotion": InternalDatasetSource(
        dataset_id="projectai_emotion",
        name="ProjectAI Internal Emotion Dataset",
        dataset_type="emotion",
        local_path=(
            r"C:\DATA\AIDATA\raw\internal"
            r"\emotion"
        ),
        description=(
            "Emotion-aware response examples "
            "created for ProjectAI."
        ),
    ),
    "preference": InternalDatasetSource(
        dataset_id="projectai_preference",
        name="ProjectAI Internal Preference Dataset",
        dataset_type="preference",
        local_path=(
            r"C:\DATA\AIDATA\raw\internal"
            r"\preference"
        ),
        description=(
            "Preference data used for response "
            "quality and alignment."
        ),
    ),
}