# 📖 ÍNDICE MAESTRO - LOLCLI Meta Analyzer

> **EMPIEZA AQUÍ PRIMERO** 👈

---

## 🎯 ¿Dónde estoy?

Si acabas de llegar al proyecto, aquí está TODO lo que necesitas.

---

## 📘 DOCUMENTO PRINCIPAL (LEE ESTO PRIMERO)

### **[META_ANALYZER_GUIA_COMPLETA.md](META_ANALYZER_GUIA_COMPLETA.md)** ⭐⭐⭐

**ESTE ES TU DOCUMENTO ÚNICO.** Incluye:
- ✅ Qué se creó
- ✅ Cómo levantar (3 opciones)
- ✅ Flujo de datos completo
- ✅ API endpoints
- ✅ Dashboard features
- ✅ Cómo usar con datos reales
- ✅ Troubleshooting
- ✅ Próximos pasos

**Tiempo de lectura:** 15-20 minutos  
**No necesitas nada más para empezar.**

---

## 🚀 LEVANTAMIENTO RÁPIDO (2 opciones)

### Opción A: Automático (Recomendado)
```bash
# Windows
LEVANTAMIENTO_RAPIDO.bat

# Linux/Mac
bash LEVANTAMIENTO_RAPIDO.sh
```

### Opción B: Manual
```bash
python setup_meta_analyzer.py --demo
python -m uvicorn src.riot_lol_cli.api_server:app --reload
start outputs\meta-analyzer-dashboard.html
```

---

## 📚 DOCUMENTACIÓN ADICIONAL (Opcional)

Si quieres profundizar en algún aspecto específico:

### Análisis Profesional
**[META_DETECTION_PROFESSIONAL_ANALYSIS.md](META_DETECTION_PROFESSIONAL_ANALYSIS.md)**
- Cómo funcionan u.gg, op.gg, mobalytics
- Estrategia de detección profesional
- Por qué funciona este sistema

### Especificación Técnica
**[META_DETECTION_SYSTEM.md](META_DETECTION_SYSTEM.md)**
- Arquitectura sistema (nivel técnico)
- Database schema detallado
- Pseudocódigo algoritmos

### Levantamiento Detallado
**[LEVANTAMIENTO_COMPLETO.md](LEVANTAMIENTO_COMPLETO.md)**
- Guía paso a paso con screenshots
- Todos los endpoints documentados
- Troubleshooting exhaustivo

### Resumen Visual
**[RESUMEN_VISUAL.md](RESUMEN_VISUAL.md)**
- Diagramas de arquitectura
- Estructura de carpetas
- Comandos rápidos

### Checklist de Verificación
**[CHECKLIST_VERIFICACION.md](CHECKLIST_VERIFICACION.md)**
- Qué se verificó
- Métricas del proyecto
- Feature completeness

---

## 💻 ARCHIVOS CREADOS

### Backend (Python)

```
src/riot_lol_cli/
├── database/
│   ├── schema.sql          (200 líneas)
│   └── models.py           (500 líneas)
│
├── meta_analyzer/
│   ├── data_collector_db.py (400 líneas) ← Recolecta datos
│   ├── anomaly_detector.py   (400 líneas) ← Detecta cambios
│   └── tier_generator.py     (400 líneas) ← Genera tier lists
│
├── api_server.py           (500 líneas) ← API FastAPI
└── dashboard.py            (300 líneas) ← Frontend HTML/JS
```

### Setup & Scripts

```
setup_meta_analyzer.py          (300 líneas) ← Setup automático
LEVANTAMIENTO_RAPIDO.bat        (Windows)
LEVANTAMIENTO_RAPIDO.sh         (Linux/Mac)
requirements.txt                (Dependencias actualizadas)
```

### Output Files

```
data/
└── meta_analyzer.db            (BD SQLite - 7 tablas)

outputs/
└── meta-analyzer-dashboard.html (Frontend - 50 KB)
```

---

## 🎯 ESTRUCTURA RÁPIDA

```
┌─────────────────────────────────────┐
│   USUARIO (Navegador)               │
│   Dashboard HTML/JS interactivo     │
└──────────────┬──────────────────────┘
               │ AXIOS (HTTP)
               ▼
┌──────────────────────────────┐
│   FASTAPI (40+ endpoints)    │
│   Port: 8000                 │
│   /docs para Swagger UI      │
└──────────────┬───────────────┘
               │ SQLAlchemy ORM
               ▼
┌──────────────────────────────┐
│   SQLite Database            │
│   7 Tablas (data/*.db)       │
└──────────────────────────────┘
```

---

## 📊 DATOS DEMO INCLUIDOS

Al ejecutar setup, obtienes automáticamente:

**10 Campeones:**
```
Ekko        WR: 52.5% ⭐ (Tier A)
Zed         WR: 51.2% ⭐ (Tier A)
Ahri        WR: 50.8% ⭐ (Tier A)
... y 7 más
```

**3 Anomalías detectadas:**
```
WINRATE_SPIKE (Ekko) - Conf: 92%
ITEM_EMERGENCE (Zed) - Conf: 89%
PICKRATE_SURGE (Ahri) - Conf: 87%
```

