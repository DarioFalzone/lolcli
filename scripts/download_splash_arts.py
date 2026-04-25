"""
Script para descargar todos los splash arts de League of Legends
Usa Data Dragon CDN de Riot Games (no requiere API key)
"""

import argparse
import os
import random
import time

import requests

from riot_lol_cli import paths
from riot_lol_cli.settings import get_ddragon_version

# Configuración
DATA_DRAGON_VERSION = get_ddragon_version()
BASE_URL = f"https://ddragon.leagueoflegends.com/cdn/{DATA_DRAGON_VERSION}"
SPLASH_BASE_URL = "https://ddragon.leagueoflegends.com/cdn/img/champion/splash"
CENTERED_BASE_URL = "https://ddragon.leagueoflegends.com/cdn/img/champion/centered"
LOADING_BASE_URL = "https://ddragon.leagueoflegends.com/cdn/img/champion/loading"
OUTPUT_DIR = str(paths.ASSETS_DIR / "splash_arts")


def get_latest_version():
    """Obtiene la versión más reciente de Data Dragon"""
    try:
        response = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
        versions = response.json()
        return versions[0]
    except Exception as e:
        print(f"⚠️ Error obteniendo última versión: {e}")
        return DATA_DRAGON_VERSION


def get_all_champions(version):
    """Obtiene la lista completa de campeones"""
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['data']
    except Exception as e:
        print(f"❌ Error obteniendo lista de campeones: {e}")
        return {}


def get_champion_skins(champion_id, version):
    """Obtiene información detallada de un campeón incluyendo todas sus skins"""
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion/{champion_id}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['data'][champion_id]['skins']
    except Exception as e:
        print(f"⚠️ Error obteniendo skins de {champion_id}: {e}")
        return []


def download_image(url, filepath, max_retries=5, base_delay=0.5):
    """Descarga una imagen desde una URL"""
    for attempt in range(max_retries):
        try:
            response = requests.get(
                url,
                stream=True,
                headers={
                    "User-Agent": "riot-lol-cli/1.0",
                    "Referer": "https://ddragon.leagueoflegends.com/",
                },
                timeout=60,
            )
            if response.status_code in (403, 404):
                return False
            response.raise_for_status()
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"❌ Error descargando {url}: {e}")
                return False
            sleep_s = base_delay * (2 ** attempt) + random.uniform(0, 0.25)
            time.sleep(sleep_s)


def download_with_fallback(urls, filepath, max_retries=5):
    for url in urls:
        if download_image(url, filepath, max_retries=max_retries):
            return True
    return False


