"""Normalize Leaguepedia Cargo records to silver schemas."""

from __future__ import annotations

from typing import Any

from riot_lol_cli.esports_research.analytics.identities import make_stable_id
from riot_lol_cli.esports_research.schemas import DraftAction, Game, Match, ParticipantGame, Player, Team, Tournament


def _rows(payload: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = payload.get(key, [])
    return value if isinstance(value, list) else []


def normalize_payload(payload: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    tournaments: list[dict[str, Any]] = []
    matches: list[dict[str, Any]] = []
    games: list[dict[str, Any]] = []
    draft_actions: list[dict[str, Any]] = []
    participants: list[dict[str, Any]] = []
    teams: dict[str, dict[str, Any]] = {}
    players: dict[str, dict[str, Any]] = {}

    for row in _rows(payload, "tournaments"):
        tournament_id = row.get("tournament_id") or make_stable_id("tournament", row.get("name"))
        tournaments.append(
            Tournament(
                tournament_id=tournament_id,
                name=row.get("name", tournament_id),
                region=row.get("region", "UNKNOWN"),
                league=row.get("league", "UNKNOWN"),
                format=row.get("format", "UNKNOWN"),
                start_date=row.get("start_date", "1970-01-01"),
                end_date=row.get("end_date"),
                source_origin="leaguepedia",
            ).model_dump(mode="json")
        )

    for row in _rows(payload, "matches"):
        match_id = row.get("match_id") or make_stable_id("match", row.get("tournament_id"), row.get("team_blue"), row.get("team_red"))
        tournament_id = row.get("tournament_id") or make_stable_id("tournament", row.get("tournament"))
        blue_team = row.get("team_blue_id") or make_stable_id("team", row.get("team_blue"))
        red_team = row.get("team_red_id") or make_stable_id("team", row.get("team_red"))
        for team_id, name in ((blue_team, row.get("team_blue")), (red_team, row.get("team_red"))):
            teams.setdefault(
                team_id,
                Team(
                    team_id=team_id,
                    name=name or team_id,
                    short=row.get("team_short", name or team_id),
                    region=row.get("region", "UNKNOWN"),
                    league=row.get("league", "UNKNOWN"),
                    active=True,
                ).model_dump(mode="json"),
            )
        matches.append(
            Match(
                match_id=match_id,
                tournament_id=tournament_id,
                scheduled_at=row.get("scheduled_at", "1970-01-01T00:00:00Z"),
                best_of=int(row.get("best_of", 1)),
                team_blue_id=blue_team,
                team_red_id=red_team,
                winner_team_id=row.get("winner_team_id"),
                source_origin="leaguepedia",
            ).model_dump(mode="json")
        )

    for row in _rows(payload, "games"):
        game_id = row.get("game_id") or make_stable_id("game", row.get("match_id"), row.get("game_number", 1))
        games.append(
            Game(
                game_id=game_id,
                match_id=row.get("match_id", "unknown"),
                game_number=int(row.get("game_number", 1)),
                patch_id=row.get("patch_id", "unknown"),
                side_selection=row.get("side_selection", "UNKNOWN"),
                fearless_context=row.get("fearless_context", []),
                duration_seconds=row.get("duration_seconds"),
                winner_side=row.get("winner_side"),
                source_origin="leaguepedia",
                source_game_key=row.get("source_game_key", game_id),
            ).model_dump(mode="json")
        )

    for row in _rows(payload, "draft_actions"):
        draft_actions.append(DraftAction.model_validate(row).model_dump(mode="json"))

    for row in _rows(payload, "participants"):
        player_id = row.get("player_id") or make_stable_id("player", row.get("player"))
        players.setdefault(
            player_id,
            Player(
                player_id=player_id,
                handle=row.get("player") or player_id,
                real_name=row.get("real_name"),
                country=row.get("country"),
                current_team_id=row.get("team_id"),
                primary_role=row.get("role", "UNKNOWN"),
            ).model_dump(mode="json"),
        )
        normalized = {**row, "player_id": player_id}
        participants.append(ParticipantGame.model_validate(normalized).model_dump(mode="json"))

    return {
        "tournaments": tournaments,
        "matches": matches,
        "games": games,
        "draft_actions": draft_actions,
        "participants": participants,
        "teams": list(teams.values()),
        "players": list(players.values()),
    }
