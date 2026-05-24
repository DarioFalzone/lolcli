"""
Router HTTP para Jungle Research dentro de Meta Analyzer (`:8000`).

Todos los endpoints son **read-only** salvo `POST /refresh`. La regla central:
si una capa de datos no está disponible, devolver 200 con `gaps` visible —
nunca 500 ni inventar datos.
"""

from __future__ import annotations

import logging
from collections import Counter
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from riot_lol_cli.jungle_research import json_storage, orchestrator
from riot_lol_cli.jungle_research.orchestrator import (
    STEP_ASIA,
    STEP_EXTRA,
    STEP_PRO_STAGE,
    STEP_RIOT_PROS,
    STEP_SOLOQ,
    VALID_STEPS,
    RefreshPlan,
)
from riot_lol_cli.jungle_research.pipelines import (
    match_history as match_history_pipeline,
)
from riot_lol_cli.jungle_research.pipelines import (
    pro_accounts as pro_accounts_pipeline,
)
from riot_lol_cli.jungle_research.reports import daily_report
from riot_lol_cli.jungle_research.riot_bridge import RiotBridge
from riot_lol_cli.jungle_research.schemas import (
    ProAccount,
    utcnow_iso,
)
from riot_lol_cli.jungle_research.source_registry import SourceRegistry

# Mapeo `mode` legacy -> set de steps del orquestador. Compat retroactiva.
_LEGACY_MODE_TO_STEPS: dict[str, tuple[set[str], bool]] = {
    # (steps, regenerate_tierlist)
    "soloq": ({STEP_SOLOQ}, True),
    "soloq_extra": ({STEP_EXTRA}, False),  # solo telemetría, no toca tier list
    "asia": ({STEP_ASIA}, False),  # solo cache asia + telemetría
    "riot_pros": ({STEP_RIOT_PROS}, False),
    "pro_stage": ({STEP_PRO_STAGE}, False),  # PR-C: bridge esports, sin regenerar
    "all": ({STEP_SOLOQ, STEP_EXTRA, STEP_ASIA, STEP_RIOT_PROS, STEP_PRO_STAGE}, True),
}

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/jungle-research", tags=["jungle-research"])


def _registry_summary() -> dict[str, Any]:
    try:
        registry = SourceRegistry.load()
    except (ValueError, FileNotFoundError) as exc:
        return {"error": str(exc), "summary": {}, "sources": []}
    return {
        "summary": registry.summary(),
        "sources": [s.model_dump(mode="json") for s in registry.all()],
    }


def _read_latest_snapshots() -> dict[str, Any] | None:
    return json_storage.read_json(json_storage.CHAMPION_SNAPSHOTS_LATEST)


def _read_latest_tierlist() -> dict[str, Any] | None:
    return json_storage.read_json(json_storage.FINAL_TIERLIST_LATEST)


def _consolidate_and_save(
    *,
    region: str,
    elo: str,
    queue: str,
    pro_presence: dict[str, float] | None = None,
    asia_presence: dict[str, float] | None = None,
    include_extra: bool = True,
    include_asia: bool = False,
) -> dict[str, Any]:
    """
    Wrapper de compat retroactiva. La lógica real vive en
    `jungle_research.orchestrator.consolidate(RefreshPlan(...))`.

    Mantenido para no romper tests externos. Nuevos callers deben usar
    el orquestador directamente.
    """
    steps = {STEP_SOLOQ}
    if include_extra:
        steps.add(STEP_EXTRA)
    if include_asia:
        steps.add(STEP_ASIA)
    plan = RefreshPlan(
        steps=steps,
        region=region,
        elo=elo,
        queue=queue,
        asia_presence_override=asia_presence,
        pro_presence_override=pro_presence,
    )
    result = orchestrator.consolidate(plan)
    # Adaptar al shape histórico (success + entries + sources_used + gaps...).
    if result.tierlist_summary and result.tierlist_summary.get("success"):
        out = dict(result.tierlist_summary)
        out["extra"] = result.extra_summary
        out["asia"] = result.asia_summary
        return out
    # Sin tier list (0 snapshots): adaptar al shape previo.
    return {
        "success": False,
        "gaps": [{"reason": g} for g in result.gaps]
        + [{"reason": "0 snapshots para consolidar"}],
        "extracted_at": result.started_at,
        "extra": result.extra_summary,
        "asia": result.asia_summary,
    }


