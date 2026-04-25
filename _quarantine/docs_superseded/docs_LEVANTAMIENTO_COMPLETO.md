# 🚀 Guía de Levantamiento - Meta Analyzer Completo

**Creado:** 11 de enero de 2026
**Status:** ✅ Ready para producción

---

## 📋 Resumen Rápido

Se ha creado un sistema completo con:

✅ **Base de Datos** (SQLite con SQLAlchemy ORM)
✅ **API Backend** (FastAPI REST)
✅ **Frontend Dashboard** (HTML/JS interactivo)
✅ **Data Collection** (Integrado con Riot API)
✅ **Datos Demo** (Para testing sin API key)

---

## 🚀 Levantamiento (5 minutos)

### PASO 1: Instalar dependencias

```bash
pip install -r requirements.txt
```

**Paquetes clave instalados:**
- `sqlalchemy` (ORM para BD)
- `fastapi` (API REST)
- `uvicorn` (Servidor ASGI)

### PASO 2: Ejecutar setup

```bash
# Setup completo con BD + datos demo + frontend
python setup_meta_analyzer.py --demo

# O sin datos demo:
python setup_meta_analyzer.py
```

**Esto crea:**
```
data/meta_analyzer.db          ← BD SQLite
outputs/meta-analyzer-dashboard.html  ← Frontend
```

### PASO 3: Levantar el API backend

```bash
python -m uvicorn src.riot_lol_cli.api_server:app --reload --host 0.0.0.0 --port 8000
```

**Output esperado:**
```
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Press CTRL+C to quit
```

### PASO 4: Abrir Frontend

**Opción A - Archivo local:**
```bash
# Windows
start outputs\meta-analyzer-dashboard.html

# Mac
open outputs/meta-analyzer-dashboard.html

# Linux
xdg-open outputs/meta-analyzer-dashboard.html
```

**Opción B - URL del servidor:**
```
http://localhost:8000/
```

---

## 🌐 URLs Disponibles

### Frontend
- **Dashboard:** http://localhost:8000/ (si hay server configurado)
- **Archivo local:** `outputs/meta-analyzer-dashboard.html`

### API Endpoints

#### Tier Lists
```
GET /api/v1/tier-list/current       → Tier list actual (S/A/B/C/D)
GET /api/v1/tier-list/history?days=7  → Histórico últimos 7 días
```

#### Stats & Data
```
GET /api/v1/stats/latest?limit=50      → Últimas stats (últimas 24h)
GET /api/v1/stats/champion/{name}?hours=24  → Stats de un campeón
GET /api/v1/stats/top-tier          → Top campeones
```

#### Anomalías
```
GET /api/v1/anomalies/high-confidence?min_confidence=0.85  → Anomalías detectadas
GET /api/v1/anomalies/champion/{name}?hours=24  → Anomalías de un campeón
GET /api/v1/anomalies/types         → Tipos de anomalías
```

#### Dashboard
```
GET /api/v1/dashboard/summary       → Resumen para dashboard
```

#### Docs
```
GET /docs                           → Documentación interactiva (Swagger UI)
GET /openapi.json                   → OpenAPI spec
```

---

## 📊 Estructura de Archivos Creados

```
LOLCLI/
├── src/riot_lol_cli/
│   ├── database/
│   │   ├── schema.sql              ← Definición de tablas
│   │   └── models.py               ← ORM (SQLAlchemy)
│   ├── meta_analyzer/
│   │   ├── data_collector_db.py    ← Recolector con BD
│   │   ├── anomaly_detector.py     ← Detector de cambios
│   │   └── tier_generator.py       ← Generador tier lists
│   ├── api_server.py               ← API FastAPI (40+ endpoints)
│   └── dashboard.py                ← Generador frontend
├── data/
│   └── meta_analyzer.db            ← BD SQLite (creada)
├── outputs/
│   └── meta-analyzer-dashboard.html  ← Frontend (creado)
├── setup_meta_analyzer.py          ← Script setup
└── requirements.txt                 ← Dependencias (actualizado)
```

---

## 💾 Base de Datos

### Tablas Principales

| Tabla | Descripción | Ventana |
|-------|-------------|---------|
| `raw_matches` | Partidas crudas | 48h rolling |
| `champion_hourly` | Stats agregadas por hora | Últimas 24h |
| `anomalies` | Cambios detectados | Histórico |
| `tier_lists` | Snapshots de tier lists | Histórico |
| `champion_stats_historical` | Stats por día | 30 días |
| `meta_events` | Eventos de patch | Histórico |
| `analysis_logs` | Logs de análisis | Histórico |

### Conexión a BD

```python
from src.riot_lol_cli.database.models import DatabaseManager

db = DatabaseManager("data/meta_analyzer.db")
db.init_db()

# Obtener sesión
session = db.get_session()

# Consultas
anomalies = db.get_high_confidence_anomalies(min_confidence=0.85)
stats = db.get_latest_stats(limit=50)
tier_list = db.get_tier_list_snapshot()
```

---

## 🔄 Flujo de Datos

