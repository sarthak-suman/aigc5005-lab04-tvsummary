"""Shared handmade input and a guard against real network calls."""

import pytest

from tvsummary import Show


@pytest.fixture(autouse=True)
def block_network(monkeypatch):
    def blocked(*args, **kwargs):
        pytest.fail("Tests must replace requests.get; network access is forbidden")

    monkeypatch.setattr("tvsummary.sources.requests.get", blocked)


@pytest.fixture
def shows():
    return [
        Show(
            {
                "name": "Alpha",
                "genres": ["Drama", "Drama"],
                "language": "English",
                "rating": {"average": 8},
            }
        ),
        Show(
            {
                "name": "Beta",
                "genres": ["Comedy", "Drama"],
                "language": "English",
                "rating": {"average": 6},
            }
        ),
        Show({"name": "Gamma"}),
    ]
