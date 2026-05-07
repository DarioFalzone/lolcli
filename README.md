# riot_lol_cli

Repositorio multi-subsistema de herramientas locales de League of Legends.
Un solo paquete Python (`riot_lol_cli`) con varios servicios FastAPI, una CLI,
una galeria offline, un Draft Advisor y un Meta Scraper, mas una base de
conocimiento estrategica y proyectos legacy preservados.

**Version:** 1.6.4 · **Python:** 3.9+ · **Tests:** 132 (pytest) · **Licencia:** Privado

## Quick Start

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

copy .env.example .env
# Editar .env con RIOT_API_KEY (https://developer.riotgames.com/, 24h)

# CLI: traer historial de partidas y exportar HTML
python main.py --platform la2 --summoner "Nombre#TAG" --html-template claude-4-5

# Levantar los 3 servicios FastAPI + abrir frontends
scripts\bat\levantar_todo.bat
```

En Linux/macOS: `source .venv/bin/activate`. Ver [docs/getting-started.md](docs/getting-started.md).

## Catalogo de proyectos

### Proyectos activos

| Proyecto | Tipo | Path / entry point | Puerto | Frontend |
|----------|------|--------------------|--------|----------|
| CLI Match History | CLI Click | `main.py` + [src/riot_lol_cli/cli.py](src/riot_lol_cli/cli.py) | — | HTML export |
| Draft Advisor | FastAPI + SPA | [src/riot_lol_cli/draft_advisor/](src/riot_lol_cli/draft_advisor/) | 8001 | http://localhost:8001/draft |
| Meta Analyzer + Dashboard | FastAPI | [src/riot_lol_cli/meta_api/](src/riot_lol_cli/meta_api/) + [meta_analyzer/](src/riot_lol_cli/meta_analyzer/) | 8000 | http://localhost:8000/docs |
| Meta Scraper | FastAPI + Playwright | [src/riot_lol_cli/meta_scraper/](src/riot_lol_cli/meta_scraper/) | 8002 | http://localhost:8002 |
| Splash Gallery | Generador HTML | [src/riot_lol_cli/splash.py](src/riot_lol_cli/splash.py) | — | `outputs/splash-viewer.html` |
| Assets and Data | Recurso compartido | [assets/](assets/), [data/](data/), [scripts/](scripts/) | — | — |
| Junglas Pro | Standalone HTML | [projects/active/junglas-pro/](projects/active/junglas-pro/) | — | `index.html` |

### Proyectos legacy (preservados, no runtime)

| Proyecto | Path | Que era |
|----------|------|---------|
| riot-lol-cli (deshu) | [projects/legacy/riot-lol-cli/](projects/legacy/riot-lol-cli/) | CLI original con frontend HTML del summoner deshu |
| Patch Notes Scraper v33a | [projects/legacy/patch-notes-scraper-v33a/](projects/legacy/patch-notes-scraper-v33a/) | Scraper PowerShell de notas de parche |
| Patch Notes Web v33b | [projects/legacy/patch-notes-web-v33b/](projects/legacy/patch-notes-web-v33b/) | Sitio web de notas de parche con HTML + JSON |
| DDragon Item Scraper | [projects/legacy/ddragon-item-scraper/](projects/legacy/ddragon-item-scraper/) | Scraper antiguo de items de Data Dragon |
| ADC Screenshots | [projects/legacy/adc-screenshots/](projects/legacy/adc-screenshots/) | Experimento de captura de pantallas ADC |

Detalle por proyecto en [projects/README.md](projects/README.md). El README maestro de cada proyecto activo vive en `projects/active/<proyecto>/README.md`.

## Capacidades por dominio

### Match history y reportes

- Consultar Riot API (`Summoner-V4`, `Match-V5`, `Account-V1`) por nombre o `nombre#tag`.
- Resolver platform → regional automaticamente (la2 → americas, etc.).
- Reintentos con `Retry-After` ante 429.
- Exportar a HTML autocontenido con plantilla `claude-4-5` (estilo Hextech).
- Cache local de partidas en `data/cache/matches.json`.

