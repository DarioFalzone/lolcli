# 🎨 Descargador de Splash Arts - League of Legends

Script para descargar automáticamente todos los splash arts de League of Legends usando Data Dragon (CDN oficial de Riot Games).

## ✨ Características

- ✅ **No requiere API Key** - Usa Data Dragon público de Riot
- 📁 **Organizado por campeón** - Cada campeón tiene su propia carpeta
- 🖼️ **Todas las skins** - Descarga splash art de todas las skins disponibles
- 🔄 **Actualización automática** - Usa la versión más reciente de Data Dragon
- 🎯 **Descargas selectivas** - Descarga todos o solo un campeón específico
- ⚡ **Rápido y eficiente** - Manejo inteligente de descargas

## 📋 Requisitos

- Python 3.7 o superior
- Librería `requests` (se instala automáticamente)

## 🚀 Uso

### Opción 1: Usar el archivo .bat (Windows)

```batch
.\download_splash_arts.bat
```

El script te mostrará un menú con opciones:
1. Descargar TODOS los splash arts
2. Descargar splash arts de UN campeón específico
3. Salir

### Opción 2: Ejecutar Python directamente

#### Descargar todos los splash arts:
```bash
python download_splash_arts.py
```

#### Descargar un campeón específico:
```bash
python download_splash_arts.py Naafiri
python download_splash_arts.py "Twisted Fate"
python download_splash_arts.py Ahri
```

## 📂 Estructura de Carpetas

Los splash arts se guardan en:
```
assets/
└── splash_arts/
    ├── Aatrox/
    │   ├── Aatrox_Classic.jpg
    │   ├── Aatrox_Justicar.jpg
    │   ├── Aatrox_Mecha.jpg
    │   └── ...
    ├── Ahri/
    │   ├── Ahri_Classic.jpg
    │   ├── Ahri_Dynasty.jpg
    │   ├── Ahri_K_DA.jpg
    │   └── ...
    ├── Naafiri/
    │   ├── Naafiri_Classic.jpg
    │   └── ...
    └── ... (todos los campeones)
```

## 📊 Información Descargada

Para cada campeón se descargan:
- ✅ Skin clásica (default)
- ✅ Todas las skins disponibles
- ✅ Imágenes en alta calidad (JPG)
- ✅ Nombres descriptivos de archivo

## 🎯 Ejemplos de Uso

### Descargar todos los splash arts
```bash
python download_splash_arts.py
```

Esto descargará:
- ~170 campeones
- ~1000+ splash arts
- Tamaño aproximado: 2-3 GB
- Tiempo estimado: 10-15 minutos

### Descargar un solo campeón
```bash
python download_splash_arts.py Naafiri
```

Esto descargará solo los splash arts de Naafiri:
- Skin clásica
- Todas sus skins alternativas

### Actualizar splash arts existentes
Si ejecutas el script nuevamente, automáticamente:
- ⏭️ Saltará archivos que ya existen
- ⬇️ Descargará solo los nuevos splash arts
- 🔄 No re-descarga archivos existentes

## 🛠️ Características Técnicas

### Control de Rate Limiting
- Pausas automáticas entre descargas (0.1s por skin)
- Pausa entre campeones (0.2s)
- Previene sobrecarga del servidor

### Manejo de Errores
- ✅ Continúa descargando si un archivo falla
- ✅ Reporta errores sin detener el proceso
- ✅ Resumen final con estadísticas

### Optimización
- ✅ Verifica si el archivo ya existe antes de descargar
- ✅ Descarga por chunks para archivos grandes
- ✅ Crea directorios automáticamente si no existen

## 📈 Estadísticas

Al finalizar, el script muestra:
```
📊 RESUMEN
════════════════════════════════════════════════════════════
✅ Splash arts descargados: 1247
❌ Fallos: 3
📁 Ubicación: E:\...\assets\splash_arts
```

## 🎨 Uso con el HTML de Naafiri

Los splash arts descargados se pueden usar en tus páginas HTML:

```html
<img src="../assets/splash_arts/Naafiri/Naafiri_Classic.jpg" alt="Naafiri">
```

## 🔧 Solución de Problemas

### Error: "Module 'requests' not found"
```bash
pip install requests
```

### Error: "Permission denied"
- Ejecuta como administrador
- Verifica permisos de escritura en la carpeta

### Descargas lentas
- Es normal, Data Dragon tiene límites de ancho de banda
- El script usa pausas para no sobrecargar el servidor

### Algunos splash arts fallan
- Algunas skins pueden no tener splash art disponible
- El script continúa con las demás

## 📝 Notas

- **Data Dragon es público**: No requiere autenticación
- **Actualización automática**: Usa la última versión disponible
- **Compatible con todas las regiones**: Las imágenes son universales
- **Alta calidad**: JPG en resolución completa (1215x717 típicamente)

## 🌐 Data Dragon

Data Dragon es el CDN oficial de Riot Games que contiene:
- Splash arts de todos los campeones
- Iconos de items
- Imágenes de habilidades
- Y más recursos del juego

URL base: `https://ddragon.leagueoflegends.com/`

## 📦 Versión

El script usa automáticamente la última versión de Data Dragon disponible.

Versión actual en código: `14.23.1`
Actualización: Automática al ejecutar

## 🎯 Próximas Mejoras

- [ ] Barra de progreso visual
- [ ] Descargar también iconos cuadrados
- [ ] Descargar loading screens
- [ ] Crear thumbnails automáticamente
- [ ] Soporte para descargas paralelas

## 📄 Licencia

Este script es para uso personal y educativo.
Todos los splash arts son propiedad de Riot Games, Inc.

---

💡 **Tip**: Después de descargar los splash arts, puedes usarlos para crear galerías, páginas de campeones, o cualquier proyecto relacionado con League of Legends.
