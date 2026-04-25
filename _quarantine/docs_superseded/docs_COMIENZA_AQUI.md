# ⚡ COMIENZA AQUÍ (30 segundos)

**¿Solo quieres que funcione? Haz esto:**

## Opción 1: Windows (Recomendado)
```bash
LEVANTAMIENTO_RAPIDO.bat
```

## Opción 2: Linux/Mac
```bash
bash LEVANTAMIENTO_RAPIDO.sh
```

## Opción 3: Manual
```bash
pip install -r requirements.txt
python setup_meta_analyzer.py --demo
python -m uvicorn src.riot_lol_cli.api_server:app --reload
start outputs\meta-analyzer-dashboard.html
```

---

## ✅ Verificación

Cuando termines, deberías tener:

1. **API corriendo:** http://localhost:8000/docs
2. **Dashboard abierto:** Tabla tier list + anomalías
3. **Datos demo:** 10 campeones, 3 anomalías

---

## 🎓 Ahora lee esto

**[INDICE_MAESTRO.md](INDICE_MAESTRO.md)** - Orientarte en el proyecto  
**[META_ANALYZER_GUIA_COMPLETA.md](META_ANALYZER_GUIA_COMPLETA.md)** - Documentación completa (ÚNICA que necesitas)

---

**¡Disfruta! 🚀**
