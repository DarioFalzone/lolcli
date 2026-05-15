"""
Pipeline pro_accounts — V2: resolución desde seed + edición vía endpoint.

Lee `data/meta_analyzer/jungle_research/pro_players_seed.json` y para cada pro:

- Si la entrada del seed trae `riot_id` (formato `"GameName#TAG"`) y `server`,
  intenta resolver el PUUID vía `RiotBridge` (requiere `RIOT_API_KEY`).
- Si no hay `riot_id` o no hay key, marca la cuenta con `gap_flag` apropiado
  (`needs_account_resolution` o `no_riot_key`).
- **Cero scraping** de TrackingThePros/DPM/etc. Solo consume seed.

V2 agrega `set_pro_account()` para upsertar Riot ID + server de un pro
puntual sin tener que editar el JSON a mano. Lo usa el endpoint
`POST /api/v1/jungle-research/pros/{name}/account` y el form de la sub-vista.

Persiste el resultado en `pro_accounts.json` (mutable, sin rotación).
El seed se modifica con escritura atómica preservando el resto del archivo.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

from riot_lol_cli.jungle_research import json_storage
from riot_lol_cli.jungle_research.riot_bridge import RiotBridge
from riot_lol_cli.jungle_research.schemas import ProAccount, utcnow_iso

logger = logging.getLogger(__name__)


@dataclass
class ProAccountsResult:
    accounts: list[ProAccount] = field(default_factory=list)
    gaps: list[dict[str, Any]] = field(default_factory=list)
    resolved_count: int = 0
    extracted_at: str = ""

    def to_payload(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "extracted_at": self.extracted_at,
            "resolved_count": self.resolved_count,
            "total_count": len(self.accounts),
            "accounts": [a.model_dump(mode="json") for a in self.accounts],
            "gaps": self.gaps,
        }


def _parse_riot_id(raw: Any) -> tuple[str, str] | None:
    """Acepta `"GameName#TAG"` o `{"game_name":..., "tagline":...}`."""
    if isinstance(raw, str) and "#" in raw:
        head, _, tail = raw.partition("#")
        return (head.strip(), tail.strip()) if head and tail else None
    if isinstance(raw, dict):
        gn = raw.get("game_name") or raw.get("gameName")
        tg = raw.get("tagline") or raw.get("tag_line")
        if gn and tg:
            return (str(gn), str(tg))
    return None


def run(*, bridge: RiotBridge | None = None, persist: bool = True) -> ProAccountsResult:
    """
    Ejecuta resolución para todo el seed.

    Args:
        bridge: instancia inyectable de RiotBridge (para tests).
        persist: si True, escribe `pro_accounts.json`.
    """
    bridge = bridge or RiotBridge()
    seed = json_storage.read_pro_players_seed()
    extracted_at = utcnow_iso()
    accounts: list[ProAccount] = []
    gaps: list[dict[str, Any]] = []
    resolved = 0

    for player in seed:
        player_name = player.get("player_name") or player.get("name") or "unknown"
        riot_id_raw = player.get("riot_id")
        server = player.get("server")
        parsed = _parse_riot_id(riot_id_raw)

        if not parsed or not server:
            accounts.append(
                ProAccount(
                    pro_player_id=player_name,
                    source="manual_seed",
                    is_active=True,
                    gap_flag="needs_account_resolution",
                )
            )
            gaps.append(
                {
                    "player": player_name,
                    "reason": "seed sin riot_id+server público",
                    "attempted_at": extracted_at,
                }
            )
            continue

        game_name, tagline = parsed
        if not bridge.has_key():
            accounts.append(
                ProAccount(
                    pro_player_id=player_name,
                    source="manual_seed",
                    riot_id_game_name=game_name,
                    riot_id_tagline=tagline,
                    server=server,
                    is_active=True,
                    gap_flag="no_riot_key",
                )
            )
            gaps.append(
                {
                    "player": player_name,
                    "reason": "RIOT_API_KEY ausente",
                    "attempted_at": extracted_at,
                }
            )
            continue

        result = bridge.resolve_riot_id(game_name, tagline, server)
        accounts.append(
            ProAccount(
                pro_player_id=player_name,
                source="manual_seed",
                riot_id_game_name=game_name,
                riot_id_tagline=tagline,
                server=server,
                puuid=result.puuid,
                is_active=True,
                last_seen_at=extracted_at if result.puuid else None,
                gap_flag=result.gap_flag,
                confidence_score=1.0 if result.puuid else 0.0,
            )
        )
        if result.puuid:
            resolved += 1
        else:
            gaps.append(
                {
                    "player": player_name,
                    "reason": result.error or result.gap_flag or "resolución falló",
                    "attempted_at": extracted_at,
                }
            )

    out = ProAccountsResult(
        accounts=accounts, gaps=gaps, resolved_count=resolved, extracted_at=extracted_at
    )
    if persist:
        json_storage.save_pro_accounts(out.to_payload())
    return out


def set_pro_account(
    player_name: str,
    *,
    riot_id: str | None,
    server: str | None,
    bridge: RiotBridge | None = None,
) -> dict[str, Any]:
    """
    Upsert de Riot ID + server para un pro puntual del seed.

    Si `riot_id` es None, limpia los campos (vuelve a `needs_account_resolution`).
    Si `riot_id` está, actualiza el seed y dispara resolución del único pro.
    El resto del seed se preserva intacto.

    Devuelve:
        {
            "player": ...,
            "updated": True/False,        # se modificó el seed
            "resolved": True/False,       # PUUID obtenido
            "puuid": ... | None,
            "gap_flag": ... | None,
            "error": ... | None,
        }
    """
    parsed = _parse_riot_id(riot_id) if riot_id else None
    if riot_id and not parsed:
        return {
            "player": player_name,
            "updated": False,
            "resolved": False,
            "puuid": None,
            "gap_flag": None,
            "error": "riot_id inválido — formato esperado 'GameName#TAG'",
        }
    if parsed and not server:
        return {
            "player": player_name,
            "updated": False,
            "resolved": False,
            "puuid": None,
            "gap_flag": None,
            "error": "server requerido cuando se setea riot_id",
        }

    raw = json_storage.read_json(json_storage.PRO_PLAYERS_SEED_FILE)
    if not raw or not isinstance(raw, dict):
        return {
            "player": player_name,
            "updated": False,
            "resolved": False,
            "puuid": None,
            "gap_flag": None,
            "error": "pro_players_seed.json no existe o tiene estructura inválida",
        }
    players = raw.get("players", [])
    target = next((p for p in players if p.get("player_name") == player_name), None)
    if not target:
        return {
            "player": player_name,
            "updated": False,
            "resolved": False,
            "puuid": None,
            "gap_flag": None,
            "error": f"jugador '{player_name}' no está en el seed",
        }

    if parsed:
        target["riot_id"] = riot_id
        target["server"] = server
    else:
        target["riot_id"] = None
        target["server"] = None
    target["updated_at"] = utcnow_iso()
    raw["players"] = players

    # Escritura atómica preservando el resto del JSON.
    tmp = json_storage.PRO_PLAYERS_SEED_FILE.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)
        f.write("\n")
    tmp.replace(json_storage.PRO_PLAYERS_SEED_FILE)

    # Si se limpió, no hay nada que resolver.
    if not parsed:
        # Re-correr el pipeline completo para refrescar pro_accounts.json.
        run(bridge=bridge, persist=True)
        return {
            "player": player_name,
            "updated": True,
            "resolved": False,
            "puuid": None,
            "gap_flag": "needs_account_resolution",
            "error": None,
        }

    # Resolver solo este pro.
    bridge = bridge or RiotBridge()
    game_name, tagline = parsed
    if not bridge.has_key():
        run(bridge=bridge, persist=True)  # actualiza pro_accounts con el nuevo dato
        return {
            "player": player_name,
            "updated": True,
            "resolved": False,
            "puuid": None,
            "gap_flag": "no_riot_key",
            "error": None,
        }
    result = bridge.resolve_riot_id(game_name, tagline, server)
    # Re-correr el pipeline completo para que pro_accounts.json refleje el nuevo estado.
    run(bridge=bridge, persist=True)
    return {
        "player": player_name,
        "updated": True,
        "resolved": bool(result.puuid),
        "puuid": result.puuid,
        "gap_flag": result.gap_flag,
        "error": result.error,
    }
