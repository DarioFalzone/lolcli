"""
Pipeline meta_asia - alto elo asiatico (KR/CN/JP).

Orquesta los 8 adapters V4 (OP.GG KR/JP/CN, PORO.GG, FOW, LOL.PS,
DEEPLOL, Tencent 101, Tencent rank). Su output va por dos caminos:

1. **Snapshots**: cada champion que aparece en una fuente asiatica produce
   un `ChampionMetaSnapshot` con `region` reflejando el origen real (KR,
   JP, CN). NO se mezcla con la cohorte global - queda en un pool aparte.

2. **asia_presence**: dict `champion_name -> score 0-1` que se inyecta al
   `score_snapshots(asia_presence=...)`. El score se calcula como:
   - presencia en multiples regiones asiaticas suma
   - alto win rate o pick rate en esas regiones suma
   - clampeado a [0, 1]

V1 (today): los 8 adapters son stubs - el pipeline corre, persiste telemetria
en `adapter_runs.json` con merge historico, y devuelve `asia_presence={}`
hasta que se active algun extract real.

Telemetria comparte el archivo `adapter_runs.json` con `meta_soloq_extra`
(merge por adapter_id, no por pipeline).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from riot_lol_cli.jungle_research import json_storage
from riot_lol_cli.jungle_research.pipelines.meta_soloq_extra import (
    AdapterRun,
    _persist_runs,
)
from riot_lol_cli.jungle_research.schemas import ChampionMetaSnapshot, utcnow_iso

logger = logging.getLogger(__name__)


@dataclass
class MetaAsiaResult:
    snapshots: list[ChampionMetaSnapshot] = field(default_factory=list)
    runs: list[AdapterRun] = field(default_factory=list)
    asia_presence: dict[str, float] = field(default_factory=dict)
    # Warnings por campeón (`asia_sample_low`, `asia_sample_unknown`).
    # El orquestador los inyecta a `warning_flags` del FinalJungleTierEntry
    # cuando aplica scoring con este asia_presence.
    asia_warnings: dict[str, list[str]] = field(default_factory=dict)
    extracted_at: str = ""

    def to_payload(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "extracted_at": self.extracted_at,
            "snapshot_count": len(self.snapshots),
            "asia_presence": self.asia_presence,
            "warnings_by_champion": self.asia_warnings,
            "runs": [r.__dict__ for r in self.runs],
        }


# Mapeo adapter_id -> region canonica usada en los snapshots y para
# calcular `asia_presence` ponderada por region.
ADAPTER_REGION = {
    "opgg_kr": "KR",
    "opgg_jp": "JP",
    "opgg_cn": "CN",
    "porogg_champions": "KR",
    "fow_kr": "KR",
    "lolps": "KR",
    "deeplol_kr_jungle": "KR",
    "tencent_101": "CN",
    "tencent_rank": "CN",
}

# Pesos por region para `asia_presence`. KR pesa mas porque historicamente
# anticipa mejor el meta global.
REGION_WEIGHT = {
    "KR": 1.0,
    "CN": 0.8,
    "JP": 0.5,
}


def _default_adapters() -> dict[str, Any]:
    """Carga los 8 adapters V4 con import lazy para tests."""
    from riot_lol_cli.meta_scraper.adapters.asia import (
        DeepLolKrAdapter,
        FowKrAdapter,
        LolPsAdapter,
        OpGgCnAdapter,
        OpGgJpAdapter,
        OpGgKrAdapter,
        PoroGgAdapter,
        Tencent101Adapter,
        TencentRankAdapter,
    )

    return {
        "opgg_kr": OpGgKrAdapter(),
        "opgg_jp": OpGgJpAdapter(),
        "opgg_cn": OpGgCnAdapter(),
        "porogg_champions": PoroGgAdapter(),
        "fow_kr": FowKrAdapter(),
        "lolps": LolPsAdapter(),
        "deeplol_kr_jungle": DeepLolKrAdapter(),
        "tencent_101": Tencent101Adapter(),
        "tencent_rank": TencentRankAdapter(),
    }


def _snapshots_from_adapter_payload(
    *,
    source_id: str,
    payload: dict[str, Any],
    region: str,
    elo: str,
    queue: str,
) -> list[ChampionMetaSnapshot]:
    """Convierte el dict crudo del adapter en snapshots asia por campeon."""
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
                region=region,  # KR/JP/CN, no GLOBAL
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
                methodology_notes=f"Asia adapter V4 ({source_id}, region={region})",
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


# Threshold de games "confiable" en asia. Bajo esto la contribución se
# penaliza para no inflar campeones con muestra trivial.
ASIA_GAMES_FULL_TRUST = 2000
ASIA_GAMES_MIN_TRUST = 200


def _games_boost(games: int | None) -> float:
    """
    Devuelve 0.0-1.0 según games. Penaliza muestras chicas para evitar
    que un champion con WR 54% en 50 games normalice a 1.0 si es el max.

    - games >= 2000: full trust (1.0)
    - games >= 200: scaling lineal entre 0.3 y 1.0
    - games <  200: 0.3 piso (sigue contando pero muy poco)
    - games is None (fuente sin sample_size): 0.5 neutral
    """
    if games is None:
        return 0.5
    if games >= ASIA_GAMES_FULL_TRUST:
        return 1.0
    if games >= ASIA_GAMES_MIN_TRUST:
        ratio = (games - ASIA_GAMES_MIN_TRUST) / (ASIA_GAMES_FULL_TRUST - ASIA_GAMES_MIN_TRUST)
        return 0.3 + 0.7 * ratio
    return 0.3


def _compute_asia_presence(
    snapshots: list[ChampionMetaSnapshot],
) -> tuple[dict[str, float], dict[str, list[str]]]:
    """
    Calcula `champion_name -> presence_score` 0-1 desde snapshots asia.

    Heurística V2 (sample-aware):
    - Cada champion acumula `region_weight × wr_boost × games_boost` por
      cada fuente que lo reporta.
    - WR boost: ≥53% full (1.0), 50-53% medio (0.6), <50% bajo (0.2),
      None neutral (0.5).
    - Region weight: KR 1.0, CN 0.8, JP 0.5, otro 0.3.
    - Games boost: ≥2000 full (1.0), 200-2000 escalado lineal, <200 piso
      0.3, None neutral 0.5.
    - Normalizado al máximo del pool.

    Devuelve:
        (asia_presence, warning_flags_by_champion)
        - warning_flags_by_champion: `{"Wukong": ["asia_sample_low"], ...}`
          cuando TODAS las muestras del champion están por debajo de
          ASIA_GAMES_MIN_TRUST. Útil para el orquestador para anotar el
          tier list final.
    """
    if not snapshots:
        return {}, {}
    raw_scores: dict[str, float] = {}
    max_games_seen: dict[str, int] = {}
    for snap in snapshots:
        region = snap.region.upper()
        region_w = REGION_WEIGHT.get(region, 0.3)
        if snap.win_rate is None:
            wr_boost = 0.5
        elif snap.win_rate >= 53.0:
            wr_boost = 1.0
        elif snap.win_rate >= 50.0:
            wr_boost = 0.6
        else:
            wr_boost = 0.2
        games_boost = _games_boost(snap.games)
        raw_scores[snap.champion_name] = raw_scores.get(snap.champion_name, 0.0) + (
            region_w * wr_boost * games_boost
        )
        # Track del max games observado por champion para warning_flags.
        if snap.games is not None:
            prev = max_games_seen.get(snap.champion_name, 0)
            if snap.games > prev:
                max_games_seen[snap.champion_name] = snap.games
    if not raw_scores:
        return {}, {}
    max_score = max(raw_scores.values())
    if max_score <= 0:
        return {}, {}
    presence = {name: round(score / max_score, 4) for name, score in raw_scores.items()}
    # Warnings: champion con max_games visto < umbral.
    warnings: dict[str, list[str]] = {}
    for name in presence:
        observed = max_games_seen.get(name, 0)
        if observed and observed < ASIA_GAMES_MIN_TRUST:
            warnings[name] = ["asia_sample_low"]
        elif name not in max_games_seen:
            # Ninguna fuente reportó games (todas fueron None) -> aviso suave.
            warnings[name] = ["asia_sample_unknown"]
    return presence, warnings


def run(
    *,
    adapters: dict[str, Any] | None = None,
    elo: str = "challenger",
    queue: str = "ranked_solo_5x5",
    persist: bool = True,
) -> MetaAsiaResult:
    """
    Invoca los 8 adapters asia y agrega snapshots + asia_presence.

    Args:
        adapters: dict {source_id: adapter_instance}. Si None, usa los 8 default.
        elo: por default "challenger" (foco V4 = high elo).
        queue: contexto canonico.
        persist: si True, escribe adapter_runs.json (merge con telemetria
            existente de meta_soloq_extra).
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
        region = ADAPTER_REGION.get(source_id, "ASIA")

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

    asia_presence, asia_warnings = _compute_asia_presence(snapshots)

    if persist:
        _persist_runs(runs, extracted_at=extracted_at)
        # Cache de asia_presence para que el scoring siguiente lo lea sin re-llamar adapters.
        json_storage.save_asia_presence(
            {
                "schema_version": 1,
                "extracted_at": extracted_at,
                "elo": elo,
                "snapshot_count": len(snapshots),
                "asia_presence": asia_presence,
                "warnings_by_champion": asia_warnings,
            }
        )

    return MetaAsiaResult(
        snapshots=snapshots,
        runs=runs,
        asia_presence=asia_presence,
        asia_warnings=asia_warnings,
        extracted_at=extracted_at,
    )


