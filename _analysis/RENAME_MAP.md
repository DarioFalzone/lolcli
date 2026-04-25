# Rename Map — Mapeo de Renombramientos

**Fecha:** 2026-04-23

## Directorios Renombrados

| Path Original | Path Nuevo | Razón |
|---------------|-----------|-------|
| `proyecto lol/` | `_archive/proyecto_lol/` | Espacios → underscore, archivado |
| `scraping info del lol/` | `_archive/scraping_info_del_lol/` | Espacios → underscore, archivado |
| `research de mejores junglas profesionales/` | `_archive/research_junglas_pro/` | Nombre largo → abreviado, archivado |
| `screenshot tirador segun cliente/` | `_archive/screenshot_tirador/` | Nombre largo → abreviado, archivado |
| `notas_parche/` | `_archive/notas_parche/` | Archivado (nombre preservado) |
| `imagenes_lol_items/` | `assets/items/` | Español → inglés corto, ubicación correcta |
| `data_id_imagen/` | `assets/data_id_imagen/` | Movido a assets/ (nombre preservado) |

## Archivos Movidos

### Datos (raíz → data/)
| Original | Nuevo |
|----------|-------|
| `adc_champions.json` | `data/adc_champions.json` |
| `junglers_list.json` | `data/junglers_list.json` |

### Scripts (raíz → scripts/)
| Original | Nuevo |
|----------|-------|
| `fetch_matches_full.py` | `scripts/fetch_matches_full.py` |
| `download_splash_arts.py` | `scripts/download_splash_arts.py` |
| `setup_meta_analyzer.py` | `scripts/setup_meta_analyzer.py` |
| `generate_dashboard.py` | `scripts/generate_dashboard.py` |
| `CHECK_DASHBOARD.py` | `scripts/CHECK_DASHBOARD.py` |

### Batch Scripts (raíz → scripts/bat/)
| Original | Nuevo |
|----------|-------|
| `fetch_matches.bat` | `scripts/bat/fetch_matches.bat` |
| `regenerar_html.bat` | `scripts/bat/regenerar_html.bat` |
| `regenerar_splash_viewer.bat` | `scripts/bat/regenerar_splash_viewer.bat` |
| `download_splash_arts.bat` | `scripts/bat/download_splash_arts.bat` |

### Documentación (raíz → docs/ o _quarantine/)
| Original | Nuevo |
|----------|-------|
| `START_HERE.md` | `_quarantine/docs_superseded/` (consolidado en docs/getting-started.md) |
| `QUICK_START.md` | `_quarantine/docs_superseded/` (consolidado en docs/getting-started.md) |
| `SPLASH_ARTS_README.md` | `_quarantine/docs_superseded/` (consolidado en docs/splash-viewer.md) |
| `SPLASH_VIEWER_README.md` | `_quarantine/docs_superseded/` (consolidado en docs/splash-viewer.md) |
| `INDEX.md` | `_quarantine/docs_superseded/` (consolidado en README.md) |
| `PROJECT_OVERVIEW.md` | `_quarantine/docs_superseded/` (consolidado en README.md) |
| `CONTEXTO_DEL_REPO.md` | `_quarantine/docs_superseded/` (consolidado en AGENTS.md) |
| `INSTRUCCIONES_API.md` | `_quarantine/docs_superseded/` (consolidado en docs/api-guide.md) |
| `DASHBOARD_CHANGELOG.md` | `docs/changelog/DASHBOARD_CHANGELOG.md` |
| `DASHBOARD_SUMMARY.md` | `docs/changelog/DASHBOARD_SUMMARY.md` |
| `docs/CONTEXTO_BRAIN_ADC_DRAFT_ADVISOR.md` | `docs/draft_advisor/README.md` |

## Archivos NO Renombrados

| Archivo | Razón |
|---------|-------|
| `main.py` | Entry point principal, se queda en raíz |
| `requirements.txt` | Convención estándar, se queda en raíz |
| `.gitignore` | Convención estándar |
| `config/version.json` | Ya estaba bien ubicado |
| `templates/*.html` | Ya estaba bien ubicado |
| `src/riot_lol_cli/` | Estructura de paquete correcta |
