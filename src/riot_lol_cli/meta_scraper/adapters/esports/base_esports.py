"""Base adapter for public esports research sources."""

from __future__ import annotations

import logging
import time
import urllib.robotparser
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx

from riot_lol_cli.meta_scraper.adapters.base import BaseAdapter

logger = logging.getLogger(__name__)

CONTACT_EMAIL = "darioefalzone95@gmail.com"
ESPORTS_USER_AGENT = f"riot_lol_cli-esports-research/0.1 (+mailto:{CONTACT_EMAIL})"


class BaseEsportsAdapter(BaseAdapter):
    """Domain adapter base that keeps BaseAdapter retry/rate patterns.

    The support-tier methods are implemented only to satisfy BaseAdapter's
    abstract interface; esports adapters expose fetch_tournaments/matches/game
    methods instead.
    """

    platform_name = "esports"
    source_id = "esports"
    min_delay = 2.0
    max_delay = 4.0

    def _build_headers(self) -> dict[str, str]:
        headers = super()._build_headers()
        headers["User-Agent"] = ESPORTS_USER_AGENT
        headers["From"] = CONTACT_EMAIL
        return headers

    def _safe_get(self, url: str, **kwargs: Any) -> httpx.Response:
        client = self._get_client()
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                if attempt > 1:
                    self._humanized_delay()
                response = client.get(url, **kwargs)
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    wait = _retry_after_seconds(retry_after) or int(30 * attempt)
                    logger.warning("[%s] 429, waiting %ss", self.platform_name, wait)
                    time.sleep(wait)
                    continue
                if response.status_code in {401, 403}:
                    raise PermissionError(f"[{self.platform_name}] access denied for {url}")
                response.raise_for_status()
                return response
            except httpx.RequestError:
                if attempt == max_retries:
                    raise
                time.sleep(5 * attempt)
            except httpx.HTTPStatusError:
                if attempt == max_retries:
                    raise
                time.sleep(5 * attempt)
        raise RuntimeError(f"[{self.platform_name}] exhausted retries for {url}")

    def robots_allowed(self, url: str) -> bool:
        parsed = urlparse(url)
        robots_url = urljoin(f"{parsed.scheme}://{parsed.netloc}", "/robots.txt")
        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(robots_url)
        try:
            parser.read()
        except Exception as exc:  # noqa: BLE001
            logger.warning("[%s] robots.txt unavailable: %s", self.platform_name, exc)
            return True
        return parser.can_fetch(ESPORTS_USER_AGENT, url)

    def fetch_tournaments(self, league: str, season: str) -> dict[str, Any]:
        raise NotImplementedError(f"[{self.platform_name}] fetch_tournaments not implemented")

    def fetch_matches(self, tournament_id: str) -> dict[str, Any]:
        raise NotImplementedError(f"[{self.platform_name}] fetch_matches not implemented")

    def fetch_game_detail(self, game_id: str) -> dict[str, Any]:
        raise NotImplementedError(f"[{self.platform_name}] fetch_game_detail not implemented")

    def fetch_draft(self, game_id: str) -> dict[str, Any]:
        raise NotImplementedError(f"[{self.platform_name}] fetch_draft not implemented")

    def fetch_support_tier_list(self, patch: str = "latest", elo: str = "emerald_plus") -> dict[str, Any]:
        raise NotImplementedError(f"[{self.platform_name}] support tier list not part of esports adapter")

    def fetch_champion_detail(self, champion_id: str) -> dict[str, Any]:
        raise NotImplementedError(f"[{self.platform_name}] champion detail not part of esports adapter")


def _retry_after_seconds(value: str | None) -> int | None:
    if not value:
        return None
    try:
        return max(0, int(value))
    except ValueError:
        return None
