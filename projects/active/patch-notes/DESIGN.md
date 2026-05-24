---
version: 1.0
name: LOLCLI Patch Notes — Design System Contract
description: >
  Sistema de diseño y contrato visual del subsistema Patch Notes. Es la fuente
  de verdad reutilizable para que Google Stitch (u otra IA de UI) genere
  propuestas alineadas con el lenguaje Hextech del repo, sin reinventar tokens
  ni patrones. Hereda del design-system canónico que vive en
  `src/riot_lol_cli/draft_advisor/static/design-system/` y se aplica a todas
  las surfaces frontend del paquete `riot_lol_cli`.
audience: League of Legends players (LATAM/ES, gamers competitivos, jungla/draft enjoyers)
platform: web (desktop-first, responsive a tablet/mobile)
language: español (es-AR / es-ES neutro, jerga gamer permitida)
dark_mode_only: true

colors:
  primary: "#c89b3c"          # arc-gold — CTA, headers, focus ring
  primary_bright: "#f0e6d2"   # arc-gold-bright — texto display sobre gold
  primary_dark: "#785a28"     # arc-gold-dark — bordes y sombras pesadas
  secondary: "#0bc6e3"        # arc-cyan — info, metadata, aliados
  secondary_bright: "#0ac8b9" # arc-cyan-bright — highlights
  background: "#010a13"       # forge-black — body bg, fondo profundo
  surface_base: "#0d1b2a"     # surface-base — superficie por defecto
  surface_card: "#0f1923"     # surface-card — cards y panels
  surface_raised: "#1b2838"   # surface-raised — hover, elementos elevados
  surface_overlay: "#1e2d3d"  # surface-overlay — modals, drawers
  text_primary: "#f0e6d2"     # crema — NO blanco puro
  text_secondary: "#a09b8c"   # metadata, helper
  text_tertiary: "#5b5a56"    # placeholders, captions
  text_on_gold: "#010a13"     # texto sobre fondo gold
  state_success: "#00d084"
  state_error: "#ff4655"
  state_warning: "#ff9a3c"
  border_subtle: "rgba(200, 155, 60, 0.12)"
  border_metal: "rgba(200, 155, 60, 0.20)"

typography:
  font_body:
    fontFamily: "Inter, system-ui, -apple-system, sans-serif"
    fallback: "Segoe UI, Roboto, sans-serif"
  font_display:
    fontFamily: "Outfit, Inter, system-ui, sans-serif"
    purpose: "Headings, pills, labels uppercase"
  font_anton:
    fontFamily: "Anton, 'Outfit Black', sans-serif"
    purpose: "Hero titles condensed italic (PATCH NOTES, TIER LIST)"
    style: italic
  font_mono:
    fontFamily: "JetBrains Mono, ui-monospace, Menlo, Consolas, monospace"
    purpose: "Code, timestamps, technical metadata"
  scale:
    hero: "clamp(3rem, 8vw, 6.5rem)"
    display_xl: "2.4rem"
    display_lg: "2rem"
    display_md: "1.5rem"
    display_sm: "1.2rem"
    body_lg: "1.05rem"
    body_md: "1rem"
    body_sm: "0.9rem"
    body_xs: "0.85rem"
    caption: "0.8rem"
    pill: "0.65rem"
  weights:
    regular: 400
    medium: 500
    semibold: 600
    bold: 700
    display: 800
    heavy: 900

spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 24px
  "2xl": 32px
  "3xl": 48px
  "4xl": 64px

rounded:
  xs: 4px
  sm: 6px
  md: 8px
  lg: 12px
  xl: 16px
  pill: 999px

elevation:
  shadow_card: "0 2px 8px rgba(0, 0, 0, 0.4)"
  shadow_raised: "0 8px 24px rgba(0, 0, 0, 0.5)"
  shadow_modal: "0 16px 48px rgba(0, 0, 0, 0.6)"
  glow_gold: "0 0 20px rgba(200, 155, 60, 0.40), 0 0 40px rgba(200, 155, 60, 0.18)"
  glow_cyan: "0 0 24px rgba(11, 198, 227, 0.40), 0 0 48px rgba(11, 198, 227, 0.18)"

motion:
  fast: "120ms ease"
  default: "180ms ease"
  slow: "320ms cubic-bezier(0.4, 0, 0.2, 1)"
  reduce_motion: respected

