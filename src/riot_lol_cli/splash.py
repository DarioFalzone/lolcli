import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from PIL import Image

from riot_lol_cli import paths
from riot_lol_cli.versioning import get_version


def extract_color_palette(img_path: Path) -> dict[str, Any]:
    """Extrae una paleta mínima para el visor de splash arts."""
    try:
        img = Image.open(img_path)
        img = img.convert("RGB")
        img.thumbnail((150, 150))

        pixels = list(img.getdata())
        color_counts = Counter(pixels)
        top_colors = color_counts.most_common(5)

        palette = [f"#{r:02x}{g:02x}{b:02x}" for (r, g, b), _ in top_colors]
        primary = palette[0] if palette else "#808080"
        return {"primary": primary, "palette": palette}
    except OSError:
        return {"primary": "#808080", "palette": ["#808080"]}


def detect_badges(skin_name: str) -> list[str]:
    badges = []
    name_lower = skin_name.lower()

    badge_keywords = {
        "Prestige": ["prestige"],
        "Legacy": ["legacy"],
        "Mythic": ["mythic"],
        "Limited": ["limited"],
        "Exclusive": ["exclusive", "pax"],
        "Championship": ["championship"],
        "Victorious": ["victorious"],
        "Hextech": ["hextech"],
        "Ultimate": ["ultimate"],
        "Legendary": ["legendary"],
    }

    for badge, keywords in badge_keywords.items():
        if any(keyword in name_lower for keyword in keywords):
            badges.append(badge)

    return badges


def estimate_release_year(skin_name: str) -> Optional[int]:
    match = re.search(r"20\d{2}", skin_name)
    if match:
        return int(match.group())

    year_hints = {
        2024: ["arcane 2024", "heavenscale", "primordian"],
        2023: ["faerie court", "soul fighter", "broken covenant"],
        2022: ["crystal rose", "anima squad", "star guardian 2022"],
        2021: ["crime city nightmare", "space groove", "sentinels"],
        2020: ["spirit blossom", "psyops", "k/da all out"],
        2019: ["true damage", "project 2019", "arcade 2019"],
        2018: ["k/da", "odyssey", "pool party 2018"],
    }

    name_lower = skin_name.lower()
    for year, hints in year_hints.items():
        if any(hint in name_lower for hint in hints):
            return year

    return None


def build_splash_manifest() -> dict[str, Any]:
    """Escanea assets/splash_arts y genera data/splash-manifest.json."""
    splash_dir = paths.ASSETS_DIR / "splash_arts"
    if not splash_dir.exists():
        raise FileNotFoundError(f"Directorio no encontrado: {splash_dir}")

    champions: dict[str, dict[str, Any]] = {}
    images: list[dict[str, Any]] = []

    for champ_dir in sorted(splash_dir.iterdir()):
        if not champ_dir.is_dir():
            continue

        champ_id = champ_dir.name
        files = list(champ_dir.glob("*.jpg")) + list(champ_dir.glob("*.png"))
        if not files:
            continue

        champions[champ_id] = {
            "id": champ_id,
            "name": champ_id,
            "count": len(files),
        }

        for file_path in sorted(files):
            rel_path = f"../assets/splash_arts/{champ_id}/{file_path.name}"
            skin_name = file_path.stem.replace(f"{champ_id}_", "")
            colors = extract_color_palette(file_path)
            badges = detect_badges(skin_name)
            release_year = estimate_release_year(skin_name)

            image_data: dict[str, Any] = {
                "championId": champ_id,
                "file": file_path.name,
                "relPath": rel_path,
                "skinName": skin_name,
                "colors": colors,
                "badges": badges,
            }
            if release_year:
                image_data["releaseYear"] = release_year

            images.append(image_data)

    manifest = {
        "champions": list(champions.values()),
        "images": images,
        "generatedAt": datetime.now().isoformat(),
        "version": get_version(),
        "totalChampions": len(champions),
        "totalImages": len(images),
    }

    manifest_path = paths.DATA_DIR / "splash-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def load_splash_manifest() -> dict[str, Any]:
    manifest_path = paths.DATA_DIR / "splash-manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(
            "Manifest no encontrado. Ejecutá primero: python -m riot_lol_cli.cli build-splash-manifest"
        )
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def generate_splash_viewer_html(manifest: dict[str, Any]) -> str:
    template_path = paths.TEMPLATES_DIR / "splash-viewer.html"
    if not template_path.exists():
        raise FileNotFoundError("Plantilla no encontrada: splash-viewer")

    html = template_path.read_text(encoding="utf-8")
    replacements = {
        "{{version}}": get_version(),
        "{{generated_at}}": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "{{total_champions}}": str(manifest.get("totalChampions", 0)),
        "{{total_images}}": str(manifest.get("totalImages", 0)),
        "{{manifest_url}}": "../data/splash-manifest.json",
    }

    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    inline_manifest = json.dumps(manifest, ensure_ascii=False)
    inline_script = f"<script>window.__INLINE_MANIFEST__ = {inline_manifest};</script>"
    return html.replace("<!-- INLINE_MANIFEST -->", inline_script)
