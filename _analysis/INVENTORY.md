# Inventario del Repositorio

**Fecha:** 2026-04-23
**Herramienta:** Análisis automatizado por Claude

---

## Estadísticas Globales

| Métrica | Valor |
|---------|-------|
| Archivos totales (sin .venv) | ~800+ |
| Archivos Python (.py) fuente | ~30 |
| Archivos Python en .venv | ~1,760 |
| Documentación (.md) | 61 |
| Splash arts (.jpg) | 2,019 |
| Iconos de ítems (.png) | 623 |
| Templates/outputs HTML | 17 |
| Archivos JSON | 20+ |
| Scripts (.bat/.sh/.ps1) | 12+ |
| Base de datos SQLite | 1 (217KB) |

## Distribución por Extensión

| Extensión | Cantidad | Tipo |
|-----------|----------|------|
| .jpg | 2,019 | Splash arts de campeones |
| .py (fuente) | ~30 | Código Python del proyecto |
| .py (.venv) | ~1,760 | Dependencias instaladas |
| .pyc | ~1,776 | Bytecode Python (en .venv) |
| .png | 623 | Iconos de ítems |
| .md | 61 | Documentación Markdown |
| .json | 20+ | Configuración y datos |
| .html | 17 | Templates y outputs |
| .bat | 12 | Scripts batch Windows |
| .txt | 54 | Archivos de texto |
| .db | 1 | Base de datos SQLite |
| .zip | 1 | Archivo comprimido |

## Proyectos / Subsistemas Detectados

| Proyecto | Path | Lenguaje | Framework | Estado | Último commit |
|----------|------|----------|-----------|--------|---------------|
| CLI Core | `src/riot_lol_cli/cli.py` | Python | Click, Jinja2 | Activo | 2025-10-22 |
| Riot API Client | `src/riot_lol_cli/api.py` | Python | requests | Activo | 2025-10-22 |
| API Server | `src/riot_lol_cli/api_server.py` | Python | FastAPI | Activo | 2025-10-22 |
| Meta Analyzer | `src/riot_lol_cli/meta_analyzer/` | Python | SQLAlchemy | Activo | 2025-10-22 |
| Draft Advisor | `src/riot_lol_cli/draft_advisor/` | Python | FastAPI, Pydantic | Activo | 2025-10-22 |
| Dashboard | `src/riot_lol_cli/dashboard*.py` | Python | HTML/JS | Activo | 2025-10-22 |
| Database | `src/riot_lol_cli/database/` | Python | SQLAlchemy | Activo | 2025-10-22 |
| Splash Viewer | CLI commands + templates | Python/HTML | Jinja2 | Activo | 2025-10-22 |

### Proyectos Legacy (Archivados)

| Proyecto | Path Original | Lenguaje | Estado |
|----------|---------------|----------|--------|
| Patch Notes Scraper | `proyecto lol/` | HTML, PowerShell | Abandonado |
| DDragon Item Scraper | `scraping info del lol/` | PowerShell | Abandonado |
| Jungler Research | `research de mejores junglas profesionales/` | HTML, MD | Abandonado |
| Patch Notes Fetcher | `notas_parche/` | PowerShell | Abandonado |
| ADC Screenshots | `screenshot tirador segun cliente/` | PNG | Abandonado |

## Archivos Huérfanos Detectados (Pre-reorganización)

| Archivo | Ubicación | Disposición |
|---------|-----------|-------------|
| `nul` | raíz | → `_quarantine/` (Windows artifact, 0 bytes) |
| `desktop.ini` | raíz | → `_quarantine/` (Windows metadata) |
| `lolitems.zip` | raíz | → `_quarantine/` (8MB, duplica imagenes_lol_items/) |
| `refernciaPaginas.txt` | raíz | → `_quarantine/` (notas sueltas) |
| `DASHBOARD_STATUS.txt` | raíz | → `_quarantine/` (snapshot superseded) |
| 6 template backups | `templates/` | → `_quarantine/templates_backups/` |
| 1 template backup | `src/riot_lol_cli/templates/` | → `_quarantine/src_template_backup/` |

## Dependencias entre Subsistemas

```
cli.py ──→ api.py (fetch online)
       ──→ templates/ (rendering)

api_server.py ──→ database/models.py
              ──→ dashboard.py, dashboard_enhanced.py

meta_analyzer/ ──→ api.py (data_collector.py)
               ──→ database/models.py (data_collector_db.py)

draft_advisor/ ──→ data/draft_advisor/*.json (self-contained)

database/ ──→ standalone (SQLAlchemy)
```

## Escaneo de Secretos

| Hallazgo | Archivo | Severidad | Estado |
|----------|---------|-----------|--------|
| RIOT_API_KEY en .env | `.env` | CRÍTICO | No commiteado, .gitignore actualizado |
| .gitignore insuficiente | `.gitignore` | ALTO | Corregido |
| Sin .env.example | — | BAJO | Creado |

Ver `SECURITY_FINDINGS.md` para detalles completos.
