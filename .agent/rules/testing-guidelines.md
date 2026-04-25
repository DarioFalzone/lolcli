# Testing Guidelines — riot_lol_cli

## Estado Actual

- **Framework:** pytest 7.4+ con pytest-asyncio
- **Tests existentes:** Ninguno implementado todavía
- **Coverage:** Directorio `coverage/` existe pero está vacío

## Estructura Propuesta

```
tests/
├── conftest.py              # Fixtures compartidos
├── test_api.py              # Tests del Riot API client
├── test_cli.py              # Tests de comandos CLI
├── test_regions.py          # Tests de mapping de regiones
├── meta_analyzer/
│   ├── test_anomaly_detector.py
│   ├── test_tier_generator.py
│   └── test_data_collector.py
├── draft_advisor/
│   ├── test_scoring.py
│   ├── test_analyzer.py
│   └── test_champion_data.py
└── database/
    └── test_models.py
```

## Cómo Correr Tests

```bash
# Todos los tests
pytest

# Con coverage
pytest --cov=src/riot_lol_cli --cov-report=html

# Un módulo específico
pytest tests/draft_advisor/test_scoring.py -v
```

## Tipos de Tests

### Unit Tests
- Testear funciones puras sin side effects
- Mockear la API de Riot (no hacer llamadas reales en tests)
- Mockear la BD con SQLite in-memory

### Integration Tests
- Testear flujo completo de data_collector → database → tier_generator
- Usar BD SQLite in-memory

### Evaluation Tests (Draft Advisor)
- Usar `data/draft_advisor/kb/evals/golden_drafts.json` como test suite
- `eval_runner.py` ya implementa este patrón
- Verificar que las recomendaciones son consistentes

## Para QA (Dario)

### Testing de APIs con Postman

Los endpoints del API Server son ideales para testing con Postman/Newman:

**Colección sugerida: Meta Analyzer API**
```
GET /stats
GET /matchups?champion=Jinx
GET /items?champion=Jinx
GET /raw-data?limit=10
GET /dashboard
GET /dashboard-enhanced
```

**Colección sugerida: Draft Advisor API**
```
POST /draft/recommend
Body: {
  "allies": ["Maokai", "Lee Sin", "Ahri", "Leona"],
  "enemies": ["Ornn", "Graves", "Syndra", "Lulu", "Kai'Sa"],
  "phase": "late",
  "comfort_picks": ["Jinx", "Kai'Sa"]
}
```

### Estructura para Newman (CI)
```
postman/
├── meta-analyzer-api.postman_collection.json
├── draft-advisor-api.postman_collection.json
└── environment.postman_environment.json
```

## Convenciones

- Nombres de tests: `test_<qué_hace>_<condición>` → `test_scoring_returns_top5_by_default`
- Un assert por test cuando sea posible
- Usar fixtures para setup compartido
- No testear implementación interna, testear comportamiento
