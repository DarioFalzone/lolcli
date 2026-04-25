import json
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

from riot_lol_cli import paths
from riot_lol_cli.settings import get_ddragon_version
from riot_lol_cli.versioning import get_version


def load_template(template_name: str) -> str:
    template_path = paths.TEMPLATES_DIR / f"{template_name}.html"
    if not template_path.exists():
        raise FileNotFoundError(f"Plantilla no encontrada: {template_name}")
    return template_path.read_text(encoding="utf-8")


def load_matches_data(json_path: str) -> dict[str, Any]:
    file_path = Path(json_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {json_path}")

    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Error al decodificar el archivo JSON: {json_path}") from exc


def get_item_icon(item_id: int, ddragon_version: str) -> str:
    if item_id == 0:
        return ""
    return f"https://ddragon.leagueoflegends.com/cdn/{ddragon_version}/img/item/{item_id}.png"


def get_champion_icon(champ_id: str, ddragon_version: str) -> str:
    return f"https://ddragon.leagueoflegends.com/cdn/{ddragon_version}/img/champion/{champ_id}.png"


def _normalize_items(items: Any) -> dict[str, Any]:
    if isinstance(items, list):
        items_dict = {str(index): item_id for index, item_id in enumerate(items) if item_id and item_id > 0}
        if len(items) > 6 and items[6]:
            items_dict["trinket"] = items[6]
        return items_dict

    if isinstance(items, dict):
        return items

    return {}


def _render_items(items: Any, ddragon_version: str) -> str:
    items = _normalize_items(items)
    items_html = ['<div class="items-container"><div class="items-row">']

    try:
        for index in range(6):
            item_id = int(items.get(str(index), 0) or 0)
            if item_id > 0:
                item_url = get_item_icon(item_id, ddragon_version)
                item_img = (
                    f'<img src="{item_url}" class="item-icon" alt="Item {item_id}" loading="lazy">'
                )
                items_html.append(f'<div class="item" data-item-id="{item_id}">{item_img}</div>')
            else:
                items_html.append('<div class="item-empty"></div>')

        trinket_id = int(items.get("trinket", items.get("6", 0)) or 0)
        if trinket_id > 0:
            trinket_url = get_item_icon(trinket_id, ddragon_version)
            trinket_img = (
                f'<img src="{trinket_url}" class="item-icon trinket" '
                f'alt="Trinket {trinket_id}" loading="lazy">'
            )
            items_html.append(f'<div class="item trinket" data-item-id="{trinket_id}">{trinket_img}</div>')
        else:
            items_html.append('<div class="item-empty trinket"></div>')
    except (TypeError, ValueError):
        return '<div class="items-container"><div class="items-row">Error al cargar ítems</div></div>'

    items_html.append("</div></div>")
    return "".join(items_html)


def _escape_text(value: Any) -> str:
    return escape(str(value or ""))


def generate_match_history_html(template: str, data: dict[str, Any], template_name: str) -> str:
    version = get_version()
    ddragon_version = _escape_text(data.get("ddragon_version") or get_ddragon_version())

    html = template
    total_matches = 0
    wins = 0
    matches_html = []

    matches_key = "rows" if "rows" in data else "matches"
    matches = data.get(matches_key, [])

    if isinstance(matches, list):
        total_matches = len(matches)

        for match in matches:
            if not isinstance(match, dict):
                continue

            try:
                win = match.get("win")
                if win is True:
                    result_class = "victory"
                    result_text = "Victoria"
                    wins += 1
                elif win is False:
                    result_class = "defeat"
                    result_text = "Derrota"
                else:
                    result_class = "remake"
                    result_text = "Remake"

                champ_id = _escape_text(match.get("champ_id"))
                champ_name = _escape_text(match.get("champ", "Desconocido"))
                champ_icon = get_champion_icon(champ_id, ddragon_version) if champ_id else ""

                kda_str = str(match.get("kda", "0/0/0"))
                kda_parts = kda_str.split("/")
                if len(kda_parts) == 3:
                    kills, deaths, assists = map(int, kda_parts)
                else:
                    kills, deaths, assists = 0, 0, 0
                kda = f"{kills}/{deaths}/{assists}"

                queue_text = _escape_text(match.get("queue"))
                role_text = _escape_text(match.get("team_position") or match.get("role"))
                cs_val = int(match.get("cs", 0) or 0)
                vision_val = int(match.get("vision_score", 0) or 0)
                largest_multi_kill = int(match.get("largest_multi_kill", 0) or 0)
                match_id = _escape_text(match.get("match_id"))

                summoners = match.get("summoners", {}) or {}
                d_name = _escape_text((summoners.get("d") or {}).get("name"))
                f_name = _escape_text((summoners.get("f") or {}).get("name"))

                runes = match.get("runes", {}) or {}
                primary = runes.get("primary") or {}
                secondary = runes.get("secondary") or {}
                p_style = _escape_text(primary.get("style"))
                s_style = _escape_text(secondary.get("style"))
                p_runes = ", ".join(_escape_text(rune) for rune in (primary.get("runes", []) or []))
                s_runes = ", ".join(_escape_text(rune) for rune in (secondary.get("runes", []) or []))

                items_html = _render_items(match.get("items", {}), ddragon_version)

                spells_html = ""
                if d_name or f_name:
                    spells_html = (
                        f'<div class="badge" title="Hechizos">Spells: <strong>{d_name}</strong> '
                        f'/ <strong>{f_name}</strong></div>'
                    )

                runes_html = ""
                if p_style or s_style or p_runes or s_runes:
                    runes_html = (
                        '<div class="badge" title="Runas">'
                        f'Runas: <strong>{p_style}</strong>'
                        + (f" ({p_runes})" if p_runes else "")
                        + (f" • <strong>{s_style}</strong>" if s_style else "")
                        + (f" ({s_runes})" if s_runes else "")
                        + "</div>"
                    )

                queue_role_html = ""
                if queue_text or role_text:
                    separator = " • " if queue_text and role_text else ""
                    queue_role_html = (
                        f'<div class="badge" title="Cola y rol">{queue_text}{separator}{role_text}</div>'
                    )

                extras_meta_html = (
                    '<div class="badge" title="CS / Visión / Multikills">'
                    f"CS: <strong>{cs_val}</strong> • Visión: <strong>{vision_val}</strong> "
                    f"• Multi: <strong>x{largest_multi_kill}</strong>"
                    "</div>"
                )

                match_id_html = ""
                if match_id:
                    match_id_html = f'<div class="badge" title="Match ID">{match_id}</div>'

                damage = int(match.get("total_damage_dealt", 0) or 0)
                gold = int(match.get("gold_earned", 0) or 0)
                champ_level = _escape_text(match.get("champ_level", "?"))
                kda_ratio = float(match.get("kda_ratio", 0) or 0)
                game_duration = _escape_text(match.get("game_duration", "0:00"))
                game_creation = _escape_text(match.get("game_creation", ""))
                time_ago = _escape_text(match.get("time_ago", "Hace un momento"))

                ratio_html = ""
                if kda_ratio > 0:
                    ratio_html = f'<div class="kda-ratio">{kda_ratio}:1 KDA</div>'

                match_html = f"""
                <tr class="match-row {result_class}">
                    <td class="champ-cell">
                        <img src="{champ_icon}" class="champ-icon" alt="{champ_name}"
                             onerror="this.onerror=null; this.src='https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/-1.png'"
                             data-champion-id="{champ_id}">
                        <div class="champ-info">
                            <div class="champ-name" title="{champ_name}">{champ_name}</div>
                            <div class="champ-role">{role_text.strip()} • Lvl {champ_level}</div>
                        </div>
                    </td>
                    <td class="kda">
                        <div class="kda-value">{kda}</div>
                        {ratio_html}
                    </td>
                    <td class="items">
                        {items_html}
                        <div class="match-stats">
                            <div class="stat">
                                <span class="stat-value">{damage:,}</span>
                                <span class="stat-label">Daño</span>
                            </div>
                            <div class="stat">
                                <span class="stat-value">{gold:,}</span>
                                <span class="stat-label">Oro</span>
                            </div>
                            <div class="stat">
                                <span class="stat-value">{vision_val}</span>
                                <span class="stat-label">Visión</span>
                            </div>
                        </div>
                        <div class="meta" style="margin-top:10px; gap:10px; flex-wrap: wrap;">
                            {queue_role_html}
                            {spells_html}
                            {runes_html}
                            {extras_meta_html}
                            {match_id_html}
                        </div>
                    </td>
                    <td class="result">
                        <span class="pill {result_class}">{result_text}</span>
                        <div class="match-duration">{game_duration}</div>
                        <div class="match-time" title="{game_creation}">
                            {time_ago}
                        </div>
                        <div class="queue-text" style="margin-top:6px; color:#c8aa6e; font-weight:700; font-size:12px;">{queue_text}</div>
                    </td>
                </tr>
                """
                matches_html.append(match_html)
            except (TypeError, ValueError):
                continue

    win_rate = (wins / total_matches * 100) if total_matches > 0 else 0
    display_name = data.get("display_name") or data.get("summoner_name") or "Invocador"

    replacements = {
        "{{matches_rows}}": "".join(matches_html) if matches_html else '<tr><td colspan="4">No se encontraron partidas</td></tr>',
        "{{generated_at}}": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "{{version}}": f"v{version}",
        "{{template_name}}": _escape_text(template_name),
        "{{total_matches}}": str(total_matches),
        "{{win_rate}}": f"{win_rate:.1f}%",
        "{{wins}}": str(wins),
        "{{losses}}": str(max(0, total_matches - wins)),
        "{{title}}": "Estadísticas de Partidas",
        "{{display_name}}": _escape_text(display_name),
        "{{subtitle}}": _escape_text(f"{total_matches} partidas jugadas • {win_rate:.1f}% de victorias"),
        "{{profile_icon_id}}": str(data.get("profileIconId", 0)),
        "{{ddragon_version}}": ddragon_version,
        "{{level}}": str(data.get("level", "?")),
        "{{server}}": _escape_text(data.get("server", data.get("platform", "N/A")).upper()),
    }

    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    return html
