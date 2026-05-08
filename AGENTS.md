# AGENTS.md — riot_lol_cli

Este es el mapa maestro del repositorio para agentes IA. Leelo antes de tocar codigo, documentacion o datos.

## Proposito del Repositorio

`riot_lol_cli` es un unico proyecto Python con multiples subsistemas para League of Legends:

- CLI de match history y exportacion HTML.
- Visor offline de splash arts.
- Meta Analyzer con API FastAPI, SQLite, deteccion de anomalias y tier lists.
- Draft Advisor para recomendar picks ADC y Support.
- Meta Scraper para recolectar datos externos de Support y ADC desde plataformas como OP.GG y LoLalytics.
- Base de conocimiento estrategica para el razonamiento de draft.

Usa Riot Games API (`Summoner-V4`, `Match-V5`, `Account-V1`) y Data Dragon CDN para datos/assets oficiales.

**Version:** 1.6.4 (`config/version.json`)
**Lenguaje:** Python 3.9+
**Package manager:** pip (`requirements.txt`, `requirements-dev.txt`)
**Arquitectura:** proyecto unico, no monorepo. La decision vigente esta resumida en `projects/README.md`.

## Estado Actual del Arbol

El repo esta en evolucion activa y puede tener un working tree sucio. Antes de editar:

1. Revisar `git status --short`.
2. No revertir cambios ajenos.
3. Trabajar sobre el estado actual del working tree, no solo sobre `HEAD`.
4. Si el cambio es significativo, actualizar `AGENTS.md`, `projects/README.md`, `docs/README.md` y `bitacora_de_cambios.md` cuando aplique.

## Mapa de Subsistemas

| Subsistema | Path | Stack | Estado | Descripcion |
|------------|------|-------|--------|-------------|
| CLI Core | `main.py`, `src/riot_lol_cli/cli.py` | Click | Activo | Entry point de comandos, version, rendering y splash viewer |
| Rendering HTML | `src/riot_lol_cli/rendering.py`, `templates/` | Jinja2 | Activo | Exporta match history a HTML desde JSON/cache |
| Splash Viewer | `src/riot_lol_cli/splash.py`, `templates/splash-viewer.html` | Pillow, HTML autocontenido | Activo | Manifest y visor offline de splash arts |
| Riot API Client | `src/riot_lol_cli/api.py` | requests, httpx async | Activo | Cliente sync/async para Riot API con retry/backoff |
| Meta API | `src/riot_lol_cli/meta_api/`, `src/riot_lol_cli/api_server.py` | FastAPI, Uvicorn | Activo | API REST del Meta Analyzer en puerto 8000 |
| Meta Analyzer | `src/riot_lol_cli/meta_analyzer/` | SQLAlchemy, estadistica | Activo | Colectores, anomalias, tier lists |
| Database | `src/riot_lol_cli/database/` | SQLAlchemy ORM, SQLite | Activo | Modelos y manager de `data/meta_analyzer.db` |
| Dashboard | `src/riot_lol_cli/dashboard.py`, `dashboard_enhanced.py` | HTML/JS embebido | Activo | Dashboards standalone y servidos por Meta API |
| Draft Advisor | `src/riot_lol_cli/draft_advisor/` | FastAPI, Pydantic V2, JS vanilla | Activo | Recomendador ADC/Support y SPA en puerto 8001 |
| Draft KB | `KB/`, `data/draft_advisor/kb/` | Markdown, JSON estructurado | Activo | Fuente conceptual y reglas estructuradas del Draft Advisor |
| Meta Scraper | `src/riot_lol_cli/meta_scraper/` | FastAPI, Playwright, JSON | Activo | Scraping/normalizacion de meta support/ADC en puerto 8002 |
| Jungle Meta | `src/riot_lol_cli/jungle_meta/` | FastAPI, JSON, SPA | Activo | Tier list de campeones jungla por patch en puerto 8003 |
| Items Browser | `src/riot_lol_cli/items_browser/` | FastAPI, JSON, SPA | Activo | Catalogo de items LoL EN+ES con filtros por grupo en puerto 8004 |
| Schemas Riot | `src/riot_lol_cli/schemas/` | Pydantic V2 | Activo | Modelos tipados para payloads de Match-V5 |
| Scripts | `scripts/`, `scripts/bat/` | Python, Batch, Shell | Activo | Automatizacion de setup, fetch, dashboards y assets |
| Tests/CI | `tests/`, `.github/workflows/ci.yml` | pytest, ruff | Activo | Unit/eval tests y CI |
| Design Handoff | `claude-design-handoff/` | Markdown, CSS refs | Activo/referencia | Contexto visual para Claude Design |
| Project Map | `projects/` | Markdown | Activo | Manifiestos por proyecto activo y proyectos legacy agrupados |
| Junglas Pro | `projects/active/junglas-pro/` | HTML, Markdown, assets | Activo/standalone | Investigacion y portal local sobre junglas profesionales |
| Dev Scratch | `projects/dev-scratch/` | Python manual | No runtime | Scripts manuales de diagnostico no importados por el paquete |
| Legacy Projects | `projects/legacy/` | Mixto | No activo | Copias y experimentos fuera del runtime actual |

