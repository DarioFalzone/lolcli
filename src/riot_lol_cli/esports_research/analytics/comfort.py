"""Player-champion comfort score helpers."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from riot_lol_cli.esports_research.schemas import ComfortScore


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def compute_comfort_scores(
    participant_games: list[dict[str, Any]],
    *,
    now: datetime | None = None,
) -> list[ComfortScore]:
    reference = now or datetime.now(timezone.utc)
    cutoff = reference - timedelta(days=90)
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in participant_games:
        player_id = row.get("player_id")
        champion_id = row.get("champion_id")
        if player_id and champion_id:
            grouped[(str(player_id), str(champion_id))].append(row)

    scores: list[ComfortScore] = []
    for (player_id, champion_id), rows in sorted(grouped.items()):
        total = len(rows)
        wins_total = sum(1 for row in rows if row.get("win") is True)
        recent_rows = [
            row
            for row in rows
            if (played_at := _parse_iso(row.get("played_at"))) is not None and played_at >= cutoff
        ]
        recent = len(recent_rows)
        wins_recent = sum(1 for row in recent_rows if row.get("win") is True)
        winrate_total = wins_total / total if total else 0.0
        winrate_recent = wins_recent / recent if recent else winrate_total
        recency_volume = min(1.0, recent / 10.0)
        last_played = max((row.get("played_at") for row in rows if row.get("played_at")), default=None)
        scores.append(
            ComfortScore(
                player_id=player_id,
                champion_id=champion_id,
                games_total=total,
                games_recent_90d=recent,
                winrate_total=winrate_total,
                winrate_recent_90d=winrate_recent,
                comfort_score=(0.4 * recency_volume) + (0.6 * winrate_recent),
                last_played_at=last_played,
            )
        )
    return scores
