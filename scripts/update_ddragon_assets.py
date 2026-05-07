"""Sincroniza assets locales desde Riot Data Dragon.

Data Dragon no requiere RIOT_API_KEY. El rate limiter existe para mantener una
cadencia conservadora cuando se actualizan muchos assets en lote.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from riot_lol_cli import paths
from riot_lol_cli.splash import build_splash_manifest, generate_splash_viewer_html

VERSIONS_URL = "https://ddragon.leagueoflegends.com/api/versions.json"
CDN_BASE = "https://ddragon.leagueoflegends.com/cdn"
SPLASH_BASE = f"{CDN_BASE}/img/champion/splash"
CENTERED_BASE = f"{CDN_BASE}/img/champion/centered"
LOADING_BASE = f"{CDN_BASE}/img/champion/loading"

DEFAULT_LANGUAGE = "es_MX"
DEFAULT_TIMEOUT = 60


class RateLimiter:
    """Rate limiter simple con ventana corta y larga."""

    def __init__(self, per_second: int = 20, per_two_minutes: int = 100) -> None:
        self.per_second = per_second
        self.per_two_minutes = per_two_minutes
        self.one_second: deque[float] = deque()
        self.two_minutes: deque[float] = deque()

    def wait(self) -> None:
        while True:
            now = time.monotonic()
            self._trim(now)

            wait_for = 0.0
            if len(self.one_second) >= self.per_second:
                wait_for = max(wait_for, 1.0 - (now - self.one_second[0]))
            if len(self.two_minutes) >= self.per_two_minutes:
                wait_for = max(wait_for, 120.0 - (now - self.two_minutes[0]))

            if wait_for <= 0:
                self.one_second.append(now)
                self.two_minutes.append(now)
                return

            time.sleep(wait_for + random.uniform(0.02, 0.08))

    def _trim(self, now: float) -> None:
        while self.one_second and now - self.one_second[0] >= 1.0:
            self.one_second.popleft()
        while self.two_minutes and now - self.two_minutes[0] >= 120.0:
            self.two_minutes.popleft()


class DDragonAssetsUpdater:
    def __init__(self, language: str, timeout: int, limiter: RateLimiter) -> None:
        self.language = language
        self.timeout = timeout
        self.limiter = limiter
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "riot-lol-cli-assets-updater/1.0",
                "Referer": "https://ddragon.leagueoflegends.com/",
            }
        )

    def get_json(self, url: str) -> Any:
        self.limiter.wait()
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def download_file(self, url: str, path: Path, force: bool, retries: int = 4) -> bool:
        if path.exists() and not force:
            return False

        path.parent.mkdir(parents=True, exist_ok=True)
        for attempt in range(retries):
            try:
                self.limiter.wait()
                response = self.session.get(url, stream=True, timeout=self.timeout)
                if response.status_code in {403, 404}:
                    return False
                response.raise_for_status()
                with path.open("wb") as handle:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            handle.write(chunk)
                return True
            except requests.RequestException:
                if attempt == retries - 1:
                    raise
                time.sleep((0.5 * (2**attempt)) + random.uniform(0.05, 0.25))
        return False

    def get_latest_version(self) -> str:
        versions = self.get_json(VERSIONS_URL)
        if not isinstance(versions, list) or not versions:
            raise RuntimeError("Respuesta inesperada de Data Dragon versions")
        return str(versions[0])

    def get_champions(self, version: str) -> dict[str, Any]:
        url = f"{CDN_BASE}/{version}/data/en_US/champion.json"
        return self.get_json(url)["data"]

    def get_champion_full(self, version: str, language: str) -> dict[str, Any]:
        url = f"{CDN_BASE}/{version}/data/{language}/championFull.json"
        return self.get_json(url)["data"]

    def get_skins(self, version: str, champion_id: str) -> list[dict[str, Any]]:
        url = f"{CDN_BASE}/{version}/data/en_US/champion/{champion_id}.json"
        return self.get_json(url)["data"][champion_id]["skins"]

    def get_items(self, version: str) -> dict[str, Any]:
        url = f"{CDN_BASE}/{version}/data/{self.language}/item.json"
        return self.get_json(url)["data"]

    def sync_items(self, version: str, force: bool) -> tuple[int, int]:
        items = self.get_items(version)
        items_dir = paths.ASSETS_DIR / "items"
        csv_path = paths.ASSETS_DIR / "data_id_imagen" / "items_ddragon.csv"
        csv_path.parent.mkdir(parents=True, exist_ok=True)

        downloaded = 0
        skipped = 0

        with csv_path.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["id", "nombre", "imagen_url", "explicacion_teorica", "explicacion_tecnica"])

            for item_id in sorted(items, key=lambda value: int(value) if value.isdigit() else value):
                item = items[item_id]
                image_url = f"{CDN_BASE}/{version}/img/item/{item_id}.png"
                stats = item.get("stats") or {}
                stats_text = "; ".join(f"{key}={value}" for key, value in stats.items())
                description = clean_html(item.get("plaintext") or "")

                writer.writerow([item_id, item.get("name", ""), image_url, description, stats_text])

                changed = self.download_file(image_url, items_dir / f"{item_id}.png", force=force)
                if changed:
                    downloaded += 1
                else:
                    skipped += 1

        return downloaded, skipped

    def sync_splash_arts(self, version: str, force: bool, include_chromas: bool) -> tuple[int, int, int]:
        champions = self.get_champion_full(version, "en_US")
        downloaded = 0
        skipped = 0
        failed = 0

        for index, champion in enumerate(champions.values(), start=1):
            champion_id = champion["id"]
            champion_name = champion["name"]
            print(f"[{index}/{len(champions)}] {champion_name}")

            skins = champion.get("skins", [])
            champion_dir = paths.ASSETS_DIR / "splash_arts" / champion_id
            champion_dir.mkdir(parents=True, exist_ok=True)

            for skin in skins:
                if not include_chromas and "parentSkin" in skin:
                    continue

                skin_num = skin["num"]
                skin_name = skin["name"]
                filename = splash_filename(champion_id, skin_name)
                target = champion_dir / filename
                asset_id = splash_asset_id(champion_id)
                urls = [
                    f"{SPLASH_BASE}/{asset_id}_{skin_num}.jpg",
                    f"{CENTERED_BASE}/{asset_id}_{skin_num}.jpg",
                    f"{LOADING_BASE}/{asset_id}_{skin_num}.jpg",
                ]

                if target.exists() and not force:
                    skipped += 1
                    continue

                ok = False
                for url in urls:
                    if self.download_file(url, target, force=True):
                        ok = True
                        break

                if ok:
                    downloaded += 1
                else:
                    failed += 1

        return downloaded, skipped, failed

    def write_splash_catalog(self, version: str, imported_at: str, include_chromas: bool) -> Path:
        """Persiste nombres localizados y metadatos DDragon para el front de galeria."""
        english_champions = self.get_champion_full(version, "en_US")
        localized_champions = (
            english_champions if self.language == "en_US" else self.get_champion_full(version, self.language)
        )

        champions: list[dict[str, Any]] = []
        images: list[dict[str, Any]] = []

        for champion_id, champion_en in sorted(english_champions.items()):
            champion_localized = localized_champions.get(champion_id, champion_en)
            champions.append(
                {
                    "id": champion_id,
                    "name": champion_localized.get("name") or champion_en.get("name") or champion_id,
                    "nameEn": champion_en.get("name") or champion_id,
                }
            )

            localized_skins = {skin.get("num"): skin for skin in champion_localized.get("skins", []) if "num" in skin}
            for skin_en in champion_en.get("skins", []):
                if not include_chromas and "parentSkin" in skin_en:
                    continue

                skin_num = skin_en["num"]
                localized_skin = localized_skins.get(skin_num, skin_en)
                skin_name_en = skin_display_name(skin_en.get("name", "default"), localized=False)
                skin_name = skin_display_name(localized_skin.get("name", skin_en.get("name", "default")))

                images.append(
                    {
                        "championId": champion_id,
                        "skinNum": skin_num,
                        "file": splash_filename(champion_id, skin_en.get("name", "default")),
                        "skinName": skin_name,
                        "skinNameEn": skin_name_en,
                        "ddragonVersion": version,
                    }
                )

        catalog = {
            "ddragonVersion": version,
            "assetsImportedAt": imported_at,
            "locale": self.language,
            "champions": champions,
            "images": images,
        }

        catalog_path = paths.DATA_DIR / "ddragon-splash-catalog.json"
        catalog_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return catalog_path


def clean_html(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value).strip()


def splash_filename(champion_id: str, skin_name: str) -> str:
    if skin_name == "default":
        return f"{champion_id}_Classic.jpg"
    safe_name = "".join(char for char in skin_name if char.isalnum() or char in (" ", "-", "_")).strip()
    safe_name = safe_name.replace(" ", "_")
    return f"{champion_id}_{safe_name}.jpg"


def splash_asset_id(champion_id: str) -> str:
    aliases = {
        "Fiddlesticks": "FiddleSticks",
    }
    return aliases.get(champion_id, champion_id)


def skin_display_name(skin_name: str, localized: bool = True) -> str:
    if skin_name == "default":
        return "Clasica" if localized else "Classic"
    return skin_name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Actualiza items y splash arts desde Data Dragon.")
    parser.add_argument("--version", help="Version Data Dragon. Default: ultima publicada.")
    parser.add_argument(
        "--language", default=DEFAULT_LANGUAGE, help="Locale para items y catalogo splash. Default: es_MX."
    )
    parser.add_argument("--skip-items", action="store_true", help="No actualizar items.")
    parser.add_argument("--skip-splash", action="store_true", help="No actualizar splash arts.")
    parser.add_argument("--include-chromas", action="store_true", help="Intentar descargar chromas como splash arts.")
    parser.add_argument("--force-items", action="store_true", help="Re-descargar iconos de items existentes.")
    parser.add_argument("--force-splash", action="store_true", help="Re-descargar splash arts existentes.")
    parser.add_argument(
        "--skip-gallery-regenerate",
        action="store_true",
        help="No regenerar data/splash-manifest.json ni outputs/splash-viewer.html luego de splash.",
    )
    parser.add_argument("--per-second", type=int, default=20, help="Requests maximas por segundo.")
    parser.add_argument("--per-two-minutes", type=int, default=100, help="Requests maximas cada 2 minutos.")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    limiter = RateLimiter(per_second=args.per_second, per_two_minutes=args.per_two_minutes)
    updater = DDragonAssetsUpdater(language=args.language, timeout=args.timeout, limiter=limiter)

    version = args.version or updater.get_latest_version()
    print(f"Data Dragon version: {version}")
    print(f"Locale items/catalogo splash: {args.language}")
    imported_at = datetime.now().isoformat(timespec="seconds")

    if not args.skip_items:
        downloaded, skipped = updater.sync_items(version, force=args.force_items)
        print(f"Items: {downloaded} descargados/actualizados, {skipped} existentes.")

    if not args.skip_splash:
        downloaded, skipped, failed = updater.sync_splash_arts(
            version,
            force=args.force_splash,
            include_chromas=args.include_chromas,
        )
        print(f"Splash arts: {downloaded} descargados/actualizados, {skipped} existentes, {failed} fallidos.")

        catalog_path = updater.write_splash_catalog(
            version,
            imported_at=imported_at,
            include_chromas=args.include_chromas,
        )
        print(f"Catalogo splash DDragon: {catalog_path}")

        if not args.skip_gallery_regenerate:
            manifest = build_splash_manifest(
                ddragon_version=version,
                assets_imported_at=imported_at,
                asset_locale=args.language,
            )
            output_path = paths.OUTPUT_DIR / "splash-viewer.html"
            output_path.write_text(generate_splash_viewer_html(manifest), encoding="utf-8")
            print(f"Galeria regenerada: {output_path}")


if __name__ == "__main__":
    main()
