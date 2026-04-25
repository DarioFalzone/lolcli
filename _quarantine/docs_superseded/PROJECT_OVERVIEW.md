# 📊 LOLCLI - Resumen Completo del Proyecto

## 🎯 Descripción General

**LOLCLI** es una herramienta CLI (Command Line Interface) en Python que integra múltiples utilidades para League of Legends, desarrollada por Deshu. El proyecto combina estadísticas de partidas en tiempo real con un visor interactivo de splash arts.

**Versión Actual:** 1.6.4
**Estado:** Activo y funcional

---

## 🏗️ Arquitectura del Proyecto

```
LOLCLI/
├── 📄 main.py                          # Punto de entrada principal
├── 📦 src/riot_lol_cli/               # Módulo principal
│   ├── cli.py                         # Comandos CLI (Click)
│   ├── api.py                         # Cliente Riot API v5
│   ├── html.py                        # Utilidades para renderizado HTML
│   ├── regions.py                     # Mapeo plataformas → regiones
│   └── templates/                     # Plantillas HTML
│       └── claude-4-5.html           # Plantilla para HTML stats
├── 📥 assets/
│   ├── splash_arts/                  # 2019 splash arts (171 campeones)
│   │   ├── Aatrox/, Ahri/, ... Zeri/
│   │   └── [2019 imágenes PNG]
│   └── splash-viewer-app.js          # App JavaScript para visor
├── 📊 data/
│   ├── splash-manifest.json          # Índice de todos los campeones
│   └── cache/
│       └── matches.json              # Datos de partidas (generados)
├── 📋 templates/                      # Plantillas HTML generadas
│   ├── claude-4-5.html               # Plantilla activa para stats
│   └── [backups y variantes]
├── 📤 outputs/
│   ├── splash-viewer.html            # Visor interactivo (generado)
│   └── claude-4-5/                   # Estadísticas exportadas
├── 🔧 config/
│   └── version.json                  # Versionado automático
├── 📄 requirements.txt                # Dependencias Python
├── 🖥️ [scripts batch]                 # Automatización Windows
│   ├── download_splash_arts.bat
│   ├── fetch_matches.bat
│   ├── regenerar_splash_viewer.bat
│   └── regenerar_html.bat
└── 📖 [documentación]                 # Guías y referencias
    ├── README.md
    ├── QUICK_START.md
    ├── INSTRUCCIONES_API.md
    ├── SPLASH_ARTS_README.md
    └── SPLASH_VIEWER_README.md
```

---

## 🎨 Módulo 1: Splash Arts Gallery (v1.6.4)

### Características
- **2019 splash arts** de 171 campeones de League of Legends
- **Visor interactivo** totalmente funcional offline
- **Filtros avanzados:** Color, badges (Prestige, Legacy, etc.), familias, favoritos
- **Navegación A-Z** con búsqueda incremental
- **Modo filmstrip** (fullscreen) con navegación
- **Comparador** de 2-4 skins side-by-side
- **Presenter Mode** con autoplay y velocidad ajustable

### Flujo de Uso

1. **Descargar Assets** (primera vez)
   ```bash
   python download_splash_arts.py
   ```
   - Descarga de Data Dragon CDN (sin API key)
   - Guarda en `assets/splash_arts/` organizados por campeón
   - ~2019 imágenes totales

2. **Generar Manifest**
   ```bash
   python src/riot_lol_cli/cli.py build-splash-manifest
   ```
   - Lee `assets/splash_arts/`
   - Extrae paleta de colores con PIL
   - Detecta badges especiales
   - Genera `data/splash-manifest.json`

3. **Generar Visor HTML**
   ```bash
   python src/riot_lol_cli/cli.py generate-splash-viewer
   ```
   - Templatea `splash-viewer.html` con manifest
   - Carga JavaScript interactivo
   - Genera en `outputs/splash-viewer.html`

