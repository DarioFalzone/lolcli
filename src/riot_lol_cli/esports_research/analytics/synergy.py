"""Composition co-occurrence helpers."""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from typing import Any

from riot_lol_cli.esports_research.schemas import SynergyPair


def compute_synergy_pairs(
    participant_games: list[dict[str, Any]],
    *,
    patch_id: str,
    region: str,
) -> list[SynergyPair]:
    by_game_side: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in participant_games:
        game_id = row.get("game_id")
        side = str(row.get("side") or "").upper()
        if game_id and side:
            by_game_side[(str(game_id), side)].append(row)

    tallies: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: {"games": 0, "wins": 0})
    for rows in by_game_side.values():
        champions = sorted({str(row.get("champion_id")) for row in rows if row.get("champion_id")})
        if len(champions) < 2:
            continue
        won = any(row.get("win") is True for row in rows)
        for champ_a, champ_b in combinations(champions, 2):
            tallies[(champ_a, champ_b)]["games"] += 1
            tallies[(champ_a, champ_b)]["wins"] += 1 if won else 0

    return [
        SynergyPair(
            patch_id=patch_id,
            region=region,
            champion_a_id=champ_a,
            champion_b_id=champ_b,
            games=tally["games"],
            wins=tally["wins"],
            winrate_raw=tally["wins"] / tally["games"] if tally["games"] else 0.0,
        )
        for (champ_a, champ_b), tally in sorted(tallies.items())
    ]
