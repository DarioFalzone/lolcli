# 🎯 Sistema de Detección de Meta en Tiempo Real - LOLCLI

## 📊 Cómo las Plataformas Detectan Cambios en el Meta

### Plataformas de Referencia
- **U.GG** - Análisis de SoloQ + ProPlay en tiempo real
- **OP.GG** - Estadísticas masivas asiáticas + globales
- **LoLalytics** - Breakdown por elo/región/patch
- **Mobalytics** - Análisis contextual + recomendaciones
- **Blitz.gg** - Integración cliente + predicción
- **ProBuilds.net** - Dados de profesionales
- **METAsrc** - Machine Learning en estadísticas masivas

---

## 🔍 Metodología: Cómo Detectan Cambios de Meta

### Fase 1: Recolección de Datos en Tiempo Real (Día 1)
Las plataformas recolectan datos de **millones de partidas por día**:

```
Fuentes de datos:
├─ API Riot (Match-V5, Summoner-V4)
├─ Scrappers de logs de partidas
├─ Integraciones cliente (op.gg desktop, Blitz overlay)
├─ Replay data
└─ Profesionales (LEC, LCK, Worlds)

Datos recolectados por partida:
├─ Campeón jugado
├─ Items comprados (orden y timestamp)
├─ Runas seleccionadas
├─ Duración de partida
├─ Resultado (W/L)
├─ Elo del jugador
├─ Región geográfica
├─ Rol específico (si aplica)
└─ Timestamp exacto
```

### Fase 2: Agregación de Datos (Ventanas de Tiempo)
```
Ventana de 1 hora:
├─ Campeón A
│  ├─ Pickrate: 8.5%
│  ├─ Winrate: 52.3%
│  ├─ Banrate: 15.2%
│  ├─ Items TOP 3 más comprados
│  ├─ Runas TOP 5 más usadas
│  └─ Tasa de aparición por elo
│
├─ Campeón B
│  └─ ...
└─ [169 campeones más]
```

### Fase 3: Detección de Cambios (Machine Learning)
Las plataformas usan algoritmos para detectar **anomalías estadísticas**:

#### A) Cambios en Winrate
```python
ANOMALIA_DETECTADA si:
  - Winrate actual > (promedio histórico + 2σ)  # Sube 3-5% en 24h
  - ΔWinrate > 2% vs. 24h anterior
  - Pickrate sube pero Winrate sube (no es coincidencia)
```

#### B) Cambios en Itemización
```python
ITEM_EMERGENTE si:
  - Tasa de compra sube de 15% a 45% en 6h
  - Tasa de compra en alta elo sube primero (adelanto)
  - Winrate con ese item > promedio general
  - Delta de posición en build order vs. ayer
```

#### C) Cambios en Runas
```python
RUNA_EMERGENTE si:
  - Tasa de selección aumenta exponencialmente
  - Winrate mejora con nueva runa
  - Cambio en runa principal (Conquerer → Electrocute, etc.)
```

---

## 🚀 Arquitectura de Sistema Para LOLCLI

### Objetivo
Detectar cambios en el meta **desde el Día 1**, no esperar a la Semana 3.

### Paso 1: Pipeline de Datos

```
┌─────────────────┐
│  Riot API V5    │
│  (Match-V5)     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Data Collection Service            │
│  ├─ Fetch matches cada 5 min        │
│  ├─ Parse items/runas/champion      │
│  └─ Store en DB temporal (rolling)  │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Aggregation Layer                  │
│  ├─ Window: 1h, 6h, 24h             │
│  ├─ Calculer winrate/pickrate       │
│  ├─ Agrupar por elo/región          │
│  └─ Normalizar datos                │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Anomaly Detection Engine           │
│  ├─ Statistical outliers            │
│  ├─ Trend analysis                  │
│  ├─ Correlation items ↔ winrate     │
│  └─ Temporal patterns               │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Tier List Generation               │
│  ├─ Rank por winrate (≥100 games)   │
│  ├─ Apply meta weighting            │
│  ├─ Assign tier (S/A/B/C/D)         │
│  └─ Generate timestamp markers      │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Output (HTML/JSON)                 │
│  └─ Timeline histórico de cambios   │
└─────────────────────────────────────┘
```