layout:
  container_max: 1480px
  sidebar_width: 280px
  touch_target_min: 44px
  breakpoints:
    sm: 640px
    md: 768px
    lg: 980px
    xl: 1280px

components:
  hero:
    type: "Diagonal pattern gradient block"
    background: "linear-gradient(135deg, forge-dark → surface-base) + diagonal stripes 45° gold + -45° cyan (variant `hero--dual`)"
    title: "font-anton italic, hero size, gold text-shadow"
    eyebrow: "font-display uppercase, tracking-widest, text-primary"
    purpose: "Página principal de cada vista (overview, detail)"

  patch_card:
    type: "Interactive grid card"
    background: "surface-card"
    border: "1px solid border-subtle"
    radius: "md (8px)"
    padding: "20px"
    hover: "translateY(-2px), border arc-gold-dark, shadow elevation-2 + glow-gold-sm"
    structure:
      header: "[version pill (font-anton gold)] + [date caption]"
      title: "font-display semibold body-md"
      summary: "body-sm secondary, 4-line clamp"
      footer: "[section count meta] + [Ver detalle CTA arc-cyan]"

  pill:
    type: "Badge / chip"
    radius: pill
    padding: "3px 12px"
    font: "font-display, weight-bold, font-pill, tracking-wider, uppercase"
    variants:
      pill-gold: "border + tint arc-gold"
      pill-cyan: "border + tint arc-cyan"
      pill-success: "border + tint state-success"
      pill-error: "border + tint state-error"
      pill-neutral: "border-divider"

  btn_pill:
    type: "Action button"
    radius: pill
    padding: "9px 18px"
    font: "font-display bold uppercase"
    variants:
      btn-pill--gold: "bg arc-gold, text forge-black"
      btn-pill--cyan: "bg rgba(11,198,227,0.08), border cyan, text cyan"

  toc_sidebar:
    type: "Sticky table of contents"
    position: "sticky, top 24px"
    background: "surface-card"
    border: "1px solid border-subtle"
    radius: md
    padding: "16px"
    items:
      level_2: "body-sm, text-secondary, hover text-primary + border-left cyan"
      level_3: "padding-left 18px, body-xs, text-tertiary"

  patch_article:
    type: "Main content area"
    background: "surface-card"
    border: "1px solid border-subtle"
    radius: md
    padding: "32px"
    headings:
      h2: "font-display display-md, color arc-gold, border-bottom divider"
      h3: "font-display display-sm, color arc-cyan"
      h4: "font-display body-lg, color text-primary"
    body: "body-md text-primary, leading-relaxed"

  detail_tabs:
    type: "Tab bar inside detail"
    layout: "horizontal flex, border-bottom divider"
    tab_default: "transparent bg, text-secondary, padding 12px 18px"
    tab_active: "color arc-gold, border-bottom 2px arc-gold"

  champion_heading:
    type: "Visual enrichment block (V2.2)"
    structure: "icon 56x56 + champion name"
    icon:
      source: "https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{championId}.png"
      size: "56x56"
      border: "2px solid arc-gold-dark"
      radius: sm
      shadow: "0 4px 12px rgba(0,0,0,0.3)"
    purpose: "Inyectado en H3 cuando el título matchea un champion canónico (Aatrox, Anivia, etc.)"

  ability_heading:
    type: "Visual enrichment block (V2.2)"
    structure: "ability icon 36x36 + 'Q - Nombre habilidad'"
    icon:
      source: "https://ddragon.leagueoflegends.com/cdn/{version}/img/{spell|passive}/{spellFile}.png"
      size: "36x36"
      border: "1px solid arc-gold-dark"
      radius: xs
    purpose: "Inyectado en H3/H4 que empiezan con 'P -', 'Q -', 'W -', 'E -', 'R -'"

  search_hit:
    type: "Search result card"
    background: "surface-card"
    border: "1px solid border-subtle"
    radius: md
    padding: "16px"
    structure: "[version pill] + [section path] + [snippet con <mark> gold] + [Ver parche CTA]"

  diff_section:
    type: "Diff comparison card"
    background: "surface-card"
    border_left:
      added: "4px solid state-success"
      removed: "4px solid state-error"
      modified: "4px solid arc-gold"
      unchanged: "4px solid border-divider, opacity 0.55"
    columns: "Antes / Después side-by-side, en mobile stack"

  meta_chip_freshness:
    type: "Freshness indicator chip"
    structure: "font-mono caption, pill radius, border + tint según edad"
    variants:
      fresh: "cyan (< 24h)"
      stale: "gold (< 7d)"
      cold: "error (> 7d)"

  scroll_to_top:
    type: "FAB transversal (design-system)"
    position: "fixed bottom-right 24px"
    size: "48x48"
    radius: circle
    background: "arc-gold con border arc-gold-dark"
    shadow: "0 6px 18px rgba(0,0,0,0.45)"
    visibility: "fade-in cuando scrollY > 320px"
    accessibility: "aria-label='Volver arriba'"
    transversal: true
