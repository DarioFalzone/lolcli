# Removal Log — Archivos en Cuarentena

**Fecha:** 2026-04-23
**Decisor:** Claude (agente autónomo)
**Acción requerida:** Dario debe revisar y decidir qué borrar definitivamente.

---

## Instrucciones

Para cada archivo, las opciones son:
- **Borrar:** `rm _quarantine/<path>` (si estás seguro)
- **Restaurar:** `mv _quarantine/<path> <destino_original>`
- **Mantener en cuarentena:** dejar hasta decidir

---

## Artefactos del Sistema

| Archivo en _quarantine/ | Path Original | Razón | Confianza | Acción Sugerida |
|-------------------------|---------------|-------|-----------|-----------------|
| `nul` | `./nul` | Artefacto Windows vacío (0 bytes) | ALTA | Borrar |
| `desktop.ini` | `./desktop.ini` | Metadata Windows Explorer | ALTA | Borrar |
| `lolitems.zip` | `./lolitems.zip` | 8MB, contenido duplicado de imagenes_lol_items/ (ahora assets/items/) | ALTA | Borrar |

## Archivos Sueltos

| Archivo en _quarantine/ | Path Original | Razón | Confianza | Acción Sugerida |
|-------------------------|---------------|-------|-----------|-----------------|
| `refernciaPaginas.txt` | `./refernciaPaginas.txt` | Notas de referencia de sitios LoL, sin uso en código | ALTA | Borrar |
| `DASHBOARD_STATUS.txt` | `./DASHBOARD_STATUS.txt` | Snapshot puntual, info cubierta por DASHBOARD_CHANGELOG.md | MEDIA | Borrar |

## Template Backups

| Archivo en _quarantine/ | Path Original | Razón | Confianza | Acción Sugerida |
|-------------------------|---------------|-------|-----------|-----------------|
| `templates_backups/claude-4-5-backup-20251011-161758.html` | `templates/` | Backup pre-VCS, 6 versiones del mismo día | ALTA | Borrar |
| `templates_backups/claude-4-5-backup-20251011-162019.html` | `templates/` | Idem | ALTA | Borrar |
| `templates_backups/claude-4-5-backup-final-20251011-162136.html` | `templates/` | Idem | ALTA | Borrar |
| `templates_backups/claude-4-5-backup-width-fix-20251011-162254.html` | `templates/` | Idem | ALTA | Borrar |
| `templates_backups/claude-4-5-backup-final2-20251011-162405.html` | `templates/` | Idem | ALTA | Borrar |
| `templates_backups/claude-4-5-backup-td-fix-20251011-162601.html` | `templates/` | Idem | ALTA | Borrar |
| `src_template_backup/claude-4-5.html.backup` | `src/riot_lol_cli/templates/` | Backup antiguo del template src | ALTA | Borrar |

## Documentación Superseded

Estos archivos fueron **consolidados** en documentos nuevos. El contenido no se perdió — fue mergeado.

| Archivo en _quarantine/ | Path Original | Consolidado En | Confianza |
|-------------------------|---------------|----------------|-----------|
| `docs_superseded/START_HERE.md` | `./START_HERE.md` | `docs/getting-started.md` | ALTA |
| `docs_superseded/QUICK_START.md` | `./QUICK_START.md` | `docs/getting-started.md` | ALTA |
| `docs_superseded/INDEX.md` | `./INDEX.md` | `README.md` | ALTA |
| `docs_superseded/PROJECT_OVERVIEW.md` | `./PROJECT_OVERVIEW.md` | `README.md` + `AGENTS.md` | ALTA |
| `docs_superseded/CONTEXTO_DEL_REPO.md` | `./CONTEXTO_DEL_REPO.md` | `AGENTS.md` | ALTA |
| `docs_superseded/INSTRUCCIONES_API.md` | `./INSTRUCCIONES_API.md` | `docs/api-guide.md` | ALTA |
| `docs_superseded/SPLASH_ARTS_README.md` | `./SPLASH_ARTS_README.md` | `docs/splash-viewer.md` | ALTA |
| `docs_superseded/SPLASH_VIEWER_README.md` | `./SPLASH_VIEWER_README.md` | `docs/splash-viewer.md` | ALTA |
| `docs_superseded/docs_INDEX.md` | `docs/INDEX.md` | `docs/README.md` | ALTA |
| `docs_superseded/docs_INDICE_MAESTRO.md` | `docs/INDICE_MAESTRO.md` | `docs/README.md` | ALTA |
| `docs_superseded/docs_COMIENZA_AQUI.md` | `docs/COMIENZA_AQUI.md` | `docs/getting-started.md` | ALTA |
| `docs_superseded/docs_REORGANIZADO.md` | `docs/REORGANIZADO.md` | Histórico, superseded por esta reorg | MEDIA |
| `docs_superseded/docs_RESUMEN_FINAL.md` | `docs/RESUMEN_FINAL.md` | Histórico | MEDIA |
| `docs_superseded/docs_RESUMEN_VISUAL.md` | `docs/RESUMEN_VISUAL.md` | Histórico | MEDIA |
| `docs_superseded/docs_SISTEMA_COMPLETO.md` | `docs/SISTEMA_COMPLETO_LEVANTADO.md` | Histórico | MEDIA |
| `docs_superseded/docs_LEVANTAMIENTO_COMPLETO.md` | `docs/LEVANTAMIENTO_COMPLETO.md` | `docs/getting-started.md` | ALTA |
| `docs_superseded/docs_CHECKLIST_VERIFICACION.md` | `docs/CHECKLIST_VERIFICACION.md` | `docs/getting-started.md` | ALTA |
| `docs_superseded/docs_GUIA_SCRIPTS.md` | `docs/GUIA_SCRIPTS_LEVANTAMIENTO.md` | `docs/getting-started.md` | ALTA |
| `docs_superseded/QUICK_REFERENCE_META_ANALYZER.md` | `docs/meta_analyzer/` | `docs/meta_analyzer/META_ANALYZER_GUIA_COMPLETA.md` | ALTA |
| `docs_superseded/QUICK_START_META_ANALYZER.md` | `docs/meta_analyzer/` | `docs/getting-started.md` | ALTA |
| `docs_superseded/META_ANALYZER_IMPLEMENTATION_SUMMARY.md` | `docs/meta_analyzer/` | Histórico | MEDIA |
| `docs_superseded/META_DETECTION_PROFESSIONAL_ANALYSIS.md` | `docs/meta_analyzer/` | `docs/meta_analyzer/META_DETECTION_SYSTEM.md` | MEDIA |
| `docs_superseded/ADC_TRACKER_QUICK_START.md` | `docs/adc_tracker/` | `docs/getting-started.md` | ALTA |
| `docs_superseded/ADC_TRACKER_SUMMARY.md` | `docs/adc_tracker/` | `docs/adc_tracker/ADC_TRACKER_COMPLETE.md` | ALTA |

---

## Resumen

| Categoría | Cantidad | Acción Sugerida |
|-----------|----------|-----------------|
| Artefactos sistema | 3 | Borrar todos |
| Archivos sueltos | 2 | Borrar todos |
| Template backups | 7 | Borrar todos |
| Docs superseded | 24 | Borrar todos (contenido preservado en docs consolidados) |
| **TOTAL** | **36** | **Borrar 36 archivos** |

### Comando para borrar todo de una vez

```bash
rm -rf _quarantine/
```

**Solo ejecutar después de verificar que los docs consolidados tienen toda la info necesaria.**
