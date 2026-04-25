import time
from typing import Any, Dict, List, Optional

import requests


class RiotAPIError(Exception):
    """Error de alto nivel para fallos del cliente Riot/Data Dragon."""


class RiotClient:
    def __init__(self, api_key: str, platform: str, regional: str, timeout: int = 10):
        self.api_key = api_key
        self.platform = platform.lower()
        self.regional = regional.lower()
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"X-Riot-Token": self.api_key})
        self.platform_base = f"https://{self.platform}.api.riotgames.com"
        self.regional_base = f"https://{self.regional}.api.riotgames.com"

    def _request_json(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
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

    def get_summoner_by_name(self, summoner_name: str) -> Dict[str, Any]:
        url = f"{self.platform_base}/lol/summoner/v4/summoners/by-name/{requests.utils.quote(summoner_name)}"
        return self._request_json("GET", url)

    def get_summoner_by_puuid(self, puuid: str) -> Dict[str, Any]:
        url = f"{self.platform_base}/lol/summoner/v4/summoners/by-puuid/{requests.utils.quote(puuid)}"
        return self._request_json("GET", url)

    def get_account_by_riot_id(self, game_name: str, tag_line: str) -> Dict[str, Any]:
        url = (
            f"{self.regional_base}/riot/account/v1/accounts/by-riot-id/"
            f"{requests.utils.quote(game_name)}/{requests.utils.quote(tag_line)}"
        )
        return self._request_json("GET", url)

    def get_match_ids_by_puuid(
        self,
        puuid: str,
        start: int = 0,
        count: int = 10,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> List[str]:
        url = f"{self.regional_base}/lol/match/v5/matches/by-puuid/{puuid}/ids"
        params: Dict[str, Any] = {"start": start, "count": count}
        if start_time is not None:
            params["startTime"] = int(start_time)
        if end_time is not None:
            params["endTime"] = int(end_time)

        data = self._request_json("GET", url, params=params)
        if not isinstance(data, list):
            raise RiotAPIError("Respuesta inesperada al listar ids de partidas")
        return data

    def get_match(self, match_id: str) -> Dict[str, Any]:
        url = f"{self.regional_base}/lol/match/v5/matches/{match_id}"
        return self._request_json("GET", url)

    def get_ddragon_versions(self) -> List[str]:
        data = self._request_json("GET", "https://ddragon.leagueoflegends.com/api/versions.json", retries=1)
        if not isinstance(data, list) or not data:
            raise RiotAPIError("Respuesta inesperada de Data Dragon versions")
        return data

    def get_ddragon_summoner_spells(self, version: str) -> Dict[str, Any]:
        url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/summoner.json"
        data = self._request_json("GET", url, retries=1)
        if not isinstance(data, dict):
            raise RiotAPIError("Respuesta inesperada de summoner.json")
        return data

    def get_ddragon_runes(self, version: str) -> List[Dict[str, Any]]:
        url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/runesReforged.json"
        data = self._request_json("GET", url, retries=1)
        if not isinstance(data, list):
            raise RiotAPIError("Respuesta inesperada de runesReforged.json")
        return data

    def get_queues(self) -> List[Dict[str, Any]]:
        data = self._request_json("GET", "https://static.developer.riotgames.com/docs/lol/queues.json", retries=1)
        if not isinstance(data, list):
            raise RiotAPIError("Respuesta inesperada de queues.json")
        return data
