# Changes — Pattern Library v2

Plan de aplicación granular. Lo usa el agente local guiado por `PROMPT_AGENTE.md`.

---

## 1. Archivos nuevos

### 1.1 `src/riot_lol_cli/draft_advisor/static/design-system/patterns.css`

**Origen:** `claude-design-handoff/pattern-library-v2/files/design-system/patterns.css`

**Tamaño:** 27.7 KB

**Contiene:** clases drop-in para 18 patrones — `app-shell`, `hero` (+
`hero--dual`), `control-panel`, `search-input`, `segmented`, `tabs`, `tab`,
`tier-tabs`, `tier-tab` (con `.tier-s/a/b/c`), `btn` (primary/secondary/ghost/
icon), `card`, `entity-card`, `champ-card`, `tier-row`, `cat-card` (con
accent variants), `stat-strip`, `score-factor`, `data-table`, `modal`,
`state-block`, `skeleton`, `toast`, `banner`, `slot` (filled/ally/enemy),
`pill` (con variantes semánticas).

Cero dependencias, cero JS. Solo CSS. Hereda 100% de `tokens.css`.

### 1.2 `claude-design-handoff/patrones_diseños_claude_design/Pattern Library.html`

**Origen:** `claude-design-handoff/pattern-library-v2/files/reference/Pattern Library.html`

Doc page navegable de referencia. 17 secciones con TOC sticky:
identidad, tokens visualizados, todos los patrones con demo + snippet de
código, recipes por surface, anti-patterns, checklist, handoff.

Junto a la HTML van `tokens.css` y `patterns.css` (mirrors) para que la
página abra standalone sin servir el repo.

---

## 2. Archivos reemplazados

### 2.1 `src/riot_lol_cli/draft_advisor/static/design-system/tokens.css`

**Origen:** `claude-design-handoff/pattern-library-v2/files/design-system/tokens.css`

**Tamaño:** 6.8 KB

**Estrategia:** reemplazo total con backup previo.

```bash
cp src/riot_lol_cli/draft_advisor/static/design-system/tokens.css \
   src/riot_lol_cli/draft_advisor/static/design-system/tokens.css.bak
cp claude-design-handoff/pattern-library-v2/files/design-system/tokens.css \
   src/riot_lol_cli/draft_advisor/static/design-system/tokens.css
```

Tras validar que las surfaces se ven idénticas, eliminar el `.bak`.

**Garantías:**

- ✅ Superset del actual: todos los nombres de variables existentes están en
  v2 con el mismo valor.
- ➕ Variables nuevas (no romper nada, solo añadir):
  - Brand extendido: `--arc-gold-bright`, `--arc-gold-text`,
    `--arc-gold-accent`, `--arc-cyan-bright`, `--arc-cyan-dark`.
  - Surfaces: `--forge-darker`, `--surface-overlay`.
  - Semánticos: `--state-neutral`.
  - Tier: `--tier-s`, `--tier-a`, `--tier-b`, `--tier-c`.
  - Glow / motion: `--glow-gold-sm`, `--glow-gold`, `--glow-cyan-sm`,
    `--glow-error`, `--motion-fast`, `--motion-base`, `--motion-slow`.
  - Type metrics: `--leading-tight`, `--leading-normal`, `--leading-relaxed`,
    `--tracking-tight`, `--tracking-wide`, `--tracking-widest`,
    `--tracking-hero`, `--font-pill`.
  - Borders: `--border-subtle`, `--border-divider`, `--border-metal`,
    `--border-metal-strong`, `--border-cyan`, `--border-error`.
  - Focus: `--focus-ring`.

---

## 3. `docs/design-system.md` — append

Añadir esta sección **al final** del archivo (no reemplazar nada existente):

```markdown
## Pattern Library v2 — `patterns.css`

Desde el PR `feat/pattern-library-v2` el sistema incluye `patterns.css` —
clases drop-in HTML+CSS para los 18 patrones transversales. Cualquier
surface nueva arranca importando `tokens.css` + `patterns.css` en ese
orden y ya queda alineada al sistema.

### Orden de carga canónico

```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800;900&family=Anton&family=JetBrains+Mono:wght@400;600&display=swap">
<link rel="stylesheet" href="/static/design-system/tokens.css?v=2">
<link rel="stylesheet" href="/static/design-system/patterns.css?v=2">
<!-- componentes legacy / compat solo si la surface los necesita -->
<link rel="stylesheet" href="/static/design-system/components.css?v=2">
```

### Recipes por surface

| Surface | Shell | Hero | Patrones | Modal |
|---|---|---|---|---|
| Home Hub | premium | compact | stat-strip, service cards, banners | — |
| Items Browser | plano | compact (ITEMS) | control-panel, tabs, entity-card | item detail |
| Jungle Meta | plano | dual (TIER LIST) | cat-card sidebar, tier-tabs, tier-row | champion detail |
| Meta Scraper | plano | compact | data-table, pill source, toast | row detail |
| Draft Advisor | premium | compact | slot grid, score-factor, top-pick | picker modal |
| Splash Gallery | plano | compact | entity-card grid (full-bleed thumb) | splash full-screen |

### Doc page de referencia

`claude-design-handoff/patrones_diseños_claude_design/Pattern Library.html` —
abrila localmente para ver tokens, demos, snippets y checklist de revisión
pre-merge.
```

---

## 4. `src/riot_lol_cli/draft_advisor/static/design-system/README.md` — patch

Buscar la sección "orden de carga" (o equivalente) y agregar `patterns.css`
**entre** `tokens.css` y `components.css`. Si no existe esa sección,
añadirla siguiendo el formato del resto del README.

---

## 5. `bitacora_de_cambios.md` — append

Agregar una entrada nueva siguiendo el formato del archivo existente. Ejemplo:

```markdown
## YYYY-MM-DD — Pattern Library v2

- ➕ `design-system/patterns.css`: clases drop-in para 18 patrones
  transversales (hero, control-panel, tabs, cards, tier-rows, sidebar
  cat-cards, stat-strip, data-table, modal, estados, draft slots, toasts,
  banners).
- 🔄 `design-system/tokens.css` → v2 canónica. Superset del anterior; sin
  breaking changes.
- 📖 `claude-design-handoff/patrones_diseños_claude_design/Pattern Library.html`:
  doc page de referencia con TOC, demos, snippets y checklist.
- Ref: PR `feat/pattern-library-v2`.
```

---

## 6. Validación

Antes de pushear, correr:

```bash
# 1. Levantar el server
make dev

# 2. Smoke-test cada surface
open http://localhost:8003           # Jungle Meta
open http://localhost:8003/items     # Items Browser
open http://localhost:8003/meta      # Meta Scraper
open http://localhost:8003/draft     # Draft Advisor

# 3. Doc page standalone
open "claude-design-handoff/patrones_diseños_claude_design/Pattern Library.html"
```

**Criterio de aceptación:** todas las surfaces se ven idénticas a antes del
cambio. Doc page abre sin errores de consola.
