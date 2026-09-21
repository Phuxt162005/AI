"""Shared pytest fixtures for repository tests."""

import pytest


class FakeDataAccess:
    """Minimal DataAccess test double for repository tests."""

    def __init__(self):
        self.executed = []
        self.queries = []
        self.query_results = []
        self.query_one_result = None

    def execute(self, sql, parameters=None):
        self.executed.append((sql, parameters))
        return None

    def query(self, sql, parameters=None):
        self.queries.append((sql, parameters))
        return self.query_results

    def query_one(self, sql, parameters=None):
        self.queries.append((sql, parameters))
        return self.query_one_result


@pytest.fixture
def fake_data_access():
    """Provide a fake DataAccess implementation for repository tests."""
    return FakeDataAccess()