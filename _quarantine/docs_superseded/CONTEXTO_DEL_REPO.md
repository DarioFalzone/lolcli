# CONTEXTO DEL REPO

## Resumen del repositorio

`LOLCLI` ya no es solamente el CLI original para consultar partidas de League of Legends. En su estado actual, el repositorio agrupa varios subsistemas y capas de trabajo:

- un flujo de captura de partidas desde Riot API y export a HTML
- un pipeline de splash arts y un visor offline
- un sistema de Meta Analyzer con base SQLite, dashboards y API FastAPI
- un Draft Advisor orientado a picks ADC
- mucha documentacion, scripts de soporte y carpetas auxiliares o legadas

Este archivo no reemplaza a `README.md`. Su objetivo es servir como mapa operativo del repo: que existe, donde vive, que depende de que y que carpetas son fuente, datos o salidas generadas.

## Subsistemas principales

### 1. CLI de match history y export HTML

El flujo historico del proyecto sigue presente, pero hoy esta dividido entre un cliente Riot/API y scripts de apoyo:

- `main.py` es un wrapper minimo que delega a `src/riot_lol_cli/cli.py`.
- `src/riot_lol_cli/cli.py` expone el CLI actual y hoy se centra en:
  - generar HTML desde un JSON ya capturado
  - versionar el proyecto
  - construir el manifest de splash arts
  - generar el splash viewer
- `fetch_matches_full.py` es el script que consulta Riot API, resuelve Riot ID, descarga partidas y escribe `data/cache/matches.json`.
- `src/riot_lol_cli/api.py` contiene `RiotClient`, que encapsula llamadas a Riot API y Data Dragon.
- `templates/` en la raiz contiene las plantillas HTML usadas en runtime por el CLI.

En otras palabras: el fetch online de partidas no esta integrado como comando directo del CLI actual; vive en `fetch_matches_full.py`, y el CLI usa despues el JSON resultante para renderizar HTML.

### 2. Splash arts y splash viewer

Este bloque funciona como pipeline de assets + visor HTML offline:

- `download_splash_arts.py` descarga splash arts desde Data Dragon a `assets/splash_arts/`.
- `python main.py build-splash-manifest` escanea esos assets y genera `data/splash-manifest.json`.
- `python main.py generate-splash-viewer` produce `outputs/splash-viewer.html`.
- `assets/splash-viewer-app.js` aporta la logica del visor.

El flujo completo depende de datos locales ya descargados y genera un HTML consumible sin necesidad de backend.

### 3. Meta Analyzer, dashboards y API FastAPI

Este es el bloque mas cercano a una aplicacion de analisis:

- `src/riot_lol_cli/database/models.py` define el modelo de datos, enums y `DatabaseManager`.
- `src/riot_lol_cli/meta_analyzer/` agrupa recoleccion, deteccion de anomalias y generacion de tier lists.
- `src/riot_lol_cli/api_server.py` expone la API FastAPI del sistema.
- `src/riot_lol_cli/dashboard.py` y `src/riot_lol_cli/dashboard_enhanced.py` generan dashboards HTML.
- `setup_meta_analyzer.py` inicializa la base, carga demo data y genera frontend.
- `generate_dashboard.py` regenera el dashboard mejorado.
- `scripts/verify_adc_tracker.py` sirve como chequeo rapido de datos ya cargados en la base.

La base por defecto esta en `data/meta_analyzer.db` y las salidas HTML se escriben en `outputs/`.

### 4. Draft Advisor

Este subsistema esta separado del Meta Analyzer aunque comparten repo y stack:

- `src/riot_lol_cli/draft_advisor/server.py` levanta una app FastAPI propia y sirve la UI en `/draft`.
- `src/riot_lol_cli/draft_advisor/api.py` expone el router `/api/v1/draft/*`.
- `src/riot_lol_cli/draft_advisor/analyzer.py`, `scoring.py`, `champion_data.py` y `schemas.py` contienen la logica de recomendacion.
- `src/riot_lol_cli/draft_advisor/static/` contiene la SPA.
- `data/draft_advisor/*.json` contiene configuracion, champion base, perfiles ADC y pesos.

El Draft Advisor parece pensado como app autocontenida dentro del monorepo, con su propio backend y frontend liviano.

### 5. Documentacion y scripts de soporte

La capa documental es grande y esta repartida entre raiz y `docs/`:

- en la raiz hay varios documentos de onboarding o resumen: `README.md`, `START_HERE.md`, `PROJECT_OVERVIEW.md`, `INDEX.md`, `QUICK_START.md`
- `docs/` concentra guias por area (`dashboard/`, `meta_analyzer/`, `adc_tracker/`) y varios indices adicionales
- `scripts/` agrupa wrappers y utilidades operativas