---

## Overview

**Patch Notes Viewer** es la surface del paquete `riot_lol_cli` que muestra las
notas de parche oficiales de League of Legends (fuente canónica
`leagueoflegends.com/es-es/news/tags/patch-notes/`), enriquecidas con análisis
de fuentes comunitarias (U.GG, OP.GG, LoLalytics, Mobalytics) y metadata técnica
(Data Dragon, calendario Riot, dev blog).

**Tono y sensación deseada**

El producto se siente **Hextech**: dark mode oscuro con acentos dorados y cian,
tipografía display condensada italic estilo cartel/poster (Anton), patrones
diagonales sutiles. Es **gamer competitivo** pero no infantil ni cartoon. Es
**denso pero ordenado**: el jugador escanea cambios de balance rápido sin
perderse en floritura visual. La paleta evoca esmalte forjado + cristal mágico,
no neón Twitch.

**Audiencia primaria**

Jugadores de LoL de niveles emerald+ que quieren saber qué cambió en el parche
actual sin tener que leer el changelog completo de Riot. Multi-rol pero con
sesgo hacia **jungla, ADC y soporte** (los proyectos hermanos del repo se
enfocan en esos roles). Hispanohablantes — el contenido es solo `es-es` desde
V2.2.

**Objetivo de negocio**

Convertir el changelog de Riot (texto plano, lectura lineal) en una experiencia
**navegable, buscable, comparable y enriquecida**: lista por parche, detalle con
TOC sticky, vista por fuente (consensus / análisis comunitario), search
full-text, diff entre versiones, iconografía de campeones e items inyectada
desde Data Dragon.

## Colors

**Paleta canónica** — heredada de `tokens.css`. Cualquier nueva surface debe
respetar estos tokens y NO introducir colores nuevos sin agregarlos primero al
sistema.

### Brand / Arc

