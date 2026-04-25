# 🎯 LOLCLI - Meta Analyzer ADC Tracker

## ⚡ Quick Start

```bash
# 1. Levantar API
python scripts/run_api.py

# 2. En navegador
http://localhost:8000/docs

# 3. Verificar ADCs
python scripts/verify_adc_tracker.py
```

---

## 📚 Documentación

**Comienza aquí (2 min):**  
→ [docs/adc_tracker/ADC_TRACKER_QUICK_START.md](docs/adc_tracker/ADC_TRACKER_QUICK_START.md)

**Sistema completo (20 min):**  
→ [docs/meta_analyzer/META_ANALYZER_GUIA_COMPLETA.md](docs/meta_analyzer/META_ANALYZER_GUIA_COMPLETA.md)

**Scripts disponibles (15 min):**  
→ [docs/GUIA_SCRIPTS_LEVANTAMIENTO.md](docs/GUIA_SCRIPTS_LEVANTAMIENTO.md)

**¿Cómo se reorganizó?**  
→ [docs/REORGANIZADO.md](docs/REORGANIZADO.md)

---

## 📊 Resumen

```
✅ 31 ADCs trackeados (Data Dragon + Yasuo)
✅ BD SQLite: data/meta_analyzer.db
✅ API FastAPI: http://localhost:8000
✅ Dashboard interactivo
✅ Documentación organizada en /docs
✅ Scripts en /scripts
✅ Proyecto limpio y escalable
```

---

## 🛠️ Estructura

```
docs/                  📚 Toda la documentación
├── adc_tracker/       ADC Tracker (4 guías)
├── meta_analyzer/     Meta Analyzer (7+ guías)
└── *.md              Guías generales

scripts/               🛠️ Scripts ejecutables
├── *.py              Python (3)
├── *.bat             Windows (1)
└── *.sh              Linux/Mac (2)

src/                  💻 Código fuente
data/                 📊 BD (31 ADCs)
outputs/              📤 Generados
```

---

## 🚀 ADCs Trackeados

**30 de Data Dragon + Yasuo = 31 total**

| Tier | ADCs |
|------|------|
| 🔥 S | Yasuo, Xayah, Vayne, Quinn, Varus |
| 💪 A | MissFortune, Twitch, Lucian, Jayce, Tristana |
| ... | +21 más |

Ver lista completa: [docs/adc_tracker/ADC_TRACKER_INFO.md](docs/adc_tracker/ADC_TRACKER_INFO.md)

---

## 📋 Carpetas de Documentación

### `/docs`
- Documentación general
- Guías de inicio
- Índices

### `/docs/adc_tracker`
- ADC_TRACKER_QUICK_START.md ⚡ Start
- ADC_TRACKER_INFO.md (Lista 31)
- ADC_TRACKER_SUMMARY.md (Técnico)
- ADC_TRACKER_COMPLETE.md (Completo)

### `/docs/meta_analyzer`
- META_ANALYZER_GUIA_COMPLETA.md
- META_DETECTION_SYSTEM.md
- META_DETECTION_PROFESSIONAL_ANALYSIS.md
- Y más...

---

## 🚀 Scripts en `/scripts`

| Script | Propósito |
|--------|-----------|
| `run_api.py` | Levanta API ⚡ |
| `verify_adc_tracker.py` | Verifica BD |
| `fetch_adc_champions.py` | Obtiene ADCs |
| `LEVANTAMIENTO_RAPIDO.bat` | Setup Windows |
| `LEVANTAMIENTO_RAPIDO.sh` | Setup Linux/Mac |

---

**¿Listo para empezar?** → [docs/adc_tracker/ADC_TRACKER_QUICK_START.md](docs/adc_tracker/ADC_TRACKER_QUICK_START.md)

**¿Quieres saber cómo se organizó?** → [docs/REORGANIZADO.md](docs/REORGANIZADO.md)
