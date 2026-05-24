"""Conservative Gol.gg HTML adapter."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote

from bs4 import BeautifulSoup

from riot_lol_cli.meta_scraper.adapters.esports.base_esports import BaseEsportsAdapter


class GolGGAdapter(BaseEsportsAdapter):
    platform_name = "gol_gg"
    source_id = "gol_gg"
    base_url = "https://gol.gg"
    min_delay = 4.0
    max_delay = 8.0

    def _public_get(self, path: str) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        if not self.robots_allowed(url):
            return {"source": self.source_id, "status": "gap", "gap": "robots_disallow", "source_url": url}
        response = self._safe_get(url)
        return {
            "source": self.source_id,
            "status": "ok",
            "source_url": url,
            "html": response.text,
            "fetched_date": datetime.now(timezone.utc).date().isoformat(),
        }

    def fetch_tournament(self, tournament_slug: str) -> dict[str, Any]:
        safe_slug = quote(tournament_slug.strip("/"))
        payload = self._public_get(f"/tournament/tournament-stats/{safe_slug}/")
        if payload.get("status") != "ok":
            return payload
        return {**payload, **parse_tournament_html(payload["html"])}

    def fetch_tournaments(self, league: str, season: str) -> dict[str, Any]:
        return self.fetch_tournament(f"{league}-{season}")

    def fetch_matches(self, tournament_id: str) -> dict[str, Any]:
        return self.fetch_tournament(tournament_id)

    def fetch_game_detail(self, game_id: str) -> dict[str, Any]:
        safe_game = quote(game_id)
        return self._public_get(f"/game/stats/{safe_game}/page-summary/")

    def fetch_draft(self, game_id: str) -> dict[str, Any]:
        detail = self.fetch_game_detail(game_id)
        if detail.get("status") != "ok":
            return detail
        return {"source": self.source_id, "game_id": game_id, "draft_actions": parse_draft_html(detail.get("html", ""))}


def parse_tournament_html(html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find("h1")
    rows = []
    for table_row in soup.select("table tr"):
        cells = [cell.get_text(" ", strip=True) for cell in table_row.find_all(["td", "th"])]
        if cells:
            rows.append(cells)
    return {"tournament": title.get_text(" ", strip=True) if title else "Gol.gg Tournament", "rows": rows}


def parse_draft_html(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    actions: list[dict[str, Any]] = []
    for idx, node in enumerate(soup.select("[data-draft-action], .draft .champion, .picks-bans img"), start=1):
        champion = node.get("alt") or node.get("title") or node.get_text(" ", strip=True)
        if champion:
            actions.append(
                {
                    "action_order": idx,
                    "champion_id": champion.replace(" ", ""),
                    "action_type": "PICK",
                    "team_side": "UNKNOWN",
                    "phase": "UNKNOWN",
                }
            )
    return actions
