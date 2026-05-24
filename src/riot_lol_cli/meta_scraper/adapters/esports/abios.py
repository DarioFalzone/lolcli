"""Stub for Abios commercial API."""

from __future__ import annotations

from typing import Any

from riot_lol_cli.meta_scraper.adapters.esports.base_esports import BaseEsportsAdapter


class AbiosAdapter(BaseEsportsAdapter):
    platform_name = "abios"
    source_id = "abios"

    def list_matches(self) -> dict[str, Any]:
        return self._stub("list_matches")

    def get_stats(self) -> dict[str, Any]:
        return self._stub("get_stats")

    def _stub(self, method: str) -> dict[str, Any]:
        return {
            "source": self.source_id,
            "method": method,
            "status": "not_implemented",
            "gaps": ["requires Abios commercial contract"],
            "rate_limit": "standard tier: 3 req/s, burst 5, 180 days history",
        }
