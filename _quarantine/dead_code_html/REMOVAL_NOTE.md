# Dead Code — html.py + templates_src

**Fecha:** 2026-04-24
**Decisión:** Dario aprobó (NHR-2: C, NHR-3: B)

## Qué se movió

| Archivo Original | Path Original | Path Nuevo |
|------------------|---------------|-----------|
| `html.py` | `src/riot_lol_cli/html.py` | `_quarantine/dead_code_html/html.py` |
| `templates/claude-4-5.html` | `src/riot_lol_cli/templates/claude-4-5.html` | `_quarantine/dead_code_html/templates_src/claude-4-5.html` |

## Por qué

Verificación con grep:
- `html.py` NO está importado por ningún módulo (`grep -rn "from.*html import\|import.*html" src/` → 0 resultados de `riot_lol_cli/html`)
- Las funciones `render_template()` y `ensure_out_dir()` no se usan en ningún lado
- `templates/claude-4-5.html` (758 líneas) en `src/` solo era usado por `html.py`
- El template autoritativo es `templates/claude-4-5.html` en el root (2329 líneas), usado por `cli.py:134`

## Acción sugerida

Borrar definitivamente cuando se confirme que el proyecto sigue funcionando:
```bash
rm -rf _quarantine/dead_code_html/
```