```
1. Recolección
   ↓
   MetaDataCollectorDB.collect_matches_batch()
   └→ Riot API V5 Match-V5
   └→ BD: raw_matches
   
2. Agregación
   ↓
   MetaDataCollectorDB.get_hourly_stats()
   └→ BD: champion_hourly (stats horarias)
   
3. Detección
   ↓
   MetaAnomalyDetector.detect_anomalies()
   └→ Z-score analysis (95% confidence)
   └→ BD: anomalies
   
4. Ranking
   ↓
   TierListGenerator.generate_tier_list()
   └→ Tier assignment (S/A/B/C/D)
   └→ BD: tier_lists
   
5. Frontend
   ↓
   Dashboard HTML/JS
   └→ API REST (FastAPI)
   └→ JSON responses
```

---

## 🧪 Testing con Datos Demo

### Sin API Key (Recomendado para testing)

```bash
# 1. Setup con datos demo
python setup_meta_analyzer.py --demo

# 2. Levantar API
python -m uvicorn src.riot_lol_cli.api_server:app --reload

# 3. Abrir dashboard
# → Verás 10 campeones con stats, anomalías y tier list
```

**Datos demo generados:**
- 10 campeones (Ekko, Zed, Ahri, etc.)
- 80 stats horarias (últimas 24h)
- 3 anomalías detectadas
- 1 tier list snapshot

### Con API Key Real

```python
# En tu código
from src.riot_lol_cli.meta_analyzer.data_collector_db import MetaDataCollectorDB

collector = MetaDataCollectorDB(api_key="RGAPI-xxxxx")

# Recolectar partidas
matches = collector.collect_matches_batch(
    summoners=["NombreJugador#ETIQUETA"],
    count_per_summoner=20
)

# Calcular stats
stats = collector.get_hourly_stats()

# Las stats automáticamente se guardan en BD
```

---

## 🛠️ Troubleshooting

### Error: "ModuleNotFoundError: No module named 'fastapi'"

```bash
pip install fastapi uvicorn[standard]
```

### Error: "Database locked"

```bash
# SQLite es single-threaded. Para multi-threading:
# Usar PostgreSQL en lugar de SQLite (ver configuración)

# O resetear la BD:
rm data/meta_analyzer.db
python setup_meta_analyzer.py --demo
```

### Error: "ConnectionRefusedError" al conectar API

```bash
# Asegúrate que el API esté corriendo:
python -m uvicorn src.riot_lol_cli.api_server:app --reload

# En una terminal DIFERENTE, abre el dashboard
```

### Dashboard muestra "Conectando..."

```bash
# 1. Verifica que API esté en http://localhost:8000
# 2. Abre http://localhost:8000/health en navegador
# 3. Debería retornar: {"status": "healthy", ...}
```

---

## 📈 Próximos Pasos

### Phase 2: Polling Real-time (Opcional)

```bash
# Crear daemon que analiza cada hora
python src/riot_lol_cli/daemon.py
```

### Phase 3: Machine Learning (Opcional)

```bash
# Predicciones de próximas 24h
python src/riot_lol_cli/ml_predictor.py
```

### Phase 4: Notificaciones (Opcional)

```bash
# Discord/Slack alerts cuando hay anomalías
python src/riot_lol_cli/notifications.py
```

---

## ✨ Características del Dashboard

### Tier List Visual
- ✅ Organizado por tiers (S/A/B/C/D)
- ✅ Stats por campeón (WR, PR)
- ✅ Colores por tier
- ✅ Click para ver detalles

### Anomalías
- ✅ Cambios detectados en real-time
- ✅ Confidence score (0-100%)
- ✅ Z-score visualizado
- ✅ Descripción de cambios

### Gráficos
- ✅ Top 10 Winrate (horizontal bar)
- ✅ Top 10 Pickrate
- ✅ Auto-actualización cada 30s

### Header
- ✅ Status del sistema (Verde = OK)
- ✅ Última actualización
- ✅ Total de partidas analizadas

---

## 🔐 Seguridad

**Para producción, considera:**

1. **Cambiar BD a PostgreSQL:**
   ```python
   engine = create_engine("postgresql://user:pass@localhost/meta_analyzer")
   ```

2. **Agregar autenticación API:**
   ```python
   from fastapi.security import HTTPBearer
   security = HTTPBearer()
   ```

3. **Rate limiting:**
   ```bash
   pip install slowapi
   ```

4. **HTTPS:**
   ```bash
   # Usar Nginx como reverse proxy
   ```

---

## 📞 Soporte

### Documentación Relacionada
- [META_DETECTION_SYSTEM.md] - Especificación técnica
- [META_DETECTION_PROFESSIONAL_ANALYSIS.md] - Análisis profesional
- [QUICK_START_META_ANALYZER.md] - Quick start

### Código Relevante
- [src/riot_lol_cli/database/models.py] - ORM models
- [src/riot_lol_cli/api_server.py] - API endpoints
- [src/riot_lol_cli/dashboard.py] - Frontend

---

## 📝 Resumen de Comandos

```bash
# Setup
python setup_meta_analyzer.py --demo

# Levantar API
python -m uvicorn src.riot_lol_cli.api_server:app --reload

# Abrir dashboard
start outputs\meta-analyzer-dashboard.html  # Windows
open outputs/meta-analyzer-dashboard.html   # Mac
xdg-open outputs/meta-analyzer-dashboard.html  # Linux

# Test API
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/tier-list/current
curl http://localhost:8000/docs
```

---

**¡Sistema listo para usar! 🚀**

Creado: 11 de enero de 2026
Versión: 1.0.0 - MVP ✅
