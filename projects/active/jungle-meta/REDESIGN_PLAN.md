# Plan de Rediseño — Jungle Meta Dashboard (Patch 26.09)

## Contexto

Rediseño completo de la SPA basado en las screenshots de SkillCapped en `projects/active/jungle-meta/screenshots/`. La estética guía es la del video de SkillCapped: tipografía display itálica grande, ícono de jungla blanco sobre cuadro negro, colores tier (S=gold, A=cyan, B=neutral, C=rojo), navegación por secciones (overview / champions / builds).

**Decisiones de estilo base:**
- **NO copiar bg blanco puro** — el usuario lo aclaró. Se mantiene el `forge-black` (#010a13) del design system, pero se incorpora la **tipografía display itálica condensada** y la jerarquía visual de las screenshots.
- **Reutilizar tokens del design-system** existente (`--arc-gold`, `--arc-cyan`, `--forge-*`, etc.).
- **Items reales de Data Dragon** desde `assets/items/<id>.png` (706 PNGs locales) en lugar de DDragon CDN.

---

## Estructura de la SPA (3 vistas)

### Vista 1 — **Overview** (entrada principal)

Captura de referencia: `caratula tier list jungle numero de parche.png` + `tier list completo vista previa general...png`

```
┌─────────────────────────────────────────────────────────┐
│  SKILLCAPPED            PATCH 26.09                     │
│                                                         │
│       T I E R   L I S T   (italic display)              │
│                                                         │
│       [🌿 jungla icon]              | JUNGLE            │
│       Last updated: 2026-05-08 18:00                    │
└─────────────────────────────────────────────────────────┘

┌────────────────────────┬────────────────────────────────┐
│   ⚡ OVERPOWERED        │  S │ [icons row]              │
│   [xin zhao] [shyvana] │ ───┼─────────────────────       │
│                        │  A │ [icons row]              │
│   🎯 LOW ELO PICKS     │ ───┼─────────────────────       │
│   [icons]              │  B │ [icons row]              │
│                        │ ───┼─────────────────────       │
│   🚫 BANS              │  C │ [icons row]              │
│   [icons]              │                                │
└────────────────────────┴────────────────────────────────┘
```

- Hero a ancho completo: copy "SKILLCAPPED", "PATCH 26.09", "TIER LIST" italic, ícono jungla, "Last updated".
- Sidebar izquierdo con 3 categorías (Overpowered, Low Elo, Bans).
- Grilla derecha con 4 filas tier (S/A/B/C) — cada champion icon es **clickeable** y lleva a la vista 3 (champion detail).

### Vista 2 — **Champions Index** (preview cards)

Captura de referencia: `caratula blanca preview champion.png`

Una tarjeta horizontal por champion con:

```
┌──────────────────────────────────────────────────────────┐
│ │   XIN ZHAO          [🖼️ portrait]    [S] tier badge  │
│ │   ▸ JUNGLE   TIER LIST                                │
│ │     CHANGES   PATCH 26.09                             │
└──────────────────────────────────────────────────────────┘
```

Esta vista muestra todos los champs como cards alineadas en grid responsive. Click en card → vista 3.

### Vista 3 — **Champion Detail** (con core builds)

Captura de referencia: `core build xin zao, doble posibilidad.png` + `core build red kayn.png` + `core build udyr tier s.png`

```
┌──────────────────────────────────────────────────────────┐
│   [🖼️ splash]  XIN ZHAO          [S] TIER               │
│                JUNGLE | PATCH 26.09                      │
│                                                          │
│   WR: 54.2%  PR: 12.5%  BR: 8.3%                         │
│   Reason: Hail of Blades + AD item buffs                 │
│   Rune: 🎯 Hail of Blades                                │
│                                                          │
│   ⌃ CORE BUILD                                           │
│   [boots] = [item] = [item] = [item]                     │
│                                                          │
│   ⌃ CORE BUILD (alt)                                     │
│   [boots] = [item] = [item] = [item]                     │
│                                                          │
│   🎯 PLAYSTYLE                                            │
│   Early game aggression, objective control.             │
└──────────────────────────────────────────────────────────┘
```

Soporta **builds múltiples** (Xin Zhao tiene 2 según screenshot).

---

## Cambios al modelo de datos

### `data/jungle_meta/patch_26.09.json`

**Antes:**
```json
{
  "core_items": ["Hail of Blades", "Warrior Enchantment", "Black Cleaver"],
  "core_rune": "Hail of Blades"
}
```

**Después:**
```json
{
  "core_builds": [
    {
      "label": "Standard",
      "items": [3047, 6699, 3071, 3156]
    },
    {
      "label": "vs Tank",
      "items": [3047, 6699, 3036, 3156]
    }
  ],
  "core_rune": {
    "name": "Hail of Blades",
    "tree": "Inspiration"
  }
}
```

Los `items` son **IDs reales de Data Dragon** (matches `assets/items/<id>.png`). Mapeo provisional desde nombres a IDs:

| Item (CSV nombre ES) | DDragon ID |
|----------------------|------------|
| Cuchilla Oscura (Black Cleaver) | 3071 |
| Cicloespada Voltaica | 6699 |
| Fauces de Malmortius | 3156 |
| Eclipse | 6692 |
| Fuerza de la Trinidad | 3078 |
| Bebedor de Sangre | 6630 |
| Cuchilla Rauda de Navori | 6675 |
| Botas de Movilidad | 3117 |
| Botas Plomizas (Plated Steelcaps) | 3047 |

> **Nota crítica:** Los items que aparecen en las screenshots de SkillCapped no son nítidos al 100% por compresión. Voy a proponer builds basadas en **arquetipos AD/AP/Tank de jungla del meta actual** y dejar que el usuario corrija item por item después. La estructura `core_builds` permite múltiples opciones por champion — esto matchea la screenshot de Xin Zhao con 2 builds.

### Nuevas categorías top-level

```json
{
  "patch": "26.09",
  "date_updated": "2026-05-08T18:00:00Z",
  "patch_theme": "Hail of Blades + AD items buffed",
  "categories": {
    "overpowered": ["XinZhao", "Shyvana"],
    "low_elo_picks": ["Warwick", "Amumu", "Nunu"],
    "bans": ["Shyvana", "Karthus"]
  },
  "items_meta": {
    "voltaic_sword_abusers": ["XinZhao", "Hecarim", "Kayn", "RekSai"]
  },
  "jungle_champions": [...]
}
```

Esto soporta:
- Sidebar de Overview (Overpowered / Low Elo / Bans)
- Vista de "abusers" del item destacado (la screenshot de Voltaic Sword)

---

## Backend — endpoints nuevos

### `loader.py` extender:
```python
def get_categories() -> dict
def get_item_abusers(item_name: str) -> list[dict]
def list_items_used() -> list[int]  # IDs únicos de items en builds
```

### `server.py` agregar:
```python
GET /api/v1/jungle/categories          # overpowered/low_elo/bans
GET /api/v1/jungle/items/abusers/{item} # champs que usan un item específico
GET /api/v1/jungle/items                # mapping ID -> nombre/imagen
```

Y servir items locales:
```python
app.mount("/items", StaticFiles(directory=str(_ITEMS_DIR)), name="items")
# → /items/3071.png en lugar de DDragon CDN
```

---

## Archivos a crear/modificar

| Archivo | Acción | Detalle |
|---------|--------|---------|
| `src/riot_lol_cli/jungle_meta/static/index.html` | **Reescribir** | SPA con 3 vistas (router por hash `#overview`, `#champions`, `#champion/{id}`) |
| `src/riot_lol_cli/jungle_meta/static/styles.css` | **Crear** | Separar estilos del HTML (importar tokens del design-system) |
| `src/riot_lol_cli/jungle_meta/static/app.js` | **Crear** | Separar JS del HTML, hash router, fetch lógico |
| `src/riot_lol_cli/jungle_meta/static/jungle-icon.svg` | **Crear** | Ícono SVG de la hoja de jungla (de la carátula) |
| `data/jungle_meta/patch_26.09.json` | **Refactor** | Nuevo schema con `core_builds`, `categories`, IDs de items |
| `src/riot_lol_cli/jungle_meta/loader.py` | Extender | `get_categories()`, `get_item_abusers()` |
| `src/riot_lol_cli/jungle_meta/server.py` | Extender | 3 endpoints nuevos + mount `/items` static |
| `tests/jungle_meta/test_loader.py` | Extender | Tests para categorías, builds múltiples, item abusers |
| `tests/test_server_factories.py` | Extender | Smoke tests para nuevas rutas |
| `bitacora_de_cambios.md` | Actualizar | Entrada de redesign |

---

## Tipografía y assets

- **Display font**: la screenshot usa una itálica condensada estilo "Inter Italic 800" o "Outfit Italic Black" — usar **Outfit** (ya en design-system) con `font-style: italic` y `font-weight: 900`. Si queda flojo, agregar `Anton` desde Google Fonts como display secundario.
- **Jungle icon**: SVG inline con la silueta de hoja de hierba (el blade icon de Riot para rol de jungla) — render blanco sobre cuadrado oscuro con bordes redondeados.
- **Champion portraits**: DDragon CDN para `champion/{id}.png` (square) y opcional splash centered para detail view.
- **Item icons**: `assets/items/{id}.png` servido desde `/items/{id}.png` por el FastAPI.

---

## Lo que NO está en este redesign (futuro)

- Animaciones / transiciones complejas
- Multi-patch navigation (sigue siendo solo 26.09)
- Builds específicas por matchup (vs hp/vs ad/vs ap)
- Integración con Draft Advisor

---

## Verificación

1. `pytest tests/jungle_meta/ -v` — todos los tests pasan
2. `pytest tests/test_server_factories.py -v` — smoke tests OK
3. Browser en `http://localhost:8003`:
   - Vista Overview muestra hero + sidebar + tier grid
   - Click en champion icon → champion detail
   - Item icons cargan desde `/items/{id}.png` (no 404s)
   - Switch entre builds múltiples (Xin Zhao tiene 2)
   - Sidebar Overpowered/Low Elo/Bans renderiza correcto
4. `ruff check src tests scripts` — limpio

---

## Caveat sobre items específicos

Las screenshots están comprimidas (video screencap). Puedo identificar:
- ✅ **Estructura visual** de las builds (4 items, dos opciones, etc.)
- ✅ **Colores y siluetas** generales
- ✅ **Item destacado**: Voltaic Cyclosword (6699) en la screenshot que lo menciona explícitamente
- ⚠️ **NO al 100%**: el item específico exacto en cada slot por champion

**Mi propuesta:** voy a llenar las builds con arquetipos canónicos del meta (AD bruiser → Voltaic+Black Cleaver+Maw, AP → Liandry's+Rylai's+Morello, Tank → Sunfire+Thornmail+Abyssal) y el usuario corrige los slots específicos contra el video real. La estructura JSON con IDs hace que esa corrección sea directa (cambiar un número).

---

## Pregunta clave para el usuario antes de ejecutar

1. **¿Modal vs ruta separada para champion detail?** → propongo hash routing (`#champion/XinZhao`) sin modal — más simple, deeplink-friendly.
2. **¿Grid de tier list compacto (solo iconos) o expandido (icono + nombre + WR)?** → propongo **compacto** matching la screenshot, con tooltip al hover.
3. **¿Mantener filtros tier tabs (S/A/B/C)?** → propongo eliminarlos: la screenshot muestra todos los tiers a la vez. Más fiel al diseño SkillCapped.
