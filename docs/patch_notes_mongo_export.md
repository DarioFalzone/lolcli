# Patch Notes -> MongoDB Atlas export

Guia paso a paso para sincronizar la data del subsistema `patch_notes` a un
cluster **MongoDB Atlas free tier** y explorarla desde **MongoDB Compass**.

## Que hace

Export idempotente (manual o cron) que toma los JSON de `data/patch_notes/`
y los upserta en 3 colecciones de MongoDB:

| Coleccion | Doc count tipico | `_id` |
|---|---|---|
| `patches` | ~16 (1 por patch_version + locale) | `"{patch_version}__{locale}"` (ej: `"26.10__es-es"`) |
| `enrichments` | ~80 (per-patch + globales) | `"{source}__{patch_version|GLOBAL}"` |
| `manifest` | 1 (singleton) | `"current"` |

Los JSON locales siguen siendo la **fuente de verdad**. MongoDB es solo
**read-only desde Compass**: no hay endpoint FastAPI que lo lea de vuelta.

## Setup (primera vez)

### 1. Crear cuenta MongoDB Atlas

1. Ir a https://www.mongodb.com/cloud/atlas/register
2. Registrarse con Google o email.
3. Skip onboarding ("I'll do this later").

### 2. Crear cluster free (M0)

1. **Build a Database** -> **M0 Free**.
2. Provider: **AWS**.
3. Region: la mas cercana (Sao Paulo `sa-east-1` para Argentina, o N. Virginia
   `us-east-1` como fallback global).
4. Cluster name: `lolcli`.
5. Crear. Tarda ~3 minutos.

### 3. Crear usuario de base de datos

1. Security -> **Database Access** -> **Add New Database User**.
2. Authentication Method: **Password**.
3. Username: `lolcli_writer`.
4. Password: clickear **Autogenerate Secure Password** -> **Copy** (la
   necesitas en el paso 5).
5. Built-in Role: **Read and write to any database**.
6. **Add User**.

### 4. Permitir tu IP

1. Security -> **Network Access** -> **Add IP Address**.
2. Click **Add Current IP Address**. Atlas detecta tu IP publica.
3. (Opcional, si tu IP cambia seguido) **Allow Access From Anywhere**
   (`0.0.0.0/0`). Sigue protegido por user+password.
4. **Confirm**.

### 5. Obtener connection string

1. **Database** -> tu cluster `lolcli` -> **Connect**.
2. **Drivers** -> **Python** -> version `3.12 or later`.
3. Copiar el string que empieza con `mongodb+srv://lolcli_writer:<password>@...`.
4. Reemplazar `<password>` por la contrasena del paso 3.

### 6. Configurar env vars (PowerShell)

```powershell
# Sesion actual (no persiste al cerrar la terminal)
$env:LOLCLI_MONGO_URI = "mongodb+srv://lolcli_writer:TU_PASS@lolcli.xxxxx.mongodb.net/?retryWrites=true&w=majority"
$env:LOLCLI_MONGO_DB  = "lolcli_patch_notes"
```

Para que persistan en todas las sesiones nuevas, usar `setx`:

```powershell
setx LOLCLI_MONGO_URI "mongodb+srv://lolcli_writer:TU_PASS@lolcli.xxxxx.mongodb.net/?retryWrites=true&w=majority"
setx LOLCLI_MONGO_DB "lolcli_patch_notes"
```

Despues de `setx`, **cerrar y reabrir la terminal** (las env vars solo
aplican a procesos nuevos). Comillas dobles obligatorias: la URI tiene `&` y
PowerShell sin comillas lo interpreta como operador.

### 7. Instalar el driver

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Esto instala `pymongo>=4.6,<5` (queda como dependencia opcional: el resto
del repo no la necesita).

### 8. Verificar con dry-run

```powershell
.venv\Scripts\python.exe scripts/export_patch_notes_to_mongo.py --dry-run
```

Salida esperada (sin tocar Atlas):

```
Dry-run summary: {
  "started_at": "2026-05-15T...",
  "patches": {"collected": 16},
  "enrichments": {"collected": ~80},
  "manifest": {"collected": 1},
  "mode": "dry-run",
  "duration_s": 0.X
}
```

### 9. Export real

```powershell
.venv\Scripts\python.exe scripts/export_patch_notes_to_mongo.py
```

Espera ~10-30 segundos. Salida esperada:

