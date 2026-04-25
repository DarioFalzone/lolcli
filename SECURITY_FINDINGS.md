# Security Findings

Hallazgos de seguridad detectados durante la reorganización del repositorio.

**Fecha:** 2026-04-23
**Auditor:** Claude (agente autónomo)

---

## HALLAZGO 1 — API Key expuesta en `.env` (CRÍTICO)

- **Archivo:** `.env`
- **Variable:** `RIOT_API_KEY`
- **Valor:** `RGAPI-5cc19c70-06fe-4314-9375-2ffe00917e43`
- **Estado en git:** NO commiteada (archivo untracked `??`), pero `.gitignore` NO la excluía
- **Riesgo:** MEDIO — No está en el historial de git, pero la ausencia de `.gitignore` la hacía vulnerable a commit accidental
- **Mitigación aplicada:** `.gitignore` actualizado para excluir `.env`
- **Acción requerida del usuario:**
  1. Rotar la API key en https://developer.riotgames.com/ (las dev keys de Riot expiran cada 24h, probablemente ya expiró)
  2. Verificar que la key nunca fue commitada: `git log --all -p -- .env` (debería dar 0 resultados)

## HALLAZGO 2 — `.gitignore` insuficiente (ALTO)

- **Estado previo:** Solo excluía `.DS_Store`, `Thumbs.db`, `*.log`, `*.tmp`, `*.temp` (5 patrones)
- **Faltaban exclusiones para:**
  - `.env` — credenciales
  - `__pycache__/`, `*.pyc` — bytecode Python (1776+ archivos .pyc en .venv y src/)
  - `.venv/` — entorno virtual completo
  - `*.db` — bases de datos SQLite
  - `outputs/` — HTML generados
  - `coverage/` — reportes de coverage
  - `desktop.ini` — metadata Windows
  - `nul` — artefacto Windows
- **Mitigación aplicada:** `.gitignore` reescrito con cobertura completa

## HALLAZGO 3 — Archivos Python compilados en el repo (BAJO)

- **Descripción:** `src/riot_lol_cli/__pycache__/` está listado como untracked (`??`), lo cual es correcto — no está commiteado
- **Riesgo:** BAJO — los .pyc no contienen secretos pero ensucian el repo
- **Mitigación aplicada:** `__pycache__/` y `*.pyc` agregados a `.gitignore`

## HALLAZGO 4 — Sin `.env.example` (BAJO)

- **Descripción:** No existía un template de variables de entorno para onboarding
- **Mitigación aplicada:** Creado `.env.example` con placeholder seguro

## Resumen de Archivos con Referencias a API Keys

Los siguientes archivos referencian la API key de forma segura (leen de env vars, no hardcodean):
- `src/riot_lol_cli/api.py` — `os.getenv("RIOT_API_KEY")`
- `fetch_matches_full.py` → `scripts/fetch_matches_full.py` — `os.getenv("RIOT_API_KEY")`
- `src/riot_lol_cli/meta_analyzer/data_collector.py` — recibe `api_key` como parámetro
- `src/riot_lol_cli/meta_analyzer/data_collector_db.py` — recibe `api_key` como parámetro
- `scripts/bat/fetch_matches.bat` — lee `.env` en runtime

**No se encontraron API keys hardcodeadas en el código fuente.** El patrón de uso es correcto.
