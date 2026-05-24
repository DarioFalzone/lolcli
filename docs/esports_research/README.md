# Esports Research

`esports_research` es el subsistema V0 para investigacion historica de LoL
Esports dentro de `riot_lol_cli`. Vive en el proceso Meta API `:8000` y expone
API bajo `/api/v1/esports/*` mas cockpit estatico en `/esports/`.

## Arquitectura

```text
adapters publicos/stubs
  -> bronze raw inmutable
  -> silver normalizado
  -> gold analytics
  -> Meta API router
  -> /esports UI vanilla
```

Capas principales:

| Capa | Path | Uso |
|------|------|-----|
| Dominio | `src/riot_lol_cli/esports_research/` | Schemas Pydantic V2, storage, registry, analytics, reports y pipelines |
| Adapters | `src/riot_lol_cli/meta_scraper/adapters/esports/` | Leaguepedia, Oracle's Elixir, Gol.gg, Data Dragon y stubs comerciales/oficiales |
| API | `src/riot_lol_cli/meta_api/routes/esports.py` | Endpoints read-only + refresh/ingest V0 con gaps visibles |
| UI | `src/riot_lol_cli/meta_api/static/esports/` | 6 paginas HTML vanilla con Pattern Library v2 |
| Datos | `data/esports_research/` | `sources.json`, bronze/silver/gold/reports |

## Fuentes

V0 activo:

- `leaguepedia`: Cargo API, bot password opcional, delay minimo 2s.
- `oracles_elixir`: CSV publico, parser stdlib.
- `gol_gg`: HTML publico conservador, robots.txt, delay 4-8s.
- `data_dragon`: CDN oficial para `Patch` y `ChampionDim`.

Stubs activables en PRs futuros:

- `riot_tournament_v5`
- `riot_esports_grid`
- `pandascore`
- `abios`
- `lol_esports_vods`
- `game_client_local`

Restricted/planned:

- `riot_match_v5`: solo historico de cuentas pro, no feed oficial LCS.
- `liquipedia`: fallback futuro para metadata.

## Storage

```text
data/esports_research/
  sources.json
  bronze/<source>/<partition>/*
  silver/tournaments.json
  silver/matches/<match_id>.json
  silver/games/<game_id>.json
  silver/teams.json
  silver/players.json
  silver/patches.json
  gold/counterpick_matrix_<patch>.json
  gold/comfort_features_<date>.json
  gold/synergy_pairs_<patch>.json
  reports/*.json
```

Toda escritura JSON usa UTF-8 sin BOM y reemplazo atomico `.tmp -> target`.

## API

Endpoints principales:

- `GET /api/v1/esports/health`
- `GET /api/v1/esports/tournaments`
- `GET /api/v1/esports/tournaments/{tournament_id}`
- `GET /api/v1/esports/matches/{match_id}`
- `GET /api/v1/esports/games/{game_id}`
- `GET /api/v1/esports/games/{game_id}/draft`
- `GET /api/v1/esports/games/{game_id}/participants`
- `GET /api/v1/esports/teams`
- `GET /api/v1/esports/teams/{team_id}`
- `GET /api/v1/esports/teams/{team_id}/recent`
- `GET /api/v1/esports/teams/{team_id}/champions`
- `GET /api/v1/esports/players/{player_id}`
- `GET /api/v1/esports/players/{player_id}/comfort`
- `GET /api/v1/esports/players/{player_id}/games`
- `GET /api/v1/esports/champions/{champion_id}/pro-stage`
- `GET /api/v1/esports/champions/{champion_id}/matchups`
- `GET /api/v1/esports/counterpicks`
- `GET /api/v1/esports/sources`
- `GET /api/v1/esports/coverage`
- `POST /api/v1/esports/refresh`
- `POST /api/v1/esports/ingest`

Regla operativa: si falta una capa o fuente, devolver `200` con `gaps`, no 500.

## Compliance

- No hay endpoints de asistencia en vivo durante partidas.
- VODs: solo metadata. Nunca se descarga ni rehostea video.
- Gol.gg respeta `robots.txt` y `min_delay >= 4s`.
- Leaguepedia usa User-Agent identificable con email de contacto y `min_delay >= 2s`.
- Si una fuente exige captcha/login, el adapter debe reportar gap y no intentar bypass.
- Stubs comerciales/oficiales no se activan sin contrato, token o production key.

## Verificacion

```powershell
.venv\Scripts\python.exe -m pytest tests/esports_research -q
.venv\Scripts\python.exe -m pytest tests/test_no_mojibake.py -q
.venv\Scripts\python.exe -m ruff check src tests scripts
python scripts/run_api.py
python scripts/visual_smoke.py http://localhost:8000/esports/
```
