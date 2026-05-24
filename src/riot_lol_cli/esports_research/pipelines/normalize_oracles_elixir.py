"""Normalize Oracle's Elixir CSV rows."""

from __future__ import annotations

import csv
from io import StringIO
from typing import Any

from riot_lol_cli.esports_research.analytics.identities import make_stable_id


def parse_csv_text(csv_text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(StringIO(csv_text)))


def normalize_csv_text(csv_text: str) -> dict[str, list[dict[str, Any]]]:
    rows = parse_csv_text(csv_text)
    participants: list[dict[str, Any]] = []
    games: dict[str, dict[str, Any]] = {}
    teams: dict[str, dict[str, Any]] = {}
    players: dict[str, dict[str, Any]] = {}
    for row in rows:
        game_id = row.get("gameid") or make_stable_id("game", row.get("date"), row.get("teamname"), row.get("game"))
        player_id = make_stable_id("player", row.get("playername"))
        team_id = make_stable_id("team", row.get("teamname"))
        games.setdefault(
            game_id,
            {
                "game_id": game_id,
                "match_id": row.get("matchid") or make_stable_id("match", game_id),
                "game_number": int(row.get("game", "1") or 1),
                "patch_id": row.get("patch", "unknown"),
                "side_selection": "UNKNOWN",
                "fearless_context": [],
                "duration_seconds": int(float(row.get("gamelength", "0") or 0)) or None,
                "winner_side": None,
                "source_origin": "oracles_elixir",
                "source_game_key": game_id,
            },
        )
        teams.setdefault(
            team_id,
            {
                "team_id": team_id,
                "name": row.get("teamname") or team_id,
                "short": row.get("teamname") or team_id,
                "region": row.get("league", "UNKNOWN"),
                "league": row.get("league", "UNKNOWN"),
                "active": True,
            },
        )
        players.setdefault(
            player_id,
            {
                "player_id": player_id,
                "handle": row.get("playername") or player_id,
                "real_name": None,
                "country": None,
                "current_team_id": team_id,
                "primary_role": row.get("position", "UNKNOWN").upper(),
            },
        )
        participants.append(
            {
                "participant_game_id": make_stable_id("participant", game_id, player_id),
                "game_id": game_id,
                "team_id": team_id,
                "player_id": player_id,
                "side": row.get("side", "UNKNOWN").upper(),
                "role": row.get("position", "UNKNOWN").upper(),
                "champion_id": row.get("champion") or "Unknown",
                "summoner_spells": [],
                "keystone_rune": None,
                "kills": _int(row.get("kills")),
                "deaths": _int(row.get("deaths")),
                "assists": _int(row.get("assists")),
                "cs": _int(row.get("total cs")),
                "gold": _int(row.get("earnedgold")),
                "damage": _int(row.get("damagetochampions")),
                "win": row.get("result") == "1",
                "played_at": row.get("date"),
                "patch_id": row.get("patch"),
                "region": row.get("league"),
            }
        )
    return {
        "games": list(games.values()),
        "participants": participants,
        "teams": list(teams.values()),
        "players": list(players.values()),
    }


def _int(value: str | None) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(float(value))
    except ValueError:
        return None
