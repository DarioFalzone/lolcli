# Jungle Metagame Dashboard

**Status:** Active  
**Type:** FastAPI + SPA  
**Port:** 8003  
**URL:** http://localhost:8003

## Overview

Curated jungle champion metagame tracker. Displays current patch tier lists (S/A/B/C) with:
- Win rates, pick rates, ban rates
- Core recommended items
- Primary keystone rune
- Brief explanation of why each champion is strong (buff or item synergy)

Data is manually curated from professional sources (SkillCapped, U.GG) and can be extended with automatic scrapers. Item builds use local Data Dragon IDs from `assets/items/<id>.png`.

## Features

- **Tier Lists**: S/A/B/C organized by patch
- **Champion Cards**: Icon + stats + items + reasoning
- **Filtering**: Tab-based tier filtering
- **Responsive**: Mobile-friendly grid layout
- **Design System**: Dark navy theme with ARC gold accents

## Quick Start

```powershell
# Option 1: Launcher script (Windows)
.\scripts\bat\jungle_meta.bat

# Option 2: Direct Python
python -m riot_lol_cli.jungle_meta.server
```

Then open http://localhost:8003

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Serve SPA frontend |
| `/health` | GET | Server health + patch info |
| `/api/v1/jungle/tier-list` | GET | All champions grouped by tier |
| `/api/v1/jungle/tier/{tier}` | GET | Champions in specific tier (S/A/B/C) |
| `/api/v1/jungle/champion/{champion_id}` | GET | Detail for specific champion |

## Data Structure

Patch data lives in `data/jungle_meta/patch_XX.XX.json`:

```json
{
  "patch": "26.09",
  "date_updated": "2026-05-08T00:00:00Z",
  "jungle_champions": [
    {
      "id": "XinZhao",
      "display_name": "Xin Zhao",
      "tier": "S",
      "winrate": 54.2,
      "pickrate": 12.5,
      "banrate": 8.3,
      "primary_reason": "item_synergy",
      "reason_text": "Hail of Blades + AD item buffs. Lethal early game tempo.",
      "core_builds": [
        {"label": "Statikk Rush (DPS spike)", "items": [3087, 2510, 4633]},
        {"label": "Dusk and Dawn First (Survivability)", "items": [2510, 4633, 3087]}
      ],
      "core_rune": {"name": "Hail of Blades", "tree": "Inspiration"},
      "playstyle": "Early game aggression, objective control."
    },
    // ... more champions
  ]
}
```

## Frontend

**Location**: `src/riot_lol_cli/jungle_meta/static/`
- `index.html` — SPA shell + inline CSS
- Uses **DDragon CDN** for champion icons and local `/items/{id}.png` for item icons
- JavaScript vanilla (no frameworks)

**Design**:
- Dark navy background (`#010a13`)
- ARC gold accents (`#c89b3c`)
- Tier colors: S (gold), A (cyan), B (gray), C (red)

## Updating Patch Data

1. Edit `data/jungle_meta/patch_XX.XX.json`
2. Restart server
3. Browser caches may need clearing

Example new patch:
```bash
cp data/jungle_meta/patch_26.09.json data/jungle_meta/patch_26.10.json
# Edit patch number and champions
```

## Future Enhancements

- [ ] Auto-scraper for U.GG / SkillCapped
- [ ] Multi-patch navigation (dropdown)
- [ ] Historical trend charts
- [ ] Build variations per champion (main + niche)
- [ ] Integration with Draft Advisor (pin junglas to pools)
- [ ] Role recommendations (AD carry synergies, etc.)

## Integration

**Module Path**: `src/riot_lol_cli/jungle_meta/`
- `server.py` — FastAPI app + routes
- `loader.py` — JSON data loading + caching

**Module Entry**:
```python
from riot_lol_cli.jungle_meta.server import app
# or
python -m riot_lol_cli.jungle_meta.server
```

---

**Note**: Current data is v1.1 style: multiple `core_builds`, curated categories and local item IDs. Keep screenshot-derived item corrections in `data/jungle_meta/patch_26.09.json` and add regression tests for champion builds that were manually verified.