## Organizacion por Proyectos

`projects/` es el mapa operacional por proyecto. No duplica codigo activo:
los subsistemas vivos siguen en sus rutas runtime actuales para evitar romper
imports, rutas de assets, scripts y tests.

| Proyecto | Manifest | Rutas reales principales |
|----------|----------|--------------------------|
| CLI Match History | `projects/active/cli-match-history/README.md` | `main.py`, `src/riot_lol_cli/cli.py`, `rendering.py`, `templates/` |
| Splash Gallery | `projects/active/splash-gallery/README.md` | `src/riot_lol_cli/splash.py`, `assets/splash_arts/`, `data/ddragon-splash-catalog.json`, `data/splash-manifest.json` |
| Meta Analyzer + Dashboard | `projects/active/meta-analyzer-dashboard/README.md` | `meta_api/`, `meta_analyzer/`, `database/`, `dashboard*.py` |
| Draft Advisor | `projects/active/draft-advisor/README.md` | `draft_advisor/`, `data/draft_advisor/`, `KB/` |
| Meta Scraper | `projects/active/meta-scraper/README.md` | `meta_scraper/`, `data/meta_scraper/` |
| Assets y Datos Riot | `projects/active/assets-and-data/README.md` | `assets/`, `data/`, scripts de descarga/fetch |
| Junglas Pro | `projects/active/junglas-pro/README.md` | `projects/active/junglas-pro/index.html`, `docs/`, `img/` |

Los proyectos no activos viven en `projects/legacy/`: copia antigua
`riot-lol-cli`, scraper legacy de items/Data Dragon, screenshots ADC y
proyectos de notas de parche. Junglas Pro es activo pero standalone: no forma
parte del paquete `riot_lol_cli`.

## Arquitectura General

```
main.py
  -> src/riot_lol_cli/cli.py
     -> rendering.py + templates/ + outputs/
     -> splash.py + assets/splash_arts/ + data/splash-manifest.json
     -> versioning.py + config/version.json

src/riot_lol_cli/api.py
  -> Riot API / Data Dragon
  -> schemas/riot_api.py para payloads Match-V5

scripts/run_api.py
  -> src/riot_lol_cli/api_server.py
     -> meta_api/app.py
        -> meta_api/routes/*
        -> database/models.py
        -> dashboard.py / dashboard_enhanced.py
        -> meta_analyzer/*

src/riot_lol_cli/draft_advisor/server.py
  -> static/index.html + static/app.js + static/styles.css
  -> api.py (/api/v1/draft/*)
  -> champion_data.py
  -> analyzer.py + scoring.py + scoring_rules.py
  -> data/draft_advisor/*.json
  -> data/draft_advisor/kb/*
  -> assets/splash_arts/ (frontend)

src/riot_lol_cli/meta_scraper/server.py
  -> static/index.html + static/app.js + static/styles.css
  -> orchestrator.py
  -> adapters/lolalytics.py + adapters/opgg.py + adapters/ugg.py
  -> normalizer.py
  -> data/meta_scraper/*
  -> data/draft_advisor/champion_base.json (normalizacion de nombres)
```

