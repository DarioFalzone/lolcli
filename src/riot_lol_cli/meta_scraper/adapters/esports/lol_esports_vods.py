"""LoL Esports VOD metadata stub.

Compliance: this adapter never downloads or rehosts video bytes. It only
models metadata references that point back to the official platform.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from riot_lol_cli.meta_scraper.adapters.esports.base_esports import BaseEsportsAdapter


class VodMetadata(BaseModel):
    game_id: str
    video_url: str
    platform: str
    timestamp_start: int | None = None
    duration_seconds: int | None = None
    thumbnail_url: str | None = None
    language: str | None = None


class LolEsportsVodsAdapter(BaseEsportsAdapter):
    platform_name = "lol_esports_vods"
    source_id = "lol_esports_vods"

    def fetch_vod_metadata(self, game_id: str) -> dict[str, Any]:
        return {
            "source": self.source_id,
            "status": "not_implemented",
            "game_id": game_id,
            "metadata": None,
            "allowed_fields": list(VodMetadata.model_fields),
            "gaps": ["official site selector validation required; video download is prohibited"],
        }

    def normalize_metadata(self, payload: dict[str, Any]) -> dict[str, Any]:
        return VodMetadata.model_validate(payload).model_dump(mode="json")