# ---------------------------------------------------------------------------
# Read endpoints
# ---------------------------------------------------------------------------


@router.get("/overview")
async def overview() -> dict[str, Any]:
    """Resumen agregado: top tiers, conteo de fuentes, freshness."""
    tierlist = _read_latest_tierlist()
    snapshots = _read_latest_snapshots()
    bridge = RiotBridge()
    registry = _registry_summary()

    if not tierlist:
        return {
            "success": True,
            "freshness": None,
            "patch": None,
            "tier_distribution": {},
            "sources": registry["summary"],
            "riot_api_key_present": bridge.has_key(),
            "gaps": ["final_jungle_tierlist/latest.json no existe — corra POST /refresh"],
            "timestamp": utcnow_iso(),
        }

    entries = tierlist.get("entries", [])
    distribution = Counter(e.get("final_tier") for e in entries)
    return {
        "success": True,
        "freshness": tierlist.get("generated_at"),
        "patch": tierlist.get("patch"),
        "region": tierlist.get("region"),
        "elo": tierlist.get("elo"),
        "tier_distribution": dict(distribution),
        "entry_count": len(entries),
        "source_count": tierlist.get("source_count_total"),
        "snapshot_count": (snapshots or {}).get("snapshot_count", 0),
        "sources": registry["summary"],
        "riot_api_key_present": bridge.has_key(),
        "gaps": tierlist.get("gaps", []),
        "timestamp": utcnow_iso(),
    }


@router.get("/current")
async def current(limit: int = Query(50, ge=1, le=500)) -> dict[str, Any]:
    """Tier list final consolidada."""
    tierlist = _read_latest_tierlist()
    if not tierlist:
        return {
            "success": True,
            "data": [],
            "gaps": ["final_jungle_tierlist/latest.json no existe — corra POST /refresh"],
            "timestamp": utcnow_iso(),
        }
    entries = tierlist.get("entries", [])[:limit]
    return {
        "success": True,
        "patch": tierlist.get("patch"),
        "region": tierlist.get("region"),
        "elo": tierlist.get("elo"),
        "generated_at": tierlist.get("generated_at"),
        "data": entries,
        "total_records": len(entries),
        "gaps": tierlist.get("gaps", []),
        "timestamp": utcnow_iso(),
    }


@router.get("/sources")
async def sources() -> dict[str, Any]:
    """Registry completo con estado por fuente + telemetría de último run."""
    payload = _registry_summary()
    runs = json_storage.read_adapter_runs().get("runs", {})
    enriched = []
    for src in payload.get("sources", []):
        adapter_run = runs.get(src.get("id"))
        if adapter_run:
            src = {
                **src,
                "last_attempted_at": adapter_run.get("last_attempted_at"),
                "last_run_status": adapter_run.get("status"),
                "last_run_reason": adapter_run.get("reason"),
                "last_run_champion_count": adapter_run.get("champion_count"),
            }
        enriched.append(src)
    return {
        "success": True,
        "summary": payload.get("summary", {}),
        "sources": enriched,
        "timestamp": utcnow_iso(),
    }


@router.get("/champions/{champion_id}/history")
async def champion_history(champion_id: str) -> dict[str, Any]:
    """Evolución del campeón en backups históricos del tier list."""
    history_dir = json_storage.FINAL_TIERLIST_HISTORY
    if not history_dir.exists():
        return {
            "success": True,
            "champion_id": champion_id,
            "data": [],
            "gaps": ["sin history aún"],
            "timestamp": utcnow_iso(),
        }
    history: list[dict[str, Any]] = []
    for path in sorted(history_dir.glob("*.json")):
        payload = json_storage.read_json(path)
        if not payload:
            continue
        for entry in payload.get("entries", []):
            if entry.get("champion_name") == champion_id:
                history.append(
                    {
                        "generated_at": payload.get("generated_at"),
                        "patch": payload.get("patch"),
                        "final_tier": entry.get("final_tier"),
                        "final_score": entry.get("final_score"),
                        "confidence": entry.get("confidence"),
                    }
                )
    return {
        "success": True,
        "champion_id": champion_id,
        "data": history,
        "total_records": len(history),
        "timestamp": utcnow_iso(),
    }


