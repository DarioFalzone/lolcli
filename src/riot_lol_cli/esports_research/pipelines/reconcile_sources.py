"""Cross-source reconciliation for silver records."""

from __future__ import annotations

from typing import Any

SOURCE_PRIORITY = {
    "leaguepedia": 0,
    "oracles_elixir": 1,
    "gol_gg": 2,
    "data_dragon": 3,
}


def reconcile_records(records: list[dict[str, Any]], id_field: str) -> dict[str, Any]:
    chosen: dict[str, dict[str, Any]] = {}
    divergences: list[dict[str, Any]] = []
    for row in records:
        record_id = row.get(id_field)
        if not record_id:
            divergences.append({"reason": "missing_id", "id_field": id_field, "record": row})
            continue
        existing = chosen.get(str(record_id))
        if existing is None:
            chosen[str(record_id)] = row
            continue
        old_priority = SOURCE_PRIORITY.get(existing.get("source_origin"), 99)
        new_priority = SOURCE_PRIORITY.get(row.get("source_origin"), 99)
        if new_priority < old_priority:
            divergences.append({"record_id": record_id, "kept": row.get("source_origin"), "replaced": existing.get("source_origin")})
            chosen[str(record_id)] = row
        elif row != existing:
            divergences.append({"record_id": record_id, "kept": existing.get("source_origin"), "discarded": row.get("source_origin")})
    return {"records": list(chosen.values()), "divergences": divergences}