Hay tres servidores FastAPI separados:

| Servicio | Entry point | Puerto | UI principal | Docs |
|----------|-------------|--------|--------------|------|
| Meta API / Meta Analyzer | `python scripts/run_api.py` | 8000 | `http://localhost:8000/dashboard-enhanced` | `http://localhost:8000/docs` |
| Draft Advisor | `python -m riot_lol_cli.draft_advisor.server` | 8001 | `http://localhost:8001/draft` | `http://localhost:8001/docs` |
| Meta Scraper | `python -m riot_lol_cli.meta_scraper.server` | 8002 | `http://localhost:8002` | `http://localhost:8002/docs` |
| Jungle Meta | `python -m riot_lol_cli.jungle_meta.server` | 8003 | `http://localhost:8003` | `http://localhost:8003/docs` |
| Items Browser | `python -m riot_lol_cli.items_browser.server` | 8004 | `http://localhost:8004` | `http://localhost:8004/docs` |

## Flujos Operativos

### Match History / HTML Export

```
python main.py ...
  -> cli.py
  -> api.py si hay fetch online, o data/cache/matches.json si se usa cache
  -> rendering.py
  -> templates/<template>.html
  -> outputs/<archivo>.html
```

- `templates/` en la raiz es la fuente activa de templates.
- `templates/claude-4-5.html` es el template principal para exports.
- `src/riot_lol_cli/html.py` y `src/riot_lol_cli/templates/` no forman parte del flujo activo actual.

### Splash Viewer

```
Data Dragon CDN
  -> scripts/update_ddragon_assets.py
  -> assets/splash_arts/<Champion>/*.jpg
  -> data/ddragon-splash-catalog.json
  -> python -m riot_lol_cli.cli build-splash-manifest
  -> splash.py
  -> data/splash-manifest.json
  -> python -m riot_lol_cli.cli generate-splash-viewer
  -> outputs/splash-viewer.html
```

El visor es HTML autocontenido para uso offline.
`scripts/update_ddragon_assets.py` regenera catalogo, manifest y HTML luego de
sincronizar splash arts, salvo que se use `--skip-gallery-regenerate`.

### Meta API / Meta Analyzer

```
python scripts/run_api.py
  -> api_server.py (wrapper)
  -> meta_api/app.py
  -> database.DatabaseManager
  -> routes/core.py, stats.py, champions.py, maintenance.py
  -> dashboard.py / dashboard_enhanced.py
  -> data/meta_analyzer.db
```

`meta_analyzer/` contiene la logica de recoleccion y analisis. `meta_api/` es la capa HTTP moderna.

### Draft Advisor

```
Browser SPA (/draft)
  -> /api/v1/draft/*
  -> api.py
  -> champion_data.py
  -> analyzer.py
  -> scoring.py / scoring_rules.py
  -> data/draft_advisor/*.json
  -> data/draft_advisor/kb/structured/*.json
```

El Draft Advisor es el subsistema mas autocontenido. No depende de `database/` ni de `meta_analyzer/`.

### Meta Scraper

```
Browser / POST /api/v1/meta/scrape
  -> meta_scraper/server.py
  -> ScrapingOrchestrator
  -> adapters/opgg.py + adapters/lolalytics.py
  -> normalizer.py
  -> data/meta_scraper/raw/*
  -> data/meta_scraper/normalized/latest_support_tier.json o latest_adc_tier.json
  -> data/meta_scraper/manifest.json
```

Playwright es requerido para scraping real. Si no esta instalado, el servidor puede levantar pero los adapters pueden no estar disponibles.

## Estructura de Paths

