# Draft Advisor — Documentación Técnica

> Motor de recomendación de picks para ranked/clash de League of Legends.
> Soporta roles **ADC**, **Soporte** y **Jungla**. Ultima actualizacion: 2026-05-11.

---

## Levantar el servidor

```bash
# Desde la raíz del repo (con .venv activado)
python -m riot_lol_cli.draft_advisor.server

# Abrir en browser
start http://localhost:8001/draft
```

Puerto **8001** — separado del Meta Analyzer API (8000).

---

## Arquitectura

```
src/riot_lol_cli/draft_advisor/
├── server.py          FastAPI app + StaticFiles mount
├── api.py             Router /api/v1/draft/*
├── scoring.py         Motor de scoring multifactor
├── analyzer.py        Análisis de composición (amenazas, gaps)
├── champion_data.py   Loader de JSONs + validación cruzada
├── jungle_meta_provider.py Proveedor Jungle Meta HTTP + fallback local
├── schemas.py         Modelos Pydantic V2
└── static/
    ├── index.html     SPA única
    ├── styles.css     Estilos de la app
    ├── app.js         Lógica frontend (vanilla JS)
    └── design-system/ Tokens CSS canónicos (ver docs/design-system.md)
        ├── tokens.css
        ├── components.css
        └── compat-spa.css
```

