import pytest
import requests

from tvsummary import DownloadError, TVMazeSource
from tvsummary.errors import ResponseShapeError


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_successful_fetch(monkeypatch):
    def fake_get(url, timeout):
        assert url == "https://example.invalid/shows"
        assert timeout == 2
        return FakeResponse([{"name": "Example"}] * 50)

    monkeypatch.setattr("tvsummary.sources.requests.get", fake_get)
    shows = TVMazeSource("https://example.invalid/shows", timeout=2).fetch()
    assert len(shows) == 50
    assert shows[0].name == "Example"


def test_connection_failure_is_chained(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.ConnectionError("no network")

    monkeypatch.setattr("tvsummary.sources.requests.get", fake_get)
    with pytest.raises(DownloadError, match="no network") as caught:
        TVMazeSource().fetch()
    assert isinstance(caught.value.__cause__, requests.ConnectionError)


@pytest.mark.parametrize(
    "payload, message",
    [
        ({}, "list of records"),
        ([], "fewer than 50"),
        ([{}] * 49 + [None], "malformed show record"),
    ],
)
def test_invalid_response(monkeypatch, payload, message):
    monkeypatch.setattr(
        "tvsummary.sources.requests.get", lambda *args, **kwargs: FakeResponse(payload)
    )
    with pytest.raises(ResponseShapeError, match=message):
        TVMazeSource().fetch()


def test_invalid_json_is_chained(monkeypatch):
    class InvalidJSONResponse(FakeResponse):
        def json(self):
            raise ValueError("invalid JSON")

    monkeypatch.setattr(
        "tvsummary.sources.requests.get",
        lambda *args, **kwargs: InvalidJSONResponse(None),
    )
    with pytest.raises(ResponseShapeError, match="valid JSON") as caught:
        TVMazeSource().fetch()
    assert isinstance(caught.value.__cause__, ValueError)


def test_http_failure_is_chained(monkeypatch):
    class HTTPFailureResponse(FakeResponse):
        def raise_for_status(self):
            raise requests.HTTPError("503 unavailable")

    monkeypatch.setattr(
        "tvsummary.sources.requests.get",
        lambda *args, **kwargs: HTTPFailureResponse(None),
    )
    with pytest.raises(DownloadError, match="503 unavailable") as caught:
        TVMazeSource().fetch()
    assert isinstance(caught.value.__cause__, requests.HTTPError)
