# Dashboard — Meta Analyzer

Documento canonico del dashboard del Meta Analyzer. Consolida la guia rapida, la referencia visual, filtros/fuentes y el historial funcional del dashboard mejorado.

## Que es

El dashboard es la superficie visual del Meta Analyzer para estudiar ADCs: tier list, matchups, builds, datos crudos y anomalías. Puede servirse desde la API local o generarse como HTML standalone.

## Como levantar

```bash
# Setup inicial: BD + datos demo + dashboards
python scripts/setup_meta_analyzer.py

# API local en puerto 8000
python scripts/run_api.py

# Dashboard standalone
python scripts/generate_dashboard.py
```

URLs principales:

- API: `http://localhost:8000`
- Dashboard enhanced: `http://localhost:8000/dashboard-enhanced`
- Docs OpenAPI: `http://localhost:8000/docs`
- HTML generado: `outputs/meta-analyzer-dashboard-enhanced.html`

## Flujos

1. **Ver tier list actual:** abrir Dashboard tab, revisar tiers S/A/B/C/D, abrir detalle de campeon.
2. **Analizar matchups:** usar tab Matchups, filtrar por campeon, ventana horaria y limite.
3. **Estudiar builds:** usar tab Items, elegir campeon y revisar frecuencia/ruta de items.
4. **Inspeccionar datos crudos:** usar Raw Data para auditar registros, fuente y timestamps.

## Tabs y Capacidades

| Tab | Uso | Datos principales |
|-----|-----|-------------------|
| Dashboard | Tier list por campeon | WR, PR, partidas, tier, trend |
| Matchups | Rendimiento contra rivales | wins/losses, WR, tendencia, timestamp |
| Items | Construcciones frecuentes | item id, frecuencia, build path |
| Raw Data | Auditoria/export manual | registros sin filtrar y source attribution |

Interacciones esperadas:

- Click en campeon abre modal de detalle.
- Encabezados de tablas permiten ordenar.
- Filtros por campeon, horas y limite de registros.
- Source badges visibles para trazabilidad.

## Endpoints Consumidos

La API real vive en `src/riot_lol_cli/meta_api/routes/`.

```text
GET /dashboard-enhanced
GET /api/v1/tier-list/current
GET /api/v1/champions/{champion_name}/matchups
GET /api/v1/champions/{champion_name}/items
GET /api/v1/champions/{champion_name}/details
GET /api/v1/champions/all/raw-data
GET /api/v1/anomalies/high-confidence
GET /api/v1/dashboard/summary
```

## Fuentes y Filtros

- Cada registro debe mantener `source` y timestamp cuando aplique.
- Data Dragon se usa para assets/datos estaticos.
- Los filtros no deben ocultar la procedencia de los datos.
- Si una tabla queda vacia, mostrar estado vacio accionable en vez de spinner infinito.

## UX y Diseño

- Identidad Hextech dark: navy profundo, gold para jerarquia/acciones, cyan para informacion.
- Dashboard desktop-first, con soporte responsive basico.
- Modal de campeon debe exponer stats, anomalías y metadata de fuente.
- Evitar duplicar sistemas visuales; preferir tokens documentados en `docs/design-system.md`.

## Archivos Relevantes

| Archivo | Rol |
|---------|-----|
| `src/riot_lol_cli/dashboard.py` | Dashboard basico standalone |
| `src/riot_lol_cli/dashboard_enhanced.py` | Dashboard enhanced autocontenido |
| `src/riot_lol_cli/meta_api/routes/core.py` | Rutas `/dashboard` y `/dashboard-enhanced` |
| `src/riot_lol_cli/meta_api/routes/champions.py` | Matchups, items, details, raw-data |
| `src/riot_lol_cli/meta_api/routes/stats.py` | Stats, tier list, anomalías, summary |
| `scripts/generate_dashboard.py` | Genera HTML standalone |
| `scripts/setup_meta_analyzer.py` | Inicializa BD/demo/dashboard |

## Troubleshooting

- **Dashboard queda cargando:** confirmar que `python scripts/run_api.py` esta corriendo y que `data/meta_analyzer.db` existe.
- **Connection refused:** verificar puerto 8000 y que no haya otro proceso usando el puerto.
- **Datos vacios:** correr `python scripts/setup_meta_analyzer.py`.
- **Endpoints desactualizados en docs antiguas:** comparar contra `src/riot_lol_cli/meta_api/routes/`.

## Deuda Conocida

- `dashboard_enhanced.py` mantiene HTML/CSS/JS embebido en Python.
- Parte de la documentacion historica mencionaba rutas antiguas; este README refleja la capa `meta_api` actual.
- Los changelogs visuales antiguos fueron absorbidos en esta guia, `docs/README.md` y `bitacora_de_cambios.md`.
