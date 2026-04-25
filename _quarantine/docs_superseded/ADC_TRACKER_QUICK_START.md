# 🎯 GUÍA RÁPIDA - ADC TRACKER

**Leer esto primero:** 2 minutos ⚡

---

## ⚡ Quick Start

### 1. Levantar API (Terminal 1)
```bash
python run_api.py
```

**Verás:**
```
🚀 Levantando API en http://localhost:8000
📚 Documentación en http://localhost:8000/docs
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Abrir Dashboard (Navegador)
```
http://localhost:8000/docs
```

O abrir archivo:
```
E:\Archivos de Drive\Desarrollos\LOLCLI\outputs\meta-analyzer-dashboard.html
```

### 3. Verificar ADCs (Terminal 2)
```bash
python verify_adc_tracker.py
```

**Verás:**
```
Total: 31 ADCs
 1. Akshan ✅
 2. Aphelios ✅
 ...
31. Zeri ✅
```

---

## 📊 Entender los Datos

### Tier List
```
Abierto: http://localhost:8000/api/v1/tier-list/current

Respuesta:
{
  "timestamp": "2026-01-11T22:00:00",
  "tiers": {
    "S": ["Yasuo", "Xayah", "Vayne"],
    "A": ["Quinn", "Varus", "MissFortune"],
    ...
  }
}
```

### Winrate por ADC
```
Abierto: http://localhost:8000/api/v1/stats/latest?limit=31

Respuesta:
[
  {
    "champion": "Yasuo",
    "winrate": 65.3,
    "pickrate": 12.7,
    "banrate": 6.4,
    "matches": 148,
    "trend": "RISING"
  },
  ...
]
```

### Anomalías Detectadas
```
Abierto: http://localhost:8000/api/v1/anomalies/high-confidence

Respuesta:
[
  {
    "champion": "Akshan",
    "anomaly_type": "WINRATE_SPIKE",
    "confidence": 0.92,
    "change_pct": 2.5,
    "description": "..."
  },
  ...
]
```

---

## 🎮 Interpretación Meta

### Verde (Tier S) - Fuerte
- **Yasuo** 65.3% WR → Nerfs próximos probables
- **Xayah** 63.9% WR → Meta ADC del momento
- **Vayne** 62.6% WR → Jugar para ganar

### Amarillo (Tier A) - Estable
- **Quinn** 62.0% WR → Buena opción
- **Varus** 61.3% WR → Segura

### Rojo (Tier B/C/D) - Débil
- Debajo de 50% WR → Evitar o especialista
- Especialmente si baja < 46% WR

---

## 🔧 Modificar Sistema

### Cambiar Puerto API
```python
# En run_api.py
uvicorn.run(app, port=5001)  # En lugar de 8000
```

### Agregar más ADCs
```python
# En adc_champions.json
"adcs_with_yasuo": [
  ...,
  "MiCampeon"  # Agregar aquí
]
```

Luego:
```bash
python setup_meta_analyzer.py --demo
```

### Regenerar BD Limpia
```bash
del data\meta_analyzer.db
python setup_meta_analyzer.py --demo
```

---

## 📈 Métricas Importantes

### Winrate (WR)
- **> 55%:** Tier S (Overpowered)
- **51-55%:** Tier A (Strong)
- **48-51%:** Tier B (Balanced)
- **45-48%:** Tier C (Weak)
- **< 45%:** Tier D (Very weak)

### Pickrate (PR)
- **> 10%:** Muy jugado
- **5-10%:** Jugado
- **2-5%:** Poco jugado
- **< 2%:** Muy poco jugado

### Banrate
- Generalmente 0.5x Pickrate
- Si es muy alto = ADC fuerte

### Z-Score
- **> 2.0:** Cambio meta detectado (95% confianza)
- **1.5-2.0:** Cambio probable
- **< 1.5:** Normal

---

## 🎯 Casos de Uso

### Caso 1: "¿Qué ADC debo jugar?"
```
1. Abrir: http://localhost:8000/api/v1/tier-list/current
2. Ver Tier S
3. Jugar el que más te guste de ahí
```

### Caso 2: "¿Cambió el meta?"
```
1. Abrir: http://localhost:8000/api/v1/anomalies/high-confidence
2. Si hay anomalías = Meta cambió
3. Ver descripción para entender qué cambió
```

### Caso 3: "¿Mi ADC fue nerfed?"
```
1. Abrir: http://localhost:8000/api/v1/stats/latest?limit=31
2. Buscar tu ADC
3. Comparar WR con hace 24h (histórico próximamente)
```

### Caso 4: "¿Qué ADC contra X?"
```
Próximamente: Matchup analysis endpoint
```

---

## 📊 Ejemplo Real

**Escenario:** Quieres saber si Yasuo ADC está fuerte

```bash
# 1. Verificar tier
GET http://localhost:8000/api/v1/tier-list/current
→ Ves que Yasuo está en Tier S