# TTL del cache asia_presence: pasado este umbral, el cache se considera
# stale y NO se aplica al scoring (devolvemos {} + warning para que el
# tier list no use datos viejos silenciosamente).
ASIA_PRESENCE_TTL_HOURS = 48.0


@dataclass
class CachedAsiaPresence:
    """Resultado de leer el cache con metadata de freshness."""

    asia_presence: dict[str, float]
    extracted_at: str | None
    age_hours: float | None
    is_stale: bool
    snapshot_count: int


def read_cached_asia_presence(
    *, max_age_hours: float = ASIA_PRESENCE_TTL_HOURS, now: datetime | None = None
) -> dict[str, float]:
    """
    Lee asia_presence cacheado. Devuelve `{}` si el cache es stale (>TTL).

    Para detalle con metadata (edad, stale flag), usar
    `read_cached_asia_presence_with_metadata()`.
    """
    cached = read_cached_asia_presence_with_metadata(
        max_age_hours=max_age_hours, now=now
    )
    return cached.asia_presence if not cached.is_stale else {}


def read_cached_asia_presence_with_metadata(
    *, max_age_hours: float = ASIA_PRESENCE_TTL_HOURS, now: datetime | None = None
) -> CachedAsiaPresence:
    """Lee asia_presence + indica freshness. Usado por orquestador + UI."""
    payload = json_storage.read_asia_presence()
    if not payload:
        return CachedAsiaPresence(
            asia_presence={},
            extracted_at=None,
            age_hours=None,
            is_stale=False,  # no es stale, simplemente no existe
            snapshot_count=0,
        )
    extracted_at = payload.get("extracted_at")
    raw_presence = payload.get("asia_presence", {})
    snapshot_count = int(payload.get("snapshot_count", 0))
    age_hours = _hours_since(extracted_at, now=now) if extracted_at else None
    is_stale = age_hours is not None and age_hours > max_age_hours
    return CachedAsiaPresence(
        asia_presence=raw_presence,
        extracted_at=extracted_at,
        age_hours=age_hours,
        is_stale=is_stale,
        snapshot_count=snapshot_count,
    )


def _hours_since(iso: str, *, now: datetime | None = None) -> float:
    """Horas desde un timestamp ISO. Tolera sufijo 'Z' y microsegundos."""
    now = now or datetime.now(timezone.utc)
    cleaned = iso.rstrip("Z")
    try:
        dt = datetime.fromisoformat(cleaned)
    except ValueError:
        return float("inf")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return max((now - dt).total_seconds() / 3600.0, 0.0)
