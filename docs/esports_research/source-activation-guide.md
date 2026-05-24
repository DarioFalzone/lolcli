# Source Activation Guide

## Reglas comunes

- Agregar credenciales via `.env`, nunca commitearlas.
- Mantener User-Agent identificable con email de contacto.
- Respetar `Retry-After`, robots.txt y delays minimos por fuente.
- Si aparece captcha/login, registrar `gap: requires_auth` y detener.
- Tests con fixtures locales y monkeypatch; cero requests reales.

## Stubs

| Source | Para activar |
|--------|--------------|
| `riot_tournament_v5` | Production Riot API key, provider/tournament/code flow y callback HTTPS publico |
| `riot_esports_grid` | Contrato GRID y payload schemas para feed oficial |
| `pandascore` | API token, limites de plan y pruebas de REST/WebSocket |
| `abios` | Contrato, limites 3 req/s burst 5 y ventana de historico |
| `lol_esports_vods` | Selectores oficiales solo para metadata, sin descarga de video |
| `game_client_local` | Uso local de scrims/testing, sin endpoints de consejo en partida |

Cada PR de activacion debe actualizar `data/esports_research/sources.json`,
docs, tests de compliance y bitacora.
