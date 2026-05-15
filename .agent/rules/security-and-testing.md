# Security And Testing

## Secretos

- **Nunca** commitear secretos. Riot API keys (`RGAPI-*`) viven en `.env` (gitignored).
- `.env.example` con placeholders seguros.
- Código lee `os.getenv("RIOT_API_KEY")` o recibe la key como parámetro.
- Dev keys de Riot expiran cada 24h; rotar desde `https://developer.riotgames.com/`.
- Verificación: `git log --all -p -- .env` y `rg "RGAPI-|api_key\\s*=" src scripts tests`.

## Riot API y scraping

- **Cero requests reales** a Riot en tests.
- **No correr scraping real** con Playwright salvo pedido explícito.
- Respetar `Retry-After` y throttling.

## Database

- SQLite local: `data/meta_analyzer.db`, gitignored. No exponer a red.
- SQLAlchemy ORM + queries parametrizadas.
- `check_same_thread=False` permite FastAPI; writes concurrentes con cuidado.
- Sin Alembic activo: cambios de schema requieren plan explícito.

## Testing

```bash
pytest tests/
pytest -q --cov=src/riot_lol_cli --cov-report=term-missing --cov-fail-under=30
ruff check src tests scripts
ruff format --check src tests scripts
```

CI (Python 3.9): instala `requirements.txt` + `requirements-dev.txt`, corre Ruff y pytest.

## Guards automáticos

- `tests/test_python39_annotations.py`: pipe-union sin `from __future__ import annotations` rompe build.
- `tests/test_no_mojibake.py`: cualquier mojibake o BOM en `src/`/`scripts/`/`templates/` rompe build.
- `tests/draft_advisor/test_data_integrity.py`: IDs no canónicos en perfiles rompen build.
- `tests/meta_scraper/test_adapter_name_maps.py`: drift entre adapters de Meta Scraper.

## Draft Advisor data

- Toda relación en `data/draft_advisor/*.json` usa IDs canónicos de `champion_base.json` (`JarvanIV`, `KogMaw`, `TahmKench`, `LeeSin`).
- `personal_adc_mastery.json` es la fuente editable; la imagen en `KB/` es evidencia visual.
- `excluded_from_recommendations` y `never_top_pick` son preferencias explícitas con prioridad sobre meta/scraping.
- ADC top: requiere meta `S` o `climb_score >= 80`. No top con meta `B` o inferior si hay candidatos `S/A`+`S/A`.
- Jungla top: `S/A` permitidos; `B` solo si no quedan `S/A`; `C` solo en `pool_only` sin mejores opciones.
- `latest_*_tier.json` se considera stale a >72h; no usar como meta vigente sin warning.
- Campeones en snapshot pero sin perfil → reportar como faltantes, no recomendar silenciosamente.

Antes de cerrar tarea Draft Advisor:

```bash
pytest tests/draft_advisor/test_data_integrity.py
pytest tests/draft_advisor
# Si :8001 está levantado:
# GET /api/v1/draft/health  y  GET /api/v1/draft/champions  → ambos 200 antes del front.
```

## Criterio por alcance

- Doc: `git diff --check` + búsqueda de referencias rotas.
- Código: subset relevante de tests.
- Datos/scoring: agregar/actualizar test de integridad.
- API: smoke del endpoint + docs actualizadas.
- **Frontend**: smoke visual con captura (`scripts/visual_smoke.py`) además del lint/test.
