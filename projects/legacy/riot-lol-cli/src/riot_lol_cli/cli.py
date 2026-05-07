import click
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Create a Click command group
@click.group()
@click.version_option()
def cli():
    """CLI principal para la generación de estadísticas de League of Legends."""
    pass

# Configuración de rutas
BASE_DIR = Path(__file__).parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "outputs"
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
CONFIG_DIR = BASE_DIR / "config"
VERSION_FILE = CONFIG_DIR / "version.json"

# Asegurar que los directorios existan
for directory in [TEMPLATES_DIR, OUTPUT_DIR, DATA_DIR, CACHE_DIR, CONFIG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

def load_version() -> str:
    """Carga la versión actual desde el archivo de versión."""
    try:
        with open(VERSION_FILE, 'r') as f:
            version_data = json.load(f)
            return version_data.get('version', '1.0.0')
    except (FileNotFoundError, json.JSONDecodeError):
        # Si el archivo no existe o está corrupto, crea uno nuevo
        version_data = {'version': '1.0.0'}
        with open(VERSION_FILE, 'w') as f:
            json.dump(version_data, f, indent=2)
        return '1.0.0'

def increment_version() -> str:
    """Incrementa el número de versión y lo guarda en el archivo."""
    current_version = load_version()
    parts = [int(part) for part in current_version.split('.')]
    parts[-1] += 1  # Incrementa el patch version
    
    # Lógica para manejar el acarreo
    for i in range(len(parts)-1, 0, -1):
        if parts[i] > 9:  # Si excedemos un dígito
            parts[i] = 0
            parts[i-1] += 1
    
    new_version = '.'.join(map(str, parts))
    
    # Guardar la nueva versión
    with open(VERSION_FILE, 'w') as f:
        json.dump({'version': new_version}, f, indent=2)
    
    return new_version

def load_template(template_name: str) -> str:
    """Carga una plantilla HTML por su nombre."""
    template_path = TEMPLATES_DIR / f"{template_name}.html"
    try:
        return template_path.read_text(encoding='utf-8')
    except FileNotFoundError:
        raise click.ClickException(f"Plantilla no encontrada: {template_name}")

def load_matches_data(json_path: str) -> Dict:
    """Carga los datos de partidas desde un archivo JSON."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise click.ClickException(f"Archivo no encontrado: {json_path}")
    except json.JSONDecodeError:
        raise click.ClickException(f"Error al decodificar el archivo JSON: {json_path}")

def get_item_icon(item_id: int) -> str:
    """Obtiene la URL del ícono del ítem."""
    if item_id == 0:
        return ""
    # Usar Data Dragon para items
    return f"https://ddragon.leagueoflegends.com/cdn/15.20.1/img/item/{item_id}.png"

def get_champion_icon(champ_id: str) -> str:
    """Obtiene la URL del ícono del campeón."""
    return f"https://ddragon.leagueoflegends.com/cdn/14.20.1/img/champion/{champ_id}.png"
def generate_html(template: str, data: Dict, template_name: str) -> str:
    """Genera el HTML final reemplazando las variables en la plantilla."""
    # Obtener la versión actual
    version = load_version()
    
    # Inicializar el HTML
    html = template
    
    # Debug: Imprimir las claves del diccionario data
    print("Claves en los datos:", data.keys())
    
    # Inicializar variables para estadísticas
    total_matches = 0
    wins = 0
    matches_html = ''
    
    # Procesar las partidas
    matches_key = 'rows' if 'rows' in data else 'matches'
    if matches_key in data and isinstance(data[matches_key], list):
        total_matches = len(data[matches_key])
        print(f"Se encontraron {total_matches} partidas")
        
        for i, match in enumerate(data[matches_key], 1):
            if not isinstance(match, dict):
                print(f"Advertencia: La partida {i} no es un diccionario")
                continue
            # Debug: Imprimir las claves de la partida
            if i == 1:  # Solo mostrar para la primera partida
                print(f"Claves en la partida: {match.keys()}")
            
            try:
                # Determinar si la partida es una victoria o derrota
                win = match.get('win', None)
                if win is True:
                    result_class = 'victory'
                    result_text = 'Victoria'
                    wins += 1
                elif win is False:
                    result_class = 'defeat'
                    result_text = 'Derrota'
                else:
                    result_class = 'remake'
                    result_text = 'Remake'
                
                # Obtener información del campeón
                champ_id = match.get('champ_id', '')
                champ_name = match.get('champ', 'Desconocido')
                champ_icon = get_champion_icon(champ_id) if champ_id else ''
                
                # Obtener KDA
                kda_str = match.get('kda', '0/0/0')
                kda_parts = kda_str.split('/')
                if len(kda_parts) == 3:
                    kills, deaths, assists = map(int, kda_parts)
                else:
                    kills, deaths, assists = 0, 0, 0
                kda = f"{kills}/{deaths}/{assists}"
                
                            # Obtener los ítems
                items = match.get('items', {})
                items_html = '<div class="items-container"><div class="items-row">'  # Inicializar items_html

                try:
                    # Si items es una lista, convertir a diccionario
                    if isinstance(items, list):
                        items_dict = {str(i): item_id for i, item_id in enumerate(items) if item_id and item_id > 0}
                        if len(items) > 6:  # Si hay trinket
                            items_dict['trinket'] = items[6] if len(items) > 6 and items[6] else 0
                        items = items_dict

                    # Mostrar los 6 ítems principales
                    for i in range(6):
                        item_id = items.get(str(i), 0)
                        if item_id and int(item_id) > 0:
                            item_url = get_item_icon(item_id)
                            item_img = f'<img src="{item_url}" class="item-icon" alt="Item {item_id}" loading="lazy">'
                            items_html += f'<div class="item" data-item-id="{item_id}">{item_img}</div>'
                        else:
                            items_html += '<div class="item-empty"></div>'

                    # Añadir el trinket
                    trinket_id = items.get('trinket', items.get('6', 0))
                    if trinket_id and int(trinket_id) > 0:
                        trinket_url = get_item_icon(trinket_id)
                        trinket_img = f'<img src="{trinket_url}" class="item-icon trinket" alt="Trinket {trinket_id}" loading="lazy">'
                        items_html += f'<div class="item trinket" data-item-id="{trinket_id}">{trinket_img}</div>'
                    else:
                        items_html += '<div class="item-empty trinket"></div>'

                    items_html += '</div></div>'  # Cerrar items-row y items-container

                except Exception as e:
                    print(f"Error procesando ítems: {e}")
                    items_html = '<div class="items-container"><div class="items-row">Error al cargar ítems</div></div>'
                
                            # Crear el HTML de la partida
                match_html = f"""
                <tr class="match-row {result_class}">
                    <td class="champ-cell">
                        <img src="{champ_icon}" class="champ-icon" alt="{champ_name}" 
                             onerror="this.onerror=null; this.src='https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/-1.png'"
                             data-champion-id="{champ_id}">
                        <div class="champ-info">
                            <div class="champ-name" title="{champ_name}">{champ_name}</div>
                            <div class="champ-role">{match.get('role', '')} • Lvl {match.get('champ_level', '?')}</div>
                        </div>
                    </td>
                    <td class="kda">
                        <div class="kda-value">{kda}</div>
                        {'<div class="kda-ratio">' + str(match.get('kda_ratio', 0)) + ':1 KDA</div>' if match.get('kda_ratio', 0) > 0 else ''}
                    </td>
                    <td class="items">
                        {items_html}
                        <div class="match-stats">
                            <div class="stat">
                                <span class="stat-value">{int(match.get('total_damage_dealt', 0) or 0):,}</span>
                                <span class="stat-label">Daño</span>
                            </div>
                            <div class="stat">
                                <span class="stat-value">{int(match.get('gold_earned', 0) or 0):,}</span>
                                <span class="stat-label">Oro</span>
                            </div>
                            <div class="stat">
                                <span class="stat-value">{match.get('vision_score', 0) or 0}</span>
                                <span class="stat-label">Visión</span>
                            </div>
                        </div>
                    </td>
                    <td class="result">
                        <span class="pill {result_class}">{result_text}</span>
                        <div class="match-duration">{match.get('game_duration', '0:00')}</div>
                        <div class="match-time" title="{match.get('game_creation', '')}">
                            {match.get('time_ago', 'Hace un momento')}
                        </div>
                    </td>
                </tr>
                """
                matches_html += match_html
                
            except Exception as e:
                print(f"Error procesando partida {i}: {str(e)}")
    
    # Calcular estadísticas generales
    win_rate = (wins / total_matches * 100) if total_matches > 0 else 0
    
    # Reemplazar variables en el HTML
    replacements = {
        '{{matches_rows}}': matches_html if matches_html else '<tr><td colspan="4">No se encontraron partidas</td></tr>',
        '{{generated_at}}': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        '{{version}}': f'v{version}',
        '{{template_name}}': template_name,
        '{{total_matches}}': str(total_matches),
        '{{win_rate}}': f'{win_rate:.1f}%',
        '{{wins}}': str(wins),
        '{{losses}}': str(max(0, total_matches - wins)),
        '{{title}}': 'Estadísticas de Partidas',
        '{{display_name}}': data.get('display_name', 'Invocador'),
        '{{subtitle}}': f'{total_matches} partidas jugadas • {win_rate:.1f}% de victorias',
        '{{profile_icon_id}}': str(data.get('profileIconId', 0)),
        '{{ddragon_version}}': data.get('ddragon_version', 'latest'),
        '{{level}}': str(data.get('level', '?')),
        '{{server}}': data.get('server', data.get('platform', 'N/A')).upper()
    }
    
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)
    
    return html

@cli.command()
@click.option('--read-json', type=click.Path(exists=True), help='Ruta al archivo JSON con datos de partidas')
@click.option('--html-template', default='default', help='Nombre de la plantilla HTML a utilizar')
@click.option('--output', '-o', help='Ruta de salida para el archivo HTML')
def generate(read_json: str, html_template: str, output: Optional[str]):
    """Genera un archivo HTML con estadísticas de partidas."""
    try:
        # Incrementar versión automáticamente
        new_version = increment_version()
        click.echo(f"📦 Versión incrementada a: v{new_version}")
        
        # Cargar plantilla
        template = load_template(html_template)
        
        # Cargar datos de partidas
        matches_data = load_matches_data(read_json)
        
        # Generar HTML
        html_content = generate_html(template, matches_data, html_template)
        
        # Determinar la ruta de salida
        if not output:
            output_dir = OUTPUT_DIR / html_template
            output_dir.mkdir(exist_ok=True)
            output = str(output_dir / f"{matches_data.get('summoner_name', 'output')}-{html_template}.html")
        
        # Guardar el archivo HTML
        with open(output, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        click.echo(f"✅ Archivo generado exitosamente: {click.format_filename(output)}")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        raise click.Abort()

@cli.command()
def version():
    """Muestra la versión actual del CLI."""
    current_version = load_version()
    click.echo(f"Versión actual: v{current_version}")

@cli.command()
def bump_version():
    """Incrementa el número de versión."""
    new_version = increment_version()
    click.echo(f"✅ Versión actualizada a: v{new_version}")

def main():
    """Punto de entrada principal del CLI."""
    cli()

if __name__ == "__main__":
    main()