---

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/draft` | Sirve la SPA |
| `GET` | `/api/v1/draft/champions` | Lista todos los campeones base |
| `GET` | `/api/v1/draft/champions/adcs` | Lista ADCs con perfil detallado |
| `GET` | `/api/v1/draft/champions/junglers` | Lista junglas recomendables desde Jungle Meta |
| `GET` | `/api/v1/draft/champions/supports` | Lista Supports con perfil detallado |
| `GET` | `/api/v1/draft/meta/version-info` | Version de patch, datos, snapshot ADC y contexto Jungle Meta |
| `POST` | `/api/v1/draft/recommend` | Recomienda pick dado un DraftState |
| `GET` | `/api/v1/draft/health` | Estado del servicio |

### POST /api/v1/draft/recommend — payload

```json
{
  "allies": [{"id": "Maokai"}, {"id": "LeeSin"}, {"id": "Ahri"}, {"id": "Samira"}],
  "enemies": [{"id": "Ornn"}, {"id": "Graves"}, {"id": "Syndra"}, {"id": "Caitlyn"}, {"id": "Zed"}],
  "target_role": "support",
  "context": {
    "pick_position": "late",
    "queue_type": "ranked_solo"
  }
}
```

`target_role` acepta `"adc"`, `"support"` o `"jungle"`. Default del schema y del front: `"adc"`.

### Respuesta ADC

En modo ADC, cada `top_pick` y alternativa incluye `adc_context`:

- `personal_tier`: tier de `personal_adc_mastery.json`.
- `meta_tier`, `meta_climb_score`, `meta_patch`, `meta_scraped_at`: datos del ultimo snapshot ADC.
- `eligibility`: `core`, `fallback_meta_soft`, `fallback_meta_low`, `fallback_lane_veto`, `fallback_draft_veto`, `fallback_meta_missing`, `fallback_personal_b_meta_s` o `fallback_meta_unavailable`.
- `eligibility_reason`: texto corto para auditar por que entro o quedo como fallback.

`RecommendationOutput.adc_priority_context` agrega estado global del snapshot,
warning de stale/missing, cantidad de candidatos elegibles y campeones detectados
por scraping que todavia no tienen perfil local.

### Respuesta Jungla

En modo Jungla, cada `top_pick` y alternativa incluye `jungle_context`:

- `tier`, `winrate`, `pickrate`, `banrate`: stats curadas de Jungle Meta.
- `patch`, `updated_at`: version y fecha/hora de la fuente.
- `source_status`: `http`, `local_fallback` o `unavailable`.
- `source`: fuente humana del snapshot (`SkillCapped Patch 26.09 Jungle Tier List` en v1).
- `core_builds`, `core_rune`: build/runa para mostrar items locales en la card.
- `eligibility`: `core`, `fallback_tier_b`, `fallback_tier_c_pool_only` o `fallback_tier_c_pool_preferred`.

La fuente primaria es `Jungle Meta` (`:8003`, endpoint `/api/v1/jungle/tier-list`).
Si el servicio no esta levantado, `jungle_meta_provider.py` usa fallback local
con `riot_lol_cli.jungle_meta.loader.load_jungle_tier_list()`, leyendo
`data/jungle_meta/patch_26.09.json`. `Meta Scraper :8002` queda documentado
como contexto secundario futuro: no decide el ranking de jungla en v1.

---

## Motor de scoring

### Modo ADC

ADC usa una politica de prioridad antes de ordenar recomendaciones:

| Capa | Peso final | Fuente |
|------|------------|--------|
| Maestría personal | 30% | `data/draft_advisor/personal_adc_mastery.json` |
| Meta ADC vigente | 30% | `data/meta_scraper/normalized/latest_adc_tier.json` |
| Fit de draft | 40% | scoring multifactor existente + KB |

Reglas vigentes:

- Top pick ADC requiere tier personal `S/A` y meta fuerte real: tier de scraping `S` o `climb_score >= 80`.
- Tier personal `B` solo entra como fallback si el scraping lo marca `S`.
- Meta `A` con `climb_score < 80` queda como `fallback_meta_soft`; meta `B` o inferior queda como `fallback_meta_low`.
- Reglas KB de linea pueden marcar `fallback_lane_veto`; por ejemplo Nilah + Soraka contra Caitlyn + Nautilus no puede ser primera opcion si existe cualquier ADC no vetado.
- Reglas KB de matchup pueden sumar fit tactico sin saltarse el gate de meta/maestria; por ejemplo Xayah recibe bonus contra Malphite y Tahm Kench por negar engage frontal y castigar frontlines melee con plumas.
- Reglas tácticas internas pueden marcar `fallback_draft_veto`, por ejemplo hypercarries sin movilidad/frontline contra dive o burst pesado.
- `excluded_from_recommendations` bloquea campeones que no queres jugar aunque el scraping los marque fuerte.
- `never_top_pick` permite que un campeon aparezca como alternativa, pero nunca como primera opcion.
- Si el snapshot ADC falta o tiene mas de 72 horas, el motor muestra warning y cae a fallback de maestria personal.
- Los campeones que aparecen en scraping pero no tienen perfil local en `adc_profiles.json` se reportan como `meta_only_missing_profiles`, no se recomiendan.

El fit de draft calcula sinergias, counters, macro/micro, seguridad blind, gap
fill, SoloQ y escalado. Ese puntaje queda como `draft_fit_score` dentro del
`score_breakdown` y pesa 40% dentro de los candidatos que pasaron los gates.

### Modo Jungla

Jungla usa `Jungle Meta` como fuente de verdad v1. No existe todavia
`personal_jungle_mastery.json`; el pool del usuario solo afecta visibilidad y
comfort opcional, no reemplaza la tier list.

| Capa | Peso final | Fuente |
|------|------------|--------|
| Fuerza Jungle Meta | 70%-80% | `http://localhost:8003/api/v1/jungle/tier-list` o fallback local |
| Fit de draft | 20% | analyzer de composicion + tags de campeon |
| Comfort opcional | 10% | `user_pool.comfort` cuando se envia |

Reglas vigentes:

- `S/A` puede ser top pick.
- `B` solo puede ser top si no hay `S/A` disponible en el pool o todos los `S/A` estan pickeados/baneados.
- `C` solo puede ser top en `pool_only` sin mejores opciones, con warning visible.
- Campeones fuera de Jungle Meta no se recomiendan; si aparecen en el pool, la API los rechaza como "no esta en Jungle Meta".
- `pool_preferred` prioriza meta `S/A/B` y agrega picks del pool como alternativas si estan en Jungle Meta.
- El badge superior del front agrega estado de Jungle Meta cuando el rol seleccionado es `Jungla`.

### Modo Support

