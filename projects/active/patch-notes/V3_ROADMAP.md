# Patch Notes V3 — Roadmap

Documento de planeamiento para la próxima iteración mayor del subsistema
`patch_notes`. Listo de próximas funcionalidades, agrupado por prioridad,
con problema que resuelve, alcance estimado y dependencias.

**Estado actual (V2.5)**: scraping multi-source con 7 fuentes, español-only,
search FTS, diff entre versiones, visual enrichment con champion + ability
icons desde Data Dragon, scroll-to-top transversal, version pill en hero,
APScheduler opt-in. Ver `bitacora_de_cambios.md` para detalle.

---

## Cómo leer este roadmap

Cada item tiene:

- **Problema**: qué pain point real resuelve.
- **Alcance**: estimación cualitativa (XS / S / M / L / XL).
- **Dependencias**: qué hace falta antes.
- **Risk**: qué puede salir mal o requerir investigación adicional.

Las prioridades son recomendaciones — el orden final lo decide el usuario.

---

## Prioridad 1 — Cierre del contract V2 (cosas pendientes documentadas)

Items que ya fueron mencionados en bitácora pero quedaron fuera del scope V2.x.
Son el complemento natural de lo construido.

### 1.1 Disclaimer legal de Riot en footer (`L:XS`)

- **Problema**: el `deep-research-report.md` indica que Riot exige el
  boilerplate legal visible si el producto sirve a jugadores. Estamos sirviendo
  contenido público pero la responsabilidad es del operador del frontend.
- **Alcance**: agregar un `<footer>` discreto al final de cada vista con el
  disclaimer estándar de fan-content de Riot. Es texto fijo, 1 archivo CSS
  + 1 fragmento HTML. **XS** (< 30 min).