**80 registros horarios** (últimas 24h)

---

## 🔗 URLs IMPORTANTES

| Recurso | URL |
|---------|-----|
| **Dashboard** | `outputs/meta-analyzer-dashboard.html` |
| **API Health** | http://localhost:8000/health |
| **API Docs** | http://localhost:8000/docs |
| **Tier List API** | http://localhost:8000/api/v1/tier-list/current |
| **Anomalías API** | http://localhost:8000/api/v1/anomalies/high-confidence |

---

## ✅ VERIFICACIÓN (¿Funciona todo?)

```bash
# Test 1: Setup
python setup_meta_analyzer.py --demo
# Debería crear data/meta_analyzer.db ✅

# Test 2: API
python -m uvicorn src.riot_lol_cli.api_server:app --reload
# Debería decir "Uvicorn running on http://0.0.0.0:8000" ✅

# Test 3: Health check
curl http://localhost:8000/health
# Debería retornar {"status": "healthy"} ✅

# Test 4: Datos
curl http://localhost:8000/api/v1/tier-list/current
# Debería retornar tier list con campeones ✅

# Test 5: Frontend
start outputs\meta-analyzer-dashboard.html
# Debería abrir dashboard en navegador ✅
```

---

## 🚨 ¿Algo no funciona?

### Error: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Error: "Database locked"
```bash
rm data/meta_analyzer.db
python setup_meta_analyzer.py --demo
```

### Error: "Connection refused" en dashboard
- Verifica que API esté corriendo en puerto 8000
- Abre http://localhost:8000/health en navegador

### Más problemas
→ Ver sección "Troubleshooting" en [META_ANALYZER_GUIA_COMPLETA.md](META_ANALYZER_GUIA_COMPLETA.md)

---

## 📋 CHECKLIST: Tu primer uso

- [ ] Leo [META_ANALYZER_GUIA_COMPLETA.md](META_ANALYZER_GUIA_COMPLETA.md) (15 min)
- [ ] Ejecuto `LEVANTAMIENTO_RAPIDO.bat` o `bash LEVANTAMIENTO_RAPIDO.sh` (30 seg)
- [ ] Abro http://localhost:8000/docs en navegador (explorar API)
- [ ] Abro dashboard (ver datos demo)
- [ ] Hago `curl http://localhost:8000/api/v1/tier-list/current` (entender respuestas)
- [ ] Revisión profunda opcional (ver otros documentos)

---

## 🎓 ¿Qué aprendí?

**Arquitectura de sistemas:**
- ✅ Layered architecture (DB → Logic → API → Frontend)
- ✅ RESTful API design
- ✅ Real-time data updates
- ✅ Frontend-backend integration

**Tecnologías:**
- ✅ SQLAlchemy ORM (SQLite)
- ✅ FastAPI framework
- ✅ JavaScript con Chart.js
- ✅ RESTful architecture

**League of Legends Meta:**
- ✅ Z-score analysis para detección
- ✅ Tier assignment logic
- ✅ Anomaly detection
- ✅ Champion stats aggregation

---

## 🎯 Próximos Pasos

### Fase 1 (Ya hecho ✅)
- BD + ORM
- API REST
- Frontend dashboard
- Data collection básica

### Fase 2 (Próximo)
- Real-time polling daemon
- Machine Learning predictions
- Database cleanup automático

### Fase 3 (Futuro)
- Discord notifications
- Slack integrations
- Mobile app
- Cloud deployment

---

## 📞 Resumen para no perderme

```
┌─────────────────────────────────────────────────┐
│  "Solo quiero levantar y ver qué funciona"      │
│  → LEVANTAMIENTO_RAPIDO.bat                     │
│  → Leer: META_ANALYZER_GUIA_COMPLETA.md         │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  "Quiero entender cómo funciona"                │
│  → META_ANALYZER_GUIA_COMPLETA.md (Completo)    │
│  → META_DETECTION_SYSTEM.md (Técnico)           │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  "Quiero profundizar en el análisis"            │
│  → META_DETECTION_PROFESSIONAL_ANALYSIS.md      │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  "Algo no funciona"                             │
│  → META_ANALYZER_GUIA_COMPLETA.md (Buscar FAQ)  │
│  → LEVANTAMIENTO_COMPLETO.md (Troubleshooting)  │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  "Quiero ver código"                            │
│  → src/riot_lol_cli/database/models.py          │
│  → src/riot_lol_cli/api_server.py               │
│  → src/riot_lol_cli/dashboard.py                │
└─────────────────────────────────────────────────┘
```

---

## ✨ Resumen Final

**Este proyecto es:**

✅ **Completo** - BD + API + Frontend + Setup  
✅ **Documentado** - Guía única + documentos opcionales  
✅ **Funcional** - Listo para producción  
✅ **Testeable** - Datos demo incluidos  
✅ **Extensible** - Diseño modular para Phase 2/3  

**¡Disfruta analizando el meta! 🚀**

---

**Última actualización:** 11 de enero de 2026  
**Versión:** 1.0.0 MVP ✅  
**Status:** Production Ready 🚀
