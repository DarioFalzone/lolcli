# Análisis de Linting & Formatting — riot_lol_cli

**Fecha:** 2026-04-24
**Métricas:** Tomadas por inspección directa del código en `src/riot_lol_cli/`

## Estado Actual

| Herramienta | Estado |
|-------------|--------|
| Linter (flake8/ruff/pylint) | NO configurado |
| Formatter (black/ruff-format) | NO configurado |
| Import sorter (isort/ruff) | NO configurado |
| Type checker (mypy/pyright) | NO configurado |
| `.editorconfig` | NO existe |
| Pre-commit hooks | NO configurado |
| `pyproject.toml` | NO existe |

## Métricas Reales del Código

### Tamaño del Codebase
- **Total líneas Python en src/**: ~8,000
- **Archivos .py en src/**: 19 (excluyendo `__init__.py`)

### Líneas Largas (>120 chars) — issues por archivo

| Archivo | Líneas >120 chars | Severidad |
|---------|-------------------|-----------|
| `dashboard_enhanced.py` | 14 | 🟡 Media |
| `cli.py` | 10 | 🟡 Media |
| `dashboard.py` | 2 | 🟢 Baja |
| `draft_advisor/scoring.py` | 2 | 🟢 Baja |
| `api.py` | 0 | ✅ |
| `api_server.py` | 0 | ✅ |

**Líneas más largas en `cli.py`:**
- Línea 309: 176 chars
- Línea 292: 165 chars
- Línea 318: 142 chars
- Línea 279: 140 chars
- Línea 350: 138 chars

Casi todas son strings HTML/CSS embebidos. Difíciles de cortar sin afectar legibilidad.

### Type Hints

- **Archivos CON type hints:** 19 (la mayoría — `schemas.py`, `models.py`, `scoring.py`, etc.)
- **Archivos SIN type hints:** 5
  - `__init__.py` (todos los packages — esperable)
  - `draft_advisor/server.py` — sin hints, debería tenerlos

### Estilo de Quotes

`cli.py` tiene **mezcla**: 109 single quotes + 146 double quotes. Inconsistente.

**Convención del proyecto (según `.agent/rules/coding-style.md`):** Comillas dobles.

### Imports

`cli.py` mezcla stdlib y terceros sin separación:
```python
import click           # ← terceros
import json            # ← stdlib
import os              # ← stdlib
from datetime import datetime  # ← stdlib
from pathlib import Path        # ← stdlib
from typing import Dict, ...    # ← stdlib
from PIL import Image           # ← terceros
from collections import Counter # ← stdlib
```

Orden esperado por PEP 8:
1. stdlib (json, os, datetime, pathlib, typing, collections)
2. terceros (click, PIL)
3. locales (`from src.riot_lol_cli...`)

### Print Statements

Hay 8 `print(...)` en archivos top-level de `src/riot_lol_cli/*.py`. Algunos son legítimos (CLI feedback), otros podrían ser debug residual. Auditar antes del primer release.

## Configuración Recomendada (Específica)

### `pyproject.toml`

```toml
[tool.ruff]
line-length = 120
target-version = "py39"
src = ["src", "scripts"]
exclude = [
    "_archive",
    "_quarantine",
    ".venv",
    "outputs",
    "templates",
]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes (unused imports, undefined names)
    "I",   # isort (import order)
    "W",   # pycodestyle warnings
    "UP",  # pyupgrade (modernización Python)
    "B",   # flake8-bugbear (bug-likely patterns)
]
ignore = [
    "E501",  # line too long (handled by formatter)
    "E402",  # module-level import not at top (común en scripts con sys.path hack)
]

[tool.ruff.lint.per-file-ignores]
"scripts/*.py" = ["E402"]  # Scripts con sys.path.insert al inicio
"src/riot_lol_cli/cli.py" = ["E501"]  # HTML/CSS embebido

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### `.editorconfig`

```ini
root = true

[*]
indent_style = space
indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.{json,yml,yaml,toml}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false

[*.bat]
end_of_line = crlf

[Makefile]
indent_style = tab
```

## Plan de Implementación

### Fase 1 — Setup (10 minutos)
```bash
pip install ruff
# Crear pyproject.toml con config arriba
# Crear .editorconfig
```

### Fase 2 — Auto-fix (5 minutos)
```bash
ruff check --fix src/ scripts/ main.py
ruff format src/ scripts/ main.py
```

Esto resuelve automáticamente:
- Imports desordenados (los 19 archivos)
- Imports sin uso
- Quote style inconsistente en `cli.py`
- Trailing whitespace
- Final newlines

### Fase 3 — Issues Manuales (30 minutos)
Después del auto-fix, quedan los manuales:
- Líneas >120 que no son strings (revisar las 28 totales)
- Type hints faltantes en `draft_advisor/server.py` (5 funciones)
- Auditar 8 `print()` en archivos no-CLI

### Fase 4 — Pre-commit Integration
Ver `_analysis/CICD_ANALYSIS.md` sección "Pre-commit Hook Recomendado".

## Issues que NO Resolverá Ruff Auto-fix

1. **Strings HTML/CSS largos en `cli.py` y `dashboard_enhanced.py`** — Requieren refactor manual o exclusión
2. **Lógica de retry en `api.py`** — Estructura, no formato
3. **Funciones largas en `scoring.py` (758 líneas)** — Refactor en helpers más pequeños

## Comandos Útiles

```bash
# Ver todos los issues sin fixear
ruff check src/ --no-fix

# Solo imports
ruff check src/ --select I

# Solo type checking (cuando se agregue mypy)
# pip install mypy
# mypy src/riot_lol_cli/

# Métricas de complejidad
# pip install radon
# radon cc src/riot_lol_cli/draft_advisor/scoring.py
```