### Draft Advisor (puerto 8001)

- Motor de scoring multifactor para ADC y Support con KB estructurada.
- Politica de prioridad ADC con maestria personal + meta gating.
- Reglas anti-meta y vetos explicitos (Nilah/Soraka).
- Bonus `climb_meta` calibrado: `(climb-50)*0.35 + (wr-50)*1.2 + min(pr,12)*0.25 - min(br,30)*0.15` (clamp ±10/+12).
- 32 perfiles ADC + soporte; integracion NotebookLM (sinergias medidas, triangulo estrategico).
- SPA en español rioplatense, dark navy, microcopy gamer.
- API: `/api/v1/draft/health`, `/api/v1/draft/champions`, `/api/v1/draft/recommendations`.

### Meta Analyzer + Dashboard (puerto 8000)

- Recoleccion de partidas → SQLite local (`data/meta_analyzer.db`).
- Deteccion de anomalias estadisticas (z-score por campeon/rol).
- Generacion de tier lists multifuente.
- Dashboard HTML con filtros y tabs.
- Endpoints: `/v1/champion/stats`, `/v1/anomalies`, `/v1/tierlist`, `/maintenance/status`.

### Meta Scraper (puerto 8002)

- Adapters para OP.GG, LoLalytics y U.GG via Playwright (sync_api).
- Normalizador que mergea datos de las 3 plataformas.
- Cache layer + manifest en `data/meta_scraper/`.
- Output canonico: `data/meta_scraper/normalized/latest_{adc,support}_tier.json`.
- Stale si supera 72h; el Draft Advisor warning si lo usa.

### Splash Gallery

- Catalogo Data Dragon localizado (~3000+ splash arts indexados).
- Visor HTML offline autocontenido con busqueda y filtros.
- Regeneracion automatica con `scripts/update_ddragon_assets.py`.

### Junglas Pro

- Portal HTML standalone con investigacion sobre junglas profesionales.
- Research notes consolidadas con tier list por region (LCK/LPL/LEC/LCS).
- Imagenes IA de pro players + analisis de comp picks.

## Estructura del Repositorio

```text
LOLCLI/
├── main.py                         # Entry point de la CLI
├── README.md                       # Este archivo
├── AGENTS.md                       # Mapa maestro detallado para agentes IA
├── CLAUDE.md                       # Shim para Claude Code (puntero a AGENTS + rules)
├── bitacora_de_cambios.md          # Bitacora de iteraciones significativas
├── pyproject.toml                  # Ruff config + tool config
├── requirements.txt                # Dependencias runtime
├── requirements-dev.txt            # pytest, ruff
├── .agent/rules/                   # 4 rules canonicas (workflow, eng, docs, sec/test)
├── projects/                       # Indice por proyecto activo/legacy
│   ├── active/                     # 7 proyectos activos
│   ├── dev-scratch/                # Scripts manuales no runtime
│   └── legacy/                     # 5 proyectos archivados
├── src/riot_lol_cli/               # Paquete Python activo
│   ├── cli.py, api.py              # CLI + Riot API client
│   ├── rendering.py, splash.py     # HTML rendering + splash viewer
│   ├── meta_api/                   # FastAPI Meta Analyzer (puerto 8000)
│   ├── meta_analyzer/              # Anomalias, tier lists, colectores
│   ├── meta_scraper/               # Scraping OP.GG/LoLalytics/U.GG (puerto 8002)
│   ├── draft_advisor/              # Motor + SPA (puerto 8001)
│   ├── database/                   # SQLAlchemy ORM
│   └── schemas/                    # Pydantic V2 schemas Riot
├── templates/                      # Templates Jinja2 runtime
├── assets/                         # Splash arts, items, design assets
├── data/                           # Cache, manifests, KB estructurada, DB
│   ├── draft_advisor/              # Profiles, KB, scoring weights, audits
│   └── meta_scraper/               # Snapshots normalizados
├── scripts/                        # Automatizacion + launchers Windows .bat
│   └── bat/                        # draft_advisor.bat, meta_scraper.bat, levantar_todo.bat
├── docs/                           # Documentacion canonica
├── KB/                             # Base estrategica del Draft Advisor (NotebookLM, sintesis)
├── tests/                          # 132 tests (pytest)
└── claude-design-handoff/          # Handoff visual para Claude Design
```

