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

## Home Hub — Panel Central

**Centro de operaciones** con health checks, lanzamiento on-demand de servicios y acceso a todos los subsistemas.

### Windows (script rápido)
```bash
scripts\bat\home.bat
```

### Manual
```powershell
$env:PYTHONPATH=(Resolve-Path .\src).Path
.\.venv\Scripts\python.exe -m riot_lol_cli.home.server
```

- **URL**: http://localhost:8080
- **Puertos monitoreados**: 8000 (Meta API), 8001 (Draft), 8002 (Meta Scraper), 8003 (Jungle Meta), 8004 (Items Browser)
- **Features**: Health checks cada 30s, botón "Abrir" lanza servicios offline automáticamente, poll hasta 20s, apertura popup-safe y retorno visible al Home Hub desde las UIs integradas

---

## Levantar Todo (todos los servicios)

**Script único** que levanta Home Hub + Meta API + Draft Advisor + Meta Scraper + Jungle Meta + Items Browser, todo en background sin ventanas CMD (logs en `logs/`).

```bash
scripts\bat\levantar_todo.bat
```

Abre automáticamente:
- Home Hub: http://localhost:8080
- Draft Advisor: http://localhost:8001/draft
- Meta Scraper: http://localhost:8002
- Jungle Meta: http://localhost:8003
- Items Browser: http://localhost:8004
- Splash Gallery: outputs\splash-viewer.html

Respeta env vars `LOLCLI_*_PORT` si están definidas.

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

### Paso 1: Actualizar assets Data Dragon
```bash
python scripts/update_ddragon_assets.py
```
Actualiza iconos de items, `assets/data_id_imagen/items_ddragon.csv`, splash arts, catalogo Data Dragon localizado, manifest y `outputs/splash-viewer.html`. No requiere API key.

### Paso 2: Regenerar el visor manualmente
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

El puerto default es `8000`; los scripts rapidos respetan `LOLCLI_META_API_PORT`
si esta definido.

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

Puerto **8001** (separado del Meta Analyzer en 8000). El servidor respeta
`LOLCLI_DRAFT_ADVISOR_PORT` si esta definido.

### Windows / PowerShell

Si el modulo no resuelve desde la raiz del repo, configurar `PYTHONPATH` antes
de levantar el servidor:

```powershell
$env:PYTHONPATH="src"
python -m riot_lol_cli.draft_advisor.server
```

Si hay problemas con el Python global o dependencias como `uvicorn`/`watchfiles`,
usar el interprete del entorno virtual del repo:

```powershell
$env:PYTHONPATH=(Resolve-Path .\src).Path
.\.venv\Scripts\python.exe -m riot_lol_cli.draft_advisor.server
```

Para validar que quedo levantado:

```powershell
Invoke-RestMethod http://127.0.0.1:8001/api/v1/draft/health
```

**Flujo de uso:**
1. Seleccionar Rol Objetivo (ADC / Soporte) en el select inferior izquierdo
2. Ir agregando los picks del equipo aliado con el botón `+` a medida que el draft avanza
3. Agregar picks enemigos en la fila inferior
4. Seleccionar Posición de Pick (Blind / Rotación Temprana / Late Counter) y Tipo de Cola
5. Hacer clic en **Recomendar Pick**
6. La card superior muestra el mejor pick con score, razones y plan de juego
7. Las 3 cards inferiores muestran alternativas

**Datos cargados al levantar:**
- `data/draft_advisor/champion_base.json` — 172 campeones
- `data/draft_advisor/adc_profiles.json` — 32 perfiles ADC detallados
- `data/draft_advisor/support_profiles.json` — 34 perfiles Support
- `data/draft_advisor/priority_profiles.json` — 41 perfiles de prioridad
- `data/draft_advisor/scoring_weights.json` — pesos del motor de scoring

---

## 5. Meta Scraper

Scrapea datos de meta de Support, ADC y jungla desde OP.GG, LoLalytics y U.GG (3 fuentes).
Los snapshots normalizados alimentan opcionalamente el motor de scoring del Draft Advisor.

### Requisitos adicionales
```bash
# Instalar browser de Playwright (el paquete Python ya viene en requirements.txt)
playwright install chromium
```

### Levantar dashboard

**Windows (script rápido):**
```bash
scripts\bat\meta_scraper.bat
```

El script usa `8002` por default y respeta `LOLCLI_META_SCRAPER_PORT` si ya
está definido en el entorno.

**Manual (desde la raíz del repo, con venv activo):**
```powershell
$env:PYTHONPATH=(Resolve-Path .\src).Path
.\.venv\Scripts\python.exe -m riot_lol_cli.meta_scraper.server
```

> Importante: no ejecutar desde `src/` ni con el Python global del sistema.

- Dashboard: http://localhost:8002
- API Docs: http://localhost:8002/docs
- Health: http://localhost:8002/health

### Uso
1. Abrir http://localhost:8002
2. Seleccionar tab **Soporte**, **ADC** o **Jungla**
3. Hacer clic en **Actualizar** para scrapear datos de las 3 plataformas
4. La tier list se actualiza con WR, PR, BR y tier badges (ADC incluye Climb Score)
5. Usar **Total** para el agregado ponderado o una fuente individual para auditar datos crudos
6. Abrir **Gaps** para ver fuentes que fallaron o no entregaron datos limpios
7. Hacer clic en un campeon para ver el desglose por fuente

