"""
Normalizador de datos de meta scraping.

Toma datos crudos de múltiples plataformas y los unifica
en un schema normalizado con timestamp, listos para consumo
por la API y el frontend.
"""

from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Resolución de paths
_BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
_DATA_DIR = _BASE_DIR / "data" / "meta_scraper"
_CHAMPION_BASE_PATH = _BASE_DIR / "data" / "draft_advisor" / "champion_base.json"

# Schema version del formato normalizado
SCHEMA_VERSION = "1.2"
SUPPORTED_ROLES = {"support", "adc", "jungle"}


def _load_champion_base() -> dict[str, str]:
    """
    Carga champion_base.json y construye un mapa de normalización
    de nombres: variantes comunes → ID canónico.

    Ejemplo: "Kai'Sa" → "Kaisa", "Miss Fortune" → "MissFortune"
    """
    name_map: dict[str, str] = {}

    if not _CHAMPION_BASE_PATH.exists():
        logger.warning("champion_base.json no encontrado en %s", _CHAMPION_BASE_PATH)
        return name_map

    with open(_CHAMPION_BASE_PATH, encoding="utf-8") as f:
        data = json.load(f)

    champions = data.get("champions", data.get("data", {}))
    if isinstance(champions, list):
        for champ in champions:
            cid = champ.get("id", champ.get("championId", ""))
            name = champ.get("name", cid)
            name_map[cid.lower()] = cid
            name_map[name.lower()] = cid
    elif isinstance(champions, dict):
        for key, champ in champions.items():
            cid = champ.get("id", key)
            name = champ.get("name", cid)
            name_map[cid.lower()] = cid
            name_map[name.lower()] = cid
            name_map[key.lower()] = cid

    logger.info("Champion name map cargado: %d entradas", len(name_map))
    return name_map


# Cache del name map (se carga una sola vez)
_CHAMPION_NAME_MAP: dict[str, str] | None = None


def _get_name_map() -> dict[str, str]:
    """Devuelve el mapa de normalización de nombres, cargándolo si es necesario."""
    global _CHAMPION_NAME_MAP
    if _CHAMPION_NAME_MAP is None:
        _CHAMPION_NAME_MAP = _load_champion_base()
    return _CHAMPION_NAME_MAP


def normalize_champion_id(raw_name: str) -> str:
    """
    Normaliza un nombre de campeón al ID canónico de champion_base.json.

    Ejemplos:
        "Kai'Sa" → "Kaisa"
        "miss fortune" → "MissFortune"
        "Thresh" → "Thresh"
    """
    name_map = _get_name_map()
    cleaned = raw_name.strip().lower().replace("'", "").replace(" ", "")
    # Intento directo
    if cleaned in name_map:
        return name_map[cleaned]
    # Intento sin apóstrofes en el map
    for key, value in name_map.items():
        if key.replace("'", "").replace(" ", "") == cleaned:
            return value
    # Fallback: devolver el nombre capitalizado
    logger.warning("Campeón '%s' no encontrado en champion_base. Usando raw.", raw_name)
    return raw_name.strip()


