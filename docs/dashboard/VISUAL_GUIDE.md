# 🎨 Guía Visual - Dashboard Mejorado

## 📱 Vista General del Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚔️ LOLCLI Meta Analyzer - Enhanced                  Sistema: ✓ │
│  Última actualización: 22:15:30                                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ [📊 Dashboard] [⚡ Matchups] [🛡️ Items] [📋 Raw Data]           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┬──────────────┬──────────────┬──────────────┐
│    31 ADCs      │  1248 Matches│    3 Anomalías│   24h Update  │
└─────────────────┴──────────────┴──────────────┴──────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│ TIER LIST (TAB DASHBOARD)                                      │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐
│ │ 🔴 TIER S - OP (5)                                          │
│ ├─────────────────────────────────────────────────────────────┤
│ │ [Corki]    [Miss F.]   [Yasuo]    [Kalista]    [Aphelios]  │
│ │ WR: 58.6%  WR: 51.2%   WR: 52.1%  WR: 54.3%    WR: 50.9%   │
│ │ PR: 42.3%  PR: 38.1%   PR: 39.2%  PR: 41.5%    PR: 37.8%   │
│ └─────────────────────────────────────────────────────────────┘
│
│ ┌─────────────────────────────────────────────────────────────┐
│ │ 🟠 TIER A - MUY BUENO (8)                                  │
│ ├─────────────────────────────────────────────────────────────┤
│ │ [Lucian]   [Ezreal]    [Jinx]     [Twitch]    [Kog Maw]    │
│ │ WR: 49.8%  WR: 48.7%   WR: 47.3%  WR: 46.8%   WR: 45.9%   │
│ │ PR: 28.4%  PR: 27.1%   PR: 26.3%  PR: 25.7%   PR: 24.9%   │
│ │                                                            │
│ │ [Draven]   [MF]        [Senna]                           │
│ │ WR: 45.2%  WR: 44.8%   WR: 44.1%                       │
│ │ PR: 23.8%  PR: 22.1%   PR: 21.3%                       │
│ └─────────────────────────────────────────────────────────────┘
│
│ [... más tiers ...]
│
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Tab Matchups

```
┌─────────────────────────────────────────────────────────────────┐
│ MATCHUPS - Historial de Enfrentamientos                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 🔍 FILTROS:                                                    │
│                                                                 │
│ Campeón:           [▼ Seleccionar...]  ← Dropdown con 31 ADCs  │
│ Últimas (horas):   [24] (1-240)        ← Input rango           │
│ Límite:            [50] (10-500)       ← Input rango           │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Hora                Campeón Rival  Partidas  W/L    WR%  Trend  Source
│ ─────────────────────────────────────────────────────────────────
│ 2026-01-11 22:00   Kalista           148    86/62  58.1% UP ↑   data_dragon
│ 2026-01-11 21:00   Ashe              134    73/61  54.5% STABLE =  data_dragon
│ 2026-01-11 20:00   Jinx              156    78/78  50.0% DOWN ↓   data_dragon
│ 2026-01-11 19:00   Lucian            142    68/74  47.9% DOWN ↓   data_dragon
│ 2026-01-11 18:00   Ezreal            138    61/77  44.2% DOWN ↓   data_dragon
│ [... más registros ...]
│                                                                 │
│ 💡 Click encabezado = Ordenar (sort)                           │
│ 💡 Click fila = Ver detalles en modal                          │
│ 💡 Badge = Source attribution                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛡️ Tab Items

```
┌─────────────────────────────────────────────────────────────────┐
│ ITEMS - Construcción de Builds por Campeón                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 🔍 FILTROS:                                                    │
│                                                                 │
│ Campeón:       [▼ Seleccionar...]  ← Dropdown                 │
│ Top Items:     [10] (5-50)         ← Input rango               │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Item ID    Frecuencia    Build Path              Source         │
│ ──────────────────────────────────────────────────────────────
│ 6672           45         Starter Item           data_dragon   │
│ 3031           43         Core Build             data_dragon   │
│ 3089           41         Defensive              data_dragon   │
│ 3094           38         Offensive              data_dragon   │
│ 3143           36         Utility                data_dragon   │
│ 3111           34         AD Item                data_dragon   │
│ 3036           32         Movement               data_dragon   │
│ 3052           30         MR Item                data_dragon   │
│ 3076           28         Armor Item             data_dragon   │
│ 3090           26         Hybrid                 data_dragon   │
│                                                                 │
│ 💡 Muestra los items más usados por orden de frecuencia       │
│ 💡 Identifica ruta de build meta                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Tab Raw Data

