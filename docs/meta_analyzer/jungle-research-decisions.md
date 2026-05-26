# Jungla 360 — Decisiones de Arquitectura (ADRs)

Registro de decisiones clave tomadas en el diseño del subsistema Jungle Research.

---

## ADR-001: Storage en JSON snapshots, no en BD relacional

**Fecha**: 2026-04-15  
**Estado**: ✅ Implementado  
**Impacto**: Alta

### Problema
Necesitamos guardar tier lists diarias para auditar cómo cambia el meta, y también poder revertir si un adapter genera datos erróneos.

### Opciones consideradas
1. **PostgreSQL** con migrations: Relacional, transacciones ACID, pero heavy setup
2. **JSON snapshots en Git**: Simple, versionado automático, auditable por commit
3. **SQLite** local: Más light que PG, pero pierde versionado Git

### Decisión
**JSON snapshots** (opción 2). Cada día genera un backup timestamped en `data/meta_analyzer/jungle_research/final_jungle_tierlist/backups/`, y `latest.json` apunta siempre al más reciente.

### Justificación
- Máxima auditabilidad: Cada snapshot es un commit Git con metadata
- Sin migrations: Simplifica onboarding
- Respaldos automáticos: No requiere scheming de BD
- Trade-off: No transacciones atómicas, pero aceptable para read-mostly workload

---

## ADR-002: Scoring con suma ponderada de cohortes

**Fecha**: 2026-04-20  
**Estado**: ✅ Implementado  
**Impacto**: Alta

### Problema
Necesitamos priorizar campeones no por una métrica única (WR%), sino por un balance de:
- Prevalencia en SoloQ (UGG, Lolalytics)
- Comfort en Asia (leaguepedia, data_dragon)
- Uso en High Elo (Gol.gg, scouted players)
- Presencia en pro stage (esports_research comfort)

### Opciones consideradas
1. **Solo WR%**: Simple, pero ignoraría prevalencia y comfort regional
2. **Ranking voting**: Múltiples tier lists votadas (3-way tie resolution), pero opaco
3. **Suma ponderada normalizada**: Explícito, auditable, fácil de ajustar pesos

### Decisión
**Suma ponderada** (opción 3):
```
final_score = (
  soloq_score * 0.50 +      // Banderas de fortaleza en SoloQ
  asia_score * 0.20 +       // Preferencia regional Asia
  high_elo_presence * 0.15 + // Viabilidad en altos elos
  pro_presence * 0.15        // Comfort de pros
)
```
Luego se normaliza por percentil dentro de la cohorte patch/región.

### Justificación
- **Transparencia**: Cada peso es observable y debatable
- **Auditabilidad**: Cambios de pesos dejan rastro en `bitacora_de_cambios.md`
- **Flexibilidad**: Ajustable si el meta requiere enfoque distinto (ej: boost pro antes de Worlds)
- **Defensa contra outliers**: Un adapter mal no domina el consensus (es solo 20% del score)

---

## ADR-003: Adapter strategy: SSR parse con BeautifulSoup, sin Playwright

**Fecha**: 2026-05-10  
**Estado**: ✅ Implementado  
**Impacto**: Media

### Problema
Los principales data sources (METAsrc, Gol.gg, Leaguepedia) sirven SSR HTML sin JS. ¿Usamos Playwright (headless browser) o parseo directo?

### Opciones consideradas
1. **Playwright**: Full JS rendering, cubre dynamic sites, pero ~200MB overhead, lento
2. **BeautifulSoup**: Puro HTML parse, rápido, pero falla si sitio es 100% JS
3. **API directo** (si existe): Ideal, pero muchos sitios no publican API

### Decisión
**BeautifulSoup** (opción 2) como default. Si un sitio es 100% JS, se marca como `gap: js_required` y se queda en `planned`.

### Justificación
- 95% de targets son SSR: METAsrc, Gol.gg, Leaguepedia ya sirven HTML completo
- Performance: Parse en <100ms vs Playwright ~2s
- Mantenibilidad: Menos dependencias (no chromium)
- Graceful degradation: Fácil detectar si selectores fallan y marcar como error

### Selectores clave (por adapter)
- **metasrc_jungle**: `table.tier-list tbody tr` + `td:nth-child(1)` (champ), `td:nth-child(4)` (tier)
- **lolalytics_jungle**: `[data-role="row"]` + data attributes
- **gol_gg_jungle**: `.champion-row .name`, `.wr`, `.pr`

---

## ADR-004: Pro presence sin resolver PUUID si no hay RIOT_API_KEY

**Fecha**: 2026-05-20  
**Estado**: ✅ Implementado (PR-C)  
**Impacto**: Media

### Problema
Tenemos datos de comfort de pro players en esports_research (dónde juegan, qué campeones), pero necesitaríamos resolver su PUUID actual para matchear sus SoloQ recent matches. Eso requiere `RIOT_API_KEY`.

### Opciones consideradas
1. **Requerir RIOT_API_KEY**: Hard dependency, bloquea gente sin key
2. **Usar solo esports comfort, sin SoloQ matching**: Desacoplado, pero menos preciso
3. **Optional resolution**: Si key presente, resuelve; si no, usa comfort as-is