---

## 💾 Schema de Base de Datos (SQLite/PostgreSQL)

```sql
-- Tabla de matches crudos (rolling window, últimas 48h)
CREATE TABLE raw_matches (
    id VARCHAR PRIMARY KEY,
    timestamp BIGINT,
    champion_id INT,
    role VARCHAR,
    result BOOLEAN,
    items JSONB,              -- [int, int, int, int, int, int, int]
    runes JSONB,              -- {primary: int, secondary: int, ...}
    elo INT,
    region VARCHAR,
    game_duration INT,
    INDEX(timestamp),
    INDEX(champion_id)
);

-- Tabla de agregaciones horarias
CREATE TABLE champion_hourly (
    timestamp BIGINT,
    champion_id INT,
    role VARCHAR,
    elo_tier VARCHAR,          -- "GOLD", "PLATINUM", "DIAMOND", etc.
    matches_count INT,
    wins INT,
    losses INT,
    pickrate FLOAT,            -- % de picks
    winrate FLOAT,             -- % de victorias
    banrate FLOAT,
    top_items JSONB,           -- [item_id, item_id, ...] TOP 3
    top_runes JSONB,
    PRIMARY KEY(timestamp, champion_id, role, elo_tier)
);

-- Tabla de anomalías detectadas
CREATE TABLE anomalies (
    id UUID PRIMARY KEY,
    timestamp BIGINT,
    champion_id INT,
    anomaly_type VARCHAR,      -- "WINRATE_SPIKE", "ITEM_EMERGE", "RUNE_CHANGE"
    magnitude FLOAT,           -- quanto cambió (2.5 = +2.5%)
    confidence FLOAT,          -- 0-1
    details JSONB,             -- contexto adicional
    INDEX(timestamp)
);

-- Tabla de tier lists por timestamp
CREATE TABLE tier_lists (
    timestamp BIGINT,
    snapshot_id VARCHAR PRIMARY KEY,  -- day_1_0h, day_1_6h, etc.
    tier_list JSONB,                   -- [{ champ, tier, wr, pr, ... }]
    meta_shift_indicators JSONB        -- [anomaly_ids]
);
```

---

## 📈 Algoritmo de Detección de Meta (Pseudocódigo)

