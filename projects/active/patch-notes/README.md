# Patch Notes Viewer

Subsistema activo del paquete `riot_lol_cli` para scrapear, normalizar y servir
las notas de parche oficiales de League of Legends.

## Estado

**Activo — V2.2 implementado.**

El subsistema vive en `src/riot_lol_cli/patch_notes/` y sigue el patrón canónico
de los demás subsistemas activos. V2 agrega scraping multi-source con 7 fuentes
(canónica + 6 enrichments), búsqueda full-text, vista diff entre versiones y
cron opcional con APScheduler.

**V2.2** (2026-05-15): el sistema pasa a ser **español-only** (la fuente de
verdad es solo `es-es` del sitio oficial de Riot), agrega **visual enrichment**
con champion + ability icons desde Data Dragon, **botón scroll-to-top
transversal** del design system y **DESIGN.md** para prompting con Google Stitch.

## Rutas runtime

| Componente | Path |
|------------|------|
| Server FastAPI | `src/riot_lol_cli/patch_notes/server.py` (puerto **8005**) |
| Schema Pydantic V2 | `src/riot_lol_cli/patch_notes/schema.py` |
| Orchestrator multi-source | `src/riot_lol_cli/patch_notes/orchestrator.py` |
| Normalizer (hash + persistencia) | `src/riot_lol_cli/patch_notes/normalizer.py` |
| Loader (API-side) | `src/riot_lol_cli/patch_notes/loader.py` |
| Search FTS in-memory | `src/riot_lol_cli/patch_notes/search.py` |
| Diff entre versiones | `src/riot_lol_cli/patch_notes/diff.py` |
| Scheduler APScheduler | `src/riot_lol_cli/patch_notes/scheduler.py` |
| 8 adapters | `src/riot_lol_cli/patch_notes/adapters/*.py` |
| Frontend SPA con tabs | `src/riot_lol_cli/patch_notes/static/` |
| Datos persistidos | `data/patch_notes/normalized/by_patch/`, `sources/{source}/`, `manifest.json` |
| Script de seed | `scripts/seed_patch_notes_from_legacy.py` |
| Tests V2 | `tests/patch_notes/` (65 tests, 100% green) |

## Fuentes scrapeadas (V2)

| Fuente | Tipo | Tecnología | Adapter |
|--------|------|------------|---------|
| **LoL oficial** | Canónica | Playwright | `lol_official.py` |
| **LoL /dev blog** | Enrichment | Playwright | `lol_dev.py` |
| **Calendario Riot** | Enrichment global | httpx + BS4 | `riot_calendar.py` |
| **Data Dragon** | Enrichment global | httpx (JSON) | `ddragon.py` |
| **U.GG** | Enrichment por patch | Playwright | `ugg_patch.py` |
| **OP.GG** | Enrichment por patch | Playwright | `opgg_patch.py` |
| **LoLalytics** | Enrichment por patch | Playwright | `lolalytics_patch.py` |
| **Mobalytics Tier List** | Enrichment por patch | Playwright | `mobalytics_patch.py` |
| **Mobalytics Breakdown** | Enrichment por patch | Playwright | `mobalytics_breakdown.py` |

## Arquitectura

```
discover (Playwright)
  → extract (Playwright + JS evaluate)
    → PatchSection[] + assets + metadata
      → compute_content_hash (sha256 estable)
        → detect_change vs manifest
          → save_normalized + update_manifest
            → API: /api/v1/patch-notes/{list,detail,scrape,manifest}
              → SPA: lista de cards → detalle con TOC sticky
```

Storage layout en disco:

```
data/patch_notes/
├── manifest.json                          # last_scrape, entries[], available_patches[]
├── normalized/
│   ├── by_patch/
│   │   ├── 25.17_es-es.json               # PatchNote completo
│   │   └── ...
│   └── history/
│       └── {timestamp}_{patch}_{locale}.json  # snapshots de cada revisión
└── raw/lol/{locale}/
    └── {timestamp}_{patch}.html           # (futuro) HTML crudo si se persiste
```

## Endpoints

