"""
Riot bridge — wrapper sobre `api.RiotClient` para Jungle Research.

Reusa el cliente sync existente y agrega:

- Auto-detección de `RIOT_API_KEY`; si falta, devuelve gap controlado.
- Mapeo `server` → `(platform, regional)` para los servidores de los pros.
- Resolución batch de Riot IDs: solo intenta los que tienen `riot_id` en seed.
- Cero scraping. Solo Riot API oficial.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Iterable
from dataclasses import dataclass

from riot_lol_cli.api import RiotAPIError, RiotClient

logger = logging.getLogger(__name__)


# Mapeo canónico server → (platform_v4, regional_v5).
# Fuente: https://developer.riotgames.com/docs/lol#routing-values
SERVER_ROUTING: dict[str, tuple[str, str]] = {
    "KR": ("kr", "asia"),
    "JP": ("jp1", "asia"),
    "CN": ("kr", "asia"),  # Tencent no expone por dev API; usamos KR como proxy de routing
    "EUW": ("euw1", "europe"),
    "EUNE": ("eun1", "europe"),
    "TR": ("tr1", "europe"),
    "RU": ("ru", "europe"),
    "NA": ("na1", "americas"),
    "BR": ("br1", "americas"),
    "LAN": ("la1", "americas"),
    "LAS": ("la2", "americas"),
    "OCE": ("oc1", "sea"),
    "VN": ("vn2", "sea"),
    "TW": ("tw2", "sea"),
}


@dataclass(frozen=True)
class ResolutionResult:
    """Resultado de un intento de resolución de Riot ID → PUUID."""

    riot_id_game_name: str
    riot_id_tagline: str
    server: str
    puuid: str | None = None
    summoner_id: str | None = None
    error: str | None = None
    gap_flag: str | None = None


class RiotBridge:
    """Wrapper sobre RiotClient con manejo explícito de gaps."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("RIOT_API_KEY")
        self._clients: dict[tuple[str, str], RiotClient] = {}

    def has_key(self) -> bool:
        return bool(self.api_key)

    def _client_for(self, server: str) -> RiotClient | None:
        if not self.api_key:
            return None
        routing = SERVER_ROUTING.get(server.upper())
        if not routing:
            return None
        if routing not in self._clients:
            self._clients[routing] = RiotClient(
                api_key=self.api_key, platform=routing[0], regional=routing[1]
            )
        return self._clients[routing]

    def resolve_riot_id(
        self, game_name: str, tagline: str, server: str
    ) -> ResolutionResult:
        """Resuelve Riot ID → PUUID. Devuelve gap si no hay key o falla."""
        if not self.api_key:
            return ResolutionResult(
                riot_id_game_name=game_name,
                riot_id_tagline=tagline,
                server=server,
                gap_flag="no_riot_key",
            )
        client = self._client_for(server)
        if not client:
            return ResolutionResult(
                riot_id_game_name=game_name,
                riot_id_tagline=tagline,
                server=server,
                gap_flag=f"unsupported_server:{server}",
            )
        try:
            account = client.get_account_by_riot_id(game_name, tagline)
        except RiotAPIError as exc:
            logger.warning("resolve_riot_id falló para %s#%s en %s: %s", game_name, tagline, server, exc)
            return ResolutionResult(
                riot_id_game_name=game_name,
                riot_id_tagline=tagline,
                server=server,
                error=str(exc),
                gap_flag="riot_api_error",
            )
        return ResolutionResult(
            riot_id_game_name=game_name,
            riot_id_tagline=tagline,
            server=server,
            puuid=account.get("puuid"),
        )

    def resolve_batch(
        self, requests: Iterable[tuple[str, str, str]]
    ) -> list[ResolutionResult]:
        """Resuelve múltiples Riot IDs; respeta orden, ningún paralelismo en V1."""
        return [self.resolve_riot_id(g, t, s) for g, t, s in requests]

    def fetch_recent_match_ids(
        self, puuid: str, server: str, count: int = 20
    ) -> list[str]:
        """Lista de match IDs recientes; respeta rate limit del cliente."""
        client = self._client_for(server)
        if not client:
            return []
        try:
            return client.get_match_ids_by_puuid(puuid, start=0, count=count)
        except RiotAPIError as exc:
            logger.warning("fetch_recent_match_ids falló para %s en %s: %s", puuid, server, exc)
            return []

    def fetch_match_detail(self, match_id: str, server: str) -> dict | None:
        """Detalle completo de una partida via match-v5."""
        client = self._client_for(server)
        if not client:
            return None
        try:
            return client.get_match(match_id)
        except RiotAPIError as exc:
            logger.warning("fetch_match_detail falló para %s en %s: %s", match_id, server, exc)
            return None
