"""Counterpick matrix helpers."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from riot_lol_cli.esports_research.schemas import CounterpickEntry


def bayesian_winrate(wins: int, games: int, alpha: float = 2.0, beta: float = 2.0) -> float:
    if games < 0 or wins < 0 or wins > games:
        raise ValueError("wins/games must be non-negative and wins <= games")
    return (wins + alpha) / (games + alpha + beta)


def sample_confidence(games: int) -> float:
    return min(1.0, max(0.0, games / 30.0))


def compute_counterpick_entries(
    participant_games: list[dict[str, Any]],
    *,
    patch_id: str,
    region: str,
) -> list[CounterpickEntry]:
    by_game_role: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in participant_games:
        game_id = row.get("game_id")
        role = str(row.get("role") or "").upper()
        if game_id and role:
            by_game_role[(game_id, role)].append(row)

    tallies: dict[tuple[str, str, str], dict[str, int]] = defaultdict(lambda: {"games": 0, "wins": 0})
    for (_game_id, role), rows in by_game_role.items():
        blue = next((row for row in rows if str(row.get("side", "")).upper() == "BLUE"), None)
        red = next((row for row in rows if str(row.get("side", "")).upper() == "RED"), None)
        if not blue or not red:
            continue
        blue_champ = blue.get("champion_id")
        red_champ = red.get("champion_id")
        if not blue_champ or not red_champ:
            continue
        blue_win = bool(blue.get("win"))
        for champ, against, won in (
            (str(blue_champ), str(red_champ), blue_win),
            (str(red_champ), str(blue_champ), not blue_win),
        ):
            key = (role, champ, against)
            tallies[key]["games"] += 1
            tallies[key]["wins"] += 1 if won else 0

    entries: list[CounterpickEntry] = []
    for (role, champion_id, against_champion_id), tally in sorted(tallies.items()):
        games = tally["games"]
        wins = tally["wins"]
        entries.append(
            CounterpickEntry(
                patch_id=patch_id,
                role=role,
                region=region,
                champion_id=champion_id,
                against_champion_id=against_champion_id,
                games=games,
                wins=wins,
                winrate_raw=wins / games if games else 0.0,
                winrate_shrunken=bayesian_winrate(wins, games),
                sample_confidence=sample_confidence(games),
            )
        )
    return entries
