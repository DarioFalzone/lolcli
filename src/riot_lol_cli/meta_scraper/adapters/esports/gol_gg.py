"""Conservative Gol.gg HTML adapter."""

from __future__ import annotations

import re
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
    actions = _parse_gol_game_draft(soup)
    if actions:
        return actions
    return _parse_legacy_draft_nodes(soup)


_CHAMPION_ICON_RE = re.compile(r"/champions_icon/([^/]+)\.png", re.IGNORECASE)


def _parse_gol_game_draft(soup: BeautifulSoup) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for team_side, header_selector in (("BLUE", ".blue-line-header"), ("RED", ".red-line-header")):
        header = soup.select_one(header_selector)
        if header is None:
            continue
        team_block = _find_team_summary_block(header)
        if team_block is None:
            continue
        for row in team_block.find_all("div", class_="row"):
            columns = row.find_all("div", recursive=False)
            if len(columns) < 2:
                continue
            label = columns[0].get_text(" ", strip=True).upper()
            if label.startswith("BANS"):
                action_type = "BAN"
            elif label.startswith("PICKS"):
                action_type = "PICK"
            else:
                continue
            for side_index, img in enumerate(columns[1].select("img.champion_icon_medium"), start=1):
                champion_id = _champion_id_from_img(img)
                if not champion_id:
                    continue
                actions.append(
                    {
                        "action_order": len(actions) + 1,
                        "champion_id": champion_id,
                        "action_type": action_type,
                        "team_side": team_side,
                        "phase": _draft_phase(action_type, side_index),
                    }
                )
    return actions


def _parse_legacy_draft_nodes(soup: BeautifulSoup) -> list[dict[str, Any]]:
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


def _find_team_summary_block(header):
    block = header
    while block is not None:
        classes = block.get("class", [])
        if "col-sm-6" in classes:
            return block
        block = block.parent
    return None


def _champion_id_from_img(img) -> str | None:
    src = img.get("src", "")
    match = _CHAMPION_ICON_RE.search(src)
    if match:
        return match.group(1)
    champion = img.get("alt") or img.get("title")
    if not champion:
        return None
    return "".join(character for character in champion if character.isalnum())


def _draft_phase(action_type: str, side_index: int) -> str:
    if action_type == "BAN":
        return "BAN_PHASE_1" if side_index <= 3 else "BAN_PHASE_2"
    return "PICK_PHASE_1" if side_index <= 3 else "PICK_PHASE_2"
