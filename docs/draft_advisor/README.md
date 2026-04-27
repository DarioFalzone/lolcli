# Draft Advisor — Documentación Técnica

> Motor de recomendación de picks para ranked/clash de League of Legends.
> Soporta roles **ADC** y **Soporte**. Última actualización: 2026-04-26.

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
| `GET` | `/api/v1/draft/champions/supports` | Lista Supports con perfil detallado |
| `GET` | `/api/v1/draft/meta/version-info` | Versión de patch y datos |
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

`target_role` acepta `"adc"` o `"support"`. Default: `"support"`.

---

## Motor de scoring

### Modo ADC

| Factor | Peso | Descripción |
|--------|------|-------------|
| Synergy con aliados | 35% | Fit con jungla, mid, support aliados |
| Counter a enemigos | 25% | Matchup vs ADC/support enemigo |
| Gap fill composición | 20% | Cubre frontline/engage/peel faltante |
| Blind pick safety | 10% | Seguridad en pick ciego |
| Comfort (pool) | 10% | Penalización por baja familiaridad |

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
- Detecta el archetype del enemy support (5 categorías fine-grained: `engage`, `poke`, `enchanter_disengage`, `enchanter_pure`, `catcher`).
- Si el supp candidato counterea al enemy → +10 al `enemy_matchup`.
- Si es counter-pickeable → -8 al `enemy_matchup`.
- Reglas: Engage > Poke; Poke > Enchanter; Enchanter Disengage > Engage (eje invertido); Catcher > Poke + Enchanter pure.

**Predominancia de comp (`comp_predominance.json`, futuro):**
- Aplica al ciclo Attack > Siege > Protect > Catch > Attack.
- No integrado al motor en esta iteración; queda como upgrade.

---

## Datos

### champion_base.json
171 campeones con: `id`, `name`, `roles[]`, `damage_type`, `range_type`.

### adc_profiles.json
24 ADCs con perfiles detallados. Campos clave:
- `lane_kill_pressure`, `teamfight_scaling`, `blind_pick_safety`
- `best_with_supports[]`, `weak_against_adcs[]`
- `play_pattern_template` (con placeholders `{ally_support}`, `{primary_threat}`)

### support_profiles.json
10 soportes core (fase 1). Campos clave:
- `archetype`: `engage | enchanter | poke | catcher`
- `engage_strength`, `peel_strength`, `anti_dive`, `anti_assassin_peel`
- `best_with_adcs[]`, `weak_against_supports[]`
- `play_pattern_template`

**Soportes fase 1:** Leona, Nautilus, Thresh, Lulu, Janna, Soraka, Milio, Lux, Pyke, Karma.
**Soportes fase 2 (pendiente):** Blitzcrank, Rakan, Rell, Alistar, Nami, Yuumi, Renata, Zyra, Brand, Xerath, Vel'Koz, Swain, Senna, Bard.

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
Init → GET /api/v1/draft/champions + /api/v1/draft/meta/version-info
     → renderiza patch-badge

Click slot vacío → openChampionPicker(team, index)
     → Modal con search + role filters
     → click campeón → asigna slot, cierra modal

Click "Recomendar Pick" → POST /api/v1/draft/recommend
     → renderResults() → Top Pick Card + 3 Alternatives
     → scroll automático a resultados
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
  targetRole: 'support',  // default actual
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