Ademas hay carpetas auxiliares o de trabajo previo que no forman parte del runtime principal, pero si ayudan a entender el historial del repo.

## Entrypoints y flujos de uso

### Entrypoints principales

| Flujo | Punto de entrada actual | Resultado esperado |
| --- | --- | --- |
| Inspeccionar CLI | `python main.py --help` | Muestra comandos `generate`, `build-splash-manifest`, `generate-splash-viewer`, `version`, `bump-version` |
| Capturar partidas | `python fetch_matches_full.py --output data/cache/matches.json` | Descarga partidas desde Riot API y guarda JSON local |
| Export HTML de matches | `python main.py generate --read-json data/cache/matches.json --html-template claude-4-5` | Genera HTML en `outputs/claude-4-5/` o ruta custom |
| Descargar splash arts | `python download_splash_arts.py` | Pobla `assets/splash_arts/` |
| Construir manifest | `python main.py build-splash-manifest` | Genera `data/splash-manifest.json` |
| Generar splash viewer | `python main.py generate-splash-viewer` | Genera `outputs/splash-viewer.html` |
| Setup Meta Analyzer | `python setup_meta_analyzer.py --demo` | Inicializa DB y dashboards base |
| Regenerar dashboard | `python generate_dashboard.py` | Genera `outputs/meta-analyzer-dashboard-enhanced.html` |
| Wrapper de API | `python scripts/run_api.py` | Wrapper presente en `scripts/`; delega al backend FastAPI |
| Backend Meta Analyzer | `src/riot_lol_cli/api_server.py` | Sirve `/health`, `/api/v1/*`, `/dashboard`, `/dashboard-enhanced` |
| Draft Advisor | `python -m src.riot_lol_cli.draft_advisor.server` | Levanta la UI en `/draft` y API en `/api/v1/draft/*` |

### Flujo real por subsistema

#### Match history / export

1. `fetch_matches_full.py` usa `src/riot_lol_cli/api.py`.
2. El resultado se guarda tipicamente en `data/cache/matches.json`.
3. `main.py generate` toma ese JSON y una plantilla de `templates/`.
4. El HTML final se escribe en `outputs/`.

#### Splash viewer

1. `download_splash_arts.py` descarga archivos a `assets/splash_arts/`.
2. `main.py build-splash-manifest` genera `data/splash-manifest.json`.
3. `main.py generate-splash-viewer` escribe `outputs/splash-viewer.html`.

#### Meta Analyzer / dashboard

1. `setup_meta_analyzer.py` inicializa `data/meta_analyzer.db`.
2. `generate_dashboard.py` regenera el dashboard HTML mejorado.
3. `src/riot_lol_cli/api_server.py` publica endpoints JSON y sirve dashboards en rutas HTTP.

#### Draft Advisor

1. `data/draft_advisor/*.json` define datos base y configuracion.
2. `draft_advisor/champion_data.py` y `scoring.py` cargan y procesan esas reglas.
3. `draft_advisor/server.py` sirve API y SPA.

## Mapeo del repo

```text
LOLCLI/
|-- main.py
|-- fetch_matches_full.py
|-- download_splash_arts.py
|-- generate_dashboard.py
|-- setup_meta_analyzer.py
|-- requirements.txt
|-- config/
|   `-- version.json
|-- src/
|   `-- riot_lol_cli/
|       |-- __init__.py
|       |-- api.py
|       |-- api_server.py
|       |-- cli.py
|       |-- dashboard.py
|       |-- dashboard_enhanced.py
|       |-- html.py
|       |-- regions.py
|       |-- database/
|       |   |-- __init__.py
|       |   |-- models.py
|       |   `-- schema.sql
|       |-- meta_analyzer/
|       |   |-- anomaly_detector.py
|       |   |-- data_collector.py
|       |   |-- data_collector_db.py
|       |   |-- tier_generator.py
|       |   `-- README.md
|       |-- draft_advisor/
|       |   |-- __init__.py
|       |   |-- analyzer.py
|       |   |-- api.py
|       |   |-- champion_data.py
|       |   |-- schemas.py
|       |   |-- scoring.py
|       |   |-- server.py
|       |   `-- static/
|       `-- templates/
|-- scripts/
|   |-- run_api.py
|   |-- verify_adc_tracker.py
|   |-- fetch_adc_champions.py
|   |-- LEVANTAMIENTO_RAPIDO.bat
|   `-- LEVANTAMIENTO_RAPIDO.sh
|-- docs/
|   |-- adc_tracker/
|   |-- dashboard/
|   |-- meta_analyzer/
|   `-- indices y guias generales
|-- data/
|   |-- cache/
|   |   `-- matches.json
|   |-- draft_advisor/
|   |   |-- adc_profiles.json
|   |   |-- champion_base.json
|   |   |-- priority_profiles.json
|   |   `-- scoring_weights.json
|   |-- meta_analyzer.db
|   `-- splash-manifest.json
|-- outputs/
|   |-- claude-4-5/
|   |-- meta-analyzer-dashboard.html
|   |-- meta-analyzer-dashboard-enhanced.html
|   `-- splash-viewer.html
|-- assets/
|   |-- splash_arts/
|   `-- splash-viewer-app.js
|-- templates/
|-- README.md
|-- START_HERE.md
|-- PROJECT_OVERVIEW.md
|-- INDEX.md
`-- directorios auxiliares o legados
```

