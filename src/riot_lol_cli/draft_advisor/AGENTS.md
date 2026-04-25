# AGENTS.md — Draft Advisor

## Qué es este subsistema

Motor de recomendación de picks ADC para League of Legends. Analiza la composición enemiga y aliada, evalúa amenazas, gaps del equipo y sinergias para recomendar el mejor ADC.

**Estado:** Activo / Producción
**Stack:** FastAPI, Pydantic, Python 3.9+

## Cómo correr

```bash
# Desde el root del repo
cd src && python -m riot_lol_cli.draft_advisor.server

# Acceder
# Frontend: http://localhost:8001/draft
# API docs: http://localhost:8001/docs
# (Puerto 8001 para no colisionar con Meta Analyzer API en 8000)
```

## Estructura de Carpetas

```
draft_advisor/
├── AGENTS.md          # Este archivo
├── __init__.py        # Package init
├── server.py          # FastAPI app entry point (monta static/ y router)
├── api.py             # REST router (/draft/recommend)
├── analyzer.py        # Análisis de composición (gaps, amenazas)
├── scoring.py         # Motor de scoring multi-factor (758 líneas)
├── champion_data.py   # Cargador de datos de campeones (3 tiers)
├── schemas.py         # Modelos Pydantic (GameplayRole, CombatClass, etc.)
├── kb_schemas.py      # Schemas del Knowledge Base
├── kb_retriever.py    # Sistema de recuperación del KB
├── eval_runner.py     # Runner de evaluación con golden drafts
└── static/            # Frontend SPA (index.html, styles.css, app.js)
```

## Puntos de Entrada

- **Server:** `server.py` → crea FastAPI app, monta `/static` y `/assets/splash_arts`
- **API:** `api.py` → `POST /draft/recommend` recibe composición y devuelve recomendaciones
- **Datos:** `champion_data.py` → carga desde `data/draft_advisor/`

## Datos (3 Tiers)

Los datos viven en `data/draft_advisor/` (fuera de este directorio):

1. **Tier 1 — Base:** `champion_base.json` (~170 campeones con roles, clases, tipo de daño)
2. **Tier 2 — ADC Profiles:** `adc_profiles.json` (25-30 ADCs con perfiles detallados)
3. **Tier 3 — Priority Profiles:** `priority_profiles.json` (30-40 no-ADCs con impacto en draft)

Otros archivos de datos:
- `scoring_weights.json` — pesos del algoritmo de scoring
- `data_manifest.json` — metadata de los datos
- `kb/` — Knowledge base con reglas de matchup, arquetipos, overrides de parche

## Scoring System

El motor de scoring (`scoring.py`) evalúa cada ADC candidato con estos factores:

- **Team gaps:** qué le falta al equipo (daño AP, engage, peel, etc.)
- **Enemy threats:** amenazas específicas del equipo rival
- **Draft phase:** blind pick vs early/late pick modifica los pesos
- **Comfort bias:** preferencias del jugador
- **Synergies:** sinergias con el soporte y el resto del equipo

## Dependencias Externas

- **Assets:** `assets/splash_arts/` (root del repo) para imágenes del frontend
- **Sin dependencia del meta_analyzer ni del database module** — completamente self-contained

## Gotchas

1. El server monta `assets/splash_arts/` como estático para el frontend
2. Los datos JSON se cargan al inicio y se cachean en memoria
3. El KB retriever busca en `data/draft_advisor/kb/` con un sistema de taxonomía
4. `eval_runner.py` usa `golden_drafts.json` para testing del motor de scoring
