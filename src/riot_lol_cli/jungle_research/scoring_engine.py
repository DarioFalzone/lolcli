"""
Scoring engine — consenso entre fuentes.

No copia ninguna tier list externa. Construye un score normalizado por
percentil dentro de la cohorte `(patch, role=jungle, region, elo, queue)` y
combina capas con pesos explícitos.

Fórmula V1:

    final_score =
        0.30 * win_rate_score
      + 0.20 * pick_rate_score
      + 0.10 * ban_rate_score
      + 0.15 * sample_size_score
      + 0.10 * high_elo_presence_score   # 0 en V1; queda hook
      + 0.10 * pro_presence_score        # desde match_history pros
      + 0.05 * trend_score               # diff vs latest backup

    confidence =
        0.25 * source_count_score
      + 0.25 * sample_size_score
      + 0.25 * freshness_score
      + 0.25 * source_agreement_score

Reglas duras:

- Normalizar SIEMPRE por percentil dentro de la cohorte. Nunca comparar
  Emerald+ global con Challenger KR sin capa explícita.
- Outlier extremo se conserva con `warning_flags=["outlier:metric"]`. No se
  elimina del cálculo.
- Si `games < THRESHOLD_LOW_SAMPLE`, agregar flag `sample_size_low`.
- Si `extracted_at` es más viejo que 72h, agregar flag `stale_>72h`.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from datetime import datetime, timedelta, timezone
from statistics import mean, stdev

from riot_lol_cli.jungle_research.schemas import (
    ChampionMetaSnapshot,
    FinalJungleTierEntry,
    JungleTier,
)

# Pesos de la fórmula final.
WEIGHTS_FINAL = {
    "win_rate": 0.30,
    "pick_rate": 0.20,
    "ban_rate": 0.10,
    "sample_size": 0.15,
    "high_elo_presence": 0.10,
    "pro_presence": 0.10,
    "trend": 0.05,
}

WEIGHTS_CONFIDENCE = {
    "source_count": 0.25,
    "sample_size": 0.25,
    "freshness": 0.25,
    "source_agreement": 0.25,
}

# Thresholds operativos.
THRESHOLD_LOW_SAMPLE = 1000  # partidas
THRESHOLD_STALE_HOURS = 72
THRESHOLD_OUTLIER_STDEVS = 3.0

# Tier cuts en percentil del final_score (0-1).
TIER_CUTS: list[tuple[float, JungleTier]] = [
    (0.85, JungleTier.S),
    (0.70, JungleTier.A),
    (0.50, JungleTier.B),
    (0.30, JungleTier.C),
]


def _percentile_score(value: float | None, all_values: list[float]) -> float:
    """Devuelve percentil 0-1 de `value` dentro de `all_values`. None → 0.5 neutral."""
    if value is None or not all_values:
        return 0.5
    sorted_vals = sorted(all_values)
    n = len(sorted_vals)
    # rank = cantidad de valores <= value
    rank = sum(1 for v in sorted_vals if v <= value)
    return rank / n if n else 0.5


def _is_outlier(value: float, all_values: list[float]) -> bool:
    if len(all_values) < 3:
        return False
    mu = mean(all_values)
    sd = stdev(all_values)
    if sd == 0:
        return False
    return abs(value - mu) > THRESHOLD_OUTLIER_STDEVS * sd


def _hours_since(iso: str, now: datetime | None = None) -> float:
    """Horas transcurridas desde un timestamp ISO. Tolera 'Z' suffix."""
    now = now or datetime.now(timezone.utc)
    cleaned = iso.rstrip("Z")
    try:
        dt = datetime.fromisoformat(cleaned)
    except ValueError:
        return float("inf")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta: timedelta = now - dt
    return max(delta.total_seconds() / 3600.0, 0.0)


def _freshness_score(iso: str, now: datetime | None = None) -> float:
    """1.0 si <12h, 0.5 si <72h, 0.1 si más viejo."""
    hours = _hours_since(iso, now=now)
    if hours < 12:
        return 1.0
    if hours < THRESHOLD_STALE_HOURS:
        return 0.5
    return 0.1


def _agreement_score(values: list[float]) -> float:
    """1.0 si todos coinciden; baja con la dispersión."""
    if len(values) < 2:
        return 1.0
    sd = stdev(values) if len(values) > 1 else 0.0
    mu = mean(values) or 1.0
    cv = sd / abs(mu) if mu else 1.0  # coef. variación
    return max(0.0, 1.0 - cv)


def _tier_for_percentile(p: float) -> JungleTier:
    for cut, tier in TIER_CUTS:
        if p >= cut:
            return tier
    return JungleTier.D


def _group_by_champion(
    snapshots: Iterable[ChampionMetaSnapshot],
) -> dict[str, list[ChampionMetaSnapshot]]:
    out: dict[str, list[ChampionMetaSnapshot]] = defaultdict(list)
    for snap in snapshots:
        out[snap.champion_name].append(snap)
    return dict(out)


def score_snapshots(
    snapshots: list[ChampionMetaSnapshot],
    *,
    patch: str,
    region: str,
    elo: str,
    pro_presence: dict[str, float] | None = None,
    asia_presence: dict[str, float] | None = None,
    previous_scores: dict[str, float] | None = None,
    now: datetime | None = None,
) -> list[FinalJungleTierEntry]:
    """
    Convierte snapshots crudos en tier list final por consenso.

    Args:
        snapshots: snapshots de la cohorte (mismo patch, region, elo, queue).
        patch/region/elo: contexto canónico.
        pro_presence: dict champion_name → score 0-1 (opcional, V1 puede ser {}).
        asia_presence: dict champion_name → score 0-1 con presencia en alto
            elo asiático (KR/CN/JP). Hook V4 — vacío hasta que se active
            el pipeline `meta_asia`. Alimenta el peso `high_elo_presence`
            del `final_score`.
        previous_scores: NO-OP hoy. Reservado para implementación real de
            `trend_score` desde backups (roadmap V10). Mantener firma para
            no romper callers; los valores se ignoran.
        now: inyectable para tests.
    """
    pro_presence = pro_presence or {}
    asia_presence = asia_presence or {}
    _ = previous_scores  # explícitamente sin usar — ver docstring
    now = now or datetime.now(timezone.utc)

    grouped = _group_by_champion(snapshots)
    if not grouped:
        return []

    # Pools por métrica para percentiles (a nivel cohorte, agregando por campeón).
    aggregated: dict[str, dict[str, float]] = {}
    for champ, snaps in grouped.items():
        wrs = [s.win_rate for s in snaps if s.win_rate is not None]
        prs = [s.pick_rate for s in snaps if s.pick_rate is not None]
        brs = [s.ban_rate for s in snaps if s.ban_rate is not None]
        gms = [s.games for s in snaps if s.games is not None]
        aggregated[champ] = {
            "win_rate": mean(wrs) if wrs else 0.0,
            "pick_rate": mean(prs) if prs else 0.0,
            "ban_rate": mean(brs) if brs else 0.0,
            "sample_size": float(sum(gms)) if gms else 0.0,
        }

    pool_wr = [a["win_rate"] for a in aggregated.values() if a["win_rate"]]
    pool_pr = [a["pick_rate"] for a in aggregated.values() if a["pick_rate"]]
    pool_br = [a["ban_rate"] for a in aggregated.values() if a["ban_rate"]]
    pool_ss = [a["sample_size"] for a in aggregated.values() if a["sample_size"]]

    entries: list[FinalJungleTierEntry] = []
    final_scores: list[tuple[str, float]] = []

    for champ, agg in aggregated.items():
        snaps = grouped[champ]
        warnings: list[str] = []

        # Capas de score por percentil.
        wr_score = _percentile_score(agg["win_rate"], pool_wr)
        pr_score = _percentile_score(agg["pick_rate"], pool_pr)
        br_score = _percentile_score(agg["ban_rate"], pool_br)
        ss_score = _percentile_score(agg["sample_size"], pool_ss)

        soloq_score = (
            0.40 * wr_score + 0.30 * pr_score + 0.10 * br_score + 0.20 * ss_score
        )

        # high_elo (asia) y pro presence — desde dicts inyectados por pipelines.
        # Si `asia_presence` viene vacio (V1 sin pipeline meta_asia), queda en 0.
        high_elo_score = max(0.0, min(1.0, asia_presence.get(champ, 0.0)))
        pro_score = pro_presence.get(champ, 0.0)

        # Trend - neutro hasta tener implementación real basada en backups.
        # NOTA: la fórmula previa `0.5 + (prev - 0.5)` no medía tendencia,
        # solo replicaba el score previo. Además `previous_scores` nunca
        # se conectó desde el orquestador. Mantener trend_score=0.5
        # constante hasta implementar trend real (diff vs último backup
        # con ventana mínima) — ver roadmap V10.
        trend_score = 0.5

        final = (
            WEIGHTS_FINAL["win_rate"] * wr_score
            + WEIGHTS_FINAL["pick_rate"] * pr_score
            + WEIGHTS_FINAL["ban_rate"] * br_score
            + WEIGHTS_FINAL["sample_size"] * ss_score
            + WEIGHTS_FINAL["high_elo_presence"] * high_elo_score
            + WEIGHTS_FINAL["pro_presence"] * pro_score
            + WEIGHTS_FINAL["trend"] * trend_score
        )

        # Warnings.
        if agg["sample_size"] and agg["sample_size"] < THRESHOLD_LOW_SAMPLE:
            warnings.append("sample_size_low")
        if any(_hours_since(s.extracted_at, now=now) > THRESHOLD_STALE_HOURS for s in snaps):
            warnings.append("stale_>72h")
        if agg["win_rate"] and _is_outlier(agg["win_rate"], pool_wr):
            warnings.append("outlier:win_rate")
        if agg["pick_rate"] and _is_outlier(agg["pick_rate"], pool_pr):
            warnings.append("outlier:pick_rate")

        # Confidence.
        sources_used = {s.source_id for s in snaps}
        per_source_wr = [s.win_rate for s in snaps if s.win_rate is not None]
        confidence = (
            WEIGHTS_CONFIDENCE["source_count"] * min(1.0, len(sources_used) / 3.0)
            + WEIGHTS_CONFIDENCE["sample_size"] * ss_score
            + WEIGHTS_CONFIDENCE["freshness"] * mean(
                _freshness_score(s.extracted_at, now=now) for s in snaps
            )
            + WEIGHTS_CONFIDENCE["source_agreement"] * _agreement_score(per_source_wr)
        )

        explanation = (
            f"WR p{int(wr_score * 100)} PR p{int(pr_score * 100)} "
            f"BR p{int(br_score * 100)} N={int(agg['sample_size'])} "
            f"sources={len(sources_used)} pro={pro_score:.2f}"
        )

        entries.append(
            FinalJungleTierEntry(
                champion_name=champ,
                role="jungle",
                final_tier=JungleTier.D,  # asignado en la 2da pasada
                final_score=final,
                soloq_score=soloq_score,
                asia_score=high_elo_score if high_elo_score else None,
                pro_soloq_score=pro_score if pro_score else None,
                pro_stage_score=None,
                otp_score=None,
                confidence=confidence,
                explanation=explanation,
                source_count=len(sources_used),
                warning_flags=warnings,
                generated_at=(now.isoformat().replace("+00:00", "Z")),
                patch=patch,
                region=region,
                elo=elo,
            )
        )
        final_scores.append((champ, final))

    # Asignación de tier por percentil del final_score.
    score_pool = [s for _, s in final_scores]
    for entry in entries:
        p = _percentile_score(entry.final_score, score_pool)
        entry.final_tier = _tier_for_percentile(p)

    entries.sort(key=lambda e: e.final_score, reverse=True)
    return entries