| Factor | Peso | Descripción |
|--------|------|-------------|
| Sinergia con ADC aliado | 35% | `best_with_adcs` / `worst_with_adcs` + **bonus de sinergia medida** |
| Matchup vs enemigos | 20% | `anti_dive`, `anti_poke`, `anti_assassin` + **triángulo Engage/Poke/Sustain** |
| Gap fill composición | 20% | Engage gap, peel gap, frontline gap, AP gap |
| Escalado / fase de juego | 15% | `lane_phase_strength` + `lategame_strength` |
| Solo queue safety | 10% | `blind_pick_safety` — `execution_difficulty` |

### Modificadores aditivos (NotebookLM 2026-04-27)

**Sinergias medidas (`measured_synergies.json`):**
- Si la pareja `{ADC aliado, supp candidato}` está en el JSON con `confidence: "measured"` y WR > 50%, aplica bonus interpolado: cada 1 punto de WR sobre 50% → +3 score (cap 15pts).
- Ej: `Ashe + Seraphine` (54.7% WR) → +14.1 score al `ally_synergy`.
- Heurísticas pro-scene (`confidence: "heuristic"`) reciben bonus reducido: factor 0.6 (cap 9pts).

**Triángulo estratégico (`strategic_triangle.json`):**
- Detecta el arquetipo del support enemigo (5 categorías fine-grained: `engage`, `poke`, `enchanter_disengage`, `enchanter_pure`, `catcher`).
- Si el support candidato counterea al enemigo, suma +10 al `enemy_matchup`.
- Si es counter-pickeable → -8 al `enemy_matchup`.
- Reglas: Engage > Poke; Poke > Enchanter; Enchanter Disengage > Engage (eje invertido); Catcher > Poke + Enchanter pure.

**Predominancia de comp (`comp_predominance.json`, futuro):**
- Aplica al ciclo Attack > Siege > Protect > Catch > Attack.
- No integrado al motor en esta iteración; queda como upgrade.

---

## Datos

### data_manifest.json
Metadata visible del servicio: `live_patch_label` actual `16.9`, `static_data_version` actual `16.9.1`, `last_verified_at` `2026-05-04T11:48:07-03:00`. El header de la SPA muestra `Parche`, `Data Dragon` y fecha/hora de ultimo update.

`live_patch_label` y `static_data_version` no son exactamente lo mismo:

- `live_patch_label`: parche jugable/meta usado para balance y decisiones de draft.
- `static_data_version`: version tecnica de Data Dragon/CDN para campeones, items, splash arts y metadata estatica. Puede tener sufijos como `.1` aunque el parche visible siga siendo `16.9`.

### champion_base.json
172 campeones con: `id`, `display_name`, roles, clase, daño, rango, tags y metadatos de Data Dragon.

### adc_profiles.json
32 perfiles ADC con scoring profundo. Campos clave:
- factores 1-10: rango efectivo, movilidad, self peel, dificultad, seguridad blind, prioridad de lane, scaling, anti-tank, anti-dive, anti-poke
- relaciones canonicas: `best_with[]`, `worst_into[]`
- notas: `power_spikes[]`, `strengths[]`, `weaknesses[]`, `draft_notes`

### personal_adc_mastery.json
Tier list personal del usuario para ADC:
- path: `data/draft_advisor/personal_adc_mastery.json`
- fuente visual: `KB/tier list adc 04 05 2026.png`
- campos consumidos: `tiers.S/A/B/C/D`, `last_updated`, `source_image`, `needs_review`
- campos de control: `excluded_from_recommendations`, `never_top_pick`
- solo campeones con perfil local en `adc_profiles.json` son recomendables
- entradas en `needs_review` no afectan scoring hasta confirmacion manual

### latest_adc_tier.json
Snapshot opcional generado por Meta Scraper (3 fuentes: OP.GG, LoLalytics, U.GG):
- path: `data/meta_scraper/normalized/latest_adc_tier.json`
- endpoints: `POST /api/v1/meta/scrape/adc`, `GET /api/v1/meta/adc/tier`
- campos consumidos: `scraped_at`, `patch`, `sources`, `stats.tier`, `stats.win_rate`, `stats.pick_rate`, `stats.ban_rate`, `stats.climb_score`
- stale si `scraped_at` supera 72 horas
- las tarjetas de recomendacion muestran patch, fecha de scrape y chips de meta; el header solo muestra version general de datos