```
Conectando a MongoDB Atlas (db=lolcli_patch_notes)...
patches: {'scanned': 16, 'upserted': 16, 'modified': 0}
enrichments: {'scanned': ~80, 'upserted': ~80, 'modified': 0}
manifest: {'scanned': 1, 'upserted': 1, 'modified': 0}
Export summary: {... "mode": "live", "duration_s": 12.5}
```

Re-ejecutar es seguro e idempotente: la segunda corrida muestra
`upserted: 0, modified: 0` salvo que el `content_hash` haya cambiado.

### 10. Conectar Compass

1. Descargar e instalar MongoDB Compass desde https://www.mongodb.com/products/compass.
2. Abrir Compass -> **New Connection**.
3. Pegar la misma URI del paso 5.
4. **Save & Connect**.
5. En el panel izquierdo: expandir DB `lolcli_patch_notes` -> ves 3 colecciones.

## Flags del script

```
--dry-run                            No conecta a Mongo. Solo cuenta docs.
--only patches|enrichments|manifest  Procesa solo una coleccion.
--verbose                            Log nivel DEBUG.
```

## Cron opcional

Para que el export corra automaticamente despues del scrape diario (12:00 UTC),
agregar al server de patch_notes:

```powershell
setx LOLCLI_PATCH_NOTES_CRON_ENABLED 1     # ya existia, habilita scrape diario
setx LOLCLI_MONGO_EXPORT_CRON_ENABLED 1    # nuevo: habilita export tras scrape
# Reabrir terminal, luego:
.venv\Scripts\python.exe -m riot_lol_cli.patch_notes.server
```

El export corre a las **12:30 UTC** (30 min despues del scrape diario).
Si falla, **no bloquea** el flujo de scraping principal (try/except aislado).

## Queries de ejemplo en Compass

### Listar todos los patches ordenados desc

- Coleccion: `patches`
- Filter: `{}`
- Sort: `{ "patch_version": -1 }`

### Patches donde se nerfeo/buffeo a un champion

- Coleccion: `patches`
- Filter: `{ "champions_mentioned": "Aatrox" }`

### Estado del breakdown de Mobalytics

- Coleccion: `enrichments`
- Filter: `{ "source": "mobalytics_breakdown" }`

### Snapshot global de Data Dragon

- Coleccion: `enrichments`
- Filter: `{ "_id": "ddragon__GLOBAL" }`

### Manifest crudo (sources_status, available_patches)

- Coleccion: `manifest`
- Filter: `{}`

## Indexes creados

El script crea automaticamente (idempotente):

- `patches`: `patch_version` desc, `source_locale`, `content_hash`, `champions_mentioned`, `published_at` desc.
- `enrichments`: `(source, patch_version_indexed)` compound, `content_hash`.
- `manifest`: ninguno extra (singleton).

## Troubleshooting

| Sintoma | Causa | Fix |
|---|---|---|
| Exit 2 "LOLCLI_MONGO_URI no esta configurada" | Env var vacia | `setx LOLCLI_MONGO_URI "..."` + reabrir terminal |
| Exit 3 "pymongo no esta instalado" | Falta el driver | `pip install -r requirements.txt` |
| Exit 4 "Conexion a MongoDB fallo" | IP no whitelist o cluster pausado | Atlas -> Network Access; o reactivar cluster M0 (free se pausa tras 60 dias sin uso) |
| Compass no muestra la DB | Export no corrio aun, o connecto a otro cluster | Validar URI en Compass coincide con la del export |
| `ServerSelectionTimeoutError` | Firewall corporativo bloqueando MongoDB Atlas | Probar desde otra red o whitelist `*.mongodb.net` (puerto 27017+443) |

## Que NO hace

- No borra docs en Mongo si los borraste localmente (el upsert solo agrega/actualiza).
- No reemplaza el flujo de scraping: el server FastAPI sigue sirviendo desde JSON.
- No hace queries desde codigo: si en el futuro queres queriar Mongo desde lolcli,
  hay que agregar un `MongoLoader`. Hoy es read-only desde Compass.

## Referencias

- `scripts/export_patch_notes_to_mongo.py` - implementacion.
- `src/riot_lol_cli/patch_notes/scheduler.py` - cron opcional.
- `tests/test_export_patch_notes_to_mongo.py` - tests del builder.
- Plan original: ver `bitacora_de_cambios.md` entrada del 2026-05-15.
