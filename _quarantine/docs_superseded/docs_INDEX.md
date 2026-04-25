# 📖 LOLCLI - Índice Completo de Documentación

## 🎯 Inicio Rápido

- **5 minutos:** [Quick Start](/docs/dashboard/QUICKSTART.md) - Tener todo corriendo
- **Dashboard:** [Dashboard Mejorado](/docs/dashboard/DASHBOARD_ENHANCED.md) - Guía completa
- **Filtros:** [Filtros & Data Source](/docs/dashboard/FILTERS_AND_SOURCES.md) - Attribution system

---

## 📊 Dashboard & Frontend

### Dashboard Mejorado ⭐ (RECOMENDADO)
Interfaz avanzada con múltiples tabs, filtros interactivos y source attribution.

- 📄 [DASHBOARD_ENHANCED.md](/docs/dashboard/DASHBOARD_ENHANCED.md)
  - Características principales
  - Guía de uso
  - API endpoints
  - Troubleshooting
  
- ⚡ [QUICKSTART.md](/docs/dashboard/QUICKSTART.md)
  - 5 pasos en 5 minutos
  - Comandos rápidos
  - Casos de uso comunes
  
- 🔍 [FILTERS_AND_SOURCES.md](/docs/dashboard/FILTERS_AND_SOURCES.md)
  - Filtros disponibles
  - Data source attribution
  - Parámetros query de API

---

## 🔧 Backend & APIs

### Meta Analyzer System
Sistema de análisis de meta en tiempo real.

- 📚 [Meta Analyzer Guide](/docs/meta_analyzer/META_ANALYZER_GUIDE.md)
  - Arquitectura
  - Componentes
  - Flujo de datos
  
- 📊 [Database Schema](/docs/meta_analyzer/DATABASE_SCHEMA.md)
  - Tablas
  - Relaciones
  - Modelos
  
- 🔌 [API Endpoints](/docs/meta_analyzer/API_ENDPOINTS.md)
  - REST endpoints
  - Query parameters
  - Response examples
  
- ⚙️ [Configuration](/docs/meta_analyzer/CONFIGURATION.md)
  - Variables de ambiente
  - Ajustes de performance
  - Opciones de instalación

---

## 📍 ADC Tracker

Sistema especializado para trackear ADCs (Attack Damage Carry) en League of Legends.

- 📋 [ADC Tracker Overview](/docs/adc_tracker/ADC_TRACKER_OVERVIEW.md)
  - 31 ADCs soportados
  - Data Dragon source
  
- 🎯 [ADC Statistics](/docs/adc_tracker/ADC_STATISTICS.md)
  - Stats por campeón
  - Meta trends
  - Anomaly detection
  
- 📈 [Tier List System](/docs/adc_tracker/TIER_LIST_SYSTEM.md)
  - Tier calculation
  - Ranking algorithm
  - Update frequency
  
- 🔍 [Data Analysis](/docs/adc_tracker/DATA_ANALYSIS.md)
  - Statistical methods
  - Confidence intervals
  - Trend detection

---

## 🚀 Setup & Instalación

### Guías de Setup
- 📦 [Setup Guide](/docs/SETUP.md)
  - Instalación Python
  - Dependencias
  - Configuración inicial
  
- 🐍 [Python Environment](/docs/PYTHON_ENVIRONMENT.md)
  - Virtual environment
  - Requirements.txt
  - Troubleshooting dependencias

### Scripts Disponibles
- `python setup_meta_analyzer.py` - Setup completo (BD + demo data + frontend)
- `python run_api.py` - Iniciar API server
- `python generate_dashboard.py` - Regenerar dashboard
- `python main.py` - Main entry point
- `python verify_adc_tracker.py` - Verificar ADCs en BD

---

## 🐛 Troubleshooting & FAQ

- ❓ [FAQ](/docs/FAQ.md)
  - Preguntas frecuentes
  - Respuestas comunes
  
- 🔧 [Troubleshooting](/docs/TROUBLESHOOTING.md)
  - Problemas comunes
  - Soluciones paso a paso
  
- 📞 [Support](/docs/SUPPORT.md)
  - Recursos de ayuda
  - Contacto
  - Comunidad

---

## 📁 Estructura de Carpetas