| Path | Rol |
|------|-----|
| `src/riot_lol_cli/` | Codigo fuente activo del paquete Python |
| `main.py` | Wrapper del CLI (`riot_lol_cli.cli.main`) |
| `config/version.json` | Version del proyecto |
| `data/cache/` | Cache de partidas y payloads runtime |
| `data/draft_advisor/` | Perfiles JSON y KB estructurada del Draft Advisor |
| `data/meta_scraper/` | Snapshots raw/normalizados del Meta Scraper |
| `data/ddragon-splash-catalog.json` | Catalogo Data Dragon localizado para nombres de skins, parche y fecha de importacion |
| `data/splash-manifest.json` | Indice generado de splash arts |
| `assets/splash_arts/` | Splash arts JPG por campeon |
| `assets/items/` | Iconos PNG de items |
| `templates/` | Templates HTML activos para exports y splash viewer |
| `outputs/` | HTML generado; gitignored |
| `docs/` | Documentacion tecnica por subsistema |
| `projects/` | Mapa por proyectos activos y legacy |
| `projects/dev-scratch/` | Scripts manuales no runtime |
| `projects/active/junglas-pro/` | Proyecto standalone activo de investigacion de junglas profesionales |
| `projects/legacy/` | Proyectos legacy; no editar salvo tarea explicita |
| `KB/` | Base conceptual humana del Support/Draft Advisor |
| `.agent/rules/` | Reglas transversales para agentes IA |
| `claude-design-handoff/` | Contexto de producto/diseno para Claude Design |

La fuente de verdad de paths runtime es `src/riot_lol_cli/paths.py`:

- `BASE_DIR = Path(__file__).resolve().parents[2]`
- `DATA_DIR = BASE_DIR / "data"`
- `OUTPUT_DIR = BASE_DIR / "outputs"`
- `TEMPLATES_DIR = BASE_DIR / "templates"`
- `ASSETS_DIR = BASE_DIR / "assets"`

## Entry Points y Comandos

| Objetivo | Comando |
|----------|---------|
| CLI help | `python main.py --help` |
| Generar HTML desde cache | `python main.py generate --read-json data/cache/matches.json --html-template claude-4-5` |
| Ver version | `python main.py version` |
| Bump version explicito | `python main.py bump-version` |
| Build splash manifest | `python -m riot_lol_cli.cli build-splash-manifest` |
| Generate splash viewer | `python -m riot_lol_cli.cli generate-splash-viewer` |
| Update Data Dragon assets | `python scripts/update_ddragon_assets.py` |
| Descargar splash arts | `python scripts/download_splash_arts.py` |
| Setup Meta Analyzer | `python scripts/setup_meta_analyzer.py` |
| Meta API | `python scripts/run_api.py` |
| Dashboard standalone | `python scripts/generate_dashboard.py` |
| Draft Advisor | `python -m riot_lol_cli.draft_advisor.server` |
| Meta Scraper | `python -m riot_lol_cli.meta_scraper.server` |
| Jungle Meta | `python -m riot_lol_cli.jungle_meta.server` |
| Items Browser | `python -m riot_lol_cli.items_browser.server` |
| Update Items Database | `python scripts/update_items_database.py` |
| Fetch completo de partidas | `python scripts/fetch_matches_full.py` |
| Tests | `pytest tests/` |
| Lint | `ruff check src tests scripts` |
| Format check | `ruff format --check src tests scripts` |

## APIs Locales

### Meta API (`:8000`)

Definida en `src/riot_lol_cli/meta_api/routes/`.

- `GET /health`
- `GET /dashboard`
- `GET /dashboard-enhanced`
- `GET /api/v1/stats/latest`
- `GET /api/v1/stats/champion/{champion_name}`
- `GET /api/v1/stats/top-tier`
- `GET /api/v1/anomalies/high-confidence`
- `GET /api/v1/anomalies/champion/{champion_name}`
- `GET /api/v1/anomalies/types`
- `GET /api/v1/tier-list/current`
- `GET /api/v1/tier-list/history`
- `GET /api/v1/analysis/logs`
- `GET /api/v1/dashboard/summary`
- `GET /api/v1/champions/{champion_name}/matchups`
- `GET /api/v1/champions/{champion_name}/items`
- `GET /api/v1/champions/{champion_name}/details`
- `GET /api/v1/champions/all/raw-data`
- `POST /api/v1/maintenance/cleanup`
- `GET /api/v1/maintenance/status`

