"""
Adaptador METAsrc — Jungle tier list.

Estrategia: HTML estatico parseable con httpx + BeautifulSoup. METAsrc
hidrata con JS pero el SSR ya trae la tabla con champions, WR, PR, BR y
tier. Sin Playwright.

URL canonica: https://www.metasrc.com/lol/{region}/tier-list/jungle
Filtros via query string:
  - region: na, euw, eune, kr, ...
  - elo: emerald_plus, platinum_plus, diamond_plus, master_plus
  - patch: latest | <patch>

Estado: ACTIVO V3.7 [2026-05-24]. El parser implementa varias estrategias
de extracción (tabla principal, divs con data-attrs, scripts JSON
embebidos) y degrada a `status: gap` con razon clara si la pagina cambia
estructura — sin romper el orquestador.

NOTA: los selectores fueron diseñados a partir de la estructura
documentada de METAsrc al [2026-05-24]. Cuando el sitio cambie markup,
actualizar `_extract_*` funciones y agregar fixtures nuevos en
`tests/jungle_research/fixtures/`.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from typing import Any

from bs4 import BeautifulSoup

from .base import BaseAdapter

logger = logging.getLogger(__name__)

_TIERLIST_URL_TEMPLATE = "https://www.metasrc.com/lol/{region}/tier-list/jungle"
_DEFAULT_REGION = "na"

# Patron de % en strings tipo "52.3%" o "52.3" para WR/PR/BR.
_PCT_RE = re.compile(r"(\d{1,3}(?:\.\d+)?)\s*%?")

# Tiers METAsrc -> canónico (S+/A+/B-/etc.)
_TIER_NORMALIZE = {
    "S+": "S", "S": "S", "S-": "S",
    "A+": "A", "A": "A", "A-": "A",
    "B+": "B", "B": "B", "B-": "B",
    "C+": "C", "C": "C", "C-": "C",
    "D+": "D", "D": "D", "D-": "D",
    "GOD": "S", "GREAT": "A", "GOOD": "B", "OK": "C", "BAD": "D",
}


class MetaSrcAdapter(BaseAdapter):
    platform_name = "metasrc"
    min_delay = 3.0
    max_delay = 7.0

    def fetch_support_tier_list(self, patch: str = "latest", elo: str = "emerald_plus") -> dict:
        return self._fetch_role("support", patch=patch, elo=elo)

    def fetch_jungle_tier_list(self, patch: str = "latest", elo: str = "emerald_plus") -> dict:
        return self._fetch_role("jungle", patch=patch, elo=elo)

    def fetch_champion_detail(self, champion_id: str) -> dict:
        # No implementado en V3.7: METAsrc tier list es la prioridad. El
        # detalle por champion requiere navegar a /lol/{region}/champion/{name}.
        return {
            "platform": self.platform_name,
            "champion_id": champion_id,
            "status": "not_implemented",
            "reason": "fetch_champion_detail no implementado en V3.7 (solo tier list)",
            "scraped_at": _now_iso(),
        }

    def _fetch_role(self, role: str, *, patch: str, elo: str, region: str = _DEFAULT_REGION) -> dict:
        url = _TIERLIST_URL_TEMPLATE.format(region=region)
        # METAsrc actualmente solo expone tier list de jungle bajo este patrón.
        # Otros roles devuelven gap explícito.
        if role != "jungle":
            return _gap_response(
                role=role, patch=patch, elo=elo, source_url=url,
                reason=f"metasrc adapter solo soporta role=jungle en V3.7 (pedido: {role})",
            )
        try:
            response = self._safe_get(url)
            html = response.text
        except Exception as exc:  # noqa: BLE001
            logger.warning("[%s] fetch falló: %s", self.platform_name, exc)
            return _gap_response(
                role=role, patch=patch, elo=elo, source_url=url,
                reason=f"http_fetch_failed: {str(exc)[:160]}",
            )
        return parse_html(html, role=role, patch=patch, elo=elo, source_url=url)


def parse_html(
    html: str, *, role: str, patch: str, elo: str, source_url: str
) -> dict[str, Any]:
    """
    Parser robusto del HTML de METAsrc. Devuelve siempre un dict con
    `status` y `champions` (lista). Si no encuentra estructura, retorna
    `status: gap` con razón en `reason`.

    Estrategias en orden:
    1. Buscar `<script>` con JSON embebido (`window.__INITIAL_STATE__`,
       `__NEXT_DATA__`).
    2. Parsear tabla principal `<table>` con thead/tbody.
    3. Fallback: divs con data-champion="...".
    """
    soup = BeautifulSoup(html, "html.parser")

    # Estrategia 1: JSON embebido.
    champions = _extract_from_embedded_json(soup)
    if champions:
        return _ok_response(
            role=role, patch=patch, elo=elo, source_url=source_url,
            champions=champions, strategy="embedded_json",
        )

    # Estrategia 2: tabla principal.
    champions = _extract_from_table(soup)
    if champions:
        return _ok_response(
            role=role, patch=patch, elo=elo, source_url=source_url,
            champions=champions, strategy="table",
        )

    # Estrategia 3: data-champion attrs.
    champions = _extract_from_data_attrs(soup)
    if champions:
        return _ok_response(
            role=role, patch=patch, elo=elo, source_url=source_url,
            champions=champions, strategy="data_attrs",
        )

    return _gap_response(
        role=role, patch=patch, elo=elo, source_url=source_url,
        reason=(
            "no_structure_match: HTML no contiene tabla/json/data-attrs "
            "esperados. Revisar markup actual de METAsrc y actualizar selectores."
        ),
    )


def _extract_from_embedded_json(soup: BeautifulSoup) -> list[dict[str, Any]]:
    """Busca <script> con JSON tipo __NEXT_DATA__ y extrae champions."""
    for script in soup.find_all("script"):
        text = script.string or script.get_text("", strip=True) or ""
        if "__NEXT_DATA__" not in text and "champions" not in text.lower():
            continue
        # Intentar parsear el contenido del script como JSON.
        try:
            data = json.loads(text)
        except (ValueError, TypeError):
            continue
        candidates = _find_champions_in_json(data)
        if candidates:
            return candidates
    return []


def _find_champions_in_json(data: Any, depth: int = 0) -> list[dict[str, Any]]:
    """Búsqueda recursiva de listas que parecen tier list."""
    if depth > 6:
        return []
    if isinstance(data, list):
        # Lista donde cada item tiene 'name'/'champion' + 'win_rate'/'wr'.
        if data and isinstance(data[0], dict):
            sample = data[0]
            if any(k in sample for k in ("name", "champion", "champion_name")) and any(
                k in sample for k in ("win_rate", "wr", "winrate", "winRate")
            ):
                return [_normalize_champion_dict(item) for item in data]
        # Recursar dentro de cada item.
        for item in data:
            found = _find_champions_in_json(item, depth + 1)
            if found:
                return found
    elif isinstance(data, dict):
        for value in data.values():
            found = _find_champions_in_json(value, depth + 1)
            if found:
                return found
    return []


def _normalize_champion_dict(raw: dict[str, Any]) -> dict[str, Any]:
    name = raw.get("name") or raw.get("champion") or raw.get("champion_name") or ""
    return {
        "id": _id_from_name(name),
        "name": name,
        "win_rate": _to_float(raw.get("win_rate") or raw.get("wr") or raw.get("winrate") or raw.get("winRate")),
        "pick_rate": _to_float(raw.get("pick_rate") or raw.get("pr") or raw.get("pickrate") or raw.get("pickRate")),
        "ban_rate": _to_float(raw.get("ban_rate") or raw.get("br") or raw.get("banrate") or raw.get("banRate")),
        "games": _to_int(raw.get("games") or raw.get("games_analyzed") or raw.get("matches")),
        "tier": _normalize_tier(raw.get("tier")),
    }


def _extract_from_table(soup: BeautifulSoup) -> list[dict[str, Any]]:
    """Extrae filas de la tabla principal de tier list."""
    table = soup.find("table")
    if not table:
        return []

    # Detectar índices de columna desde headers.
    headers = []
    thead = table.find("thead")
    if thead:
        headers = [th.get_text(" ", strip=True).lower() for th in thead.find_all(["th", "td"])]

    col_map = _build_col_map(headers)
    tbody = table.find("tbody") or table
    rows = tbody.find_all("tr")

    champions: list[dict[str, Any]] = []
    for row in rows:
        cells = row.find_all(["td", "th"])
        if not cells:
            continue
        # Champion name: primera celda con texto largo + posible <img alt>.
        name = _extract_champion_name(cells)
        if not name:
            continue
        champion = {
            "id": _id_from_name(name),
            "name": name,
            "win_rate": _cell_pct(cells, col_map.get("win_rate")),
            "pick_rate": _cell_pct(cells, col_map.get("pick_rate")),
            "ban_rate": _cell_pct(cells, col_map.get("ban_rate")),
            "games": _cell_int(cells, col_map.get("games")),
            "tier": _cell_tier(cells, col_map.get("tier")),
        }
        champions.append(champion)
    return champions


def _build_col_map(headers: list[str]) -> dict[str, int]:
    """Mapea nombre semántico -> índice de columna desde headers."""
    mapping: dict[str, int] = {}
    for idx, header in enumerate(headers):
        if any(k in header for k in ("win rate", "winrate", "wr")):
            mapping.setdefault("win_rate", idx)
        elif any(k in header for k in ("pick rate", "pickrate", "pr")):
            mapping.setdefault("pick_rate", idx)
        elif any(k in header for k in ("ban rate", "banrate", "br")):
            mapping.setdefault("ban_rate", idx)
        elif any(k in header for k in ("games", "matches", "sample")):
            mapping.setdefault("games", idx)
        elif "tier" in header:
            # NOTE: "rank" NO va acá — "Rank" suele ser el número de orden
            # (1, 2, 3...) y se confunde con tier list (S, A, B). Si futuro
            # METAsrc usa "rank" con letras, agregar fixture específico.
            mapping.setdefault("tier", idx)
    return mapping


def _extract_champion_name(cells: list) -> str:
    """Extrae nombre de campeón de las primeras celdas (img alt o texto)."""
    for cell in cells[:3]:
        img = cell.find("img")
        if img and img.get("alt"):
            alt = img["alt"].strip()
            if alt and len(alt) < 30 and not alt.lower().startswith("rank"):
                return alt
        text = cell.get_text(" ", strip=True)
        # Heurística: nombre champion suele ser 3-25 chars sin números puros.
        if text and 3 <= len(text) <= 25 and not text.replace(".", "").isdigit():
            return text
    return ""


def _extract_from_data_attrs(soup: BeautifulSoup) -> list[dict[str, Any]]:
    """Fallback: divs/rows con data-champion="...", data-wr="..."."""
    champions: list[dict[str, Any]] = []
    for node in soup.find_all(attrs={"data-champion": True}):
        name = node.get("data-champion") or ""
        if not name:
            continue
        champions.append({
            "id": _id_from_name(name),
            "name": name,
            "win_rate": _to_float(node.get("data-wr") or node.get("data-win-rate")),
            "pick_rate": _to_float(node.get("data-pr") or node.get("data-pick-rate")),
            "ban_rate": _to_float(node.get("data-br") or node.get("data-ban-rate")),
            "games": _to_int(node.get("data-games") or node.get("data-matches")),
            "tier": _normalize_tier(node.get("data-tier")),
        })
    return champions


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _id_from_name(name: str) -> str:
    """Canonicaliza nombre a ID Data Dragon (sin espacios/puntuación)."""
    return name.replace(" ", "").replace("'", "").replace(".", "")


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        match = _PCT_RE.search(value)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
    return None


def _to_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        cleaned = re.sub(r"[^\d]", "", value)
        if cleaned:
            try:
                return int(cleaned)
            except ValueError:
                return None
    return None


def _normalize_tier(value: Any) -> str | None:
    if value is None:
        return None
    raw = str(value).strip().upper()
    return _TIER_NORMALIZE.get(raw, raw[:1] if raw and raw[0] in "SABCD" else None)


def _cell_pct(cells: list, idx: int | None) -> float | None:
    if idx is None or idx >= len(cells):
        return None
    return _to_float(cells[idx].get_text(" ", strip=True))


def _cell_int(cells: list, idx: int | None) -> int | None:
    if idx is None or idx >= len(cells):
        return None
    return _to_int(cells[idx].get_text(" ", strip=True))


def _cell_tier(cells: list, idx: int | None) -> str | None:
    if idx is None or idx >= len(cells):
        return None
    return _normalize_tier(cells[idx].get_text(" ", strip=True))


def _ok_response(
    *, role: str, patch: str, elo: str, source_url: str,
    champions: list[dict[str, Any]], strategy: str,
) -> dict[str, Any]:
    return {
        "platform": "metasrc",
        "source_url": source_url,
        "role": role,
        "patch": patch,
        "elo": elo,
        "status": "ok",
        "strategy": strategy,
        "champions": champions,
        "champion_count": len(champions),
        "scraped_at": _now_iso(),
    }


def _gap_response(
    *, role: str, patch: str, elo: str, source_url: str, reason: str,
) -> dict[str, Any]:
    return {
        "platform": "metasrc",
        "source_url": source_url,
        "role": role,
        "patch": patch,
        "elo": elo,
        "status": "gap",
        "reason": reason,
        "champions": [],
        "champion_count": 0,
        "scraped_at": _now_iso(),
    }
