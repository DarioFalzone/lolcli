"""Script para ingerir el patch notes breakdown de Mobalytics 26.10.

Parsea el markdown proporcionado y lo agrega como un PatchEnrichment
al patch 26.10. Remueve navegación y links de terceros innecesarios.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

# Content limpio — solo el análisis de cambios (sin navegación UI)
MOBALYTICS_BREAKDOWN_26_10 = """# League of Legends 26.10 Patch Notes Breakdown

Welcome to our patch notes breakdown for **League of Legends Season 26.10 (Split 2 for LoL)**!

Let's break down all the new changes in LoL coming this week.

We recommend following along with the official patch notes since we won't be listing all the specific stat changes, but rather focusing on the impact of the changes and the champions' place in the current meta.

If you're wondering how these changes will affect the meta, check out our LoL champion tier list!

## Champion Changes

### Ambessa (change)
- Her Q max health damage is increased, and the damage it deals to monsters is reduced.
- Her Ultimate healing is increased, which will give Ambessa a bit of extra sustain in team fights. The healing it provides versus monsters is reduced, though.
- These changes are going to help Ambessa in the Top role, but reduce her effectiveness moving forward in the Jungle role due to the monster damage nerfs.
- Ambessa had a 46.7% win rate on patch 26.09.

### Anivia (nerf)
- Her base armor is reduced, and the armor growth per level is reduced. These changes are going to make Anivia weaker against AD assassins in the Mid lane, like Zed or Yasuo.
- Anivia had a 51% win rate on patch 26.09.

### Ashe (buff)
- Her Q AD ratio is increased. This is going to make Ashe deal more damage in trades, especially in the latter parts of the game.
- Ashe had a 52.2% win rate on patch 26.09.

### Galio (change)
- Galio's Q mana cost is reduced, which is going to help him clear waves and poke the enemy down.
- His E damage has changed as well. The AP ratio is increased.
- Galio's Ultimate now scales with bonus magic resistance.
- These changes are interesting, and it will be good to see how they play out for Galio in the future.
- Galio had a 48.7% win rate on patch 26.09.

### Lee Sin (change)
- Lee's W base shield is reduced, and the cooldown is reduced from 12 seconds to 7, which is nice.
- It no longer reduces cooldown if it's a champion he uses it on. Instead, he now also gains a shield if he uses it on a minion or ward.
- Lee's E damage is nerfed as well, which is going to reduce his clear speed and trading power.
- It will be interesting to see how these changes play out for Lee Sin. We could see him being played in a solo lane again soon.
- Lee Sin had a 49.9% win rate on patch 26.09.

### Naafiri (nerf)
- Naafiri's Q damage from packmates is reduced vs monsters. This is going to reduce Naafiri's strength in the Mid and Jungle roles.
- Her Ultimate damage is also reduced, which is going to negatively impact her all-ins post 6 and reduce her kill pressure in lane.
- These changes will make Naafiri weaker in both the Mid and Jungle roles.
- Naafiri had a 50.3% win rate on patch 26.09.

### Quinn (buff)
- Her Passive now deals extra damage against monsters.
- Quinn's Q damage vs monsters is increased.
- Her Ultimate mana cost is reduced.
- All these changes to Quinn tell us Riot wants people to play Quinn in the Jungle role moving forward.
- Quinn had a 50.5% win rate on patch 26.09.

### Shyvana (nerf)
- Her health growth per level is lower; this will make her weaker as the game progresses.
- The cooldown on her W is increased and the shield is nerfed, which is going to make her weaker in those 1v1s.
- These changes will make Shyvana weaker in the Jungle role moving forward.
- Shyvana had a 52.4% win rate on patch 26.09.

### Wukong (buff)
- His W damage and duration are increased.
- Wukong's E bonus attack speed is increased.
- These changes to Wukong are good. They will make him stronger in the Jungle and Top lane, and we will see him more often. He will be a bigger threat in the upcoming patches.
- Wukong had a 49.4% win rate on patch 26.09.

### Zed (nerf)
- Zed's Passive health ratio reduction is reduced.
- His E damage and AD ratio are also decreased. These changes will make Zed weaker in the Jungle and Mid Lane roles going forward.
- Zed had a 51.9% win rate on patch 26.09.

### Zeri (buff)
- Zeri's Q bonus AD is increased, meaning her all-in and trading damage will increase too.
- These are some good changes to Zeri as she is relatively weak compared to many other ADCs in the current meta.
- Zeri had a 47.4% win rate on patch 26.09.

## Items

