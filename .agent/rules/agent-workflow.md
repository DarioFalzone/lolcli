# Agent Workflow

Reglas operativas para agentes IA que trabajen en este repositorio.

## Lectura inicial

1. Leer `AGENTS.md` en la raiz.
2. Revisar `projects/README.md` para ubicar el proyecto logico afectado.
3. Leer el README del proyecto activo en `projects/active/*/README.md`.
4. Leer la doc tecnica del subsistema en `docs/` si el cambio toca API, datos, UI o comandos.
5. Revisar `git status --short` antes de editar y no revertir cambios ajenos.

## Mapa operativo

- Runtime activo: `src/riot_lol_cli/`, `data/`, `assets/`, `templates/`, `scripts/`.
- Mapa por proyecto: `projects/`.
- Documentacion tecnica activa: `docs/`.
- Base estrategica humana del Draft Advisor: `KB/`.
- Reglas de agentes: `.agent/rules/`.
- Historico no runtime: `projects/legacy/`.

No mover `src/`, `data/`, `assets/`, `templates/` o `scripts/` sin plan explicito de imports, rutas, docs y tests.

## Subsistemas y gotchas

- Hay tres FastAPI separados: Meta API `:8000`, Draft Advisor `:8001`, Meta Scraper `:8002`.
- `api_server.py` es wrapper; la app real del Meta Analyzer vive en `src/riot_lol_cli/meta_api/app.py`.
- Templates runtime activos: `templates/` en la raiz. No reintroducir `src/riot_lol_cli/templates/`.
- Rendering activo: `src/riot_lol_cli/rendering.py`; `html.py` es legado.
- `projects/legacy/riot-lol-cli/` no es el paquete activo.
- Meta Scraper requiere Playwright para scraping real (declarado en `requirements.txt` + `playwright install chromium`), pero no correr scraping salvo pedido explicito.
- Los 3 adapters de Meta Scraper tienen maps de nombres por plataforma; cualquier campeon nuevo en uno debe ir a los 3. `tests/meta_scraper/test_adapter_name_maps.py` detecta drift.
- `data/meta_analyzer.db`, caches, outputs y snapshots generados no son fuente de verdad.
- `projects/active/junglas-pro/` es standalone; no copiar su investigacion completa a `KB/`.
- `support_profiles.json` tiene drift historico de conteos; no corregir incidentalmente.

## Agentes por subsistema

Los antiguos `src/riot_lol_cli/*/AGENTS.md` fueron absorbidos. Usar estas referencias:

| Area | Documento canonico |
|------|--------------------|
| Draft Advisor | `projects/active/draft-advisor/README.md` + `docs/draft_advisor/README.md` |
| Meta Analyzer | `projects/active/meta-analyzer-dashboard/README.md` + `docs/meta_analyzer/README.md` |
| Database | `docs/meta_analyzer/README.md` seccion Base de Datos |
| Meta Scraper | `projects/active/meta-scraper/README.md` |
| Splash Gallery | `projects/active/splash-gallery/README.md` + `docs/splash-viewer.md` |

## Como cerrar una tarea

Antes de dar una tarea por terminada, ejecutar este checklist en orden:

1. **Tests**: correr `pytest -q` y `ruff check src tests scripts`. Si alguno falla, resolver antes de continuar.
2. **Bitacora**: si el cambio es significativo, agregar entrada en `bitacora_de_cambios.md` (fecha, que se hizo, archivos clave, resultado de verificacion). Ver criterios en `.agent/rules/documentation-and-commits.md`.
3. **Docs tecnicas**: revisar la tabla "Documentos a revisar" en `documentation-and-commits.md` y actualizar los que apliquen.
4. **Rules**: si el cambio introduce un gotcha nuevo, patron obligatorio o limitacion de entorno, registrarlo en la rule de `.agent/rules/` correspondiente.
5. **Commit**: un commit por cambio logico, Conventional Commit format, descripcion en imperativo.
6. **Informar**: reportar al usuario: que se hizo, tests ejecutados, riesgos residuales y documentos actualizados.

> Omitir cualquier paso de esta lista es deuda inmediata que el proximo agente o el usuario tendran que pagar.

## Glosario minimo

- ADC: tirador de bot lane.
- Draft: fase de seleccion de campeones.
- KB: Knowledge Base humana y estrategica del Draft Advisor.
- Golden drafts: casos de evaluacion/regresion del Draft Advisor.
- DDragon: Data Dragon CDN de Riot con datos y assets oficiales.
- PUUID: identificador universal de jugador usado por Riot APIs.
