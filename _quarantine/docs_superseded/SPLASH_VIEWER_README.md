# 🎨 League of Legends - Splash Arts Gallery

Visor interactivo de splash arts de League of Legends con navegación avanzada, búsqueda, filtros y vista filmstrip.

## 📦 Versión actual: 1.6.4

---

## 🚀 Inicio rápido

### 1. Descargar splash arts (si aún no los tenés)

```bash
python download_splash_arts.py
```

Esto descarga todos los splash arts en `assets/splash_arts/` organizados por campeón.

### 2. Generar el visor

**Opción A - Usando el .bat:**
```bash
regenerar_splash_viewer.bat
```

**Opción B - Comandos manuales:**
```bash
# Construir manifest
python src/riot_lol_cli/cli.py build-splash-manifest

# Generar HTML
python src/riot_lol_cli/cli.py generate-splash-viewer
```

### 3. Abrir el visor

El HTML generado está en: `outputs/splash-viewer.html`

---

## ✨ Características implementadas

### 🔍 Navegación y Búsqueda

- **Navegación A–Z lateral**: Alfabeto interactivo con letras habilitadas/deshabilitadas según campeones disponibles
- **Buscador incremental**: Busca campeones en tiempo real
- **Mini-rostros (Contact sheet)**: Lista lateral con avatares por campeón para saltar rápido
- **Breadcrumbs dinámicos**: Muestra tu ubicación actual y contador de resultados
- **Acordeones por campeón**: Secciones expandibles/colapsables para ahorrar scroll

### 🖼️ Visualización

- **Grid responsivo**: Muestra las skins en tarjetas adaptables
- **Carga incremental**: "Cargar 12 más" por campeón para evitar sobrecarga
- **Lazy loading**: Las imágenes cargan solo cuando entran al viewport
- **Hover effects**: Zoom y efectos al pasar el mouse

### 🎬 Modo Filmstrip

- **Visor grande**: Modal fullscreen con imagen centrada y controles
- **Tira de thumbnails**: Navegación horizontal con vista previa
- **Prefetch inteligente**: Pre-carga la imagen anterior y siguiente para transiciones instantáneas
- **Navegación con teclado**: J/K o ←/→ para cambiar de imagen
- **Metadata**: Muestra nombre del campeón y skin

### ⌨️ Atajos de teclado (Hotkeys)

| Tecla | Acción |
|-------|--------|
| **H** | Ocultar/Mostrar UI |
| **F** | Pantalla completa (toggle) |
| **J** o **←** | Imagen anterior (en filmstrip) |
| **K** o **→** | Imagen siguiente (en filmstrip) |
| **ESC** | Cerrar filmstrip o ayuda |
| **?** | Mostrar/Ocultar panel de atajos |

### 🔗 Estado compartible

- **URL con hash**: La URL se actualiza con tus filtros, campeón y skin actual
- **Deep links**: Compartí la URL exacta de lo que estás viendo
- **Back/Forward**: Los botones del navegador funcionan para navegar tu historial
- **Restauración automática**: Al recargar, vuelve al estado anterior

### 🎨 Filtros Avanzados (Phase 2 & 3)

- **Filtro por familia**: PROJECT, Star Guardian, K/DA, Spirit Blossom, etc.
- **Filtro por badges**: Prestige, Legacy, Mythic, Championship, Hextech, Victorious
- **Filtro por color**: 8 chips de colores más comunes extraídos de las paletas
- **Favoritos**: Marca skins favoritas (★) con persistencia en localStorage
- **Shuffle con seed**: Orden aleatorio compartible vía URL
- **Comparador**: Selecciona 2-4 skins para vista side-by-side
- **Sort cronológico**: Ordena skins por año de lanzamiento

### 🎬 Presenter Mode

- **Autoplay**: Reproducción automática de skins en filmstrip
- **Velocidad ajustable**: 2s, 3s, 5s u 8s por imagen
- **Controles**: Play/Pause, velocidad, fullscreen

### 🔊 Audio Ambiente (Opcional)

- **Toggle de audio**: Activa/desactiva música ambiente
- **Volumen ajustable**: Control de volumen integrado
- **Temático**: Audio inspirado en el universo de League of Legends

