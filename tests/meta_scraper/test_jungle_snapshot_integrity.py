"""Regresiones para el snapshot normalizado de jungla."""

import json
from pathlib import Path

from riot_lol_cli.meta_scraper.normalizer import MAX_GAMES_ANALYZED


def test_latest_jungle_snapshot_has_no_known_cross_role_artifacts():
    repo_root = Path(__file__).resolve().parents[2]
    snapshot_path = repo_root / "data" / "meta_scraper" / "normalized" / "latest_jungle_tier.json"
    if not snapshot_path.exists():
        return

    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    champion_ids = {champ["id"] for champ in snapshot.get("champions", [])}

    assert champion_ids.isdisjoint({"Smolder", "Ashe", "Velkoz", "Seraphine", "Xerath", "Vladimir"})


def test_latest_jungle_snapshot_games_are_bounded():
    repo_root = Path(__file__).resolve().parents[2]
    snapshot_path = repo_root / "data" / "meta_scraper" / "normalized" / "latest_jungle_tier.json"
    if not snapshot_path.exists():
        return

    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    for champ in snapshot.get("champions", []):
        assert champ["stats"].get("games_analyzed", 0) <= MAX_GAMES_ANALYZED
        for source_stats in champ.get("source_breakdown", {}).values():
            assert source_stats.get("games_analyzed", 0) <= MAX_GAMES_ANALYZED