def merge_platform_data(
    platform_datasets: dict[str, dict],
    role: str = "support",
    elo_filter: str = "emerald_plus",
    source_gaps: list[dict] | None = None,
    min_pick_rate: float = 0.5,
) -> dict:
    """
    Mergea datos de múltiples plataformas en un dataset normalizado.

    Args:
        platform_datasets: dict[platform_name] → raw tier list data
        min_pick_rate: Limite inferior de pick rate para incluir en el dataset final.

    Returns:
        Schema normalizado unificado con promedios ponderados.
    """
    role = _normalize_role(role)
    now = datetime.now(timezone.utc).isoformat()
    merged_champions: dict[str, dict] = {}
    source_gaps = source_gaps or []
    sources = list(platform_datasets.keys())
    source_status: list[dict] = []
    patch = "unknown"

    for platform, data in platform_datasets.items():
        patch = data.get("patch", patch)
        champions = data.get("champions", [])
        source_status.append(
            {
                "source": platform,
                "status": "ok",
                "patch": data.get("patch", "unknown"),
                "role": data.get("role", role),
                "elo": data.get("elo", elo_filter),
                "champion_count": len(champions),
                "scraped_at": data.get("scraped_at"),
            }
        )

        for champ in champions:
            raw_id = champ.get("id", champ.get("champion_id", champ.get("name", "")))
            canonical_id = normalize_champion_id(raw_id)

            if canonical_id not in merged_champions:
                merged_champions[canonical_id] = {
                    "id": canonical_id,
                    "display_name": champ.get("display_name", canonical_id),
                    "stats": {
                        "win_rate": 0.0,
                        "pick_rate": 0.0,
                        "ban_rate": 0.0,
                        "games_analyzed": 0,
                        "tier": "B",
                    },
                    "source_breakdown": {},
                    "builds": champ.get("builds", {}),
                    "matchups": champ.get("matchups", {}),
                    "synergies": champ.get("synergies", {}),
                    "_sources_count": 0,
                    "_wr_sum": 0.0,
                    "_pr_sum": 0.0,
                    "_br_sum": 0.0,
                    "_games_sum": 0,
                    "_wr_weighted_sum": 0.0,
                    "_pr_weighted_sum": 0.0,
                    "_br_weighted_sum": 0.0,
                    "_weighted_games_sum": 0,
                    "_sources_without_games": 0,
                }

            entry = merged_champions[canonical_id]
            wr = champ.get("win_rate", champ.get("stats", {}).get("win_rate", 0))
            pr = champ.get("pick_rate", champ.get("stats", {}).get("pick_rate", 0))
            br = champ.get("ban_rate", champ.get("stats", {}).get("ban_rate", 0))
            games = champ.get("games_analyzed", champ.get("stats", {}).get("games_analyzed", 0))

            entry["source_breakdown"][platform] = {
                "win_rate": wr,
                "pick_rate": pr,
                "ban_rate": br,
                "games_analyzed": games,
                "tier": champ.get("tier_raw", champ.get("tier", champ.get("stats", {}).get("tier"))),
                "patch": data.get("patch", "unknown"),
                "scraped_at": data.get("scraped_at"),
            }
            entry["_sources_count"] += 1
            entry["_wr_sum"] += wr
            entry["_pr_sum"] += pr
            entry["_br_sum"] += br
            entry["_games_sum"] += games
            if games > 0:
                entry["_wr_weighted_sum"] += wr * games
                entry["_pr_weighted_sum"] += pr * games
                entry["_br_weighted_sum"] += br * games
                entry["_weighted_games_sum"] += games
            else:
                entry["_sources_without_games"] += 1

            # Mantener builds/matchups/synergies del source con más partidas
            if games > entry["stats"]["games_analyzed"]:
                if champ.get("builds"):
                    entry["builds"] = champ["builds"]
                if champ.get("matchups"):
                    entry["matchups"] = champ["matchups"]
                if champ.get("synergies"):
                    entry["synergies"] = champ["synergies"]

    # Calcular promedios y tier
    champion_list = []
    weighted_champions = 0
    fallback_champions = 0
    for entry in merged_champions.values():
        n = entry["_sources_count"]
        weighted_games = entry["_weighted_games_sum"]
        if weighted_games > 0:
            entry["stats"]["win_rate"] = round(entry["_wr_weighted_sum"] / weighted_games, 2)
            entry["stats"]["pick_rate"] = round(entry["_pr_weighted_sum"] / weighted_games, 2)
            entry["stats"]["ban_rate"] = round(entry["_br_weighted_sum"] / weighted_games, 2)
            entry["stats"]["games_analyzed"] = entry["_games_sum"]
            weighted_champions += 1
            if entry["_sources_without_games"] > 0:
                entry["stats"]["aggregation_note"] = (
                    "Fuentes sin partidas quedaron en el desglose, no en el promedio ponderado."
                )
        elif n > 0:
            entry["stats"]["win_rate"] = round(entry["_wr_sum"] / n, 2)
            entry["stats"]["pick_rate"] = round(entry["_pr_sum"] / n, 2)
            entry["stats"]["ban_rate"] = round(entry["_br_sum"] / n, 2)
            entry["stats"]["games_analyzed"] = 0
            entry["stats"]["aggregation_note"] = (
                "Promedio simple por fuente: ninguna fuente trajo partidas para ponderar."
            )
            fallback_champions += 1
        entry["stats"]["tier"] = _compute_tier(entry["stats"]["win_rate"], entry["stats"]["pick_rate"])
        entry["stats"]["climb_score"] = _compute_climb_score(
            entry["stats"]["win_rate"],
            entry["stats"]["pick_rate"],
            entry["stats"]["ban_rate"],
        )
        for key in (
            "_sources_count",
            "_wr_sum",
            "_pr_sum",
            "_br_sum",
            "_games_sum",
            "_wr_weighted_sum",
            "_pr_weighted_sum",
            "_br_weighted_sum",
            "_weighted_games_sum",
            "_sources_without_games",
        ):
            entry.pop(key, None)

        if entry["stats"]["pick_rate"] >= min_pick_rate:
            champion_list.append(entry)

    # Ordenar ADC por climb_score; support conserva orden por tier + winrate.
    tier_order = {"S": 0, "A": 1, "B": 2, "C": 3}
    if role == "adc":
        champion_list.sort(key=lambda c: -c["stats"].get("climb_score", 0))
    else:
        champion_list.sort(key=lambda c: (tier_order.get(c["stats"]["tier"], 9), -c["stats"]["win_rate"]))

    for gap in source_gaps:
        source_status.append(
            {
                "source": gap.get("source", gap.get("platform", "unknown")),
                "status": "gap",
                "stage": gap.get("stage", "adapter_fetch"),
                "reason": gap.get("reason", gap.get("error", "Error no especificado")),
                "attempted_at": gap.get("attempted_at"),
            }
        )

    fallback = None
    if champion_list and fallback_champions == len(champion_list):
        fallback = "source_average_no_games"
    elif fallback_champions:
        fallback = "partial_source_average_no_games"

    return {
        "schema_version": SCHEMA_VERSION,
        "scraped_at": now,
        "patch": patch,
        "role": role,
        "elo_filter": elo_filter,
        "sources": sources,
        "source_status": source_status,
        "source_gaps": source_gaps,
        "aggregation": {
            "method": "games_weighted_average_v1",
            "fallback": fallback,
            "weighted_champion_count": weighted_champions,
            "fallback_champion_count": fallback_champions,
        },
        "champion_count": len(champion_list),
        "champions": champion_list,
    }