4. **Abrir y Usar**
   - Doble clic en `outputs/splash-viewer.html`
   - Búsqueda incremental
   - Filtros dinámicos
   - Hotkeys: J/K (navegar), H (home), F (fullscreen), ? (ayuda)

### Archivo Clave: splash-manifest.json

```json
{
  "champions": [
    {
      "id": "Aatrox",
      "name": "Aatrox",
      "count": 13,
      "skins": [
        {
          "num": 0,
          "name": "Classic",
          "path": "assets/splash_arts/Aatrox/0.jpg",
          "colors": { "primary": "#c21000", "palette": [...] },
          "badges": ["Classic"]
        },
        ...
      ]
    },
    ...
  ],
  "version": "1.6.4"
}
```

---

## 📊 Módulo 2: Match History & Stats

### Características
- Consulta **historial completo de partidas** (últimos N)
- **Estadísticas detalladas:** KDA, items, runas, hechizos, daño
- **Exportación a HTML** con diseño Hextech premium
- Soporta **Riot ID** (nombre#tag) automáticamente

### Flujo de Datos

```
Usuario: "Deshu#LAS"
  ↓
[fetch_matches_full.py]
  ↓
RiotClient (api.py)
  ├─ Account-V1: Riot ID → PUUID
  ├─ Summoner-V4: PUUID → Datos invocador
  ├─ Match-V5: PUUID → Match IDs
  └─ Para cada Match:
      ├─ Match-V5: Match ID → Datos partida
      └─ Data Dragon: Catálogos (items, runas, hechizos)
  ↓
[data/cache/matches.json] - Datos estructurados
  ↓
[cli.py generate-html]
  ↓
[outputs/claude-4-5/<slug>.html] - HTML exportado
```

### Endpoints Riot API Utilizados

| Endpoint | Uso |
|----------|-----|
| **Account-V1** | `GET /riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}` → PUUID |
| **Summoner-V4** | `GET /lol/summoner/v4/summoners/by-puuid/{puuid}` → Nivel, icono |
| **Match-V5** | `GET /lol/match/v5/matches/by-puuid/{puuid}/ids` → Lista de matches |
| **Match-V5** | `GET /lol/match/v5/matches/{matchId}` → Detalles completos |
| **Data Dragon** | Versiones, items, runas, hechizos (sin API key) |

### Comando de Uso

```bash
# Opción 1: Con variable de entorno
export RIOT_API_KEY="RGAPI-xxxxxxxx"
python main.py --platform la2 --summoner "Deshu#LAS" --count 10

# Opción 2: Con argumento
python main.py --platform la2 --summoner "Deshu#LAS" --count 10 --api-key "$RIOT_API_KEY"

# Opción 3: Último mes completo
python main.py --platform la2 --summoner "Deshu#LAS" --last-month

# Opción 4: Con exportación HTML
python main.py --platform la2 --summoner "Deshu#LAS" --count 10 --html-template "claude-4-5"
```

### Plataformas Soportadas

| Región | Plataformas | Ruta Regional |
|--------|-------------|--------------|
| **Americas** | na1, br1, la1, la2, oc1 | americas |
| **Europe** | euw1, eun1, tr1, ru | europe |
| **Asia** | kr, jp1 | asia |

---

## 🔑 Gestión de API Key

### Formas de Proporcionar API Key (orden de búsqueda)

1. **Variable de entorno** `RIOT_API_KEY`
   ```bash
   export RIOT_API_KEY="RGAPI-xxxx"
   ```

2. **Archivo `.env`** en raíz
   ```ini
   RIOT_API_KEY=RGAPI-xxxx
   ```

3. **Archivo `config/api_key.txt`**
   ```
   RGAPI-xxxx
   ```

4. **Archivo `api_key.txt`** en raíz
   ```
   RGAPI-xxxx
   ```

### Obtener API Key

1. Ir a https://developer.riotgames.com/
2. Iniciar sesión con cuenta Riot
3. Copiar **Development API Key** (válida 24h)

---

## 🛠️ Scripts de Automatización (Windows .bat)

### 1. `download_splash_arts.bat`
Descarga todos los splash arts de Data Dragon
```batch
.\download_splash_arts.bat
```

### 2. `fetch_matches.bat`
Obtiene datos de partidas desde Riot API
```batch
.\fetch_matches.bat
```
- Busca RIOT_API_KEY en .env o variables de entorno
- Ejecuta `fetch_matches_full.py`

### 3. `regenerar_splash_viewer.bat`
Regenera el visor HTML completo
```batch
.\regenerar_splash_viewer.bat
```
- Build manifest
- Genera HTML
- Abre en navegador

### 4. `regenerar_html.bat`
Regenera HTML de estadísticas
```batch
.\regenerar_html.bat
```

---

## 📦 Dependencias

```
click>=8.0.0        # Framework CLI
requests>=2.25.0    # HTTP client
Pillow               # Procesamiento de imágenes
```

Instalar:
```bash
pip install -r requirements.txt
```

---

## 🔄 Flujos de Trabajo Típicos

### Workflow 1: Usar el Visor de Splash Arts

```bash
# Primera vez (descargar todo)
python download_splash_arts.py

# Generar visor
.\regenerar_splash_viewer.bat

# Usar
Doble clic en outputs/splash-viewer.html
```

### Workflow 2: Obtener Stats de Jugador

```bash
# Configurar API key
setx RIOT_API_KEY "tu-api-key"

# Obtener datos
python fetch_matches_full.py

# Exportar a HTML
python src/riot_lol_cli/cli.py generate-html

# Abrir
start outputs\claude-4-5\deshu-claude-4-5.html
```

### Workflow 3: Actualización Completa

```bash
# Todo-en-uno
.\fetch_matches.bat
.\regenerar_html.bat
```

---

## 🎯 Casos de Uso

1. **Jugador Casual**: Descargar splash arts → Disfrutar visor offline
2. **Jugador Competitivo**: Monitorear stats de partidas → Exportar reportes
3. **Streamer**: Generar overlays con stats
4. **Content Creator**: Comparador de skins para videos
5. **Desarrollador**: Base para bot Discord/APIs personalizadas

---

## 🐛 Manejo de Errores

### Rate Limit (429)
- Implementa retry automático con backoff exponencial
- Respeta header `Retry-After` de Riot
- Máximo 3 reintentos por defecto

### API Key Inválida
```
❌ No autorizado (401/403). Detalle: ...
```
→ Verificar API key válida en https://developer.riotgames.com/

### Recurso No Encontrado (404)
- Invocador no existe
- Partida borrada
- Región incorrecta

---

## 📊 Estadísticas Actuales

- **Campeones:** 171
- **Splash Arts:** 2019 imágenes
- **Versión:** 1.6.4
- **Estado:** ✅ Funcional
- **Soporte Offline:** ✅ Sí (visor HTML)
- **API Key Requerida:** ✅ Solo para Match History

---

## 🔗 Recursos Clave

- **Riot Developer Portal:** https://developer.riotgames.com/
- **Riot API Docs:** https://developer.riotgames.com/docs/lol
- **Data Dragon CDN:** https://ddragon.leagueoflegends.com/
- **League of Legends:** https://www.leagueoflegends.com/

---

## 📝 Notas de Desarrollo

### Versiones Python Soportadas
- Python 3.9+

### Librerías Internas
- `Click` - Framework para CLI moderno
- `Requests` - Cliente HTTP robusto
- `PIL/Pillow` - Procesamiento de imágenes
- `Pathlib` - Manejo de rutas

### Patrones Implementados
- **CLI modular:** Comandos desacoplados con Click
- **Caching:** JSON persistente de datos
- **Rate limiting:** Manejo automático de 429
- **Versionado:** Incremental automático

---

**Última actualización:** 11 de enero de 2026
**Desarrollador:** Deshu
**Estado:** Mantenido y activo ✅
