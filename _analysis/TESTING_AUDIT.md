# Auditoría de Testing

**Fecha:** 2026-04-23
**Auditor:** Claude (agente autónomo)
**Nota:** Auditoría especial para Dario (QA profesional)

---

## Estado Actual

| Aspecto | Estado |
|---------|--------|
| Framework de testing | pytest 7.4+ instalado |
| Tests escritos | **NINGUNO** |
| Directorio tests/ | **NO EXISTE** |
| Coverage reports | Directorio `coverage/` vacío |
| CI/CD con tests | No hay CI/CD configurado |

## Cobertura por Subsistema

| Subsistema | Tests | Coverage | Prioridad |
|------------|-------|----------|-----------|
| API Client (`api.py`) | 0 | 0% | ALTA — core del proyecto |
| CLI (`cli.py`) | 0 | 0% | MEDIA — entrada del usuario |
| Meta Analyzer | 0 | 0% | ALTA — lógica de negocio compleja |
| Draft Advisor | 0 parcial* | 0% | ALTA — motor de scoring crítico |
| Database Models | 0 | 0% | MEDIA — ORM standard |
| Dashboard | 0 | 0% | BAJA — generación HTML |
| Regions | 0 | 0% | BAJA — mapping trivial |

*El Draft Advisor tiene `eval_runner.py` con golden drafts — es un proto-test pero no usa pytest.

## Evaluación del Draft Advisor (eval_runner.py)

El archivo `src/riot_lol_cli/draft_advisor/eval_runner.py` implementa un sistema de evaluación:
- Carga drafts de referencia desde `data/draft_advisor/kb/evals/golden_drafts.json`
- Ejecuta el motor de scoring contra cada draft
- Verifica que las recomendaciones sean consistentes

**Esto es testing de facto pero no está integrado con pytest.** Recomendación: migrar a pytest fixtures.

## Propuestas de Testing

### 1. Tests Unitarios Prioritarios

```python
# tests/test_regions.py — el más simple para empezar
def test_la2_maps_to_americas():
    assert get_regional_route("la2") == "americas"

# tests/test_api.py — mockear requests
def test_get_summoner_handles_404():
    # Mock requests.get para retornar 404
    # Verificar que RiotClient levanta excepción apropiada

# tests/draft_advisor/test_scoring.py — el más valioso
def test_scoring_prefers_ad_when_team_lacks_physical():
    # Crear composición sin daño físico
    # Verificar que ADCs con alto daño físico rankean más alto
```

### 2. Tests de Integración

```python
# tests/meta_analyzer/test_pipeline.py
def test_full_pipeline_with_demo_data():
    # DB in-memory
    # Insertar datos demo
    # Correr anomaly detector
    # Verificar que genera tier list válida
```

### 3. Tests de API (para QA con Postman)

#### Colección: Meta Analyzer API

| Request | Method | URL | Expected |
|---------|--------|-----|----------|
| Health check | GET | `/` | 200 |
| Stats | GET | `/stats` | 200, JSON con champion stats |
| Stats filtrado | GET | `/stats?champion=Jinx` | 200, solo datos de Jinx |
| Matchups | GET | `/matchups` | 200, JSON array |
| Items | GET | `/items?champion=Jinx` | 200, item builds |
| Raw Data | GET | `/raw-data?limit=5` | 200, max 5 registros |
| Dashboard | GET | `/dashboard` | 200, HTML |
| Dashboard Enhanced | GET | `/dashboard-enhanced` | 200, HTML con tabs |

#### Colección: Draft Advisor API

| Request | Method | URL | Body | Expected |
|---------|--------|-----|------|----------|
| Recommend | POST | `/draft/recommend` | `{"allies":["Maokai","Lee Sin","Ahri","Leona"],"enemies":["Ornn","Graves","Syndra","Lulu","Kai'Sa"]}` | 200, top 5 ADCs |
| Empty draft | POST | `/draft/recommend` | `{"allies":[],"enemies":[]}` | 200, general recommendations |
| Invalid champion | POST | `/draft/recommend` | `{"allies":["NoExiste"],...}` | 400 o handling graceful |

### 4. Estructura de Newman para CI

```
postman/
├── collections/
│   ├── meta-analyzer-api.json
│   └── draft-advisor-api.json
├── environments/
│   └── local.json                 # baseUrl: http://localhost:8000
└── run-tests.sh
    # newman run collections/meta-analyzer-api.json -e environments/local.json
```

## Recomendaciones para Dario

### Paso 1: Quick Wins
1. Crear `tests/` con `conftest.py`
2. Escribir tests para `regions.py` (5 minutos, 100% coverage)
3. Migrar `eval_runner.py` a pytest

### Paso 2: API Testing con Postman
1. Crear colección para Meta Analyzer API
2. Crear colección para Draft Advisor API
3. Agregar tests de status code, schema validation, response time
4. Exportar como Newman collections para CI futuro

### Paso 3: Tests de Lógica de Negocio
1. Tests de scoring del draft advisor (lo más crítico)
2. Tests del anomaly detector
3. Tests del tier generator

### Paso 4: CI Pipeline
1. GitHub Actions workflow básico: `pytest --cov`
2. Newman run para API tests
3. Linting con ruff/flake8
