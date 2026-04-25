# riot_lol_cli

CLI en Python para League of Legends con múltiples subsistemas de análisis y visualización.

**Version:** 1.6.4 | **Python:** 3.9+ | **Licencia:** Privado

---

## Subsistemas

| Subsistema | Descripción | Entry Point |
|------------|-------------|-------------|
| **CLI Match History** | Consulta de partidas, exportación HTML Hextech | `python main.py --platform la2 --summoner "Nombre#TAG"` |
| **Splash Arts Gallery** | Visor interactivo de 2019 splash arts, 171 campeones | `scripts/bat/regenerar_splash_viewer.bat` |
| **Meta Analyzer** | Detección de meta, anomalías, tier lists S/A/B/C/D | `python scripts/setup_meta_analyzer.py` |
| **Dashboard Enhanced** | Dashboard HTML con 4 tabs y filtros interactivos | `python scripts/generate_dashboard.py` |
| **Draft Advisor** | Motor de recomendación de picks ADC | `cd src && python -m riot_lol_cli.draft_advisor.server` |
| **API Server** | Backend REST FastAPI para meta analyzer | `python scripts/run_api.py` |

---

## Quick Start

```bash
# 1. Clonar y entorno virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/Mac

# 2. Dependencias
pip install -r requirements.txt

# 3. API Key (obtener en https://developer.riotgames.com/)
cp .env.example .env
# Editar .env con tu RIOT_API_KEY

# 4. Usar
python main.py --platform la2 --summoner "Nombre#TAG" --html-template claude-4-5
```

Ver [docs/getting-started.md](docs/getting-started.md) para guía completa de cada subsistema.

---

## Estructura del Repositorio

```
LOLCLI/
├── main.py                    # Entry point del CLI
├── requirements.txt           # Dependencias Python
├── .env.example               # Template de variables de entorno
├── AGENTS.md                  # Contexto para agentes de IA
│
├── src/riot_lol_cli/          # Código fuente principal
│   ├── cli.py                 # Comandos Click (generate, build-splash-manifest, etc.)
│   ├── api.py                 # Cliente Riot API (Summoner-V4, Match-V5)
│   ├── api_server.py          # FastAPI backend
│   ├── dashboard.py           # Generador de dashboard HTML
│   ├── dashboard_enhanced.py  # Dashboard mejorado con tabs
│   ├── html.py                # Utilidades de rendering
│   ├── regions.py             # Mapping plataforma → región
│   ├── database/              # SQLAlchemy ORM models
│   ├── meta_analyzer/         # Sistema de detección de meta
│   └── draft_advisor/         # Motor de recomendación ADC
│
├── templates/                 # Plantillas Jinja2 (HTML)
├── config/                    # Configuración (version.json)
├── data/                      # Datos y cache
│   ├── cache/                 # Datos cacheados de partidas
│   ├── draft_advisor/         # KB y perfiles del draft advisor
│   └── splash-manifest.json   # Índice de splash arts
│
├── assets/                    # Assets estáticos
│   ├── splash_arts/           # 2019 splash arts JPG (171 campeones)
│   ├── items/                 # 623 iconos de ítems PNG
│   └── data_id_imagen/        # Mapeo ID-imagen
│
├── scripts/                   # Scripts de utilidad
│   ├── bat/                   # Batch scripts Windows
│   ├── fetch_matches_full.py  # Fetch completo de partidas
│   ├── download_splash_arts.py # Descarga splash arts
│   ├── setup_meta_analyzer.py # Setup BD + datos demo
│   ├── generate_dashboard.py  # Genera dashboard HTML
│   ├── run_api.py             # Levanta API server
│   └── ...
│
├── docs/                      # Documentación
│   ├── getting-started.md     # Guía de inicio rápido
│   ├── api-guide.md           # Guía de API
│   ├── splash-viewer.md       # Guía del visor de splash arts
│   ├── dashboard/             # Docs del dashboard
│   ├── meta_analyzer/         # Docs del meta analyzer
│   ├── adc_tracker/           # Docs del ADC tracker
│   └── draft_advisor/         # Docs del draft advisor
│
├── .agent/rules/              # Reglas para agentes de IA
├── _archive/                  # Proyectos legacy preservados
├── _quarantine/               # Archivos pendientes de revisión
└── _analysis/                 # Reportes de análisis
```

---

## Para Agentes de IA

Leé [`AGENTS.md`](AGENTS.md) primero. Contiene la arquitectura, convenciones, puntos de entrada y gotchas del proyecto. Las reglas transversales están en [`.agent/rules/`](.agent/rules/).

## Para Humanos Nuevos

1. Leé este README
2. Seguí [docs/getting-started.md](docs/getting-started.md) para setup
3. Revisá [docs/api-guide.md](docs/api-guide.md) para la API key
4. Explorá el subsistema que te interese en [docs/](docs/)

## Documentación

| Documento | Descripción |
|-----------|-------------|
| [docs/getting-started.md](docs/getting-started.md) | Setup y primeros pasos |
| [docs/api-guide.md](docs/api-guide.md) | API de Riot + API local |
| [docs/splash-viewer.md](docs/splash-viewer.md) | Visor de splash arts |
| [docs/README.md](docs/README.md) | Índice completo de docs |

## Estado de Reorganización

Este repositorio fue reorganizado el 2026-04-23. Ver:
- [REORGANIZATION_REPORT.md](REORGANIZATION_REPORT.md) — Reporte completo
- [SECURITY_FINDINGS.md](SECURITY_FINDINGS.md) — Hallazgos de seguridad
- [_analysis/](\_analysis/) — Reportes de análisis detallados