### 📊 Estadísticas

- **Badge en header**: Muestra total de campeones y skins cargados
- **Contador por letra**: Al filtrar por letra, muestra cuántos campeones hay
- **Contador de búsqueda**: Muestra resultados en breadcrumbs
- **Badges visuales**: Prestige, Legacy, Mythic, etc. en cada tarjeta
- **Año de lanzamiento**: Metadata temporal en cada skin

---

## 🎨 Diseño Hextech

Siguiendo el **Hextech Visual Language** oficial de Riot Games:

- **Paleta Hextech**: Dorados (#c89b3c), azules (#0bc6e3) y oscuros Piltover
- **Animaciones sutiles**: Glow pulse, shimmer, fade-in
- **Grid animado**: Fondo con patrón geométrico en movimiento
- **Tipografía Spiegel**: Font oficial de League of Legends
- **Shadows y efectos**: Depth shadows, hextech glow, gold shine
- **Responsive**: Sidebar oculto en mobile, navegación táctil

---

## 🗂️ Estructura de archivos

```
LOLCLI/
├── assets/
│   ├── splash_arts/           # Imágenes organizadas por campeón
│   │   ├── Ahri/
│   │   │   ├── Ahri_Classic.jpg
│   │   │   ├── Ahri_KDA.jpg
│   │   │   └── ...
│   │   └── ...
│   └── splash-viewer-app.js   # Lógica del visor
├── data/
│   └── splash-manifest.json   # Índice de imágenes con rutas
├── outputs/
│   └── splash-viewer.html     # HTML generado (abrir este)
├── templates/
│   └── splash-viewer.html     # Plantilla base
├── src/riot_lol_cli/
│   └── cli.py                 # Comandos CLI
└── regenerar_splash_viewer.bat # Script regeneración rápida
```

---

## 🛠️ Comandos CLI

### `build-splash-manifest`

Escanea `assets/splash_arts/` y genera el manifest JSON con extracción de colores y detección de badges.

```bash
python src/riot_lol_cli/cli.py build-splash-manifest
```

**Salida:**
- `data/splash-manifest.json`: Índice con campeones, imágenes, rutas relativas, paletas de colores y badges

**Características:**
- **Extracción de paleta**: Usa PIL/Pillow para extraer los 5 colores dominantes de cada splash art
- **Detección de badges**: Identifica Prestige, Legacy, Mythic, Championship, Hextech, Victorious por nombre
- **Año de lanzamiento**: Extrae el año del nombre del archivo cuando está disponible

**Ejemplo de manifest:**
```json
{
  "champions": [
    { "id": "Ahri", "name": "Ahri", "count": 22 }
  ],
  "images": [
    {
      "championId": "Ahri",
      "file": "Ahri_Classic.jpg",
      "relPath": "../assets/splash_arts/Ahri/Ahri_Classic.jpg",
      "skinName": "Classic",
      "colors": {
        "primary": "#110207",
        "palette": ["#110207", "#120308", "#100106", "#0f0005", "#0e0004"]
      },
      "badges": [],
      "releaseYear": null
    },
    {
      "championId": "Ahri",
      "file": "Ahri_Prestige_KDA.jpg",
      "relPath": "../assets/splash_arts/Ahri/Ahri_Prestige_KDA.jpg",
      "skinName": "Prestige KDA",
      "colors": {
        "primary": "#fefefe",
        "palette": ["#fefefe", "#feffff", "#fefeff", "#ffffff", "#fdfefe"]
      },
      "badges": ["Prestige"],
      "releaseYear": null
    }
  ],
  "totalChampions": 171,
  "totalImages": 2019,
  "version": "1.6.4",
  "generatedAt": "2025-10-26T04:22:00Z"
}
```

### `generate-splash-viewer`

Genera el HTML del visor usando la plantilla.

```bash
python src/riot_lol_cli/cli.py generate-splash-viewer
```

**Opciones:**
- `-o, --output`: Ruta de salida personalizada (default: `outputs/splash-viewer.html`)

**Ejemplo:**
```bash
python src/riot_lol_cli/cli.py generate-splash-viewer -o mi-visor.html
```

---

## 🔧 Cómo funciona

### 1. Escaneo y manifest

El comando `build-splash-manifest` recorre la carpeta `assets/splash_arts/`:
- Detecta carpetas de campeones
- Lista todos los `.jpg` y `.png`
- Extrae nombre de skin del filename
- **Extrae paleta de colores**: Usa PIL para obtener los 5 colores dominantes de cada imagen
- **Detecta badges**: Identifica Prestige, Legacy, Mythic, Championship, Hextech, Victorious
- **Extrae año**: Busca patrones de año (2018-2025) en el nombre del archivo
- Genera rutas relativas desde `outputs/splash-viewer.html`

### 2. Generación HTML

El comando `generate-splash-viewer`:
- Carga la plantilla `templates/splash-viewer.html`
- Reemplaza variables: `{{version}}`, `{{manifest_url}}`, `{{total_champions}}`, etc.
- Incrementa la versión automáticamente (siguiendo tu memoria de versionado)
- Guarda el HTML final en `outputs/`

### 3. Carga dinámica en el navegador

Al abrir el HTML:
- Carga `splash-viewer-app.js` con el manifest URL en `data-manifest-url`
- Fetch del manifest JSON
- Renderiza A–Z, lista de campeones y secciones acordeón
- Lazy load de imágenes con `loading="lazy"`
- Event listeners para teclado, búsqueda y navegación

### 4. Filmstrip y estado

- Al hacer clic en una skin → abre filmstrip modal
- Prefetch de vecinos para navegación fluida
- Actualiza hash en URL: `#champ=Ahri&idx=5`
- Al navegar back/forward → restaura estado desde hash

---

## 📈 Rendimiento

### Optimizaciones implementadas

1. **Lazy loading**: Imágenes cargan solo al ser visibles
2. **Carga incremental**: 12 skins por vez con "Cargar más"
3. **Prefetch de vecinos**: Pre-carga siguiente/anterior en filmstrip
4. **Acordeones colapsables**: Solo renderiza lo expandido
5. **Rutas relativas**: Sin dependencia de servidor, todo local
6. **CSS comprimido**: Estilos minificados inline
7. **JS externo cacheable**: Un solo archivo JavaScript

### Estadísticas actuales

- **171 campeones**
- **2019 splash arts**
- **Paletas de colores**: 2019 paletas extraídas (5 colores por splash)
- **Badges detectados**: Prestige, Legacy, Mythic, Championship, Hextech, Victorious
- **Tamaño HTML**: ~20KB (comprimido, con manifest inline)
- **Tamaño JS**: ~12KB
- **Tamaño Manifest**: ~1.5MB (con paletas de colores)
- **Carga inicial**: <150ms (sin imágenes)
- **Carga por campeón**: ~500ms (12 skins)

---

## 🎯 Casos de uso

### 1. Explorar skins por campeón
1. Busca el campeón en el sidebar
2. Clic para saltar a su sección
3. Navega su galería

### 2. Buscar skins específicas
1. Usa el buscador: escribe "K/DA", "Prestige", etc.
2. Filtra resultados por letra si querés
3. Abre en filmstrip para ver detalles

### 3. Presentación fullscreen
1. Abre cualquier skin en filmstrip
2. Presiona **F** para fullscreen
3. Navega con **J/K** o flechas
4. Presiona **H** para ocultar UI

### 4. Compartir selección
1. Navega al campeón/skin que querés mostrar
2. Copia la URL del navegador (tiene el hash)
3. Compartí el link → se abre en el mismo estado

---

## 🐛 Solución de problemas

### El visor no carga imágenes

**Causa**: Rutas relativas incorrectas o imágenes no descargadas.

**Solución**:
1. Verificá que existe `assets/splash_arts/` con las carpetas de campeones
2. Ejecuta `python download_splash_arts.py` para descargar
3. Re-genera el manifest: `python src/riot_lol_cli/cli.py build-splash-manifest`

### El manifest está vacío

**Causa**: `assets/splash_arts/` no existe o está vacío.

**Solución**:
```bash
# Descargar todas las imágenes
python download_splash_arts.py

# Verificar que se descargaron
dir assets\splash_arts

# Re-construir manifest
python src/riot_lol_cli/cli.py build-splash-manifest
```

### Error al abrir el HTML (CORS)

**Causa**: Algunos navegadores bloquean `file://` fetch por seguridad.

**Solución**:
- **Opción A**: Usa Chrome/Edge con flag: `--allow-file-access-from-files`
- **Opción B**: Sirve con HTTP local:
  ```bash
  python -m http.server 8000
  # Abre: http://localhost:8000/outputs/splash-viewer.html
  ```

### Los atajos de teclado no funcionan

**Causa**: Focus en input de búsqueda o modal no abierto.

**Solución**:
- Atajos globales (**?**, **ESC**) funcionan siempre
- Atajos de filmstrip (**J/K/H/F**) solo funcionan con modal abierto
- Si estás en el input de búsqueda, presiona **Tab** o clic afuera

---

## ✅ Features completadas

### Phase 1 - MVP
- ✅ Navegación A-Z lateral
- ✅ Buscador incremental
- ✅ Lista sidebar con mini-rostros
- ✅ Breadcrumbs dinámicos
- ✅ Acordeones por campeón
- ✅ Grid responsivo con lazy loading
- ✅ Carga incremental (12 por vez)
- ✅ Filmstrip modal fullscreen
- ✅ Prefetch inteligente
- ✅ Hotkeys completos
- ✅ Estado compartible (URL hash)
- ✅ Diseño Hextech oficial

### Phase 2 - Plus features
- ✅ Filtro por familias de skins (PROJECT, Star Guardian, K/DA, Spirit Blossom)
- ✅ Shuffle con seed compartible
- ✅ Favoritos con persistencia (localStorage)
- ✅ Presenter Mode con autoplay y velocidad ajustable

### Phase 3 - Nice-to-have
- ✅ Filtro por paleta de colores (8 chips)
- ✅ Badges Legacy/Prestige/Mythic/Championship/Hextech/Victorious
- ✅ Comparador side-by-side (2-4 skins)
- ✅ Timeline cronológico por año de lanzamiento
- ✅ Audio ambiente opcional (toggle)

## 🔮 Futuras mejoras (roadmap)

### Fase 4 - Advanced features
- [ ] Radar de etiquetas (oscuras, ciberpunk, festivas)
- [ ] Before/After slider para reworks
- [ ] Scatter mood × energía
- [ ] Kanban para curación
- [ ] Panel de metadata lateral con relaciones
- [ ] Export de favoritos a JSON
- [ ] Tableros personalizados

---

## 📝 Notas técnicas

### Versionado automático

Cada regeneración incrementa la versión automáticamente:
- Formato: `MAJOR.MINOR.PATCH`
- Archivo: `config/version.json`
- Función: `increment_version()` en `cli.py`

### Atomización

Siguiendo tu estilo de trabajo atomizado:
- **1 plantilla**: `templates/splash-viewer.html`
- **1 JS**: `assets/splash-viewer-app.js`
- **1 manifest**: `data/splash-manifest.json`
- **Estilos inline**: CSS comprimido en el HTML
- **Sin dependencias externas**: Todo autocontent excepto Spiegel font

### Compatibilidad

- **Navegadores**: Chrome, Edge, Firefox, Safari (últimas 2 versiones)
- **Mobile**: Responsive con sidebar oculto y gestos táctiles
- **File protocol**: Funciona sin servidor (con excepciones CORS)
- **Offline**: Completamente local, sin conexión necesaria

---

## 🎉 Créditos

- **Data Dragon**: Riot Games CDN para splash arts
- **Hextech Design**: Sistema de diseño oficial de League of Legends
- **Spiegel Font**: Tipografía oficial de LoL
- **Inspiración**: Cliente de LoL y Universe

---

## 📄 Licencia

Este proyecto es una herramienta personal no oficial. League of Legends y todos los splash arts son propiedad de Riot Games.

---

**¡Disfrutá explorando los 2019 splash arts de LoL!** 🎨✨
