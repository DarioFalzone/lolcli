"""
Data Collector - Recolecta datos de partidas en tiempo real
"""
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict

from riot_lol_cli.api import RiotClient


class MetaDataCollector:
    """Recolecta datos de partidas para análisis de meta"""
    
    def __init__(self, api_key: str, platform: str = "la2", regional: str = "americas"):
        self.client = RiotClient(api_key, platform, regional)
        self.platform = platform
        self.regional = regional
        self.data_dir = Path(__file__).parent.parent.parent.parent / "data" / "meta"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def collect_matches_batch(self, summoners: List[str], count_per_summoner: int = 20) -> List[Dict[str, Any]]:
        """
        Recolecta partidas de múltiples jugadores
        
        Args:
            summoners: Lista de "nombre#tag" en formato Riot ID
            count_per_summoner: Cantidad de matches por jugador
            
        Returns:
            Lista de matches procesados
        """
        matches_data = []
        
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
                        matches_data.append(processed)
                    except Exception as e:
                        print(f"⚠️ Error procesando match {match_id}: {e}")
                        continue
                    
                    time.sleep(0.05)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error con jugador {summoner}: {e}")
                continue
        
        return matches_data
    
    def _process_match(self, match_detail: Dict[str, Any], match_id: str) -> Dict[str, Any]:
        """
        Procesa un match crudo en estructura útil para análisis
        
        Estructura de salida:
        {
            'match_id': 'LA2_...',
            'timestamp': 1704067200,
            'duration': 1547,
            'champions': [
                {
                    'champion_id': 'Ekko',
                    'role': 'MIDDLE',
                    'team': 100,
                    'result': True,
                    'items': [3089, 3156, 3001, 0, 0, 0],
                    'runes': {'primary': 8112, 'secondary': 8214},
                    'stats': {
                        'kills': 5,
                        'deaths': 2,
                        'assists': 10,
                        'damage': 18500,
                        'gold': 12300,
                        'vision': 45
                    }
                },
                ...
            ]
        }
        """
        
        info = match_detail['info']
        participants = info['participants']
        
        match_data = {
            'match_id': match_id,
            'timestamp': info['gameCreationTime'] // 1000,  # Convertir a segundos
            'duration': info['gameDuration'],
            'game_type': info['gameType'],
            'queue_id': info['queueId'],
            'champions': []
        }
        
        for participant in participants:
            champion_data = {
                'champion_id': participant['championId'],
                'champion_name': participant['championName'],
                'role': participant.get('role', 'UNKNOWN'),
                'lane': participant.get('lane', 'UNKNOWN'),
                'team': participant['teamId'],
                'result': participant['win'],
                'items': [
                    participant['item0'],
                    participant['item1'],
                    participant['item2'],
                    participant['item3'],
                    participant['item4'],
                    participant['item5'],
                    participant['item6'],  # Trinket
                ],
                'runes': {
                    'primary': participant['perks']['styles'][0]['selections'][0]['perk'],
                    'secondary': participant['perks']['styles'][1]['style'],
                },
                'stats': {
                    'kills': participant['kills'],
                    'deaths': participant['deaths'],
                    'assists': participant['assists'],
                    'damage_champions': participant['totalDamageDealtToChampions'],
                    'damage_taken': participant['totalDamageTaken'],
                    'gold': participant['goldEarned'],
                    'cs': participant['totalMinionsKilled'] + participant.get('neutralMinionsKilled', 0),
                    'vision': participant['visionScore'],
                    'level': participant['champLevel']
                }
            }
            
            match_data['champions'].append(champion_data)
        
        return match_data
    
    def save_matches(self, matches: List[Dict[str, Any]], timestamp: Optional[str] = None) -> Path:
        """
        Guarda matches en archivo JSON con timestamp
        
        Nombre archivo: meta_data_2025-01-11_14-30.json
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        
        filepath = self.data_dir / f"meta_data_{timestamp}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'collected_at': datetime.now().isoformat(),
                'platform': self.platform,
                'count': len(matches),
                'matches': matches
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✅ {len(matches)} matches guardados en {filepath}")
        return filepath
    
    def get_hourly_stats(self, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Genera estadísticas agregadas por hora
        
        Retorna:
        {
            'Ekko': {
                'matches': 45,
                'wins': 24,
                'losses': 21,
                'winrate': 53.33,
                'pickrate': 8.5,
                'items_top3': [3089, 3156, 3001],
                'avg_damage': 18500,
                'avg_gold': 12300,
                'roles': {
                    'MIDDLE': {
                        'matches': 44,
                        'winrate': 53.5
                    }
                }
            },
            ...
        }
        """
        
        stats = defaultdict(lambda: {
            'matches': 0,
            'wins': 0,
            'losses': 0,
            'total_damage': 0,
            'total_gold': 0,
            'total_vision': 0,
            'items_counter': defaultdict(int),
            'roles': defaultdict(lambda: {'matches': 0, 'wins': 0}),
        })
        
        total_matches = sum(len(m['champions']) for m in matches)
        
        for match in matches:
            for champ in match['champions']:
                champion_name = champ['champion_name']
                role = champ['role']
                
                stats[champion_name]['matches'] += 1
                if champ['result']:
                    stats[champion_name]['wins'] += 1
                else:
                    stats[champion_name]['losses'] += 1
                
                stats[champion_name]['total_damage'] += champ['stats']['damage_champions']
                stats[champion_name]['total_gold'] += champ['stats']['gold']
                stats[champion_name]['total_vision'] += champ['stats']['vision']
                
                # Contar items
                for item_id in champ['items']:
                    if item_id > 0:  # 0 = empty slot
                        stats[champion_name]['items_counter'][item_id] += 1
                
                # Estadísticas por rol
                stats[champion_name]['roles'][role]['matches'] += 1
                if champ['result']:
                    stats[champion_name]['roles'][role]['wins'] += 1
        
        # Formatear resultados
        result = {}
        for champion, data in stats.items():
            matches = data['matches']
            if matches == 0:
                continue
            
            result[champion] = {
                'matches': matches,
                'wins': data['wins'],
                'losses': data['losses'],
                'winrate': round((data['wins'] / matches) * 100, 2),
                'pickrate': round((matches / total_matches) * 100, 2),
                'avg_damage': round(data['total_damage'] / matches),
                'avg_gold': round(data['total_gold'] / matches),
                'avg_vision': round(data['total_vision'] / matches, 1),
                'items_top3': [
                    item_id for item_id, _ in 
                    sorted(data['items_counter'].items(), key=lambda x: x[1], reverse=True)[:3]
                ],
                'roles': {
                    role: {
                        'matches': role_data['matches'],
                        'wins': role_data['wins'],
                        'winrate': round((role_data['wins'] / role_data['matches']) * 100, 2)
                        if role_data['matches'] > 0 else 0
                    }
                    for role, role_data in data['roles'].items()
                    if role_data['matches'] > 0
                }
            }
        
        return result


if __name__ == "__main__":
    import os
    
    api_key = os.getenv("RIOT_API_KEY")
    if not api_key:
        print("❌ RIOT_API_KEY no encontrada")
        exit(1)
    
    collector = MetaDataCollector(api_key)
    
    # Ejemplo: Recolectar datos de algunos jugadores
    summoners = ["Deshu#LAS"]
    matches = collector.collect_matches_batch(summoners, count_per_summoner=10)
    
    # Guardar
    collector.save_matches(matches)
    
    # Mostrar estadísticas
    stats = collector.get_hourly_stats(matches)
    print("\n📊 Estadísticas por campeón:")
    for champ, data in sorted(stats.items(), key=lambda x: x[1]['winrate'], reverse=True):
        print(f"\n{champ}:")
        print(f"  Matches: {data['matches']}")
        print(f"  Winrate: {data['winrate']}%")
        print(f"  Items: {data['items_top3']}")
