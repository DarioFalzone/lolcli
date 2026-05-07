"""
Clase base abstracta para todos los adaptadores de scraping.

Cada plataforma (LoLalytics, OP.GG, etc.) implementa esta interfaz.
El orquestador llama a estos métodos de forma uniforme.
"""

import logging
import random
import time
from abc import ABC, abstractmethod
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# User-Agent pool para rotación — evita fingerprinting trivial.
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
]


class BaseAdapter(ABC):
    """
    Interfaz abstracta para adaptadores de scraping.

    Cada adaptador implementa la extracción de datos de su plataforma
    y devuelve diccionarios con el schema crudo de esa plataforma.
    El normalizer se encarga de unificar los schemas después.
    """

    platform_name: str = "unknown"

    # Rate-limiting: delay entre requests (segundos).
    min_delay: float = 3.0
    max_delay: float = 7.0

    def __init__(self) -> None:
        self._client: httpx.Client | None = None

    def _get_client(self) -> httpx.Client:
        """Crea o reutiliza un cliente HTTP con headers humanizados."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.Client(
                headers=self._build_headers(),
                timeout=30.0,
                follow_redirects=True,
            )
        return self._client

    def _build_headers(self) -> dict[str, str]:
        """Headers que simulan un browser real."""
        return {
            "User-Agent": random.choice(_USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }

    def _humanized_delay(self) -> None:
        """Pausa humanizada con jitter gaussiano entre requests."""
        base = random.uniform(self.min_delay, self.max_delay)
        jitter = random.gauss(0, 0.5)
        delay = max(1.0, base + jitter)
        logger.debug("[%s] Delay humanizado: %.1fs", self.platform_name, delay)
        time.sleep(delay)

    def _safe_get(self, url: str, **kwargs: Any) -> httpx.Response:
        """
        GET con rate-limiting, retry y logging.

        Hace hasta 3 intentos con backoff exponencial.
        """
        client = self._get_client()
        max_retries = 3

        for attempt in range(1, max_retries + 1):
            try:
                if attempt > 1:
                    self._humanized_delay()

                response = client.get(url, **kwargs)

                if response.status_code == 429:
                    wait = 30 * attempt
                    logger.warning(
                        "[%s] Rate limited (429). Esperando %ds...",
                        self.platform_name,
                        wait,
                    )
                    time.sleep(wait)
                    continue

                if response.status_code == 403:
                    logger.error(
                        "[%s] Bloqueado (403) en %s. Posible anti-bot.",
                        self.platform_name,
                        url,
                    )
                    raise PermissionError(f"[{self.platform_name}] Acceso denegado (403) a {url}")

                response.raise_for_status()
                return response

            except httpx.HTTPStatusError as e:
                logger.warning(
                    "[%s] HTTP %d en intento %d/%d: %s",
                    self.platform_name,
                    e.response.status_code,
                    attempt,
                    max_retries,
                    url,
                )
                if attempt == max_retries:
                    raise
            except httpx.RequestError as e:
                logger.warning(
                    "[%s] Error de red en intento %d/%d: %s",
                    self.platform_name,
                    attempt,
                    max_retries,
                    e,
                )
                if attempt == max_retries:
                    raise
                time.sleep(5 * attempt)

        raise RuntimeError(f"[{self.platform_name}] Agotados {max_retries} intentos para {url}")

    def close(self) -> None:
        """Cierra el cliente HTTP."""
        if self._client and not self._client.is_closed:
            self._client.close()
            self._client = None

    # --- Métodos abstractos que cada plataforma implementa ---

    @abstractmethod
    def fetch_support_tier_list(self, patch: str = "latest", elo: str = "emerald_plus") -> dict:
        """
        Extrae la tier list de soportes.

        Returns:
            dict con keys: champions (list), patch, elo, scraped_at
        """
        ...

    def fetch_adc_tier_list(self, patch: str = "latest", elo: str = "emerald_plus") -> dict:
        """
        Extrae la tier list de ADC/bot lane.

        Los adapters existentes pueden sobreescribirlo. Por defecto falla de
        forma explicita para que el orquestador reporte la plataforma.
        """
        raise NotImplementedError(f"[{self.platform_name}] fetch_adc_tier_list no implementado")

    @abstractmethod
    def fetch_champion_detail(self, champion_id: str) -> dict:
        """
        Extrae el detalle de un soporte: builds, runas, matchups.

        Returns:
            dict con keys: champion_id, builds, runes, matchups, synergies
        """
        ...
