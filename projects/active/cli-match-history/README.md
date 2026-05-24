# CLI Match History / Match Viewer

Proyecto para consultar el historial de partidas de un invocador de League of Legends
via Riot API, enriquecer los datos con Data Dragon, y exportar/visualizar reportes HTML.

## Estado

**Activo — listo para refactorizar.**

El flujo funciona de punta a punta: fetch → cache → render → HTML. La estrategia de visualización
y el diseño del frontend están abiertos a cambio total. Ver sección [Roadmap de refactor](#roadmap-de-refactor).

## Que hace hoy

1. Resuelve el invocador por nombre+tag via **Account-V1** → obtiene `puuid`.
2. Consulta el historial de partidas via **Match-V5** (hasta N partidas o último mes).
3. Descarga el detalle de cada partida y lo procesa para extraer KDA, win/loss, campeón, queue, fecha.
4. Enriquece con assets de **Data Dragon CDN** (splash arts, iconos de campeón).
5. Renderiza un **reporte HTML** usando templates Jinja2 con diseño Hextech dark.

## Rutas runtime

El código vive en el paquete activo `src/riot_lol_cli/` del repo raíz — no en esta carpeta.

| Archivo | Rol |
|---------|-----|
| `main.py` (raíz) | Entry point del CLI |
| `src/riot_lol_cli/cli.py` | Comandos Click: fetch, generate, version |
| `src/riot_lol_cli/api.py` | Cliente Riot API (sync + async) con retry/backoff |
| `src/riot_lol_cli/rendering.py` | Renderizado HTML via Jinja2 |
| `templates/claude-4-5.html` | Template HTML activo |
| `data/cache/matches.json` | Cache local de payloads Match-V5 |
| `outputs/` | HTML generado (gitignored) |

## Flujo principal

```
main.py
  -> cli.py (Click)
     -> api.py  (Riot API: Account-V1, Summoner-V4, Match-V5, Data Dragon)
     -> data/cache/matches.json  (cache local)
     -> rendering.py  (Jinja2 + templates/)
     -> outputs/<template>/<slug>-<template>.html
```

## APIs externas usadas

| API | Endpoint | Uso |
|-----|----------|-----|
| Account-V1 | `GET /riot/account/v1/accounts/by-riot-id/{name}/{tag}` | Resolver nombre+tag → puuid |
| Summoner-V4 | `GET /lol/summoner/v4/summoners/by-puuid/{puuid}` | Datos del invocador (nivel, iconId) |
| Match-V5 | `GET /lol/match/v5/matches/by-puuid/{puuid}/ids` | Lista de matchIds |
| Match-V5 | `GET /lol/match/v5/matches/{matchId}` | Detalle de cada partida |
| Data Dragon | `ddragon.leagueoflegends.com/cdn/{v}/data/{lang}/champion.json` | Roster de campeones |
| Data Dragon | `ddragon.leagueoflegends.com/cdn/{v}/img/champion/{name}.png` | Iconos de campeón |

La API key de Riot (dev key, 24h) va en `.env` como `RIOT_API_KEY`.

## Comandos

```powershell
# Fetch completo de partidas para un invocador (plataforma LAS)
python main.py --platform la2 --summoner "nombre#TAG" --count 20

# Solo últimas N partidas
python main.py --platform la2 --summoner "nombre#TAG" --count 10

# Último mes completo
python main.py --platform la2 --summoner "nombre#TAG" --last-month

# Regenerar HTML desde cache local (sin llamadas a la API)
python main.py generate --read-json data/cache/matches.json --html-template claude-4-5

# Cambiar directorio de salida
python main.py --platform la2 --summoner "nombre#TAG" --html-template claude-4-5 --out-dir export
```

## Plataformas soportadas

| Plataforma | Region derivada |
|------------|-----------------|
| `la2`, `la1`, `na1`, `br1`, `oc1` | `americas` |
| `euw1`, `eun1`, `tr1`, `ru` | `europe` |
| `kr`, `jp1` | `asia` |

## Artefacto canonico

El reporte de referencia del invocador **deshu** (LAS) está en la copia legacy:
`projects/legacy/riot-lol-cli/outputs/claude-4-5/deshu-las-claude-4-5.html`

Muestra: invocador, nivel, KDA por partida, win/loss, queue, fecha, splash arts.

## Deuda tecnica actual

- El template `claude-4-5.html` tiene el diseño hardcodeado en Jinja2; la capa de datos y la de presentación están mezcladas.
- No hay API REST: el CLI escribe archivos HTML estáticos, no sirve datos via JSON.
- La cache (`data/cache/matches.json`) es un archivo plano sin TTL ni invalidación automática.
- No hay paginación en el HTML generado (si hay muchas partidas, el HTML es un scroll largo).
- Los splash arts se referencian desde `assets/splash_arts/` local; si no existen se cae silenciosamente.
- `rendering.py` mezcla lógica de transformación de datos con la renderización — debería separarse.
- No hay tests de rendering (solo tests de integración del cliente API en `tests/test_api.py`).
- La copia legacy `projects/legacy/riot-lol-cli/` contiene templates y outputs históricos — no es la fuente activa.

## Roadmap de refactor

El proyecto está listo para una refactorización completa. Las decisiones abiertas son:

### Estrategia de visualización
- **Opción A (actual):** HTML estático generado por CLI (offline, portable, sin servidor).
- **Opción B:** FastAPI en nuevo puerto (ej: `:8005`) con SPA que consume `/api/v1/matches/*`.
- **Opción C:** Tab dentro del Home Hub (`:8080`) con carga lazy de datos.
- **Opción D:** Dashboard-enhanced (`:8000`) con nuevo tab de historial personal.

### Estrategia de datos
- **Opción A (actual):** Cache JSON plano + regeneración manual.
- **Opción B:** SQLite con `match_id` como PK, TTL configurable, fetch incremental (solo partidas nuevas).
- **Opción C:** Usar la DB de `meta_analyzer.db` con tablas separadas para historial personal.

### Estrategia visual
- El template `claude-4-5.html` puede reemplazarse completamente.
- Posibles ángulos: tabla interactiva con filtros por campeón/queue, gráficas de winrate histórico,
  vista de progresión de rating, integración con splash arts HD.
- El design system activo del repo (tokens Hextech en `draft_advisor/static/design-system/`) puede usarse como base.

### Separacion de responsabilidades
- Separar `DataFetcher` (Riot API) de `DataTransformer` (procesar payloads) de `Renderer` (HTML/JSON).
- Esto permite testear cada capa independientemente y reutilizar el fetcher en otros subsistemas.

### Enriquecimiento de datos
- Agregar: rating estimado de MMR, tendencias (champion pool evolution), heatmap de horas/días.
- Cruzar con la tier list del Meta Scraper para marcar campeones meta/off-meta en cada partida.

## Tests relacionados

```
tests/test_api.py         — cliente Riot API sync
tests/test_async_api.py   — cliente Riot API async
tests/test_cli.py         — comandos CLI / rendering
tests/test_regions.py     — mapeo plataforma -> region
tests/test_schemas.py     — schemas Pydantic Match-V5
```

## Documentacion relacionada

- `AGENTS.md` — mapa maestro del repo
- `docs/api-guide.md` — endpoints Riot API y Data Dragon
- `docs/getting-started.md` — setup y comandos de arranque
- `projects/legacy/riot-lol-cli/README.md` — referencia histórica del proyecto original
