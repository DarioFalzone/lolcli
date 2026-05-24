"""Adapter Data Dragon — versiones técnicas del CDN de Riot.

NO requiere Playwright. Single GET a `https://ddragon.leagueoflegends.com/api/versions.json`.
Devuelve un snapshot global con la lista de versiones y un mapping de patch_label → ddragon_version.

Ejemplo:
  patch 26.10 (gameplay) → DDragon 26.10.1 (puede tener sufijos .1, .2, etc.)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import httpx

from .base import PatchNotesAdapterBase

logger = logging.getLogger(__name__)

_VERSIONS_URL = "https://ddragon.leagueoflegends.com/api/versions.json"
_REALMS_URL = "https://ddragon.leagueoflegends.com/realms/na.json"


class DDragonAdapter(PatchNotesAdapterBase):
    """Adapter de Data Dragon. Sin Playwright; solo GET JSON."""

    platform_name = "ddragon"
    min_delay = 0.5
    max_delay = 1.5

    def discover(self, locale: str, max_patches: int = 10) -> list[str]:
        """DDragon no tiene URLs por parche — devuelve [_VERSIONS_URL] como pseudo-URL."""
        return [_VERSIONS_URL]

    def extract(self, url: str, locale: str) -> dict[str, Any]:
        """GET versions.json + realms para construir el snapshot global."""
        versions: list[str] = []
        realms: dict[str, Any] = {}

        try:
            resp = self._get_client().get(_VERSIONS_URL, timeout=15.0)
            resp.raise_for_status()
            versions = resp.json()
            if not isinstance(versions, list):
                versions = []
        except (httpx.HTTPError, ValueError) as e:
            logger.warning("[ddragon] versions.json falló: %s", e)
            raise

        try:
            realms_resp = self._get_client().get(_REALMS_URL, timeout=15.0)
            realms_resp.raise_for_status()
            realms = realms_resp.json() if isinstance(realms_resp.json(), dict) else {}
        except (httpx.HTTPError, ValueError) as e:
            logger.warning("[ddragon] realms/na.json falló: %s (no bloquea)", e)

        # Mapping patch_label → versions DDragon. patch_label = "MAJOR.MINOR" sin sufijo.
        # DDragon además tiene entradas raras tipo "lolpatch_7" — las saltamos.
        by_patch: dict[str, list[str]] = {}
        for version in versions:
            parts = version.split(".")
            if len(parts) < 2:
                continue
            try:
                label = f"{int(parts[0])}.{int(parts[1])}"
            except ValueError:
                # Versión legacy (ej. "lolpatch_7", "lolpatch_3.10") — skip
                continue
            by_patch.setdefault(label, []).append(version)

        return {
            "versions": versions[:50],  # cap para no saturar el JSON
            "latest": versions[0] if versions else None,
            "realms": realms,
            "by_patch_label": by_patch,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
