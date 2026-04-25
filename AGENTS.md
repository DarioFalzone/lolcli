# AGENTS.md — riot_lol_cli

## Propósito del Repositorio

CLI en Python para League of Legends con múltiples subsistemas: consulta de match history, visor de splash arts, detección de meta con anomalías, y motor de recomendación de picks ADC. Usa los endpoints Summoner-V4, Match-V5, Account-V1 y Data Dragon CDN de Riot Games.

**Versión:** 1.6.4 (auto-incrementada en `config/version.json`)
**Lenguaje:** Python 3.9+
**Package manager:** pip (`requirements.txt`)

## Mapa de Subsistemas

| Subsistema | Path | Stack | Estado | Descripción |
|------------|------|-------|--------|-------------|
| CLI Core | `src/riot_lol_cli/cli.py` | Click, Jinja2, PIL | Activo | Match history, exportación HTML, splash arts |
| Riot API Client | `src/riot_lol_cli/api.py` | requests | Activo | Wrapper de Summoner-V4, Match-V5, Account-V1 |
| API Server | `src/riot_lol_cli/api_server.py` | FastAPI, Uvicorn | Activo | Backend REST para meta analyzer |
| Dashboard | `src/riot_lol_cli/dashboard*.py` | HTML/JS embebido | Activo | Generador de dashboards HTML con Chart.js |
| Meta Analyzer | `src/riot_lol_cli/meta_analyzer/` | SQLAlchemy, estadísticas | Activo | Detección de anomalías, tier lists |
| Draft Advisor | `src/riot_lol_cli/draft_advisor/` | FastAPI, Pydantic | Activo | Recomendador de picks ADC |
| Database | `src/riot_lol_cli/database/` | SQLAlchemy ORM | Activo | Modelos y gestión de BD SQLite |

## Arquitectura General

```
main.py → cli.py (Click commands)
                ├── api.py (Riot API client)
                ├── html.py + templates/ (rendering)
                └── regions.py (platform mapping)

api_server.py (FastAPI) → database/models.py (SQLAlchemy)
                        → dashboard.py / dashboard_enhanced.py
                        → meta_analyzer/ (data_collector, anomaly_detector, tier_generator)

draft_advisor/server.py (FastAPI separado)
                        → analyzer.py, scoring.py, champion_data.py
                        → data/draft_advisor/ (JSON knowledge base)
```

**Nota:** Hay dos servidores FastAPI separados — `api_server.py` (Meta Analyzer) en puerto **8000**, y `draft_advisor/server.py` en puerto **8001**. Pueden correr simultáneamente.

## Convenciones de Paths

- `BASE_DIR = Path(__file__).parent.parent.parent` desde `src/riot_lol_cli/` resuelve al root del repo
- **Templates runtime:** `templates/` (root) — usados por `cli.py` para generación HTML
- **Templates render:** `src/riot_lol_cli/templates/` — usados por `html.py`
- **Data:** `data/` — cache, draft_advisor KB, splash-manifest, bases de datos
- **Output generado:** `outputs/` (gitignored)
- **Assets estáticos:** `assets/` — splash_arts (JPG), items (PNG), JS del visor
- **Config:** `config/version.json`
- **Scripts:** `scripts/` — scripts de utilidad, `scripts/bat/` — batch files Windows

## Stack Global

- **CLI:** Click 8+
- **HTTP:** requests 2.25+
- **ORM:** SQLAlchemy 2.0+, Alembic 1.12+
- **API:** FastAPI 0.109+, Uvicorn 0.27+, Pydantic 2.0+
- **Templates:** Jinja2 3.1+
- **Testing:** pytest 7.4+, pytest-asyncio
- **Env:** python-dotenv 1.0+
- **Imágenes:** Pillow (PIL)

## Reglas y Convenciones

Ver `.agent/rules/` para detalles completos:
- **Estilo de código:** Python PEP 8, docstrings en español
- **Commits:** Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`)
- **Idioma:** Documentación y comentarios en español, código en inglés
- **Secretos:** NUNCA commitear `.env`, usar `.env.example` como template

## Cómo Navegar Este Repo (para agentes)

1. Leé este `AGENTS.md` primero para entender la arquitectura general
2. Identificá el subsistema relevante en el mapa
3. Si es Draft Advisor, leé también `src/riot_lol_cli/draft_advisor/AGENTS.md`
4. Consultá `.agent/rules/` para convenciones transversales
5. Leé `docs/getting-started.md` para saber cómo correr cada parte

## Puntos de Entrada

| Entry Point | Comando | Descripción |
|-------------|---------|-------------|
| CLI | `python main.py --platform la2 --summoner "Nombre#TAG"` | Match history |
| API Server | `python scripts/run_api.py` | Meta analyzer API en :8000 |
| Draft Advisor | `cd src && python -m riot_lol_cli.draft_advisor.server` | Draft API en :8001 |
| Dashboard | `python scripts/generate_dashboard.py` | Genera HTML standalone |
| Splash Viewer | `scripts/bat/regenerar_splash_viewer.bat` | Regenera visor HTML |

## Gotchas Globales

1. **Puertos de FastAPI separados:** `api_server.py` (Meta Analyzer) corre en `:8000`, `draft_advisor/server.py` corre en `:8001`. Pueden correr simultáneamente.
2. **Templates duplicados:** `templates/claude-4-5.html` (root, 68KB, activo) vs `src/riot_lol_cli/templates/claude-4-5.html` (22KB, legacy). El root es el autoritativo.
3. **API key expira cada 24h:** Los tokens de desarrollo de Riot son temporales. Hay que renovar en https://developer.riotgames.com/
4. **PIL no está en requirements.txt:** `cli.py` usa Pillow para extracción de paleta de colores. Instalarlo manualmente si falta: `pip install Pillow`.
5. **Scripts usan paths relativos al repo root:** Todos los scripts en `scripts/` hacen `os.chdir()` al root del repo para resolver paths correctamente.

## Dependencias entre Subsistemas

```
cli.py ──────────→ api.py (si fetch online)
                 → templates/ (rendering)

api_server.py ──→ database/models.py
               → dashboard.py, dashboard_enhanced.py

meta_analyzer/ ─→ api.py (data_collector)
               → database/models.py (data_collector_db)

draft_advisor/ ─→ data/draft_advisor/*.json (self-contained)
               → assets/splash_arts/ (imágenes del frontend)

database/ ──────→ standalone (SQLAlchemy models)
```
