"""
Módulo Gaps Registry Core — riot_lol_cli.

Centraliza el registro y persistencia de brechas técnicas de datos (gaps)
de todos los subsistemas en un único archivo JSON global consolidado.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from riot_lol_cli import paths

GAPS_FILE = paths.DATA_DIR / "global_gaps.json"


def read_global_gaps() -> list[dict[str, Any]]:
    """Lee el JSON global de gaps. Devuelve [] si no existe o está corrupto."""
    if not GAPS_FILE.exists():
        return []
    try:
        with GAPS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _write_atomic(gaps: list[dict[str, Any]]) -> None:
    """Escribe los gaps al JSON global de forma atómica y en UTF-8 sin BOM."""
    GAPS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = GAPS_FILE.with_suffix(GAPS_FILE.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(gaps, f, ensure_ascii=False, indent=2, sort_keys=False)
        f.write("\n")
    tmp.replace(GAPS_FILE)


def register_gap(
    source: str,
    gap_id: str,
    description: str,
    severity: str = "warning",
    action_required: str | None = None,
) -> None:
    """
    Registra o actualiza un gap en el JSON global.

    Si ya existía un gap con el mismo (source, gap_id), lo sobreescribe
    preservando el resto y actualizando el timestamp.
    """
    gaps = read_global_gaps()
    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    existing_idx = -1
    for i, g in enumerate(gaps):
        if g.get("source") == source and g.get("gap_id") == gap_id:
            existing_idx = i
            break

    payload = {
        "source": source,
        "gap_id": gap_id,
        "description": description,
        "severity": severity,
        "detected_at": now_iso,
        "action_required": action_required,
    }

    if existing_idx != -1:
        gaps[existing_idx] = payload
    else:
        gaps.append(payload)

    _write_atomic(gaps)


def clear_gap(source: str, gap_id: str) -> None:
    """Remueve un gap específico de un source del JSON global."""
    gaps = read_global_gaps()
    filtered = [g for g in gaps if not (g.get("source") == source and g.get("gap_id") == gap_id)]
    if len(filtered) != len(gaps):
        _write_atomic(filtered)


def clear_source_gaps(source: str) -> None:
    """Remueve todos los gaps asociados a un source del JSON global."""
    gaps = read_global_gaps()
    filtered = [g for g in gaps if g.get("source") != source]
    if len(filtered) != len(gaps):
        _write_atomic(filtered)
