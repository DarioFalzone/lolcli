# CONTEXT.md — Memoria de proyecto Pattern Library v2

Resumen condensado de lo que Cloud Claude exploró y decidió mientras
diseñaba la Pattern Library v2. Sirve para que tu Claude local arranque
con el mismo criterio sin re-explicar todo desde cero.

---

## 1. Estado actual del repo (snapshot)

- **5 surfaces activas** con CSS propio:
  - `home/` — Home Hub (premium shell, gradient ambient).
  - `items_browser/` — Items Browser (catálogo plano, hero "ITEMS").
  - `jungle_meta/` — Jungle Meta tier list (hero dual con role icon).
  - `meta_scraper/` — Meta Scraper (tablas densas, source badges).
  - `draft_advisor/` — Draft Advisor SPA (premium shell, picker grid).
- **Design-system** vive en `src/riot_lol_cli/draft_advisor/static/design-system/`
  con `tokens.css`, `components.css`, `compat-spa.css`, `compat-dashboard.css`.
- **Docs** en `docs/design-system.md` + bitácora en `bitacora_de_cambios.md`.

## 2. Diagnóstico (lo que detectamos)

- **3 golds distintos** entre surfaces: `#c89b3c` (canónico), `#d4af37`,
  `#c8aa6e`. Items y Jungle redefinían `:root` con su propia paleta.
- **2 cyans distintos**: `#0bc6e3` vs `#0ac8b9`.
- **Componentes duplicados**: search input, tabs, cards, modal estaban
  reimplementados 4 veces con leves variaciones (padding, radius, border).
- **Hero inconsistente**: Items usaba shell plano, Jungle premium, ambos
  con la misma intención visual (hero compacto Anton italic).
- **Tipografía mezclada**: Anton se usaba bien en hero, pero Outfit/Inter
  se intercambiaban sin regla clara.

## 3. Decisiones tomadas

| Decisión | Por qué |
|---|---|
| **Una sola `tokens.css` canónica** (v2 = superset del actual) | Eliminar las 3 golds y las 2 cyans. Cualquier nuevo surface importa esto y listo. |
| **`patterns.css` nuevo, drop-in HTML+CSS plain** | Sin React, sin bundlers — alineado con el resto del repo (vanilla). |
| **Anton italic SOLO para hero / tier label** | Es la firma visual. Si se usa en cards y CTAs, pierde fuerza. |
| **Outfit 700-800 caps para eyebrows / card titles** | Tracking widest, contrasta con body Inter. |
| **Inter 400 para body** | Legibilidad alta en densidad de tablas y descripciones. |
| **JetBrains Mono + tabular-nums** para todo número | WR / PR / gold cost / scores. Alineación vertical en tablas. |
| **Dos shells canónicos: premium vs plano** | Premium (Home, Draft) tiene gradient radial sutil; plano (Items, Jungle, Meta Scraper) es navy plano. No hay tercera variante. |
| **Glow gold/cyan reservado a CTA primario, focus y top-pick** | "Si todo brilla, nada brilla." |
| **Tier S/A/B/C como tokens semánticos** (`--tier-s` cream, `--tier-a` cyan, `--tier-b` neutral, `--tier-c` red) | Colorea solo el `.active`, no toda la pill. |
| **`prefers-reduced-motion` respetado en `patterns.css`** | A11y mínima. |
| **Voz: español rioplatense + jerga gamer EN** | "Recomendar Pick", "blind pick", "peel", "scaling". No traducir términos universales. |

## 4. Cosas que descartamos (y por qué)

- **Tailwind / utility CSS** — repo es vanilla, sumar build step rompe
  el flujo de export HTML. Patterns.css usa custom props + clases
  semánticas, mucho más editable inline.
- **Iconografía custom SVG inline** — yo dejé placeholders. Cuando haya
  que poblarla, viene de DDragon o lucide-via-`<link>`, NO inventada por
  Claude.
- **Hero a pantalla completa con slogan** — descartado: esto son
  herramientas de uso repetido, no landing page.
- **Gradient en cada card** — descartado: ruido visual, no agrega info.
- **Border-left accent + rounded corner** como contenedor genérico —
  descartado por ser "AI slop trope". Solo se usa en `cat-card` con
  motivo semántico (cyan = info, gold = signal, error = ban).
- **Spinner infinito sin fallback** — descartado. Todo loading → skeleton.
  Todo error → bloque rojo con copy + reintentar.
- **Variantes "magic" / "special" de boton** — descartado. Si no es
  primary / secondary / ghost / icon, repensar el problema.

## 5. Roadmap de PRs

| PR | Scope | Estado |
|---|---|---|
| **#0 Pattern Library v2** | Add `patterns.css` + tokens v2 + doc page | **Esta PR** |
| #1 Migración Items + Jungle a tokens compartidos | Eliminar `:root` local en Items y Jungle | Próximo |
| #2 Migración Home + Meta Scraper a `patterns.css` | Reemplazar clases custom por `.hero`, `.control-panel`, `.tabs`, `.tier-row` | Después de #1 |
| #3 Draft Advisor SPA — alinear nombres | Renombrar clases SPA donde aplique sin tocar lógica | Después de #2 |
| #4 Deprecar `compat-spa.css` y `compat-dashboard.css` | Sync `docs/design-system.md` final | Cierre |

## 6. Cosas a las que prestar atención si seguís diseñando

- **Cualquier surface nueva** importa `tokens.css` + `patterns.css` en
  ese orden. NO redefinir `:root` con paleta local.
- **Densidad sobre marketing**: las herramientas se usan repetido, no se
  miran 1 vez. Score, contexto y razones tienen que escanearse en 2 seg.
- **Hover lift de 2px, transition 120-180ms**: anima estados, no decoración.
- **Hit target mínimo 44px** en mobile. Foco gold con `--focus-ring` en
  todo elemento navegable.
- **Texto crema, no blanco puro** (`#f0e6d2` vía `--text-primary`).
- **Numeros siempre tabular-nums + JetBrains Mono o Outfit 700**.
- Si dudás de algo, abrí `Pattern Library.html` antes de improvisar —
  probablemente ya está resuelto ahí.

## 7. Archivos que tu Claude local debería leer ANTES de iterar

1. `pattern-library-prompt.md` (raíz del repo) — visión original.
2. `claude-design-handoff/patrones_diseños_claude_design/Pattern Library.html` —
   doc page navegable. Tokens, demos, anti-patterns, checklist.
3. `src/riot_lol_cli/draft_advisor/static/design-system/tokens.css` —
   variables canónicas.
4. `src/riot_lol_cli/draft_advisor/static/design-system/patterns.css` —
   componentes drop-in.
5. `src/riot_lol_cli/draft_advisor/static/design-system/README.md` —
   orden de carga.
6. `docs/design-system.md` — estado documental.
7. `bitacora_de_cambios.md` — historial.

Las surfaces (`src/riot_lol_cli/*/static/`) se leen on-demand cuando se
las vaya a tocar, no upfront.
