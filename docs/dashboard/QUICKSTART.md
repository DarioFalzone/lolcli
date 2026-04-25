# ⚡ Quick Start - Dashboard Mejorado

## 5 Minutos para tener todo corriendo

### Paso 1: Generar el Dashboard (1 min)
```bash
python generate_dashboard.py
```
✅ Genera el HTML con toda la interfaz

### Paso 2: Inicializar Base de Datos (1 min)
```bash
python setup_meta_analyzer.py
```
✅ Crea DB, carga 31 ADCs, genera demo data

### Paso 3: Iniciar API Server (< 1 min)
```bash
python run_api.py
```
✅ Levanta FastAPI en http://localhost:8000

### Paso 4: Abrir Dashboard (< 1 min)
Opción A - Local:
```
file:///E:/Archivos de Drive/Desarrollos/LOLCLI/outputs/meta-analyzer-dashboard-enhanced.html
```

Opción B - Desde API:
```
http://localhost:8000/dashboard-enhanced
```

### Paso 5: ¡Explora! (2+ min)
1. 📊 **Dashboard** - Ve Tier List de ADCs
2. ⚡ **Matchups** - Selecciona un campeón, ve matchups
3. 🛡️ **Items** - Analiza builds por campeón
4. 📋 **Raw Data** - Descarga datos completos

---

## 🎯 Comandos Rápidos

### Generar todo de una vez
```bash
python setup_meta_analyzer.py && python generate_dashboard.py && python run_api.py
```

### Solo regenerar dashboard (sin resetear DB)
```bash
python generate_dashboard.py
```

### Ver estado del sistema
```bash
curl http://localhost:8000/
```

### Listar ADCs trackeados
```bash
curl http://localhost:8000/api/v1/champions/list
```

### Ver Tier List actual
```bash
curl http://localhost:8000/api/v1/tier-list/current
```

### Obtener matchups de Corki
```bash
curl "http://localhost:8000/api/v1/champions/Corki/matchups?limit=50&hours=24"
```

### Obtener items de MissFortune
```bash
curl "http://localhost:8000/api/v1/champions/MissFortune/items?limit=10"
```

### Obtener detalles de Yasuo
```bash
curl http://localhost:8000/api/v1/champions/Yasuo/details
```

---

## 💡 Casos de Uso Comunes

### Caso 1: "¿Qué ADC está OP ahora?"
1. Abre Dashboard → Tier List
2. Revisa Tier S
3. Click en campeón para detalles
4. ✅ Sabes si tiene anomalía

### Caso 2: "¿Cómo va Corki contra Kalista?"
1. Tab Matchups
2. Selecciona "Corki"
3. Ordena por "Campeón Rival"
4. Busca "Kalista"
5. ✅ Ver WR, tendencia, matches

### Caso 3: "¿Qué items compra MissFortune?"
1. Tab Items
2. Selecciona "MissFortune"
3. Aumenta "Top Items" a 15
4. ✅ Ver build path recomendada

### Caso 4: "Necesito todos los datos de Yasuo"
1. Tab Raw Data
2. Filtro: "Yasuo"
3. Limita a 100-500 registros
4. ✅ Descarga para análisis externo

---

## 🔧 Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| "Dashboard no encontrado" | `python generate_dashboard.py` |
| "Desconectado" (header) | `python run_api.py` |
| "Sin datos" en Matchups | Selecciona un campeón en el dropdown |
| Modal no abre | Prueba F5 (refresh) |
| Data antigüa | `python setup_meta_analyzer.py` (resetea DB) |

---

## 📊 Dashboard Tabs Explicados

### 📊 Dashboard
**Qué ves:**
- Tier List actual (S/A/B/C/D)
- Winrate y Pickrate de cada ADC
- 31 ADCs totales

**Por qué:** Overview rápido del meta

### ⚡ Matchups
**Qué ves:**
- Historial de enfrentamientos
- Winrate por matchup
- Tendencia (UP/DOWN)

**Por qué:** Predecir resultados

### 🛡️ Items
**Qué ves:**
- Items más usados
- Frecuencia de compra
- Build path recomendado

**Por qué:** Copiar builds meta

### 📋 Raw Data
**Qué ves:**
- Datos sin procesar
- Todas las métricas
- Source attribution

**Por qué:** Análisis avanzado

---

## ℹ️ Información de Data

- **Campeones:** 31 ADCs (Data Dragon + Yasuo)
- **Fuente:** Riot Games Data Dragon API
- **Demo Data:** 248 registros (8 por campeón)
- **Actualización:** Automática cada 24h
- **Base de Datos:** SQLite (`data/meta_analyzer.db`)

---

## 🌐 URLs Importantes

| URL | Descripción |
|-----|-------------|
| `http://localhost:8000/` | API Root |
| `http://localhost:8000/docs` | Swagger API Docs |
| `http://localhost:8000/dashboard` | Dashboard Original |
| `http://localhost:8000/dashboard-enhanced` | Dashboard Mejorado ⭐ |

---

## ✅ Checklist de Verificación

- [ ] ✅ Python 3.8+ instalado
- [ ] ✅ `pip install -r requirements.txt`
- [ ] ✅ BD existe (`data/meta_analyzer.db`)
- [ ] ✅ API corre en puerto 8000
- [ ] ✅ Dashboard HTML generado
- [ ] ✅ Navegador abierto en localhost
- [ ] ✅ Datos cargan en 5 segundos
- [ ] ✅ Puedo hacer click en campeones

---

**¿Problemas? Revisa:** `/docs/TROUBLESHOOTING.md`  
**¿Más detalles?** Consulta: `/docs/dashboard/DASHBOARD_ENHANCED.md`
