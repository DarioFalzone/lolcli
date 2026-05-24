"""Data quality report helpers."""

from __future__ import annotations

from typing import Any

from riot_lol_cli.esports_research.schemas import utcnow_iso


def build_quality_log(divergences: list[dict[str, Any]] | None = None, gaps: list[str] | None = None) -> dict[str, Any]:
    return {
        "generated_at": utcnow_iso(),
        "divergences": divergences or [],
        "gaps": gaps or [],
        "divergence_count": len(divergences or []),
        "gap_count": len(gaps or []),
    }
