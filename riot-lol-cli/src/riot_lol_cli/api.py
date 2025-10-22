import time
from typing import Any, Dict, List, Optional

import requests


class RiotAPIError(Exception):
    pass


class RiotClient:
    def __init__(self, api_key: str, platform: str, regional: str, timeout: int = 10):
        self.api_key = api_key
        self.platform = platform.lower()
        self.regional = regional.lower()
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "X-Riot-Token": self.api_key,
        })
        self.platform_base = f"https://{self.platform}.api.riotgames.com"
        self.regional_base = f"https://{self.regional}.api.riotgames.com"

    def _request(self, method: str, url: str, params: Optional[Dict[str, Any]] = None, retries: int = 3) -> Any:
        attempt = 0
        backoff = 1.0
        while True:
            resp = self.session.request(method, url, params=params, timeout=self.timeout)
            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                sleep_s = float(retry_after) if retry_after and retry_after.isdigit() else backoff
                time.sleep(sleep_s)
                attempt += 1
                backoff = min(backoff * 2, 10)
                if attempt > retries:
                    raise RiotAPIError("Rate limit excedido repetidamente (429)")
                continue
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code in (401, 403):
                detail = resp.text.strip()
                raise RiotAPIError(f"No autorizado (401/403). Detalle: {detail}")
            if resp.status_code == 404:
                raise RiotAPIError("Recurso no encontrado (404)")
            # Otros códigos
            raise RiotAPIError(f"Error de Riot API: {resp.status_code} - {resp.text}")

    # Summoner-V4
    def get_summoner_by_name(self, summoner_name: str) -> Dict[str, Any]:
        url = f"{self.platform_base}/lol/summoner/v4/summoners/by-name/{requests.utils.quote(summoner_name)}"
        return self._request("GET", url)

    def get_summoner_by_puuid(self, puuid: str) -> Dict[str, Any]:
        url = f"{self.platform_base}/lol/summoner/v4/summoners/by-puuid/{requests.utils.quote(puuid)}"
        return self._request("GET", url)

    # Account-V1 (por Riot ID)
    def get_account_by_riot_id(self, game_name: str, tag_line: str) -> Dict[str, Any]:
        url = (
            f"{self.regional_base}/riot/account/v1/accounts/by-riot-id/"
            f"{requests.utils.quote(game_name)}/{requests.utils.quote(tag_line)}"
        )
        return self._request("GET", url)

    # Match-V5
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
        data = self._request("GET", url, params=params)
        if not isinstance(data, list):
            raise RiotAPIError("Respuesta inesperada al listar ids de partidas")
        return data

    def get_match(self, match_id: str) -> Dict[str, Any]:
        url = f"{self.regional_base}/lol/match/v5/matches/{match_id}"
        return self._request("GET", url)

    # Data Dragon
    def get_ddragon_versions(self) -> List[str]:
        url = "https://ddragon.leagueoflegends.com/api/versions.json"
        resp = requests.get(url, timeout=self.timeout)
        if resp.status_code != 200:
            raise RiotAPIError(f"No se pudieron obtener versiones de Data Dragon: {resp.status_code}")
        data = resp.json()
        if not isinstance(data, list) or not data:
            raise RiotAPIError("Respuesta inesperada de Data Dragon versions")
        return data