### Lectura rapida del mapeo

- `src/riot_lol_cli/` es el nucleo del codigo.
- `src/riot_lol_cli/database/` concentra persistencia y modelo de datos para Meta Analyzer.
- `src/riot_lol_cli/meta_analyzer/` concentra la logica analitica.
- `src/riot_lol_cli/draft_advisor/` es un subsistema separado con API y UI propias.
- `scripts/` agrupa utilidades operativas.
- `docs/` concentra la mayor parte de la documentacion formal.
- `data/` guarda base SQLite, cache y configuraciones JSON.
- `outputs/` contiene HTMLs generados.
- `assets/` contiene assets locales para el visor.
- `templates/` en la raiz es relevante porque el CLI carga plantillas desde ahi, no desde `src/riot_lol_cli/templates/`.

### Directorios auxiliares o legados que aportan contexto

No forman parte del runtime principal, pero ayudan a entender el historial del repo:

- `notas_parche/`: scripts y logs vinculados a patch notes.
- `proyecto lol/`: material previo de scraping y resultados HTML/JSON.
- `scraping info del lol/`: scripts de scraping puntuales.
- `research de mejores junglas profesionales/`: material de investigacion y salida estatica.
- `screenshot tirador segun cliente/`: capturas de referencia visual.
- `data_id_imagen/` e `imagenes_lol_items/`: datasets y assets de items.

## Que es fuente, que es generado y que es dato

| Tipo | Rutas principales | Rol |
| --- | --- | --- |
| Fuente ejecutable | `src/`, `main.py`, `fetch_matches_full.py`, `download_splash_arts.py`, `generate_dashboard.py`, `setup_meta_analyzer.py`, `scripts/` | Codigo y entrypoints |
| Documentacion | `docs/`, `README.md`, `START_HERE.md`, `PROJECT_OVERVIEW.md`, `INDEX.md`, otros `.md` de raiz | Contexto, onboarding, guias |
| Datos persistidos | `data/`, `config/version.json`, `adc_champions.json`, otros `.json` de raiz | Cache, DB, configuracion y snapshots |
| Generado | `outputs/`, parte de `data/cache/`, `coverage/` | HTMLs, dashboards y artefactos de ejecucion |
| Assets locales | `assets/`, `imagenes_lol_items/`, `screenshot tirador segun cliente/` | Imagenes y recursos visuales |
| Plantillas | `templates/` y, en menor medida, `src/riot_lol_cli/templates/` | Base HTML para renderizados |

## Observaciones del estado actual

- La documentacion esta solapada. Hay varios puntos de entrada documentales y no todos cuentan la misma historia del repo.
- `README.md` sigue muy orientado al CLI original, mientras que `START_HERE.md`, `PROJECT_OVERVIEW.md`, `INDEX.md` y `docs/INDEX.md` reflejan etapas posteriores mas cercanas a dashboard, meta analyzer y ADC tracker.
- El repo mezcla codigo producto, assets grandes, documentacion extensa y carpetas auxiliares/legacy en una misma raiz.
- `templates/` en la raiz parece ser la fuente efectiva para el CLI actual; `src/riot_lol_cli/templates/` funciona mas como copia o respaldo empaquetado.
- No se observa una carpeta `tests/` clara en la raiz; la validacion visible hoy parece apoyarse mas en scripts, dashboards generados y documentos de chequeo.

## Uso recomendado de este archivo

Usar `CONTEXTO_DEL_REPO.md` como referencia de orientacion tecnica rapida cuando necesites:

- ubicar el codigo fuente correcto antes de editar
- distinguir entre codigo, datos, assets y salidas generadas
- entender que entrypoint corresponde a cada flujo
- detectar si una guia vieja describe el estado actual o una etapa previa del proyecto

Para detalle funcional o tutoriales de uso, conviene complementar este archivo con la documentacion especifica de `docs/` y con los `.md` tematicos de la raiz.
