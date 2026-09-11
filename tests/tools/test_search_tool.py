"""Tests for SearchTool."""

import pytest

from self_built.tools.search_tool import (
    SearchProvider,
    SearchResult,
    SearchTool,
)


class FakeSearchProvider(SearchProvider):
    def __init__(self) -> None:
        self.last_query: str | None = None
        self.last_max_results: int | None = None

    def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[SearchResult]:
        self.last_query = query
        self.last_max_results = max_results

        return [
            SearchResult(
                title="MQTT",
                url="https://example.com/mqtt",
                snippet="MQTT information.",
            )
        ][:max_results]


class FailingSearchProvider(SearchProvider):
    def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[SearchResult]:
        raise RuntimeError("search provider failure")


def test_search_tool_calls_provider() -> None:
    provider = FakeSearchProvider()
    tool = SearchTool(provider)

    results = tool.execute(
        {
            "query": "MQTT",
            "max_results": 3,
        }
    )

    assert provider.last_query == "MQTT"
    assert provider.last_max_results == 3
    assert len(results) == 1
    assert results[0].title == "MQTT"
    assert results[0].url == "https://example.com/mqtt"


def test_search_tool_default_max_results() -> None:
    provider = FakeSearchProvider()
    tool = SearchTool(provider)

    tool.execute(
        {
            "query": "MQTT",
        }
    )

    assert provider.last_max_results == 5


def test_search_tool_empty_query_fails() -> None:
    provider = FakeSearchProvider()
    tool = SearchTool(provider)

    with pytest.raises(ValueError, match="must not be empty"):
        tool.execute(
            {
                "query": "   ",
            }
        )


def test_search_tool_query_must_be_string() -> None:
    provider = FakeSearchProvider()
    tool = SearchTool(provider)

    with pytest.raises(TypeError, match="must be a string"):
        tool.execute(
            {
                "query": 123,  # type: ignore[arg-type]
            }
        )


def test_search_tool_max_results_must_be_integer() -> None:
    provider = FakeSearchProvider()
    tool = SearchTool(provider)

    with pytest.raises(TypeError, match="must be an integer"):
        tool.execute(
            {
                "query": "MQTT",
                "max_results": "5",  # type: ignore[arg-type]
            }
        )


def test_search_tool_max_results_must_be_positive() -> None:
    provider = FakeSearchProvider()
    tool = SearchTool(provider)

    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        tool.execute(
            {
                "query": "MQTT",
                "max_results": 0,
            }
        )


def test_search_tool_exposes_provider() -> None:
    provider = FakeSearchProvider()
    tool = SearchTool(provider)

    assert tool.provider is provider


def test_search_provider_failure_is_propagated() -> None:
    provider = FailingSearchProvider()
    tool = SearchTool(provider)

    with pytest.raises(
        RuntimeError,
        match="search provider failure",
    ):
        tool.execute(
            {
                "query": "MQTT",
            }
        )


def test_search_result_is_structured() -> None:
    result = SearchResult(
        title="Example",
        url="https://example.com",
        snippet="Example result.",
    )

    assert result.title == "Example"
    assert result.url == "https://example.com"
    assert result.snippet == "Example result."