### Draft Advisor API (`:8001`)

Definida en `src/riot_lol_cli/draft_advisor/api.py`.

- `GET /draft`
- `GET /api/v1/draft/health`
- `GET /api/v1/draft/meta/version-info`
- `GET /api/v1/draft/champions`
- `GET /api/v1/draft/champions/adcs`
- `GET /api/v1/draft/champions/supports`
- `POST /api/v1/draft/recommend`
- `GET /api/v1/draft/strategic-triangle/{champion_id}`

### Meta Scraper API (`:8002`)

Definida en `src/riot_lol_cli/meta_scraper/server.py`.

- `GET /`
- `GET /health`
- `GET /api/v1/meta/support/tier`
- `GET /api/v1/meta/support/champion/{champion_id}`
- `GET /api/v1/meta/support/history`
- `GET /api/v1/meta/adc/tier`
- `GET /api/v1/meta/adc/champion/{champion_id}`
- `POST /api/v1/meta/scrape`
- `POST /api/v1/meta/scrape/adc`

### Jungle Meta API (`:8003`)

Definida en `src/riot_lol_cli/jungle_meta/server.py`.

- `GET /` (dashboard SPA)
- `GET /health`
- `GET /api/v1/jungle/tier-list`
- `GET /api/v1/jungle/tier/{tier}` (S, A, B, C)
- `GET /api/v1/jungle/champion/{champion_id}`
- `GET /api/v1/jungle/categories`
- `GET /api/v1/jungle/items/abusers/{item_key}`
- `GET /api/v1/jungle/items/used`

### Items Browser API (`:8004`)

Definida en `src/riot_lol_cli/items_browser/server.py`. Sirve `data/items/database.json` (generado por `scripts/update_items_database.py`).

- `GET /` (dashboard SPA)
- `GET /health`
- `GET /api/v1/items/all?include_deprecated=false`
- `GET /api/v1/items/{item_id}`
- `GET /api/v1/items/groups` (starter/boots/components/legendary/consumables/trinkets/jungle_specific/deprecated)
- `GET /api/v1/items/categories` (tags Riot)
- `GET /api/v1/items/search?q=&lang=en|es`

## Datos y Knowledge Base

### Snapshot Observado (2026-04-30)

Estos conteos describen el working tree observado. No son contrato estable.

| Archivo | Conteo/estado observado |
|---------|-------------------------|
| `data/draft_advisor/champion_base.json` | 172 perfiles de campeon |
| `data/draft_advisor/adc_profiles.json` | 32 perfiles ADC |
| `data/draft_advisor/personal_adc_mastery.json` | Tier list personal ADC, fuente `KB/tier list adc 04 05 2026.png` |
| `data/draft_advisor/priority_profiles.json` | 41 perfiles de impacto |
| `data/draft_advisor/support_profiles.json` | 34 perfiles en el JSON |
| `data/splash-manifest.json` | 172 campeones, 2079 imagenes, Data Dragon 16.9.1 |
| `assets/items/` | 705 iconos PNG |
| `data/meta_scraper/manifest.json` | Ultimo snapshot OP.GG, 46 supports |

Los perfiles y relaciones del Draft Advisor deben usar IDs canonicos de `champion_base.json` (`JarvanIV`, `KogMaw`, `TahmKench`, etc.), no alias ni display names.

### Draft Advisor Data

