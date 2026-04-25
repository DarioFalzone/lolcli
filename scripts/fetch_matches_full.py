"""
Script para obtener datos completos de partidas desde la API de Riot
Incluye: daño, oro, visión, duración, nivel del campeón, etc.
"""
import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path

from riot_lol_cli.api import RiotClient
from riot_lol_cli.paths import BASE_DIR

# Configuración por defecto (se puede sobreescribir por args/env)
DEFAULT_GAME_NAME = os.getenv("GAME_NAME", "Deshu")
DEFAULT_TAG_LINE = os.getenv("TAG_LINE", "LAS")
DEFAULT_PLATFORM = os.getenv("PLATFORM", "la2")
DEFAULT_REGIONAL = os.getenv("REGIONAL", "americas")
DEFAULT_MAX_MATCHES = int(os.getenv("MAX_MATCHES", "100"))


def find_api_key():
    """Busca la API key en múltiples ubicaciones (sin hardcode)."""
    # 1) Variable de entorno
    api_key = os.getenv("RIOT_API_KEY", "").strip()
    if api_key:
        return api_key

    # 2) Archivo .env
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("RIOT_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")

    # 3) Archivo config/api_key.txt
    api_key_file = Path("config/api_key.txt")
    if api_key_file.exists():
        return api_key_file.read_text(encoding="utf-8").strip()

    # 4) Archivo api_key.txt en raíz
    api_key_file2 = Path("api_key.txt")
    if api_key_file2.exists():
        return api_key_file2.read_text(encoding="utf-8").strip()

    return None

