# 🚀 Quick Start - Splash Arts Gallery

## ⚡ 3 pasos para usar tu visor

### 1️⃣ Descargar splash arts (solo la primera vez)

```bash
python download_splash_arts.py
```

**Resultado:** 2019 imágenes descargadas en `assets/splash_arts/`

---

### 2️⃣ Generar el visor

**Opción fácil (Windows):**
```bash
regenerar_splash_viewer.bat
```

**Opción manual:**
```bash
python src/riot_lol_cli/cli.py build-splash-manifest
python src/riot_lol_cli/cli.py generate-splash-viewer
```

**Resultado:** 
- `data/splash-manifest.json` → Índice con rutas
- `outputs/splash-viewer.html` → Tu visor listo

---

### 3️⃣ Abrir y disfrutar

**Windows:**
```bash
start outputs\splash-viewer.html
```

**O simplemente:** Doble clic en `outputs/splash-viewer.html`

---

## 🎮 Cómo usar el visor

### Buscar un campeón
1. Escribe en el buscador: "Ahri"
2. Clic en el campeón del sidebar
3. Se abre su sección con todas sus skins

### Navegar por letra
1. Clic en cualquier letra del A-Z
2. Se filtran solo los campeones de esa letra
3. Clic de nuevo en la misma letra para quitar filtro

### Ver en grande (Filmstrip)
1. Clic en cualquier skin card
2. Se abre el visor fullscreen
3. Usa flechas ←/→ o J/K para navegar
4. Presiona ESC para cerrar

### Pantalla completa
1. Abre filmstrip (clic en una skin)
2. Presiona **F**
3. Navega sin distracciones

### Ver atajos
Presiona **?** en cualquier momento

---

## 📊 Estadísticas actuales

- ✅ **171 campeones** indexados
- ✅ **2019 splash arts** disponibles con paletas de colores
- ✅ **v1.6.4** generada automáticamente
- ✅ **Filtros avanzados**: Color, badges, familias, favoritos
- ✅ **Comparador**: Vista side-by-side de 2-4 skins
- ✅ **Presenter Mode**: Autoplay con velocidad ajustable
- ✅ Todo funciona offline (sin internet)

---

## 🔄 Regenerar después de agregar más skins

Si descargas nuevos campeones o skins:

```bash
regenerar_splash_viewer.bat
```

Esto:
1. Re-escanea `assets/splash_arts/`
2. Extrae paletas de colores con PIL
3. Detecta badges (Prestige, Legacy, etc.)
4. Actualiza el manifest
5. Incrementa versión (1.6.4 → 1.6.5)
6. Regenera el HTML
7. Lo abre en tu navegador

---

## 💡 Tips

### Compartir una skin específica
1. Abre la skin que querés compartir
2. Copia la URL del navegador
3. Compartí el link (incluye todo el estado)

### Filtrar por familia o badge
Usa los selectores en el header:
- **Familias**: PROJECT, Star Guardian, K/DA, Spirit Blossom
- **Badges**: Prestige, Legacy, Mythic, Championship, Hextech, Victorious
- **Colores**: Clic en los chips de colores para filtrar por paleta

### Comparar skins
1. Marca los checkboxes en las esquinas de las tarjetas (máx 4)
2. Clic en el botón "Comparar (N)" que aparece
3. Ve las skins lado a lado en pantalla completa

### Favoritos
1. Clic en la estrella (☆) de cualquier skin
2. Se guarda en localStorage
3. Activa "Favoritos: on" para ver solo tus favoritas

### Presenter Mode
1. Abre filmstrip (clic en una skin)
2. Clic en "▶ Reproducir"
3. Ajusta velocidad (2s, 3s, 5s, 8s)
4. Disfruta el slideshow automático

### Performance con muchas skins
- El visor carga solo 12 skins por campeón inicialmente
- Clic en "Cargar 12 más" para ver el resto
- Las imágenes se cargan solo cuando las ves (lazy loading)

---

## ❓ Problemas comunes

### No se ven las imágenes

**Problema:** Rutas incorrectas o imágenes no descargadas

**Solución:**
```bash
# Verificar carpeta
dir assets\splash_arts

# Si está vacía, descargar
python download_splash_arts.py

# Regenerar manifest
python src/riot_lol_cli/cli.py build-splash-manifest
```

### Error al cargar manifest

**Problema:** `data/splash-manifest.json` no existe

**Solución:**
```bash
python src/riot_lol_cli/cli.py build-splash-manifest
```

### El navegador bloquea CORS

**Problema:** Algunos navegadores bloquean `file://` fetch

**Solución A - Servir con HTTP:**
```bash
python -m http.server 8000
# Abrir: http://localhost:8000/outputs/splash-viewer.html
```

**Solución B - Chrome con flag:**
```bash
chrome.exe --allow-file-access-from-files outputs\splash-viewer.html
```

---

## 📚 Más info

- **Documentación completa:** `SPLASH_VIEWER_README.md`
- **Roadmap de features:** Ver sección "Futuras mejoras"
- **Código fuente:** `src/riot_lol_cli/cli.py` + `assets/splash-viewer-app.js`

---

**¡Disfrutá los 2019 splash arts!** 🎨✨