| Método | Path | Descripción |
|--------|------|-------------|
| GET | `/` | SPA frontend (overview + detail con hash router) |
| GET | `/health` | `{status, patch_count, locales, last_scrape, scraper_available}` |
| GET | `/api/v1/patch-notes/list?locale=es-es` | Lista de parches descendente por versión |
| GET | `/api/v1/patch-notes/{patch_version}?locale=es-es` | Patch note completo |
| GET | `/api/v1/patch-notes/manifest` | Manifest crudo para debug |
| POST | `/api/v1/patch-notes/scrape?max_patches=6&locales=es-es,en-us` | Dispara scrape en background |

## Comandos

```powershell
# 1. Seed inicial desde los 6 parches legacy (es-es)
.venv\Scripts\python.exe scripts/seed_patch_notes_from_legacy.py

# 2. Levantar el server
.venv\Scripts\python.exe -m riot_lol_cli.patch_notes.server

# 3. Verificar
curl http://localhost:8005/health
curl http://localhost:8005/api/v1/patch-notes/list

# 4. Disparar scrape real multi-source (requiere `playwright install chromium`)
curl -X POST "http://localhost:8005/api/v1/patch-notes/scrape?max_patches=3&locales=es-es"

# 4b. Scrape de una sola fuente
curl -X POST "http://localhost:8005/api/v1/patch-notes/scrape/ddragon"

# 4c. Endpoints V2
curl "http://localhost:8005/api/v1/patch-notes/26.3/sources"
curl "http://localhost:8005/api/v1/patch-notes/search?q=aatrox&locale=es-es"
curl "http://localhost:8005/api/v1/patch-notes/diff/26.3/25.17?locale=es-es"

# 5. Tests y lint
.venv\Scripts\python.exe -m pytest tests/patch_notes -q
ruff check src/riot_lol_cli/patch_notes tests/patch_notes
```

## Fuentes scrapeadas

| Locale | URL índice | URL detalle |
|--------|-----------|-------------|
| `es-es` | `leagueoflegends.com/es-es/news/tags/patch-notes/` | `/es-es/news/game-updates/[league-of-legends-]patch-XX-YY-notes/` |
| `es-mx` | `leagueoflegends.com/es-mx/news/tags/patch-notes/` | idem locale |
| `en-us` | `leagueoflegends.com/en-us/news/tags/patch-notes/` | idem locale |

> **Nota V2.1**: a partir del patch 26.4, Riot cambió el slug a `league-of-legends-patch-X-Y-notes`.
> El regex del adapter acepta ambos formatos con `(?:league-of-legends-)?` opcional.

El adapter usa Playwright sync con `service_workers="block"`, click en "Ver más"
hasta agotar el índice, y `page.evaluate()` para extraer H1/fecha/jerarquía H2-H4/imágenes/links en una sola pasada.

## Schema canónico

`PatchNote` (modelos en `schema.py`):
- `publisher: "riot"`, `game: "lol"`, `channel: "site" | "dev" | "support"`.
- `source_locale: "es-es" | "es-mx" | "en-us"`.
- `patch_version: str` (ej: `26.10`, `26.10b`).
- `title`, `canonical_url`, `published_at`, `fetched_at`.
- `content_hash: sha256` — para change detection.
- `summary`, `sections: list[PatchSection]` (recursiva H2 → H3 → H4), `assets: list[PatchAsset]`.

## Cobertura V2

**Backend:**
- ✅ Scraping multi-locale del sitio oficial (es-es / es-mx / en-us).
- ✅ Scraping multi-source: 7 adapters (canónico + 6 enrichments).
- ✅ Schema Pydantic V2 con `content_hash` y `PatchEnrichment` por fuente.
- ✅ Persistencia: `by_patch/`, `history/`, `sources/{source}/`, `manifest.json` con `sources_status`.
- ✅ Tolerancia a fallos: enrichments con `error` no bloquean el flujo principal.
- ✅ Búsqueda full-text in-memory (índice TF al startup, AND lógico, snippet con highlight).
- ✅ Diff entre versiones con matching por título normalizado (heading recursivo).
- ✅ Cron opcional vía APScheduler (env var `LOLCLI_PATCH_NOTES_CRON_ENABLED=1`).
- ✅ 10 endpoints REST (list, detail, sources, sources/{src}, search, diff, manifest, registry, scrape, scrape/{src}).