| Archivo | Uso |
|---------|-----|
| `champion_base.json` | Roster base desde DDragon + curacion manual |
| `adc_profiles.json` | Perfiles profundos de ADC |
| `personal_adc_mastery.json` | Maestría personal ADC usada como gate de recomendacion; top ADC requiere meta `S` o `climb_score >= 80` |
| `support_profiles.json` | Perfiles profundos de supports y picks anti-meta |
| `priority_profiles.json` | Campeones de alto impacto para draft |
| `scoring_weights.json` | Pesos del motor |
| `data_manifest.json` | Metadata de versiones y validacion |
| `kb/manifest.json` | Fuentes de la KB estructurada |
| `kb/structured/*.json` | Reglas consumidas por el motor |
| `kb/evals/golden_drafts.json` | Casos de regresion/evaluacion |
| `kb/research/**/*.md` | Notas de investigacion con frontmatter |

`KB/` es la fuente conceptual humana. Cuando cambia el razonamiento estrategico, primero documentar ahi y luego sincronizar JSON/codigo.

### Meta Analyzer Data

- DB local: `data/meta_analyzer.db` (gitignored).
- Modelos autoritativos: `src/riot_lol_cli/database/models.py`.
- `database/schema.sql` existe como referencia SQL, pero no es la fuente de verdad.
- No hay migraciones Alembic activas. Cambios de schema requieren plan explicito.

### Meta Scraper Data

- Raw: `data/meta_scraper/raw/<platform>/...json`
- Normalizado support actual: `data/meta_scraper/normalized/latest_support_tier.json`
- Normalizado ADC actual: `data/meta_scraper/normalized/latest_adc_tier.json`
- Historico normalizado: `data/meta_scraper/normalized/history/*.json`
- Manifest: `data/meta_scraper/manifest.json`

## Documentacion Viva

| Documento | Rol |
|-----------|-----|
| `AGENTS.md` | Mapa maestro para agentes |
| `CLAUDE.md` | Shim corto para que Claude Code use `AGENTS.md` y `.agent/rules/` |
| `README.md` | Entrada humana general |
| `projects/README.md` | Indice operacional por proyectos activos y legacy |
| `docs/getting-started.md` | Como levantar cada subsistema |
| `docs/README.md` | Indice de documentacion |
| `docs/api-guide.md` | API Riot y APIs locales |
| `docs/design-system.md` | Tokens y componentes visuales |
| `docs/draft_advisor/README.md` | API, datos y scoring del Draft Advisor |
| `docs/meta_analyzer/README.md` | Guia canonica del Meta Analyzer |
| `docs/dashboard/README.md` | Guia canonica del dashboard |
| `docs/splash-viewer.md` | Splash viewer |
| `KB/README.md` | Indice de la base estrategica |
| `projects/active/junglas-pro/README.md` | Proyecto activo standalone de investigacion de junglas |
| `projects/active/junglas-pro/research-notes.md` | Notas consolidadas de investigacion y operacion de Junglas Pro |
| `bitacora_de_cambios.md` | Registro obligatorio de cambios significativos |

Nota: algunos documentos de `docs/` pueden tener endpoints, comandos o conteos antiguos. Antes de implementar contra docs, verificar contra codigo y tests.

## Design System y Frontend

Stack frontend: HTML, CSS y JavaScript vanilla. No hay React, bundler ni TypeScript.

Surfaces principales:

- Draft Advisor SPA: `src/riot_lol_cli/draft_advisor/static/`
- Meta Scraper dashboard: `src/riot_lol_cli/meta_scraper/static/`
- Match History export: `templates/claude-4-5.html`
- Splash Viewer export: `templates/splash-viewer.html`
- Dashboard Meta Analyzer: HTML embebido en `dashboard.py` y `dashboard_enhanced.py`

Tokens canonicos del design system:

- `src/riot_lol_cli/draft_advisor/static/design-system/tokens.css`
- `components.css`
- `compat-spa.css`
- `compat-dashboard.css`