- **`--arc-gold` (#c89b3c)** — Acción primaria, headers H2, focus ring, CTAs,
  pills "Versión X.Y". Reservar para el elemento más importante de cada pantalla.
  Una sola acción dorada por contexto.
- **`--arc-gold-bright` (#f0e6d2)** — Texto display sobre fondo dorado, también
  como text-primary general.
- **`--arc-gold-dark` (#785a28)** — Bordes pesados, sombras de iconos, separator
  de subsection-group.
- **`--arc-cyan` (#0bc6e3)** — Estado info, metadata, "Fuente oficial" pill,
  Home Hub link, headings H3 (subsecciones dentro de un Campeón).
- **`--arc-cyan-bright` (#0ac8b9)** — Highlights cyan en bordes activos.

### Forge / Surfaces

Capas de superficie ordenadas de más profunda a más elevada:

- **`--forge-black` (#010a13)** — `body` bg, fondo más profundo del producto.
- **`--forge-darker` (#05101c)** — Inputs deprimidos, tablas, `<pre>` blocks.
- **`--forge-dark` (#0a1428)** — Origen del gradient del hero.
- **`--surface-base` (#0d1b2a)** — Superficie por defecto, fin del hero gradient.
- **`--surface-card` (#0f1923)** — Cards, panels, TOC sidebar.
- **`--surface-raised` (#1b2838)** — Hover state, elementos elevados.
- **`--surface-overlay` (#1e2d3d)** — Modals, drawers, popovers.

### Texto

- **`--text-primary` (#f0e6d2)** — Texto principal. **NO usar blanco puro
  (#ffffff)** — siempre crema. El blanco rompe el vibe Hextech.
- **`--text-secondary` (#a09b8c)** — Metadata, helper copy, descripciones secundarias.
- **`--text-tertiary` (#5b5a56)** — Placeholders, captions menores.
- **`--text-on-gold` (#010a13)** — Texto negro forge sobre fondo gold (botones primarios).

### Estado

Uso semántico estricto:

- **`--state-success` (#00d084)** — Diff "added", health checks online,
  enrichment OK, "valid" en source registry.
- **`--state-error` (#ff4655)** — Diff "removed", scrape error, banneo,
  "scraper_available: false".
- **`--state-warning` (#ff9a3c)** — Deprecated, freshness "stale".

### Freshness Chips (V2 pattern transversal)

- **Fresh** (< 24h): cyan — manifest fresco.
- **Stale** (< 7d): gold — necesita refresh pronto.
- **Cold** (> 7d): error — outdated, recomienda re-scrape.

## Typography

**Tres familias, jerarquía estricta.**

### Familias

- **`--font-body` (Inter)** — Body copy, párrafos, search snippets, descripciones.
  Excelente legibilidad en pantalla, soporta tabular figures.
- **`--font-display` (Outfit)** — Headings (excepto hero), pills, labels uppercase
  con `tracking-wider`, botones, navegación. Geométrico, moderno, tech.
- **`--font-anton`** — Solo para **hero titles**: "PATCH NOTES", "TIER LIST",
  "NOTAS DE LA VERSIÓN 26.10", versiones grandes en patch cards. Italic,
  condensed, agresivo — evoca cartel de cine / poster de torneo.
- **`--font-mono` (JetBrains Mono)** — Code blocks (payload de enrichments),
  timestamps, hashes, IDs técnicos.

### Escala (clamp en hero, fijos en el resto)

```
hero        clamp(3rem, 8vw, 6.5rem)   PATCH NOTES, hero versión
display-xl  2.4rem                      Patch title en detail-hero
display-lg  2rem                         Versión en patch-card
display-md  1.5rem                       H2 sección (Campeones, Objetos)
display-sm  1.2rem                       H3 subsección (Aatrox, Anivia)
body-lg     1.05rem                      H4, lead paragraphs
body-md     1rem                          Body text
body-sm     0.9rem                        Cards summary, TOC items
caption     0.8rem                        Dates, meta info
pill        0.65rem                       Pills uppercase tracking-wider
```

### Reglas tipográficas

- **Hero** = Anton italic, text-shadow gold, letter-spacing tight-hero.
- **H2** = Outfit display-md weight-display, color arc-gold, border-bottom divider.
- **H3** = Outfit display-sm weight-bold, color arc-cyan, scroll-margin-top space-6.
- **H4** = Outfit body-lg weight-semibold, color text-primary.
- Máximo **dos pesos por pantalla** además del hero. Si una sección necesita
  3+ pesos, falló la jerarquía.
- Microtexto uppercase = tracking-wider (0.08em) o tracking-widest (0.12em).
- Lowercase texto = tracking-normal.

## Layout

**Desktop-first, responsive a tablet (768) y mobile (640).**

### Containers

- Container principal: `max-width: 1480px`, padding `space-6` (24px).
- Sidebar TOC: `width: 280px`, sticky con `top: 24px`, max-height `calc(100vh - 96px)`.
- Touch target mínimo: **44x44px** (botones, pills clickeables, FAB).

### Hero

Ocupa el alto natural de su contenido (NO full-viewport). Estructura típica:

```
┌─────────────────────────────────────────────────┐
│ EYEBROW (uppercase)        [Home Hub] [N PARCHES]│
│                                                  │
│             PATCH NOTES                          │  ← anton italic gigante
│         Multi-source · análisis                  │  ← subtitle text-secondary
│                                                  │
│    [📜icon]  | FUENTE OFICIAL                    │
│              Último parche: 26.10                │
│              [meta-chip freshness]               │
└─────────────────────────────────────────────────┘
```

### Overview

```
[hero]
[control-panel: search bar (cyan submit)]
[patches-grid: cards 320px min, auto-fill, gap 20px]
  └─ 3 cols desktop, 2 cols tablet, 1 col mobile
```

### Detail

```
[detail-hero: back-link + home-link + pills + title + summary]
[detail-tabs: Notas oficiales | Por fuente]
[tab-panel "official":
  ┌─────────┬────────────────────────────────────┐
  │   TOC   │  patch-article                     │
  │ sticky  │  ├─ H2 "Los platos fuertes"        │
  │ 280px   │  ├─ H2 "Campeones"                 │
  │         │  │   ├─ [icon] H3 Ambessa          │
  │         │  │   │   ├─ [icon] Q - Habilidad   │
  │         │  │   │   └─ blocks                 │
  │         │  │   └─ [icon] H3 Anivia           │
  │         │  └─ H2 "Objetos"                   │
  └─────────┴────────────────────────────────────┘
]
```

Mobile (≤980px): TOC pasa a flujo lineal, no sticky.

### Search

```
[hero compact: back-link + pills "30 resultados" + título "QUERY"]
[search-input + Buscar]
[search-list:
  ├─ search-hit card
  │   ├─ [version pill] [locale pill] [section path]
  │   ├─ snippet con <mark> highlight gold
  │   └─ [Ver parche → CTA gold]
  └─ ...
]
```

### Diff

```
[hero compact: pills A vs B + summary "+54 / -110 / ~19"]
[legend: added/removed/modified/unchanged chips]
[diff-grid:
  ├─ diff-section card (border-left color-coded)
  │   ├─ [badge change_type] H2 título
  │   ├─ columns: Antes (rojo) | Después (verde)
  │   └─ sub_diffs nested
  └─ ...
]
```

## Elevation & Depth

**5 niveles de profundidad** — usar el mínimo necesario, no apilar sombras.

1. **Plano** (forge-black): body bg, sin sombra.
2. **Card** (`shadow-card`): cards, panels en reposo.
3. **Raised** (`shadow-raised`): hover de cards interactivas.
4. **Modal** (`shadow-modal`): drawers, popovers.
5. **Glow signature**: solo en CTAs primarios o estados activos
   (`glow-gold`, `glow-cyan`). NO usar glow como decoración, solo como señal.

**Patrones diagonales** (no shadows):

El hero usa `repeating-linear-gradient` a 45° con líneas gold 1px cada 60px,
opacidad 0.04. Variant `hero--dual` agrega un segundo set a -45° en cyan 0.03.
Esto crea textura "esmalte forjado" sin saturar.

## Shapes

Bordes y radios con propósito jerárquico:

- **Pills** (`--radius-pill`, 999px): versión, estado, fuente.
- **Cards** (`--radius-md`, 8px): patch cards, source cards, search hits.
- **Inputs / botones inline** (`--radius-sm`, 6px): search input, select.
- **Champion icons** (`--radius-sm`): cuadrados con esquinas redondeadas
  evocando el client de LoL.
- **Ability icons** (`--radius-xs`, 4px): cuadrados más pequeños, esquina mínima.
- **Hero** (`--radius-lg`, 12px): contenedor grande.

**Bordes**:

- `--border-subtle` (gold @ 12%) — separadores en surface-card.
- `--border-metal` (gold @ 20%) — bordes activos.
- `--border-cyan` / `--border-error` / `--border-success` — para pills semánticas.
- `--border-divider` (#1f2937) — separadores neutrales (border-bottom de H2).

## Components

### Hero

Bloque firma. Uso obligatorio en overview y detail (variant `--compact` en
search/diff).

- Background: gradient 135deg forge-dark → surface-base + patrón diagonal.
- Variant `hero--dual`: doble patrón gold + cyan.
- Title: `font-anton` italic, `font-hero`, text-shadow gold 24px blur.
- Eyebrow + acciones a izquierda y derecha del row superior.

### Patch Card

Card interactiva grande para el grid de overview. Hover eleva 2px + glow gold.

```html
<article class="patch-card" tabindex="0">
  <header class="patch-card-header">
    <div class="patch-card-version">26.10</div>
    <div class="patch-card-date">12 DE MAY DE 2026</div>
  </header>
  <div class="patch-card-title">Notas de la versión 26.10</div>
  <div class="patch-card-summary">Ivern chamán de la lluvia y PROYECTO: Quinn…</div>
  <footer class="patch-card-footer">
    <div class="patch-card-meta">14 secciones · es-es</div>
    <div class="patch-card-cta">Ver detalle →</div>
  </footer>
</article>
```

### Pills

Inline-flex, padding 3px 12px, radius-pill, font-pill uppercase. Variantes:
`pill-gold`, `pill-cyan`, `pill-success`, `pill-error`, `pill-neutral`.

### TOC Sidebar

Sticky `top: 24px`, surface-card, padding 16px. Items level-2 con border-left
2px transparent → arc-cyan en hover. Item active tiene background tint gold +
border-left arc-gold.

### Detail Tabs

Flex row, border-bottom divider. Tabs default text-secondary, active color
arc-gold + border-bottom 2px arc-gold. Cambio sin recargar — panels con `hidden`.

### Visual Enrichment (V2.2)

Champion + ability headings se inyectan post-render desde Data Dragon. Match
por nombre normalizado contra `champion.json` de DDragon CDN.

### Scroll-to-top (FAB transversal)

Botón circular dorado bottom-right, aparece al scrollear > 320px. Pattern del
design system canónico (`/design-system/scroll-to-top.js`) — debe estar en
**todas las surfaces del repo**.

## Do's and Don'ts

### Do

- **Do** usar `--arc-gold` solo para la acción más importante por pantalla.
- **Do** mantener jerarquía estricta H1 (Anton) → H2 (Outfit display-md gold)
  → H3 (Outfit display-sm cyan) → H4 (Outfit body-lg primary).
- **Do** preservar contraste WCAG AA en todo texto (`text-primary` sobre
  `surface-card` ≈ 12.5:1).
- **Do** usar `text-primary` (crema #f0e6d2) — **nunca blanco puro**.
- **Do** respetar `prefers-reduced-motion`: las transiciones bajan a 0.01ms.
- **Do** invocar `window.LOLCLI_ScrollToTop.refresh()` después de re-render
  en SPAs con hash router (las vistas que reemplazan `#app`).
- **Do** inyectar champion icons via Data Dragon CDN — match por nombre
  normalizado contra `champion.json`.
- **Do** mostrar la freshness chip (cyan/gold/error) cuando hay un
  `last_scrape` timestamp visible.
- **Do** usar microcopy en **español rioplatense con jerga gamer** clara
  (ADC, draft, gank, peel, roam, scaling).
- **Do** mostrar 4-line clamp en card summaries — el patch tiene mucho texto.

### Don't

- **Don't** introducir colores nuevos sin agregarlos a `tokens.css` primero.
- **Don't** usar más de **dos font weights** en una pantalla (además de Anton).
- **Don't** crear **múltiples acciones doradas que compitan** en la misma vista
  (overview puede tener "Buscar" cyan, pero "Ver detalle →" dorado es una sola
  por card).
- **Don't** usar shadows decorativos. Solo elevación funcional.
- **Don't** usar gradients chillones tipo Twitch/neon. El brillo del producto
  viene del **glow-gold** sobre el dark + tipografía Anton, no de saturación.
- **Don't** romper el dark mode — el producto **no tiene light mode**, no asumir
  que puede agregarse sin redefinir todo.
- **Don't** scrapear ni mostrar contenido de otros locales (es-mx, en-us) —
  desde V2.2 la fuente de verdad es solo **es-es** del sitio oficial de Riot.
- **Don't** usar emojis decorativos en headings. Los emojis (📜 📡 🌐) están
  reservados a los tabs principales.
- **Don't** insertar imágenes pesadas inline si DDragon ya tiene el icon.
  Lazy-load (`loading="lazy"`) en cualquier `<img>` external.
- **Don't** usar texto en MAYÚSCULAS sin `tracking-wider` o `tracking-widest`
  — queda apretado y rompe la legibilidad.
- **Don't** centrar texto en bloques largos. Centrado solo para hero / titles.

## Prompting Stitch — recetas para esta surface

Pattern recomendado por la guía Stitch (cf. `Google_Stitch_DESIGNmd_Guia.pdf`):
**un cambio fuerte por prompt, decir qué proteger, usar data mock realista**.

### Prompt para nueva pantalla (ej: vista de "Campeón individual")

```text
Use the attached DESIGN.md as the source of truth.

Create a web screen for LOLCLI Patch Notes.

User:
LoL emerald+ player who wants to see all changes for a specific champion
across multiple patches.

Context:
Reached from clicking a champion icon inside a patch detail.

Primary goal:
Show the history of buffs/nerfs for one champion across patches.

Primary action:
Filter or jump to a specific patch.

Layout:
- Hero compact with [back link] + [champion icon 90x90 detail-portrait]
  + champion display name + tier badge si está disponible.
- Timeline vertical de patch entries, cada uno con: version pill gold,
  date pill neutral, list of ability/item changes.
- Optional sidebar derecho con "estadísticas DDragon" (HP, AD, attack range)
  desde versions.json correspondiente.

Visual direction:
Hextech dark, gold/cyan, font-anton hero, dense pero ordenado, Riot-poster
energy. NO neon, NO cartoon.

Mock content (real Riot data):
- Ambessa Q "Barrido artero" — Daño por vida máxima: 2/3/4/5/6% → 4/4.5/5/5.5/6%
- Ambessa R "Ajusticiar" — Porcentaje de curación: 10/12.5/15% → 15/17.5/20%

Constraints:
- Use only existing tokens from this DESIGN.md.
- Do not introduce new colors.
- Preserve dark mode (forge-black background).
- Spanish copy (es-AR), gamer jargon allowed.
- Champion icons from Data Dragon CDN.
- Mobile: stack timeline, hide sidebar.

Output:
Generate only this screen, in plain HTML+CSS+vanilla JS compatible
with the existing /design-system mounts.
```

### Prompt para refinar sin romper

```text
Keep the existing visual style, hero, tabs and TOC.

Only modify the "Por fuente" tab inside detail:
- Add a top filter row with chips: [Riot Oficial] [DDragon] [Comunidad].
- Filtering hides the corresponding source cards in the accordion below.

Do not modify: tokens, hero, official tab, search, diff views, scroll-to-top.
Preserve typography and spacing from the design system.
```

### Prompt para pedir consistencia

```text
Use DESIGN.md from projects/active/patch-notes/ as the source of truth.

Follow its color, typography, spacing, radius and component rules.
Do not introduce new tokens unless absolutely necessary.

If a new pattern is needed:
- Reuse arc-gold for primary actions (one per screen).
- Reuse arc-cyan for info/metadata.
- Reuse surface-card for panels.
- Use font-anton ONLY for hero titles.
- Respect 44px touch target minimum.
- Respect dark mode (no white backgrounds).
```

## Referencias y fuentes

- **Design system canónico**:
  - `src/riot_lol_cli/draft_advisor/static/design-system/tokens.css` — fuente de verdad de todos los tokens.
  - `src/riot_lol_cli/draft_advisor/static/design-system/components.css` — `.pill`, `.btn-pill`, `.card`, `.scroll-to-top`.
  - `src/riot_lol_cli/draft_advisor/static/design-system/patterns.css` — `.hero`, `.control-panel`, `.home-hub-link`.
- **Surfaces que aplican este sistema**:
  - Home Hub (`src/riot_lol_cli/home/`).
  - Draft Advisor (`src/riot_lol_cli/draft_advisor/`).
  - Jungle Meta (`src/riot_lol_cli/jungle_meta/`).
  - Items Browser (`src/riot_lol_cli/items_browser/`).
  - Meta Scraper dashboard (`src/riot_lol_cli/meta_scraper/static/`).
  - Patch Notes (este proyecto).
- **Material design adicional**:
  - `claude-design-handoff/` — referencias y notas de producto.
  - `claude-design-handoff_revolution/` — versión 2 del handoff con pattern library.
- **Documentación operativa**:
  - `projects/active/patch-notes/deep-research-report.md` — fundamento del scraping multi-source.
  - `projects/active/patch-notes/Google_Stitch_DESIGNmd_Guia.pdf` — guía de prompting para Stitch.
  - `AGENTS.md` § Design System y Frontend — reglas transversales para agentes.

## Versionado del DESIGN.md

- **1.0 (2026-05-15)** — Captura inicial post-V2.2 (multi-source + español-only
  + scroll-to-top transversal + visual enrichment champion/ability icons).

Actualizar `version:` cuando se agreguen tokens nuevos o se cambien reglas de
uso. La frontmatter YAML es leída por Stitch como tokens; el cuerpo markdown
es para humanos y agentes que necesitan contexto narrativo.
