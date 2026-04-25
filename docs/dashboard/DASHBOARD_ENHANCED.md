# 📊 Dashboard Mejorado - LOLCLI Meta Analyzer

## Descripción General

El dashboard mejorado proporciona una interfaz visual completa y avanzada para analizar el meta de ADCs en League of Legends. Incluye múltiples tabs, filtros interactivos y visualización de datos con source attribution.

## 🚀 Características Principales

### 1. **Dashboard Tab** - Tier List
Visualiza el ranking actual de ADCs organizados por tiers:
- **Tier S (OP)**: Campeones completamente dominantes
- **Tier A (Muy Bueno)**: Campeones muy viables
- **Tier B (Viable)**: Campeones balanceados
- **Tier C (Aceptable)**: Campeones con limitaciones
- **Tier D (Débil)**: Campeones no recomendados

**Funcionalidades:**
- ✅ Click en campeón → Abre modal con detalles
- ✅ Muestra Winrate (WR%) y Pickrate (PR%)
- ✅ Información en tiempo real desde Data Dragon

### 2. **Matchups Tab** - Historial de Enfrentamientos
Análisis detallado de cómo cada ADC se desempeña contra otros.

**Columnas:**
| Campo | Descripción |
|-------|-------------|
| Hora | Timestamp del registro |
| Campeón Rival | Contra quién se jugó |
| Partidas | Cantidad de matches |
| Victorias | Wins en el matchup |
| Derrotas | Losses en el matchup |
| WR % | Winrate del matchup |
| Tendencia | UP/DOWN/STABLE (cambio meta) |
| Fuente | Data Dragon (attribution) |

**Filtros disponibles:**
- 📌 Seleccionar campeón (dropdown)
- ⏱️ Últimas N horas (1-240)
- 📊 Límite de registros (10-500)

**Interactividad:**
- 🔢 Click en encabezados para ordenar
- 📝 Click en filas para ver detalles
- 🔄 Actualización automática

### 3. **Items Tab** - Análisis de Construcción
Muestra qué items están siendo más utilizados por cada ADC.

**Columnas:**
| Campo | Descripción |
|-------|-------------|
| Item ID | ID del item en Data Dragon |
| Frecuencia | Cuántas veces se construye |
| Ruta de Build | Path/recomendación |
| Fuente | Origen de datos |

**Utilidad:**
- 🎯 Identifica builds meta
- 📈 Detecta cambios en construcciones
- 📊 Trending items

**Filtros:**
- 🏆 Top N items por campeón
- 👤 Selector de campeón

### 4. **Raw Data Tab** - Datos Sin Filtrar
Acceso directo a datos sin procesar con estructura completa.

**Estructura de datos:**
```json
{
  "champion": "Corki",
  "hour": "2026-01-11T22:00:00",
  "matches": 148,
  "winrate": 58.6,
  "pickrate": 42.3,
  "source": "data_dragon"
}
```

**Capacidades:**
- 🔍 Buscar por campeón (optional)
- 📏 Limitar registros (10-1000)
- 📋 Exportar para análisis externo

## 🎯 Data Source Attribution

**Cada registro incluye el campo `source`:**
```html
<span class="source-badge">data_dragon</span>
```

Esto permite:
- ✅ Rastrear el origen de cada dato
- ✅ Validar confiabilidad
- ✅ Identificar anomalías por fuente
- ✅ Auditoría de datos

## 📱 Modal de Detalles del Campeón

Al hacer click en un campeón en cualquier parte del dashboard:

### Se abre un modal con:

1. **Estadísticas Actuales**
   - Winrate (%)
   - Pickrate (%)
   - Total de partidas analizadas
   - Tier asignado

2. **Anomalías Detectadas** (si existen)
   - Tipo de anomalía
   - Descripción del cambio
   - Confianza estadística (%)
   - Severidad

3. **Información Metadata**
   - Fuente de datos (Data Dragon)
   - Último update timestamp
   - Contador de registros

**Ejemplo modal:**
```
┌─────────────────────────────────┐
│ Corki    [data_dragon]          │
├─────────────────────────────────┤
│ 📊 Estadísticas Actuales         │
│ • Winrate: 58.6%                │
│ • Pickrate: 42.3%               │
│ • Partidas: 1,247               │
│ • Tier: S                        │
│                                  │
│ ⚠️ Anomalías Detectadas         │
│ • HIGH_WINRATE                  │
│   Confianza: 95%                │
│   "Corki tiene un 10% más WR    │
│    que su promedio histórico"   │
│                                  │
│ ℹ️ Información               │
│ • Fuente: data_dragon           │
│ • Actualizado: 2026-01-11       │
│   22:15:30                      │
└─────────────────────────────────┘
```

## 🔧 API Endpoints Utilizados

El dashboard mejorado utiliza estos endpoints:

### 1. **GET /api/v1/champions/list**
```bash
curl http://localhost:8000/api/v1/champions/list
```
Response: Lista de 31 ADCs trackeados

### 2. **GET /api/v1/tier-list/current**
```bash
curl http://localhost:8000/api/v1/tier-list/current
```
Response: Tier list organizado por ranks

