"""
Pipeline match_history — V1: descarga últimas N partidas vía Riot API.

Solo intenta descargar para cuentas con `puuid` resuelto (output del pipeline
`pro_accounts`). Si `RIOT_API_KEY` está ausente, registra gap y no llama a la
API. Persiste por PUUID en `match_history/<puuid>/<timestamp>.json`.

V1 conservador: descarga matchIDs y la metadata mínima por partida (champion,
queue, win, role detectado). El raw payload completo de match-v5 queda en
`raw_payload_ref` opcional.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from riot_lol_cli.jungle_research import json_storage
from riot_lol_cli.jungle_research.riot_bridge import RiotBridge
from riot_lol_cli.jungle_research.schemas import MatchHistoryEntry, ProAccount, utcnow_iso

logger = logging.getLogger(__name__)

QUEUE_RANKED_SOLO_5X5 = 420
QUEUE_RANKED_FLEX_5X5 = 440


@dataclass
class MatchHistoryResult:
    entries_per_account: dict[str, list[MatchHistoryEntry]] = field(default_factory=dict)
    gaps: list[dict[str, Any]] = field(default_factory=list)
    extracted_at: str = ""

    def total_entries(self) -> int:
        return sum(len(v) for v in self.entries_per_account.values())


def _participant_for_puuid(match_payload: dict[str, Any], puuid: str) -> dict[str, Any] | None:
    """Encuentra el participant correcto en una respuesta match-v5."""
    info = match_payload.get("info") or {}
    for participant in info.get("participants", []):
        if participant.get("puuid") == puuid:
            return participant
    return None


def _entry_from_match(
    match_payload: dict[str, Any],
    *,
    puuid: str,
    player_id: str | None,
    server: str | None,
    raw_ref: str | None,
) -> MatchHistoryEntry | None:
    info = match_payload.get("info") or {}
    metadata = match_payload.get("metadata") or {}
    participant = _participant_for_puuid(match_payload, puuid)
    if not participant:
        return None
    epoch_ms = info.get("gameStartTimestamp") or info.get("gameCreation") or 0
    game_dt = datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc) if epoch_ms else datetime.now(timezone.utc)
    return MatchHistoryEntry(
        match_id=str(metadata.get("matchId") or info.get("gameId") or ""),
        puuid=puuid,
        player_id=player_id,
        source="riot_api",
        server=server,
        queue_id=info.get("queueId"),
        game_datetime=game_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        patch=str(info.get("gameVersion", "")).rsplit(".", 2)[0] if info.get("gameVersion") else None,
        champion_id=str(participant.get("championName") or ""),
        champion_name=str(participant.get("championName") or "Unknown"),
        detected_role=participant.get("teamPosition") or participant.get("individualPosition"),
        team_position=participant.get("teamPosition"),
        win=participant.get("win"),
        kills=participant.get("kills"),
        deaths=participant.get("deaths"),
        assists=participant.get("assists"),
        cs=(participant.get("totalMinionsKilled", 0) or 0)
        + (participant.get("neutralMinionsKilled", 0) or 0),
        gold=participant.get("goldEarned"),
        damage=participant.get("totalDamageDealtToChampions"),
        vision_score=participant.get("visionScore"),
        game_duration=info.get("gameDuration"),
        raw_payload_ref=raw_ref,
        created_at=utcnow_iso(),
    )


def run_for_account(
    account: ProAccount,
    *,
    bridge: RiotBridge | None = None,
    count: int = 20,
    persist: bool = True,
) -> tuple[list[MatchHistoryEntry], list[dict[str, Any]]]:
    """Descarga últimas `count` partidas para una cuenta resuelta."""
    bridge = bridge or RiotBridge()
    gaps: list[dict[str, Any]] = []
    extracted_at = utcnow_iso()

    if not account.puuid:
        gaps.append(
            {
                "player": account.pro_player_id,
                "reason": "cuenta sin PUUID resuelto",
                "attempted_at": extracted_at,
            }
        )
        return [], gaps
    if not bridge.has_key():
        gaps.append(
            {
                "player": account.pro_player_id,
                "reason": "RIOT_API_KEY ausente",
                "attempted_at": extracted_at,
            }
        )
        return [], gaps
    if not account.server:
        gaps.append(
            {
                "player": account.pro_player_id,
                "reason": "cuenta sin server",
                "attempted_at": extracted_at,
            }
        )
        return [], gaps

    match_ids = bridge.fetch_recent_match_ids(account.puuid, account.server, count=count)
    if not match_ids:
        gaps.append(
            {
                "player": account.pro_player_id,
                "reason": "Riot API devolvió 0 partidas",
                "attempted_at": extracted_at,
            }
        )
        return [], gaps

    entries: list[MatchHistoryEntry] = []
    for match_id in match_ids:
        detail = bridge.fetch_match_detail(match_id, account.server)
        if not detail:
            gaps.append(
                {
                    "player": account.pro_player_id,
                    "match_id": match_id,
                    "reason": "match-v5 detalle no disponible",
                    "attempted_at": extracted_at,
                }
            )
            continue
        entry = _entry_from_match(
            detail,
            puuid=account.puuid,
            player_id=account.pro_player_id,
            server=account.server,
            raw_ref=None,
        )
        if entry:
            entries.append(entry)

    if persist and entries:
        payload = {
            "schema_version": 1,
            "extracted_at": extracted_at,
            "puuid": account.puuid,
            "player_id": account.pro_player_id,
            "server": account.server,
            "entry_count": len(entries),
            "entries": [e.model_dump(mode="json") for e in entries],
        }
        json_storage.save_match_history(account.puuid, payload)

    return entries, gaps


def run(
    accounts: list[ProAccount],
    *,
    bridge: RiotBridge | None = None,
    count: int = 20,
    persist: bool = True,
) -> MatchHistoryResult:
    """Itera todas las cuentas resueltas y descarga su match history."""
    bridge = bridge or RiotBridge()
    extracted_at = utcnow_iso()
    out = MatchHistoryResult(extracted_at=extracted_at)

    for account in accounts:
        entries, gaps = run_for_account(account, bridge=bridge, count=count, persist=persist)
        if entries:
            out.entries_per_account[account.pro_player_id] = entries
        out.gaps.extend(gaps)

    return out


def recent_pro_picks(
    accounts: list[ProAccount],
    *,
    hours: int = 48,
    bridge: RiotBridge | None = None,
) -> dict[str, float]:
    """
    Devuelve `champion_name -> presence_score` (0-1) para uso por scoring engine.

    V1: corre `run` y agrega; en producción, leer de `match_history/<puuid>/`
    para no rehacer Riot calls en cada scoring.
    """
    bridge = bridge or RiotBridge()
    if not bridge.has_key():
        return {}
    cutoff = datetime.now(timezone.utc).timestamp() - (hours * 3600)
    presence: dict[str, int] = {}
    total = 0
    for account in accounts:
        entries, _ = run_for_account(account, bridge=bridge, count=10, persist=False)
        for entry in entries:
            try:
                game_ts = datetime.fromisoformat(entry.game_datetime.rstrip("Z")).replace(
                    tzinfo=timezone.utc
                ).timestamp()
            except ValueError:
                continue
            if game_ts < cutoff:
                continue
            presence[entry.champion_name] = presence.get(entry.champion_name, 0) + 1
            total += 1
    if not total:
        return {}
    return {champ: count / total for champ, count in presence.items()}
