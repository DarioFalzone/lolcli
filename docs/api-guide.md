# Guía de API — riot_lol_cli

> Consolidado desde: INSTRUCCIONES_API.md

## Riot Games API

### Obtener API Key

1. Ir a https://developer.riotgames.com/
2. Registrarse/loguearse con cuenta de Riot
3. Copiar la "Development API Key" (expira cada 24 horas)
4. Guardarla en `.env`:
   ```
   RIOT_API_KEY=RGAPI-tu-key-aqui
   ```

### Endpoints Utilizados

| API | Endpoint | Uso |
|-----|----------|-----|
| Summoner-V4 | `GET /lol/summoner/v4/summoners/by-name/{name}` | Obtener datos del invocador |
| Account-V1 | `GET /riot/account/v1/accounts/by-riot-id/{name}/{tag}` | Resolver Riot ID a PUUID |
| Match-V5 | `GET /lol/match/v5/matches/by-puuid/{puuid}/ids` | Listar IDs de partidas |
| Match-V5 | `GET /lol/match/v5/matches/{matchId}` | Detalle de una partida |
| Data Dragon | `https://ddragon.leagueoflegends.com/cdn/...` | Assets estáticos (no requiere key) |

### Plataformas y Regiones

| Region | Plataformas |
|--------|------------|
| americas | `na1`, `br1`, `la1`, `la2`, `oc1` |
| europe | `euw1`, `eun1`, `tr1`, `ru` |
| asia | `kr`, `jp1` |

### Rate Limiting

- Riot implementa rate limiting por API key
- El cliente (`src/riot_lol_cli/api.py`) maneja reintentos con `Retry-After`
- Si recibís muchos 429, esperá o reducí la frecuencia

## API Local (FastAPI)

### Meta Analyzer API

```bash
python scripts/run_api.py
```

**Endpoints principales:**
- `GET /stats` — Estadísticas generales
- `GET /matchups` — Historial de matchups
- `GET /items` — Análisis de ítems
- `GET /raw-data` — Datos sin filtrar
- `GET /dashboard` — Dashboard HTML
- `GET /dashboard-enhanced` — Dashboard mejorado con tabs

**Documentación interactiva:** http://localhost:8000/docs

### Draft Advisor API

```bash
cd src && python -m riot_lol_cli.draft_advisor.server
```
**Puerto:** 8001 (para no chocar con Meta Analyzer API en 8000 — pueden correr juntos).

**Endpoint principal:**
- `POST /draft/recommend` — Recomendar ADC para el draft

**Documentación interactiva:** http://localhost:8001/docs
**Frontend SPA:** http://localhost:8001/draft