## Puertos locales

| Servicio | Puerto | URL |
|----------|--------|-----|
| Meta API / Meta Analyzer | 8000 | http://localhost:8000/docs |
| Draft Advisor | 8001 | http://localhost:8001/draft |
| Meta Scraper | 8002 | http://localhost:8002 |

Levantar los 3 a la vez (idempotente, hidden processes, logs en `logs/`):

```powershell
scripts\bat\levantar_todo.bat
```

Cada servicio tambien tiene su launcher individual en `scripts/bat/`.

## Comandos clave

```powershell
# CLI
python main.py --platform la2 --summoner "Nombre#TAG" --count 10
python main.py --platform la2 --summoner "Nombre#TAG" --last-month --html-template claude-4-5

# Servidores standalone
python -m riot_lol_cli.draft_advisor.server      # 8001
python -m riot_lol_cli.meta_scraper.server       # 8002
python -m uvicorn src.riot_lol_cli.api_server:app --reload --port 8000

# Refrescar Data Dragon (assets + manifest + viewer)
python scripts/update_ddragon_assets.py

# Tests + lint
.venv\Scripts\python.exe -m pytest -q
ruff check src tests scripts
ruff format --check src tests scripts
```

## Documentacion

| Documento | Uso |
|-----------|-----|
| [AGENTS.md](AGENTS.md) | Mapa maestro detallado para agentes IA (subsistemas, gotchas, flujos) |
| [projects/README.md](projects/README.md) | Indice por proyectos activos y legacy |
| [docs/README.md](docs/README.md) | Indice de documentacion tecnica |
| [docs/getting-started.md](docs/getting-started.md) | Setup y primeros pasos |
| [docs/api-guide.md](docs/api-guide.md) | Riot API y APIs locales |
| [docs/draft_advisor/README.md](docs/draft_advisor/README.md) | API + scoring + datos del Draft Advisor |
| [docs/meta_analyzer/README.md](docs/meta_analyzer/README.md) | Meta Analyzer + DB + endpoints |
| [docs/dashboard/README.md](docs/dashboard/README.md) | Dashboard enhanced (filtros, tabs) |
| [docs/splash-viewer.md](docs/splash-viewer.md) | Galeria de splash arts |
| [docs/design-system.md](docs/design-system.md) | Tokens y componentes visuales |
| [KB/README.md](KB/README.md) | Base estrategica del Draft Advisor |
| [KB/notebooklm/sintesis/README.md](KB/notebooklm/sintesis/README.md) | Sintesis NotebookLM (paradigma, jerarquia, comps, sinergias, economia, roaming, crash-and-move, meta regional) |
| [bitacora_de_cambios.md](bitacora_de_cambios.md) | Log de iteraciones (fuente de verdad operacional) |
| [.agent/rules/](.agent/rules/) | 4 rules canonicas para agentes |
| [claude-design-handoff/README.md](claude-design-handoff/README.md) | Handoff visual consolidado para Claude Design |

## Para agentes (humanos o IA)

1. Leer [AGENTS.md](AGENTS.md) para el mapa detallado.
2. Si tocas estructura, rutas, docs, comandos u ownership: revisar tambien `projects/README.md`, `docs/README.md` y registrar la iteracion en [bitacora_de_cambios.md](bitacora_de_cambios.md).
3. Reglas operativas: [.agent/rules/](.agent/rules/) (workflow, engineering-standards, documentation-and-commits, security-and-testing).
4. [CLAUDE.md](CLAUDE.md) es solo un shim de compatibilidad para Claude Code.
