# Decisión de Arquitectura

**Fecha:** 2026-04-23

## Contexto

El repositorio contiene múltiples componentes (CLI, API Server, Meta Analyzer, Draft Advisor, Splash Viewer) que inicialmente parecen proyectos independientes pero comparten:
- Un único `requirements.txt`
- El paquete Python `riot_lol_cli` bajo `src/`
- Imports cruzados (meta_analyzer → api.py → database)
- Datos compartidos en `data/`
- Templates compartidos en `templates/`
- Un único entry point (`main.py`)

## Decisión: Proyecto Único Reorganizado

**NO se trata de un monorepo multi-proyecto.** Es un **único proyecto Python con múltiples subsistemas**.

### Justificación

1. **Lenguaje único:** Todo es Python 3.9+
2. **Package único:** Todo vive bajo `src/riot_lol_cli/`
3. **Dependencias compartidas:** Un solo `requirements.txt`
4. **Imports cruzados:** meta_analyzer importa de api.py y database/
5. **No hay manifests independientes:** No hay múltiples `setup.py`, `pyproject.toml`, etc.

### Lo que SÍ se separa

Los directorios de **research y scraping** (`proyecto lol/`, `scraping info del lol/`, `research de mejores junglas profesionales/`, `notas_parche/`, `screenshot tirador segun cliente/`) son realmente proyectos independientes que:
- No comparten código con `riot_lol_cli`
- Usan otros lenguajes (PowerShell, HTML standalone)
- No tienen actividad reciente
- No son referenciados por ningún import

**Disposición:** Archivados en `_archive/`. Si en el futuro Dario quiere moverlos a repos separados, ya están en carpetas autocontenidas.

### Candidatos a Split (futuro)

El **Draft Advisor** es el subsistema más independiente:
- No importa de meta_analyzer ni database
- Tiene su propio frontend SPA (`static/`)
- Tiene su propio server FastAPI
- Datos autocontenidos en `data/draft_advisor/`

**Recomendación:** Si el Draft Advisor crece significativamente, considerar extraerlo a un repo separado. Por ahora se mantiene en `src/riot_lol_cli/draft_advisor/` porque comparte el namespace del paquete.

## Estructura Elegida

```
Proyecto único "riot_lol_cli" con:
├── src/riot_lol_cli/      → código fuente (paquete Python)
├── templates/             → templates Jinja2
├── data/                  → datos y cache
├── assets/                → assets estáticos
├── scripts/               → scripts de utilidad
├── docs/                  → documentación consolidada
├── config/                → configuración
├── _archive/              → proyectos legacy preservados
└── _quarantine/           → archivos pendientes de revisión
```
