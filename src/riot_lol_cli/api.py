"""
Riot API client — síncrono (requests) y asíncrono (httpx).

Ambas variantes comparten la lógica de backoff exponencial y manejo de
errores de red, 429, 401/403 y 404.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any
from urllib.parse import quote

import requests

logger = logging.getLogger(__name__)


class RiotAPIError(Exception):
    """Error de alto nivel para fallos del cliente Riot/Data Dragon."""


# ---------------------------------------------------------------------------
# Sync client (usado por CLI, scripts y collectors existentes)
# ---------------------------------------------------------------------------


class RiotClient:
    """Cliente síncrono para Riot API y Data Dragon."""

    def __init__(self, api_key: str, platform: str, regional: str, timeout: int = 10):
        self.api_key = api_key
        self.platform = platform.lower()
        self.regional = regional.lower()
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"X-Riot-Token": self.api_key})
        self.platform_base = f"https://{self.platform}.api.riotgames.com"
        self.regional_base = f"https://{self.regional}.api.riotgames.com"

    # -- Transporte -----------------------------------------------------------

    def _request_json(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        retries: int = 3,
    ) -> Any:
        attempt = 0
        backoff = 1.0

        while True:
            try:
                response = self.session.request(method, url, params=params, timeout=self.timeout)
            except requests.RequestException as exc:
                raise RiotAPIError(f"Error de red consultando '{url}': {exc}") from exc

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                try:
                    sleep_seconds = float(retry_after) if retry_after else backoff
                except ValueError:
                    sleep_seconds = backoff

                logger.warning("Rate-limited (429). Reintentando en %.1fs…", sleep_seconds)
                time.sleep(sleep_seconds)
                attempt += 1
                backoff = min(backoff * 2, 10)
                if attempt > retries:
                    raise RiotAPIError("Rate limit excedido repetidamente (429)")
                continue

            if response.status_code == 200:
                try:
                    return response.json()
                except ValueError as exc:
                    raise RiotAPIError(f"Respuesta JSON inválida para '{url}'") from exc

            if response.status_code in (401, 403):
                detail = response.text.strip()
                raise RiotAPIError(f"No autorizado (401/403). Detalle: {detail}")

            if response.status_code == 404:
                raise RiotAPIError("Recurso no encontrado (404)")

            raise RiotAPIError(f"Error de Riot API: {response.status_code} - {response.text}")

    # -- Summoner / Account ---------------------------------------------------

    def get_summoner_by_name(self, summoner_name: str) -> dict[str, Any]:
        url = f"{self.platform_base}/lol/summoner/v4/summoners/by-name/{quote(summoner_name)}"
        return self._request_json("GET", url)

    def get_summoner_by_puuid(self, puuid: str) -> dict[str, Any]:
        url = f"{self.platform_base}/lol/summoner/v4/summoners/by-puuid/{quote(puuid)}"
        return self._request_json("GET", url)

    def get_account_by_riot_id(self, game_name: str, tag_line: str) -> dict[str, Any]:
        url = f"{self.regional_base}/riot/account/v1/accounts/by-riot-id/{quote(game_name)}/{quote(tag_line)}"
        return self._request_json("GET", url)

    # -- Match ----------------------------------------------------------------

    def get_match_ids_by_puuid(
        self,
        puuid: str,
        start: int = 0,
        count: int = 10,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[str]:
        url = f"{self.regional_base}/lol/match/v5/matches/by-puuid/{puuid}/ids"
        params: dict[str, Any] = {"start": start, "count": count}
        if start_time is not None:
            params["startTime"] = int(start_time)
        if end_time is not None:
            params["endTime"] = int(end_time)

        data = self._request_json("GET", url, params=params)
        if not isinstance(data, list):
            raise RiotAPIError("Respuesta inesperada al listar ids de partidas")
        return data

    def get_match(self, match_id: str) -> dict[str, Any]:
        url = f"{self.regional_base}/lol/match/v5/matches/{match_id}"
        return self._request_json("GET", url)

    # -- Data Dragon ----------------------------------------------------------

    def get_ddragon_versions(self) -> list[str]:
        data = self._request_json("GET", "https://ddragon.leagueoflegends.com/api/versions.json", retries=1)
        if not isinstance(data, list) or not data:
            raise RiotAPIError("Respuesta inesperada de Data Dragon versions")
        return data

    def get_ddragon_summoner_spells(self, version: str) -> dict[str, Any]:
        url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/summoner.json"
        data = self._request_json("GET", url, retries=1)
        if not isinstance(data, dict):
            raise RiotAPIError("Respuesta inesperada de summoner.json")
        return data

    def get_ddragon_runes(self, version: str) -> list[dict[str, Any]]:
        url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/runesReforged.json"
        data = self._request_json("GET", url, retries=1)
        if not isinstance(data, list):
            raise RiotAPIError("Respuesta inesperada de runesReforged.json")
        return data

    def get_queues(self) -> list[dict[str, Any]]:
        data = self._request_json("GET", "https://static.developer.riotgames.com/docs/lol/queues.json", retries=1)
        if not isinstance(data, list):
            raise RiotAPIError("Respuesta inesperada de queues.json")
        return data


# ---------------------------------------------------------------------------
# Async client (para batch collection, API server, etc.)
# ---------------------------------------------------------------------------


class AsyncRiotClient:
    """Cliente asíncrono para Riot API con httpx y backoff exponencial."""

    def __init__(
        self,
        api_key: str,
        platform: str,
        regional: str,
        timeout: float = 10.0,
    ):
        import httpx  # lazy import — no falla si httpx no está instalado en CLI-only env

        self.api_key = api_key
        self.platform = platform.lower()
        self.regional = regional.lower()
        self.platform_base = f"https://{self.platform}.api.riotgames.com"
        self.regional_base = f"https://{self.regional}.api.riotgames.com"
        self._client = httpx.AsyncClient(
            headers={"X-Riot-Token": self.api_key},
            timeout=httpx.Timeout(timeout),
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> AsyncRiotClient:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    # -- Transporte -----------------------------------------------------------

    async def _request_json(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        retries: int = 3,
    ) -> Any:
        import httpx

        attempt = 0
        backoff = 1.0

        while True:
            try:
                response = await self._client.request(method, url, params=params)
            except httpx.HTTPError as exc:
                raise RiotAPIError(f"Error de red consultando '{url}': {exc}") from exc

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                try:
                    sleep_seconds = float(retry_after) if retry_after else backoff
                except ValueError:
                    sleep_seconds = backoff

                logger.warning("Rate-limited (429). Reintentando en %.1fs…", sleep_seconds)
                await asyncio.sleep(sleep_seconds)
                attempt += 1
                backoff = min(backoff * 2, 10)
                if attempt > retries:
                    raise RiotAPIError("Rate limit excedido repetidamente (429)")
                continue

            if response.status_code == 200:
                try:
                    return response.json()
                except ValueError as exc:
                    raise RiotAPIError(f"Respuesta JSON inválida para '{url}'") from exc

            if response.status_code in (401, 403):
                detail = response.text.strip()
                raise RiotAPIError(f"No autorizado (401/403). Detalle: {detail}")

            if response.status_code == 404:
                raise RiotAPIError("Recurso no encontrado (404)")

            raise RiotAPIError(f"Error de Riot API: {response.status_code} - {response.text}")

    # -- Summoner / Account ---------------------------------------------------

    async def get_account_by_riot_id(self, game_name: str, tag_line: str) -> dict[str, Any]:
        url = f"{self.regional_base}/riot/account/v1/accounts/by-riot-id/{quote(game_name)}/{quote(tag_line)}"
        return await self._request_json("GET", url)

    # -- Match ----------------------------------------------------------------

    async def get_match_ids_by_puuid(
        self,
        puuid: str,
        start: int = 0,
        count: int = 10,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[str]:
        url = f"{self.regional_base}/lol/match/v5/matches/by-puuid/{puuid}/ids"
        params: dict[str, Any] = {"start": start, "count": count}
        if start_time is not None:
            params["startTime"] = int(start_time)
        if end_time is not None:
            params["endTime"] = int(end_time)

        data = await self._request_json("GET", url, params=params)
        if not isinstance(data, list):
            raise RiotAPIError("Respuesta inesperada al listar ids de partidas")
        return data

    async def get_match(self, match_id: str) -> dict[str, Any]:
        url = f"{self.regional_base}/lol/match/v5/matches/{match_id}"
        return await self._request_json("GET", url)

    # -- Data Dragon ----------------------------------------------------------

    async def get_ddragon_versions(self) -> list[str]:
        data = await self._request_json("GET", "https://ddragon.leagueoflegends.com/api/versions.json", retries=1)
        if not isinstance(data, list) or not data:
            raise RiotAPIError("Respuesta inesperada de Data Dragon versions")
        return data
