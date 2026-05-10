# Design System — riot_lol_cli

> Documentación del sistema de tokens CSS canónicos aplicado a las 5 surfaces principales del proyecto.
> Última actualización: 2026-05-08.

---

## Identidad visual

**"Hextech meets modern dark UI"** — inspirado en el lenguaje visual de League of Legends.

- Dark mode obligatorio
- Paleta: gold (`#c89b3c`) + cyan (`#0bc6e3`) sobre navy profundo (`#010a13`)
- Glow effects y gradientes como firma visual
- Animaciones lentas y sutiles (el UI "vive")

---

## Archivos del design system

Ubicados en `src/riot_lol_cli/draft_advisor/static/design-system/`:

| Archivo | Líneas | Propósito |
|---------|--------|-----------|
| `tokens.css` | 169 | Tokens canónicos — única fuente de verdad de colores, tipografía, espaciado, sombras |
| `components.css` | 506 | Clases drop-in: `.btn`, `.card`, `.pill`, `.score-bar`, `.modal` |
| `compat-spa.css` | 74 | Aliases legacy para el SPA (tokens NO migrados: `--bg-*`, `--green`, etc.) |
| `compat-dashboard.css` | 35 | Aliases legacy para el Dashboard (referencia, no linkeado activamente) |

### Claude Design

Para explorar una libreria propia de patrones transversales con Claude Design,
usar `claude-design-handoff/pattern-library-prompt.md` junto con screenshots de
Items Browser y Jungle Meta. La salida esperada debe seguir siendo compatible
con HTML/CSS/JS vanilla y consolidar estos tokens, no reemplazarlos por un
sistema visual ajeno.

---

## Familias de tokens canónicos

### Colores de marca

```css
/* Gold (acciones primarias, highlights, scores) */
--arc-gold:         #c89b3c
--arc-gold-bright:  #f0e6d2
--arc-gold-dark:    #785a28
--arc-gold-accent:  #c8aa6e

/* Cyan (info, aliados, links secundarios) */
--arc-cyan:         #0bc6e3
--arc-cyan-bright:  #0ac8b9
--arc-cyan-dark:    #0397ab
```

### Fondos (Forge = Piltover dark)

```css
--forge-black:   #010a13   /* fondo más profundo */
--forge-dark:    #0a1428
--forge-darker:  #05101c

/* Superficies */
--surface-base:    #0d1b2a
--surface-raised:  #1b2838
--surface-card:    #0f1923
--surface-overlay: #1e2d3d
```

### Estado semántico

```css
--state-success:     #00d084   /* victorias, strengths */
--state-success-dim: rgba(0, 208, 132, 0.15)
--state-error:       #ff4655   /* derrotas, enemigos, riesgos */
--state-error-dim:   rgba(255, 70, 85, 0.2)
--state-warning:     #ff9a3c   /* precaución */
--state-warning-dim: rgba(255, 154, 60, 0.15)
--state-info:        #0bc6e3
--state-neutral:     #a09b8c   /* remake */
```

### Tipografía

```css
--font-display:   'Spiegel', 'Outfit', sans-serif   /* títulos */
--font-body:      'Inter', system-ui, sans-serif     /* cuerpo */

/* Escala de tamaños */
--font-display-xl: 2.5rem    --font-display-lg: 2rem
--font-display-md: 1.5rem    --font-display-sm: 1.25rem
--font-body-lg: 1.125rem     --font-body-md: 1rem
--font-body-sm: 0.875rem     --font-body-xs: 0.75rem
```

### Espaciado

```css
--space-1: 4px    --space-2: 8px    --space-3: 12px   --space-4: 16px
--space-5: 20px   --space-6: 24px   --space-8: 32px   --space-10: 40px
--space-12: 48px  --space-16: 64px
```

### Radio de borde

```css
--radius-xs: 4px    --radius-sm: 8px    --radius-md: 12px
--radius-lg: 16px   --radius-xl: 20px   --radius-pill: 999px
```

### Elevación / Sombras

