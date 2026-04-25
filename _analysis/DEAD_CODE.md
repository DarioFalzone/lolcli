# Dead Code Analysis

**Fecha:** 2026-04-23

## Metodología

Análisis por inspección de imports y referencias en archivos `.py`, `.bat`, `.html`. Sin ejecución de código.

## Archivos Sin Referencias (candidatos a dead code)

### Confianza ALTA (sin ningún import/reference encontrado)

| Archivo | Razón | Acción Tomada |
|---------|-------|---------------|
| `nul` | Archivo vacío de 0 bytes, artefacto Windows | → `_quarantine/` |
| `desktop.ini` | Metadata de Windows Explorer | → `_quarantine/` |
| `refernciaPaginas.txt` | Notas sueltas, no referenciado | → `_quarantine/` |
| `lolitems.zip` | ZIP sin referencia en código | → `_quarantine/` |
| 6 template backups | Backups históricos, no usados | → `_quarantine/templates_backups/` |

### Confianza MEDIA (referenciado indirectamente o por scripts)

| Archivo | Razón | Disposición |
|---------|-------|-------------|
| `src/riot_lol_cli/templates/claude-4-5.html` | Duplica `templates/claude-4-5.html` (root). Solo usado por `html.py` (que también es dead code). | ✅ Movido a `_quarantine/dead_code_html/templates_src/` (NHR-2: C, 2026-04-24) |
| `src/riot_lol_cli/html.py` (23 líneas) | Verificado: NO importado por ningún módulo. Dead code confirmado. | ✅ Movido a `_quarantine/dead_code_html/html.py` (NHR-3: B, 2026-04-24) |
| `coverage/` directorio | Vacío, sugiere coverage nunca se corrió | MANTENER — será útil cuando haya tests |
| `scripts/CHECK_DASHBOARD.py` | Script de verificación con paths hardcodeados a archivos que ya se movieron | MANTENER — actualizar paths |

### Confianza BAJA (probablemente activo)

| Archivo | Razón | Disposición |
|---------|-------|-------------|
| `data/draft_advisor/audit/` | Archivos de auditoría del KB, referenciados por docs | MANTENER |
| `data/draft_advisor/kb/research/` | Documentos de research del KB | MANTENER |
| `src/riot_lol_cli/draft_advisor/eval_runner.py` | No importado por otros módulos, pero es herramienta de evaluación standalone | MANTENER |

## Código Muerto Dentro de Archivos

### `cli.py` — Posible código muerto
- `TEMPLATES_DIR` y `OUTPUT_DIR` se definen pero también se definen localmente en funciones. Verificar si las constantes globales se usan.

### `api_server.py` — Imports potencialmente sin uso
- Importa `dashboard` y `dashboard_enhanced` pero las funciones pueden no ejecutarse sin la BD.

### `alembic` — Dependencia sin uso
- ✅ Removido de `requirements.txt` en reorg 2026-04-24 (NHR-4: A). Re-agregar cuando se necesiten migraciones reales.

## Resumen

| Categoría | Cantidad | Acción |
|-----------|----------|--------|
| Dead code ALTA confianza | 9 archivos | Ya en `_quarantine/` |
| Dead code MEDIA confianza | 4 items | NEEDS_HUMAN_REVIEW |
| Dead code BAJA confianza | 3 items | Mantener |
| Dependencia sin uso | 1 (alembic) | Considerar remover |