# 2. Verificar WR exacta
GET http://localhost:8000/api/v1/stats/latest?limit=31
→ Yasuo: 65.3% WR (muy alta)

# 3. Ver si hay cambios meta
GET http://localhost:8000/api/v1/anomalies/high-confidence
→ No hay anomalía para Yasuo (WR es consistente)

# 4. Conclusión
Yasuo es fuerte ahora, juega sin miedo
```

---

## 🚨 Errores Comunes

### ❌ "API no responde"
```
Solución: Asegurate de ejecutar: python run_api.py
Verifica: http://localhost:8000/health
```

### ❌ "No hay datos en dashboard"
```
Solución: Regenera BD: python setup_meta_analyzer.py --demo
Verifica: python verify_adc_tracker.py
```

### ❌ "Puerto 8000 ya en uso"
```
Solución: Cambiar puerto en run_api.py
O matar proceso: lsof -i :8000 && kill -9 PID
```

### ❌ "Solo veo 10 ADCs"
```
Solución: Eliminar BD vieja: rm data/meta_analyzer.db
Regenerar: python setup_meta_analyzer.py --demo
Verificar: python verify_adc_tracker.py
```

---

## 📚 Documentación Completa

- **[ADC_TRACKER_INFO.md](ADC_TRACKER_INFO.md)** - Lista completa de ADCs
- **[ADC_TRACKER_SUMMARY.md](ADC_TRACKER_SUMMARY.md)** - Resumen técnico
- **[META_ANALYZER_GUIA_COMPLETA.md](META_ANALYZER_GUIA_COMPLETA.md)** - Sistema completo
- **[GUIA_SCRIPTS_LEVANTAMIENTO.md](GUIA_SCRIPTS_LEVANTAMIENTO.md)** - Scripts disponibles

---

## ✅ Checklist Rápido

- [ ] Ejecuté `python run_api.py`
- [ ] API está en http://localhost:8000
- [ ] Abrí Swagger en http://localhost:8000/docs
- [ ] Ejecuté `python verify_adc_tracker.py`
- [ ] Vi 31 ADCs en la lista
- [ ] Abrí dashboard en navegador
- [ ] Vi datos (tier lists, stats, gráficos)

Si todo está ✅ → **Sistema listo** 🚀

---

## 🎊 ¿Qué Puedes Hacer Ahora?

1. **Explorar meta actual** → Ver tier lists
2. **Monitorear cambios** → Ver anomalías
3. **Analizar ADCs** → Obtener estadísticas
4. **Conectar Riot API** → Recolectar datos reales
5. **Crear alertas** → Notificaciones automáticas

---

**¡Disfruta del ADC Tracker!** 🎯

Para preguntas, ver documentación completa: [META_ANALYZER_GUIA_COMPLETA.md](META_ANALYZER_GUIA_COMPLETA.md)