def _normalize_role(role: str) -> str:
    """Normaliza el rol scrapeable al vocabulario interno."""
    normalized = role.strip().lower()
    if normalized in {"bottom", "bot", "marksman"}:
        normalized = "adc"
    if normalized not in SUPPORTED_ROLES:
        raise ValueError(f"Rol no soportado para meta scraping: {role}")
    return normalized


def _compute_tier(win_rate: float, pick_rate: float) -> str:
    """
    Calcula el tier de un campeón basado en winrate y pickrate.

    Lógica inspirada en las tier lists de las plataformas:
    - S tier: WR ≥ 52% y PR ≥ 5%, o WR ≥ 54%
    - A tier: WR ≥ 51% y PR ≥ 3%, o WR ≥ 52.5%
    - B tier: WR ≥ 49% o PR ≥ 5%
    - C tier: todo lo demás
    """
    if (win_rate >= 52 and pick_rate >= 5) or win_rate >= 54:
        return "S"
    if (win_rate >= 51 and pick_rate >= 3) or win_rate >= 52.5:
        return "A"
    if win_rate >= 49 or pick_rate >= 5:
        return "B"
    return "C"


def _compute_climb_score(win_rate: float, pick_rate: float, ban_rate: float) -> float:
    """
    Score 0-100 para ordenar picks de climb.

    Favorece winrate alto, pickrate suficiente para confianza estadistica y
    penaliza bans altos porque reducen disponibilidad real en solo queue.
    """
    wr_component = (win_rate - 50.0) * 7.0
    pr_component = min(pick_rate, 14.0) * 1.4
    ban_penalty = min(ban_rate, 35.0) * 0.35
    score = 50.0 + wr_component + pr_component - ban_penalty
    return round(max(0.0, min(100.0, score)), 2)


def save_normalized(data: dict, tag: str = "merged", role: str | None = None) -> Path:
    """
    Guarda los datos normalizados en el filesystem.

    Escribe dos archivos:
    - `normalized/history/{timestamp}_{tag}.json` — snapshot histórico
    - `normalized/latest_<role>_tier.json` — siempre apunta al más reciente

    Returns:
        Path al archivo histórico guardado.
    """
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    history_dir = _DATA_DIR / "normalized" / "history"
    history_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    history_path = history_dir / f"{timestamp}_{tag}.json"

    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info("Snapshot guardado: %s", history_path)

    # Actualizar latest
    latest_role = _normalize_role(role or data.get("role", "support"))
    latest_path = _DATA_DIR / "normalized" / f"latest_{latest_role}_tier.json"
    _backup_latest_if_needed(latest_path, latest_role)
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info("Latest actualizado: %s", latest_path)

    return history_path


def _backup_latest_if_needed(latest_path: Path, role: str) -> Path | None:
    """Backupea el ultimo snapshot de jungla antes de pisarlo."""
    if role != "jungle" or not latest_path.exists():
        return None

    backup_dir = _DATA_DIR / "normalized" / "backups" / "jungle"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    backup_path = backup_dir / f"latest_jungle_tier_{timestamp}.json"
    shutil.copy2(latest_path, backup_path)
    logger.info("Backup latest jungla guardado: %s", backup_path)
    return backup_path


def save_raw(data: dict, platform: str, tag: str = "support_tier") -> Path:
    """
    Guarda datos crudos de una plataforma individual.

    Returns:
        Path al archivo raw guardado.
    """
    raw_dir = _DATA_DIR / "raw" / platform
    raw_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    raw_path = raw_dir / f"{timestamp}_{tag}.json"

    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info("[%s] Raw guardado: %s", platform, raw_path)

    return raw_path


def load_latest(role: str = "support") -> dict | None:
    """Carga el snapshot normalizado más reciente, si existe."""
    latest_path = _DATA_DIR / "normalized" / f"latest_{_normalize_role(role)}_tier.json"
    if not latest_path.exists():
        return None
    with open(latest_path, encoding="utf-8") as f:
        return json.load(f)