### latest_support_tier.json
Snapshot opcional generado por Meta Scraper (mismas fuentes):
- path: `data/meta_scraper/normalized/latest_support_tier.json`
- endpoints: `POST /api/v1/meta/scrape`, `GET /api/v1/meta/support/tier`
- campos consumidos: `stats.win_rate`, `stats.pick_rate`, `stats.ban_rate`
- el factor `solo_queue_reliability` de Support incorpora este bonus acotado a `[-10, +12]`
- sin `climb_score` (el normalizer no lo calcula para support)

### Jungle Meta para Draft Advisor
Fuente primaria para recomendaciones de Jungla:
- HTTP preferido: `http://localhost:8003/api/v1/jungle/tier-list`
- fallback local: `data/jungle_meta/patch_26.09.json`
- loader compartido: `riot_lol_cli.jungle_meta.loader.load_jungle_tier_list()`
- campos consumidos: `jungle_champions[].tier`, `winrate`, `pickrate`, `banrate`, `reason_text`, `core_builds`, `core_rune`, `categories.overpowered`, `categories.bans`
- `Meta Scraper :8002` y `latest_jungle_tier.json` quedan como contexto secundario futuro, sin impacto en scoring Jungla v1

### Proveniencia y sanitizacion de datos

Los reportes historicos de auditoria quedaron absorbidos en esta seccion para evitar auditorias sueltas fuera de la doc canonica.

Decisiones vigentes:

- Separar `live_patch_label` del `static_data_version`: el primero es el parche visible para jugadores; el segundo es la version tecnica de Data Dragon que alimenta assets/datos estaticos.
- Validar el roster base contra Data Dragon antes de tratar `champion_base.json` como confiable.
- Mantener ADC roster, support roster y priority profiles como subconjuntos curados del proyecto, no como reflejo automatico de todo Data Dragon.
- Usar siempre IDs canonicos de `champion_base.json` en perfiles y relaciones: `JarvanIV`, no `Jarvan`; `KogMaw`, no `Kog'Maw`; `TahmKench`, no `Tahm Kench`.
- Proteger el pipeline contra contaminacion LoL/TFT y notas de parche de otros productos.
- Mostrar en UI el contexto correcto del dato: no presentar version tecnica de DDragon como si fuera parche live.

Campos auditados historicamente:

| Dataset | Fuente esperada | Riesgo a vigilar |
|---------|-----------------|------------------|
| `champion_base.json` | Data Dragon + curacion local | drift de roster o version conflada |
| `adc_profiles.json` | Curacion experta | alias no canonicos en relaciones |
| `support_profiles.json` | Curacion experta + KB | alias no canonicos o counters stale |
| `priority_profiles.json` | Curacion experta | claims sin fuente actualizada |
| `kb/research/**/*.md` | notas con frontmatter | patch labels stale |
| `scoring_weights.json` | arquitectura del motor | cambios sin evals |

### Contrato de integridad

`ChampionDataService` valida al iniciar. Si hay una referencia invalida en los JSON, `/api/v1/draft/health` y `/api/v1/draft/champions` pueden devolver 500 y el picker del front queda vacio.

Verificacion minima al tocar datos/scoring:

```bash
pytest tests/draft_advisor/test_data_integrity.py
pytest tests/draft_advisor
ruff check src/riot_lol_cli/draft_advisor tests/draft_advisor
ruff format --check src/riot_lol_cli/draft_advisor tests/draft_advisor
```

### support_profiles.json
34 perfiles Support con scoring profundo. Campos clave:
- `archetype`: `engage | enchanter | poke | catcher | warden`
- `engage_strength`, `peel_strength`, `anti_dive`, `anti_assassin_peel`
- `best_with_adcs[]`, `weak_against_supports[]`
- `play_pattern_template`

Roster actual: Alistar, Ashe, Bardo, Blitzcrank, Brand, Braum, Camille, Janna, Karma, Leona, Lulu, Lux, Maokai, Milio, Nami, Nautilus, Pantheon, Poppy, Pyke, Rakan, Rell, Renata, Senna, Shen, Sona, Soraka, Swain, Sylas, Taric, Thresh, Vel'Koz, Xerath, Yuumi, Zyra.

### Política de idioma

