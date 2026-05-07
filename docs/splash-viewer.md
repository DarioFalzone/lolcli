# Splash Arts Gallery — riot_lol_cli

> Consolidado desde: SPLASH_ARTS_README.md, SPLASH_VIEWER_README.md, QUICK_START.md

## Versión: 1.6.4

Visor interactivo de splash arts de League of Legends con navegación avanzada, búsqueda, filtros y vista filmstrip.

## Inicio Rápido

### 1. Actualizar assets
```bash
python scripts/update_ddragon_assets.py
```
Actualiza iconos de items, CSV de items y splash arts desde Data Dragon CDN. No requiere API key.
Cuando sincroniza splash arts tambien regenera `data/ddragon-splash-catalog.json`,
`data/splash-manifest.json` y `outputs/splash-viewer.html`, por lo que las skins
nuevas quedan agregadas al front automaticamente.

### 2. Regenerar el visor manualmente
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
- **Buscador incremental**: busca campeones y nombres de skins en español/inglés, tolerando acentos
- **Mini-rostros (Contact sheet)**: avatares laterales para saltar rápido
- **Breadcrumbs dinámicos**: ubicación actual + contador de resultados
- **Acordeones por campeón**: secciones expandibles/colapsables
- **Familias dinámicas**: el filtro de familias se arma desde familias presentes en el manifest

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
| `data/ddragon-splash-catalog.json` | Catalogo Data Dragon localizado con parche, fecha de importacion y nombres de skins |
| `data/splash-manifest.json` | Indice generado de todos los splash arts |
| `outputs/splash-viewer.html` | Visor HTML autocontenido generado |

## Fuente de Datos

Las imágenes se obtienen de la CDN pública de Data Dragon:
- `https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{Champion}_{SkinNum}.jpg`
- No requiere API key
- La versión de DDragon se detecta automáticamente
- El front muestra el parche Data Dragon y la fecha/hora de importacion tomada del manifest

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
