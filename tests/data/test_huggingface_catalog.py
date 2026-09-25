from data.sources.huggingface_catalog import HF_DATASETS


def test_huggingface_catalog_contains_required_datasets() -> None:
    required = {
        "pretraining_fsnaix",
        "pretraining_tuan_nt",
        "instruction_sft_10k",
        "instruction_merged",
        "conversation_alpaca",
        "emotion_vsmec",
        "preference_vi_srs",
        "multimodal_vista",
        "evaluation_vmmu",
    }

    assert required.issubset(HF_DATASETS.keys())


def test_huggingface_catalog_entries_are_valid() -> None:
    for source in HF_DATASETS.values():
        assert source.dataset_id
        assert source.url.startswith(
            "https://huggingface.co/datasets/"
        )
        assert source.dataset_type
        assert source.split
        assert source.local_path
        assert source.streaming is True


def test_huggingface_catalog_local_paths_use_aidata() -> None:
    for source in HF_DATASETS.values():
        assert source.local_path.startswith(
            r"C:\DATA\AIDATA"
        )


def test_huggingface_catalog_dataset_types_are_supported() -> None:
    supported_types = {
        "pre_training",
        "instruction",
        "conversation",
        "personality",
        "emotion",
        "multimodal",
        "preference",
    }

    for source in HF_DATASETS.values():
        assert source.dataset_type in supported_types