```
LOLCLI/
├── /docs/                          # Documentación
│   ├── /dashboard/                 # Dashboard guides
│   │   ├── DASHBOARD_ENHANCED.md   # Dashboard mejorado
│   │   ├── QUICKSTART.md           # 5 min setup
│   │   ├── FILTERS_AND_SOURCES.md  # Filtros & attribution
│   ├── /adc_tracker/               # ADC tracker docs
│   │   ├── ADC_TRACKER_OVERVIEW.md
│   │   ├── ADC_STATISTICS.md
│   │   ├── TIER_LIST_SYSTEM.md
│   │   ├── DATA_ANALYSIS.md
│   ├── /meta_analyzer/             # Meta analyzer docs
│   │   ├── META_ANALYZER_GUIDE.md
│   │   ├── DATABASE_SCHEMA.md
│   │   ├── API_ENDPOINTS.md
│   │   ├── CONFIGURATION.md
│   ├── INDEX.md                    # Este archivo
│   ├── SETUP.md
│   ├── FAQ.md
│   ├── TROUBLESHOOTING.md
│   ├── SUPPORT.md
│
├── /scripts/                       # Scripts ejecutables
│   ├── fetch_adc_champions.py
│   ├── setup_meta_analyzer.py
│   ├── verify_adc_tracker.py
│
├── /src/
│   └── /riot_lol_cli/
│       ├── api_server.py           # FastAPI backend
│       ├── dashboard.py            # Dashboard original
│       ├── dashboard_enhanced.py   # Dashboard mejorado
│       ├── /database/
│       │   ├── models.py
│       │   ├── manager.py
│       ├── /analyzer/
│       │   ├── meta_analyzer.py
│       │   ├── anomaly_detector.py
│
├── /data/
│   ├── meta_analyzer.db            # SQLite database
│   ├── splash-manifest.json
│   ├── /cache/
│
├── /outputs/
│   ├── meta-analyzer-dashboard.html           # Dashboard original
│   ├── meta-analyzer-dashboard-enhanced.html  # Dashboard mejorado
│   ├── splash-viewer.html
│
├── /templates/                     # Backups de dashboard
├── /config/
│   └── version.json
│
├── generate_dashboard.py           # Generador de dashboard
├── main.py                        # Entry point
├── run_api.py                     # API runner
├── setup_meta_analyzer.py         # Setup completo
├── requirements.txt               # Dependencias Python
├── README.md                      # README principal
├── QUICK_START.md                 # Quick start
```

---

## 🔄 Flujo de Datos

```
┌─────────────────────────────────┐
│  Data Dragon API (Riot Games)   │
│  - Champion stats               │
│  - Item information             │
│  - Meta data                    │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Backend (FastAPI)              │
│  - /api/v1/champions/*          │
│  - /api/v1/tier-list/*          │
│  - /api/v1/dashboard/*          │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Database (SQLite)              │
│  - ChampionHourly               │
│  - Anomaly                      │
│  - TierList                     │
│  - AnalysisLog                  │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Frontend (HTML/JS)             │
│  - Dashboard Enhanced ⭐        │
│  - Charts & Tables              │
│  - Filters & Modals             │
└─────────────────────────────────┘
```

---

## 📊 Estadísticas del Proyecto

- **Campeones Trackeados:** 31 ADCs (Data Dragon)
- **Endpoints API:** 45+ REST endpoints
- **Tablas DB:** 7 (ChampionHourly, Anomaly, TierList, etc.)
- **Frontend Tabs:** 4 (Dashboard, Matchups, Items, Raw Data)
- **Datos Demo:** 248 registros (8 por ADC)
- **Fuente Principal:** Riot Games Data Dragon API

---

## 🎯 Próximas Fases

### Phase 1: ✅ Completada
- Setup y scaffolding
- 31 ADCs configurados
- Dashboard mejorado
- API endpoints base

### Phase 2: 🔄 En Progreso
- Integración con Riot Official API
- Auto-refresh de datos
- Notificaciones de anomalías

### Phase 3: ⏳ Planeada
- Análisis predictivo
- Comparación de campeones
- Gráficos de tendencias
- Exportación a CSV/Excel

---

## 📚 Recursos Externos

- [Data Dragon API](https://ddragon.leagueoflegends.com/)
- [Riot Developer Portal](https://developer.riotgames.com/)
- [League of Legends Meta](https://www.lolmeta.net/)
- [OP.GG Statistics](https://op.gg/)
- [U.GG Analytics](https://u.gg/)

---

## 🤝 Contribuir

Para contribuir al proyecto:
1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/amazing-feature`)
3. Commit cambios (`git commit -m 'Add amazing feature'`)
4. Push a rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver [LICENSE](LICENSE) para detalles.

---

## ✍️ Autores

**LOLCLI Development Team**
- Análisis de meta con IA
- Sistema de detección de anomalías
- Dashboard interactivo

---

## 📞 Soporte

- 📖 Consulta la [documentación](/docs/)
- ❓ Revisa [FAQ](/docs/FAQ.md)
- 🐛 Reporta bugs en [SUPPORT](/docs/SUPPORT.md)
- 💬 Comunidad: [Discord/Chat]

---

**Última actualización:** 2026-01-11  
**Versión:** 1.0.0 - Dashboard Enhanced  
**Mantenedor:** LOLCLI Team

---

## 🗺️ Navegación Rápida

| Necesito... | Ir a... |
|------------|---------|
| Empezar rápido | [QUICKSTART.md](/docs/dashboard/QUICKSTART.md) |
| Usar el dashboard | [DASHBOARD_ENHANCED.md](/docs/dashboard/DASHBOARD_ENHANCED.md) |
| Entender filtros | [FILTERS_AND_SOURCES.md](/docs/dashboard/FILTERS_AND_SOURCES.md) |
| Setup del proyecto | [SETUP.md](/docs/SETUP.md) |
| Entender la base de datos | [DATABASE_SCHEMA.md](/docs/meta_analyzer/DATABASE_SCHEMA.md) |
| Conocer los APIs | [API_ENDPOINTS.md](/docs/meta_analyzer/API_ENDPOINTS.md) |
| Información de ADCs | [ADC_TRACKER_OVERVIEW.md](/docs/adc_tracker/ADC_TRACKER_OVERVIEW.md) |
| Resolver problemas | [TROUBLESHOOTING.md](/docs/TROUBLESHOOTING.md) |
