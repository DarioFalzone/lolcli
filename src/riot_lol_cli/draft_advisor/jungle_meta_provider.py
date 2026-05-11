"""Jungle Meta provider for Draft Advisor.

The Draft Advisor uses Jungle Meta as the primary jungle source, but it must
keep working when the :8003 service is offline. This provider tries HTTP first
and falls back to the same local JSON loader used by Jungle Meta.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from riot_lol_cli.jungle_meta.loader import load_jungle_tier_list
from riot_lol_cli.settings import get_jungle_meta_port

JungleMetaFetcher = Callable[[str, float], dict[str, Any]]
JungleMetaLocalLoader = Callable[[], dict[str, Any]]


@dataclass(frozen=True)
class JungleMetaSnapshot:
    """Normalized source wrapper for Jungle Meta data."""

    data: dict[str, Any]
    status: str
    error: str | None = None
    source_url: str | None = None

    @property
    def patch(self) -> str | None:
        return self.data.get("patch")

    @property
    def date_updated(self) -> str | None:
        return self.data.get("date_updated")

    @property
    def source(self) -> str | None:
        return self.data.get("source")

    @property
    def champions(self) -> list[dict[str, Any]]:
        raw = self.data.get("jungle_champions", [])
        return raw if isinstance(raw, list) else []

    @property
    def champion_count(self) -> int:
        return len(self.champions)

    @property
    def categories(self) -> dict[str, Any]:
        raw = self.data.get("categories", {})
        return raw if isinstance(raw, dict) else {}

    @property
    def is_available(self) -> bool:
        return self.status in {"http", "local_fallback"} and bool(self.champions)


class JungleMetaProvider:
    """Load Jungle Meta through HTTP first, with local JSON fallback."""

    def __init__(
        self,
        *,
        timeout: float = 0.45,
        fetcher: JungleMetaFetcher | None = None,
        local_loader: JungleMetaLocalLoader | None = None,
    ) -> None:
        self._timeout = timeout
        self._fetcher = fetcher or self._fetch_http_json
        self._local_loader = local_loader or load_jungle_tier_list

    def load(self) -> JungleMetaSnapshot:
        """Return the best available Jungle Meta snapshot."""
        url = f"http://localhost:{get_jungle_meta_port()}/api/v1/jungle/tier-list"
        http_error: str | None = None

        try:
            data = self._fetcher(url, self._timeout)
            if self._has_champions(data):
                return JungleMetaSnapshot(data=data, status="http", source_url=url)
            http_error = "HTTP response did not include jungle_champions"
        except Exception as exc:  # noqa: BLE001 - provider must degrade gracefully
            http_error = str(exc)

        try:
            data = self._local_loader()
            if self._has_champions(data):
                return JungleMetaSnapshot(
                    data=data,
                    status="local_fallback",
                    error=http_error,
                    source_url=url,
                )
            local_error = "Local fallback did not include jungle_champions"
        except Exception as exc:  # noqa: BLE001 - surfaced as unavailable context
            local_error = str(exc)

        return JungleMetaSnapshot(
            data={},
            status="unavailable",
            error=f"http: {http_error}; local: {local_error}",
            source_url=url,
        )

    @staticmethod
    def _has_champions(data: dict[str, Any]) -> bool:
        return isinstance(data.get("jungle_champions"), list) and bool(data["jungle_champions"])

    @staticmethod
    def _fetch_http_json(url: str, timeout: float) -> dict[str, Any]:
        request = urllib.request.Request(url, headers={"Accept": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = response.read().decode("utf-8")
        except urllib.error.URLError as exc:
            raise RuntimeError(str(exc.reason)) from exc
        return json.loads(payload)
