"""Coverage report for Esports Research."""

from __future__ import annotations

from riot_lol_cli.esports_research import json_storage
from riot_lol_cli.esports_research.schemas import CoverageReport, utcnow_iso
from riot_lol_cli.esports_research.source_registry import SourceRegistry


def generate() -> CoverageReport:
    try:
        registry = SourceRegistry.load()
        active_sources = len(registry.active())
        gaps: list[str] = []
    except Exception as exc:  # noqa: BLE001
        active_sources = 0
        gaps = [f"sources registry unavailable: {exc}"]

    games = json_storage.list_json_rows(json_storage.SILVER_GAMES_DIR)
    matches = json_storage.list_json_rows(json_storage.SILVER_MATCHES_DIR)
    tournaments = json_storage.read_silver_collection("tournaments")
    teams = json_storage.read_silver_collection("teams")
    players = json_storage.read_silver_collection("players")
    patches = json_storage.read_silver_collection("patches")
    return CoverageReport(
        generated_at=utcnow_iso(),
        tournaments=len(tournaments),
        matches=len(matches),
        games=len(games),
        teams=len(teams),
        players=len(players),
        patches=len(patches),
        active_sources=active_sources,
        gaps=gaps,
        storage_root=str(json_storage.ROOT),
    )
