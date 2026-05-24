"""Base abstracta para adaptadores de patch notes.

Reusa la filosofía de `meta_scraper/adapters/base.py` (rate limit humanizado,
user-agent pool, retries con backoff) pero la interfaz es diferente: en lugar
de `fetch_*_tier_list()`, los adapters de patch notes exponen `discover()` y
`extract()`.
"""

from __future__ import annotations

import logging
import random
import time
from abc import ABC, abstractmethod

import httpx

logger = logging.getLogger(__name__)

# Pool de user agents — mismo set que meta_scraper para consistencia.
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
]


class PatchNotesAdapterBase(ABC):
    """Interface para adaptadores de patch notes.

    Implementaciones concretas:
    - `discover(locale)` → lista de URLs canónicas de patch notes.
    - `extract(url, locale)` → dict listo para validar contra `PatchNote`.
    """

    platform_name: str = "unknown"
    min_delay: float = 3.0
    max_delay: float = 7.0

    def __init__(self) -> None:
        self._client: httpx.Client | None = None

    def _get_client(self) -> httpx.Client:
        if self._client is None or self._client.is_closed:
            self._client = httpx.Client(
                headers=self._build_headers(),
                timeout=30.0,
                follow_redirects=True,
            )
        return self._client

    def _build_headers(self) -> dict[str, str]:
        return {
            "User-Agent": random.choice(_USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
        }

    def _humanized_delay(self) -> None:
        base = random.uniform(self.min_delay, self.max_delay)
        jitter = random.gauss(0, 0.5)
        delay = max(1.0, base + jitter)
        logger.debug("[%s] Delay humanizado: %.1fs", self.platform_name, delay)
        time.sleep(delay)

    def _safe_get(self, url: str, max_retries: int = 3) -> httpx.Response | None:
        """GET con retries y backoff. None si todos los intentos fallan."""
        client = self._get_client()
        for attempt in range(1, max_retries + 1):
            try:
                if attempt > 1:
                    self._humanized_delay()
                resp = client.get(url)
                if resp.status_code == 429:
                    wait = 30 * attempt
                    logger.warning("[%s] 429, espero %ds...", self.platform_name, wait)
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                return resp
            except httpx.HTTPError as e:
                logger.warning("[%s] intento %d/%d falló: %s", self.platform_name, attempt, max_retries, e)
                if attempt == max_retries:
                    return None
                time.sleep(5 * attempt)
        return None

    def close(self) -> None:
        if self._client and not self._client.is_closed:
            self._client.close()
            self._client = None

    # --- Métodos abstractos ---

    @abstractmethod
    def discover(self, locale: str, max_patches: int = 10) -> list[str]:
        """Devuelve URLs canónicas de patch notes para el locale dado.

        Args:
            locale: ej. "es-es", "es-mx", "en-us".
            max_patches: tope superior de URLs a devolver (las más recientes).
        """
        ...

    @abstractmethod
    def extract(self, url: str, locale: str) -> dict:
        """Descarga un patch note y devuelve dict que `PatchNote` puede validar.

        Returns:
            Dict con keys: title, patch_version, canonical_url, published_at,
            sections, assets, summary, source_locale.
        """
        ...
