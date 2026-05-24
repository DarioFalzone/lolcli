# Projects

Este directorio es el indice principal del repositorio por proyectos logicos.

Decision vigente: el repo sigue siendo un unico proyecto Python (`riot_lol_cli`)
con varios subsistemas. Los proyectos activos que forman parte del runtime
mantienen codigo, datos y assets en `src/`, `data/`, `assets/`, `templates/` y
`scripts/` para no romper imports, entry points ni tests. Sus carpetas bajo
`projects/active/` son manifiestos navegables, no copias del codigo.

Los proyectos standalone que no importan ni son importados por `riot_lol_cli`
pueden vivir fisicamente dentro de `projects/active/` o `projects/legacy/`.

## Proyectos activos

| Proyecto | Manifest | Codigo, datos o artefactos reales |
|----------|----------|------------------------------------|
| CLI Match History | `active/cli-match-history/README.md` | `main.py`, `src/riot_lol_cli/cli.py`, `src/riot_lol_cli/api.py`, `src/riot_lol_cli/rendering.py`, `templates/`, `data/cache/` |
| Patch Notes Viewer | `active/patch-notes/README.md` | `src/riot_lol_cli/patch_notes/`, `data/patch_notes/`, `tests/patch_notes/`, `scripts/seed_patch_notes_from_legacy.py` |
| Splash Gallery | `active/splash-gallery/README.md` | `src/riot_lol_cli/splash.py`, `templates/splash-viewer.html`, `assets/splash_arts/`, `data/ddragon-splash-catalog.json`, `data/splash-manifest.json`, `outputs/splash-viewer.html` |
| Home Hub | `active/home-hub/README.md` | `src/riot_lol_cli/home/`, `scripts/bat/home.bat`, `scripts/bat/levantar_todo.bat` |
| Draft Advisor | `active/draft-advisor/README.md` | `src/riot_lol_cli/draft_advisor/`, `data/draft_advisor/`, `KB/`, `tests/draft_advisor/` |
| Meta Analyzer + Dashboard | `active/meta-analyzer-dashboard/README.md` | `src/riot_lol_cli/meta_api/`, `src/riot_lol_cli/meta_analyzer/`, `src/riot_lol_cli/database/`, `src/riot_lol_cli/dashboard*.py`, `data/meta_analyzer.db` |
| Esports Research | `active/meta-analyzer-dashboard/README.md` | `src/riot_lol_cli/esports_research/`, `src/riot_lol_cli/meta_api/routes/esports.py`, `src/riot_lol_cli/meta_api/static/esports/`, `data/esports_research/`, `tests/esports_research/` |
| Meta Scraper | `active/meta-scraper/README.md` | `src/riot_lol_cli/meta_scraper/`, `data/meta_scraper/`, `tests/meta_scraper/` |
| Jungle Meta | `active/jungle-meta/README.md` | `src/riot_lol_cli/jungle_meta/`, `data/jungle_meta/`, `tests/jungle_meta/` |
| Items Browser | `active/items-browser/README.md` | `src/riot_lol_cli/items_browser/`, `data/items/database.json`, `assets/items/`, `tests/items_browser/` |
| Assets y datos Riot | `active/assets-and-data/README.md` | `assets/`, `data/`, scripts de descarga/fetch |
| Junglas Pro | `active/junglas-pro/README.md` | `active/junglas-pro/index.html`, `active/junglas-pro/research-notes.md`, `active/junglas-pro/docs/deeps_searchs/`, `active/junglas-pro/img/` |

## Herramientas manuales

| Area | Ruta | Uso |
|------|------|-----|
| Dev Scratch | `dev-scratch/` | Scripts manuales no runtime; promover a `scripts/` o `tests/` si se vuelven repetibles |

## Proyectos legacy

| Proyecto | Ruta | Estado |
|----------|------|--------|
| Copia antigua del paquete | `legacy/riot-lol-cli/` | Referencia histórica — el proyecto activo es `active/cli-match-history/` |
| Scraper de items/Data Dragon | `legacy/ddragon-item-scraper/` | Experimento archivado |
| Screenshots ADC | `legacy/adc-screenshots/` | Experimento archivado |
| Scraper de notas de parche (v33a) | `legacy/patch-notes-scraper-v33a/` | Referencia histórica — supersedido por `active/patch-notes/` |
| Web/proyecto de notas de parche (v33b) | `legacy/patch-notes-web-v33b/` | Referencia histórica — supersedido por `active/patch-notes/` |

## Historial de organizacion

- 2026-05-15: `patch-notes-scraper-v33a` y `patch-notes-web-v33b` reactivados como `active/patch-notes/`
  (proyecto standalone con scraper + frontend + datos). Legacy originals conservados como referencia.
  `cli-match-history` reactivado con README exhaustivo listo para refactor de estrategia visual.
- 2026-04-23/24: primera reorganizacion del repo heterogeneo hacia un proyecto
  Python navegable con `src/`, `data/`, `assets/`, `scripts/`, `docs/` y
  archivo historico.
- 2026-04-30: se adopta el mapa por proyectos, se consolidan docs canonicas y
  se mueven proyectos no runtime a `projects/legacy/`.
- 2026-04-30: `junglas-pro` vuelve a estar activo como proyecto standalone y
  los reportes de auditoria se absorben en docs, reglas y bitacora.
- 2026-05-02: se reduce Markdown disperso: reglas de agentes quedan en cuatro
  archivos canonicos, ADC Tracker se integra al Meta Analyzer, KB NotebookLM se
  consolida en un README y Junglas Pro/Handoff pasan a notas unificadas.
- 2026-05-02: Splash Gallery suma catalogo Data Dragon localizado y
  regeneracion automatica de manifest/HTML desde `scripts/update_ddragon_assets.py`.

## Reglas de mantenimiento

- No mover `src/`, `data/`, `assets/`, `templates/` o `scripts/` por proyecto
  sin plan explicito de imports, paths, docs y tests.
- La KB (`KB/`) es conocimiento estrategico para el Draft Advisor; no es un
  destino generico para documentos de arquitectura o analisis del repo.
- `projects/legacy/` conserva el material historico; no usarlo como fuente operacional salvo pedido explicito.
- Despues de cada iteracion que cambie estructura, endpoints, comandos, datos
  canonicos o docs, revisar y alinear `AGENTS.md`, `projects/README.md`,
  `docs/README.md` y `bitacora_de_cambios.md`.
