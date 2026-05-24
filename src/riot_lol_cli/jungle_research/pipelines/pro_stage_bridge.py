"""
Bridge pro-stage → jungle scoring.

Cierra el gap reportado en el audit jungle_research: `pro_presence_score`
estaba hardcoded a 0 si no había `RIOT_API_KEY` + cuentas resueltas via
Riot match-v5. Este módulo alimenta `pro_presence` desde `esports_research`
gold features (`comfort_features_*.json`), sin depender de Riot API.

Flujo:
1. Lee el archivo `comfort_features_*.json` más reciente de
   `data/esports_research/gold/`.
2. Agrega comfort por champion (max entre jugadores del rol).
3. Convierte `champion_id` (Data Dragon canonical) → `champion_name`
   usando `champion_base.json` del Draft Advisor.
4. Normaliza a [0, 1].
5. Retorna dict `{champion_name: pro_presence_score}`.

Si no hay archivo gold, retorna `{}` con gap visible — el orquestador
sabe que `STEP_PRO_STAGE` requirió bridge pero no había datos disponibles.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from riot_lol_cli import paths

logger = logging.getLogger(__name__)

# Gold features de esports_research (escritos por compute_comfort_scores).
ESPORTS_GOLD_DIR = paths.DATA_DIR / "esports_research" / "gold"

# Roster canónico para mapear champion_id (Data Dragon) → display_name.
CHAMPION_BASE_FILE = paths.DATA_DIR / "draft_advisor" / "champion_base.json"


@dataclass
class ProStageBridgeResult:
    """Resultado de leer comfort de esports y producir pro_presence."""

    pro_presence: dict[str, float] = field(default_factory=dict)
    source_file: str | None = None
    extracted_at: str | None = None
    champion_count: int = 0
    gaps: list[str] = field(default_factory=list)


def load_pro_presence_from_esports(
    *, role: str = "jungle", gold_dir: Path | None = None
) -> ProStageBridgeResult:
    """
    Lee el comfort_features más reciente de esports y produce un dict
    `{champion_name: pro_presence_score}` listo para inyectar al scoring
    de jungla.

    Args:
        role: filtro de rol. Hoy V0 NO filtra (todo lo que esté en el
            gold features se considera). Cuando ComfortScore incorpore
            role como campo, agregar filtro acá.
        gold_dir: override para tests. Default: `data/esports_research/gold/`.
    """
    base_dir = gold_dir or ESPORTS_GOLD_DIR
    if not base_dir.exists():
        return ProStageBridgeResult(
            gaps=[f"gold dir no existe: {base_dir}"],
        )
    latest = _find_latest_comfort_file(base_dir)
    if latest is None:
        return ProStageBridgeResult(
            gaps=["sin archivos comfort_features_*.json en gold dir"],
        )

    raw = _read_json(latest)
    if not isinstance(raw, list):
        return ProStageBridgeResult(
            source_file=latest.name,
            gaps=[f"comfort_features no es lista: {type(raw).__name__}"],
        )

    if not raw:
        return ProStageBridgeResult(
            source_file=latest.name,
            gaps=["comfort_features vacío"],
        )

    # Agregar max de comfort_score por champion_id.
    max_by_champion: dict[str, float] = {}
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        champion_id = entry.get("champion_id")
        comfort = entry.get("comfort_score")
        if not champion_id or comfort is None:
            continue
        prev = max_by_champion.get(champion_id, 0.0)
        if comfort > prev:
            max_by_champion[champion_id] = float(comfort)

    if not max_by_champion:
        return ProStageBridgeResult(
            source_file=latest.name,
            gaps=["sin entries válidas con champion_id + comfort_score"],
        )

    # Normalizar a [0, 1] sobre el max del pool.
    pool_max = max(max_by_champion.values())
    if pool_max <= 0:
        return ProStageBridgeResult(
            source_file=latest.name,
            gaps=["pool max <= 0, no se puede normalizar"],
        )

    # Mapear champion_id -> champion_name vía champion_base.json.
    id_to_name = _load_id_to_name_map()

    pro_presence: dict[str, float] = {}
    unmapped: list[str] = []
    for champion_id, comfort in max_by_champion.items():
        normalized = round(comfort / pool_max, 4)
        # Si no hay mapping, usar el champion_id directo (asume adapter usó
        # ID canónico Data Dragon como name).
        name = id_to_name.get(champion_id, champion_id)
        if name == champion_id and champion_id not in id_to_name:
            unmapped.append(champion_id)
        pro_presence[name] = normalized

    gaps: list[str] = []
    if unmapped:
        gaps.append(
            f"{len(unmapped)} champion_id sin mapping en champion_base.json "
            f"(usando ID directo como name): {unmapped[:5]}"
        )

    return ProStageBridgeResult(
        pro_presence=pro_presence,
        source_file=latest.name,
        extracted_at=_extract_date_from_filename(latest.name),
        champion_count=len(pro_presence),
        gaps=gaps,
    )


def _find_latest_comfort_file(base_dir: Path) -> Path | None:
    """Devuelve el archivo `comfort_features_*.json` con fecha más reciente."""
    candidates = sorted(
        base_dir.glob("comfort_features_*.json"),
        key=lambda p: p.name,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _read_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as exc:
        logger.warning("read_json falló para %s: %s", path, exc)
        return None


def _load_id_to_name_map() -> dict[str, str]:
    """Mapea champion_id (Data Dragon) → display_name desde champion_base.json."""
    if not CHAMPION_BASE_FILE.exists():
        return {}
    raw = _read_json(CHAMPION_BASE_FILE)
    if not isinstance(raw, dict):
        return {}
    mapping: dict[str, str] = {}
    champions = raw.get("champions") or raw.get("data") or raw
    if isinstance(champions, dict):
        for champion_id, info in champions.items():
            if isinstance(info, dict):
                display = info.get("display_name") or info.get("name") or champion_id
                mapping[champion_id] = display
    elif isinstance(champions, list):
        for item in champions:
            if isinstance(item, dict):
                cid = item.get("id") or item.get("champion_id")
                display = item.get("display_name") or item.get("name") or cid
                if cid:
                    mapping[cid] = display
    return mapping


def _extract_date_from_filename(name: str) -> str | None:
    """`comfort_features_2026-05-24.json` → `2026-05-24`."""
    if not name.startswith("comfort_features_") or not name.endswith(".json"):
        return None
    return name[len("comfort_features_"):-len(".json")] or None