### Endpoints principales
```bash
# Scrapear Support
curl -X POST http://localhost:8002/api/v1/meta/scrape

# Scrapear ADC (incluye climb_score)
curl -X POST http://localhost:8002/api/v1/meta/scrape/adc

# Scrapear Jungla
curl -X POST http://localhost:8002/api/v1/meta/scrape/jungle

# Leer tier list Support normalizada
curl http://localhost:8002/api/v1/meta/support/tier

# Leer tier list ADC normalizada con climb_score
curl http://localhost:8002/api/v1/meta/adc/tier

# Leer tier list Jungla normalizada
curl http://localhost:8002/api/v1/meta/jungle/tier
```

**Datos guardados en:** `data/meta_scraper/` (raw por plataforma, `normalized/latest_<role>_tier.json`, history y backups de jungla en `normalized/backups/jungle/`)

---

## 6. Jungle Meta

Dashboard de tier list de campeones de jungla por parche con estadísticas (WR, PR, BR), items core y runa keystone.

### Levantar dashboard

**Windows (script rápido):**
```bash
scripts\bat\jungle_meta.bat
```

El script levanta en puerto `8003` (respeta `LOLCLI_JUNGLE_META_PORT` si está definido).

**Manual (desde la raíz del repo):**
```powershell
$env:PYTHONPATH=(Resolve-Path .\src).Path
.\.venv\Scripts\python.exe -m riot_lol_cli.jungle_meta.server
```

- Dashboard: http://localhost:8003
- API Docs: http://localhost:8003/docs
- Health: http://localhost:8003/health

### Uso
1. Abrir http://localhost:8003
2. Ver tier list completa (todos los campeones jungla)
3. Hacer clic en tabs **S**, **A**, **B**, **C** para filtrar por tier
4. Cada card muestra: nombre campeón, WR/PR/BR, items core, runa keystone y razón de fuerza

### Endpoints principales
```bash
# Tier list completa
curl http://localhost:8003/api/v1/jungle/tier-list

# Campeones de un tier específico
curl http://localhost:8003/api/v1/jungle/tier/S
curl http://localhost:8003/api/v1/jungle/tier/A

# Detalle de un campeón
curl http://localhost:8003/api/v1/jungle/champion/XinZhao
```

**Datos:** `data/jungle_meta/patch_26.09.json` (16 campeones jungla por tier)

---

## 7. Items Browser

Catalogo navegable de items de LoL (EN + ES) con filtros por grupo (botas, componentes, legendarios, consumibles, trinkets, jungla, obsoletos) y busqueda por nombre. El browser oculta por defecto variantes duplicadas por mapa/modo de Data Dragon; la API permite auditarlas con `include_variants=true`.

### Setup inicial (database)

```powershell
.\.venv\Scripts\python.exe scripts/update_items_database.py
```

Genera `data/items/database.json` desde Data Dragon (en_US + es_ES) y descarga PNGs faltantes.

### Levantar dashboard

**Windows (script rapido):**
```powershell
scripts\bat\items_browser.bat
```

(Regenera automaticamente la database si no existe.)

El script levanta en puerto `8004` (respeta `LOLCLI_ITEMS_BROWSER_PORT` si esta definido).

**Manual:**
```powershell
$env:PYTHONPATH=(Resolve-Path .\src).Path
.\.venv\Scripts\python.exe -m riot_lol_cli.items_browser.server
```

- Dashboard: http://localhost:8004
- API Docs: http://localhost:8004/docs
- Health: http://localhost:8004/health (incluye version DDragon + counts)

### Endpoints principales
```bash
curl "http://localhost:8004/api/v1/items/all?include_deprecated=false&include_variants=false"
curl http://localhost:8004/api/v1/items/6699           # Voltaic Cyclosword
curl http://localhost:8004/api/v1/items/groups         # buckets por uso
curl "http://localhost:8004/api/v1/items/search?q=voltaic&lang=en"
```

**Datos:** `data/items/database.json` (regenerable con el script).

---

## 8. Fetch completo de partidas

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
| `scripts/update_ddragon_assets.py` | Actualiza items, CSV y splash arts desde Data Dragon | `python scripts/update_ddragon_assets.py` |
| `scripts/download_splash_arts.py` | Descarga splash arts de Data Dragon | `python scripts/download_splash_arts.py` |
| `scripts/setup_meta_analyzer.py` | Setup de BD + datos demo + dashboards | `python scripts/setup_meta_analyzer.py` |
| `scripts/generate_dashboard.py` | Genera dashboard enhanced HTML | `python scripts/generate_dashboard.py` |
| `scripts/run_api.py` | Levanta API FastAPI | `python scripts/run_api.py` |
| `scripts/update_items_database.py` | Genera `data/items/database.json` (Data Dragon EN+ES) | `python scripts/update_items_database.py` |
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
| `scripts/bat/levantar_todo.bat` | Levanta Home Hub, Meta API, Draft Advisor, Meta Scraper, Jungle Meta e Items Browser respetando `LOLCLI_*_PORT` |
| `scripts/bat/meta_scraper.bat` | Levanta Meta Scraper dashboard (puerto 8002) |
| `scripts/bat/jungle_meta.bat` | Levanta Jungle Meta dashboard (puerto 8003) |
| `scripts/bat/items_browser.bat` | Levanta Items Browser dashboard (puerto 8004) |
