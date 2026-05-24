"""
Daily report — agrega cambios del día.

Compara el `final_jungle_tierlist/latest.json` actual con el último backup
(efectivamente "ayer" si el job corre 1x/día) y produce:

- Top junglers actuales.
- Risers (subieron tier o score).
- Fallers (bajaron tier o score).
- Contradicciones entre fuentes (campeón con WR alto en una y bajo en otra).
- Gaps acumulados de la pasada.

V1: NO toca el reporte si no existe `latest.json` (no inventa datos).
"""

from __future__ import annotations

import logging
from typing import Any

from riot_lol_cli.jungle_research import json_storage
from riot_lol_cli.jungle_research.schemas import (
    DailyReport,
    FinalJungleTierEntry,
    FinalJungleTierList,
    TierMovement,
    utcnow_iso,
)

logger = logging.getLogger(__name__)

TOP_N = 10
RISER_FALLER_LIMIT = 8


def _load_tierlist(path) -> FinalJungleTierList | None:
    raw = json_storage.read_json(path)
    if not raw:
        return None
    return FinalJungleTierList.model_validate(raw)


def _latest_backup() -> Any:
    """Intenta leer el backup más reciente del final_jungle_tierlist."""
    backups_dir = json_storage.FINAL_TIERLIST_DIR / "backups"
    if not backups_dir.exists():
        return None
    candidates = sorted(backups_dir.glob("*.json"))
    if not candidates:
        return None
    return _load_tierlist(candidates[-1])


def _movements(
    current: list[FinalJungleTierEntry],
    previous: list[FinalJungleTierEntry] | None,
) -> tuple[list[TierMovement], list[TierMovement]]:
    """Compara entries actuales vs previas. Devuelve (risers, fallers) por delta."""
    if not previous:
        return [], []
    prev_by_name: dict[str, FinalJungleTierEntry] = {e.champion_name: e for e in previous}
    movements: list[TierMovement] = []
    for entry in current:
        prev = prev_by_name.get(entry.champion_name)
        if not prev:
            continue
        delta = entry.final_score - prev.final_score
        movements.append(
            TierMovement(
                champion_name=entry.champion_name,
                previous_tier=prev.final_tier,
                current_tier=entry.final_tier,
                previous_score=prev.final_score,
                current_score=entry.final_score,
                delta=delta,
            )
        )
    risers = sorted(
        [m for m in movements if m.delta > 0], key=lambda m: m.delta, reverse=True
    )[:RISER_FALLER_LIMIT]
    fallers = sorted(
        [m for m in movements if m.delta < 0], key=lambda m: m.delta
    )[:RISER_FALLER_LIMIT]
    return risers, fallers


def _contradictions(snapshots_payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    """
    Detecta campeones con dispersión alta de WR entre fuentes (>5pp).

    Lee `champion_meta_snapshots/latest.json`. Si no existe, devuelve [].
    """
    if not snapshots_payload:
        return []
    by_champion: dict[str, list[tuple[str, float]]] = {}
    for snap in snapshots_payload.get("snapshots", []):
        wr = snap.get("win_rate")
        if wr is None:
            continue
        by_champion.setdefault(snap["champion_name"], []).append(
            (snap["source_id"], float(wr))
        )
    out: list[dict[str, Any]] = []
    for champ, pairs in by_champion.items():
        if len(pairs) < 2:
            continue
        wrs = [wr for _, wr in pairs]
        spread = max(wrs) - min(wrs)
        if spread > 5.0:
            out.append(
                {
                    "champion_name": champ,
                    "spread": round(spread, 2),
                    "by_source": dict(pairs),
                }
            )
    return sorted(out, key=lambda x: x["spread"], reverse=True)[:RISER_FALLER_LIMIT]


def generate(
    *,
    report_date: str,
    persist: bool = True,
) -> DailyReport | None:
    """
    Genera el reporte del día.

    Devuelve None si no hay tier list disponible aún (no inventa datos).
    """
    current = _load_tierlist(json_storage.FINAL_TIERLIST_LATEST)
    if not current:
        logger.info("No hay final_jungle_tierlist/latest.json — skip daily report")
        return None

    previous_obj = _latest_backup()
    previous_entries = previous_obj.entries if previous_obj else None

    risers, fallers = _movements(current.entries, previous_entries)
    snapshots_payload = json_storage.read_json(json_storage.CHAMPION_SNAPSHOTS_LATEST)
    contradictions = _contradictions(snapshots_payload)

    confidence_summary: dict[str, float] = {}
    if current.entries:
        confs = [e.confidence for e in current.entries]
        confidence_summary = {
            "min": min(confs),
            "max": max(confs),
            "avg": sum(confs) / len(confs),
        }

    report = DailyReport(
        report_date=report_date,
        generated_at=utcnow_iso(),
        patch=current.patch,
        top_junglers=current.entries[:TOP_N],
        risers=risers,
        fallers=fallers,
        pro_recent_picks=[],
        contradictions=contradictions,
        soloq_vs_pro_diff=[],
        confidence_summary=confidence_summary,
        gaps=current.gaps + current.warning_flags,
    )

    if persist:
        json_storage.save_daily_report(report_date, report.model_dump(mode="json"))

    return report