- **Dependencias**: ninguna.
- **Risk**: bajo — solo es texto. Confirmar redacción actual del boilerplate
  con el [legal disclaimer oficial de Riot](https://www.riotgames.com/en/legal).
- **Trigger para hacerlo**: antes de publicar el server fuera de localhost.

### 1.2 Cron en producción con UI para log de runs (`L:M`)

- **Problema**: APScheduler ya está integrado y se activa con
  `LOLCLI_PATCH_NOTES_CRON_ENABLED=1`, pero no hay visibilidad de cuándo
  corrió ni qué resultado dio cada job. Hoy hay que leer logs del proceso.
- **Alcance**:
  - Persistir cada run en `data/patch_notes/runs/{timestamp}.json` con
    summary (sources OK / sources error / patches nuevos / tiempo total).
  - Nuevo endpoint `GET /api/v1/patch-notes/runs?limit=20`.
  - Nueva ruta SPA `#runs` con tabla cronológica + colores semánticos
    (success / partial / error).
  - Toggle "habilitar cron" desde la UI llamando a un endpoint que
    persiste el bit en `settings.json` local.
- **Dependencias**: el orchestrator ya tiene el `summary` que devuelve
  `run_full_scrape()` — solo hay que serializarlo a disco.
- **Risk**: medio — el toggle UI requiere reiniciar el server para que el
  scheduler se rearme; documentar bien.

### 1.3 Adapter resilience con `markdown.new` fallback (`L:M`)

- **Problema**: los 4 adapters comunitarios (`ugg_patch`, `opgg_patch`,
  `lolalytics_patch`, `mobalytics_patch`) dependen de selectores DOM
  específicos. Si U.GG o Mobalytics cambian markup, scrapeamos basura.
- **Alcance**:
  - Implementar capa de fallback: si el primer extract devuelve `rows_count == 0`
    o falla, reintentar pasando la URL por `markdown.new` (o un servicio
    análogo) que devuelve texto plano estructurado.
  - Parsear el markdown resultante con regex tolerante (versión + nombre
    de campeón + porcentajes).
  - Marcar el enrichment con `fallback_method: "markdown.new"` para
    auditoría.
- **Dependencias**: ninguna técnica. Requiere validar términos de uso de
  `markdown.new` antes de usarlo en producción.
- **Risk**: medio-alto — dependencia externa adicional. Considerar
  hospedar un fallback propio si `markdown.new` se vuelve crítico.

### 1.4 Data Dragon enrichment inline (`L:S`)

- **Problema**: V2.2 inyecta icons en headings (`H3 Aatrox`, `H4 Q -
  Habilidad`), pero el cuerpo de los párrafos sigue siendo texto plano.
  Una mención "Acumulaciones por matar a Garen" no muestra el icon de Garen.
- **Alcance**: extender `enrichChampionHeadings()` para escanear bloques
  de texto y reemplazar nombres canónicos por `<span class="inline-champ">
  <img src="..." />Nombre</span>`. Mismo champion index ya cargado.
- **Dependencias**: el champion index ya está cacheado en `state.championIndex`.
- **Risk**: bajo. Cuidar performance — usar `requestIdleCallback` para
  no bloquear el render principal.

---

## Prioridad 2 — Features visuales que aprovechan data ya scrapeada

Cosas que no necesitan nuevos adapters pero suben el valor percibido.

### 2.1 Item icons inline (`L:M`)

- **Problema**: el patch 26.10 menciona "Espada ciclovoltaica", "Toque de
  muerte ígnea", "Grebas codiciosas" — todos sin icon. Tenemos 705 iconos
  PNG locales en `assets/items/`.
- **Alcance**:
  - Cargar `data/items/database.json` (ya generado por Items Browser) al
    startup del frontend o lazy via API.
  - Indexar items por nombre normalizado.
  - Extender el patrón de visual enrichment para items (similar a champions).
  - Bonus: hover sobre el icon muestra tooltip con stats del item.
- **Dependencias**: el Items Browser ya tiene la database normalizada
  en `data/items/database.json`.
- **Risk**: bajo — assets ya están en disco.

### 2.2 Rune icons (`L:S`)

- **Problema**: las notas mencionan "Toque de muerte ígnea", "Tensión del
  saqueador de tormentas" — son runas, también con icons en Data Dragon.
- **Alcance**: extender champion index pattern para runas. Endpoint
  DDragon: `cdn/{version}/data/{lang}/runesReforged.json`.
- **Dependencias**: 2.1 (mismo enfoque).

### 2.3 Patch impact score (`L:S`)

- **Problema**: ningún parche es igual a otro. 26.4 fue un mid-season
  mayor; 26.5 fue un mini-patch. La UI los muestra idénticos.
- **Alcance**: derivar una métrica al server-side por patch:
  - `n_champions_changed`: contar H3 que matchean champion.
  - `n_items_changed`: similar para items.
  - `n_sections_total`: tamaño del documento.
  - `impact_score = clamp(0-100, weighted_sum)`.
- **Exponer** en `PatchNoteIndex.impact_score` (campo nuevo en schema).
- **UI**: barra de progreso color-coded en cada patch card.
- **Dependencias**: champion + item index (de 2.1).
- **Risk**: bajo — calculado desde data en disco, sin scraping.

### 2.4 Filtros en la vista diff (`L:S`)

- **Problema**: comparar 26.10 vs 26.5 devuelve cientos de diff sections.
  No hay forma de filtrar "solo nerfs a campeones" o "solo cambios de items".
- **Alcance**:
  - Chips en el hero de diff: `[Campeones] [Items] [Runas] [Modos] [Otros]`.
  - Click filtra `diff_sections` por título de la sección padre.
  - Bonus: chip "Solo nerfs" / "Solo buffs" usando regex sobre los blocks.
- **Dependencias**: ninguna. Es solo UI.
- **Risk**: bajo. Pulir UX para que el toggle sea claro.

---

## Prioridad 3 — Integración con otros subsistemas del repo

Aprovechar que somos parte de un paquete con `draft_advisor`, `jungle_meta`,
`items_browser`, etc.

### 3.1 Cross-link patch → draft_advisor (`L:M`)

- **Problema**: cuando el patch dice "Quinn se va a la jungla", el usuario
  querría saber si el Draft Advisor (`:8001`) ya la trata como jungler
  válida. Hoy son dos surfaces aisladas.
- **Alcance**:
  - Al renderizar un H3 con champion canónico, agregar al hover un
    pequeño botón "Ver en Draft Advisor →" linkeando a
    `http://localhost:8001/draft#/champion/{id}` (si el Draft Advisor
    expone deep-links, sino al overview).
  - Idem para Jungle Meta: "Ver en Jungle Tier →" → `:8003/#champion/{id}`.
- **Dependencias**: confirmar que los servers `:8001` y `:8003` exponen
  deep-links por champion. Si no, agregarlos primero.
- **Risk**: medio — requiere coordinación entre subsistemas. Mejor
  empezar como abrir en pestaña nueva sin asumir auth/state compartido.

### 3.2 Tier shift indicator (`L:M`)

- **Problema**: el meta_scraper ya guarda snapshots de tier list por parche
  en `data/meta_scraper/normalized/`. Tenemos data histórica de cómo cambió
  un champion entre 26.9 y 26.10, pero el patch detail no la muestra.
- **Alcance**:
  - Cargar `latest_*_tier.json` files antes y después del patch siendo
    visualizado.
  - Para cada champion en el H3, calcular `tier_shift` (S→A, A→B, etc.).
  - Mostrar arrow icon next to champion icon: ↑ buff, ↓ nerf, → sin
    cambio.
- **Dependencias**: meta_scraper debe tener al menos 2 snapshots
  consecutivos. Si solo tiene 1, no hay nada que comparar.
- **Risk**: medio. La nomenclatura de tiers no siempre matchea exacto entre
  fuentes (S+, S, S- vs S, A, A+).

### 3.3 Pro picks tracker (`L:L`)

- **Problema**: el patch dice "Quinn en jungla" y al día siguiente los
  pros ya están probándolo en SoloQ. ¿Quién picó qué post-patch?
- **Alcance**:
  - Reusar el sistema de Jungle Research (que ya scrapea SoloQ de pros
    en `src/riot_lol_cli/jungle_research/`).
  - Endpoint nuevo `/api/v1/patch-notes/{patch}/pro-picks` que filtra
    matches de pros con `game_creation > patch.published_at`.
  - UI: tab nuevo en detail "Pro picks", con lista de pros + champions
    + win/loss en los primeros 7 días post-patch.
- **Dependencias**: el sistema `jungle_research` ya tiene scrapers de pro
  matches. Hay que extender para filtrar por fecha de patch.
- **Risk**: alto — depende de la fiabilidad del scraping de Riot Pros.
  Quedó como pendiente en jungle_research V1.

---

## Prioridad 4 — Refinamientos visuales con Stitch

Aprovechar el `DESIGN.md` que creamos para generar nuevas pantallas con IA.

### 4.1 Mobile-first refinement (`L:M`)

- **Problema**: el subsistema está pensado desktop-first. Mobile funciona
  pero hay rozaduras: hero muy grande, cards muy anchas, TOC se vuelve
  scrollable raro.
- **Alcance**:
  - Pasar `DESIGN.md` + screenshots actuales a Stitch.
  - Pedir variantes mobile-first para overview y detail.
  - Implementar las mejores propuestas: hero compacto, bottom nav, TOC
    como accordion colapsable.
- **Dependencias**: acceso a Stitch + iteración manual.
- **Risk**: medio — Stitch puede proponer patrones que no se condicen
  con el design system. Filtrar con criterio.

### 4.2 "Patch summary" view (`L:M`)

- **Problema**: a veces el usuario quiere un TL;DR del patch, no leer
  3000 líneas. Reusar el `summary` que ya extraemos sí, pero también un
  resumen visual:
  - "X campeones modificados"
  - "Y items modificados"
  - "Z nuevas skins"
  - Top 3 cambios destacados (regla heurística).
- **Alcance**:
  - Nuevo endpoint `/api/v1/patch-notes/{patch}/summary` con conteos
    calculados al server-side.
  - Nueva ruta `#summary/{patch}` o tab dentro de detail.
  - Diseño visual via Stitch (input: DESIGN.md + screenshots).
- **Dependencias**: 2.1, 2.2, 2.3 (item/rune index + impact score).
- **Risk**: medio. La heurística "top 3 cambios destacados" puede ser
  arbitraria — empezar con criterios simples (más bloques, palabras
  "NUEVO"/"NOVEDAD" en mayúscula).

### 4.3 "What's new this week" digest (`L:M`)

- **Problema**: si el usuario abre el sitio una vez por semana, querría ver
  "qué pasó desde mi última visita". Hoy tiene que recordar qué patch leyó.
- **Alcance**:
  - Track de patches visitados en localStorage por hash de contenido.
  - Hero variant que dice "Hay 2 parches nuevos desde tu última visita".
  - Lista filtrada solo de los nuevos.
- **Dependencias**: ninguna técnica. Solo state local.
- **Risk**: bajo. UX delicada — no asumir que el usuario quiere
  "marcar como leído" automáticamente.

---

## Prioridad 5 — Infraestructura y observabilidad

Cosas que el usuario final no ve pero que importan para mantener el sistema.

### 5.1 Audit log de scrapes (`L:S`)

- **Problema**: hoy `sources_status` solo guarda `last_scrape` y
  `last_error`. No hay historial.
- **Alcance**:
  - Append-only log en `data/patch_notes/audit.jsonl` con cada operación
    (`scrape_started`, `scrape_completed`, `enrichment_failed`).
  - Endpoint `GET /api/v1/patch-notes/audit?limit=100` para inspección.
- **Dependencias**: ninguna.
- **Risk**: bajo. Sobreescribir: rotar logs si el archivo crece > 10MB.

### 5.2 Métricas de salud (`L:S`)

- **Problema**: ¿con qué frecuencia falla un adapter? ¿cuánto tarda
  scrapear `lol_official` vs `mobalytics_patch`? No tenemos números.
- **Alcance**:
  - Agregar timing a cada `_scrape_one_*` en el orchestrator.
  - Endpoint `/api/v1/patch-notes/metrics` con: success rate por source,
    p50/p95 latency, total scrapes en últimos 7 días.
  - Bonus: tab "Métricas" en source registry view.
- **Dependencias**: 5.1 (log) o estructura propia.
- **Risk**: bajo.

### 5.3 Migración a async Playwright (`L:L`)

- **Problema**: el patrón de "cerrar el browser temprano para liberar el
  slot del thread" es un workaround. La solución correcta es usar la API
  async de Playwright e integrarla con FastAPI nativamente.
- **Alcance**:
  - Reescribir cada adapter Playwright a async (`async def discover`,
    `async def extract`).
  - El orchestrator pasa a ser async; `run_full_scrape` retorna coroutine.
  - El endpoint `/scrape` puede volver a usar `BackgroundTasks` sin
    threading manual.
- **Dependencias**: ninguna. Refactor significativo.
- **Risk**: alto. Cada adapter tiene su quirks. Cubrir bien con tests
  antes de migrar.

---

## Prioridad 6 — Funcionalidades exploratorias

Ideas más especulativas. Listadas por si encajan con la dirección del producto.

### 6.1 Notificaciones push de nuevos parches (`L:L`)

- Service worker que checkea `/health` periódicamente y dispara una
  notificación cuando aparece un nuevo `available_patches[0]`.

### 6.2 Voice search (`L:S`)

- Web Speech API: botón micrófono en search bar → "patch veintiséis diez aatrox".

### 6.3 Export PDF / compartir link (`L:S`)

- `print` styles que generen un PDF legible.
- Link compartible con anchor a sección específica.

### 6.4 Light mode (`L:M`)

- El producto es dark-only por design. Si alguna vez se prioriza
  accesibilidad, requiere redefinir tokens — no es un toggle CSS simple.
- Bloqueado por design intent: ver `DESIGN.md` § Do's and Don'ts.

### 6.5 Video walkthroughs (`L:XL`)

- Embed de videos de YouTube cuando el patch tiene "highlights video"
  oficial de Riot. Requiere scraping adicional y permission policy.

---

## Tabla resumen — recomendación de orden

| # | Item | Prio | Alcance | ROI |
|---|------|------|---------|-----|
| 1.1 | Disclaimer legal Riot | P1 | XS | Crítico antes de publicar |
| 1.2 | Cron UI + log de runs | P1 | M | Alto |
| 1.3 | markdown.new fallback | P1 | M | Medio (depende de cuánto se rompan los adapters) |
| 1.4 | Inline champion enrichment | P1 | S | Alto |
| 2.1 | Item icons inline | P2 | M | Alto |
| 2.2 | Rune icons | P2 | S | Medio |
| 2.3 | Patch impact score | P2 | S | Alto |
| 2.4 | Filtros en diff | P2 | S | Alto |
| 3.1 | Cross-link a draft_advisor | P3 | M | Medio |
| 3.2 | Tier shift indicator | P3 | M | Alto |
| 3.3 | Pro picks tracker | P3 | L | Alto (si la data es fiable) |
| 4.1 | Mobile refinement via Stitch | P4 | M | Medio |
| 4.2 | Patch summary view | P4 | M | Alto |
| 4.3 | "What's new" digest | P4 | M | Medio |
| 5.1 | Audit log | P5 | S | Medio |
| 5.2 | Métricas de salud | P5 | S | Medio |
| 5.3 | Migración async Playwright | P5 | L | Bajo (solo si los workarounds se vuelven inestables) |
| 6.x | Exploratorios | P6 | varios | TBD |

### Sprint propuesto si se reactiva en algún momento

**Sprint V3.0 — "Iconografía completa"** (~ 1 sesión):
- 1.1 Disclaimer legal (XS)
- 1.4 Inline champion enrichment (S)
- 2.1 Item icons inline (M)
- 2.2 Rune icons (S)
- 2.3 Patch impact score (S)

Esto rinde mucho valor visual con poco trabajo, todo dentro del subsistema
y sin dependencias externas nuevas.

**Sprint V3.1 — "Operabilidad"** (~ 1 sesión):
- 1.2 Cron UI + log de runs (M)
- 5.1 Audit log (S)
- 5.2 Métricas (S)
- 2.4 Filtros en diff (S)

Convierte el subsistema en algo verdaderamente operable en producción.

---

## Estado del proyecto al cierre V2.5

- 16 patches en disco (26.10 al 25.12, es-es)
- 7 adapters funcionales (todos OK, riot_calendar fix via Playwright en V2.5)
- 65 tests verdes
- Server `:8005` operativo
- 4 vistas UI funcionales: overview / detail con tabs / search / diff
- Version pill `v2.2.0` visible en hero
- Design system canónico aplicado
- DESIGN.md disponible para iteración con Stitch
- Documentación: `README.md`, `DESIGN.md`, `V3_ROADMAP.md` (este archivo),
  `deep-research-report.md`, `Google_Stitch_DESIGNmd_Guia.pdf`

**Próximo movimiento**: stand by hasta nuevo aviso. Cuando se reactive,
abrir este archivo, elegir un item, y comenzar.
