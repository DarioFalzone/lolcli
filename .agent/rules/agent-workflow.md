# Agent Workflow

Reglas operativas para agentes IA en este repo.

## Antes de editar

1. `git status --short` — no revertir cambios ajenos.
2. `AGENTS.md` para mapa de subsistemas, puertos y entrypoints.
3. `projects/active/<proyecto>/README.md` y `docs/<subsistema>/README.md` si el cambio toca API, datos o UI.

## Mapa rápido

- Runtime activo: `src/riot_lol_cli/`, `data/`, `assets/`, `templates/`, `scripts/`.
- Mapa por proyecto: `projects/`. Histórico no runtime: `projects/legacy/`.
- Reglas de agentes: `.agent/rules/`.
- 6 FastAPI: Home Hub `:8080`, Meta API `:8000`, Draft Advisor `:8001`, Meta Scraper `:8002`, Jungle Meta `:8003`, Items Browser `:8004`.

No mover `src/`, `data/`, `assets/`, `templates/` o `scripts/` sin plan explícito de imports, paths, docs y tests.

## Gotchas que no están en el código

- `api_server.py` es wrapper; la app real del Meta Analyzer vive en `src/riot_lol_cli/meta_api/app.py`.
- Templates runtime activos: `templates/` raíz. No reintroducir `src/riot_lol_cli/templates/`.
- Rendering activo: `src/riot_lol_cli/rendering.py`. `html.py` es legacy.
- Meta Scraper requiere Playwright para scraping real, pero **no correr scraping salvo pedido explícito**.
- Adapters Meta Scraper tienen maps de nombres por plataforma; champion nuevo va en los 3. Drift detector: `tests/meta_scraper/test_adapter_name_maps.py`.
- `data/meta_analyzer.db`, caches, outputs y snapshots no son fuente de verdad.
- `projects/active/junglas-pro/` es standalone; no copiar su investigación a `KB/`.
- `support_profiles.json` tiene drift histórico de conteos; no corregir incidentalmente.

## Home Hub: contrato obligatorio

Al agregar un sistema/servicio/proyecto: actualizar `src/riot_lol_cli/home/`. Cada UI integrada debe tener:

- Acceso visible de vuelta al Home Hub.
- Favicon explícito (evita 404 ruidoso en consola).
- Si depende de launch async, reservar pestaña en el click y navegar al confirmar `online`.

## Cierre de tarea

Antes de cerrar una iteración, aplicar verificación proporcional al alcance:

1. **Código/datos runtime**: tests focalizados + `ruff check src tests scripts`.
2. **Frontend visible**: `python scripts/visual_smoke.py <URL>` + abrir el PNG y validar (ver `engineering-standards.md` § Verificación visual obligatoria).
3. **Doc/estructura**: búsquedas o checks de consistencia, sin forzar pytest completo.
4. **Bitácora y docs**: actualizar en la misma iteración (ver `documentation-and-commits.md`).
5. **Rules**: registrar gotcha nuevo en la rule canónica correspondiente.
6. **Informar**: cerrar con resumen, verificación ejecutada y archivos creados/modificados.

> No es "correr todo siempre"; es no cerrar sin la verificación que cubre el cambio hecho. Para frontend, eso incluye **siempre** ver una captura, no solo leer el HTML.

## Glosario mínimo

- ADC: tirador bot lane.
- Draft: fase de selección de campeones.
- KB: Knowledge Base humana del Draft Advisor.
- Golden drafts: casos de regresión del Draft Advisor.
- DDragon: Data Dragon CDN de Riot.
- PUUID: identificador universal de jugador en Riot APIs.