### Doran's Bow
- The AD is increased from 6 to 8.

### Doran's Helm
- It now gives a little more HP.

### Gluttonous Graves
- The cost has increased to 1000 gold.
- Slay Omnivamp per stack is reduced, but the max stacks are increased to 10 from 6.

### Immortal Path
- Slay Omnivamp per stack is reduced, but the max stacks are increased to 10 from 6.

### Lich Bane
- It gives more movement speed now.
- The Spellblade AP ratio is increased.

### Voltaic Cyclosword
- The cost is increased by 100g.

## Runes

### Deathfire Touch
- The base damage is changed.

### Stormraider's Surge
- Bonus movement speed duration is increased.
"""


def create_patch_enrichment() -> dict:
    """Crea el payload de PatchEnrichment para Mobalytics Breakdown."""
    content_hash = hashlib.sha256(MOBALYTICS_BREAKDOWN_26_10.encode("utf-8")).hexdigest()

    return {
        "source": "mobalytics_breakdown",
        "source_url": "https://mobalytics.gg/lol/guides/patch-notes-breakdown",
        "fetched_at": "2026-05-12T19:10:21Z",
        "content_hash": content_hash,
        "payload": {
            "title": "League of Legends 26.10 Patch Notes Breakdown",
            "content_markdown": MOBALYTICS_BREAKDOWN_26_10,
            "section_count": 4,  # Champion Changes, Items, Runes, metadata
            "published_at": "2026-05-12T00:00:00Z",
            "champions_mentioned": [
                "Ambessa", "Anivia", "Ashe", "Galio", "Lee Sin",
                "Naafiri", "Quinn", "Shyvana", "Wukong", "Zed", "Zeri"
            ],
            "items_mentioned": [
                "Doran's Bow", "Doran's Helm", "Gluttonous Graves",
                "Immortal Path", "Lich Bane", "Voltaic Cyclosword"
            ],
            "runes_mentioned": ["Deathfire Touch", "Stormraider's Surge"],
        },
        "error": None,
    }


def main() -> None:
    """Ingiere el breakdown y lo agrega a 26.10."""
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data" / "patch_notes"
    by_patch_dir = data_dir / "normalized" / "by_patch"
    sources_dir = data_dir / "sources"

    # Asegurar que los directorios existan
    by_patch_dir.mkdir(parents=True, exist_ok=True)
    sources_dir.mkdir(parents=True, exist_ok=True)

    # Patch 26.10 (asumiendo que existe)
    patch_file = by_patch_dir / "26.10_es-es.json"
    if not patch_file.exists():
        print(f"⚠️  {patch_file} no existe. Creando estructura básica...")
        patch_file.parent.mkdir(parents=True, exist_ok=True)

    # Leer el patch existente o crear uno nuevo
    if patch_file.exists():
        with open(patch_file, encoding="utf-8") as f:
            patch_note = json.load(f)
    else:
        # Crear un patch note minimal si no existe
        patch_note = {
            "publisher": "riot",
            "game": "lol",
            "channel": "site",
            "source_locale": "es-es",
            "patch_version": "26.10",
            "title": "Notas de la versión 26.10",
            "canonical_url": "https://www.leagueoflegends.com/es-es/news/game-updates/league-of-legends-patch-26-10-notes",
            "published_at": "2026-05-12T00:00:00Z",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "content_hash": "placeholder",
            "summary": None,
            "sections": [],
            "assets": [],
            "scraper_version": "patch_notes_v2.0.0",
            "raw_html_ref": None,
            "enrichments": [],
        }

    # Crear y agregar el enrichment
    enrichment = create_patch_enrichment()
    patch_note["enrichments"].append(enrichment)

    # Guardar el patch actualizado
    with open(patch_file, "w", encoding="utf-8") as f:
        json.dump(patch_note, f, indent=2, ensure_ascii=False)

    # Guardar el contenido raw en sources/ si es deseable
    sources_breakdown_dir = sources_dir / "mobalytics_breakdown"
    sources_breakdown_dir.mkdir(parents=True, exist_ok=True)
    breakdown_file = sources_breakdown_dir / "26.10.json"

    with open(breakdown_file, "w", encoding="utf-8") as f:
        json.dump(enrichment, f, indent=2, ensure_ascii=False)

    print("OK - Mobalytics Breakdown 26.10 ingerido exitosamente")
    print(f"   Patch: {patch_file}")
    print(f"   Source: {breakdown_file}")
    print(f"   Content hash: {enrichment['content_hash'][:16]}...")


if __name__ == "__main__":
    main()
