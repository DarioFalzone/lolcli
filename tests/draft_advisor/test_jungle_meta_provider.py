from __future__ import annotations

import pytest

from riot_lol_cli.draft_advisor.jungle_meta_provider import JungleMetaProvider


def _sample_data() -> dict:
    return {
        "patch": "26.09",
        "date_updated": "2026-05-09T00:00:00Z",
        "source": "test",
        "jungle_champions": [{"id": "XinZhao", "tier": "S"}],
    }


def test_provider_uses_http_when_available() -> None:
    def fetcher(url: str, timeout: float) -> dict:
        assert "/api/v1/jungle/tier-list" in url
        assert timeout < 1
        return _sample_data()

    provider = JungleMetaProvider(fetcher=fetcher, local_loader=lambda: pytest.fail("local fallback not expected"))

    snapshot = provider.load()

    assert snapshot.status == "http"
    assert snapshot.patch == "26.09"
    assert snapshot.champion_count == 1


def test_provider_falls_back_to_local_when_http_fails() -> None:
    def fetcher(url: str, timeout: float) -> dict:
        raise RuntimeError("service offline")

    provider = JungleMetaProvider(fetcher=fetcher, local_loader=_sample_data)

    snapshot = provider.load()

    assert snapshot.status == "local_fallback"
    assert snapshot.error == "service offline"
    assert snapshot.champions[0]["id"] == "XinZhao"


def test_provider_reports_unavailable_when_http_and_local_fail() -> None:
    def fetcher(url: str, timeout: float) -> dict:
        raise RuntimeError("http down")

    def local_loader() -> dict:
        raise RuntimeError("missing local json")

    provider = JungleMetaProvider(fetcher=fetcher, local_loader=local_loader)

    snapshot = provider.load()

    assert snapshot.status == "unavailable"
    assert snapshot.is_available is False
    assert "http down" in (snapshot.error or "")
    assert "missing local json" in (snapshot.error or "")
