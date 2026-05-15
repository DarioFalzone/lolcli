"""
Pipeline meta_soloq — fuente SoloQ activa V1.

Lee dos fuentes locales que ya existen en el repo:

1. `data/meta_scraper/normalized/latest_jungle_tier.json` — Meta Scraper :8002
   (U.GG + LoLalytics + OP.GG agregados ponderados por `games_analyzed`).
2. `data/jungle_meta/patch_*.json` más reciente — Jungle Meta :8003
   (tier list curada por humano por patch).

Cada champion se descompone en `ChampionMetaSnapshot` por fuente individual
para que el scoring engine pueda razonar por consenso. Si una fuente está en
`source_gaps`, queda registrada como flag pero **no se inventan datos**.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from riot_lol_cli import paths
from riot_lol_cli.jungle_research.json_storage import save_champion_snapshots
from riot_lol_cli.jungle_research.schemas import ChampionMetaSnapshot, utcnow_iso

logger = logging.getLogger(__name__)

META_SCRAPER_NORMALIZED = (
    paths.DATA_DIR / "meta_scraper" / "normalized" / "latest_jungle_tier.json"
)
JUNGLE_META_DIR = paths.DATA_DIR / "jungle_meta"


@dataclass
class MetaSoloQResult:
    """Resultado de una pasada del pipeline."""

    snapshots: list[ChampionMetaSnapshot]
    gaps: list[dict[str, Any]]
    sources_used: list[str]
    patch: str | None
    region: str
    elo: str
    queue: str
    extracted_at: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "extracted_at": self.extracted_at,
            "patch": self.patch,
            "region": self.region,
            "elo": self.elo,
            "queue": self.queue,
            "sources_used": self.sources_used,
            "snapshot_count": len(self.snapshots),
            "snapshots": [s.model_dump(mode="json") for s in self.snapshots],
            "gaps": self.gaps,
        }


def _read_json(path: Path) -> Any:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _latest_jungle_meta_patch_file() -> Path | None:
    """Patch file más reciente bajo data/jungle_meta/patch_*.json."""
    if not JUNGLE_META_DIR.exists():
        return None
    candidates = sorted(JUNGLE_META_DIR.glob("patch_*.json"))
    return candidates[-1] if candidates else None


def _normalize_iso(value: Any) -> str:
    """Normaliza un timestamp a ISO 8601 UTC con sufijo Z (sin microsegundos)."""
    if not isinstance(value, str) or not value:
        return utcnow_iso()
    cleaned = value.replace("+00:00", "Z")
    # Recortar microsegundos si existen, conservando sufijo Z.
    if "." in cleaned:
        head, _, tail = cleaned.partition(".")
        cleaned = head + ("Z" if "Z" in tail or "z" in tail else "")
    if not cleaned.endswith("Z"):
        cleaned += "Z"
    return cleaned


def _meta_scraper_snapshots(
    payload: dict[str, Any], *, region: str, elo: str, queue: str
) -> tuple[list[ChampionMetaSnapshot], list[dict[str, Any]], list[str]]:
    """Convierte el payload normalizado del Meta Scraper en snapshots por fuente."""
    snapshots: list[ChampionMetaSnapshot] = []
    sources_used: set[str] = set()
    gaps = list(payload.get("source_gaps", []))

    champions = payload.get("champions", [])
    for champ in champions:
        champ_id = champ.get("id") or ""
        champ_name = champ.get("display_name") or champ_id or "Unknown"
        breakdown = champ.get("source_breakdown") or {}
        for source_id, stats in breakdown.items():
            if not isinstance(stats, dict):
                continue
            sources_used.add(source_id)
            url = SOURCE_URLS.get(source_id, "")
            extracted = _normalize_iso(stats.get("scraped_at"))
            patch_str = str(stats.get("patch") or payload.get("patch") or "")
            tier_raw = stats.get("tier")
            warning_flags: list[str] = []
            tier_value = _normalize_tier(tier_raw, warning_flags)
            snapshots.append(
                ChampionMetaSnapshot(
                    source_id=f"{source_id}_jungle",
                    source_name=source_id.upper(),
                    source_url=url,
                    extracted_at=extracted,
                    patch=patch_str,
                    region=region,
                    queue=queue,
                    elo=elo,
                    role="jungle",
                    champion_id=champ_id,
                    champion_name=champ_name,
                    tier=tier_value,
                    win_rate=_safe_float(stats.get("win_rate")),
                    pick_rate=_safe_float(stats.get("pick_rate")),
                    ban_rate=_safe_float(stats.get("ban_rate")),
                    games=_safe_int(stats.get("games_analyzed")),
                    methodology_notes=f"Fuente {source_id} via meta_scraper_local",
                    warning_flags=warning_flags,
                )
            )
    return snapshots, gaps, sorted(sources_used)


SOURCE_URLS: dict[str, str] = {
    "ugg": "https://u.gg/lol/jungle-tier-list",
    "lolalytics": "https://lolalytics.com/lol/tierlist/?lane=jungle",
    "opgg": "https://op.gg/champions?position=jungle",
}


def _normalize_tier(tier_raw: Any, warnings: list[str]):
    """Mapea tiers de fuentes (S+, A+, ...) a JungleTier canónico."""
    from riot_lol_cli.jungle_research.schemas import JungleTier

    if not tier_raw:
        return None
    s = str(tier_raw).strip().upper().rstrip("+").rstrip("-")
    try:
        return JungleTier(s)
    except ValueError:
        warnings.append(f"unknown_tier:{tier_raw}")
        return None


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _curated_local_snapshots(
    payload: dict[str, Any], *, region: str, elo: str, queue: str
) -> list[ChampionMetaSnapshot]:
    """Convierte la tier list curada de Jungle Meta :8003 en snapshots."""
    snapshots: list[ChampionMetaSnapshot] = []
    extracted = _normalize_iso(payload.get("date_updated"))
    patch_str = str(payload.get("patch") or "")
    for champ in payload.get("jungle_champions", []):
        warning_flags: list[str] = []
        tier_value = _normalize_tier(champ.get("tier"), warning_flags)
        snapshots.append(
            ChampionMetaSnapshot(
                source_id="jungle_meta_local",
                source_name="Jungle Meta (curated)",
                source_url="http://localhost:8003/api/v1/jungle/tier-list",
                extracted_at=extracted,
                patch=patch_str,
                region=region,
                queue=queue,
                elo=elo,
                role="jungle",
                champion_id=str(champ.get("id") or ""),
                champion_name=str(champ.get("display_name") or champ.get("id") or "Unknown"),
                tier=tier_value,
                win_rate=_safe_float(champ.get("winrate")),
                pick_rate=_safe_float(champ.get("pickrate")),
                ban_rate=_safe_float(champ.get("banrate")),
                games=None,  # curado, no tiene sample size
                methodology_notes=f"Curated by humans: {champ.get('primary_reason') or ''}",
                warning_flags=warning_flags,
            )
        )
    return snapshots


def run(
    *,
    region: str = "GLOBAL",
    elo: str = "EMERALD_PLUS",
    queue: str = "ranked_solo_5x5",
    persist: bool = True,
) -> MetaSoloQResult:
    """
    Ejecuta el pipeline V1.

    Args:
        region/elo/queue: contexto canónico para la cohorte.
        persist: si True, escribe `champion_meta_snapshots/latest.json` y rota.
    """
    extracted_at = utcnow_iso()
    snapshots: list[ChampionMetaSnapshot] = []
    gaps: list[dict[str, Any]] = []
    sources_used: list[str] = []
    patch: str | None = None

    # Fuente 1: Meta Scraper local.
    scraper_payload = _read_json(META_SCRAPER_NORMALIZED)
    if scraper_payload:
        scraper_snaps, scraper_gaps, scraper_sources = _meta_scraper_snapshots(
            scraper_payload, region=region, elo=elo, queue=queue
        )
        snapshots.extend(scraper_snaps)
        gaps.extend(scraper_gaps)
        sources_used.extend(scraper_sources)
        patch = scraper_payload.get("patch") or patch
    else:
        gaps.append(
            {
                "source": "meta_scraper_local",
                "stage": "read_normalized",
                "reason": "latest_jungle_tier.json no existe",
                "attempted_at": extracted_at,
            }
        )

    # Fuente 2: Jungle Meta curated.
    curated_path = _latest_jungle_meta_patch_file()
    if curated_path:
        curated_payload = _read_json(curated_path)
        if curated_payload:
            curated_snaps = _curated_local_snapshots(
                curated_payload, region=region, elo=elo, queue=queue
            )
            snapshots.extend(curated_snaps)
            sources_used.append("jungle_meta_local")
            patch = patch or curated_payload.get("patch")
    else:
        gaps.append(
            {
                "source": "jungle_meta_local",
                "stage": "discover_patch_file",
                "reason": "ningún data/jungle_meta/patch_*.json encontrado",
                "attempted_at": extracted_at,
            }
        )

    result = MetaSoloQResult(
        snapshots=snapshots,
        gaps=gaps,
        sources_used=sources_used,
        patch=patch,
        region=region,
        elo=elo,
        queue=queue,
        extracted_at=extracted_at,
    )

    if persist and snapshots:
        save_champion_snapshots(result.to_payload())

    return result
