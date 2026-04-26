# Screens & Flows — riot_lol_cli

> Inventario de pantallas/vistas del proyecto, con sus rutas, propósito, componentes que usan, y flujo entre ellas.

## Contexto

El proyecto tiene **4 surfaces de UI** que viven en **3 procesos diferentes**:

| Surface | Servidor | Puerto | Stack |
|---------|----------|--------|-------|
| Draft Advisor SPA | `draft_advisor.server` (FastAPI) | 8001 | HTML+CSS+JS vanilla |
| Meta Analyzer Dashboard | `api_server` (FastAPI) | 8000 | HTML embebido en Python |
| Match History Export | CLI `python main.py … --html-template` | — (file) | Jinja2 → HTML estático |
| Splash Arts Gallery | CLI `… generate-splash-viewer` | — (file) | Jinja2 → HTML estático |

Los dos primeros son **interactivos en navegador**. Los dos últimos son **exports estáticos**.

---

## 1. Draft Advisor SPA

**Ruta servida:** `GET http://localhost:8001/draft` ([`server.py:59`](../src/riot_lol_cli/draft_advisor/server.py#L59))
**Archivo:** `src/riot_lol_cli/draft_advisor/static/index.html` (174 líneas)
**Stack:** HTML + CSS (`styles.css`) + JS vanilla (`app.js`)

### 1.1 Pantalla "Draft Board" (única — SPA con estado interno)

**Propósito:** Ingresar el draft actual (aliados + enemigos + contexto), elegir el rol objetivo (ADC / Soporte), y obtener una recomendación de pick con score breakdown, razones y plan de juego.

**Layout:**
```
┌─────────────────────────────────────────────────┐
│              Header (título + patch)            │
├─────────────────────┬───────────────────────────┤
│ Tablero de Draft    │ Pool de Campeones         │
│  ┌────┬────┬────┐   │  [Mejor / Pool / Solo]    │
│  │ +  │ +  │ +  │   │                           │
│  └────┴────┴────┘   │  Tag chips                │
│  Equipo Aliado      │  + Comfort sliders        │
│                     │                           │
│  ┌────┬────┬────┐   │                           │
│  │ +  │ +  │ +  │   │                           │
│  └────┴────┴────┘   │                           │
│  Equipo Enemigo     │                           │
│                     │                           │
│  Pick position │ Q  │                           │
│  Tipo cola │ Rol    │                           │
└─────────────────────┴───────────────────────────┘
                  [Recomendar Pick]
┌─────────────────────────────────────────────────┐
│ (visible al recomendar)                         │
│ Draft Summary tags                              │
├─────────────────────────────────────────────────┤
│ TOP PICK CARD                                   │
│  [Avatar] Nombre         Score: 87              │
│  [Score breakdown bars]                         │
│  ┌──────────┬──────────┐                        │
│  │ Strength │ Risks    │                        │
│  └──────────┴──────────┘                        │
│  ┌──────────┬──────────┐                        │
│  │ Avoid    │ Pattern  │                        │
│  └──────────┴──────────┘                        │
├─────────────────────────────────────────────────┤
│ ALTERNATIVAS (3 cards en grid)                  │
└─────────────────────────────────────────────────┘
```

**Componentes que usa:**
- Header (con `.patch-badge`)
- Card (×2 para input — Tablero, Pool)
- ChampionSlot (×9: 4 aliados + 5 enemigos)
- ChampionSlot disabled (×1: el slot del rol objetivo, `id="target-role-slot"`)
- Select (×3: pick-position, queue-type, target-role)
- Button.recommend (CTA principal)
- Modal (champion picker overlay)
- TopPickCard (composite con Avatar + ScoreBar × 6 + ExplanationBlock × 4)
- AlternativeCard (×3, grid)

**Flujo de interacción:**

```
[Inicial] → fetch /api/v1/draft/champions + /api/v1/draft/meta/version-info
        → renderiza patch-badge

[Click slot vacío] → openChampionPicker(team, index)
        → abre Modal
        → usuario filtra por rol o busca
        → click campeón → asigna a slot, cierra modal

[Cambio target-role select] → state.targetRole actualizado
        → resetea pool y comfort

[Toggle pool mode] → muestra/oculta pool config

[Click Recomendar Pick] → POST /api/v1/draft/recommend (con DraftState completo)
        → renderResults: draft summary + top pick + alternatives
        → scroll a resultados
```

**Estado JS persistido** (en memoria, [`app.js:9-20`](../src/riot_lol_cli/draft_advisor/static/app.js#L9-L20)):
```js
const state = {
  champions: [],
  allies: [null,null,null,null],
  enemies: [null,null,null,null,null],
  poolMode: 'unrestricted',
  poolChampions: [],
  comfort: {},
  modalTarget: null,
  roleFilter: 'all',
  recommendation: null,
  targetRole: 'support',  // default actual
};
```

**No persiste** entre sesiones (no usa localStorage por ahora — [A confirmar] si se planea agregar).

### 1.2 Modal "Champion Picker" (overlay sobre la misma pantalla)

**Propósito:** Buscar y seleccionar un campeón para asignar a un slot del draft o al pool.

**Layout:**
```
┌──────────────────────────────────────┐
│ [search input]              [×]      │
├──────────────────────────────────────┤
│ Todos · Top · Jungla · Mid · ADC · Sup│  (role-filters)
├──────────────────────────────────────┤
│ ┌──┬──┬──┬──┬──┬──┬──┬──┐            │
│ │🔥│🔥│🔥│🔥│🔥│🔥│🔥│🔥│  champion grid  │
│ ├──┼──┼──┼──┼──┼──┼──┼──┤            │
│ │🔥│🔥│🔥│🔥│🔥│🔥│🔥│🔥│            │
│ └──┴──┴──┴──┴──┴──┴──┴──┘            │
└──────────────────────────────────────┘
```

**Componentes:** Modal, Input (search), Button.filter (×6: Todos + 5 roles), Grid de champion-options.

---

## 2. Meta Analyzer Dashboards (servidos por FastAPI)

**Servidor:** `api_server` en puerto 8000 ([`server.py`](../src/riot_lol_cli/api_server.py))

### 2.1 Pantalla "Dashboard básico"

**Ruta:** `GET http://localhost:8000/dashboard` ([`core.py:19`](../src/riot_lol_cli/meta_api/routes/core.py#L19))
**Generador:** `dashboard.py` → HTML embebido (legacy)

**Propósito:** Tier list visual de ADCs con WR/PR/BR.

[A confirmar — esta vista es legacy y se reemplazó por el enhanced. Probablemente seguirá disponible pero no es la primaria.]

### 2.2 Pantalla "Dashboard mejorado" (4 tabs)

**Ruta:** `GET http://localhost:8000/dashboard-enhanced` ([`core.py:28`](../src/riot_lol_cli/meta_api/routes/core.py#L28))
**Generador:** `dashboard_enhanced.py` → HTML embebido

**Propósito:** Análisis interactivo con filtros y data source attribution.

**Tabs:**
1. **Dashboard** — Tier list S/A/B/C/D con cards de campeón, click → modal de detalle.
2. **Matchups** — Historial de enfrentamientos con filtro por campeón / horas / límite. Trend indicators (UP/DOWN/STABLE).
3. **Items** — Build analysis por campeón (frecuencia de compra, build path).
4. **Raw Data** — Datos sin filtrar con badge `[data_dragon]` en cada registro (source attribution).

**Componentes:**
- Header con stats badges
- Tab bar (×4 tabs)
- Filter row (selects de campeón, range de horas, límite)
- Cards de campeón con tier badge
- Tablas sortables
- Modal de detalle (click en campeón)

### 2.3 Endpoints de datos (no UI propias, consumidos por dashboard JS)

```
GET /api/v1/stats/latest
GET /api/v1/stats/champion/{champion_name}
GET /api/v1/stats/top-tier
GET /api/v1/champions/{champion_name}/matchups
GET /api/v1/champions/{champion_name}/items
GET /api/v1/champions/{champion_name}/details
GET /api/v1/champions/all/raw-data
GET /api/v1/anomalies/high-confidence
GET /api/v1/anomalies/champion/{champion_name}
GET /api/v1/tier-list/current
GET /api/v1/tier-list/history
GET /api/v1/dashboard/summary
```

---

## 3. Match History Export (HTML estático)

**Generación:** `python main.py --platform la2 --summoner "Nombre#TAG" --html-template claude-4-5`
**Output:** `outputs/claude-4-5/<slug>-claude-4-5.html`
**Template:** `templates/claude-4-5.html` (2329 líneas, autocontenido)

### 3.1 Pantalla "Match History Report"

**Propósito:** Reporte HTML autocontenido (sin JS de servidor) con últimas N partidas del invocador.

**Layout (basado en estructura del template):**
- **Header** con logo, nombre del invocador, nivel, version badge, animación de border glow.
- **Stats row** — KDA promedio, win rate, partidas jugadas.
- **Lista de matches** — Cada match es una card con: campeón, victoria/derrota, KDA, items, runas, hechizos, duración, modo de juego.
- **Footer** [A confirmar — habría que leer el template completo para mapear].

**Componentes:**
- Header con efecto border-flow animado
- VersionBadge (top-right, gradient gold)
- MatchCard (×N, una por partida)
  - WinLoss badge (Victory `--victory` / Defeat `--defeat`)
  - Champion portrait
  - KDA display
  - Items grid (5-6 íconos)
  - Runes display
- Stats summary row

**Particularidad:** El HTML es **completamente autocontenido** — funciona offline, abriendo el archivo localmente sin servidor.

---

## 4. Splash Arts Gallery (HTML estático)

**Generación:** `python -m riot_lol_cli.cli generate-splash-viewer`
**Output:** `outputs/splash-viewer.html` (612 KB, incluye manifest inline)
**Template:** `templates/splash-viewer.html` (148 líneas + JS externo)

### 4.1 Pantalla "Splash Gallery"

**Layout (3 zonas — sidebar + main):**

```
┌─────────────────────────────────────────────────────┐
│ ⚡ SPLASH GALLERY  Todos › Aatrox │ 171 Camp · 2019 Skins · ★ Fav · v1.6.4 │
├─────────────┬───────────────────────────────────────┤
│ [Buscar…]   │ Aatrox (3 skins)             [▼]      │
│             │ ┌─────┬─────┬─────┐                   │
│ A—Z grid    │ │skin │skin │skin │                   │
│ ABCDEFGH... │ └─────┴─────┴─────┘                   │
│             │ Cargar 12 más…                        │
│ Champions   │                                       │
│ • Aatrox 3  │ Ahri (8 skins)                [▼]     │
│ • Ahri  8   │ ┌─────┬─────┬─────┐                   │
│ • Akali 6   │ │skin │skin │skin │                   │
│ • …         │ └─────┴─────┴─────┘                   │
└─────────────┴───────────────────────────────────────┘
```

**Componentes:**
- Header sticky con logo + breadcrumbs + acciones (filtros badges/familias, favoritos, shuffle, comparator, audio, hotkeys, version)
- Sidebar (sticky 280px)
  - Search input
  - Alphabet grid (A-Z, letras enabled/disabled)
  - Champions list (item con avatar + name + count)
- Main content scrollable
  - Champion section (header colapsable) × N campeones
    - Section header con title + count + toggle ▼
    - Gallery grid (auto-fill 280px) de `.skin-card` (image + name + meta)
    - Load more button

**Modales:**
- **Filmstrip** — visor fullscreen con imagen grande + navegación + thumbnails strip + presenter mode (autoplay).
- **Hotkeys overlay** — H/F/J/K/ESC documentados.
- **Comparator** — grid de skins seleccionadas para comparar lado a lado.

**Hotkeys (declarados en UI):**
- `H` — Ocultar/Mostrar UI
- `F` — Pantalla completa
- `J` / `←` — Imagen anterior
- `K` / `→` — Imagen siguiente
- `ESC` — Cerrar visor
- `?` — Mostrar ayuda

---

## 5. Flujos de navegación

### Flujo 1 — Pre-game ranked (caso de uso principal del Draft Advisor)

```
Usuario en client de LoL en lobby de ranked
  │
  ▼
Abrir http://localhost:8001/draft (Draft Advisor)
  │
  ▼
Seleccionar target-role (Soporte / ADC) en select
  │
  ▼
A medida que el equipo pickea:
  ├─ Click + en slot ally → Modal → buscar/elegir → asignar
  ├─ Click + en slot enemy → Modal → buscar/elegir → asignar
  └─ Repetir
  │
  ▼
Click "Recomendar Pick"
  │
  ▼
POST /api/v1/draft/recommend (con DraftState completo)
  │
  ▼
Mostrar Top Pick + Alternativas
  │
  ▼
Usuario lee Razones + Plan de juego → pickea en cliente de LoL
```

### Flujo 2 — Análisis de meta (Meta Dashboard)

```
Setup inicial: python scripts/setup_meta_analyzer.py
  → genera datos demo en data/meta_analyzer.db
  │
  ▼
Levantar API: python scripts/run_api.py (puerto 8000)
  │
  ▼
Abrir http://localhost:8000/dashboard-enhanced
  │
  ▼
Tab "Dashboard" → ver tier list general
  │
  ├─ Click campeón → Modal con stats detallados
  ├─ Tab "Matchups" → filtros → ver enfrentamientos
  ├─ Tab "Items" → ver builds populares
  └─ Tab "Raw Data" → exportar/auditar datos
```

### Flujo 3 — Match history export

```
python main.py --platform la2 --summoner "Nombre#TAG" --html-template claude-4-5
  │
  ▼
CLI fetch Riot API → guarda data/cache/matches.json
  │
  ▼
Renderiza Jinja2 → outputs/claude-4-5/<slug>-claude-4-5.html
  │
  ▼
Doble click el archivo → abre en browser local (offline)
  │
  ▼
Usuario revisa últimas N partidas con stats
```

### Flujo 4 — Splash gallery

```
python scripts/download_splash_arts.py
  → descarga 2019 imágenes en assets/splash_arts/
  │
  ▼
python -m riot_lol_cli.cli build-splash-manifest
  → genera data/splash-manifest.json
  │
  ▼
python -m riot_lol_cli.cli generate-splash-viewer
  → renderiza templates/splash-viewer.html → outputs/splash-viewer.html
  │
  ▼
Doble click outputs/splash-viewer.html → abre en browser
  │
  ▼
Usuario navega: A-Z, búsqueda, filtros, favoritos, comparator, filmstrip
```

---

## Resumen — superficies a diseñar en Claude Design

| # | Pantalla | Tipo | Prioridad |
|---|----------|------|-----------|
| 1 | Draft Advisor — Draft Board | App SPA | **Alta** (caso de uso principal) |
| 2 | Champion Picker Modal | Overlay | Alta (depende de #1) |
| 3 | Top Pick Card | Composite component | Alta |
| 4 | Alternative Card | Component | Alta |
| 5 | Meta Dashboard — Tabs (Dashboard/Matchups/Items/Raw) | App | Media |
| 6 | Champion Detail Modal (Meta) | Overlay | Media |
| 7 | Match History Report | Static export | Baja (ya estable) |
| 8 | Splash Gallery — Sidebar+Main | App | Baja (ya estable) |
| 9 | Filmstrip Modal | Overlay fullscreen | Baja |
| 10 | Comparator Modal | Overlay | Baja |