```
┌─────────────────────────────────────────────────────────────────┐
│ RAW DATA - Datos Sin Filtrar                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 🔍 FILTROS:                                                    │
│                                                                 │
│ Campeón (optional):    [▼ Todos] ← Dropdown opcional           │
│ Límite:                [100] (10-1000)                         │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Campeón          Hora                  Matches  WR%   PR%  Source
│ ────────────────────────────────────────────────────────────────
│ Corki           2026-01-11 22:00:00    248     58.6% 42.3% data_dragon
│ Miss Fortune    2026-01-11 22:00:00    195     51.8% 39.0% data_dragon
│ Yasuo           2026-01-11 22:00:00    187     52.1% 38.5% data_dragon
│ Kalista         2026-01-11 22:00:00    203     54.3% 41.5% data_dragon
│ Aphelios        2026-01-11 22:00:00    178     50.9% 37.8% data_dragon
│ Lucian          2026-01-11 22:00:00    156     49.8% 32.1% data_dragon
│ [... 94 registros más ...]
│                                                                 │
│ 💡 Click en campeón = Ver detalles                             │
│ 💡 Datos exportables para análisis externo                     │
│ 💡 Source en cada registro para auditoría                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Modal de Detalles del Campeón

```
                    ┌─────────────────────────┐
                    │ Corki  [data_dragon] ✕  │
                    ├─────────────────────────┤
                    │                         │
                    │ 📊 ESTADÍSTICAS ACTUALES│
                    │                         │
                    │ • Winrate: 58.6%       │
                    │ • Pickrate: 42.3%      │
                    │ • Partidas: 1,247      │
                    │ • Tier: S (OP)         │
                    │                         │
                    ├─────────────────────────┤
                    │                         │
                    │ ⚠️ ANOMALÍAS DETECTADAS│
                    │                         │
                    │ HIGH_WINRATE           │
                    │ Confianza: 95%         │
                    │ "Corki tiene 10% más   │
                    │  WR que su promedio    │
                    │  histórico"            │
                    │                         │
                    │ STABLE_PICKRATE        │
                    │ Confianza: 87%         │
                    │ "Pickrate estable en   │
                    │  últimas 24h"          │
                    │                         │
                    ├─────────────────────────┤
                    │                         │
                    │ ℹ️ INFORMACIÓN         │
                    │                         │
                    │ • Fuente: data_dragon  │
                    │ • Actualizado: 2026-01-11
                    │   22:15:30             │
                    │                         │
                    └─────────────────────────┘

    ESC o click fuera → Cierra modal
