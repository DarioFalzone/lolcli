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

### Home Hub

```bash
python -m riot_lol_cli.home.server
```

**Puerto:** 8080.

**Endpoints principales:**
- `GET /health`
- `GET /api/v1/home/status`
- `GET /api/v1/home/version`
- `POST /api/v1/home/launch/{service_id}`

**Frontend SPA:** http://localhost:8080

### Meta Analyzer API

```bash
python scripts/run_api.py
```

**Endpoints principales:**
- `GET /health`
- `GET /api/v1/stats/latest`
- `GET /api/v1/stats/champion/{champion_name}`
- `GET /api/v1/stats/top-tier`
- `GET /api/v1/anomalies/high-confidence`
- `GET /api/v1/tier-list/current`
- `GET /api/v1/maintenance/status`
- `GET /dashboard` — Dashboard HTML
- `GET /dashboard-enhanced` — Dashboard mejorado con tabs

**Documentación interactiva:** http://localhost:8000/docs

### Draft Advisor API

```bash
python -m riot_lol_cli.draft_advisor.server
```
**Puerto:** 8001 (para no chocar con Meta Analyzer API en 8000 — pueden correr juntos).

**Endpoints principales:**
- `GET /api/v1/draft/health`
- `GET /api/v1/draft/champions`
- `GET /api/v1/draft/champions/adcs`
- `GET /api/v1/draft/champions/supports`
- `POST /api/v1/draft/recommend`
- `GET /api/v1/draft/strategic-triangle/{champion_id}`

**Documentación interactiva:** http://localhost:8001/docs
**Frontend SPA:** http://localhost:8001/draft

### Meta Scraper API

```bash
python -m riot_lol_cli.meta_scraper.server
```

**Puerto:** 8002.

**Endpoints principales:**
- `GET /health`
- `GET /api/v1/meta/support/tier`
- `GET /api/v1/meta/adc/tier`
- `GET /api/v1/meta/jungle/tier`
- `GET /api/v1/meta/adc/champion/{champion_id}`
- `GET /api/v1/meta/jungle/champion/{champion_id}`
- `POST /api/v1/meta/scrape`
- `POST /api/v1/meta/scrape/adc`
- `POST /api/v1/meta/scrape/jungle`

**Frontend SPA:** http://localhost:8002

### Jungle Meta API

```bash
python -m riot_lol_cli.jungle_meta.server
```

**Puerto:** 8003.

**Endpoints principales:**
- `GET /health`
- `GET /api/v1/jungle/tier-list`
- `GET /api/v1/jungle/tier/{tier}`
- `GET /api/v1/jungle/champion/{champion_id}`
- `GET /api/v1/jungle/categories`
- `GET /api/v1/jungle/items/abusers/{item_key}`
- `GET /api/v1/jungle/items/used`

**Frontend SPA:** http://localhost:8003

### Items Browser API

```bash
python -m riot_lol_cli.items_browser.server
```

**Puerto:** 8004.

**Endpoints principales:**
- `GET /health`
- `GET /api/v1/items/all?include_deprecated=false&include_variants=false`
- `GET /api/v1/items/{item_id}`
- `GET /api/v1/items/groups?include_variants=false`
- `GET /api/v1/items/categories`
- `GET /api/v1/items/search?q=&lang=en|es&include_variants=false`

**Frontend SPA:** http://localhost:8004
