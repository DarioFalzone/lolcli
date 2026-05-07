# Security And Testing

Reglas de seguridad, Riot API, CI y verificaciones.

## Secretos

- Nunca commitear secretos.
- Riot API keys (`RGAPI-*`) viven en `.env`, que debe estar gitignored.
- `.env.example` puede existir con placeholders seguros.
- Codigo debe leer `RIOT_API_KEY` via `os.getenv("RIOT_API_KEY")` o inyeccion explicita.
- Las dev keys de Riot expiran cada 24h; rotarlas desde `https://developer.riotgames.com/`.

## Hallazgos historicos absorbidos

El reporte `SECURITY_FINDINGS.md` fue absorbido aqui. Hallazgos vigentes:

- En 2026-04-23 se detecto una API key local en `.env`; no estaba commiteada, pero `.gitignore` era insuficiente.
- `.gitignore` se amplio para cubrir `.env`, `.venv/`, `__pycache__/`, `*.pyc`, `*.db`, `outputs/`, coverage y artefactos Windows.
- Se creo `.env.example` con placeholders.
- No se encontraron API keys hardcodeadas en codigo fuente; los usos conocidos leen desde entorno o reciben la key como parametro.

Verificacion manual sugerida si hay dudas:

```bash
git log --all -p -- .env
rg "RGAPI-|api_key\\s*=" src scripts tests
```

## Riot API y scraping

- No hacer requests reales a Riot en tests.
- No ejecutar scraping real con Playwright salvo pedido explicito.
- Evitar loops contra Riot sin throttling; respetar `Retry-After`.
- Meta Scraper puede levantar sin Playwright instalado, pero los adapters reales pueden fallar.

## Database

- SQLite local: `data/meta_analyzer.db`, gitignored.
- No exponer la DB a la red.
- Usar SQLAlchemy ORM y queries parametrizadas.
- `check_same_thread=False` permite FastAPI, pero writes concurrentes requieren cuidado.
- No cambiar schema sin plan; no hay Alembic activo.

## Testing

Framework: pytest, pytest-asyncio, pytest-cov.

Comandos principales:

```bash
pytest tests/
pytest -q --cov=src/riot_lol_cli --cov-report=term-missing --cov-fail-under=30
ruff check src tests scripts
ruff format --check src tests scripts
```

CI usa Python 3.9, instala `requirements.txt` y `requirements-dev.txt`, ejecuta Ruff y pytest.

## Draft Advisor Data

- Todo perfil en `data/draft_advisor/*.json` debe usar IDs canonicos de `champion_base.json`, no display names ni alias. Ejemplos: `JarvanIV`, `KogMaw`, `TahmKench`, `LeeSin`.
- En campos relacionales (`best_with`, `worst_into`, `best_with_adcs`, `strong_against_supports`, etc.) validar contra el roster canonico antes de levantar el servidor.
- `data/draft_advisor/personal_adc_mastery.json` es la fuente editable de maestria ADC. La imagen en `KB/` es evidencia visual, no input runtime.
- Respetar `excluded_from_recommendations` y `never_top_pick`: son preferencias explicitas del usuario y tienen prioridad sobre scraping/meta.
- En ADC, no recomendar como top un campeon con meta scraping `B` o inferior si hay candidatos con maestria `S/A` y meta `S/A`.
- `data/meta_scraper/normalized/latest_adc_tier.json` se considera stale si supera 72 horas; no tratarlo como meta vigente sin warning.
- Campeones presentes en el snapshot ADC pero ausentes en `adc_profiles.json` deben reportarse como faltantes de perfil, no recomendarse silenciosamente.
- Cualquier cambio en datos, KB estructurada o scoring del Draft Advisor debe correr:

```bash
pytest tests/draft_advisor/test_data_integrity.py
pytest tests/draft_advisor
```

- Si el servidor local esta levantado, hacer smoke de `GET /api/v1/draft/health` y `GET /api/v1/draft/champions`; ambos deben responder 200 antes de revisar el front.

## Criterio por alcance

- Cambios documentales: `git diff --check` y busqueda de referencias rotas.
- Cambios de codigo: correr suite o subconjunto relevante.
- Cambios de datos/scoring: agregar o actualizar tests/evals del Draft Advisor y correr el test de integridad de datos.
- Cambios de API: smoke test del endpoint y docs actualizadas.