- La UI, API visible, perfiles JSON y notas activas de KB deben estar en español rioplatense claro.
- Los IDs internos siguen siendo los canónicos de Data Dragon (`Bard`, `MasterYi`, `KogMaw`) aunque el `display_name` visible use español (`Bardo`, `Maestro Yi`, `Kog'Maw`).
- Se permiten tecnicismos de LoL cuando son más claros que una traducción forzada: `ADC`, `draft`, `teamfight`, `stun`, `dive`, `peel`, `poke`, `engage`, `roam`, `gank`, `matchup`, `all-in`, `frontline`, `wave`, `burst`, `scaling`.

### KB/ (Knowledge Base)
Documentos markdown con el razonamiento estratégico detrás del scoring:
- `KB/filosofia-de-pickeo.md` — pesos, heurísticas (17 reglas)
- `KB/arquetipos-de-soporte.md` — engage / enchanter / poke / catcher
- `KB/sinergia-supp-adc.md` — tabla de sinergias 10×15
- `KB/matchups-supp-vs-supp.md` — matchups de lane
- `KB/plan-de-juego-por-arquetipo.md` — templates de game plan
- `KB/amenazas-y-respuestas.md` — vs dive comp, vs poke comp, etc.

---

## Frontend (SPA)

Stack: **HTML + CSS + JavaScript vanilla**. Sin React, sin bundler, sin TypeScript.

### Flujo de interacción

```
Init -> GET /api/v1/draft/champions + /api/v1/draft/meta/version-info
     -> renderiza patch-badge con parche, version Data Dragon y fecha/hora de ultimo update

Click slot vacio -> openChampionPicker(team, index)
     -> Modal con search + role filters
     -> click campeon -> asigna slot, cierra modal

Click "Analizar Draft" -> POST /api/v1/draft/recommend
     -> renderResults() -> Recomendación principal + 3 alternativas
     -> chips: Maestría, Meta, Subida, Scraping, Alternativa
     -> scroll automatico a resultados
```

### State global (app.js)

```javascript
const state = {
  champions: [],          // todos los campeones cargados
  allies: [null,null,null,null],
  enemies: [null,null,null,null,null],
  poolMode: 'unrestricted',
  poolChampions: [],
  comfort: {},
  modalTarget: null,
  roleFilter: 'all',
  recommendation: null,
  targetRole: 'adc',  // default actual del front
};
```

### Design System

La SPA carga 4 hojas de estilo en orden:
```html
<link href="/static/design-system/tokens.css?v=1">   <!-- tokens canónicos -->
<link href="/static/design-system/compat-spa.css?v=1"> <!-- aliases legacy SPA -->
<link href="/static/design-system/components.css?v=1"> <!-- .btn, .card, .pill -->
<link href="/static/styles.css?v=3">                  <!-- estilos específicos SPA -->
```

Ver [docs/design-system.md](../design-system.md) para la documentación completa.

---

## Upgrade Futuro: Pool de Campeones

El panel "Pool de Campeones" está **comentado en index.html** (líneas 104-133).
Permite definir un pool personal y niveles de confort para sesgar las recomendaciones.

**Backend ya implementado:** `DraftState.pool_mode`, `DraftState.comfort`, validación de pool en `api.py`.

**Para activar:**
1. Descomentar el bloque HTML en `index.html`
2. Implementar `setPoolMode()`, `renderComfortSliders()`, `addToPool()` en `app.js`
3. Asegurarse de que el payload del POST incluye `pool_champions` y `comfort`

---

## Tests

```bash
# Smoke test del endpoint de recommend
curl -X POST http://localhost:8001/api/v1/draft/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "allies": [{"id":"Maokai"},{"id":"LeeSin"},{"id":"Ahri"},{"id":"Samira"}],
    "enemies": [{"id":"Ornn"},{"id":"Graves"},{"id":"Syndra"},{"id":"Caitlyn"},{"id":"Zed"}],
    "target_role": "support",
    "context": {"pick_position":"late"}
  }' | python -m json.tool

# Verificar lista de supports
curl http://localhost:8001/api/v1/draft/champions/supports | python -m json.tool

# Health check
curl http://localhost:8001/api/v1/draft/health | python -m json.tool
```
