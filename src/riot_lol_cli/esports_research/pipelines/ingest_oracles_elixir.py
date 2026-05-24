"""Bronze ingest helpers for Oracle's Elixir CSV payloads."""

from __future__ import annotations

from typing import Any

from riot_lol_cli.esports_research import json_storage
from riot_lol_cli.meta_scraper.adapters.esports.oracles_elixir import OraclesElixirAdapter


def ingest_csv(year: int, filename: str, adapter: OraclesElixirAdapter | None = None) -> dict[str, Any]:
    client = adapter or OraclesElixirAdapter()
    payload = client.fetch_csv(year=year, filename=filename)
    target = json_storage.save_bronze_text(
        "oracles_elixir",
        str(year),
        filename.replace(".csv", ""),
        payload["csv_text"],
        ".csv",
    )
    return {"success": True, "source": "oracles_elixir", "raw_uri": str(target), "rows": payload["row_count"]}