```python
class MetaDetectionEngine:
    
    def detect_changes(self, current_hour_data, historical_data):
        """Detecta cambios significativos en el meta"""
        
        anomalies = []
        
        for champion in current_hour_data:
            # 1. DETECCIÓN DE SPIKE DE WINRATE
            current_wr = champion['winrate']
            historical_wr = historical_data[champion]['avg_winrate_7d']
            historical_std = historical_data[champion]['std_winrate_7d']
            
            z_score = (current_wr - historical_wr) / historical_std
            if z_score > 2.0:  # 2 desviaciones estándar
                anomalies.append({
                    'type': 'WINRATE_SPIKE',
                    'champion': champion,
                    'magnitude': current_wr - historical_wr,
                    'confidence': min(0.95, z_score / 5.0)
                })
            
            # 2. DETECCIÓN DE CAMBIO DE ITEMIZACIÓN
            current_items = set(champion['top_items'])
            historical_items = set(historical_data[champion]['top_items_7d'])
            
            new_items = current_items - historical_items
            if new_items:
                for item in new_items:
                    item_wr = self.calculate_item_wr(champion, item)
                    if item_wr > champion['overall_wr'] + 1.5:
                        anomalies.append({
                            'type': 'ITEM_EMERGE',
                            'champion': champion,
                            'item': item,
                            'item_wr': item_wr,
                            'confidence': 0.85
                        })
            
            # 3. DETECCIÓN DE CAMBIO DE RUNAS
            current_rune = champion['primary_rune']
            historical_rune = historical_data[champion]['primary_rune']
            
            if current_rune != historical_rune:
                rune_wr = self.calculate_rune_wr(champion, current_rune)
                if rune_wr > champion['overall_wr'] + 2.0:
                    anomalies.append({
                        'type': 'RUNE_CHANGE',
                        'champion': champion,
                        'old_rune': historical_rune,
                        'new_rune': current_rune,
                        'winrate_delta': rune_wr - champion['overall_wr'],
                        'confidence': 0.90
                    })
            
            # 4. DETECCIÓN DE SINERGIA META
            # Si muchos campeones spike juntos
            if len(anomalies) > 3 and self.check_meta_shift():
                anomalies.append({
                    'type': 'META_SHIFT',
                    'description': 'Cambio significativo en el meta general',
                    'affected_champions': len(anomalies),
                    'confidence': 0.92
                })
        
        return anomalies
    
    def generate_tier_list(self, champion_data, anomalies):
        """Genera tier list considerando meta shifts"""
        
        tier_list = []
        
        for champion in champion_data:
            # Base: winrate puro
            tier = self.get_base_tier(champion['winrate'])
            
            # Ajuste 1: Pickrate (champeones populares son estudiados)
            if champion['pickrate'] < 2:
                tier = downgrade_tier(tier)  # Puede ser subestimado
            
            # Ajuste 2: Confianza (>=100 juegos)
            if champion['matches'] < 100:
                tier = add_uncertainty(tier)
            
            # Ajuste 3: Si hay anomalía detectada
            anomaly = find_anomaly(champion, anomalies)
            if anomaly and anomaly['confidence'] > 0.85:
                tier = upgrade_tier(tier)  # Tendencia al alza
                tier['trend'] = 'RISING'
            
            tier_list.append({
                'champion': champion['name'],
                'tier': tier,
                'winrate': champion['winrate'],
                'pickrate': champion['pickrate'],
                'banrate': champion['banrate'],
                'matches': champion['matches'],
                'trend': tier.get('trend', 'STABLE'),
                'changed_at': anomaly.get('timestamp') if anomaly else None
            })
        
        # Sort por tier (S > A > B > C > D)
        return sort_by_tier(tier_list)
    
    def get_base_tier(self, winrate):
        """Asigna tier basado en winrate"""
        if winrate >= 54:
            return 'S'
        elif winrate >= 51.5:
            return 'A'
        elif winrate >= 48.5:
            return 'B'
        elif winrate >= 46:
            return 'C'
        else:
            return 'D'
```

---

## 📅 Ejemplo: Detección de Ekko (Tu Caso)

### Día 1 - Parche 15.2 (Items nuevos)

**Timeline:**
```
00:00 - Parche aplicado
  └─ Items nuevos disponibles
  └─ Ekko: WR 49.2%, PR 4.5% (histórico)

06:00 - Primeros datos llegando
  └─ Ekko pickrate: 5.1% (+0.6%)
  └─ Ekko winrate: 49.8% (+0.6%)
  └─ ITEM NUEVO: "Hollow Radiance" en 38% de builds
  └─ Sistema: ⚠️ OBSERVACIÓN (no es significativo aún)

12:00 - Datos acumulándose
  └─ Ekko pickrate: 6.8% (+1.7%)
  └─ Ekko winrate: 51.2% (+2.0%)  ← ESTADÍSTICAMENTE SIGNIFICATIVO
  └─ "Hollow Radiance" → 64% de builds
  └─ Item-specific winrate con Hollow: 53.5%
  └─ Sistema: 🔔 ANOMALÍA DETECTADA (z-score = 2.4)
  └─ Tier: B → A (TENDENCIA AL ALZA)

18:00 - Confirmación
  └─ 500+ matches procesados
  └─ Ekko WR: 52.1% (estable)
  └─ Sistema CONFIDENCE: 0.92
  └─ Tier: A (CONFIRMED)

Día 1 Resumen:
✅ Cambio detectado en 12 horas
✅ Antes que la comunidad lo note
✅ vs. Semana 3 (día 21)
```