```

---

## 🎨 Elementos UI

### Badges de Source
```
┌─────────────────┐
│ data_dragon ✓   │  ← Badge azul/cyan
└─────────────────┘  Indica origen de datos
```

### Indicadores de Tendencia
```
UP ↑    → Campeón mejorando (color verde)
STABLE = → Campeón estable (color naranja)
DOWN ↓  → Campeón empeorando (color rojo)
```

### Colores en Stats
```
Winrate:   59.2%  ← Verde (success color)
Pickrate:  42.1%  ← Cyan (info color)
Losses:    62     ← Rojo (danger color)
Wins:      86     ← Verde (success color)
```

### Tier Colors
```
🔴 Tier S - Rojo vivo       (OP Champions)
🟠 Tier A - Naranja         (Very Good)
🔵 Tier B - Cyan/Turquoise  (Viable)
🟢 Tier C - Verde           (Acceptable)
⚪ Tier D - Gris            (Weak)
```

---

## 📱 Responsividad

### Desktop (1400px+)
```
┌─────────────────────────────────────────────────────────────────┐
│ Full Width Dashboard con 4 columnas/3 filas                    │
│ Tablas con todas las columnas visibles                         │
│ Filtros en una línea                                           │
└─────────────────────────────────────────────────────────────────┘
```

### Tablet (768px - 1399px)
```
┌──────────────────────────────────┐
│ Medium Dashboard                 │
│ 2 columnas/2 filas               │
│ Tablas con scroll horizontal     │
│ Filtros en 2 líneas              │
└──────────────────────────────────┘
```

### Mobile (< 768px)
```
┌──────────┐
│ Compact  │
│ 1 col    │
│ 1 fila   │
│ Full    │
│ width    │
│ scroll   │
└──────────┘
```

---

## ⌨️ Atajos de Teclado

| Tecla | Acción |
|-------|--------|
| Tab | Navegar entre elementos |
| Enter | Confirmar filtro |
| ESC | Cerrar modal |
| Click | Interactuar con elementos |

---

## 🖱️ Interacciones Mouse

| Acción | Resultado |
|--------|-----------|
| Hover en campeón | Destaca con sombra |
| Click en campeón | Abre modal detalles |
| Click en tab | Cambia de vista |
| Click encabezado tabla | Ordena esa columna |
| Click fila tabla | Abre detalles (algunas tabs) |
| Hover filtro | Tooltip con info |

---

## 📊 Equivalencia Visual

### ANTES (Dashboard Original)
```
┌────────────────┐
│ Tier List ONLY │
│  S│A│B│C│D    │
│                │
│ Limited info   │
└────────────────┘
```

### AHORA (Dashboard Mejorado)
```
┌──────────────────────────────────┐
│ 📊 Dashboard │ ⚡ Matchups      │
│ 🛡️ Items    │ 📋 Raw Data      │
├──────────────────────────────────┤
│ ✅ Tier List                     │
│ ✅ Matchup history               │
│ ✅ Build analysis                │
│ ✅ Raw data export               │
│ ✅ Source attribution            │
│ ✅ Modal details                 │
│ ✅ Filtros avanzados            │
│ ✅ Tablas ordenables            │
└──────────────────────────────────┘
```

---

## 🔄 Flujos de Navegación

### Flujo 1: ADC Overview
```
Abre Dashboard
     ↓
Ve Tier List
     ↓
Click campeón
     ↓
Ver detalles en Modal
     ↓
Cierra modal (ESC)
```

### Flujo 2: Análisis de Matchup
```
Abre Dashboard
     ↓
Click tab Matchups
     ↓
Selecciona campeón
     ↓
Ajusta filtros
     ↓
Analiza tabla
     ↓
Click en fila para detalles
     ↓
Identifica strengths/weaknesses
```

### Flujo 3: Build Copying
```
Click tab Items
     ↓
Elige campeón
     ↓
Ve top 10 items
     ↓
Identifica core + late game
     ↓
Copia build mentalmente/físicamente
```

### Flujo 4: Data Export
```
Click tab Raw Data
     ↓
(Opcional) Filtra por campeón
     ↓
Aumenta límite a 500-1000
     ↓
Selecciona todos (Ctrl+A)
     ↓
Copia (Ctrl+C)
     ↓
Pega en editor/Excel
     ↓
Analiza datos externos
```

---

## ⚙️ Componentes Técnicos Visibles

### Header
```
┌─────────────────────────────────┐
│ ⚔️ LOLCLI Meta Analyzer Enhanced│
│ Sistema: ✓  |  22:15:30        │
└─────────────────────────────────┘
```

### Navigation
```
[📊 Dashboard] [⚡ Matchups] [🛡️ Items] [📋 Raw Data]
     ↑ Active (highlighted)
```

### Statistics Bar
```
┌──────┬──────┬──────┬──────┐
│ 31   │1248  │  3   │ 24h  │
│ ADCs │Match │Anom  │ Upd  │
└──────┴──────┴──────┴──────┘
```

### Filter Section
```
Campeón: [dropdown]  Horas: [input]  Límite: [input]
```

### Data Table
```
Headers (sorteable) → Rows → Source badge
```

### Modal Overlay
```
Fondo oscuro + blur
Modal centrado
Close button en esquina
```

---

**Versión:** 1.0.0 Visual Guide  
**Fecha:** 2026-01-11  
**Status:** ✅ Dashboard Mejorado Completo