### Decisión
**Opción 3**: Pro presence vive en `esports_research/gold/comfort_features_*.json`. Si `RIOT_API_KEY` está set, se resuelve PUUID y se enriquece; si no, la columna "Pro presence" en Consenso muestra solo comfort (score ≥ 0 si jugador apareció en esports).

### Justificación
- **Decoupling**: jungle_research no requiere Riot API, esports_research sí
- **Clarity**: Dos fuentes distintas, dos procesos: esports (determinístico) vs SoloQ (RIOT_API)
- **Audit trail**: Badge "ES" en tabla muestra origen (esports_research comfort)

---

## ADR-005: Drill-down expandible en tabla Consenso, no spread sheet

**Fecha**: 2026-05-25  
**Estado**: ✅ Implementado (PR-D)  
**Impacto**: Baja (UI)

### Problema
Tabla Consenso tiene muchas columnas (tier, champ, score, confidence, soloq, asia, high_elo, pro, warnings, explanation). En mobile y small screens, es ilegible.

### Opciones consideradas
1. **Todos las columns visibles**: Horizontal scroll, ilegible en mobile
2. **Tabs secundarios para detalles**: Extra clicks, ruptura de flow
3. **Drill-down expandible** (fila detalle): Mismo contexto, reveal on demand

### Decisión
**Drill-down expandible** (opción 3):
- Tabla primary: Tier | Champion | Score | Confidence | Source Count
- Click → expandible row muestra: SoloQ score, Asia score, High Elo, Pro presence, Warnings, Explanation

### Justificación
- **Mobile-first**: 5 columnas caben en cualquier pantalla
- **Information hierarchy**: Highlights lo importante (tier, champ, score) primero
- **Responsive**: Auto-grid en detalle se stacks en mobile
- **Sin ruptura**: El usuario sigue en la misma tabla, no navega a otra vista

---

## ADR-006: Dashboard extraction a /static/, no en Python string

**Fecha**: 2026-05-24  
**Estado**: ✅ Implementado (PR-D)  
**Impacto**: Baja (DevExp)

### Problema
`dashboard_enhanced.py` tenía 1554 líneas de raw HTML/CSS/JS embebido. Hacer cambios UI requería grep-por-el-archivo y era propenso a mojibakes.

### Opciones consideradas
1. **Mantener embedido en Python**: Centralizado, una línea para servir
2. **Archivos separados en /static/**: HTML/CSS/JS en archivos reales, pero agrupa en import-time
3. **Servir directo con StaticFiles**: Sin aggregation, requiere cambiar route

### Decisión
**Opción 2**: Extraer a `/src/riot_lol_cli/meta_api/static/dashboard-enhanced/`:
- `index.html` — skeleton con placeholders `/* {{DASHBOARD_CSS}} */`, `/* {{DASHBOARD_JS}} */`
- `dashboard.css` — estilos base + tabs
- `dashboard.js` — lógica general (switchTab, matchups, items, raw-data, modales)
- `jungle-research.js` — lógica Jungla 360 (jr* functions)

`dashboard_enhanced.py` queda como wrapper que lee los 4 archivos y arma `ENHANCED_DASHBOARD_HTML` en import-time.

### Justificación
- **Separation of concerns**: Cambios UI no tocan Python
- **Debuggable**: Inspecciona HTML real en DevTools, no generado
- **Syntax highlighting**: IDE soporta correctamente HTML/CSS/JS files
- **Backwards-compatible**: El contrato de `ENHANCED_DASHBOARD_HTML` (string) se preserva

---

## ADR-007: Mini-router hash en lugar de full SPA framework

**Fecha**: 2026-05-25  
**Estado**: ✅ Implementado (PR-D)  
**Impacto**: Baja (Frontend)

### Problema
Dashboard tiene 5 tabs principales (Dashboard, Matchups, Items, Raw Data, Jungla 360), y Jungla 360 tiene 5 sub-tabs internos. ¿Usamos React/Vue con routing, o un mini-router vanilla?

### Opciones consideradas
1. **React/Vue router**: Full SPA, componentes, state management, pero +200KB bundle
2. **Full vanilla JS**: Sin framework, pero buen control
3. **Minimal router**: 50 líneas de JS, hash-based, sufficient para navegación

### Decisión
**Opción 3**: Minimal vanilla router:
- Hash format: `#tab` (primary) o `#tab/subtab` (jungle-research sub-tabs)
- Click en tab → `switchTab()` → actualiza hash
- Hash change → `hashchange` event → `jrActivateView()` restaura estado
- DOMContentLoaded → si hash presente, restaura desde URL

### Justificación
- **Lightweight**: No bundler needed, 0 dependencies
- **Shareable URLs**: `http://localhost:8000/dashboard-enhanced#jungle-research/jr-sources` funciona
- **Smoke visual**: URLs reproducibles para test automation
- **Simple state**: Tabs no tienen estado complex, hash es suficiente

---

## 🔗 Referencias

- [`jungle-research-status.md`](jungle-research-status.md) — métricas y estado actual
- [`jungle-research-roadmap.md`](jungle-research-roadmap.md) — fases futuras
- [`AGENTS.md`](../../AGENTS.md) — subsistema details
- `bitacora_de_cambios.md` — decisiones por fecha