### 3. **GET /api/v1/champions/{champion}/matchups**
```bash
curl http://localhost:8000/api/v1/champions/Corki/matchups?limit=50&hours=24
```
Response: Historial de matchups con trends

### 4. **GET /api/v1/champions/{champion}/items**
```bash
curl http://localhost:8000/api/v1/champions/Corki/items?limit=20
```
Response: Top items por campeón

### 5. **GET /api/v1/champions/{champion}/details**
```bash
curl http://localhost:8000/api/v1/champions/Corki/details
```
Response: Perfil completo con anomalías

### 6. **GET /api/v1/champions/all/raw-data**
```bash
curl http://localhost:8000/api/v1/champions/all/raw-data?limit=100&champion=Corki
```
Response: Datos sin filtrar con source

## 🎮 Guía de Uso Rápido

### 1. **Generar el Dashboard**
```bash
python generate_dashboard.py
```

### 2. **Iniciar la API**
```bash
python run_api.py
```

### 3. **Abrir en navegador**
- Local: `file:///C:/path/to/outputs/meta-analyzer-dashboard-enhanced.html`
- API: `http://localhost:8000/dashboard-enhanced`

### 4. **Flujo Típico**

#### Escenario 1: Ver ADCs mejores ahora
1. Ve al tab "Dashboard"
2. Observa Tier List
3. Click en un campeón → Ve detalles
4. Revisa estadísticas y anomalías

#### Escenario 2: Analizar matchups
1. Ve al tab "Matchups"
2. Selecciona campeón (ej: Corki)
3. Ajusta filtros (últimas 24h, top 50)
4. Ordena por WR (click encabezado)
5. Identifica matchups favorables/desfavorables

#### Escenario 3: Estudiar builds
1. Ve al tab "Items"
2. Elige campeón (ej: Miss Fortune)
3. Ve top 10 items
4. Analiza frecuencia
5. Identifica ruta de build optimal

#### Escenario 4: Exportar para análisis
1. Ve al tab "Raw Data"
2. Filtra por campeón si es necesario
3. Aumenta límite de registros (hasta 1000)
4. Copia datos o descarga

## 🎨 Diseño & UX

### Colores
- 🔵 **Azul (#0ac800)** - Winrate/Success
- 🟡 **Naranja (#c89b3c)** - Accent/Important
- 🔴 **Rojo (#ff3d3d)** - Danger/Losses
- 🟦 **Cyan (#00a8ff)** - Info/Pickrate

### Responsividad
- ✅ Desktop (1400px+)
- ✅ Tablet (768px-1399px)
- ✅ Mobile (< 768px)

### Interactividad
- ✅ Hover effects en filas
- ✅ Modal animado con fade-in
- ✅ Sorting en encabezados
- ✅ Cierre de modal con ESC key
- ✅ Click fuera modal → cierra

## 📊 Estadísticas Disponibles

### Por Campeón
- **Winrate (WR%)**: % de partidas ganadas
- **Pickrate (PR%)**: % de veces seleccionado
- **Matchcount**: Total de partidas analizadas
- **Tier**: Ranking (S/A/B/C/D)

### Por Matchup
- **Victorias**: Wins contra enemigo específico
- **Derrotas**: Losses contra enemigo
- **Tendencia**: UP/DOWN/STABLE
- **Timestamp**: Cuándo fue el registro

### Por Item
- **Frecuencia**: Cuántas veces se compró
- **Build Path**: Recomendación de construcción

## 🔐 Data Privacy & Attribution

- ✅ Todos los datos de **Data Dragon** (oficial Riot Games)
- ✅ **Source attribution** en cada registro
- ✅ Timestamps para auditoría
- ✅ Trazabilidad completa de datos

## ⚙️ Requisitos

### Backend
- Python 3.8+
- FastAPI
- SQLite
- Axios (JavaScript)
- Chart.js (opcional)

### Frontend
- Navegador moderno (Chrome 90+, Firefox 88+, Safari 14+)
- JavaScript habilitado
- Sin requerimientos de librerías externas (CDN)

## 🐛 Troubleshooting

### "Dashboard no encontrado"
```bash
python setup_meta_analyzer.py
```

### "Desconectado" en header
- Verifica que `python run_api.py` esté corriendo
- Revisa puerto 8000: `netstat -an | findstr 8000`

### Datos no se cargan
1. Asegúrate que la BD existe: `data/meta_analyzer.db`
2. Verifica datos de demo: `python setup_meta_analyzer.py`
3. Revisa console (F12) para errores

### Modal no cierra
- Prueba presionar ESC
- Refresh la página
- Limpia cache del navegador

## 📈 Próximas Mejoras

- [ ] Integración con Riot API en tiempo real
- [ ] Gráficos de tendencias (Chart.js)
- [ ] Exportación a CSV/Excel
- [ ] Notificaciones de anomalías
- [ ] Análisis predictivo
- [ ] Comparación de campeones side-by-side

## 📚 Referencias

- [Data Dragon API](https://ddragon.leagueoflegends.com/)
- [League of Legends Meta](https://www.lolmeta.net/)
- [Documentación LOLCLI](/docs/INDEX.md)

---

**Última actualización:** 2026-01-11  
**Versión:** 1.0.0 Enhanced  
**Autor:** LOLCLI Team
