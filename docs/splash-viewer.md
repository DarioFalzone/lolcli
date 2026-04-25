# Splash Arts Gallery — riot_lol_cli

> Consolidado desde: SPLASH_ARTS_README.md, SPLASH_VIEWER_README.md, QUICK_START.md

## Versión: 1.6.4

Visor interactivo de splash arts de League of Legends con navegación avanzada, búsqueda, filtros y vista filmstrip.

## Inicio Rápido

### 1. Descargar splash arts (solo primera vez)
```bash
python scripts/download_splash_arts.py
```
Descarga **2019 imágenes** de **171 campeones** desde Data Dragon CDN en `assets/splash_arts/`.

### 2. Generar el visor
```bash
# Windows (abre automáticamente)
scripts\bat\regenerar_splash_viewer.bat

# Manual
python src/riot_lol_cli/cli.py build-splash-manifest
python src/riot_lol_cli/cli.py generate-splash-viewer
```

### 3. Abrir
Doble clic en `outputs/splash-viewer.html`

---

## Características

### Navegación y Búsqueda
- **Navegación A-Z lateral**: alfabeto interactivo con letras habilitadas/deshabilitadas
- **Buscador incremental**: busca campeones en tiempo real
- **Mini-rostros (Contact sheet)**: avatares laterales para saltar rápido
- **Breadcrumbs dinámicos**: ubicación actual + contador de resultados
- **Acordeones por campeón**: secciones expandibles/colapsables

### Visualización
- **Grid responsivo**: skins en tarjetas adaptables
- **Carga incremental**: "Cargar 12 más" por campeón
- **Lazy loading**: imágenes cargan solo cuando entran al viewport
- **Hover effects**: zoom y efectos al pasar el mouse

### Modo Filmstrip
- **Visor grande**: modal fullscreen con imagen centrada
- **Hotkeys**: J/K (anterior/siguiente), H (ocultar sidebar), F (fullscreen)
- **Estado compartible**: URL actualiza con campeón y skin actual

### Diseño
- **Hextech theme**: diseño oficial de Riot Games
- **Dark mode**: tema oscuro por defecto
- **Responsivo**: funciona en desktop y mobile

---

## Archivos Generados

| Archivo | Descripción |
|---------|-------------|
| `data/splash-manifest.json` | Índice de todos los splash arts (893KB) |
| `outputs/splash-viewer.html` | Visor HTML autocontenido (612KB) |

## Fuente de Datos

Las imágenes se obtienen de la CDN pública de Data Dragon:
- `https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{Champion}_{SkinNum}.jpg`
- No requiere API key
- La versión de DDragon se detecta automáticamente

## Estructura de Assets

```
assets/splash_arts/
├── Aatrox/
│   ├── Aatrox_0.jpg    (default skin)
│   ├── Aatrox_1.jpg    (skin 1)
│   └── ...
├── Ahri/
│   ├── Ahri_0.jpg
│   └── ...
└── ... (171 campeones)
```
