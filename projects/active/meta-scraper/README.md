# Meta Scraper

Proyecto activo para scrapear fuentes externas de meta, normalizar resultados y
guardar snapshots JSON locales de Support y ADC.

## Rutas runtime

- API FastAPI: `src/riot_lol_cli/meta_scraper/server.py`
- Orquestacion: `src/riot_lol_cli/meta_scraper/orchestrator.py`
- Normalizacion: `src/riot_lol_cli/meta_scraper/normalizer.py`
- Adapters: `src/riot_lol_cli/meta_scraper/adapters/`
  - `opgg.py` — OP.GG via Playwright (tabla HTML, position=support|adc)
  - `lolalytics.py` — LoLalytics via Playwright (extraccion por indice de celda)
  - `ugg.py` — U.GG via Playwright (tabla React `.rt-tr`/`.rt-td`, `/lol/champions/{slug}/build/`)
- Frontend: `src/riot_lol_cli/meta_scraper/static/`
- Datos generados: `data/meta_scraper/`
- Tests: `tests/meta_scraper/`

## Flujo principal

- Support: `POST /api/v1/meta/scrape` -> adapters (3) -> normalizer -> `latest_support_tier.json`
- ADC: `POST /api/v1/meta/scrape/adc` -> adapters (3) -> normalizer -> `latest_adc_tier.json`

El snapshot ADC incluye `climb_score` (calculado desde WR/PR/BR para ordenar
picks de solo queue). El snapshot Support no lo incluye.

## Fuentes activas

| Adapter | URL | Tecnica | Support | ADC |
|---------|-----|---------|---------|-----|
| `opgg` | `op.gg/champions?position={pos}` | Playwright, tabla HTML | Si | Si |
| `lolalytics` | `lolalytics.com/lol/tierlist/?lane={lane}` | Playwright, celdas por indice | Si | Si |
| `ugg` | `u.gg/lol/tier-list?role={role}` | Playwright, tabla React `.rt-tr` | Si | Si |

## Dashboard frontend (puerto 8002)

SPA con tabs Soporte / ADC. Funcionalidades:
- Tab Soporte: carga `GET /api/v1/meta/support/tier`, boton Actualizar dispara `POST /api/v1/meta/scrape`
- Tab ADC: carga `GET /api/v1/meta/adc/tier`, columna Climb Score, boton dispara `POST /api/v1/meta/scrape/adc`
- Poll de `/health` cada 10s para detectar scraping en curso y recargar al terminar

## Puerto

- Meta Scraper: `8002` por defecto (`LOLCLI_META_SCRAPER_HOST` y `LOLCLI_META_SCRAPER_PORT` permiten override).

## Alertas conocidas

- El paquete Playwright esta declarado en `requirements.txt`; para scraping real falta instalar el browser con `playwright install chromium`.
- `server.py` usa `settings.py` para host/port del Meta Scraper; el copy y los scripts deben asumir `8002` solo como default.
- Los snapshots en `data/meta_scraper/` son datos generados, no contrato estable.
- El Draft Advisor consume ambos snapshots de forma opcional: si no existen, el scoring conserva el comportamiento curado local.
- U.GG reporta el patch con numeracion propia (ej: "26.9") vs la convencion "16.9" de OP.GG y LoLalytics.
- LoLalytics ADC suele traer menos campeones que OP.GG porque algunos picks de nicho no aparecen en el top de la pagina dentro del timeout actual.

## Documentacion relacionada

- `AGENTS.md`
- `KB/README.md` (seccion Fuentes de scraping y jungla)
