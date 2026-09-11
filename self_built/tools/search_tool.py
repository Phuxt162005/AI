"""Search Tool and provider abstractions for ProjectAI."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from core.interfaces import ToolInterface

@dataclass(frozen=True)
class SearchResult:
    """One search result."""

    title: str
    url: str
    snippet: str = ""

class SearchProvider(ABC):
    """Interface for search backends."""

    @abstractmethod
    def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[SearchResult]:
        """Search for a query."""
        raise NotImplementedError

class HttpSearchProvider(SearchProvider):
    """Search provider using DuckDuckGo's public instant-answer endpoint."""

    def __init__(
        self,
        endpoint: str = "https://api.duckduckgo.com/",
        timeout: float = 10.0,
    ) -> None:
        self._endpoint = endpoint
        self._timeout = timeout

    def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[SearchResult]:
        """Perform an HTTP search."""

        if not isinstance(query, str):
            raise TypeError("Search query must be a string.")

        query = query.strip()
        if not query:
            raise ValueError("Search query must not be empty.")
        if max_results <= 0:
            raise ValueError("max_results must be greater than zero.")

        url = (
            f"{self._endpoint}"
            f"?q={quote_plus(query)}"
            "&format=json"
            "&no_html=1"
            "&skip_disambig=1"
        )

        request = Request(
            url,
            headers={
                "User-Agent": "ProjectAI/0.1",
                "Accept": "application/json",
            },
        )

        try:
            with urlopen(request, timeout=self._timeout,) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise RuntimeError("Search provider request failed.") from exc

        return self._parse_response(payload, max_results)

    def _parse_response(
        self,
        payload: dict[str, Any],
        max_results: int,
    ) -> list[SearchResult]:
        """Convert provider response into common SearchResult objects."""

        results: list[SearchResult] = []
        abstract_text = payload.get("AbstractText")
        abstract_url = payload.get("AbstractURL")
        heading = payload.get("Heading")

        if (
            isinstance(abstract_text, str)
            and abstract_text.strip()
            and isinstance(abstract_url, str)
            and abstract_url.strip()
        ):
            results.append(
                SearchResult(
                    title=str(heading or "Result"),
                    url=abstract_url,
                    snippet=abstract_text,
                )
            )

        self._collect_related_topics(
            payload.get("RelatedTopics"),
            results,
            max_results,
        )

        return results[:max_results]

    def _collect_related_topics(
        self,
        topics: Any,
        results: list[SearchResult],
        max_results: int,
    ) -> None:
        """Collect flattened related topics."""

        if not isinstance(topics, list):
            return

        for topic in topics:
            if len(results) >= max_results:
                return

            if not isinstance(topic, dict):
                continue

            text = topic.get("Text")
            url = topic.get("FirstURL")

            if (
                isinstance(text, str)
                and text.strip()
                and isinstance(url, str)
                and url.strip()
            ):
                results.append(
                    SearchResult(
                        title=text.strip(),
                        url=url.strip(),
                        snippet=text.strip(),
                    )
                )
                continue

            nested = topic.get("Topics")
            if nested is not None:
                self._collect_related_topics(
                    nested,
                    results,
                    max_results,
                )

class SearchTool(ToolInterface):
    """Tool that delegates search requests to a SearchProvider."""

    def __init__(self, provider: SearchProvider) -> None:
        if not isinstance(provider, SearchProvider):
            raise TypeError("provider must implement SearchProvider.")

        self._provider = provider

    @property
    def name(self) -> str:
        return "search"

    @property
    def description(self) -> str:
        return (
            "Search for information using a configurable "
            "search provider."
        )

    @property
    def provider(self) -> SearchProvider:
        """Return the configured search provider."""

        return self._provider

    def execute(self, inputs: dict[str, Any]) -> list[SearchResult]:
        """Execute a search request."""

        if not isinstance(inputs, dict):
            raise TypeError("Search inputs must be a dictionary.")

        query = inputs.get("query")

        if not isinstance(query, str):
            raise TypeError("Search input 'query' must be a string.")

        query = query.strip()
        if not query:
            raise ValueError("Search input 'query' must not be empty.")

        max_results = inputs.get("max_results", 5)
        if (isinstance(max_results, bool) or not isinstance(max_results, int)):
            raise TypeError("Search input 'max_results' must be an integer.")

        if max_results <= 0:
            raise ValueError(
                "Search input 'max_results' must be greater than zero."
            )

        return self._provider.search(
            query=query,
            max_results=max_results,
        )