@router.get("/pros")
async def list_pros() -> dict[str, Any]:
    """Lista pros del seed + cuentas resueltas + estado por jugador."""
    seed = json_storage.read_pro_players_seed()
    accounts_payload = json_storage.read_json(json_storage.PRO_ACCOUNTS_FILE) or {}
    accounts_by_player: dict[str, dict[str, Any]] = {
        a.get("pro_player_id"): a for a in accounts_payload.get("accounts", [])
    }
    bridge = RiotBridge()
    rows: list[dict[str, Any]] = []
    for player in seed:
        name = player.get("player_name")
        account = accounts_by_player.get(name) or {}
        rows.append(
            {
                "player_name": name,
                "real_name": player.get("real_name"),
                "country": player.get("country"),
                "current_team": player.get("current_team"),
                "priority_tier": player.get("priority_tier"),
                "urls": player.get("urls", {}),
                "riot_id": player.get("riot_id"),
                "server": player.get("server"),
                "puuid": account.get("puuid"),
                "gap_flag": account.get("gap_flag"),
                "last_seen_at": account.get("last_seen_at"),
                "is_active": account.get("is_active", True),
            }
        )
    return {
        "success": True,
        "data": rows,
        "total": len(rows),
        "resolved": sum(1 for r in rows if r["puuid"]),
        "riot_api_key_present": bridge.has_key(),
        "timestamp": utcnow_iso(),
    }


class SetProAccountBody(BaseModel):
    riot_id: str | None = Field(
        None, description="Formato 'GameName#TAG'. None para limpiar la cuenta."
    )
    server: str | None = Field(
        None, description="KR | EUW | NA | BR | LAN | LAS | JP | TR | RU | etc. Requerido si riot_id presente."
    )