**Frontend V2:**
- ✅ Hero con "Actualizado hace X días" + chip de freshness (fresh/stale/cold).
- ✅ Multi-locale toggle (ES-ES / ES-MX / EN-US) con persistencia en `localStorage`.
- ✅ Search input visible en overview con highlight de matches en resultados.
- ✅ Tab bar en detail: `[Notas oficiales] [Por fuente] [Comparar locales]`.
- ✅ Tab "Por fuente": accordion expandible con payload + estado (OK / Error).
- ✅ Tab "Comparar locales": 3 columnas lado a lado con los 3 locales.
- ✅ Vista diff (`#diff/{a}/{b}`) con badges añadido/eliminado/modificado, columnas a/b.
- ✅ Vista search (`#search?q=`) con cards de resultados linkeadas al patch.

**Calidad:**
- ✅ 65 tests V2 (schema + normalizer + loader + search + diff + enrichments + adapters_smoke).
- ✅ Ruff clean.
- ✅ Suite completa del repo: 367 tests pasan sin regresiones.
- ✅ Mojibake guard pasa.

## Endpoints V2

| Método | Path | Descripción |
|--------|------|-------------|
| GET | `/` | Frontend SPA |
| GET | `/health` | Estado + manifest + search index |
| GET | `/api/v1/patch-notes/list?locale=` | Lista de parches |
| GET | `/api/v1/patch-notes/{version}?locale=` | Patch + enrichments hidratados |
| GET | `/api/v1/patch-notes/{version}/sources` | Enrichments por patch |
| GET | `/api/v1/patch-notes/{version}/sources/{source}` | Payload de una fuente |
| GET | `/api/v1/patch-notes/search?q=&locale=` | Búsqueda full-text |
| GET | `/api/v1/patch-notes/diff/{a}/{b}?locale=` | Diff entre versiones |
| GET | `/api/v1/patch-notes/manifest` | Manifest crudo con sources_status |
| GET | `/api/v1/patch-notes/sources/registry` | Adapters disponibles + estado |
| POST | `/api/v1/patch-notes/scrape` | Scrape full multi-source en background |
| POST | `/api/v1/patch-notes/scrape/{source}` | Scrape de una sola fuente |

## Roadmap V2.5 / V3

- **Adapter resilience**: si los sitios comunitarios cambian markup, considerar
  fallback a `markdown.new` para extraer texto plano sin depender de selectores.
- **Cron en producción**: agendar `/scrape` cada 6h con notificación cuando aparezca
  un patch nuevo (env var `LOLCLI_PATCH_NOTES_CRON_ENABLED=1` lo habilita pero
  no hay UI para visualizar el log de runs).
- **Data Dragon enrichment más rico**: cruzar nombres de campeones mencionados en
  el patch con DDragon para mostrar iconos inline.
- **Disclaimer legal de Riot**: agregar boilerplate Riot Legal en el footer antes
  de cualquier publicación externa.
- **Lifespan API**: migrar `on_event` (deprecated) a `lifespan` context manager.

## Documentación relacionada

- [`deep-research-report.md`](./deep-research-report.md) — fuentes, estrategia, schema, UX.
- [`DESIGN.md`](./DESIGN.md) — contrato visual para Google Stitch / IA de UI.
- [`V3_ROADMAP.md`](./V3_ROADMAP.md) — próximas iteraciones planificadas (P1-P6).
- `Google_Stitch_DESIGNmd_Guia.pdf` — guía de prompting para Stitch.
- `AGENTS.md` — mapa maestro del repo (incluye puerto 8005 y subsistema).
- `projects/legacy/patch-notes-scraper-v33a/` — versión PS legacy (referencia histórica).
- `projects/legacy/patch-notes-web-v33b/` — frontend HTML legacy (referencia histórica).

Los archivos `scraper/`, `web/` y `data/` dentro de `projects/active/patch-notes/`
son del prototipo original anterior a esta reactivación; quedan accesibles como
material de comparación pero **no son fuente activa**.
