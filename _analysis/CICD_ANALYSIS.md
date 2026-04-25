# Análisis de CI/CD — riot_lol_cli

**Fecha:** 2026-04-24

## Estado Actual

| Aspecto | Estado |
|---------|--------|
| `.github/workflows/` | NO existe |
| GitLab CI | N/A (no se usa GitLab) |
| Pre-commit hooks | NO configurado |
| Linting automatizado | NO configurado |
| Tests automatizados | NO configurado (no hay tests aún) |
| Deploy automatizado | NO aplica (CLI/local) |

**No existe ningún pipeline de CI/CD.** Es una aplicación local + CLI sin deploy continuo, así que el CI debería enfocarse en: lint, smoke tests, y validación del manifest.

## Scripts existentes que se podrían portar a CI

| Script | Path | Función | Equivalente Linux |
|--------|------|---------|-------------------|
| `LEVANTAMIENTO_RAPIDO.bat` | `scripts/bat/` | Setup completo: pip install + setup BD + levanta API | `LEVANTAMIENTO_RAPIDO.sh` (existe ✅) |
| `regenerar_html.bat` | `scripts/bat/` | Regenera HTML desde cache | NO tiene equivalente .sh |
| `regenerar_splash_viewer.bat` | `scripts/bat/` | Regenera visor de splash arts | NO tiene equivalente .sh |
| `fetch_matches.bat` | `scripts/bat/` | Fetch de partidas con `.env` | NO tiene equivalente .sh |
| `download_splash_arts.bat` | `scripts/bat/` | Descarga splash arts | NO tiene equivalente .sh |

**Implicación para CI:** Los runners de Linux (GitHub Actions) no pueden usar `.bat`. Habrá que portar 4 batch scripts a `.sh` si se quieren usar en CI.

## Workflow Propuesto (Específico para este Repo)

### `.github/workflows/ci.yml` — Validación Mínima

```yaml
name: CI
on:
  push:
    branches: [main, refactor/**]
  pull_request:
    branches: [main]

jobs:
  smoke-test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.11', '3.13']
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Smoke test — main.py importa
        run: python -c "import main; print('main.py OK')"

      - name: Smoke test — CLI help
        run: python main.py --help

      - name: Smoke test — RiotClient importa
        run: python -c "from src.riot_lol_cli.api import RiotClient; print('api OK')"

      - name: Smoke test — DatabaseManager inicializa
        run: |
          mkdir -p data
          python -m src.riot_lol_cli.database.models

      - name: Smoke test — Draft Advisor schemas
        run: python -c "from src.riot_lol_cli.draft_advisor.schemas import GameplayRole; print('draft schemas OK')"

      - name: Smoke test — Meta Analyzer modules
        run: python -c "from src.riot_lol_cli.meta_analyzer import anomaly_detector, tier_generator, data_collector; print('meta OK')"

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install ruff
      - run: ruff check src/ scripts/ main.py
```

### `.github/workflows/security.yml` — Auditoría Semanal

```yaml
name: Security
on:
  schedule:
    - cron: '0 6 * * 1'  # Lunes 6am UTC
  workflow_dispatch:

jobs:
  audit-deps:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pip-audit
      - run: pip-audit -r requirements.txt --strict

  detect-secrets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Verificar que .env no esté trackeado
        run: |
          if git ls-files | grep -q "^\.env$"; then
            echo "ERROR: .env está trackeado en git"; exit 1
          fi
      - name: Buscar API keys hardcodeadas
        run: |
          if grep -r "RGAPI-" --include="*.py" --include="*.bat" --include="*.sh" --exclude-dir=_archive --exclude-dir=_quarantine .; then
            echo "ERROR: API key hardcodeada encontrada"; exit 1
          fi
```

### Cuando Haya Tests — `.github/workflows/test.yml`

```yaml
name: Tests
on: [push, pull_request]

jobs:
  pytest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt pytest-cov
      - run: pytest --cov=src/riot_lol_cli --cov-report=xml -v
      - uses: codecov/codecov-action@v4
        if: success()
```

### Cuando Haya Postman Collections — `.github/workflows/api-tests.yml`

```yaml
name: API Tests (Newman)
on: [pull_request]

jobs:
  newman:
    runs-on: ubuntu-latest
    services:
      api:
        image: python:3.11
        ports:
          - 8000:8000
          - 8001:8001
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - name: Setup BD demo
        run: python scripts/setup_meta_analyzer.py --demo
      - name: Levantar Meta Analyzer API
        run: python scripts/run_api.py &
      - name: Levantar Draft Advisor API
        run: cd src && python -m riot_lol_cli.draft_advisor.server &
      - name: Esperar APIs
        run: |
          timeout 30 sh -c 'until curl -s http://localhost:8000 > /dev/null; do sleep 1; done'
          timeout 30 sh -c 'until curl -s http://localhost:8001 > /dev/null; do sleep 1; done'
      - uses: actions/setup-node@v4
      - run: npm install -g newman
      - run: newman run postman/collections/meta-analyzer-api.json -e postman/environments/local.json
      - run: newman run postman/collections/draft-advisor-api.json -e postman/environments/local.json
```

## Pre-commit Hook Recomendado

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: detect-private-key       # Crítico: bloquea .pem, .key, etc.
      - id: check-added-large-files
        args: ['--maxkb=1000']        # Permite hasta 1MB (splash JPGs son ~300KB)
        exclude: '^(assets/splash_arts/|_archive/|_quarantine/)'
      - id: check-merge-conflict
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-yaml

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix]
```

## Prioridades de Implementación

| Prioridad | Item | Esfuerzo |
|-----------|------|----------|
| 🔴 ALTA | Pre-commit con `detect-private-key` (mitiga riesgo de commitear `.env`) | 5 min |
| 🟡 MEDIA | `.github/workflows/ci.yml` con smoke tests | 30 min |
| 🟡 MEDIA | Portar `regenerar_html.bat` etc. a `.sh` para CI | 1 hora |
| 🟢 BAJA | Workflow de tests (cuando haya tests) | bloqueado por testing |
| 🟢 BAJA | Workflow de Newman (cuando haya colecciones) | bloqueado por Postman |

## Smoke Tests Específicos a Validar en CI

Estos tests validan que el reorg no rompió nada:

```bash
# Validar imports después del reorg
python -c "import main"
python -c "from src.riot_lol_cli import api, regions, cli, dashboard, dashboard_enhanced, api_server"
python -c "from src.riot_lol_cli.database import DatabaseManager"
python -c "from src.riot_lol_cli.meta_analyzer import anomaly_detector, tier_generator, data_collector, data_collector_db"
python -c "from src.riot_lol_cli.draft_advisor import api, scoring, analyzer, schemas, server"

# Validar que los scripts corren desde cualquier CWD
cd /tmp && python /path/to/repo/scripts/CHECK_DASHBOARD.py
```
