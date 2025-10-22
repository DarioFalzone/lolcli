"""
Script para obtener datos completos de partidas desde la API de Riot
Incluye: daño, oro, visión, duración, nivel del campeón, etc.
"""
import json
import os
import time
from datetime import datetime
from pathlib import Path

from src.riot_lol_cli.api import RiotClient

# Configuración
GAME_NAME = "Deshu"
TAG_LINE = "LAS"
PLATFORM = "la2"
REGIONAL = "americas"
MAX_MATCHES = 100

def find_api_key():
    """Busca la API key en múltiples ubicaciones"""
    # 0. API Key hardcoded (temporal)
    hardcoded_key = "RGAPI-f6a264bb-7878-4e16-8852-8ef348c464de"
    if hardcoded_key and hardcoded_key.startswith("RGAPI-"):
        print("✅ Usando API key configurada")
        return hardcoded_key
    
    # 1. Variable de entorno
    api_key = os.getenv("RIOT_API_KEY", "")
    if api_key:
        return api_key
    
    # 2. Archivo .env
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                if line.startswith("RIOT_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    
    # 3. Archivo config/api_key.txt
    api_key_file = Path("config/api_key.txt")
    if api_key_file.exists():
        with open(api_key_file, "r") as f:
            return f.read().strip()
    
    # 4. Archivo api_key.txt en raíz
    api_key_file = Path("api_key.txt")
    if api_key_file.exists():
        with open(api_key_file, "r") as f:
            return f.read().strip()
    
    return None

def main():
    API_KEY = find_api_key()
    
    if not API_KEY:
        print("❌ Error: No se encontró RIOT_API_KEY")
        print("Buscado en:")
        print("  - Variable de entorno RIOT_API_KEY")
        print("  - Archivo .env")
        print("  - config/api_key.txt")
        print("  - api_key.txt")
        return
    
    print("🔧 Inicializando cliente de Riot API...")
    client = RiotClient(API_KEY, PLATFORM, REGIONAL)
    
    try:
        # 1. Obtener cuenta por Riot ID
        print(f"📡 Obteniendo cuenta para {GAME_NAME}#{TAG_LINE}...")
        account = client.get_account_by_riot_id(GAME_NAME, TAG_LINE)
        puuid = account["puuid"]
        print(f"✅ PUUID: {puuid}")
        
        # 2. Obtener datos del invocador
        print("📡 Obteniendo datos del invocador...")
        summoner = client.get_summoner_by_puuid(puuid)
        summoner_level = summoner.get("summonerLevel", 0)
        profile_icon_id = summoner.get("profileIconId", 0)
        print(f"✅ Nivel: {summoner_level}, Icono: {profile_icon_id}")
        
        # 3. Obtener versión de Data Dragon
        print("📡 Obteniendo versión de Data Dragon...")
        versions = client.get_ddragon_versions()
        ddragon_version = versions[0]
        print(f"✅ Versión: {ddragon_version}")
        
        # 4. Obtener IDs de partidas
        print(f"📡 Obteniendo últimas {MAX_MATCHES} partidas...")
        match_ids = client.get_match_ids_by_puuid(puuid, start=0, count=MAX_MATCHES)
        print(f"✅ Se encontraron {len(match_ids)} partidas")
        
        # 5. Obtener detalles de cada partida
        matches_data = []
        wins = 0
        losses = 0
        
        for i, match_id in enumerate(match_ids, 1):
            print(f"📡 [{i}/{len(match_ids)}] Obteniendo detalles de {match_id}...")
            
            try:
                match_detail = client.get_match(match_id)
                
                # Buscar al jugador en los participantes
                participant = None
                for p in match_detail["info"]["participants"]:
                    if p["puuid"] == puuid:
                        participant = p
                        break
                
                if not participant:
                    print(f"⚠️  No se encontró al jugador en la partida {match_id}")
                    continue
                
                # Extraer datos
                win = participant["win"]
                if win:
                    wins += 1
                else:
                    losses += 1
                
                # Calcular KDA ratio
                kills = participant["kills"]
                deaths = participant["deaths"]
                assists = participant["assists"]
                kda_ratio = ((kills + assists) / deaths) if deaths > 0 else (kills + assists)
                
                # Duración de la partida
                game_duration_seconds = match_detail["info"]["gameDuration"]
                game_duration_minutes = game_duration_seconds // 60
                game_duration_display = f"{game_duration_minutes // 60}:{game_duration_minutes % 60:02d}" if game_duration_minutes >= 60 else f"{game_duration_minutes}:{game_duration_seconds % 60:02d}"
                
                # Timestamp
                game_creation = match_detail["info"]["gameCreation"]
                game_date = datetime.fromtimestamp(game_creation / 1000)
                time_ago = calculate_time_ago(game_date)
                
                match_data = {
                    "champ": participant["championName"],
                    "champ_id": participant["championName"],
                    "champ_level": participant["champLevel"],
                    "kda": f"{kills}/{deaths}/{assists}",
                    "kda_ratio": round(kda_ratio, 2),
                    "kills": kills,
                    "deaths": deaths,
                    "assists": assists,
                    "win": win,
                    "match_id": match_id,
                    "items": [
                        participant["item0"],
                        participant["item1"],
                        participant["item2"],
                        participant["item3"],
                        participant["item4"],
                        participant["item5"],
                        participant["item6"]  # Trinket
                    ],
                    "total_damage_dealt": participant["totalDamageDealtToChampions"],
                    "gold_earned": participant["goldEarned"],
                    "vision_score": participant["visionScore"],
                    "game_duration": game_duration_display,
                    "game_duration_seconds": game_duration_seconds,
                    "game_creation": game_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "time_ago": time_ago,
                    "ddragon_version": ddragon_version
                }
                
                matches_data.append(match_data)
                
                # Rate limiting: pequeña pausa entre requests
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Error obteniendo detalles de {match_id}: {e}")
                continue
        
        # 6. Calcular estadísticas
        total_matches = len(matches_data)
        win_rate = (wins / total_matches * 100) if total_matches > 0 else 0
        
        # 7. Crear estructura de datos final
        output_data = {
            "version": 1,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "platform": PLATFORM,
            "server": "LAS",
            "display_name": f"{GAME_NAME}#{TAG_LINE}",
            "level": summoner_level,
            "puuid": puuid,
            "ddragon_version": ddragon_version,
            "profileIconId": profile_icon_id,
            "filters": {
                "range": "last_100",
                "queue": 420  # Ranked Solo/Duo
            },
            "rows": matches_data,
            "count": total_matches,
            "wins": wins,
            "losses": losses,
            "win_rate": round(win_rate, 1)
        }
        
        # 8. Guardar en archivo JSON
        output_dir = Path("data/cache")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "matches.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ ¡Datos guardados exitosamente en {output_file}!")
        print(f"📊 Estadísticas:")
        print(f"   Total de partidas: {total_matches}")
        print(f"   Victorias: {wins}")
        print(f"   Derrotas: {losses}")
        print(f"   Win Rate: {win_rate:.1f}%")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def calculate_time_ago(game_date):
    """Calcula cuánto tiempo hace que se jugó la partida"""
    now = datetime.now()
    delta = now - game_date
    
    if delta.days > 365:
        years = delta.days // 365
        return f"Hace {years} año{'s' if years > 1 else ''}"
    elif delta.days > 30:
        months = delta.days // 30
        return f"Hace {months} mes{'es' if months > 1 else ''}"
    elif delta.days > 0:
        return f"Hace {delta.days} día{'s' if delta.days > 1 else ''}"
    elif delta.seconds > 3600:
        hours = delta.seconds // 3600
        return f"Hace {hours} hora{'s' if hours > 1 else ''}"
    elif delta.seconds > 60:
        minutes = delta.seconds // 60
        return f"Hace {minutes} minuto{'s' if minutes > 1 else ''}"
    else:
        return "Hace un momento"

if __name__ == "__main__":
    main()
