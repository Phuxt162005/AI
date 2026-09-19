from data.processing.tokenizer import (
    SimpleTokenizer,
)


def test_tokenizer():
    tokenizer = SimpleTokenizer()

    tokenizer.build_vocabulary(
        ["ProjectAI is an AI assistant"]
    )

    tokens = tokenizer.tokenize(
        "ProjectAI is an AI assistant"
    )

    assert tokens == [
        "ProjectAI",
        "is",
        "an",
        "AI",
        "assistant",
    ]


def test_tokenizer_encode_decode():
    tokenizer = SimpleTokenizer()

    tokenizer.build_vocabulary(
        ["ProjectAI is AI"]
    )

    token_ids = tokenizer.encode(
        "ProjectAI is AI"
    )

    assert len(token_ids) == 3

    decoded = tokenizer.decode(token_ids)

    assert decoded == "ProjectAI is AI"


def test_unknown_token():
    tokenizer = SimpleTokenizer()

    tokenizer.build_vocabulary(
        ["ProjectAI"]
    )

    encoded = tokenizer.encode(
        "Unknown"
    )

    assert encoded == [1]