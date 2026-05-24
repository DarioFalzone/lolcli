# Engineering Standards

## Python

- Python 3.9+ (CI corre 3.9). PEP 8, 4 espacios, line length 120.
- `from __future__ import annotations` en todo archivo que use pipe-union (`X | None`). Guard: `tests/test_python39_annotations.py`.
- f-strings, type hints donde ayuden, docstrings en espanol si el archivo ya lo esta.
- Logging para librerias/servidores; `click.echo()` solo en CLI.
- FastAPI: exponer `create_app()` y `app = create_app()`. Estado mutable en `app.state`, no singletons globales.
- Pydantic V2 para payloads complejos en `src/riot_lol_cli/schemas/`; evitar dict access fragil.
- Paths runtime: usar `src/riot_lol_cli/paths.py`, no `Path(__file__)` ad-hoc.

## Encoding y mojibake (regla dura)

Todo archivo de texto del repo es UTF-8 sin BOM y sin doble-encoding. **Cero excepciones.** Esto incluye JSON, Python, Markdown, HTML, CSS, etc.

**Tres modos de fallo previstos:**

1. **BOM UTF-8**: `Set-Content -Encoding UTF8` y `Out-File -Encoding UTF8` agregan los bytes `EF BB BF`. Rompe parsers JSON estrictos.
2. **Doble-encoding**: PowerShell legacy lee UTF-8 como Latin-1 y re-codifica. Un caracter de 2 bytes UTF-8 termina ocupando 4 bytes en disco; el archivo es UTF-8 valido pero contiene mojibake al renderizar.
3. **Servidor sin charset**: FastAPI por defecto sirve `application/json` sin `charset=utf-8`. Navegadores interpretan como Latin-1 y rompen tildes en el frontend.

**Prevención:**

- **Edit/Write tools**: respetan UTF-8 sin BOM automáticamente — son seguros.
- **PowerShell**: nunca `-Encoding UTF8`. Para JSON, delegar a Python:
  ```powershell
  .venv\Scripts\python.exe -c "import json; json.dump(data, open('out.json','w',encoding='utf-8'), ensure_ascii=False)"
  ```
- **FastAPI**: forzar `charset=utf-8` con custom response class:
  ```python
  class UTF8JSONResponse(JSONResponse):
      media_type = "application/json; charset=utf-8"
  app = FastAPI(default_response_class=UTF8JSONResponse)
  ```
- **Limpieza retroactiva**: `python scripts/fix_double_encoding.py` revierte mojibake en JSON via reemplazo de patrones conocidos.

**Defensa en profundidad (post-incidente 2026-05-15):**

| Capa | Guard | Qué detecta |
|------|-------|-------------|
| Build-time | `pre-commit` hook (`.pre-commit-config.yaml`) | BOM en JSON nuevos, mojibake, lint |
| Code | `riot_lol_cli.http_utils.UTF8JSONResponse` | Charset HTTP correcto en TODOS los servidores |
| Tests | `tests/test_no_mojibake.py` | Doble-encoding y BOM en src/docs/scripts |
| Tests | `tests/test_encoding_global.py` | JSONs del repo entero, scripts PS, servidores FastAPI |
| Tests | `tests/patch_notes/test_encoding.py` | Subsistema patch_notes E2E |
| CI | Job dedicado `encoding-guard` corre primero | Falla fast antes que lint/test |
| Runtime | `scripts/fix_double_encoding.py` | Reparación retroactiva |
| Runtime | `scripts/check_no_bom.py` | Validación on-demand |

**Patrones obligatorios:**

- **Todos los servidores FastAPI** del paquete usan `UTF8JSONResponse`:
  ```python
  from riot_lol_cli.http_utils import UTF8JSONResponse
  app = FastAPI(default_response_class=UTF8JSONResponse)
  ```
- **Todos los scripts PowerShell** que escriben texto usan UTF-8 sin BOM via
  `[System.IO.File]::WriteAllText($p, $c, [System.Text.UTF8Encoding]::new($false))`.
- **Toda escritura JSON desde scripts** delega a Python (no PowerShell).

**Incidente 2026-05-15**: Ingesta de Mobalytics breakdown generó 3 fallos
simultáneos (BOM, doble-encoding, charset HTTP faltante). Fix: extracción de
`UTF8JSONResponse` a módulo compartido + aplicación a los 6 servidores FastAPI,
`fix_double_encoding.py` con tabla de reemplazos, 12 tests preventivos, hook de
pre-commit, job CI dedicado. Si vuelve a aparecer, ver
`tests/test_encoding_global.py` para diagnóstico exacto y `scripts/fix_double_encoding.py`
para reparación automática.

## Frontend

- Stack vanilla: HTML + CSS + JS. Sin React, bundler ni TypeScript.
- Tokens canonicos: `src/riot_lol_cli/draft_advisor/static/design-system/` (`tokens.css`, `patterns.css`).
- Orden de carga: fonts -> `tokens.css` -> `patterns.css` -> CSS local. CSS local define overrides; **patterns.css gana la cascada por orden** salvo que el override use mayor especificidad.
- Identidad: Hextech dark, gold/cyan, dark mode obligatorio. Microcopy espanol rioplatense con jerga gamer.
- IDs internos canonicos Data Dragon (`Bard`, `MasterYi`); localizar solo `display_name` y copy visible.
- No duplicar paletas: extender `docs/design-system.md`.

### Verificacion visual obligatoria

Despues de cualquier cambio en HTML/CSS/JS de una surface visible, **antes de cerrar la tarea**:

```bash
python scripts/visual_smoke.py http://localhost:<port>/<path>
# abre outputs/visual-smoke/<page>.png con Read tool y verifica:
#  - hero/titulo visible (no cortado, no oculto)
#  - layout sin overlays fantasma (modales que deberian estar cerrados)
#  - tipografia cargada (no fallback)
#  - texto sin mojibake
#  - estados con datos reales (no "Cargando..." perpetuo)
```

Auditar `<link>` order y endpoints en consola **no es suficiente**: cascadas
rotas, modales fantasma y mojibake renderizado solo se ven en el browser.

## Ruff

`pyproject.toml` define line 120, target 3.9, `src = ["src","scripts"]`, exclusiones para `.venv`, `outputs`, `templates`, `projects/legacy`.

```bash
ruff check src tests scripts
ruff format --check src tests scripts
```

## Dead code y artefactos

- No borrar archivos por no aparecer en grep: pueden ser entry points manuales, templates, assets runtime, docs canonicas o standalone projects.
- `outputs/`, caches y DBs locales: artefactos generados, no fuente de verdad.
- Scripts manuales repetibles -> `scripts/`. Diagnosticos one-off -> `projects/dev-scratch/`.
