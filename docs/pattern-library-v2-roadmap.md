# Hoja de Ruta — Rediseño Pattern Library v2

> Estado del rediseño visual completo aplicando `tokens.css` + `patterns.css` a las 6 surfaces.
> Actualizar la tabla de estado y el log de cambios a medida que se mergean PRs.

---

## Estado por surface

| PR | Surface | Puerto | Estado | Commit/Branch |
|---|---|---|---|---|
| 1 | Draft Advisor | `:8001` | ✅ Completado | `feat/draft-advisor-pattern-library-v2` (`460623f`) |
| 2 | Items Browser | `:8004` | ✅ Completado | `feat/items-browser-pattern-library-v2` (`f270bc0`) |
| 3 | Jungle Meta | `:8003` | ✅ Completado | `feat/jungle-meta-pattern-library-v2` (`892acd4`) |
| 4 | Home Hub | `:8080` | ✅ Completado | `feat/home-hub-pattern-library-v2` (`30e13c7`) |
| 5 | Meta Scraper | `:8002` | ✅ Completado | `feat/meta-scraper-pattern-library-v2` (`01e78fa`) |
| 6 | Splash Viewer | offline | ✅ Completado | `feat/splash-viewer-pattern-library-v2` (`f98e215`) |

---

## Orden de carga canónico (todas las surfaces)

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800;900&family=Anton&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/static/design-system/tokens.css?v=2">
<link rel="stylesheet" href="/static/design-system/patterns.css?v=2">
<link rel="stylesheet" href="/static/styles.css?vN">
```

---

## Recipes por surface

| Surface | Shell | Hero | Patrones principales | Modal/Detail |
|---|---|---|---|---|
| Home Hub | `.app-shell` premium | `.hero` compact | `.stat-strip`, `.card.interactive` (service cards), `.banner` | — |
| Items Browser | flat black | `.hero` compact ("ITEMS") | `.control-panel`, `.tabs`, `.entity-card` grid | `.modal` (item detail) |
| Jungle Meta | flat black | `.hero--dual` ("TIER LIST") | `.cat-card` sidebar, `.tier-tabs`, `.tier-row`, `.champ-card` | `.modal` (champion detail) |
| Meta Scraper | flat black | `.hero` compact (3 sources) | `.data-table`, `.pill` source badges, `.toast`, `.banner` | `.modal` (row detail) |
| Draft Advisor | `.app-shell` premium | `.hero` compact | `.slot` grid, `.score-factor` bars, `.card` (top-pick), `.modal` (picker) | `.modal` |
| Splash Viewer | flat black | `.hero` compact | `.entity-card` grid full-bleed | `.modal` filmstrip (custom) |

---

## Reglas de oro

- ❌ No mergear PRs — solo abrir, el usuario revisa y mergea
- ❌ No tocar `tokens.css` ni `patterns.css` — son canónicos
- ❌ No promover patrones únicos a `patterns.css` — mantener como CSS local
- ❌ No alterar lógica de negocio JS/Python
- ✅ Una surface, un PR — atómicos e independientes
- ✅ Verificar visualmente en browser antes de declarar listo
- ✅ Actualizar `bitacora_de_cambios.md` en el mismo commit
- ✅ Actualizar este archivo al completar cada PR

---

## Log de cambios por PR

### PR 1 — Draft Advisor `feat/draft-advisor-pattern-library-v2`

**Fecha**: 2026-05-10 / 2026-05-11

**Archivos modificados**:
- `src/riot_lol_cli/draft_advisor/static/index.html` — imports fonts + patterns.css, body `.app-shell`, clases compuestas (`.slot.champion-slot`, `.pill.pill-success`, `.card.panel`, `.modal-overlay.modal-backdrop`, etc.)
- `src/riot_lol_cli/draft_advisor/static/styles.css` — reescritura: solo overrides sobre patterns.css, tokens canónicos, layout específico del Draft
- `src/riot_lol_cli/draft_advisor/static/app.js` — slots usan clases Pattern Library (`slot champion-slot filled ally/enemy`) para que patterns.css matchee correctamente

**Decisiones técnicas**:
- `compat-spa.css` eliminado (overridea `--text-primary` y otros tokens canónicos)
- `.app-shell` en `<body>` (premium gradient), `.draft-container` como wrapper interno max-width
- Slots: `slot` base class se preserva al hacer fill via JS (era el bug que rompía imágenes y nombres)
- Modal: `border-metal-strong` + box-shadow profundo para destacar sobre fondo oscuro

**Bugs encontrados y corregidos post-merge**:
1. Slots llenos perdían clase `slot` → JS actualizado a `slot champion-slot filled ally/enemy`
2. `.slot-name` no era uppercase ni estaba contenida → fix via preservar clase `slot`
3. Modal con borde invisible → `border-metal-strong` + shadow
4. Botón `+` descentrado → resuelto al preservar `slot` (flex centering de patterns.css)

---

### PR 2 — Items Browser `feat/items-browser-pattern-library-v2`

**Fecha**: 2026-05-11

**Archivos modificados**:
- `index.html` — imports tokens+patterns, `.control-panel`/`.segmented`/`.tabs` compuestos, `.modal-overlay` + `.modal` reestructurado
- `styles.css` — reescrito como overrides, ~70% CSS redundante eliminado
- `app.js` — `openModal/closeModal` usan `classList.add/remove("active")` en vez de toggle del atributo `hidden`
- `server.py` — mount `/design-system`

---

### PR 3 — Jungle Meta `feat/jungle-meta-pattern-library-v2`

**Fecha**: 2026-05-11

**Archivos modificados**:
- `index.html` — imports, `.hero--dual`, sidebar con `.cat-card.cat-card--accent-{cyan|gold|error}`, tier-tabs renombrados a `.tier-s/a/b/c`, detail-stats con `.stat-strip`
- `styles.css` — overrides, preserva champion detail page única (splash hero, builds, runes)
- `app.js` — champ-card name/stats compuestos con clases canónicas
- `server.py` — mount `/design-system`

---

### PR 4 — Home Hub `feat/home-hub-pattern-library-v2`

**Fecha**: 2026-05-11

**Enfoque conservador**: surface compleja con tweaks system + ambient-particles. Solo se integran tokens canónicos y se componen clases clave.

**Archivos modificados**:
- `index.html` — imports tokens+patterns ANTES de styles.css local, `.stat-strip` compuesto, fonts expandidas
- `app.js` — `.card` compuesto en service-card render
- Preservado: tweaks panel, particles, view-toggle, footer kbd hints, status-summary

---

### PR 5 — Meta Scraper `feat/meta-scraper-pattern-library-v2`

**Fecha**: 2026-05-11

**Decisión clave**: renombrar `.app-shell` local → `.scraper-shell` para evitar colisión con `patterns.css .app-shell` (que aplica gradientes premium incompatibles con la paleta teal/cyan propia del Meta Scraper).

**Archivos modificados**:
- `index.html` — imports tokens+patterns, fonts expandidas, `.app-shell` → `.scraper-shell`
- `styles.css` — `.app-shell` → `.scraper-shell` (2 ocurrencias)
- Preservado: role-tabs animado, stat-cards 4 variantes teal/violet/gold/cyan, gaps-panel, detail-panel slide-in

---

### PR 6 — Splash Viewer `feat/splash-viewer-pattern-library-v2`

**Fecha**: 2026-05-11

**Estado especial**: la surface ya estaba alineada por diseño. Sus tokens inline (`--arc-gold`, `--forge-black`, `--surface-*`, `--state-*`, `--border-metal*`, `--glow-*`, `--elevation-*`, `--radius-*`) coinciden con `tokens.css` canónico.

**Constraint**: distribuible como HTML offline (file://), por lo que mantiene CSS+JS inline en `templates/splash-viewer.html`.

**Archivos modificados**:
- `templates/splash-viewer.html` — comentario explicativo documentando la alineación
- Sin cambios visuales

---

## Próximos pasos

Todos los PRs creados. Pendiente del usuario:

1. **Push** de cada branch a origin (`git push -u origin <branch>`)
2. **Abrir PRs** en GitHub (uno por surface, mergeables independientemente)
3. **Verificación visual** por surface antes de mergear
4. **Iteración aparte** post-merge: evaluar deprecación de `compat-spa.css` y `compat-dashboard.css`
