import pytest
import requests

from riot_lol_cli.api import RiotAPIError, RiotClient


class DummyResponse:
    def __init__(self, status_code, payload=None, text="", headers=None):
        self.status_code = status_code
        self._payload = payload
        self.text = text
        self.headers = headers or {}

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


def test_request_retries_on_rate_limit(monkeypatch):
    client = RiotClient("token", "la2", "americas")
    responses = [
        DummyResponse(429, headers={"Retry-After": "0"}),
        DummyResponse(200, payload={"ok": True}),
    ]
    sleeps = []

    monkeypatch.setattr(client.session, "request", lambda *args, **kwargs: responses.pop(0))
    monkeypatch.setattr("riot_lol_cli.api.time.sleep", lambda seconds: sleeps.append(seconds))

    assert client._request_json("GET", "https://example.test") == {"ok": True}
    assert sleeps == [0.0]


def test_request_raises_for_auth_errors(monkeypatch):
    client = RiotClient("token", "la2", "americas")
    monkeypatch.setattr(
        client.session,
        "request",
        lambda *args, **kwargs: DummyResponse(403, text="forbidden"),
    )

    with pytest.raises(RiotAPIError, match="No autorizado"):
        client._request_json("GET", "https://example.test")


def test_request_raises_for_not_found(monkeypatch):
    client = RiotClient("token", "la2", "americas")
    monkeypatch.setattr(
        client.session,
        "request",
        lambda *args, **kwargs: DummyResponse(404, text="missing"),
    )

    with pytest.raises(RiotAPIError, match="404"):
        client._request_json("GET", "https://example.test")


def test_request_wraps_network_errors(monkeypatch):
    client = RiotClient("token", "la2", "americas")

    def raise_connection_error(*args, **kwargs):
        raise requests.ConnectionError("boom")

    monkeypatch.setattr(client.session, "request", raise_connection_error)

    with pytest.raises(RiotAPIError, match="Error de red"):
        client._request_json("GET", "https://example.test")
