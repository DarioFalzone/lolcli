# Guía de Inicio Rápido — riot_lol_cli

> Consolidado desde: START_HERE.md, QUICK_START.md, COMIENZA_AQUI.md, LEVANTAMIENTO_COMPLETO.md

## Requisitos Previos

- Python 3.9+
- Una API Key de Riot Games (https://developer.riotgames.com/) — expira cada 24h

## Instalación

```bash
# Crear entorno virtual
python -m venv .venv

# Activar (Windows)
.venv\Scripts\activate

# Activar (Linux/Mac)
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## Configurar API Key

```bash
# Copiar template
cp .env.example .env

# Editar .env y agregar tu key
# RIOT_API_KEY=RGAPI-tu-key-aqui
```

---

## 1. CLI — Match History

Consultar historial de partidas y generar HTML:

```bash
# Consultar últimas 10 partidas
python main.py --platform la2 --summoner "Nombre#TAG"

# Generar HTML con plantilla claude-4-5
python main.py --platform la2 --summoner "Nombre#TAG" --html-template claude-4-5

# Usando datos cacheados
python main.py generate --read-json data/cache/matches.json --html-template claude-4-5
```

**Script rápido (Windows):**
```bash
scripts\bat\regenerar_html.bat
```

---

## 2. Splash Arts Gallery

### Paso 1: Descargar splash arts (solo primera vez)
```bash
python scripts/download_splash_arts.py
```
Descarga 2019 imágenes en `assets/splash_arts/`.

### Paso 2: Generar el visor
```bash
# Windows (automático)
scripts\bat\regenerar_splash_viewer.bat

# Manual
python src/riot_lol_cli/cli.py build-splash-manifest
python src/riot_lol_cli/cli.py generate-splash-viewer
```

### Paso 3: Abrir
Doble clic en `outputs/splash-viewer.html` o:
```bash
start outputs\splash-viewer.html
```

---

## 3. Meta Analyzer

Sistema de detección de meta con anomalías y tier lists.

### Setup inicial
```bash
python scripts/setup_meta_analyzer.py
```
Esto inicializa la BD SQLite, genera datos de demo y crea dashboards.

### Levantar API
```bash
python scripts/run_api.py
```
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Dashboard: http://localhost:8000/dashboard-enhanced

### Generar dashboard standalone
```bash
python scripts/generate_dashboard.py
```
Output: `outputs/meta-analyzer-dashboard-enhanced.html`

---

## 4. Draft Advisor

Motor de recomendación de picks para **ADC y Soporte** en ranked/clash.

```bash
# Levantar servidor (desde la raíz del repo, no desde src/)
python -m riot_lol_cli.draft_advisor.server

# Abrir en browser
start http://localhost:8001/draft
```

Puerto **8001** (separado del Meta Analyzer en 8000).

**Flujo de uso:**
1. Seleccionar Rol Objetivo (ADC / Soporte) en el select inferior izquierdo
2. Ir agregando los picks del equipo aliado con el botón `+` a medida que el draft avanza
3. Agregar picks enemigos en la fila inferior
4. Seleccionar Posición de Pick (Blind / Rotación Temprana / Late Counter) y Tipo de Cola
5. Hacer clic en **Recomendar Pick**
6. La card superior muestra el mejor pick con score, razones y plan de juego
7. Las 3 cards inferiores muestran alternativas

**Datos cargados al levantar:**
- `data/draft_advisor/champion_base.json` — 171 campeones
- `data/draft_advisor/adc_profiles.json` — 24 perfiles ADC detallados
- `data/draft_advisor/support_profiles.json` — 10 perfiles Support (Leona, Nautilus, Thresh, Lulu, Janna, Soraka, Milio, Lux, Pyke, Karma)
- `data/draft_advisor/priority_profiles.json` — 41 perfiles de prioridad
- `data/draft_advisor/scoring_weights.json` — pesos del motor de scoring

---

## 5. Fetch completo de partidas

Para obtener datos completos (daño, oro, visión, etc.):

```bash
# Windows (automático)
scripts\bat\fetch_matches.bat

# Manual
python scripts/fetch_matches_full.py
```

Los datos se guardan en `data/cache/matches.json`.

---

## Scripts Disponibles

| Script | Descripción | Ejecución |
|--------|-------------|-----------|
| `scripts/fetch_matches_full.py` | Fetch completo de partidas desde Riot API | `python scripts/fetch_matches_full.py` |
| `scripts/download_splash_arts.py` | Descarga splash arts de Data Dragon | `python scripts/download_splash_arts.py` |
| `scripts/setup_meta_analyzer.py` | Setup de BD + datos demo + dashboards | `python scripts/setup_meta_analyzer.py` |
| `scripts/generate_dashboard.py` | Genera dashboard enhanced HTML | `python scripts/generate_dashboard.py` |
| `scripts/run_api.py` | Levanta API FastAPI | `python scripts/run_api.py` |
| `scripts/fetch_adc_champions.py` | Obtiene lista de ADCs de Data Dragon | `python scripts/fetch_adc_champions.py` |
| `scripts/verify_adc_tracker.py` | Verifica ADCs en la BD | `python scripts/verify_adc_tracker.py` |
| `scripts/CHECK_DASHBOARD.py` | Verifica estado del dashboard | `python scripts/CHECK_DASHBOARD.py` |

### Batch Scripts (Windows)

| Script | Descripción |
|--------|-------------|
| `scripts/bat/fetch_matches.bat` | Fetch de partidas con validación |
| `scripts/bat/regenerar_html.bat` | Regenera HTML con plantilla claude-4-5 |
| `scripts/bat/regenerar_splash_viewer.bat` | Regenera visor de splash arts |
| `scripts/bat/download_splash_arts.bat` | Descarga splash arts (menú interactivo) |
