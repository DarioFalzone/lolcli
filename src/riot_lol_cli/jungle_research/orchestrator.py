"""
Orquestador de pipelines para Jungle Research.

Centraliza la composición de pipelines (`meta_soloq`, `meta_soloq_extra`,
`meta_asia`, `pro_accounts`) detrás de una interfaz declarativa
(`RefreshPlan`), dejando el router HTTP como adaptador delgado.

Razón del refactor (audit Codex 2026-05-12):

> "_consolidate_and_save() en jungle_research.py decide qué pipelines
> correr, mergea snapshots, maneja gaps, lee cache Asia y persiste
> tierlist. Eso debería migrar a un servicio tipo
> jungle_research/orchestrator.py, dejando el router como adaptador HTTP."

Interfaz:

    plan = RefreshPlan(steps={"soloq", "extra", "asia"})
    result = consolidate(plan, region="GLOBAL", elo="EMERALD_PLUS")

`steps` es un set: el orden de ejecución lo decide el orquestador
internamente (asia primero para alimentar scoring; soloq+extras para el
pool de snapshots; pros aparte). Esto reemplaza la combinación de flags
`include_extra` / `include_asia` que crecía con cada fase.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from riot_lol_cli.jungle_research import json_storage
from riot_lol_cli.jungle_research.pipelines import (
    meta_asia,
    meta_soloq,
    meta_soloq_extra,
    pro_stage_bridge,
)
from riot_lol_cli.jungle_research.pipelines import (
    pro_accounts as pro_accounts_pipeline,
)
from riot_lol_cli.jungle_research.riot_bridge import RiotBridge
from riot_lol_cli.jungle_research.schemas import (
    ChampionMetaSnapshot,
    FinalJungleTierList,
    utcnow_iso,
)
from riot_lol_cli.jungle_research.scoring_engine import score_snapshots

logger = logging.getLogger(__name__)

# Steps canónicos. El router los mapea desde `modes=list[str]` o el
# `mode: Literal[...]` legacy. Mantener este set único de strings evita
# inconsistencias entre código y docs.
STEP_SOLOQ = "soloq"               # Meta Scraper local + Jungle Meta curated
STEP_EXTRA = "extra"               # Adapters V3 (METAsrc/Mobalytics/LoG/Tracker)
STEP_ASIA = "asia"                 # Pipeline V4 KR/JP/CN + asia_presence
STEP_RIOT_PROS = "riot_pros"       # Resolución de Riot ID + match history
STEP_PRO_STAGE = "pro_stage"       # PR-C: comfort de esports_research → pro_presence

VALID_STEPS = frozenset({
    STEP_SOLOQ, STEP_EXTRA, STEP_ASIA, STEP_RIOT_PROS, STEP_PRO_STAGE,
})


@dataclass
class RefreshPlan:
    """
    Plan declarativo de qué pipelines correr y bajo qué contexto.

    Ejemplos:

        # Solo soloq local (compat con `mode=soloq` legacy):
        RefreshPlan(steps={"soloq"})

        # Todo el meta consolidado:
        RefreshPlan(steps={"soloq", "extra", "asia"})

        # Solo asia (poblar cache sin tocar tier list):
        RefreshPlan(steps={"asia"}, regenerate_tierlist=False)

        # Todo + pros:
        RefreshPlan(steps={"soloq", "extra", "asia", "riot_pros"})
    """

    steps: set[str] = field(default_factory=set)
    region: str = "GLOBAL"
    elo: str = "EMERALD_PLUS"
    queue: str = "ranked_solo_5x5"
    # Si False, el orquestador no regenera `final_jungle_tierlist/latest.json`.
    # Útil para `mode=asia` puro o telemetría aislada de adapters V3.
    regenerate_tierlist: bool = True
    # Override explícito de asia_presence (raro; útil para tests).
    asia_presence_override: dict[str, float] | None = None
    # Override de pro_presence (V2.6 cache; hoy no se usa).
    pro_presence_override: dict[str, float] | None = None

    def __post_init__(self) -> None:
        invalid = self.steps - VALID_STEPS
        if invalid:
            raise ValueError(
                f"Steps inválidos: {sorted(invalid)}. Válidos: {sorted(VALID_STEPS)}"
            )


@dataclass
class OrchestratorResult:
    """Resultado consolidado de una corrida del orquestador."""

    success: bool
    plan: RefreshPlan
    started_at: str
    finished_at: str
    soloq_summary: dict[str, Any] | None = None
    extra_summary: dict[str, Any] | None = None
    asia_summary: dict[str, Any] | None = None
    pros_summary: dict[str, Any] | None = None
    tierlist_summary: dict[str, Any] | None = None
    gaps: list[str] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "steps": sorted(self.plan.steps),
            "region": self.plan.region,
            "elo": self.plan.elo,
            "queue": self.plan.queue,
            "regenerate_tierlist": self.plan.regenerate_tierlist,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "soloq": self.soloq_summary,
            "extra": self.extra_summary,
            "asia": self.asia_summary,
            "pros": self.pros_summary,
            "tierlist": self.tierlist_summary,
            "gaps": self.gaps,
        }


def consolidate(plan: RefreshPlan) -> OrchestratorResult:
    """
    Ejecuta el `RefreshPlan` y persiste artifacts según corresponda.

    Orden interno fijo:
      1. asia (poblar cache antes del scoring)
      2. soloq (cohorte SoloQ global)
      3. extra (adapters V3 — mergean al pool si están ok)
      4. scoring + persistencia tier list (si `regenerate_tierlist`)
      5. pros (independiente del scoring)
    """
    started_at = utcnow_iso()
    result = OrchestratorResult(
        success=True, plan=plan, started_at=started_at, finished_at=""
    )

    snapshots: list[ChampionMetaSnapshot] = []
    sources_used: list[str] = []
    gaps_raw: list[Any] = []
    patch: str | None = None
    asia_presence: dict[str, float] = {}
    asia_warnings_by_champ: dict[str, list[str]] = {}
    asia_stale = False

    # 1. Asia (si está en plan): corre y genera asia_presence fresco.
    if STEP_ASIA in plan.steps:
        asia_result = meta_asia.run(
            elo="challenger", queue=plan.queue, persist=True
        )
        asia_presence = asia_result.asia_presence
        asia_warnings_by_champ = asia_result.asia_warnings
        for run_obj in asia_result.runs:
            sources_used.append(run_obj.adapter_id)
            if run_obj.status != "ok":
                gaps_raw.append(
                    {"reason": f"{run_obj.adapter_id}: {run_obj.reason[:140]}"}
                )
        result.asia_summary = {
            "asia_snapshots": len(asia_result.snapshots),
            "asia_presence_size": len(asia_presence),
            "warnings_champion_count": len(asia_warnings_by_champ),
            "runs": [
                {"adapter_id": r.adapter_id, "status": r.status}
                for r in asia_result.runs
            ],
            "extracted_at": asia_result.extracted_at,
        }
    elif plan.asia_presence_override is not None:
        asia_presence = plan.asia_presence_override
    else:
        # Plan no pide asia. Leer cache solo si está fresh (TTL).
        cached = meta_asia.read_cached_asia_presence_with_metadata()
        asia_presence = cached.asia_presence if not cached.is_stale else {}
        asia_stale = cached.is_stale
        if asia_stale and cached.extracted_at:
            gaps_raw.append(
                {
                    "reason": (
                        f"asia_presence cache stale "
                        f"(edad {cached.age_hours:.1f}h > TTL); "
                        "no se aplica al scoring. Corre POST /refresh?mode=asia."
                    )
                }
            )

    # 2 + 3. SoloQ + Extras: pueblan el pool de snapshots.
    if STEP_SOLOQ in plan.steps:
        soloq = meta_soloq.run(
            region=plan.region, elo=plan.elo, queue=plan.queue, persist=True
        )
        snapshots.extend(soloq.snapshots)
        sources_used.extend(soloq.sources_used)
        gaps_raw.extend(soloq.gaps)
        patch = soloq.patch or patch
        result.soloq_summary = {
            "snapshots": len(soloq.snapshots),
            "sources_used": soloq.sources_used,
            "gaps": len(soloq.gaps),
            "patch": soloq.patch,
            "extracted_at": soloq.extracted_at,
        }

    if STEP_EXTRA in plan.steps:
        extra = meta_soloq_extra.run(
            region=plan.region, elo=plan.elo, queue=plan.queue, persist=True
        )
        snapshots.extend(extra.snapshots)
        for run_obj in extra.runs:
            sources_used.append(run_obj.adapter_id)
            if run_obj.status != "ok":
                gaps_raw.append(
                    {"reason": f"{run_obj.adapter_id}: {run_obj.reason[:140]}"}
                )
        result.extra_summary = {
            "extra_snapshots": len(extra.snapshots),
            "runs": [
                {"adapter_id": r.adapter_id, "status": r.status} for r in extra.runs
            ],
            "extracted_at": extra.extracted_at,
        }

    # 3b. Pro stage bridge (PR-C): comfort de esports → pro_presence.
    # Si STEP_PRO_STAGE está, se sobreescribe `pro_presence_override` con
    # los datos de esports_research/gold/comfort_features_*.json.
    # Si NO está pero el plan tampoco trae override, queda en {} (el
    # scoring engine usa 0 — comportamiento previo).
    pro_presence_from_bridge: dict[str, float] = {}
    pro_stage_summary: dict[str, Any] | None = None
    if STEP_PRO_STAGE in plan.steps:
        bridge_result = pro_stage_bridge.load_pro_presence_from_esports()
        pro_presence_from_bridge = bridge_result.pro_presence
        pro_stage_summary = {
            "champion_count": bridge_result.champion_count,
            "source_file": bridge_result.source_file,
            "extracted_at": bridge_result.extracted_at,
            "gaps": bridge_result.gaps,
        }
        for gap in bridge_result.gaps:
            gaps_raw.append({"reason": f"pro_stage_bridge: {gap}"})

    # 4. Scoring + persistencia tierlist.
    if plan.regenerate_tierlist:
        result.tierlist_summary = _score_and_persist(
            snapshots=snapshots,
            sources_used=sources_used,
            gaps_raw=gaps_raw,
            patch=patch or "unknown",
            plan=plan,
            asia_presence=asia_presence,
            asia_warnings_by_champ=asia_warnings_by_champ,
            asia_stale=asia_stale,
            pro_presence_from_bridge=pro_presence_from_bridge,
        )
        if not result.tierlist_summary.get("success", False):
            result.success = False
    # Adjuntar summary del bridge para visibilidad incluso si no se regenera.
    if pro_stage_summary is not None:
        result.tierlist_summary = result.tierlist_summary or {}
        result.tierlist_summary["pro_stage"] = pro_stage_summary

    # 5. Pros (independiente del scoring).
    if STEP_RIOT_PROS in plan.steps:
        bridge = RiotBridge()
        pro_result = pro_accounts_pipeline.run(bridge=bridge, persist=True)
        result.pros_summary = {
            "resolved": pro_result.resolved_count,
            "total": len(pro_result.accounts),
            "gaps": pro_result.gaps,
        }

    result.gaps = [
        g.get("reason", str(g)) if isinstance(g, dict) else str(g) for g in gaps_raw
    ]
    result.finished_at = utcnow_iso()
    return result


def _score_and_persist(
    *,
    snapshots: list[ChampionMetaSnapshot],
    sources_used: list[str],
    gaps_raw: list[Any],
    patch: str,
    plan: RefreshPlan,
    asia_presence: dict[str, float],
    asia_warnings_by_champ: dict[str, list[str]],
    asia_stale: bool,
    pro_presence_from_bridge: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Arma el tier list final desde el pool de snapshots y lo persiste.

    Orden de resolución de `pro_presence`:
    1. `plan.pro_presence_override` (explicit override en plan).
    2. `pro_presence_from_bridge` (esports comfort vía STEP_PRO_STAGE).
    3. `{}` (scoring usa 0 — comportamiento histórico).
    """
    if not snapshots:
        return {
            "success": False,
            "reason": "0 snapshots para consolidar",
            "patch": patch,
            "asia_presence_applied": len(asia_presence),
        }
    pro_presence = (
        plan.pro_presence_override
        if plan.pro_presence_override is not None
        else (pro_presence_from_bridge or {})
    )
    pro_presence_source = (
        "override" if plan.pro_presence_override is not None
        else ("esports_bridge" if pro_presence_from_bridge else "none")
    )
    entries = score_snapshots(
        snapshots,
        patch=patch,
        region=plan.region,
        elo=plan.elo,
        pro_presence=pro_presence,
        asia_presence=asia_presence,
    )
    # Anotar warnings de asia por campeón en los entries correspondientes.
    if asia_warnings_by_champ:
        for entry in entries:
            extra = asia_warnings_by_champ.get(entry.champion_name)
            if extra:
                entry.warning_flags.extend(extra)
    # Warning global si se aplicó cache asia stale.
    tierlist_warning_flags = ["asia_presence_stale"] if asia_stale else []
    tierlist = FinalJungleTierList(
        generated_at=utcnow_iso(),
        patch=patch,
        region=plan.region,
        elo=plan.elo,
        queue=plan.queue,
        entries=entries,
        source_count_total=len(set(sources_used)),
        gaps=[
            g.get("reason", str(g)) if isinstance(g, dict) else str(g) for g in gaps_raw
        ],
        warning_flags=tierlist_warning_flags,
    )
    json_storage.save_final_tierlist(tierlist.model_dump(mode="json"))
    return {
        "success": True,
        "patch": tierlist.patch,
        "entries": len(entries),
        "sources_used": sorted(set(sources_used)),
        "gaps": tierlist.gaps,
        "generated_at": tierlist.generated_at,
        "asia_presence_applied": len(asia_presence),
        "asia_stale": asia_stale,
        "pro_presence_applied": len(pro_presence),
        "pro_presence_source": pro_presence_source,
        "warning_flags": tierlist_warning_flags,
    }