def download_all_splash_arts(image_delay=0.2, champion_delay=0.4, max_retries=5):
    """Descarga todos los splash arts organizados por campeón"""
    print("🎨 Descargador de Splash Arts de League of Legends")
    print("=" * 60)
    
    # Obtener última versión
    print("\n📦 Obteniendo última versión de Data Dragon...")
    version = get_latest_version()
    print(f"✅ Versión: {version}")
    
    # Obtener todos los campeones
    print("\n📋 Obteniendo lista de campeones...")
    champions = get_all_champions(version)
    total_champions = len(champions)
    print(f"✅ Encontrados {total_champions} campeones")
    
    # Estadísticas
    total_downloaded = 0
    total_failed = 0
    
    # Descargar splash arts
    print("\n🖼️ Descargando splash arts...")
    print("-" * 60)
    
    for idx, (champion_key, champion_data) in enumerate(champions.items(), 1):
        champion_id = champion_data['id']
        champion_name = champion_data['name']
        
        print(f"\n[{idx}/{total_champions}] {champion_name}")
        
        # Obtener todas las skins del campeón
        skins = get_champion_skins(champion_id, version)
        
        if not skins:
            print("  ⚠️ No se encontraron skins")
            continue
        
        # Crear carpeta para el campeón
        champion_folder = os.path.join(OUTPUT_DIR, champion_id)
        os.makedirs(champion_folder, exist_ok=True)
        
        # Descargar cada skin
        for skin in skins:
            skin_num = skin['num']
            skin_name = skin['name']
            
            # URL del splash art
            splash_url = f"{SPLASH_BASE_URL}/{champion_id}_{skin_num}.jpg"
            centered_url = f"{CENTERED_BASE_URL}/{champion_id}_{skin_num}.jpg"
            loading_url = f"{LOADING_BASE_URL}/{champion_id}_{skin_num}.jpg"
            
            # Nombre del archivo
            if skin_name == "default":
                filename = f"{champion_id}_Classic.jpg"
            else:
                safe_name = "".join(c for c in skin_name if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_name = safe_name.replace(' ', '_')
                filename = f"{champion_id}_{safe_name}.jpg"
            
            filepath = os.path.join(champion_folder, filename)
            
            # Verificar si ya existe
            if os.path.exists(filepath):
                print(f"  ⏭️ Ya existe: {skin_name}")
                total_downloaded += 1
                continue
            
            # Descargar
            print(f"  ⬇️ Descargando: {skin_name}...", end=" ")
            if download_with_fallback([splash_url, centered_url, loading_url], filepath, max_retries=max_retries):
                print("✅")
                total_downloaded += 1
            else:
                print("❌")
                total_failed += 1
            
            time.sleep(image_delay)
        
        time.sleep(champion_delay)
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    print(f"✅ Splash arts descargados: {total_downloaded}")
    print(f"❌ Fallos: {total_failed}")
    print(f"📁 Ubicación: {os.path.abspath(OUTPUT_DIR)}")
    print("\n✨ ¡Descarga completada!")


def download_single_champion(champion_name, image_delay=0.2, max_retries=5):
    """Descarga los splash arts de un solo campeón"""
    print(f"🎨 Descargando splash arts de {champion_name}...")
    
    version = get_latest_version()
    champions = get_all_champions(version)
    
    # Buscar campeón
    champion_data = None
    champion_id = None
    
    for key, data in champions.items():
        if data['name'].lower() == champion_name.lower() or data['id'].lower() == champion_name.lower():
            champion_data = data
            champion_id = data['id']
            break
    
    if not champion_data:
        print(f"❌ Campeón '{champion_name}' no encontrado")
        return
    
    print(f"✅ Encontrado: {champion_data['name']}")
    
    # Obtener skins
    skins = get_champion_skins(champion_id, version)
    
    # Crear carpeta
    champion_folder = os.path.join(OUTPUT_DIR, champion_id)
    os.makedirs(champion_folder, exist_ok=True)
    
    total = 0
    for skin in skins:
        skin_num = skin['num']
        skin_name = skin['name']
        
        if skin_name == "default":
            filename = f"{champion_id}_Classic.jpg"
        else:
            safe_name = "".join(c for c in skin_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')
            filename = f"{champion_id}_{safe_name}.jpg"
        
        filepath = os.path.join(champion_folder, filename)
        
        if os.path.exists(filepath):
            print(f"⏭️ Ya existe: {skin_name}")
            total += 1
            continue
        
        print(f"⬇️ Descargando: {skin_name}...", end=" ")
        if download_with_fallback([
            f"{SPLASH_BASE_URL}/{champion_id}_{skin_num}.jpg",
            f"{CENTERED_BASE_URL}/{champion_id}_{skin_num}.jpg",
            f"{LOADING_BASE_URL}/{champion_id}_{skin_num}.jpg",
        ], filepath, max_retries=max_retries):
            print("✅")
            total += 1
        else:
            print("❌")
        time.sleep(image_delay)
    
    print(f"\n✨ Descargados {total} splash arts en: {os.path.abspath(champion_folder)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("champion", nargs="*", help="Nombre del campeón (opcional)")
    parser.add_argument("--image-delay", type=float, default=0.2)
    parser.add_argument("--champion-delay", type=float, default=0.4)
    parser.add_argument("--max-retries", type=int, default=5)
    args = parser.parse_args()
    
    if args.champion:
        champion_name = " ".join(args.champion)
        download_single_champion(champion_name, image_delay=args.image_delay, max_retries=args.max_retries)
    else:
        download_all_splash_arts(image_delay=args.image_delay, champion_delay=args.champion_delay, max_retries=args.max_retries)