@router.post("/pros/{player_name}/account")
async def set_pro_account_endpoint(
    player_name: str, body: SetProAccountBody
) -> dict[str, Any]:
    """Upsert de Riot ID + server para un pro puntual del seed.

    Si `riot_id` es None, limpia la cuenta (vuelve a needs_account_resolution).
    Si está, actualiza el seed y dispara resolución vía Riot bridge.
    Cero scraping. Solo Riot API oficial cuando hay key.
    """
    try:
        result = pro_accounts_pipeline.set_pro_account(
            player_name,
            riot_id=body.riot_id,
            server=body.server,
            bridge=RiotBridge(),
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("set_pro_account falló")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    if result.get("error"):
        return {"success": False, **result, "timestamp": utcnow_iso()}
    return {"success": True, **result, "timestamp": utcnow_iso()}


@router.get("/pros/recent-picks")
async def pros_recent_picks(
    hours: int = Query(48, ge=1, le=240),
) -> dict[str, Any]:
    """Picks recientes de pros (V1: requiere RIOT_API_KEY + cuentas resueltas)."""
    bridge = RiotBridge()
    if not bridge.has_key():
        return {
            "success": True,
            "data": [],
            "gaps": ["no_riot_key"],
            "hours": hours,
            "timestamp": utcnow_iso(),
        }
    accounts_payload = json_storage.read_json(json_storage.PRO_ACCOUNTS_FILE)
    if not accounts_payload:
        return {
            "success": True,
            "data": [],
            "gaps": ["pro_accounts.json no existe — corra POST /refresh?mode=riot_pros"],
            "hours": hours,
            "timestamp": utcnow_iso(),
        }
    resolved = [
        ProAccount.model_validate(a)
        for a in accounts_payload.get("accounts", [])
        if a.get("puuid")
    ]
    presence = match_history_pipeline.recent_pro_picks(
        resolved, hours=hours, bridge=bridge
    )
    data = sorted(
        ({"champion_name": k, "presence": v} for k, v in presence.items()),
        key=lambda x: x["presence"],
        reverse=True,
    )
    return {
        "success": True,
        "data": data,
        "hours": hours,
        "resolved_accounts": len(resolved),
        "timestamp": utcnow_iso(),
    }


@router.get("/pros/{player_name}/matches")
async def pro_matches(player_name: str) -> dict[str, Any]:
    """Match history persistido para un pro específico."""
    accounts_payload = json_storage.read_json(json_storage.PRO_ACCOUNTS_FILE)
    if not accounts_payload:
        return {
            "success": True,
            "player": player_name,
            "data": [],
            "gaps": ["pro_accounts.json no existe — corra POST /refresh?mode=riot_pros"],
            "timestamp": utcnow_iso(),
        }
    target_puuid = next(
        (
            a.get("puuid")
            for a in accounts_payload.get("accounts", [])
            if a.get("pro_player_id") == player_name and a.get("puuid")
        ),
        None,
    )
    if not target_puuid:
        return {
            "success": True,
            "player": player_name,
            "data": [],
            "gaps": [f"sin PUUID resuelto para {player_name}"],
            "timestamp": utcnow_iso(),
        }
    puuid_dir = json_storage.MATCH_HISTORY_DIR / target_puuid
    if not puuid_dir.exists():
        return {
            "success": True,
            "player": player_name,
            "data": [],
            "gaps": ["sin match history persistido — corra POST /refresh"],
            "timestamp": utcnow_iso(),
        }
    latest = sorted(puuid_dir.glob("*.json"))
    if not latest:
        return {
            "success": True,
            "player": player_name,
            "data": [],
            "gaps": ["puuid dir vacío"],
            "timestamp": utcnow_iso(),
        }
    payload = json_storage.read_json(latest[-1])
    return {
        "success": True,
        "player": player_name,
        "puuid": target_puuid,
        "extracted_at": payload.get("extracted_at"),
        "data": payload.get("entries", []),
        "total_records": payload.get("entry_count", 0),
        "timestamp": utcnow_iso(),
    }


@router.get("/champions/{champion_id}/otp")
async def champion_otp(champion_id: str) -> dict[str, Any]:
    """OTPs por campeón. V1: registry-only, devuelve gap visible."""
    return {
        "success": True,
        "champion_id": champion_id,
        "data": [],
        "gaps": ["pipeline_otp_rankings: planned (V1 sin scrape)"],
        "timestamp": utcnow_iso(),
    }


@router.get("/emerging")
async def emerging(limit: int = Query(10, ge=1, le=50)) -> dict[str, Any]:
    """Campeones con mayor subida de score vs último backup."""
    report_payload = json_storage.read_json(
        json_storage.DAILY_REPORTS_DIR
        / f"{utcnow_iso()[:10]}.json"
    )
    if report_payload and report_payload.get("risers"):
        return {
            "success": True,
            "data": report_payload["risers"][:limit],
            "source": "daily_report",
            "timestamp": utcnow_iso(),
        }
    return {
        "success": True,
        "data": [],
        "gaps": ["daily_report no disponible aún"],
        "timestamp": utcnow_iso(),
    }


@router.get("/consensus")
async def consensus(limit: int = Query(20, ge=1, le=100)) -> dict[str, Any]:
    """Mayor acuerdo entre fuentes (confidence alta + source_count alto)."""
    tierlist = _read_latest_tierlist()
    if not tierlist:
        return {
            "success": True,
            "data": [],
            "gaps": ["final_jungle_tierlist/latest.json no existe"],
            "timestamp": utcnow_iso(),
        }
    entries = tierlist.get("entries", [])
    sorted_entries = sorted(
        entries,
        key=lambda e: (e.get("source_count", 0), e.get("confidence", 0.0)),
        reverse=True,
    )[:limit]
    return {
        "success": True,
        "data": sorted_entries,
        "timestamp": utcnow_iso(),
    }


@router.get("/daily-report")
async def daily_report_endpoint(date: str | None = None) -> dict[str, Any]:
    """Reporte diario: fecha por defecto = hoy UTC. Genera al vuelo si no existe."""
    target_date = date or utcnow_iso()[:10]
    existing = json_storage.read_json(
        json_storage.DAILY_REPORTS_DIR / f"{target_date}.json"
    )
    if existing:
        return {"success": True, "data": existing, "timestamp": utcnow_iso()}
    generated = daily_report.generate(report_date=target_date, persist=True)
    if not generated:
        return {
            "success": True,
            "data": None,
            "gaps": ["sin tier list — corra POST /refresh primero"],
            "timestamp": utcnow_iso(),
        }
    return {"success": True, "data": generated.model_dump(mode="json"), "timestamp": utcnow_iso()}


# ---------------------------------------------------------------------------
# Refresh
# ---------------------------------------------------------------------------


_LEGACY_MODE_LITERAL = Literal[
    "soloq", "soloq_extra", "asia", "riot_pros", "pro_stage", "all"
]


@router.post("/refresh")
async def refresh(
    mode: _LEGACY_MODE_LITERAL | None = Query(
        None,
        description=(
            "Modo legacy (compat). Mapea a un set de steps fijo. "
            "Preferir `modes` para composición libre."
        ),
    ),
    modes: list[str] | None = Query(
        None,
        description=(
            "Lista de steps a ejecutar. Valores válidos: "
            "soloq, extra, asia, riot_pros. Ejemplo: ?modes=soloq&modes=asia"
        ),
    ),
    regenerate_tierlist: bool | None = Query(
        None,
        description=(
            "Si se pasa, fuerza/saltea regeneración del final_jungle_tierlist. "
            "Default: True si steps incluyen soloq o extra; False si solo asia "
            "o riot_pros (cache + telemetría sin tocar tier list)."
        ),
    ),
    region: str = Query("GLOBAL"),
    elo: str = Query("EMERALD_PLUS"),
    queue: str = Query("ranked_solo_5x5"),
) -> dict[str, Any]:
    """
    Dispara pipelines según `modes` (preferido) o `mode` (legacy).

    **Nuevo (V2.8)**: `modes=list[str]` permite composición libre.
    Ejemplos:
      - `?modes=soloq&modes=asia` → regenera tier list con asia fresh
      - `?modes=asia&regenerate_tierlist=true` → asia fresh + regenera con cache
      - `?modes=asia` → solo refresca cache asia, NO toca tier list (default)

    **Legacy (`mode=`)**: mapeado a steps fijos.
      - `soloq`: solo Meta Scraper local + Jungle Meta curated → regenera
      - `soloq_extra`: solo telemetría adapters V3 → NO regenera
      - `asia`: solo cache asia + telemetría V4 → NO regenera
      - `riot_pros`: resuelve cuentas pro si hay RIOT_API_KEY → NO regenera
      - `all`: todo + regenera tier list con todo aplicado

    Si `mode` y `modes` se pasan ambos, gana `modes`.
    """
    if mode is None and modes is None:
        mode = "all"

    try:
        plan = _build_refresh_plan(
            mode=mode,
            modes=modes,
            regenerate_tierlist=regenerate_tierlist,
            region=region,
            elo=elo,
            queue=queue,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        result = orchestrator.consolidate(plan)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Refresh falló")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return result.to_payload()


def _build_refresh_plan(
    *,
    mode: str | None,
    modes: list[str] | None,
    regenerate_tierlist: bool | None,
    region: str,
    elo: str,
    queue: str,
) -> RefreshPlan:
    """Convierte parámetros HTTP (mode legacy o modes nuevo) a RefreshPlan."""
    if modes:
        steps = set(modes)
        invalid = steps - VALID_STEPS
        if invalid:
            raise ValueError(
                f"modes inválidos: {sorted(invalid)}. Válidos: {sorted(VALID_STEPS)}"
            )
        # Por defecto regenera si el set incluye fuentes que aportan snapshots
        # (soloq, extra). Solo asia o riot_pros no regenera salvo override.
        default_regen = bool(steps & {STEP_SOLOQ, STEP_EXTRA})
    elif mode and mode in _LEGACY_MODE_TO_STEPS:
        steps, default_regen = _LEGACY_MODE_TO_STEPS[mode]
        steps = set(steps)  # copia (frozenset → mutable)
    else:
        raise ValueError(f"mode desconocido: {mode!r}")

    regen = default_regen if regenerate_tierlist is None else regenerate_tierlist
    return RefreshPlan(
        steps=steps,
        region=region,
        elo=elo,
        queue=queue,
        regenerate_tierlist=regen,
    )
