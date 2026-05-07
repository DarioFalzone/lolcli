# 📋 Instrucciones para Obtener Datos Completos de la API

## 🔑 Paso 1: Configurar API Key de Riot

1. Ve a [Riot Developer Portal](https://developer.riotgames.com/)
2. Inicia sesión con tu cuenta de Riot
3. Copia tu **Development API Key** (válida por 24 horas)

## ⚙️ Paso 2: Configurar Variable de Entorno

### En Windows (PowerShell):
```powershell
$env:RIOT_API_KEY = "RGAPI-tu-key-aqui"
```

### En Windows (CMD):
```cmd
set RIOT_API_KEY=RGAPI-tu-key-aqui
```

### Permanente (Windows):
```cmd
setx RIOT_API_KEY "RGAPI-tu-key-aqui"
```
*Nota: Después de usar `setx`, cierra y abre una nueva terminal*

## 🚀 Paso 3: Ejecutar Script de Obtención de Datos

```cmd
.\fetch_matches.bat
```

O directamente con Python:
```cmd
python fetch_matches_full.py
```

## 📊 Datos que se Obtienen

El script obtiene **TODOS** los datos necesarios de cada partida:

### ✅ Datos del Jugador
- Nombre de invocador
- Nivel
- Icono de perfil
- PUUID

### ✅ Datos de Cada Partida
- **Campeón**: Nombre, ID, nivel del campeón
- **KDA**: Kills, Deaths, Assists, KDA Ratio
- **Items**: Los 6 items + trinket
- **Estadísticas**:
  - 💥 Daño total a campeones
  - 💰 Oro ganado
  - 👁️ Visión score
- **Resultado**: Victoria/Derrota
- **Duración**: Tiempo de partida
- **Fecha**: Timestamp y "hace cuánto"

## 📁 Archivo Generado

Los datos se guardan en:
```
data/cache/matches.json
```

## 🔄 Paso 4: Regenerar HTML

Después de obtener los datos, regenera el HTML:

```cmd
.\regenerar_html.bat
```

## ⚡ Script Todo-en-Uno

Si quieres hacer todo en un solo paso, puedes crear un script `actualizar_todo.bat`:

```batch
@echo off
echo Obteniendo datos de la API...
python fetch_matches_full.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Regenerando HTML...
    .\regenerar_html.bat
) else (
    echo ERROR: No se pudieron obtener los datos
    pause
)
```

## 🎨 Mejoras Implementadas

### ✅ Paginación Funcional
- Botones Anterior/Siguiente funcionan correctamente
- Selector de items por página (10, 20, 50, 100)

### ✅ Buscador
- Filtra por nombre de campeón en tiempo real

### ✅ Filtros
- Todas las partidas
- Solo victorias
- Solo derrotas

### ✅ Diseño Mejorado
- **Más compacto** pero atractivo
- **Colores temáticos**: Verde para victorias, Rojo para derrotas
- **KDA ratio oculto** cuando es 0.0:1
- **Items visibles** con mejor diseño
- **Duración y tiempo** de cada partida visible
- **Stats reales**: Daño, Oro, Visión (cuando hay datos)

### ✅ Estilos Hextech
- Campeones con nombre dorado brillante
- Filas con gradiente según resultado
- Hover effects mejorados
- Bordes laterales de color según victoria/derrota

## 🐛 Solución de Problemas

### Error: "RIOT_API_KEY no está configurada"
- Asegúrate de haber configurado la variable de entorno
- Si usaste `setx`, cierra y abre una nueva terminal

### Error: "No autorizado (401/403)"
- Tu API key puede haber expirado (duran 24 horas)
- Genera una nueva key en el Developer Portal

### Error: "Rate limit excedido (429)"
- La API de Riot tiene límites de requests
- El script tiene manejo automático de rate limiting
- Espera unos segundos y vuelve a intentar

## 📝 Notas

- Las **Development API Keys** expiran cada 24 horas
- El script hace una pausa entre requests para evitar rate limiting
- Se recomienda obtener máximo 100 partidas por ejecución
- Los datos se guardan en formato JSON para fácil acceso

## 🎯 Resultado Final

Después de seguir estos pasos, tendrás:
- ✅ Datos completos de todas tus partidas
- ✅ HTML con estadísticas reales
- ✅ Interfaz funcional con búsqueda y filtros
- ✅ Diseño Hextech premium de Riot Games