Identidad visual: Hextech dark, gold/cyan, dark mode obligatorio, microcopy en espanol rioplatense con jerga gamer. En Draft Advisor, nombres visibles y razones deben estar en español; los IDs internos siguen en canon Data Dragon. Se permiten terminos gamer claros como `ADC`, `draft`, `teamfight`, `stun`, `dive`, `peel`, `poke`, `engage`, `roam`, `gank`, `matchup`, `all-in`, `frontline`, `wave`, `burst` y `scaling`.

## Testing y CI

### Tests existentes

- `tests/test_api.py`: Riot client sync.
- `tests/test_async_api.py`: Riot client async.
- `tests/test_cli.py`: comandos CLI/version/rendering.
- `tests/test_regions.py`: mapping plataforma -> region.
- `tests/test_schemas.py`: schemas Pydantic Riot.
- `tests/test_meta_api.py`: errores/control de rutas Meta API.
- `tests/draft_advisor/*`: golden drafts, KB extendida, anti-meta.
- `tests/meta_scraper/test_normalizer.py`: normalizacion y merge del scraper.

### Comandos

```bash
pytest tests/
pytest -q --cov=src/riot_lol_cli --cov-report=term-missing --cov-fail-under=30
ruff check src tests scripts
ruff format --check src tests scripts
```

El comando de coverage es una verificacion local/manual. CI corre en GitHub Actions con Python 3.9, instala `requirements.txt` y `requirements-dev.txt`, ejecuta Ruff y pytest.

## Reglas para Agentes

Ver `.agent/rules/`:

- `agent-workflow.md`: navegacion, comportamiento, mapa operativo y gotchas.
- `engineering-standards.md`: estilo Python/frontend, paths, Ruff y dead code.
- `documentation-and-commits.md`: protocolo documental y Conventional Commits.
- `security-and-testing.md`: secretos, Riot API, scraping, DB, tests y CI.

Reglas clave:

1. No commitear `.env` ni claves `RGAPI-*`.
2. No hacer requests reales a Riot en tests.
3. No tocar `projects/legacy/` sin pedido explicito.
4. No mover `assets/`, `data/`, `templates/` o `src/` sin actualizar codigo, docs y tests afectados.
5. Usar `logging` en librerias/servidores; `click.echo()` solo para CLI.
6. Usar modelos Pydantic para payloads complejos, no dict access fragil.
7. Toda iteracion significativa revisa `AGENTS.md`, `projects/README.md`, `docs/README.md` y actualiza `bitacora_de_cambios.md`.

## Gotchas Globales

1. **Cinco FastAPI separados:** Meta API `:8000`, Draft Advisor `:8001`, Meta Scraper `:8002`, Jungle Meta `:8003`, Items Browser `:8004`.
2. **`api_server.py` es wrapper:** la app real del Meta Analyzer vive en `meta_api/app.py`.
3. **Templates activos:** usar `templates/` raiz. No asumir `src/riot_lol_cli/templates/`.
4. **Rendering activo:** usar `rendering.py`. No reintroducir `html.py` legacy.
5. **Legacy copy:** `projects/legacy/riot-lol-cli/` no es el paquete activo.
6. **API key Riot:** dev keys expiran cada 24h; usar `.env`.
7. **Playwright:** Meta Scraper declara Playwright en `requirements.txt`, pero el browser Chromium se instala aparte con `playwright install chromium`.
8. **Puertos 8000-8004:** Meta API (:8000), Draft Advisor (:8001), Meta Scraper (:8002), Jungle Meta (:8003) e Items Browser (:8004) usan `settings.py` para host/port configurables via `LOLCLI_*_HOST` y `LOLCLI_*_PORT`.
9. **Data versioning:** `live_patch_label` es el parche jugable/meta; `static_data_version` es la version tecnica de Data Dragon/CDN y puede tener sufijos como `.1`.
10. **Draft data IDs:** relaciones de `adc_profiles.json`, `support_profiles.json` y `personal_adc_mastery.json` deben validar contra IDs canonicos de `champion_base.json`.
11. **ADC personal policy:** `excluded_from_recommendations` bloquea picks aunque sean meta; `never_top_pick` permite alternativa pero nunca primera opcion. Top ADC requiere maestria `S/A`, meta `S` o `climb_score >= 80`, y no estar vetado por reglas KB de linea como Nilah + Soraka vs Caitlyn + Nautilus ni por vetos tacticos de draft contra dive/burst sin frontline. Los bonus KB de matchup, como Xayah contra Malphite/TahmKench, solo suman fit de draft y no saltan el gate de meta/maestria.
12. **Docs con drift:** algunos docs antiguos mencionan endpoints o rutas pre-reorganizacion.
13. **SQLite concurrency:** `check_same_thread=False` permite FastAPI, pero writes concurrentes requieren cuidado.
14. **Generated outputs:** `outputs/`, DBs, caches y artefactos generados no son fuente de verdad.
15. **Dev scratch:** scripts manuales viven en `projects/dev-scratch/`; no dejarlos en `src/` si no son paquete.
16. **Junglas Pro:** vive en `projects/active/junglas-pro/` como proyecto standalone; no copiarlo entero a `KB/`.

