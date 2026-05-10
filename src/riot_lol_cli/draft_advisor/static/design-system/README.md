# Design System — riot_lol_cli

CSS canónico compartido por todas las surfaces del repo (Home Hub, Draft
Advisor, Meta Scraper, Jungle Meta, Items Browser, etc.).

## Orden de carga

```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800;900&family=Anton&family=JetBrains+Mono:wght@400;600&display=swap">
<link rel="stylesheet" href="/static/design-system/tokens.css?v=2">
<link rel="stylesheet" href="/static/design-system/patterns.css?v=2">
<!-- componentes legacy / compat solo si la surface los necesita -->
<link rel="stylesheet" href="/static/design-system/components.css?v=2">
```

1. **`tokens.css`** — variables canónicas (colores, tipografía, spacing, motion).
2. **`patterns.css`** — 18 patrones drop-in HTML+CSS vanilla.
3. **`components.css`** — componentes legacy con clases custom (en deprecación gradual).
4. **`compat-spa.css`** o **`compat-dashboard.css`** — adapters para surfaces preexistentes.

## Archivos

| Archivo | Tamaño | Propósito |
|---|---|---|
| `tokens.css` | ~7 KB | Fuente única de verdad para tokens (v2 canónica). |
| `patterns.css` | ~28 KB | Clases drop-in: `.hero`, `.control-panel`, `.tabs`, `.tier-row`, `.cat-card`, `.stat-strip`, `.data-table`, `.modal`, `.btn`, `.entity-card`, etc. |
| `components.css` | ~17 KB | Componentes legacy. Surfaces nuevas no deberían importarlo. |
| `compat-spa.css` | ~3 KB | Adapter para Draft Advisor SPA. |
| `compat-dashboard.css` | ~2 KB | Adapter para Meta Analyzer dashboard. |

## Doc page de referencia

`claude-design-handoff_revolution/patrones_diseños_claude_design/Pattern Library.html`
— abrir en browser para ver tokens visualizados, demos de cada patrón,
snippets copy-pasteable y checklist pre-merge.

## Cómo agregar una surface nueva

1. Importá `tokens.css` + `patterns.css` (en ese orden).
2. **No redefinas `:root`** con paleta local — usá los tokens existentes.
3. Componé la UI con clases de `patterns.css` (hero, control-panel, etc.).
4. Si necesitás un componente que no está en `patterns.css`, abrí la doc page
   de referencia primero — probablemente ya está resuelto.
