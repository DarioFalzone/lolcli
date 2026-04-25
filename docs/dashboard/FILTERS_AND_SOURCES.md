# 🔍 Filtros & Data Source Attribution

## Data Source Attribution System

Cada registro de datos en el dashboard incluye información sobre su origen.

### Badge de Fuente
```html
<span class="source-badge">data_dragon</span>
```

**Actualmente:**
- ✅ **data_dragon** - Datos de Riot Games Data Dragon API

**En el futuro:**
- 🔄 **riot_api** - Riot Official API
- 🔄 **opgg** - OP.GG API
- 🔄 **leagueofgraphs** - League of Graphs
- 🔄 **u.gg** - U.GG Analytics

---

## 🎯 Filtros Disponibles por Tab

### Tab: Matchups

#### 1. Selector de Campeón (Obligatorio)
```
Campeón: [Seleccionar...]
```
- Dropdown con los 31 ADCs
- Actualiza tabla dinámicamente
- Sin selección = "Selecciona un campeón"

#### 2. Filtro de Horas
```
Últimas (horas): [24] (1-240)
```
- Rango: 1 a 240 horas
- Default: 24 horas (último día)
- Afecta registros mostrados

**Ejemplos:**
- 1 = Último 1 hora
- 24 = Últimas 24 horas (default)
- 168 = Última semana
- 240 = Últimos 10 días

#### 3. Filtro de Límite
```
Límite: [50] (10-500)
```
- Rango: 10 a 500 registros
- Default: 50 registros
- Mejora performance con datasets grandes

**Ejemplos:**
- 10 = Top 10 matchups
- 50 = Análisis estándar
- 200 = Análisis profundo
- 500 = Análisis exhaustivo

**Combinación típica:**
```
Campeón: Corki
Últimas: 24 horas
Límite: 50 registros
→ Top 50 matchups de Corki en las últimas 24 horas
```

---

### Tab: Items

#### 1. Selector de Campeón (Obligatorio)
```
Campeón: [Seleccionar...]
```
- Dropdown con los 31 ADCs
- Obligatorio para ver datos

#### 2. Filtro de Top Items
```
Top Items: [10] (5-50)
```
- Rango: 5 a 50 items
- Default: 10 items principales
- Valores comunes: 5, 10, 15, 20

**Ejemplos:**
- 5 = Build essencial (muy reducida)
- 10 = Build meta (default)
- 20 = Builds alternativas
- 50 = Análisis exhaustivo

**Flujo típico:**
```
Campeón: Miss Fortune
Top Items: 10
→ Muestra los 10 items más frecuentes
→ Identifica build meta actual
```

---

### Tab: Raw Data

#### 1. Selector de Campeón (Opcional)
```
Campeón (opcional): [Todos]
```
- Dropdown con "Todos" + 31 ADCs
- Default: Todos (sin filtro)
- Permite buscar por campeón específico

#### 2. Filtro de Límite
```
Límite: [100] (10-1000)
```
- Rango: 10 a 1000 registros
- Default: 100 registros
- Para exportar/analizar grandes datasets

**Casos de uso:**
- 100 = Análisis rápido
- 500 = Análisis completo
- 1000 = Dataset completo

**Combinaciones:**
```
Campeón: Todos, Límite: 1000
→ Descarga 1000 últimos registros (todos los ADCs)

Campeón: Yasuo, Límite: 500
→ Descarga 500 últimos registros de Yasuo
```

---

## 🔗 Parámetros Query de API

Todos los filtros del dashboard se mapean a parámetros de query en la API.

### GET /api/v1/champions/{champion}/matchups
```bash
curl "http://localhost:8000/api/v1/champions/Corki/matchups?limit=50&hours=24"
```

**Parámetros:**
| Parámetro | Tipo | Default | Rango |
|-----------|------|---------|-------|
| `limit` | int | 50 | 10-500 |
| `hours` | int | 24 | 1-240 |

### GET /api/v1/champions/{champion}/items
```bash
curl "http://localhost:8000/api/v1/champions/MissFortune/items?limit=10"
```

**Parámetros:**
| Parámetro | Tipo | Default | Rango |
|-----------|------|---------|-------|
| `limit` | int | 10 | 5-50 |

### GET /api/v1/champions/all/raw-data
```bash
curl "http://localhost:8000/api/v1/champions/all/raw-data?limit=100&champion=Yasuo"
```