## Alertas y Deuda Conocida

- Working tree observado con cambios amplios en docs, scripts, codigo, datos y tests.
- La suite del Draft Advisor incluye `tests/draft_advisor/test_data_integrity.py` para prevenir relaciones con IDs no canonicos.
- `docs/api-guide.md` y algunos docs de dashboard/meta pueden tener rutas antiguas comparadas con `meta_api/routes/*`.
- `docs/draft_advisor/README.md` puede describir una fase anterior del roster de supports.
- `Meta Scraper` requiere `playwright install chromium` para scraping real; el paquete Python ya esta declarado en `requirements.txt`.
- `settings.py` ya tiene helpers para Meta Scraper y Jungle Meta host/port; revisar scripts y copy visible cuando se agreguen nuevos entrypoints.
- `dashboard_enhanced.py` mantiene HTML embebido en Python; migrar a template solo con pedido explicito.
- `database/` no tiene migraciones; no cambiar schema sin plan.
- `projects/active/junglas-pro/` conserva contenido de investigacion standalone; validar vigencia de fuentes antes de usarlo como dato actual.

## Orden Recomendado de Lectura

1. `AGENTS.md` raiz.
2. `projects/README.md`.
3. `.agent/rules/agent-workflow.md`.
4. `.agent/rules/documentation-and-commits.md`.
5. `docs/getting-started.md`.
6. `CLAUDE.md`.
7. README del proyecto activo en `projects/active/*/README.md`.
8. Docs canonicas del subsistema.
9. Codigo del subsistema.
10. Tests correspondientes.

## Como Decidir Que Documento Actualizar

| Cambio | Documento obligatorio |
|--------|-----------------------|
| Arquitectura, puerto, subsistema, path critico | `AGENTS.md` + `projects/README.md` si cambia el mapa de proyectos |
| Comandos de setup/ejecucion | `docs/getting-started.md` |
| Endpoint o schema Draft Advisor | `docs/draft_advisor/README.md` |
| Token visual o componente CSS | `docs/design-system.md` |
| Estrategia de soporte/draft | `KB/` + JSON estructurado si aplica |
| Estrategia de jungla reutilizable para Draft Advisor | `KB/` + JSON estructurado solo si se integra al motor |
| Meta Analyzer API/dashboard | `docs/meta_analyzer/` o `docs/dashboard/` |
| Fusion, renombre o baja de docs | `docs/README.md` |
| Cambio significativo cualquiera | `bitacora_de_cambios.md` |

## Definicion Practica de Hecho

Un cambio esta completo cuando:

- El codigo o docs solicitados estan actualizados.
- No se revirtieron cambios ajenos.
- Se corrio la verificacion razonable para el alcance.
- La documentacion relacionada esta sincronizada.
- `AGENTS.md` y `projects/README.md` fueron revisados si cambio estructura o ownership.
- `bitacora_de_cambios.md` registra la iteracion si fue significativa.
- El resultado final informa pruebas ejecutadas y cualquier riesgo residual.
