# Meta Analyzer + Dashboard

Proyecto activo para recopilar partidas, detectar anomalias de meta, generar
tier lists y exponer dashboards/API locales.

## Rutas runtime

- API wrapper raiz: `src/riot_lol_cli/api_server.py`
- App FastAPI real: `src/riot_lol_cli/meta_api/app.py`
- Runner: `scripts/run_api.py`
- Analisis: `src/riot_lol_cli/meta_analyzer/`
- Modelos DB: `src/riot_lol_cli/database/`
- Dashboards standalone: `src/riot_lol_cli/dashboard.py`, `src/riot_lol_cli/dashboard_enhanced.py`
- Scripts: `scripts/setup_meta_analyzer.py`, `scripts/generate_dashboard.py`
- Tests: `tests/test_meta_api.py`

## Flujo principal

`scripts/run_api.py` -> `api_server.py` -> `meta_api/app.py` -> DB/routes/dashboard

## Puerto

- Meta API: `8000`

## Deuda conocida

- No hay migraciones Alembic; cambios de schema requieren plan explicito.
- `dashboard_enhanced.py` mantiene HTML embebido en Python.
- La BD local `data/meta_analyzer.db` es runtime/gitignored.

## Documentacion relacionada

- `docs/meta_analyzer/README.md`
- `docs/dashboard/README.md`
- `docs/getting-started.md`
- `.agent/rules/agent-workflow.md`
