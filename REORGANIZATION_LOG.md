# Reorganization Log

Registro de decisiones y movimientos realizados durante la reorganización del repositorio.

**Fecha de inicio:** 2026-04-23
**Branch:** `refactor/repo-reorganization-20260423`
**Autor:** Claude (agente autónomo) a pedido de Dario

---

## FASE 0 — Preparación (2026-04-23)

- Creada branch `refactor/repo-reorganization-20260423`
- Creada carpeta `_quarantine/` para candidatos a borrado
- Creada carpeta `_archive/` para proyectos viejos/abandonados
- Creada carpeta `_analysis/` para reportes de análisis
- Creado este archivo `REORGANIZATION_LOG.md`

## FASE 1 — Security Fixes (2026-04-23)

- **HALLAZGO CRÍTICO:** `.env` contiene `RIOT_API_KEY` en texto plano y NO estaba en `.gitignore`
- Reescrito `.gitignore` con exclusiones comprehensivas (`.env`, `__pycache__/`, `.venv/`, `*.db`, `outputs/`, etc.)
- Creado `.env.example` como template seguro
- Creado `SECURITY_FINDINGS.md` documentando hallazgos

## FASE 2 — Quarantine Artifacts (2026-04-23)

Archivos movidos a `_quarantine/`:
| Archivo Original | Razón |
|------------------|-------|
| `nul` | Artefacto Windows vacío (0 bytes) |
| `desktop.ini` | Metadata de Windows Explorer |
| `lolitems.zip` | Archivo ZIP de 8MB, contenido duplicado de imagenes_lol_items/ |
| `refernciaPaginas.txt` | Notas sueltas de referencia, sin uso en código |
| `DASHBOARD_STATUS.txt` | Snapshot puntual, superseded por changelog |
| `templates/claude-4-5-backup-*` | Backups viejos de plantillas (hay VCS) |
| `src/riot_lol_cli/templates/claude-4-5.html.backup` | Backup redundante |

## FASE 3 — Archive Legacy Dirs (2026-04-23)

Directorios movidos a `_archive/`:
| Directorio Original | Nuevo Path | Razón |
|---------------------|-----------|-------|
| `proyecto lol/` | `_archive/proyecto_lol/` | Proyecto legacy de scraping de patch notes |
| `scraping info del lol/` | `_archive/scraping_info_del_lol/` | Scripts de scraping de DDragon |
| `research de mejores junglas profesionales/` | `_archive/research_junglas_pro/` | Proyecto de research standalone |
| `notas_parche/` | `_archive/notas_parche/` | Scripts PowerShell de notas de parche |
| `screenshot tirador segun cliente/` | `_archive/screenshot_tirador/` | Screenshots de referencia ADC |

## FASE 4 — Move Data Files & Assets (2026-04-23)

| Archivo Original | Nuevo Path | Razón |
|------------------|-----------|-------|
| `adc_champions.json` | `data/adc_champions.json` | Data pertenece a data/ |
| `junglers_list.json` | `data/junglers_list.json` | Data pertenece a data/ |
| `imagenes_lol_items/` | `assets/items/` | Assets de imagen junto a otros assets |
| `data_id_imagen/` | `assets/data_id_imagen/` | CSV de mapeo imagen-ID |

## FASE 5 — Consolidate Scripts (2026-04-23)

Scripts movidos desde raíz a `scripts/`:
| Script Original | Nuevo Path |
|-----------------|-----------|
| `fetch_matches_full.py` | `scripts/fetch_matches_full.py` |
| `download_splash_arts.py` | `scripts/download_splash_arts.py` |
| `setup_meta_analyzer.py` | `scripts/setup_meta_analyzer.py` |
| `generate_dashboard.py` | `scripts/generate_dashboard.py` |
| `CHECK_DASHBOARD.py` | `scripts/CHECK_DASHBOARD.py` |
| `fetch_matches.bat` | `scripts/bat/fetch_matches.bat` |
| `regenerar_html.bat` | `scripts/bat/regenerar_html.bat` |
| `regenerar_splash_viewer.bat` | `scripts/bat/regenerar_splash_viewer.bat` |
| `download_splash_arts.bat` | `scripts/bat/download_splash_arts.bat` |

Batch files actualizados para funcionar desde `scripts/bat/` con `cd /d "%~dp0\..\.."`

## FASE 6 — Consolidate Documentation (2026-04-23)

Documentación consolidada:
| Tema | Doc Autoritativo | Docs Consolidados |
|------|-----------------|-------------------|
| Getting Started | `docs/getting-started.md` | START_HERE.md, QUICK_START.md, COMIENZA_AQUI.md, LEVANTAMIENTO_COMPLETO.md |
| API Guide | `docs/api-guide.md` | INSTRUCCIONES_API.md |
| Splash Viewer | `docs/splash-viewer.md` | SPLASH_ARTS_README.md, SPLASH_VIEWER_README.md |
| Docs Index | `docs/README.md` | docs/INDEX.md, docs/INDICE_MAESTRO.md |
| Dashboard | `docs/changelog/` | DASHBOARD_CHANGELOG.md, DASHBOARD_SUMMARY.md |

Docs originales superseded movidos a `_quarantine/docs_superseded/`

## FASE 7 — AGENTS.md Hierarchy (2026-04-23)

Creados:
- `AGENTS.md` (raíz) — contexto global del proyecto
- `src/riot_lol_cli/draft_advisor/AGENTS.md` — contexto del Draft Advisor
- `.agent/rules/coding-style.md`
- `.agent/rules/commit-conventions.md`
- `.agent/rules/testing-guidelines.md`
- `.agent/rules/security-guidelines.md`
- `.agent/rules/glossary.md`
- `.agent/rules/ai-agent-guidelines.md`

## FASE 8 — README.md (2026-04-23)

- Reescrito `README.md` raíz como mapa navegable del repositorio

## FASE 9 — Analysis Reports (2026-04-23)

Generados en `_analysis/`:
- `INVENTORY.md` — inventario completo de archivos
- `ARCHITECTURE_DECISION.md` — decisión de arquitectura
- `DEPENDENCIES_ANALYSIS.md` — análisis de dependencias
- `TESTING_AUDIT.md` — auditoría de testing (especial para QA)
- `DEAD_CODE.md` — archivos sin referencias
- `RENAME_MAP.md` — mapeo de renombramientos

## FASE 10 — Final Cleanup (2026-04-23)

- Creado `_quarantine/REMOVAL_LOG.md` con tabla completa
- Creados `ARCHIVE_NOTE.md` en cada subdirectorio de `_archive/`
