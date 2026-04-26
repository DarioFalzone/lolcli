# Design System — riot_lol_cli

> Extraído del código real del repositorio. Cuando un dato no está claro, se marca `[A confirmar]`.

## ⚠️ Aviso: hay 3 paletas de tokens en uso

El proyecto tiene **3 surfaces de UI** con paletas distintas pero la misma **identidad visual ("Hextech meets dark UI")**:

| Surface | Path | Tokens prefix | Tipografía | Estado |
|---------|------|---------------|------------|--------|
| **Draft Advisor SPA** | `src/riot_lol_cli/draft_advisor/static/styles.css` | sin prefijo (`--gold`, `--blue`) | Inter + Outfit | Actual / V2 |
| **Match History Export** | `templates/claude-4-5.html` (inline `<style>`) | `--hextech-*` / `--piltover-*` | Spiegel | Más extensa / canónica |
| **Splash Viewer** | `templates/splash-viewer.html` (inline `<style>` minified) | `--hextech-*` / `--piltover-*` | Spiegel | Comparte tokens con Match History |
| Dashboard Meta | `src/riot_lol_cli/dashboard_enhanced.py` (HTML embebido) | `--primary`, `--secondary`, `--accent` | Segoe UI | Genérica/legacy |

**Recomendación para Claude Design**: Adoptar como **canónica la paleta de `templates/claude-4-5.html`** (es la más extensa y semánticamente nombrada con `--hextech-*` y `--piltover-*`). El SPA del Draft Advisor es una traducción simplificada de los mismos colores.

---

## 1. Paleta de Colores

### 1.1 Paleta canónica (Hextech / Piltover)

