from __future__ import annotations

from collections.abc import Iterable

import httpx
import pytest

from riot_lol_cli.meta_scraper.adapters.esports.base_esports import (
    CONTACT_EMAIL,
    ESPORTS_USER_AGENT,
    BaseEsportsAdapter,
    _retry_after_seconds,
)


class _FakeClient:
    is_closed = False

    def __init__(self, outcomes: Iterable[httpx.Response | Exception]) -> None:
        self._outcomes = list(outcomes)
        self.calls: list[str] = []

    def get(self, url: str, **kwargs) -> httpx.Response:
        self.calls.append(url)
        outcome = self._outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def _response(status_code: int, *, url: str = "https://example.com/data", headers: dict[str, str] | None = None):
    return httpx.Response(status_code, headers=headers, request=httpx.Request("GET", url))


def test_build_headers_uses_identifiable_esports_contact() -> None:
    headers = BaseEsportsAdapter()._build_headers()
    assert headers["User-Agent"] == ESPORTS_USER_AGENT
    assert headers["From"] == CONTACT_EMAIL
    assert "mailto:" in headers["User-Agent"]


def test_retry_after_seconds_accepts_only_delta_seconds() -> None:
    assert _retry_after_seconds("12") == 12
    assert _retry_after_seconds("-5") == 0
    assert _retry_after_seconds("Wed, 21 Oct 2015 07:28:00 GMT") is None
    assert _retry_after_seconds(None) is None


def test_safe_get_retries_429_with_retry_after(monkeypatch) -> None:
    adapter = BaseEsportsAdapter()
    client = _FakeClient([_response(429, headers={"Retry-After": "7"}), _response(200)])
    sleeps: list[int | float] = []
    delays: list[str] = []

    monkeypatch.setattr(adapter, "_get_client", lambda: client)
    monkeypatch.setattr(adapter, "_humanized_delay", lambda: delays.append("delay"))
    monkeypatch.setattr("riot_lol_cli.meta_scraper.adapters.esports.base_esports.time.sleep", sleeps.append)

    response = adapter._safe_get("https://example.com/data")

    assert response.status_code == 200
    assert len(client.calls) == 2
    assert sleeps == [7]
    assert delays == ["delay"]


def test_safe_get_429_without_retry_after_uses_attempt_backoff(monkeypatch) -> None:
    adapter = BaseEsportsAdapter()
    client = _FakeClient([_response(429), _response(200)])
    sleeps: list[int | float] = []

    monkeypatch.setattr(adapter, "_get_client", lambda: client)
    monkeypatch.setattr(adapter, "_humanized_delay", lambda: None)
    monkeypatch.setattr("riot_lol_cli.meta_scraper.adapters.esports.base_esports.time.sleep", sleeps.append)

    assert adapter._safe_get("https://example.com/data").status_code == 200
    assert sleeps == [30]


def test_safe_get_access_denied_raises_without_retry(monkeypatch) -> None:
    adapter = BaseEsportsAdapter()
    client = _FakeClient([_response(403)])

    monkeypatch.setattr(adapter, "_get_client", lambda: client)

    with pytest.raises(PermissionError):
        adapter._safe_get("https://example.com/data")

    assert len(client.calls) == 1


def test_safe_get_retries_request_errors_with_linear_backoff(monkeypatch) -> None:
    adapter = BaseEsportsAdapter()
    request = httpx.Request("GET", "https://example.com/data")
    client = _FakeClient(
        [
            httpx.ConnectError("temporary outage", request=request),
            httpx.ReadTimeout("slow upstream", request=request),
            _response(200),
        ]
    )
    sleeps: list[int | float] = []
    delays: list[str] = []

    monkeypatch.setattr(adapter, "_get_client", lambda: client)
    monkeypatch.setattr(adapter, "_humanized_delay", lambda: delays.append("delay"))
    monkeypatch.setattr("riot_lol_cli.meta_scraper.adapters.esports.base_esports.time.sleep", sleeps.append)

    assert adapter._safe_get("https://example.com/data").status_code == 200
    assert sleeps == [5, 10]
    assert delays == ["delay", "delay"]


def test_safe_get_retries_http_status_errors_then_succeeds(monkeypatch) -> None:
    adapter = BaseEsportsAdapter()
    client = _FakeClient([_response(500), _response(200)])
    sleeps: list[int | float] = []

    monkeypatch.setattr(adapter, "_get_client", lambda: client)
    monkeypatch.setattr(adapter, "_humanized_delay", lambda: None)
    monkeypatch.setattr("riot_lol_cli.meta_scraper.adapters.esports.base_esports.time.sleep", sleeps.append)

    assert adapter._safe_get("https://example.com/data").status_code == 200
    assert sleeps == [5]


def test_safe_get_exhausts_429_retries(monkeypatch) -> None:
    adapter = BaseEsportsAdapter()
    client = _FakeClient([_response(429), _response(429), _response(429)])
    sleeps: list[int | float] = []

    monkeypatch.setattr(adapter, "_get_client", lambda: client)
    monkeypatch.setattr(adapter, "_humanized_delay", lambda: None)
    monkeypatch.setattr("riot_lol_cli.meta_scraper.adapters.esports.base_esports.time.sleep", sleeps.append)

    with pytest.raises(RuntimeError):
        adapter._safe_get("https://example.com/data")

    assert sleeps == [30, 60, 90]