**Parámetros:**
| Parámetro | Tipo | Default | Rango | Nota |
|-----------|------|---------|-------|------|
| `limit` | int | 100 | 10-1000 | Max registros |
| `champion` | str | - | Nombre | Opcional |

---

## 📊 Estructura de Respuesta con Source

### Matchups Response
```json
{
  "success": true,
  "champion": "Corki",
  "data": [
    {
      "hour": "2026-01-11T22:00:00",
      "champion": "Kalista",
      "matches": 148,
      "wins": 86,
      "losses": 62,
      "winrate": 58.11,
      "trend": "UP",
      "source": "data_dragon"
    },
    {
      "hour": "2026-01-11T21:00:00",
      "champion": "Ashe",
      "matches": 134,
      "wins": 73,
      "losses": 61,
      "winrate": 54.48,
      "trend": "STABLE",
      "source": "data_dragon"
    }
  ],
  "source": "data_dragon",
  "timestamp": "2026-01-11T22:15:30"
}
```

### Items Response
```json
{
  "success": true,
  "champion": "MissFortune",
  "data": [
    {
      "item_id": 6672,
      "frequency": 45,
      "build_path": "Starter Item",
      "source": "data_dragon"
    },
    {
      "item_id": 3031,
      "frequency": 43,
      "build_path": "Core Build",
      "source": "data_dragon"
    }
  ],
  "source": "data_dragon",
  "timestamp": "2026-01-11T22:15:30"
}
```

### Raw Data Response
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "champion": "Corki",
      "hour": "2026-01-11T22:00:00",
      "matches": 248,
      "winrate": 58.60,
      "pickrate": 42.34,
      "source": "data_dragon"
    },
    {
      "id": 2,
      "champion": "MissFortune",
      "hour": "2026-01-11T22:00:00",
      "matches": 195,
      "winrate": 51.79,
      "pickrate": 38.98,
      "source": "data_dragon"
    }
  ],
  "total": 100,
  "source": "data_dragon",
  "timestamp": "2026-01-11T22:15:30"
}
```

---

## 🎨 Visualización de Source en Frontend

### 1. Badge Inline
```html
<span class="source-badge">data_dragon</span>
```
**Estilo:** Fondo azul, texto cyan, pequeño

### 2. En Tabla
```
| Fuente         |
|----------------|
| data_dragon ✓  |
| data_dragon ✓  |
```
En cada fila de datos

### 3. En Modal
```
ℹ️ Información
• Fuente de Datos: [data_dragon]
• Último Update: 2026-01-11 22:15:30
```

---

## ⚙️ Validación de Filtros

El dashboard valida automáticamente:

### Validación de Rango
```javascript
// Matchup hours: 1-240
if (hours < 1) hours = 1;
if (hours > 240) hours = 240;

// Matchup limit: 10-500
if (limit < 10) limit = 10;
if (limit > 500) limit = 500;

// Items limit: 5-50
if (limit < 5) limit = 5;
if (limit > 50) limit = 50;

// Raw data limit: 10-1000
if (limit < 10) limit = 10;
if (limit > 1000) limit = 1000;
```

### Validación de Campeón
```javascript
// Verifica que el campeón exista en la lista
if (!allChampions.includes(champion)) {
  showError("Campeón no válido");
  return;
}
```

---

## 🔄 Actualización de Datos

### Auto-refresh
- Dashboard se actualiza automáticamente
- Intervalo: 30 segundos
- Afecta: Summary stats, tier list

### Manual Refresh
- Presiona F5 para refrescar página completa
- Click en tab limpia cache local

### Forzar Actualización de DB
```bash
python setup_meta_analyzer.py
```
Regenera datos demo (borra datos anteriores)

---

## 📈 Tips de Filtrado

### Para Análisis Rápido
```
Filtro: 24h, 50 matchups
Resultado: Overview actual en minutos
```

### Para Análisis Profundo
```
Filtro: 168h (7 días), 200 matchups
Resultado: Tendencias semanales
```

### Para Export/Data Science
```
Filtro: Raw Data, Sin filtro campeón, 1000 registros
Resultado: Dataset completo para análisis externo
```

---

## 🚨 Limitaciones & Notas

- ✅ Máximo 1000 registros por query (performance)
- ✅ Filtros se aplican en backend (no frontend)
- ✅ Source siempre es "data_dragon" actualmente
- ⚠️ Datos de demo son simulados (no datos reales)
- ⚠️ Timestamps son ficticios en modo demo

---

**Última actualización:** 2026-01-11  
**Versión:** 1.0.0
