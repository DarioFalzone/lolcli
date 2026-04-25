# 🎯 Meta Analyzer - Inicio Rápido

Detecta cambios en el meta de League of Legends desde **Día 1** (como u.gg, op.gg y mobalytics).

## 🚀 Levantamiento en 2 minutos

### Windows
```bash
LEVANTAMIENTO_RAPIDO.bat
```

### Linux/Mac
```bash
bash LEVANTAMIENTO_RAPIDO.sh
```

## 📊 Alternativa Manual

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Setup BD + datos demo
python setup_meta_analyzer.py --demo

# 3. Levantar API (Terminal 1)
python -m uvicorn src.riot_lol_cli.api_server:app --reload

# 4. Abrir Frontend (Terminal 2)
# Windows
start outputs\meta-analyzer-dashboard.html

# Mac
open outputs/meta-analyzer-dashboard.html

# Linux
xdg-open outputs/meta-analyzer-dashboard.html
```

## 🌐 URLs

- **Dashboard:** http://localhost:8000 (o archivo local)
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## 📚 Documentación

- **Setup Completo:** [LEVANTAMIENTO_COMPLETO.md](LEVANTAMIENTO_COMPLETO.md)
- **Resumen Visual:** [RESUMEN_VISUAL.md](RESUMEN_VISUAL.md)
- **Sistema Completo:** [SISTEMA_COMPLETO_LEVANTADO.md](SISTEMA_COMPLETO_LEVANTADO.md)
- **Checklist:** [CHECKLIST_VERIFICACION.md](CHECKLIST_VERIFICACION.md)

## 🎨 Características

✅ **Base de Datos** - SQLite con 7 tablas  
✅ **API REST** - 40+ endpoints FastAPI  
✅ **Dashboard** - HTML/JS interactivo  
✅ **Datos Demo** - 10 campeones listos para testing  
✅ **Setup Automático** - Instalación en un comando  

## 🔧 Requisitos

- Python 3.9+
- pip

## 📈 ¿Qué incluye?

```
✅ Recolección de datos (Riot API V5)
✅ Análisis estadístico (Z-scores)
✅ Detección de anomalías (7 tipos)
✅ Generación de tier lists (S/A/B/C/D)
✅ Dashboard interactivo
✅ API REST completa
```

## 🎯 Próximos Pasos

1. **Leer:** [LEVANTAMIENTO_COMPLETO.md](LEVANTAMIENTO_COMPLETO.md)
2. **Ejecutar:** Setup script
3. **Explorar:** Dashboard en navegador
4. **Integrar:** Tu API key (Riot)

---

**Versión:** 1.0.0 MVP ✅  
**Status:** Production Ready 🚀  
**Creado:** 11 de enero de 2026

¡Listo para usar! 🚀