def main():
    parser = argparse.ArgumentParser(description="Fetch de partidas desde Riot API y guarda matches.json")
    parser.add_argument("--game-name", dest="game_name", default=DEFAULT_GAME_NAME)
    parser.add_argument("--tag-line", dest="tag_line", default=DEFAULT_TAG_LINE)
    parser.add_argument("--platform", dest="platform", default=DEFAULT_PLATFORM,
                        help="la2, la1, na1, br1, euw1, eun1, tr1, ru, kr, jp1, oc1")
    parser.add_argument("--regional", dest="regional", default=DEFAULT_REGIONAL,
                        help="americas, europe, asia")
    parser.add_argument("--count", dest="count", type=int, default=DEFAULT_MAX_MATCHES)
    parser.add_argument("--output", dest="output", default="data/cache/matches.json")
    args = parser.parse_args()

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
    client = RiotClient(API_KEY, args.platform, args.regional)
    
    try:
        # 1. Obtener cuenta por Riot ID
        print(f"📡 Obteniendo cuenta para {args.game_name}#{args.tag_line}...")
        account = client.get_account_by_riot_id(args.game_name, args.tag_line)
        puuid = account["puuid"]
        print(f"✅ PUUID: {puuid}")
        
        # 2. Obtener datos del invocador
        print("📡 Obteniendo datos del invocador...")
        summoner = client.get_summoner_by_puuid(puuid)
        summoner_level = summoner.get("summonerLevel", 0)
        profile_icon_id = summoner.get("profileIconId", 0)
        print(f"✅ Nivel: {summoner_level}, Icono: {profile_icon_id}")
        
        # 3. Obtener versión de Data Dragon y catálogos
        print("📡 Obteniendo versión de Data Dragon...")
        versions = client.get_ddragon_versions()
        ddragon_version = versions[0]
        print(f"✅ Versión: {ddragon_version}")

        print("📡 Cargando catálogos (spells, runes, queues)...")
        spells_catalog = client.get_ddragon_summoner_spells(ddragon_version)
        runes_catalog = client.get_ddragon_runes(ddragon_version)
        queues_catalog = client.get_queues()

        # Construir mapas de resolución rápida
        # Hechizos: id numérico -> nombre
        spell_id_to_name = {}
        try:
            for key, value in spells_catalog.get("data", {}).items():
                sid = int(value.get("key", 0))
                spell_id_to_name[sid] = value.get("name", key)
        except Exception:
            pass

        # Runas: treeId->treeName y perkId->runeName
        rune_tree_id_to_name = {}
        rune_id_to_name = {}
        try:
            for tree in runes_catalog:
                rune_tree_id_to_name[tree.get("id")] = tree.get("name")
                for slot in tree.get("slots", []):
                    for rune in slot.get("runes", []):
                        rune_id_to_name[rune.get("id")] = rune.get("name")
        except Exception:
            pass

        # Queues: queueId -> descripción amigable
        queue_id_to_desc = {}
        try:
            for q in queues_catalog:
                qid = q.get("queueId")
                map_ = q.get("map", "")
                desc = q.get("description") or ""
                if desc:
                    queue_id_to_desc[qid] = desc
                else:
                    queue_id_to_desc[qid] = map_ or "Unknown Queue"
        except Exception:
            pass
        
        # 4. Obtener IDs de partidas
        print(f"📡 Obteniendo últimas {args.count} partidas...")
        match_ids = client.get_match_ids_by_puuid(puuid, start=0, count=args.count)
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

                # Queue info
                queue_id = match_detail["info"].get("queueId")
                queue_desc = queue_id_to_desc.get(queue_id, str(queue_id))

                # Rol/línea (preferir teamPosition si existe)
                team_position = participant.get("teamPosition") or ""
                role = participant.get("role") or team_position
                lane = participant.get("lane")

                # Hechizos (ids -> nombres)
                summoner1_id = participant.get("summoner1Id")
                summoner2_id = participant.get("summoner2Id")
                summoner1_name = spell_id_to_name.get(summoner1_id, str(summoner1_id))
                summoner2_name = spell_id_to_name.get(summoner2_id, str(summoner2_id))

                # Runas (estructura perks -> nombres)
                perks = participant.get("perks", {})
                primary_style_id = None
                secondary_style_id = None
                primary_runes = []
                secondary_runes = []
                try:
                    styles = perks.get("styles", [])
                    if len(styles) > 0:
                        primary_style_id = styles[0].get("style")
                        for sel in styles[0].get("selections", []):
                            rid = sel.get("perk")
                            if rid is not None:
                                primary_runes.append(rune_id_to_name.get(rid, str(rid)))
                    if len(styles) > 1:
                        secondary_style_id = styles[1].get("style")
                        for sel in styles[1].get("selections", []):
                            rid = sel.get("perk")
                            if rid is not None:
                                secondary_runes.append(rune_id_to_name.get(rid, str(rid)))
                except Exception:
                    pass

                primary_style_name = rune_tree_id_to_name.get(primary_style_id, str(primary_style_id)) if primary_style_id else None
                secondary_style_name = rune_tree_id_to_name.get(secondary_style_id, str(secondary_style_id)) if secondary_style_id else None

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
                    "role": role,
                    "lane": lane,
                    "team_position": team_position,
                    "queue_id": queue_id,
                    "queue": queue_desc,
                    "summoners": {
                        "d": {"id": summoner1_id, "name": summoner1_name},
                        "f": {"id": summoner2_id, "name": summoner2_name}
                    },
                    "runes": {
                        "primary": {"style": primary_style_name, "runes": primary_runes},
                        "secondary": {"style": secondary_style_name, "runes": secondary_runes}
                    },
                    "total_damage_dealt": participant["totalDamageDealtToChampions"],
                    "gold_earned": participant["goldEarned"],
                    "vision_score": participant["visionScore"],
                    "cs": participant.get("totalMinionsKilled", 0) + participant.get("neutralMinionsKilled", 0),
                    "largest_multi_kill": participant.get("largestMultiKill", 0),
                    "multi_kills": {
                        "double": participant.get("doubleKills", 0),
                        "triple": participant.get("tripleKills", 0),
                        "quadra": participant.get("quadraKills", 0),
                        "penta": participant.get("pentaKills", 0)
                    },
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
            "platform": args.platform,
            "server": args.tag_line.upper(),
            "display_name": f"{args.game_name}#{args.tag_line}",
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
        output_dir = Path(args.output).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = Path(args.output)
        
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