Fuente: [`templates/claude-4-5.html:11-60`](../templates/claude-4-5.html#L11-L60)

#### Acentos primarios (Gold — uso jerárquico, CTAs principales)
| Token | Hex | Uso semántico |
|-------|-----|---------------|
| `--hextech-gold` | `#c89b3c` | **primary accent** — labels destacados, scores, badges |
| `--hextech-gold-bright` | `#f0e6d2` | **primary text on dark** — headings principales |
| `--hextech-gold-dark` | `#785a28` | **primary muted** — bordes, hover dim |
| `--hextech-gold-accent` | `#c8aa6e` | **primary subtle** — variante intermedia |

#### Acentos secundarios (Blue — interactividad, info)
| Token | Hex | Uso semántico |
|-------|-----|---------------|
| `--hextech-blue` | `#0bc6e3` | **secondary** — info, links, glow effects |
| `--hextech-blue-dark` | `#0397ab` | **secondary muted** |
| `--hextech-blue-bright` | `#0ac8b9` | **secondary alt** — usado en SPA Draft Advisor como `--blue` |

#### Surfaces (Dark / Piltover)
| Token | Hex | Uso semántico |
|-------|-----|---------------|
| `--piltover-black` | `#010a13` | **background-base** — el más oscuro, body |
| `--piltover-dark` | `#0a1428` | **background-1** — gradient stop |
| `--piltover-darker` | `#05101c` | **background-deep** — capas internas |
| `--surface-base` | `#0d1b2a` | **surface-base** |
| `--surface-raised` | `#1b2838` | **surface-raised** — cards, headers |
| `--surface-overlay` | `#1e2d3d` | **surface-overlay** — modales |
| `--surface-card` | `#0f1923` | **surface-card** — fondo de cards individuales |

#### Texto
| Token | Hex | Uso semántico |
|-------|-----|---------------|
| `--text-primary` | `#f0e6d2` | **text-default** — cuerpo principal (color crema, no blanco puro) |
| `--text-secondary` | `#a09b8c` | **text-secondary** — labels, subtítulos |
| `--text-tertiary` | `#5b5a56` | **text-tertiary** — placeholders |
| `--text-muted` | `#3c3c41` | **text-muted** — disabled |

#### Semánticos (estado / feedback)
| Token | Hex | Uso semántico |
|-------|-----|---------------|
| `--magic-glow` | `#0bc6e3` | **info** — alias de hextech-blue |
| `--victory` | `#00d084` | **success** — wins, positivos |
| `--victory-dark` | `#00aa6a` | **success-dim** |
| `--defeat` | `#ff4655` | **error / danger** — losses, riesgos |
| `--defeat-dark` | `#d13639` | **error-dim** |
| `--remake` | `#8b9cb3` | **neutral** — partidas remake |

> En el SPA Draft Advisor, los nombres equivalentes son: `--green: #2dcc70` (success), `--orange: #ff9a3c` (warning), `--red: #ff4655` (error), `--purple: #7b61ff` (decoración). [A confirmar] si se mantiene `--purple` en el sistema oficial — solo aparece declarado, no se ve en uso intensivo.

### 1.2 Bordes (rgba con opacidad)

Fuente: [`templates/claude-4-5.html:46-52`](../templates/claude-4-5.html#L46-L52) y [`styles.css:43-49`](../src/riot_lol_cli/draft_advisor/static/styles.css#L43-L49)

| Token | Valor | Uso |
|-------|-------|-----|
| `--border-metal` | `rgba(200,155,60,0.2)` | Borde gold sutil (default) |
| `--border-metal-strong` | `rgba(200,155,60,0.4)` | Borde gold marcado (hover, focus) |
| `--border-blue` | `rgba(11,198,227,0.3)` | Borde info / secondary |
| `--border` (SPA) | `#1f2937` | Borde gris sutil |
| `--glass-border` | `rgba(200, 155, 60, 0.15)` | Borde sobre glassmorphism |

### 1.3 Tabla rápida — mapeo a roles semánticos universales

| Rol semántico | Token canónico | Hex |
|---------------|----------------|-----|
| Primary | `--hextech-gold` | `#c89b3c` |
| Primary (text on dark) | `--hextech-gold-bright` | `#f0e6d2` |
| Secondary / Info | `--hextech-blue` | `#0bc6e3` |
| Background base | `--piltover-black` | `#010a13` |
| Surface | `--surface-card` | `#0f1923` |
| Border default | `--border-metal` | `rgba(200,155,60,0.2)` |
| Text primary | `--text-primary` | `#f0e6d2` |
| Text secondary | `--text-secondary` | `#a09b8c` |
| Success | `--victory` | `#00d084` |
| Error | `--defeat` | `#ff4655` |
| Warning | `--warning` (dashboard) o `--orange` (SPA) | `#ff9900` / `#ff9a3c` |

---

## 2. Tipografía

### 2.1 Familias

Fuente: [`templates/claude-4-5.html:9`](../templates/claude-4-5.html#L9), [`styles.css:8`](../src/riot_lol_cli/draft_advisor/static/styles.css#L8)

| Familia | Cargada en | Uso |
|---------|-----------|-----|
| **Spiegel** (Google Fonts) | claude-4-5, splash-viewer | **Match History + Splash Viewer** — fuente oficial de Riot Games |
| **Inter** (Google Fonts) | Draft Advisor SPA (body) | **Body text, párrafos, controles** |
| **Outfit** (Google Fonts) | Draft Advisor SPA (display) | **Headings, números grandes, titulares** |
| **Segoe UI** (system font stack) | dashboard_enhanced (legacy) | Solo en dashboard antiguo. [A migrar] |

**Stacks completos:**

```css
/* claude-4-5 + splash-viewer (canónico) */
font-family: 'Spiegel', -apple-system, BlinkMacSystemFont, "SF Pro Display",
             "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;

/* Draft Advisor SPA */
font-family: 'Inter', system-ui, -apple-system, sans-serif;       /* body */
font-family: 'Outfit', sans-serif;                                /* headings */
```

**Recomendación**: Para Claude Design, definir **dos familias**:
- **Display** = `Outfit` (más moderno, geométrico) o `Spiegel` (auténtico LoL).
- **Body** = `Inter` (legibilidad superior para datos densos).

### 2.2 Pesos (font-weight)

| Peso | Donde se usa |
|------|--------------|
| `300` | (definido en Inter pero no se ve en uso intensivo) |
| `400` | body por defecto |
| `500` | controls secundarios, labels |
| `600` | botones, cells de tabla, controls primarios |
| `700` | nombres de campeones, headings de cards (h2, h3) |
| `800` | display headings (h1) |
| `900` | display extra-bold — versiones, badges, números grandes |

### 2.3 Tamaños (font-size)

Sistema **basado en `rem` con base de 15px** (no 16px) en SPA Draft Advisor:

```css
html { font-size: 15px; }   /* SPA */
```

| Token (sugerido) | rem | px (SPA base 15) | Uso |
|------------------|-----|------------------|-----|
| `--font-display-xl` | 2.4rem | 36px | Score grande (top pick) |
| `--font-display-lg` | 2.2rem | 33px | h1 header |
| `--font-display-md` | 1.8rem | 27px | top-pick name |
| `--font-display-sm` | 1.2rem | 18px | alt-score |
| `--font-body-lg` | 1.05rem | 16px | recommend-btn |
| `--font-body-md` | 1rem | 15px | body, alt-name |
| `--font-body-sm` | 0.9rem | 13.5px | subtitle, modal input, context-group select |
| `--font-body-xs` | 0.85rem | 12.75px | context-group select alternate |
| `--font-caption` | 0.8rem | 12px | explanation li, alt-reason |
| `--font-caption-sm` | 0.75rem | 11.25px | team-label, modal, role-filter |
| `--font-micro` | 0.7rem | 10.5px | context-group label |
| `--font-pill` | 0.65rem | ~10px | score-label, draft-summary label |
| `--font-tiny` | 0.6rem | 9px | slot-name, .name en grid |

**Tamaños fijos (px)** en match-history y splash-viewer:
- 12px — micro labels, badges
- 13px — body small
- 14px — body default, hotkey-btn
- 16px — body large
- 20px — sub-headings
- 24px — section titles
- 28px — logo, h1
- 32px — hotkey overlay header

### 2.4 Line height

Fuente: [`templates/claude-4-5.html:74`](../templates/claude-4-5.html#L74)

```css
body { line-height: 1.6; }       /* canónico — match history y splash viewer */
.explanation li { line-height: 1.4; }
.alt-reason   { line-height: 1.4; }
.pattern-text { line-height: 1.5; }
```

**Sugerencia para tokens**:
- `--leading-tight` = 1.2 (display headings)
- `--leading-snug` = 1.4 (listas, captions)
- `--leading-normal` = 1.5 (cuerpo de texto)
- `--leading-relaxed` = 1.6 (body principal)

### 2.5 Letter-spacing

Letras espaciadas para **labels en mayúscula** (cualidad de UI militar/sci-fi):

```css
letter-spacing: -0.03em;   /* h1 display tight */
letter-spacing: -0.02em;   /* top-pick-name */
letter-spacing: 0.02em;    /* recommend-btn */
letter-spacing: 0.05em;    /* explanation h4 (caps) */
letter-spacing: 0.08em;    /* draft-summary label */
letter-spacing: 0.1em;     /* team-label, score-label, top-pick-label */
letter-spacing: 1px;       /* logo splash viewer */
letter-spacing: 2px;       /* hotkeys-header overlay */
```

---

## 3. Espaciado y Grid

### 3.1 Spacing tokens

Fuente: [`styles.css:56-64`](../src/riot_lol_cli/draft_advisor/static/styles.css#L56-L64)

```css
:root {
  --gap: 16px;          /* gap default entre elementos */
  --radius: 12px;
  --radius-sm: 8px;
  --radius-lg: 16px;
}
```

**Espaciados observados (base de 4px implícita)**:

| Pixel | Uso típico |
|-------|------------|
| `2px` | gaps mínimos en compactos (champion-slot remove-btn) |
| `4px` | gaps de chips en línea |
| `6px` | gaps de role-filters |
| `8px` | gap de champion-slots; padding de pool-toggle |
| `10px` | padding card-hover |
| `12px` | gaps de .draft-summary, alt-card padding |
| `14px` | recommend-btn padding-y |
| `16px` | `--gap` default, padding cards, modal padding |
| `20px` | padding card-body, top-pick padding, splash gallery gap |
| `24px` | header padding, container x-padding (claude-4-5) |
| `32px` | padding sidebar/main-content (splash viewer), container claude-4-5 |
| `48px` | container x-padding (claude-4-5 desktop), section margin-bottom |

**Sugerencia de scale**: 4 / 8 / 12 / 16 / 20 / 24 / 32 / 48 / 64

### 3.2 Grid system

**Layout principal del SPA (Draft Advisor):**

```css
.app { max-width: 1440px; margin: 0 auto; padding: 20px; }

.main-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;     /* 2 columns desktop */
  gap: 24px;
}

@media (max-width: 1024px) {
  .main-grid { grid-template-columns: 1fr; }
}
```

**Layout splash viewer (3-zone)**:

```css
.app-container {
  display: grid;
  grid-template-columns: 280px 1fr;   /* sidebar + main */
  grid-template-rows: auto 1fr;       /* header + content */
}
```

**Grid de slots de campeones (5 columnas siempre)**:

```css
.champion-slots { grid-template-columns: repeat(5, 1fr); gap: 8px; }
```

**Grid de gallery (auto-fill responsive)**:

```css
.gallery-grid { grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
.alternatives-grid { grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; }
.champion-grid { grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); gap: 8px; }
```

---

## 4. Border Radius, Shadows, Glow

### 4.1 Border radius

Fuente: [`templates/claude-4-5.html:55-59`](../templates/claude-4-5.html#L55-L59) y [`styles.css:58-60`](../src/riot_lol_cli/draft_advisor/static/styles.css#L58-L60)

| Token canónico | Token SPA | Valor | Uso |
|----------------|-----------|-------|-----|
| `--shape-radius-sm` | `--radius-sm` | `4px` / `8px` | Inputs, chips pequeños |
| `--shape-radius-md` | (sin token) | `8px` | Buttons, cards small |
| `--shape-radius-lg` | `--radius` | `12px` | Cards principales |
| `--shape-radius-xl` | `--radius-lg` | `16px` / `20px` | Modales, headers panels |
| (especial) | — | `20px` (pill) | Badges, role-filters, chips redondos |
| (especial) | — | `50%` | Avatars, dot bullets |

**Recomendación**: Estandarizar en `4 / 8 / 12 / 16 / 20 / pill / circle`.

### 4.2 Shadows

Fuente: [`templates/claude-4-5.html:49-54`](../templates/claude-4-5.html#L49-L54)

```css
--shadow-depth-1:  0 2px 8px rgba(0,0,0,0.4);
--shadow-depth-2:  0 8px 24px rgba(0,0,0,0.5);
--shadow-depth-3:  0 16px 48px rgba(0,0,0,0.6);
--shadow-hextech:  0 0 24px rgba(11,198,227,0.4), 0 0 48px rgba(11,198,227,0.2);
--shadow-gold:     0 0 20px rgba(200,155,60,0.4), 0 0 40px rgba(200,155,60,0.2);

/* SPA Draft Advisor (más sutiles) */
--shadow-lg:    0 25px 50px -12px rgba(0, 0, 0, 0.5);
--shadow-glow:  0 0 40px rgba(10, 200, 185, 0.1);
--shadow-gold:  0 0 30px rgba(200, 155, 60, 0.15);
```

**Sistema sugerido para Claude Design**:
- `--elevation-1` = depth-1 (cards default)
- `--elevation-2` = depth-2 (cards hover, raised)
- `--elevation-3` = depth-3 (modales, overlays)
- `--glow-info` = shadow-hextech (highlight cyan)
- `--glow-primary` = shadow-gold (highlight gold)

### 4.3 Animaciones / Transiciones

```css
--transition: 200ms ease;                       /* default */
--transition-slow: 400ms cubic-bezier(0.4, 0, 0.2, 1);
```

Animaciones declaradas:
- `fadeIn` (200ms ease) — modales, results
- `slideUp` (250ms cubic-bezier) — modal entry
- `spin` (800ms / 1s linear infinite) — spinners
- `border-flow` (3s linear infinite) — header border glow
- `glow-pulse` (2s ease-in-out infinite) — accent glow
- `grid-flow` (60s linear infinite) — background grid drift
- `shimmer` (1.5s infinite) — skeleton loaders

---

## 5. Breakpoints Responsive

Fuente: múltiples `@media` queries en CSS.

| Breakpoint | Valor | Uso observado |
|------------|-------|---------------|
| Mobile / tablet | `max-width: 768px` | `.explanation-grid` colapsa a 1 columna |
| Small desktop | `max-width: 1024px` | `.main-grid` colapsa a 1 columna; sidebar splash viewer se oculta |
| Mid desktop | `max-width: 1400px` | `.container` (claude-4-5) padding ajusta |
| Default | `≥1024px` | layout completo 2 columnas / 280+1fr |

**Max-widths de containers:**

```css
.app       { max-width: 1440px; }    /* SPA Draft Advisor */
.container { max-width: 1600px; }    /* Match history */
```

**Recomendación**: Adoptar el set de Tailwind / CSS estándar:
- `sm` = 640px
- `md` = 768px (ya usado)
- `lg` = 1024px (ya usado)
- `xl` = 1280px
- `2xl` = 1440px / 1600px (containers)

---

## 6. Efectos visuales firmados

Estos no son tokens, son **patrones recurrentes** que firman la identidad visual.

### 6.1 Background gradient con orbes radiales

```css
body {
  background:
    radial-gradient(ellipse 1400px 900px at 20% -15%, rgba(11,198,227,0.15), transparent 60%),
    radial-gradient(ellipse 1200px 800px at 80% 115%, rgba(200,155,60,0.12), transparent 60%),
    linear-gradient(180deg, var(--piltover-black) 0%, var(--piltover-dark) 40%, var(--surface-base) 100%);
}
```

### 6.2 Grid pattern animado (background overlay)

```css
body::before {
  background-image:
    repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(200,155,60,0.04) 2px, rgba(200,155,60,0.04) 4px),
    repeating-linear-gradient(90deg, ...),
    repeating-linear-gradient(45deg, ...);
  animation: grid-flow 60s linear infinite;
  opacity: 0.4;
}
```

### 6.3 Text gradient en headings

```css
.header h1 {
  background: linear-gradient(135deg, var(--gold-light) 0%, var(--gold) 50%, var(--blue) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

### 6.4 Border glow animado (con mask compositing)

Patrón en `.header::before` de claude-4-5: borde gradiente animado usando `mask-composite: exclude` para crear marco brillante alrededor de la card.

### 6.5 Glassmorphism (modales)

```css
.modal-overlay { background: rgba(0,0,0,0.7); backdrop-filter: blur(4px); }
.filmstrip-modal { background: rgba(1,10,19,0.95); backdrop-filter: blur(10px); }
```
