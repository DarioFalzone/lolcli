import os
import argparse
from datetime import datetime
from typing import Optional
from pathlib import Path
import time
import json

from .regions import get_regional_route
from .api import RiotClient, RiotAPIError
from .html import render_template, ensure_out_dir


def fmt_datetime(ms: int) -> str:
    try:
        return datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return "-"


def print_match_summary(match: dict, puuid: str) -> str:
    info = match.get("info", {})
    participants = info.get("participants", [])
    me = next((p for p in participants if p.get("puuid") == puuid), None)
    if not me:
        return "-"

    champion = me.get("championName", "?")
    k = me.get("kills", 0)
    d = me.get("deaths", 0)
    a = me.get("assists", 0)
    win = "Win" if me.get("win") else "Loss"
    game_mode = info.get("gameMode", "?")
    started_at = info.get("gameStartTimestamp") or info.get("gameCreation") or 0

    return f"{fmt_datetime(started_at)} | {game_mode} | {champion} | {k}/{d}/{a} | {win}"


CHAMP_NAME_ES_LATAM = {
    "MonkeyKing": "Wukong",
    "Chogath": "Cho'Gath",
    "XinZhao": "Xin Zhao",
    "JarvanIV": "Jarvan IV",
    "LeeSin": "Lee Sin",
    "MasterYi": "Master Yi",
    "MissFortune": "Miss Fortune",
    "TahmKench": "Tahm Kench",
    "TwistedFate": "Twisted Fate",
    "AurelionSol": "Aurelion Sol",
    "KSante": "K'Sante",
    "RekSai": "Rek'Sai",
    "KhaZix": "Kha'Zix",
    "VelKoz": "Vel'Koz",
    "KogMaw": "Kog'Maw",
    "RenGar": "Rengar",
    "Nunu": "Nunu y Willump",
}

def row_from_match(match: dict, puuid: str, match_id: str, ddragon_version: str) -> dict:
    info = match.get("info", {})
    queue_id = info.get("queueId")
    # Solo SoloQ: queueId 420 (Ranked Solo/Duo)
    if queue_id != 420:
        return None
    
    participants = info.get("participants", [])
    me = next((p for p in participants if p.get("puuid") == puuid), None)
    if not me:
        return None
    
    champion_raw = me.get("championName", "?")
    champion = CHAMP_NAME_ES_LATAM.get(champion_raw, champion_raw)
    k = me.get("kills", 0)
    d = me.get("deaths", 0)
    a = me.get("assists", 0)
    win = bool(me.get("win"))
    
    # Items (0-6)
    items = [
        me.get("item0", 0),
        me.get("item1", 0),
        me.get("item2", 0),
        me.get("item3", 0),
        me.get("item4", 0),
        me.get("item5", 0),
        me.get("item6", 0),  # trinket
    ]
    
    return {
        "champ": champion,
        "champ_id": champion_raw,
        "kda": f"{k}/{d}/{a}",
        "win": win,
        "match_id": match_id,
        "items": items,
        "ddragon_version": ddragon_version,
    }


def slugify(value: str) -> str:
    allowed = "abcdefghijklmnopqrstuvwxyz0123456789-"
    value = (value or "").lower().replace("#", "-").replace(" ", "-")
    return "".join(ch for ch in value if ch in allowed or ch.isalnum())

SERVER_MAP = {
    "la2": "LAS",
    "la1": "LAN",
    "na1": "NA",
    "br1": "BR",
    "euw1": "EUW",
    "eun1": "EUNE",
    "tr1": "TR",
    "ru": "RU",
    "kr": "KR",
    "jp1": "JP",
    "oc1": "OCE",
}