```css
--elevation-1: 0 2px 8px rgba(0,0,0,0.4)
--elevation-2: 0 8px 24px rgba(0,0,0,0.5)
--elevation-3: 0 16px 48px rgba(0,0,0,0.6)
--elevation-4: 0 25px 50px -12px rgba(0,0,0,0.5)   /* shadow-lg legacy */

--glow-gold: 0 0 20px rgba(200,155,60,0.4), 0 0 40px rgba(200,155,60,0.2)
--glow-cyan: 0 0 24px rgba(11,198,227,0.4), 0 0 48px rgba(11,198,227,0.2)
```

---

## Cómo usar en una nueva surface

### Surface con servidor FastAPI (puede cargar CSS externo)

```html
<link rel="stylesheet" href="/static/design-system/tokens.css?v=1">
<link rel="stylesheet" href="/static/design-system/components.css?v=1">
<!-- Si hay tokens legacy que aún no migraste: -->
<link rel="stylesheet" href="/static/design-system/compat-spa.css?v=1">
<link rel="stylesheet" href="/static/tu-surface.css">
```

### Surface estática offline (HTML autocontenido)

Copiar el bloque `:root` de `tokens.css` dentro del `<style>` del template.
Ver `templates/claude-4-5.html` y `templates/splash-viewer.html` como referencia.

---

## Clases de componentes (components.css)

### Botones

```html
<!-- Primario (gold, CTA principal) -->
<button class="btn btn-primary">Recomendar Pick</button>

<!-- Secundario (outline gold) -->
<button class="btn btn-secondary">+ Agregar</button>

<!-- Ghost (minimal, filtros, acciones menores) -->
<button class="btn btn-ghost">Cerrar</button>
<button class="btn btn-ghost active">Mejor Teórico</button>
```

### Pills / Badges

```html
<span class="pill pill-gold">Parche 26.7</span>
<span class="pill pill-cyan">ADC</span>
<span class="pill pill-success">Victoria</span>
<span class="pill pill-error">Derrota</span>
```

### Cards

```html
<div class="card">
  <div class="card-header"><h2>Título</h2></div>
  <div class="card-body">Contenido</div>
</div>

<!-- Card clickeable con hover lift -->
<div class="card card-interactive">...</div>
```

---

## Estado de migración por surface

| Surface | Archivo | Estado |
|---------|---------|--------|
| Draft Advisor SPA | `static/styles.css` + `index.html` | ✅ Migrado (tokens canónicos + .btn/.pill) |
| Match History | `templates/claude-4-5.html` | ✅ Migrado (tokens canónicos inline) |
| Splash Viewer | `templates/splash-viewer.html` | ✅ Migrado (tokens canónicos inline) |
| Dashboard | `dashboard_enhanced.py` | ✅ Tokens renombrados (sigue siendo autocontenido) |

**Tokens NO migrados en SPA** (requieren decisión de valor antes de migrar):

| Token legacy | Valor SPA | Canónico | Diferencia |
|---|---|---|---|
| `--bg-primary` | `#0a0e1a` | `--forge-black` `#010a13` | SPA más claro |
| `--text-primary` | `#e4e4e7` (gris frío) | `--text-primary` `#f0e6d2` (crema) | Paleta diferente |
| `--green` | `#2dcc70` | `--state-success` `#00d084` | Verde diferente |
| `--gold-light` | `#e8c97a` | `--arc-gold-bright` `#f0e6d2` | Diferente |

---

## Historial de la migración

```
2026-04-26  FASE 0  Import tokens.css + components.css + compat layers → static/design-system/
2026-04-26  FASE 1  Wire design system al SPA via compat layer, drop :root de styles.css
2026-04-26  FASE 2  Migración de nombres en las 4 surfaces, drop compat block de tokens.css
2026-04-26  FASE 3  Link components.css, .btn/.pill en SPA, Pool de Campeones comentado
```

Commits relevantes: `c47c87e` → `f1ff944` → `b98af17` → `e046130` → `a735989` → `141cc77` → `7110e74` → `4d5633a`
