# 🚀 GUÍA COMPLETA - Scripts y Levantamiento

**Tabla de Contenidos:**
1. [Todos los Scripts](#-todos-los-scripts)
2. [Cómo Levantar el Proyecto](#-cómo-levantar-el-proyecto)
3. [Cómo Manipular el Proyecto](#-cómo-manipular-el-proyecto)
4. [Troubleshooting](#-troubleshooting)

---

## 📋 Todos los Scripts

### 1️⃣ LEVANTAMIENTO_RAPIDO.bat (Windows)

**Qué hace:**
Levanta el proyecto completo en 4 pasos automáticos.

**Ubicación:** Raíz del proyecto

**Pasos que ejecuta:**
```
[1/4] Instala dependencias (pip install -r requirements.txt)
[2/4] Inicializa BD y carga datos demo (python setup_meta_analyzer.py --demo)
[3/4] Muestra información del sistema
[4/4] Pregunta si quieres levantar el API Backend
```

**Cómo ejecutar:**
```powershell
# Opción 1: Doble click en el archivo
LEVANTAMIENTO_RAPIDO.bat

# Opción 2: Línea de comandos
cd E:\Archivos de Drive\Desarrollos\LOLCLI
LEVANTAMIENTO_RAPIDO.bat
```

**Salida esperada:**
```
✅ Dependencias instaladas
✅ BD lista
📊 Base de datos: data\meta_analyzer.db
🎨 Frontend: outputs\meta-analyzer-dashboard.html
🚀 API Backend: http://localhost:8000
📚 Docs: http://localhost:8000/docs

¿Deseas levantar el API Backend? (Y/N)
```

**Duración:** ~30 segundos

---

### 2️⃣ LEVANTAMIENTO_RAPIDO.sh (Linux/Mac)

**Qué hace:**
Lo mismo que el .bat pero para sistemas Unix.

**Ubicación:** Raíz del proyecto

**Cómo ejecutar:**
```bash
# Necesitas permisos de ejecución (primera vez)
chmod +x LEVANTAMIENTO_RAPIDO.sh

# Ejecutar
bash LEVANTAMIENTO_RAPIDO.sh
# o
./LEVANTAMIENTO_RAPIDO.sh
```

**Diferencias con .bat:**
- Usa `python3` en lugar de `python`
- Rutas con `/` en lugar de `\`
- Lee respuesta con `read -r` en lugar de `choice`

---

### 3️⃣ setup_meta_analyzer.py

**Qué hace:**
Script principal que inicializa TODO (BD, datos, API, frontend).

**Ubicación:** Raíz del proyecto

**Cómo ejecutar:**

#### Con demostración:
```bash
python setup_meta_analyzer.py --demo
```
**Resultado:** Crea BD con 10 campeones, 80 stats horarios, 3 anomalías.

#### Sin demostración (BD vacía):
```bash
python setup_meta_analyzer.py
```
**Resultado:** Crea BD vacía lista para Riot API.

#### Verbose (ve todo lo que hace):
```bash
python setup_meta_analyzer.py --demo --verbose
```

**Salida esperada:**
```
============================================================
📊 INICIALIZANDO BASE DE DATOS
============================================================
✅ BD inicializada correctamente en: data/meta_analyzer.db

============================================================
📈 GENERANDO DATOS DE DEMO
============================================================
✅ 10 campeones insertados
✅ 80 stats horarios generados
✅ 3 anomalías detectadas
✅ Tier list creada

============================================================
🎨 GENERANDO FRONTEND
============================================================
✅ Dashboard generado en: outputs/meta-analyzer-dashboard.html

============================================================
📋 RESUMEN
============================================================
✅ BD: data/meta_analyzer.db
✅ Frontend: outputs/meta-analyzer-dashboard.html
✅ API: python -m uvicorn src.riot_lol_cli.api_server:app --reload
```

**Funciones principales:**
- `setup_database()` - Crea tablas
- `generate_demo_data()` - Inserta datos de demo
- `generate_frontend()` - Genera HTML dashboard
- `setup_requirements()` - Verifica dependencias
- `print_summary()` - Muestra resumen

---

### 4️⃣ ROADMAP_DOCUMENTACION.sh

**Qué hace:**
Muestra un mapa visual de cómo está organizada la documentación.

**Ubicación:** Raíz del proyecto

**Cómo ejecutar:**
```bash
bash ROADMAP_DOCUMENTACION.sh
```

**Salida esperada:**
```
╔═══════════════════════════════════════════════════════╗
║        DOCUMENTACIÓN META ANALYZER ROADMAP            ║
╚═══════════════════════════════════════════════════════╝

NIVEL 1: ⚡ ULTRA RÁPIDO (2 min)
┗ COMIENZA_AQUI.md

NIVEL 2: 📋 ORIENTACIÓN (5 min)
┗ INDICE_MAESTRO.md

NIVEL 3: 📘 COMPLETO (20 min)
┗ META_ANALYZER_GUIA_COMPLETA.md

NIVEL 4: 🎓 PROFUNDIDAD (30+ min)
┣ META_DETECTION_PROFESSIONAL_ANALYSIS.md
┣ META_DETECTION_SYSTEM.md
┣ LEVANTAMIENTO_COMPLETO.md
┗ ... (5 más)
```

---

### 5️⃣ Otros Scripts (Anteriores - No usar ahora)

| Script | Propósito | Estado |
|--------|-----------|--------|
| `fetch_matches.bat` | Descargar matches de Riot API | ⚠️ Anterior |
| `download_splash_arts.bat` | Descargar splash arts | ⚠️ Anterior |
| `regenerar_html.bat` | Regenerar viewer HTML | ⚠️ Anterior |
| `regenerar_splash_viewer.bat` | Regenerar splash viewer | ⚠️ Anterior |

**Nota:** Estos scripts son del proyecto anterior. NO necesitas ejecutarlos para Meta Analyzer.

---

## 🚀 Cómo Levantar el Proyecto

### Opción 1: Automática (RECOMENDADO - 30 seg)

**Windows:**
```powershell
# Doble-click o
LEVANTAMIENTO_RAPIDO.bat
```

**Linux/Mac:**
```bash
bash LEVANTAMIENTO_RAPIDO.sh
```

**Resultado:** Proyecto completamente listo en 30 segundos.

---

### Opción 2: Semi-Manual (Paso a paso)

**Windows:**
```powershell
# 1. Activar venv (si no está activo)
.\.venv\Scripts\Activate.ps1

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Setup BD + demo
python setup_meta_analyzer.py --demo

# 4. Levantar API
python -m uvicorn src.riot_lol_cli.api_server:app --reload

# En otra terminal:
# 5. Abrir dashboard
start outputs\meta-analyzer-dashboard.html
```

**Linux/Mac:**
```bash
# 1. Activar venv (si no está activo)
source venv/bin/activate  # o .venv/bin/activate

# 2. Instalar dependencias
pip3 install -r requirements.txt

# 3. Setup BD + demo
python3 setup_meta_analyzer.py --demo

# 4. Levantar API
python3 -m uvicorn src.riot_lol_cli.api_server:app --reload

# En otra terminal:
# 5. Abrir dashboard
open outputs/meta-analyzer-dashboard.html
```

---

### Opción 3: Completamente Manual

**Paso 1: Crear BD**
```python
from src.riot_lol_cli.database.models import DatabaseManager

db = DatabaseManager("data/meta_analyzer.db")
db.init_db()
print("✅ BD creada")
```

**Paso 2: Insertar datos (desde Riot API)**
```python
from src.riot_lol_cli.meta_analyzer.data_collector_db import MetaDataCollectorDB

collector = MetaDataCollectorDB(riot_api_key="RGAPI-xxxxx")
collector.collect_matches_batch(limit=100)
```

**Paso 3: Levantar API**
```bash
# Método 1: Usar el wrapper (RECOMENDADO)
python run_api.py

# Método 2: Uvicorn directo (requiere estar en carpeta raíz)
python -m uvicorn src.riot_lol_cli.api_server:app --reload --port 8000
```

**Paso 4: Abrir Frontend**
```bash
# Generar primero
from src.riot_lol_cli.dashboard import save_dashboard
save_dashboard("outputs/dashboard.html")

# Luego abrir en navegador
start outputs/dashboard.html
```

---

## 🎮 Cómo Manipular el Proyecto

### 1️⃣ Conectar tu API Key de Riot

**Archivo:** `src/riot_lol_cli/meta_analyzer/data_collector_db.py`

**Actual (dummy):**
```python
collector = MetaDataCollectorDB(riot_api_key="RGAPI-xxxxx")
```

**Para usar (reemplazar):**
```python
collector = MetaDataCollectorDB(riot_api_key="RGAPI-tu-clave-aqui")
collector.collect_matches_batch(limit=1000)  # Descargar 1000 matches
```

---

### 2️⃣ Cambiar Puerto API

**Actual (puerto 8000):**
```bash
python -m uvicorn src.riot_lol_cli.api_server:app --reload
```

**Para cambiar a puerto 5000:**
```bash
python -m uvicorn src.riot_lol_cli.api_server:app --reload --port 5000
```

**Luego actualizar:**
- Dashboard: Cambiar URLs de `localhost:8000` a `localhost:5000`
- Swagger: Ir a `http://localhost:5000/docs`

---

### 3️⃣ Cambiar Ubicación BD

**Actual:** `data/meta_analyzer.db`

**Opción 1: Cambiar en setup**
```bash
python setup_meta_analyzer.py --db-path "ruta/a/mi/db.db" --demo
```

**Opción 2: Cambiar en código**
```python
# En api_server.py
db = DatabaseManager("nueva/ruta/bd.db")

# En setup_meta_analyzer.py
setup_database("nueva/ruta/bd.db")
```

---

### 4️⃣ Agregar Más Datos Demo

**Archivo:** `setup_meta_analyzer.py`

**Ubicar:** Función `generate_demo_data()`

**Ejemplo - Agregar campeón:**
```python
# Línea ~60 (busca "Campeones demo")
champions = [
    {"name": "Ekko", "wr": 52.5, "pr": 8.2},
    {"name": "Zed", "wr": 51.2, "pr": 7.5},
    # AGREGAR AQUÍ:
    {"name": "MiCampeon", "wr": 50.0, "pr": 6.0},
]
```

**Luego ejecutar:**
```bash
python setup_meta_analyzer.py --demo
```

---

### 5️⃣ Limpiar BD Existente

**Para empezar de nuevo (elimina todo):**

**Windows:**
```powershell
# Opción 1: Manual
del data\meta_analyzer.db
python setup_meta_analyzer.py --demo

# Opción 2: Automático
python setup_meta_analyzer.py --fresh --demo
```

**Linux/Mac:**
```bash
# Opción 1: Manual
rm data/meta_analyzer.db
python3 setup_meta_analyzer.py --demo

# Opción 2: Automático
python3 setup_meta_analyzer.py --fresh --demo
```

---

### 6️⃣ Regenerar Dashboard

**Si modificaste el HTML o quieres actualizar:**

```python
from src.riot_lol_cli.dashboard import save_dashboard

save_dashboard("outputs/meta-analyzer-dashboard.html")
print("✅ Dashboard regenerado")
```

**O por terminal:**
```bash
python setup_meta_analyzer.py --generate-frontend-only
```

---

### 7️⃣ Testear Endpoints API

**Verificar que API está funcionando:**

```bash
# Ver estado del servidor
curl http://localhost:8000/health

# Ver tier list actual
curl http://localhost:8000/api/v1/tier-list/current

# Ver anomalías detectadas
curl http://localhost:8000/api/v1/anomalies/high-confidence

# Ver documentación interactiva
# Abrir en navegador: http://localhost:8000/docs
```

**Con Python:**
```python
import requests

# Tier list
response = requests.get("http://localhost:8000/api/v1/tier-list/current")
print(response.json())

# Anomalías
response = requests.get("http://localhost:8000/api/v1/anomalies/high-confidence")
print(response.json())
```

---

### 8️⃣ Ver Logs y Errores

**Terminal (durante ejecución):**
```
[2026-01-11 14:23:45] INFO: API iniciada
[2026-01-11 14:23:46] INFO: BD conectada
[2026-01-11 14:23:47] GET /api/v1/tier-list/current - 200 OK
```

**Si hay error:**
```
[2026-01-11 14:24:00] ERROR: No se puede conectar a BD
[2026-01-11 14:24:00] ERROR: FileNotFoundError: data/meta_analyzer.db
```

**Solución:**
```bash
python setup_meta_analyzer.py --demo
```

---

### 9️⃣ Integrar con tu Código

**Importar models:**
```python
from src.riot_lol_cli.database.models import DatabaseManager, ChampionHourly

db = DatabaseManager()
stats = db.get_latest_stats(limit=10)
print(stats)
```

**Importar data collector:**
```python
from src.riot_lol_cli.meta_analyzer.data_collector_db import MetaDataCollectorDB

collector = MetaDataCollectorDB(riot_api_key="RGAPI-xxxxx")
stats = collector.get_hourly_stats()
print(stats)
```

**Usar API con Python:**
```python
import requests

api_url = "http://localhost:8000/api/v1"

# Obtener tier list
tier_list = requests.get(f"{api_url}/tier-list/current").json()

# Obtener anomalías
anomalies = requests.get(f"{api_url}/anomalies/high-confidence").json()

# Procesar datos
print(f"Top 5 campeones: {tier_list['tiers']['S'][:5]}")
```

---

## 🔧 Troubleshooting

### ❌ Problema: "No se puede encontrar python"

**Causa:** Python no está en PATH

**Solución:**
```powershell
# Usar python completo
C:\Users\TuUsuario\AppData\Local\Programs\Python\Python311\python.exe setup_meta_analyzer.py --demo

# O activar venv
.\.venv\Scripts\Activate.ps1
python setup_meta_analyzer.py --demo
```

---

### ❌ Problema: "ModuleNotFoundError: No module named 'fastapi'"

**Causa:** Dependencias no instaladas

**Solución:**
```bash
pip install -r requirements.txt
```

---

### ❌ Problema: "Address already in use :8000"

**Causa:** Puerto 8000 ya está siendo usado

**Solución 1 - Cambiar puerto:**
```bash
python -m uvicorn src.riot_lol_cli.api_server:app --port 8001
```

**Solución 2 - Matar proceso anterior:**

**Windows:**
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
lsof -i :8000
kill -9 <PID>
```

---

### ❌ Problema: "BD locked" o "database is locked"

**Causa:** Otra instancia está usando la BD

**Solución:**
```bash
# Cerrar todas las instancias del API
# Eliminar la BD
del data\meta_analyzer.db

# Recrear
python setup_meta_analyzer.py --demo
```

---

### ❌ Problema: "Dashboard abre pero no muestra datos"

**Causa:** API no está corriendo

**Solución:**
```bash
# Terminal 1: Levantar API
python -m uvicorn src.riot_lol_cli.api_server:app --reload

# Terminal 2: Abrir dashboard
start outputs\meta-analyzer-dashboard.html
```

---

### ❌ Problema: "archivo .bat / .sh no ejecuta"

**Windows (.bat no funciona):**
```powershell
# Ejecutar directamente
powershell -ExecutionPolicy Bypass -File .\LEVANTAMIENTO_RAPIDO.bat
# O
python setup_meta_analyzer.py --demo
```

**Linux/Mac (.sh no funciona):**
```bash
# Dar permisos
chmod +x LEVANTAMIENTO_RAPIDO.sh

# Ejecutar
bash LEVANTAMIENTO_RAPIDO.sh
# O
python3 setup_meta_analyzer.py --demo
```

---

## 📊 Resumen de Scripts

| Script | Plataforma | Qué hace | Uso |
|--------|------------|----------|-----|
| `LEVANTAMIENTO_RAPIDO.bat` | Windows | Setup completo + pregunta API | Recomendado |
| `LEVANTAMIENTO_RAPIDO.sh` | Linux/Mac | Setup completo + pregunta API | Recomendado |
| `setup_meta_analyzer.py` | Todos | Setup manual controlable | Avanzado |
| `ROADMAP_DOCUMENTACION.sh` | Linux/Mac | Muestra mapa docs | Referencia |

---

## ✅ Checklist Rápido

- [ ] Ejecuté `LEVANTAMIENTO_RAPIDO.bat` (Windows) o `bash LEVANTAMIENTO_RAPIDO.sh` (Linux/Mac)
- [ ] Ver ✅ en todos los pasos
- [ ] Abrí `outputs/meta-analyzer-dashboard.html` en navegador
- [ ] Abrí `http://localhost:8000/docs` y vi Swagger UI
- [ ] Probé endpoint GET `/api/v1/tier-list/current`
- [ ] Vi datos demo cargados en dashboard

---

## 🎊 ¿Listo?

1. **Ejecuta:** `LEVANTAMIENTO_RAPIDO.bat` o `bash LEVANTAMIENTO_RAPIDO.sh`
2. **Lee:** [META_ANALYZER_GUIA_COMPLETA.md](META_ANALYZER_GUIA_COMPLETA.md)
3. **Explora:** http://localhost:8000/docs
4. **Disfruta:** El sistema está funcionando 🚀

---

**Última actualización:** 11 de enero de 2026  
**Versión:** 1.0.0