def main():
    parser = argparse.ArgumentParser(description="CLI para League of Legends (Riot API)")
    parser.add_argument("--platform", required=True, help="Plataforma: la2, la1, na1, br1, euw1, eun1, tr1, ru, kr, jp1, oc1")
    parser.add_argument("--summoner", required=True, help="Nombre exacto de invocador o Riot ID (nombre#tag)")
    parser.add_argument("--count", type=int, default=10, help="Cantidad de partidas a listar (por defecto 10)")
    parser.add_argument("--api-key", default=os.getenv("RIOT_API_KEY"), help="API key de Riot (o variable RIOT_API_KEY)")
    parser.add_argument("--html-template", default=None, help="Nombre de plantilla HTML (ej: 'gpt 5 medium', 'gpt5-medium')")
    parser.add_argument("--out-dir", default="out", help="Directorio de salida para HTML (por defecto 'out')")
    parser.add_argument("--last-month", action="store_true", help="Listar todas las partidas del último mes (ignora --count)")
    parser.add_argument("--last-year", action="store_true", help="Listar todas las partidas del último año (ignora --count y --last-month)")
    parser.add_argument("--write-json", default=None, help="Guardar datos obtenidos en un archivo JSON")
    parser.add_argument("--read-json", default=None, help="Leer datos desde un archivo JSON y evitar llamadas a la API")
    args = parser.parse_args()

    if not args.api_key and not args.read_json:
        print("Error: Debes proporcionar una API key (argumento --api-key o variable de entorno RIOT_API_KEY)")
        raise SystemExit(2)

    try:
        regional = get_regional_route(args.platform)
    except ValueError as e:
        print(str(e))
        raise SystemExit(2)

    client: Optional[RiotClient] = None
    if not args.read_json:
        client = RiotClient(api_key=args.api_key, platform=args.platform, regional=regional)

    # Variables comunes
    puuid = None
    riot_id_str = None
    summoner = {}
    cache_data = None
    ddragon_version = ""

    if args.read_json:
        # Cargar desde JSON y evitar llamadas a API
        try:
            cache_path = Path(args.read_json)
            cache_data = json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Error leyendo cache JSON: {e}")
            raise SystemExit(2)
        display_name = cache_data.get("display_name") or args.summoner
        level = cache_data.get("level")
        puuid = cache_data.get("puuid")
        ddragon_version = cache_data.get("ddragon_version") or ddragon_version
        # Falso summoner para icono de perfil
        summoner = {"profileIconId": cache_data.get("profileIconId")}
    else:
        # Flujo normal vía API
        try:
            # Permitir formato Riot ID: nombre#tag
            if "#" in args.summoner:
                game_name, tag_line = args.summoner.split("#", 1)
                account = client.get_account_by_riot_id(game_name, tag_line)
                riot_game = account.get("gameName") or game_name
                riot_tag = account.get("tagLine") or tag_line
                riot_id_str = f"{riot_game}#{riot_tag}"
                puuid = account.get("puuid")
                if not puuid:
                    raise RiotAPIError("No se obtuvo PUUID desde Account-V1")
                summoner = client.get_summoner_by_puuid(puuid)
            else:
                summoner = client.get_summoner_by_name(args.summoner)
                puuid = summoner.get("puuid")
        except RiotAPIError as e:
            print(f"Error obteniendo invocador: {e}")
            raise SystemExit(1)

    name = summoner.get("name")
    level = summoner.get("summonerLevel")
    puuid = puuid or summoner.get("puuid")
    display_name = name or riot_id_str or args.summoner

    print(f"Invocador: {display_name} (Nivel {level}) - Plataforma {args.platform}")

    start_ts: Optional[int] = None
    end_ts: Optional[int] = None
    rows = []

    if args.read_json:
        # Usar filas desde cache
        rows = cache_data.get("rows", [])
        ddragon_version = cache_data.get("ddragon_version") or ddragon_version
    else:
        try:
            if args.last_year:
                end_ts = int(time.time())
                start_ts = end_ts - 365 * 24 * 3600
                match_ids: list[str] = []
                start_idx = 0
                page_size = 100
                while True:
                    batch = client.get_match_ids_by_puuid(
                        puuid, start=start_idx, count=page_size, start_time=start_ts, end_time=end_ts
                    )
                    if not batch:
                        break
                    match_ids.extend(batch)
                    if len(batch) < page_size:
                        break
                    start_idx += page_size
            elif args.last_month:
                end_ts = int(time.time())
                start_ts = end_ts - 30 * 24 * 3600
                match_ids: list[str] = []
                start_idx = 0
                page_size = 100
                while True:
                    batch = client.get_match_ids_by_puuid(
                        puuid, start=start_idx, count=page_size, start_time=start_ts, end_time=end_ts
                    )
                    if not batch:
                        break
                    match_ids.extend(batch)
                    if len(batch) < page_size:
                        break
                    start_idx += page_size
            else:
                match_ids = client.get_match_ids_by_puuid(puuid, start=0, count=args.count)
        except RiotAPIError as e:
            print(f"Error listando partidas: {e}")
            raise SystemExit(1)

    # Obtener versión de Data Dragon si no viene en cache
    if not ddragon_version:
        try:
            versions = client.get_ddragon_versions() if client else []
            ddragon_version = versions[0] if versions else "14.1.1"
        except Exception:
            ddragon_version = "14.1.1"

    if not args.read_json:
        if args.last_year:
            print(f"Últimas {len(match_ids)} partidas del último año (filtrando solo SoloQ):")
        elif args.last_month:
            print(f"Últimas {len(match_ids)} partidas del último mes (filtrando solo SoloQ):")
        else:
            print(f"Últimas {len(match_ids)} partidas (filtrando solo SoloQ):")
        for mid in match_ids:
            try:
                match = client.get_match(mid)
                summary = print_match_summary(match, puuid)
                print(f"- {summary} | {mid}")
                row = row_from_match(match, puuid, mid, ddragon_version)
                if row:  # Solo agregar si es SoloQ
                    rows.append(row)
            except RiotAPIError as e:
                print(f"- {mid}: error obteniendo detalle ({e})")

    # Guardar JSON si corresponde
    if args.write_json and not args.read_json:
        try:
            out_path = Path(args.write_json)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            server_label = SERVER_MAP.get(args.platform.lower(), args.platform.upper())
            payload = {
                "version": 1,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "platform": args.platform,
                "server": server_label,
                "display_name": display_name,
                "level": level,
                "puuid": puuid,
                "ddragon_version": ddragon_version,
                "profileIconId": summoner.get("profileIconId"),
                "filters": {
                    "range": "last_year" if args.last_year else ("last_month" if args.last_month else "custom"),
                    "start_ts": start_ts,
                    "end_ts": end_ts,
                    "queue": 420,
                },
                "rows": rows,
                "count": len(rows),
            }
            out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"Cache JSON guardado en: {out_path}")
        except Exception as e:
            print(f"No se pudo guardar el JSON: {e}")

    # Exportar HTML si se solicita
    if args.html_template:
        key = (args.html_template or "").strip().lower().replace("_", "-").replace(" ", "-").replace(".", "-")
        mapping = {
            "gpt5-medium": "gpt5-medium",
            "gpt-5-medium": "gpt5-medium",
            "gpt5medium": "gpt5-medium",
            "claude-4-5": "claude-4-5",
            "claude-45": "claude-4-5",
            "claude45": "claude-4-5",
            "claude4-5": "claude-4-5",
        }
        template_name = mapping.get(key, key)

        # Construir filas HTML
        def row_html(r: dict) -> str:
            pill_cls = "win" if r.get("win") else "loss"
            pill_txt = "Victoria" if r.get("win") else "Derrota"
            champ_id = r.get("champ_id", "")
            champ_name = r.get("champ", "")
            ddragon_v = r.get("ddragon_version", "14.1.1")
            champ_img = f"https://ddragon.leagueoflegends.com/cdn/{ddragon_v}/img/champion/{champ_id}.png"
            
            # Items
            items = r.get("items", [])
            items_html = ""
            for item_id in items:
                if item_id and item_id != 0:
                    item_img = f"https://ddragon.leagueoflegends.com/cdn/{ddragon_v}/img/item/{item_id}.png"
                    items_html += f'<img src="{item_img}" class="item-icon" alt="Item {item_id}" title="Item {item_id}" />'
                else:
                    items_html += '<div class="item-empty"></div>'
            
            return (
                f"<tr>"
                f"<td><div class='champ-cell'><img src='{champ_img}' class='champ-icon' alt='{champ_name}' /><span>{champ_name}</span></div></td>"
                f"<td>{r.get('kda','')}</td>"
                f"<td><div class='items-row'>{items_html}</div></td>"
                f"<td><span class=\"pill {pill_cls}\">{pill_txt}</span></td>"
                f"</tr>"
            )

        matches_rows = "\n".join(row_html(r) for r in rows)
        initials = (display_name or "?").strip()[:2].upper()
        # Obtener icono de perfil Data Dragon
        icon_url = None
        icon_id = (summoner or {}).get("profileIconId")
        if icon_id is not None:
            icon_url = f"https://ddragon.leagueoflegends.com/cdn/{ddragon_version}/img/profileicon/{icon_id}.png"

        server_label = SERVER_MAP.get(args.platform.lower(), args.platform.upper())
        placeholders = {
            "title": f"Perfil LoL · {display_name}",
            "avatar": initials,
            "invoker_name": display_name,
            "subtitle": f"Historial del último año" if args.last_year else (f"Historial del último mes" if args.last_month else f"Historial de las últimas {len(rows)} partidas"),
            "platform": args.platform,
            "server": server_label,
            "level": level,
            "matches_rows": matches_rows,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "profile_icon_url": icon_url or "",
        }

        html = render_template(template_name, placeholders)
        slug = slugify(display_name)
        out_dir = Path(args.out_dir) / template_name
        out_path = out_dir / f"{slug}-{template_name}.html"
        ensure_out_dir(out_path)
        out_path.write_text(html, encoding="utf-8")
        print(f"HTML generado: {out_path}")


if __name__ == "__main__":
    main()
