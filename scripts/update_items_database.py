"""Fetch latest Data Dragon item.json (en_US + es_ES) and build a merged DB.

- Resuelve la version actual desde versions.json.
- Pide en_US y es_ES.
- Genera data/items/database.json con: id, name_en, name_es, version, gold,
  tags, maps, stats, image, deprecated flag.
- Marca como deprecated los items presentes en assets/items/<id>.png o en
  assets/data_id_imagen/items_ddragon.csv pero ausentes en la version actual.
- Descarga PNG faltantes (items nuevos) a assets/items/.

Ejecutar con: python scripts/update_items_database.py
"""

from __future__ import annotations

import csv
import json
import sys
import time
import warnings
from pathlib import Path

import requests

try:
    from urllib3.exceptions import InsecureRequestWarning
    warnings.simplefilter("ignore", InsecureRequestWarning)
except ImportError:
    pass

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data" / "items"
ASSETS_DIR = REPO_ROOT / "assets" / "items"
LEGACY_CSV = REPO_ROOT / "assets" / "data_id_imagen" / "items_ddragon.csv"

DDRAGON_BASE = "https://ddragon.leagueoflegends.com"
VERSIONS_URL = f"{DDRAGON_BASE}/api/versions.json"
SLEEP_BETWEEN_DOWNLOADS = 0.05

_SSL_VERIFY = True


def _request_get(url: str, **kwargs) -> requests.Response:
    """Wrapper que cae a verify=False si el bundle local no tiene el CA."""
    global _SSL_VERIFY
    try:
        return requests.get(url, verify=_SSL_VERIFY, timeout=30, **kwargs)
    except requests.exceptions.SSLError:
        if _SSL_VERIFY:
            print(
                "  WARNING: SSL verification failed; falling back to verify=False.\n"
                "  Data Dragon es un CDN publico, no hay credenciales en juego.\n"
                "  Para arreglar el bundle local: pip install --upgrade certifi",
                file=sys.stderr,
            )
            _SSL_VERIFY = False
            return requests.get(url, verify=False, timeout=30, **kwargs)
        raise


def fetch_json(url: str) -> dict:
    resp = _request_get(url)
    resp.raise_for_status()
    return resp.json()


def latest_version() -> str:
    versions = fetch_json(VERSIONS_URL)
    if not versions or not isinstance(versions, list):
        raise RuntimeError("versions.json devolvio respuesta vacia o invalida")
    return versions[0]


def fetch_items(version: str, lang: str) -> dict:
    url = f"{DDRAGON_BASE}/cdn/{version}/data/{lang}/item.json"
    print(f"  Fetching {lang} -> {url}")
    return fetch_json(url)


def collect_legacy_ids() -> set[int]:
    """IDs presentes en el CSV viejo o en assets/items/*.png."""
    ids: set[int] = set()
    if LEGACY_CSV.exists():
        with open(LEGACY_CSV, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    ids.add(int(row["id"]))
                except (KeyError, ValueError):
                    continue
    if ASSETS_DIR.exists():
        for png in ASSETS_DIR.glob("*.png"):
            try:
                ids.add(int(png.stem))
            except ValueError:
                continue
    return ids


def download_missing_icons(items: dict, version: str) -> tuple[int, int]:
    """Descarga PNG de items nuevos. Retorna (downloaded, skipped)."""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    downloaded = 0
    skipped = 0
    for item_id in items.keys():
        png_path = ASSETS_DIR / f"{item_id}.png"
        if png_path.exists():
            skipped += 1
            continue
        url = f"{DDRAGON_BASE}/cdn/{version}/img/item/{item_id}.png"
        try:
            resp = _request_get(url)
            resp.raise_for_status()
            png_path.write_bytes(resp.content)
            downloaded += 1
            print(f"    + {item_id}.png ({len(resp.content)} bytes)")
            time.sleep(SLEEP_BETWEEN_DOWNLOADS)
        except requests.RequestException as exc:
            print(f"    ! {item_id}: {exc}", file=sys.stderr)
    return downloaded, skipped


def build_database(version: str, en_data: dict, es_data: dict) -> dict:
    """Mezcla en_US y es_ES en un schema simple para la SPA."""
    en_items = en_data.get("data", {})
    es_items = es_data.get("data", {})
    legacy_ids = collect_legacy_ids()
    current_ids = {int(k) for k in en_items.keys()}

    merged: list[dict] = []
    for raw_id, en in en_items.items():
        item_id = int(raw_id)
        es = es_items.get(raw_id, {})
        gold = en.get("gold") or {}
        merged.append(
            {
                "id": item_id,
                "name_en": en.get("name", ""),
                "name_es": es.get("name", en.get("name", "")),
                "plaintext_en": en.get("plaintext") or "",
                "plaintext_es": es.get("plaintext") or "",
                "tags": en.get("tags") or [],
                "stats": en.get("stats") or {},
                "gold_total": gold.get("total", 0),
                "gold_base": gold.get("base", 0),
                "gold_sell": gold.get("sell", 0),
                "purchasable": bool(gold.get("purchasable", False)),
                "depth": en.get("depth", 1),
                "from": [int(x) for x in (en.get("from") or []) if str(x).isdigit()],
                "into": [int(x) for x in (en.get("into") or []) if str(x).isdigit()],
                "maps": [k for k, v in (en.get("maps") or {}).items() if v],
                "image": (en.get("image") or {}).get("full", f"{item_id}.png"),
                "deprecated": False,
            }
        )

    deprecated_ids = sorted(legacy_ids - current_ids)
    for item_id in deprecated_ids:
        merged.append(
            {
                "id": item_id,
                "name_en": f"(deprecated #{item_id})",
                "name_es": f"(obsoleto #{item_id})",
                "plaintext_en": "",
                "plaintext_es": "",
                "tags": ["Deprecated"],
                "stats": {},
                "gold_total": 0,
                "gold_base": 0,
                "gold_sell": 0,
                "purchasable": False,
                "depth": 1,
                "from": [],
                "into": [],
                "maps": [],
                "image": f"{item_id}.png",
                "deprecated": True,
            }
        )

    merged.sort(key=lambda i: (i["deprecated"], i["id"]))

    return {
        "version": version,
        "source": f"{DDRAGON_BASE}/cdn/{version}/data/<lang>/item.json",
        "lang_supported": ["en_US", "es_ES"],
        "total_count": len(merged),
        "current_count": len(current_ids),
        "deprecated_count": len(deprecated_ids),
        "items": merged,
    }


def write_database(database: dict) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_DIR / "database.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(database, f, ensure_ascii=False, indent=2)
    return out_path


def main() -> int:
    print("Fetching latest Data Dragon version...")
    version = latest_version()
    print(f"  Latest: {version}\n")

    print("Fetching item.json (en_US + es_ES)...")
    en_data = fetch_items(version, "en_US")
    es_data = fetch_items(version, "es_ES")
    print(f"  EN items: {len(en_data.get('data', {}))}")
    print(f"  ES items: {len(es_data.get('data', {}))}\n")

    print("Building merged database...")
    database = build_database(version, en_data, es_data)
    out_path = write_database(database)
    print(f"  Wrote {out_path}")
    print(f"  Total: {database['total_count']}  current: {database['current_count']}  deprecated: {database['deprecated_count']}\n")

    print("Downloading missing PNG icons...")
    downloaded, skipped = download_missing_icons(en_data["data"], version)
    print(f"  Downloaded: {downloaded}  already-on-disk: {skipped}\n")

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
