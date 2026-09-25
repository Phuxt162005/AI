"""ProjectAI Hugging Face dataset catalog."""

from __future__ import annotations

from data.sources.huggingface import (
    HuggingFaceDatasetSource,
)


HF_DATASETS = {
    # ---------------------------------------------------------
    # PRE-TRAINING
    # ---------------------------------------------------------

    "pretraining_fsnaix": HuggingFaceDatasetSource(
        dataset_id="fsnaix/vietnamese-corpus-large",
        url=(
            "https://huggingface.co/datasets/"
            "fsnaix/vietnamese-corpus-large"
        ),
        dataset_type="pre_training",
        split="wikipedia",
        local_path=(
            r"C:\DATA\AIDATA\raw\external"
            r"\pretraining\fsnaix_vietnamese_corpus_large"
        ),
        license="apache-2.0",
        access="gated",
    ),

    "pretraining_tuan_nt": HuggingFaceDatasetSource(
        dataset_id=(
            "Tuan-NT/"
            "vietnamese-corpus-pretrain"
        ),
        url=(
            "https://huggingface.co/datasets/"
            "Tuan-NT/vietnamese-corpus-pretrain"
        ),
        dataset_type="pre_training",
        split="train",
        local_path=(
            r"C:\DATA\AIDATA\raw\external"
            r"\pretraining\tuan_nt_vietnamese_corpus_pretrain"
        ),
    ),

    # ---------------------------------------------------------
    # INSTRUCTION
    # ---------------------------------------------------------

    "instruction_sft_10k": HuggingFaceDatasetSource(
        dataset_id=(
            "522H0134-NguyenNhatHuy/"
            "vietnamese-sft-10k"
        ),
        url=(
            "https://huggingface.co/datasets/"
            "522H0134-NguyenNhatHuy/"
            "vietnamese-sft-10k"
        ),
        dataset_type="instruction",
        split="train",
        local_path=(
            r"C:\DATA\AIDATA\raw\external"
            r"\instruction\vietnamese_sft_10k"
        ),
    ),

    "instruction_merged": HuggingFaceDatasetSource(
        dataset_id=(
            "BlossomsAI/"
            "merged_vietnamese_instruction_dataset"
        ),
        url=(
            "https://huggingface.co/datasets/"
            "BlossomsAI/"
            "merged_vietnamese_instruction_dataset"
        ),
        dataset_type="instruction",
        split="train",
        local_path=(
            r"C:\DATA\AIDATA\raw\external"
            r"\instruction\merged_vietnamese_instruction_dataset"
        ),
    ),

    # ---------------------------------------------------------
    # CONVERSATION
    # ---------------------------------------------------------

    "conversation_alpaca": HuggingFaceDatasetSource(
        dataset_id=(
            "5CD-AI/"
            "Vietnamese-Multi-turn-Chat-Alpaca"
        ),
        url=(
            "https://huggingface.co/datasets/"
            "5CD-AI/"
            "Vietnamese-Multi-turn-Chat-Alpaca"
        ),
        dataset_type="conversation",
        split="train",
        local_path=(
            r"C:\DATA\AIDATA\raw\external"
            r"\conversation"
            r"\vietnamese_multi_turn_chat_alpaca"
        ),
        license="apache-2.0",
    ),

    # ---------------------------------------------------------
    # EMOTION
    # ---------------------------------------------------------

    "emotion_vsmec": HuggingFaceDatasetSource(
        dataset_id="visolex/UIT-VSMEC",
        url=(
            "https://huggingface.co/datasets/"
            "visolex/UIT-VSMEC"
        ),
        dataset_type="emotion",
        split="train",
        local_path=(
            r"C:\DATA\AIDATA\raw\external"
            r"\emotion\uit_vsmec"
        ),
    ),

    # ---------------------------------------------------------
    # PREFERENCE
    # ---------------------------------------------------------

    "preference_vi_srs": HuggingFaceDatasetSource(
        dataset_id="NLPLab-SoICT/Vi-SRS",
        url=(
            "https://huggingface.co/datasets/"
            "NLPLab-SoICT/Vi-SRS"
        ),
        dataset_type="preference",
        split="train",
        local_path=(
            r"C:\DATA\AIDATA\raw\external"
            r"\preference\vi_srs"
        ),
        license="apache-2.0",
    ),

    # ---------------------------------------------------------
    # MULTIMODAL
    # ---------------------------------------------------------

    "multimodal_vista": HuggingFaceDatasetSource(
        dataset_id="Vi-VLM/Vista",
        url=(
            "https://huggingface.co/datasets/"
            "Vi-VLM/Vista"
        ),
        dataset_type="multimodal",
        subset="vi_llava_conversation",
        split="train",
        local_path=(
            r"C:\DATA\AIDATA\raw\external"
            r"\multimodal\vista"
        ),
        license="mit",
    ),

    # ---------------------------------------------------------
    # EVALUATION
    # ---------------------------------------------------------

    "evaluation_vmmu": HuggingFaceDatasetSource(
        dataset_id="anvo25/vmmu",
        url=(
            "https://huggingface.co/datasets/"
            "anvo25/vmmu"
        ),
        dataset_type="multimodal",
        split="full_vqa",
        local_path=(
            r"C:\DATA\AIDATA\raw\external"
            r"\multimodal\vmmu"
        ),
        license="mit",
    ),
}