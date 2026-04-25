"""
Data Collector - Recolecta datos de partidas en tiempo real
Versión BD-integrada (SQLAlchemy)
"""
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from riot_lol_cli.api import RiotClient
from riot_lol_cli.database.models import ChampionHourly, DatabaseManager, RawMatch

logger = logging.getLogger(__name__)


class MetaDataCollectorDB:
    """Recolecta datos de partidas y los guarda en BD"""
    
    def __init__(self, api_key: str, platform: str = "la2", regional: str = "americas", db_path: str = "data/meta_analyzer.db"):
        self.client = RiotClient(api_key, platform, regional)
        self.platform = platform
        self.regional = regional
        self.db = DatabaseManager(db_path)
        self.data_dir = Path(__file__).parent.parent.parent.parent / "data" / "meta"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def collect_matches_batch(self, summoners: list[str], count_per_summoner: int = 20) -> list[dict[str, Any]]:
        """
        Recolecta partidas de múltiples jugadores y las guarda en BD
        
        Args:
            summoners: Lista de "nombre#tag" en formato Riot ID
            count_per_summoner: Cantidad de matches por jugador
            
        Returns:
            Lista de matches procesados
        """
        matches_data = []
        session = self.db.get_session()
        
        try:
            for summoner in summoners:
                try:
                    game_name, tag_line = summoner.split("#")
                    account = self.client.get_account_by_riot_id(game_name, tag_line)
                    puuid = account["puuid"]
                    
                    # Obtener match IDs
                    match_ids = self.client.get_match_ids_by_puuid(puuid, start=0, count=count_per_summoner)
                    
                    for match_id in match_ids:
                        try:
                            match_detail = self.client.get_match(match_id)
                            processed = self._process_match(match_detail, match_id)
                            
                            # Guardar en BD
                            self._save_match_to_db(session, processed)
                            matches_data.append(processed)
                            
                        except Exception as e:
                            logger.warning("Error procesando match %s: %s", match_id, e)
                            continue
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    logger.warning("Error con summoner %s: %s", summoner, e)
                    continue
            
            session.commit()
            logger.info("Guardadas %d partidas en BD", len(matches_data))
            
        except Exception as e:
            session.rollback()
            logger.error("Error guardando en BD: %s", e)
        finally:
            session.close()
        
        return matches_data

    def _process_match(self, match_detail: dict, match_id: str) -> dict[str, Any]:
        """
        Procesa datos crudos de una partida
        
        Args:
            match_detail: Respuesta del API Match-V5
            match_id: ID de la partida
            
        Returns:
            Match procesado con stats
        """
        info = match_detail.get("info", {})
        participants = info.get("participants", [])
        
        processed = {
            "match_id": match_id,
            "platform_id": info.get("platformId", self.platform),
            "timestamp": datetime.fromtimestamp(info.get("gameCreation", 0) / 1000),
            "match_duration_seconds": info.get("gameDuration", 0),
            "game_mode": info.get("gameMode", ""),
            "game_type": info.get("gameType", ""),
            "participants": []
        }
        
        for participant in participants:
            champ_data = {
                "champion_id": participant.get("championId", 0),
                "champion_name": participant.get("championName", "Unknown"),
                "summoner_name": participant.get("summonerName", ""),
                "summoner_id": participant.get("summonerId", ""),
                "role": participant.get("role", ""),
                "team_id": participant.get("teamId", 0),
                "win": participant.get("win", False),
                "kills": participant.get("kills", 0),
                "deaths": participant.get("deaths", 0),
                "assists": participant.get("assists", 0),
                "damage_dealt": participant.get("totalDamageDealtToChampions", 0),
                "damage_taken": participant.get("totalDamageTaken", 0),
                "gold_earned": participant.get("goldEarned", 0),
                "minions_killed": participant.get("totalMinionsKilled", 0),
                "vision_score": participant.get("visionScore", 0),
                "items": [
                    participant.get("item0"),
                    participant.get("item1"),
                    participant.get("item2"),
                    participant.get("item3"),
                    participant.get("item4"),
                    participant.get("item5"),
                    participant.get("item6"),
                ],
                "runes": {
                    "primary": participant.get("perks", {}).get("styles", [{}])[0].get("style"),
                    "secondary": participant.get("perks", {}).get("styles", [{}])[1].get("style") if len(participant.get("perks", {}).get("styles", [])) > 1 else None,
                }
            }
            processed["participants"].append(champ_data)
        
        return processed

    def _save_match_to_db(self, session, processed: dict[str, Any]):
        """Guarda una partida procesada en BD"""
        for participant in processed.get("participants", []):
            match = RawMatch(
                match_id=processed["match_id"],
                platform_id=processed["platform_id"],
                timestamp=processed["timestamp"],
                match_duration_seconds=processed["match_duration_seconds"],
                game_mode=processed["game_mode"],
                game_type=processed["game_type"],
                champion_id=participant["champion_id"],
                champion_name=participant["champion_name"],
                summoner_name=participant["summoner_name"],
                summoner_id=participant["summoner_id"],
                role=participant["role"],
                team_id=participant["team_id"],
                win=participant["win"],
                kills=participant["kills"],
                deaths=participant["deaths"],
                assists=participant["assists"],
                damage_dealt=participant["damage_dealt"],
                damage_taken=participant["damage_taken"],
                gold_earned=participant["gold_earned"],
                minions_killed=participant["minions_killed"],
                vision_score=participant["vision_score"],
                item_0=participant["items"][0],
                item_1=participant["items"][1],
                item_2=participant["items"][2],
                item_3=participant["items"][3],
                item_4=participant["items"][4],
                item_5=participant["items"][5],
                item_6=participant["items"][6],
                rune_primary=participant["runes"]["primary"],
                rune_secondary=participant["runes"]["secondary"],
            )
            session.add(match)

    def get_hourly_stats(self, matches: Optional[list[dict]] = None, hours_back: int = 24) -> dict[str, dict]:
        """
        Calcula estadísticas agregadas por hora desde BD
        
        Args:
            matches: Si es None, obtiene desde BD
            hours_back: Cuántas horas atrás a consultar
            
        Returns:
            Stats agregadas por campeón: {champion: {winrate, pickrate, items_top3, ...}}
        """
        session = self.db.get_session()
        
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours_back)
            
            # Obtener matches del período
            raw_matches = session.query(RawMatch).filter(
                RawMatch.timestamp >= cutoff
            ).all()
            
            # Agrupar por campeón
            champ_stats = defaultdict(lambda: {
                "matches": 0,
                "wins": 0,
                "losses": 0,
                "kills": [],
                "deaths": [],
                "assists": [],
                "damage_dealt": [],
                "damage_taken": [],
                "gold_earned": [],
                "minions_killed": [],
                "vision_score": [],
                "items": defaultdict(int),
                "roles": defaultdict(int),
            })
            
            for match in raw_matches:
                stats = champ_stats[match.champion_name]
                stats["matches"] += 1
                
                if match.win:
                    stats["wins"] += 1
                else:
                    stats["losses"] += 1
                
                stats["kills"].append(match.kills)
                stats["deaths"].append(match.deaths)
                stats["assists"].append(match.assists)
                stats["damage_dealt"].append(match.damage_dealt)
                stats["damage_taken"].append(match.damage_taken)
                stats["gold_earned"].append(match.gold_earned)
                stats["minions_killed"].append(match.minions_killed)
                stats["vision_score"].append(match.vision_score)
                
                # Items
                for item_id in [match.item_0, match.item_1, match.item_2, match.item_3, match.item_4, match.item_5]:
                    if item_id and item_id > 0:
                        stats["items"][item_id] += 1
                
                if match.role:
                    stats["roles"][match.role] += 1
            
            # Calcular promedios
            result = {}
            for champion, stats in champ_stats.items():
                total_matches = len(raw_matches)  # Total de todas las partidas
                
                result[champion] = {
                    "matches": stats["matches"],
                    "wins": stats["wins"],
                    "losses": stats["losses"],
                    "winrate": (stats["wins"] / stats["matches"] * 100) if stats["matches"] > 0 else 0,
                    "pickrate": (stats["matches"] / max(total_matches, 1) * 100),
                    "avg_kills": sum(stats["kills"]) / max(len(stats["kills"]), 1),
                    "avg_deaths": sum(stats["deaths"]) / max(len(stats["deaths"]), 1),
                    "avg_assists": sum(stats["assists"]) / max(len(stats["assists"]), 1),
                    "avg_damage": sum(stats["damage_dealt"]) / max(len(stats["damage_dealt"]), 1),
                    "avg_gold": sum(stats["gold_earned"]) / max(len(stats["gold_earned"]), 1),
                    "avg_vision": sum(stats["vision_score"]) / max(len(stats["vision_score"]), 1),
                    "items_top3": sorted(stats["items"].items(), key=lambda x: x[1], reverse=True)[:3],
                    "main_role": max(stats["roles"].items(), key=lambda x: x[1])[0] if stats["roles"] else "UNKNOWN",
                }
            
            # Guardar stats agregadas por hora
            self._save_hourly_stats(session, result)
            session.commit()
            
            return result
            
        finally:
            session.close()

    def _save_hourly_stats(self, session, stats: dict[str, dict]):
        """Guarda stats horarias en BD"""
        hour_bucket = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        
        for champion, champ_stats in stats.items():
            hourly = ChampionHourly(
                hour_bucket=hour_bucket,
                champion_name=champion,
                total_matches=champ_stats["matches"],
                total_wins=champ_stats["wins"],
                total_losses=champ_stats["losses"],
                winrate_pct=champ_stats["winrate"],
                pickrate_pct=champ_stats["pickrate"],
                banrate_pct=0,  # No tenemos datos de bans aún
                item_1_id=champ_stats["items_top3"][0][0] if champ_stats["items_top3"] else None,
                item_2_id=champ_stats["items_top3"][1][0] if len(champ_stats["items_top3"]) > 1 else None,
                item_3_id=champ_stats["items_top3"][2][0] if len(champ_stats["items_top3"]) > 2 else None,
                avg_kills=champ_stats["avg_kills"],
                avg_deaths=champ_stats["avg_deaths"],
                avg_assists=champ_stats["avg_assists"],
                avg_damage_dealt=champ_stats["avg_damage"],
                avg_damage_taken=0,
                avg_gold_earned=champ_stats["avg_gold"],
                avg_minions_killed=0,
                avg_vision_score=champ_stats["avg_vision"],
                avg_game_duration_seconds=0,
            )
            session.add(hourly)

    def get_stats_by_hour(self) -> dict:
        """
        Obtiene las últimas stats agregadas por hora desde BD
        
        Returns:
            Stats más recientes
        """
        session = self.db.get_session()
        try:
            latest = session.query(ChampionHourly).order_by(
                ChampionHourly.hour_bucket.desc()
            ).first()
            
            if not latest:
                return {}
            
            stats = {}
            hourly_stats = session.query(ChampionHourly).filter(
                ChampionHourly.hour_bucket == latest.hour_bucket
            ).all()
            
            for stat in hourly_stats:
                stats[stat.champion_name] = stat.to_dict()
            
            return stats
            
        finally:
            session.close()
