"""
Pipeline meta_soloq_extra - adapters SoloQ adicionales (V3).

Orquesta los 4 adapters nuevos del set V3 (Mobalytics, METAsrc,
LeagueOfGraphs, Tracker.gg). Cada adapter expone `fetch_jungle_tier_list`
con la interfaz unificada de `BaseAdapter`. Por defecto retornan
`status: not_implemented` hasta que el operador active el extract real.

Telemetria: cada run actualiza `data/meta_analyzer/jungle_research/
adapter_runs.json` con `last_attempted_at`, `status`, `reason`,
`champion_count` por adapter. La sub-vista Fuentes del cockpit lee este
archivo para mostrar la salud actual de cada adapter.

Cero scraping ciego: si un adapter retorna status != 'ok', el pipeline
registra el gap pero no inyecta datos al snapshot consolidado.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from riot_lol_cli.jungle_research import json_storage
from riot_lol_cli.jungle_research.schemas import ChampionMetaSnapshot, utcnow_iso

logger = logging.getLogger(__name__)


@dataclass
class AdapterRun:
    """Resultado de una invocacion a un adapter."""

    adapter_id: str
    status: str  # "ok" | "not_implemented" | "error" | "disabled"
    reason: str
    champion_count: int = 0
    last_attempted_at: str = ""
    source_url: str = ""


@dataclass
class MetaSoloQExtraResult:
    snapshots: list[ChampionMetaSnapshot] = field(default_factory=list)
    runs: list[AdapterRun] = field(default_factory=list)
    extracted_at: str = ""

    def to_payload(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "extracted_at": self.extracted_at,
            "snapshot_count": len(self.snapshots),
            "snapshots": [s.model_dump(mode="json") for s in self.snapshots],
            "runs": [r.__dict__ for r in self.runs],
        }


def _default_adapters() -> dict[str, Any]:
    """Carga los 4 adapters V3 con import lazy para tests."""
    from riot_lol_cli.meta_scraper.adapters.leagueofgraphs import LeagueOfGraphsAdapter
    from riot_lol_cli.meta_scraper.adapters.metasrc import MetaSrcAdapter
    from riot_lol_cli.meta_scraper.adapters.mobalytics import MobalyticsAdapter
    from riot_lol_cli.meta_scraper.adapters.tracker_gg import TrackerGgAdapter

    return {
        "metasrc_jungle": MetaSrcAdapter(),
        "mobalytics_jungle_tierlist": MobalyticsAdapter(),
        "leagueofgraphs_jungle": LeagueOfGraphsAdapter(),
        "tracker_gg_lol": TrackerGgAdapter(),
    }


def _snapshots_from_adapter_payload(
    *,
    source_id: str,
    payload: dict[str, Any],
    region: str,
    elo: str,
    queue: str,
) -> list[ChampionMetaSnapshot]:
    """Convierte el dict crudo del adapter en snapshots por campeon."""
    if payload.get("status") != "ok":
        return []
    out: list[ChampionMetaSnapshot] = []
    source_url = payload.get("source_url", "")
    patch = str(payload.get("patch") or "")
    scraped_at = str(payload.get("scraped_at") or utcnow_iso())
    for champ in payload.get("champions", []):
        champ_id = str(champ.get("id") or champ.get("champion_id") or "")
        champ_name = str(
            champ.get("display_name") or champ.get("name") or champ_id or "Unknown"
        )
        if not champ_id and not champ_name:
            continue
        out.append(
            ChampionMetaSnapshot(
                source_id=source_id,
                source_name=payload.get("platform", source_id).upper(),
                source_url=source_url,
                extracted_at=scraped_at,
                patch=patch,
                region=region,
                queue=queue,
                elo=elo,
                role="jungle",
                champion_id=champ_id,
                champion_name=champ_name,
                tier=None,
                win_rate=_safe_float(champ.get("win_rate") or champ.get("winrate")),
                pick_rate=_safe_float(champ.get("pick_rate") or champ.get("pickrate")),
                ban_rate=_safe_float(champ.get("ban_rate") or champ.get("banrate")),
                games=_safe_int(champ.get("games") or champ.get("games_analyzed")),
                methodology_notes=f"Adapter V3 ({source_id})",
            )
        )
    return out


def _safe_float(value: Any) -> float | None:
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value: Any) -> int | None:
    try:
        return None if value is None else int(value)
    except (TypeError, ValueError):
        return None


def run(
    *,
    adapters: dict[str, Any] | None = None,
    region: str = "GLOBAL",
    elo: str = "emerald_plus",
    queue: str = "ranked_solo_5x5",
    persist: bool = True,
) -> MetaSoloQExtraResult:
    """
    Invoca los 4 adapters V3 y agrega los snapshots de los que respondan ok.

    Args:
        adapters: dict {source_id: adapter_instance}. Si None, usa los 4 default.
        region/elo/queue: contexto canonico para los snapshots.
        persist: si True, escribe adapter_runs.json con la telemetria.
    """
    adapters = adapters if adapters is not None else _default_adapters()
    extracted_at = utcnow_iso()
    snapshots: list[ChampionMetaSnapshot] = []
    runs: list[AdapterRun] = []

    for source_id, adapter in adapters.items():
        attempted_at = utcnow_iso()
        try:
            payload = adapter.fetch_jungle_tier_list(elo=elo)
        except Exception as exc:  # noqa: BLE001
            logger.warning("[%s] adapter raised: %s", source_id, exc)
            runs.append(
                AdapterRun(
                    adapter_id=source_id,
                    status="error",
                    reason=str(exc)[:200],
                    last_attempted_at=attempted_at,
                )
            )
            continue

        status = str(payload.get("status") or "ok")
        reason = str(payload.get("reason") or "")
        source_url = str(payload.get("source_url") or "")
        champion_count = int(payload.get("champion_count") or len(payload.get("champions", [])))

        if status == "ok":
            new_snaps = _snapshots_from_adapter_payload(
                source_id=source_id,
                payload=payload,
                region=region,
                elo=elo,
                queue=queue,
            )
            snapshots.extend(new_snaps)

        runs.append(
            AdapterRun(
                adapter_id=source_id,
                status=status,
                reason=reason or ("ok" if status == "ok" else "sin razon"),
                champion_count=champion_count,
                last_attempted_at=attempted_at,
                source_url=source_url,
            )
        )

    if persist:
        _persist_runs(runs, extracted_at=extracted_at)

    return MetaSoloQExtraResult(
        snapshots=snapshots,
        runs=runs,
        extracted_at=extracted_at,
    )


def _persist_runs(new_runs: list[AdapterRun], *, extracted_at: str) -> None:
    """Merge de nuevas runs con telemetria histórica por adapter."""
    existing = json_storage.read_adapter_runs()
    runs_map = existing.get("runs", {}) if isinstance(existing, dict) else {}
    for run_obj in new_runs:
        runs_map[run_obj.adapter_id] = run_obj.__dict__
    payload = {
        "schema_version": 1,
        "last_updated_at": extracted_at,
        "runs": runs_map,
    }
    json_storage.save_adapter_runs(payload)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None).isoformat() + "Z"
