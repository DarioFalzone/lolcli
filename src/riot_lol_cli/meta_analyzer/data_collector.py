"""
Data Collector - Recolecta datos de partidas en tiempo real.

Usa los modelos Pydantic de riot_lol_cli.schemas.riot_api para parsear y
validar las respuestas de Match-V5, en vez de acceder a dicts crudos.
"""

import json
import logging
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from riot_lol_cli.api import RiotClient
from riot_lol_cli.schemas.riot_api import MatchDto, ProcessedMatch

logger = logging.getLogger(__name__)


class MetaDataCollector:
    """Recolecta datos de partidas para análisis de meta."""

    def __init__(self, api_key: str, platform: str = "la2", regional: str = "americas"):
        self.client = RiotClient(api_key, platform, regional)
        self.platform = platform
        self.regional = regional
        self.data_dir = Path(__file__).parent.parent.parent.parent / "data" / "meta"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def collect_matches_batch(
        self, summoners: list[str], count_per_summoner: int = 20
    ) -> list[dict[str, Any]]:
        """
        Recolecta partidas de múltiples jugadores.

        Args:
            summoners: Lista de "nombre#tag" en formato Riot ID
            count_per_summoner: Cantidad de matches por jugador

        Returns:
            Lista de matches procesados (dicts serializables).
        """
        matches_data: list[dict[str, Any]] = []

        for summoner in summoners:
            try:
                game_name, tag_line = summoner.split("#")
                account = self.client.get_account_by_riot_id(game_name, tag_line)
                puuid = account["puuid"]

                match_ids = self.client.get_match_ids_by_puuid(
                    puuid, start=0, count=count_per_summoner
                )

                for match_id in match_ids:
                    try:
                        raw = self.client.get_match(match_id)
                        processed = self._process_match(raw, match_id)
                        matches_data.append(processed)
                    except Exception:
                        logger.warning("Error procesando match %s", match_id, exc_info=True)
                        continue

                    time.sleep(0.05)  # Rate limiting

            except Exception:
                logger.warning("Error con jugador %s", summoner, exc_info=True)
                continue

        return matches_data

    @staticmethod
    def _process_match(raw: dict[str, Any], match_id: str) -> dict[str, Any]:
        """
        Parsea un dict crudo de Riot Match-V5 usando Pydantic
        y devuelve un dict procesado serializable.
        """
        match_dto = MatchDto.model_validate(raw)
        processed = ProcessedMatch.from_match_dto(match_dto, match_id)
        return processed.model_dump()

    def save_matches(
        self, matches: list[dict[str, Any]], timestamp: Optional[str] = None
    ) -> Path:
        """Guarda matches en archivo JSON con timestamp."""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

        filepath = self.data_dir / f"meta_data_{timestamp}.json"

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "collected_at": datetime.now().isoformat(),
                    "platform": self.platform,
                    "count": len(matches),
                    "matches": matches,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        logger.info("Guardados %d matches en %s", len(matches), filepath)
        return filepath

    def get_hourly_stats(self, matches: list[dict[str, Any]]) -> dict[str, Any]:
        """Genera estadísticas agregadas por hora."""

        stats = defaultdict(
            lambda: {
                "matches": 0,
                "wins": 0,
                "losses": 0,
                "total_damage": 0,
                "total_gold": 0,
                "total_vision": 0,
                "items_counter": defaultdict(int),
                "roles": defaultdict(lambda: {"matches": 0, "wins": 0}),
            }
        )

        total_matches = sum(len(m["champions"]) for m in matches)

        for match in matches:
            for champ in match["champions"]:
                champion_name = champ["champion_name"]
                role = champ["role"]

                stats[champion_name]["matches"] += 1
                if champ["result"]:
                    stats[champion_name]["wins"] += 1
                else:
                    stats[champion_name]["losses"] += 1

                champ_stats = champ["stats"]
                stats[champion_name]["total_damage"] += champ_stats["damage_champions"]
                stats[champion_name]["total_gold"] += champ_stats["gold"]
                stats[champion_name]["total_vision"] += champ_stats["vision"]

                for item_id in champ["items"]:
                    if item_id > 0:
                        stats[champion_name]["items_counter"][item_id] += 1

                stats[champion_name]["roles"][role]["matches"] += 1
                if champ["result"]:
                    stats[champion_name]["roles"][role]["wins"] += 1

        result: dict[str, Any] = {}
        for champion, data in stats.items():
            count = data["matches"]
            if count == 0:
                continue

            result[champion] = {
                "matches": count,
                "wins": data["wins"],
                "losses": data["losses"],
                "winrate": round((data["wins"] / count) * 100, 2),
                "pickrate": round((count / total_matches) * 100, 2),
                "avg_damage": round(data["total_damage"] / count),
                "avg_gold": round(data["total_gold"] / count),
                "avg_vision": round(data["total_vision"] / count, 1),
                "items_top3": [
                    item_id
                    for item_id, _ in sorted(
                        data["items_counter"].items(), key=lambda x: x[1], reverse=True
                    )[:3]
                ],
                "roles": {
                    role: {
                        "matches": role_data["matches"],
                        "wins": role_data["wins"],
                        "winrate": (
                            round((role_data["wins"] / role_data["matches"]) * 100, 2)
                            if role_data["matches"] > 0
                            else 0
                        ),
                    }
                    for role, role_data in data["roles"].items()
                    if role_data["matches"] > 0
                },
            }

        return result


if __name__ == "__main__":
    import os

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    api_key = os.getenv("RIOT_API_KEY")
    if not api_key:
        logger.error("RIOT_API_KEY no encontrada")
        raise SystemExit(1)

    collector = MetaDataCollector(api_key)

    summoners_list = ["Deshu#LAS"]
    collected = collector.collect_matches_batch(summoners_list, count_per_summoner=10)

    collector.save_matches(collected)

    hourly = collector.get_hourly_stats(collected)
    logger.info("Estadísticas por campeón:")
    for champ_name, champ_data in sorted(hourly.items(), key=lambda x: x[1]["winrate"], reverse=True):
        logger.info("  %s: %d matches, %.1f%% WR", champ_name, champ_data["matches"], champ_data["winrate"])