---

## 🛠️ Implementación en LOLCLI

### Estructura de Carpetas Propuesta

```
LOLCLI/
├── meta_analyzer/
│   ├── __init__.py
│   ├── data_collector.py      # Recolecta datos de Riot API
│   ├── aggregator.py          # Agrega en ventanas de tiempo
│   ├── anomaly_detector.py    # Detecta cambios
│   ├── tier_generator.py      # Genera tier lists
│   ├── models.py              # SQLAlchemy models
│   └── utils.py               # Helpers (stats, math)
├── data/
│   ├── meta_db.sqlite         # Base de datos de meta
│   └── cache/
│       ├── hourly_stats.json  # Últimas 48h
│       └── anomalies.json
└── outputs/
    └── meta_timeline.html     # Tier list con timeline
```

### Comandos Propuestos (CLI)

```bash
# Iniciar detector de meta (background)
python -m meta_analyzer.collector start --interval 5m

# Generar tier list actual
python -m meta_analyzer.tier_generator generate --output outputs/current_tier_list.json

# Ver anomalías en últimas 24h
python -m meta_analyzer.anomaly_detector show --hours 24

# Timeline histórico de un campeón
python -m meta_analyzer show-champion Ekko --since "24h" --timeline

# Dashboard HTML con timeline interactivo
python -m meta_analyzer generate-html --output outputs/meta_dashboard.html
```

---

## 📊 Métricas Clave de Vigilancia

### Para Detectar Cambios TEMPRANO

| Métrica | Umbral | Acción |
|---------|--------|--------|
| **ΔWR (24h)** | > +2.0% | 🔔 Alert: Posible buff/sinergias nuevas |
| **ΔPickrate (24h)** | > +3.0% | 🔔 Alert: Posible cambio en valoración |
| **Item Emergence** | +15% pickrate en 6h | 🔔 Alert: Nueva itemización detectada |
| **Confidence Score** | > 0.85 | ✅ Tier list update |
| **Sample Size** | > 100 games | ✅ Datos válidos |
| **Z-score WR** | > 2.0σ | 🔔 Anomalía estadística |

---

## 🎯 Ventajas vs. Competencia

Con este sistema en LOLCLI podrías:

✅ **Detectar cambios el mismo día** (no esperar semanas)
✅ **Timeline histórico** de cada cambio
✅ **Análisis causa-efecto** (qué item/runa causó subida)
✅ **Predicción temprana** basada en patrón
✅ **Alertas personalizadas** por rol/elo
✅ **Comparación regional** (LAS vs. EUW vs. KR)
✅ **Análisis profesional** (LEC vs. SoloQ trends)

---

## 🔧 Dependencias Python Necesarias

```
numpy              # Para cálculos estadísticos
pandas             # Para DataFrames y análisis
scipy              # Para distribuciones estadísticas
sqlalchemy         # ORM para base de datos
requests           # Para Riot API
plotly             # Para gráficos interactivos
jinja2             # Para templating HTML
```

---

## 📈 Roadmap de Implementación

### Phase 1: MVP (Esta semana)
- [ ] Data collector (Match-V5 polling)
- [ ] Hourly aggregation
- [ ] Basic tier list generation
- [ ] SQLite database

### Phase 2: Detection (Próxima semana)
- [ ] Anomaly detection engine
- [ ] Z-score calculations
- [ ] Item emergence detection
- [ ] Alerts/logging

### Phase 3: UI (Semana 3)
- [ ] HTML dashboard
- [ ] Timeline interactivo
- [ ] Gráficos históricos
- [ ] API JSON

### Phase 4: Intelligence (Semana 4)
- [ ] Machine Learning predictions
- [ ] Causa-efecto analysis
- [ ] Regional comparison
- [ ] Pro play correlation

---

**Creado:** 11 de enero de 2026
**Objetivo:** Detectar meta cambios en tiempo real, desde el día 1
