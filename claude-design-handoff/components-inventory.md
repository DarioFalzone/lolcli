# Components Inventory — riot_lol_cli

> Componentes reutilizables identificados en el código actual. Como el proyecto **NO usa una librería de componentes** (es HTML/CSS/JS plain + templates Jinja2), estos son patrones CSS que se repiten y deberían ser componentes formales en Claude Design.

## Importante

Los componentes están definidos como **clases CSS** (no JSX/Vue), distribuidos en:
- `src/riot_lol_cli/draft_advisor/static/styles.css` (954 líneas, sistema más prolijo)
- `templates/claude-4-5.html` (estilos inline, 2329 líneas)
- `templates/splash-viewer.html` (estilos inline minified)
- `src/riot_lol_cli/dashboard_enhanced.py` (HTML embebido en Python)

Para Claude Design, traducir cada uno a un componente formal con sus props/variantes.

---

## 1. Card

Container universal con borde sutil y header opcional.

**Selector base:** `.card`
**Variante extendida:** `.top-pick-card`, `.alt-card`, `.skin-card`

**Estructura:**
```html
<div class="card">
  <div class="card-header">
    <h2><span class="icon">⚙</span> Título</h2>
  </div>
  <div class="card-body">
    <!-- contenido -->
  </div>
</div>
```

**Props (sugeridas):**
- `title: string`
- `icon: string` (emoji o glifo Unicode — actualmente)
- `variant: "default" | "top-pick" | "alternative" | "skin"`
- `interactive: boolean` (aplica hover state)

**Estados:**
- Default → `border: 1px solid var(--border)`
- Hover → `border-color: var(--border-gold)` (transition 200ms)
- Variante `top-pick` → fondo gradient + `border: 1px solid var(--gold-dim)` + `box-shadow: var(--shadow-gold)`

**Ejemplo de uso real:** [`index.html:22-26`](../src/riot_lol_cli/draft_advisor/static/index.html#L22-L26)

---

## 2. Button — Recommend (Primary CTA)

**Selector:** `.recommend-btn`

**Estructura:**
```html
<button class="recommend-btn" id="recommend-btn" onclick="getRecommendation()">
  Recomendar Pick
</button>
```

**Props:**
- `loading: boolean` (deshabilita y reduce opacity)
- `disabled: boolean` [A confirmar — no hay estado disabled explícito]

**Estados:**
- Default → gradiente gold con `box-shadow: 0 4px 20px rgba(200,155,60,0.3)`
- Hover → `transform: translateY(-2px)` + sombra más fuerte
- Active (press) → `transform: translateY(0)`
- Loading → `pointer-events: none; opacity: 0.7;`

**Tipografía:** `Outfit` 1.05rem weight 700 letter-spacing 0.02em.

**Estilo visible** (de [`styles.css:584-613`](../src/riot_lol_cli/draft_advisor/static/styles.css#L584-L613)):
```css
.recommend-btn {
  padding: 14px 48px;
  background: linear-gradient(135deg, var(--gold), var(--gold-light));
  color: var(--bg-primary);   /* texto oscuro sobre fondo gold */
  border-radius: var(--radius);  /* 12px */
}
```

---

## 3. Button — Secondary (Pool Toggle / Hotkey)

**Selectores:** `.pool-toggle button`, `.hotkey-btn`

**Variantes vistas:**
- **Pool toggle** (3 botones segmentados): default transparente, active = gradiente gold sólido.
- **Hotkey button** (splash viewer): fondo `rgba(200,155,60,0.1)` con borde `--border-metal`.

**Estados:**
- Default → fondo translúcido + borde sutil
- Hover → fondo más opaco + borde más fuerte + glow box-shadow
- Active / Selected → gradiente sólido

```css
.pool-toggle button.active {
  background: linear-gradient(135deg, var(--gold-dim), var(--gold));
  color: var(--bg-primary);
}
```

---

## 4. Button — Ghost / Filter (role-filter, alphabet-letter)

**Selectores:** `.role-filter`, `.alphabet-letter`, `.filmstrip-btn`

**Forma:** chip rounded (`border-radius: 20px` para role-filter; cuadrado pequeño para alphabet-letter).

**Estados:**
- Default → fondo transparente, borde gris, color text-secondary
- Hover / Active → fondo translúcido gold + borde gold-dim + color gold

**Ejemplo:** [`index.html:160-167`](../src/riot_lol_cli/draft_advisor/static/index.html#L160-L167)

---

## 5. Champion Slot (Card de campeón vacío/lleno)

Slot interactivo en el draft board.

**Selector:** `.champion-slot`
**Modificadores:** `.filled`, `.ally`, `.enemy`, `.disabled`

**Estructura (vacío):**
```html
<div class="champion-slot" data-team="ally" data-index="0" onclick="openChampionPicker('ally', 0)">
  <span class="slot-placeholder">+</span>
</div>
```

**Estructura (lleno):**
```html
<div class="champion-slot filled ally">
  <img class="slot-img" src="..." alt="Jinx">
  <div class="slot-name">Jinx</div>
  <button class="remove-btn">×</button>
</div>
```

**Props:**
- `team: "ally" | "enemy"`
- `index: number`
- `champion: { id, displayName, splashUrl } | null`
- `disabled: boolean`
- `onPick: (team, index) => void`
- `onRemove: () => void`

**Estados:**
- Empty → `border: 2px dashed var(--border)` + placeholder `+`
- Empty hover → `border-color: var(--gold-dim)` + bg cambia
- Filled (ally) → `border-color: var(--blue-dim)` solid
- Filled (enemy) → `border-color: var(--red-dim)` solid
- Filled hover → muestra `.remove-btn`

**Aspect ratio:** 1:1 (cuadrado, mínimo 80x80).

---

## 6. Modal (overlay + dialog)

Modal centrado con backdrop blur.

**Selectores:** `.modal-overlay`, `.modal`
**Variantes:** Champion Picker (`.modal`), Filmstrip (`.filmstrip-modal`), Comparator (`.comparator-modal`), Hotkeys (`.hotkeys-overlay`)

**Estructura:**
```html
<div class="modal-overlay active">
  <div class="modal">
    <div class="modal-header">
      <input type="text" placeholder="Buscar…">
      <button class="modal-close">×</button>
    </div>
    <div class="role-filters">
      <button class="role-filter active">Todos</button>
      …
    </div>
    <div class="champion-grid">…</div>
  </div>
</div>
```

**Props:**
- `open: boolean` (toggle clase `.active`)
- `title: string`
- `closable: boolean`
- `onClose: () => void`

**Estados:**
- Closed → `display: none`
- Opening → animación `fadeIn 200ms` (overlay) + `slideUp 250ms cubic-bezier` (dialog)

**Backdrop:** `background: rgba(0,0,0,0.7); backdrop-filter: blur(4px)`.
Para filmstrip: `rgba(1,10,19,0.95)` con `blur(10px)` (más opaco, full-screen).

---

## 7. Input — Search

**Selectores:** `.modal-header input`, `.search-input`

**Estructura:**
```html
<input type="text" id="champion-search" placeholder="Buscar campeón…" autofocus>
```

**Estados:**
- Default → `border: 1px solid var(--border)` (o `--border-metal`)
- Focus → `border-color: var(--gold)` + box-shadow glow gold
- Placeholder → `color: var(--text-muted)` o `--text-tertiary`

**Variante grande (splash viewer):**
```css
.search-input {
  padding: 12px 16px;
  border: 2px solid var(--border-metal);
  border-radius: var(--shape-radius-md);
}
.search-input:focus {
  box-shadow: 0 0 16px rgba(200,155,60,0.4);
}
```

---

## 8. Select (dropdown nativo estilizado)

**Selector:** `.context-group select`

Usa `<select>` nativo con `appearance: none` y SVG inline para el caret.

**Estructura:**
```html
<div class="context-group">
  <label>Posición de Pick</label>
  <select id="pick-position">
    <option value="blind">Blind Pick (A ciegas)</option>
    <option value="early">Rotación Temprana</option>
    <option value="late" selected>Late / Counter</option>
  </select>
</div>
```

**Props:**
- `label: string`
- `value: string`
- `options: Array<{ value, label }>`
- `onChange: (value) => void`

**Caret embebido como SVG data URI:**
```css
background-image: url("data:image/svg+xml,%3Csvg ... stroke='%239ca3af'...");
```

---

## 9. Score Bar (factor breakdown bar)

Barra horizontal con label, track, fill animado y valor.

**Estructura:**
```html
<div class="score-factor">
  <div class="score-factor-label">Ally Synergy</div>
  <div class="score-bar-track">
    <div class="score-bar-fill" style="width: 78%"></div>
  </div>
  <div class="score-factor-value">78</div>
</div>
```

**Props:**
- `label: string`
- `value: number` (0-100)
- `colorScheme: "default" | "warning" | "success"` [A confirmar — actualmente único gradient]

**Estilo del fill:**
```css
.score-bar-fill {
  background: linear-gradient(90deg, var(--blue), var(--gold));
  transition: width 600ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

**Track height:** 6px. Label width: 130px.

---

## 10. Pill / Badge

Etiquetas pequeñas redondeadas con varios colores.

**Selectores observados:** `.patch-badge`, `.pool-chip`, `.team-label`, `.score-label`, `.badge`

### Variantes:
- **Patch badge** ([`styles.css:123-133`](../src/riot_lol_cli/draft_advisor/static/styles.css#L123-L133)):
  ```css
  background: rgba(200, 155, 60, 0.1);
  border: 1px solid var(--border-gold);
  color: var(--gold);
  border-radius: 20px;
  padding: 3px 12px;
  ```

- **Pool chip** (item del pool con close button):
  ```css
  background: rgba(200, 155, 60, 0.1);
  border: 1px solid var(--border-gold);
  color: var(--gold);
  ```

- **Pool add button** (dashed, cyan):
  ```css
  background: rgba(10, 200, 185, 0.1);
  border: 1px dashed var(--border-blue);
  color: var(--blue);
  ```

- **Skin family badges** (splash viewer):
  ```css
  .badge.Prestige     { background: linear-gradient(135deg,#ffd700,#ffed4e); color:#000 }
  .badge.Legacy       { background: linear-gradient(135deg,#8b4513,#cd853f); color:#fff }
  .badge.Mythic       { background: linear-gradient(135deg,#9b30ff,#da70d6); color:#fff }
  .badge.Championship { background: linear-gradient(135deg,#1e90ff,#87ceeb); color:#fff }
  .badge.Hextech      { background: linear-gradient(135deg,#0bc6e3,#0ac8b9); color:#000 }
  ```

**Props sugeridas:**
- `variant: "default" | "primary" | "info" | "success" | "warning" | "error"`
- `style: "filled" | "outline" | "dashed"`
- `size: "sm" | "md"`
- `removable: boolean` (incluye close X)

---

## 11. Avatar (Champion portrait)

**Selectores:** `.top-pick-portrait`, `.alt-portrait`, `.champion-avatar`, `.thumbnail`

**Tamaños:**
| Selector | Tamaño |
|----------|--------|
| `.top-pick-portrait` | 90×90 |
| `.alt-portrait` | 48×48 |
| `.champion-avatar` (splash sidebar) | 40×40 (round) |
| `.champion-option img` | aspect-ratio 1 (variable, ~80) |
| `.thumbnail` | 120×68 |

**Props:**
- `src: string`
- `name: string`
- `size: "xs" | "sm" | "md" | "lg" | "xl"`
- `border: "none" | "subtle" | "primary"` (gold border en top-pick)
- `shape: "square" | "rounded" | "circle"`

**Border styling:**
```css
.top-pick-portrait { border: 2px solid var(--gold); border-radius: var(--radius); box-shadow: 0 0 20px rgba(200,155,60,0.2); }
.alt-portrait { border: 1px solid var(--border); border-radius: var(--radius-sm); }
```

---

## 12. List Item — Explanation block

Lista con bullet redondo coloreado por tipo.

**Selector:** `.explanation-block`
**Variantes:** `.strengths`, `.risks`, `.avoid`, `.pattern`

**Estructura:**
```html
<div class="explanation-block">
  <h4 class="strengths">▲ Strengths in this draft</h4>
  <ul class="strengths-list">
    <li>Strong synergy with allied Lulu</li>
    <li>Counter to enemy Zed dive</li>
  </ul>
</div>
```

**Color por variante (h4 + bullet):**
- `.strengths` → `--green` (success)
- `.risks` → `--orange` (warning)
- `.avoid` → `--red` (error)
- `.pattern` → `--blue` (info)

**Bullet** (custom dot via `::before`):
```css
.explanation-block li::before {
  content: '';
  position: absolute;
  width: 5px; height: 5px;
  border-radius: 50%;
}
.explanation-block .strengths-list li::before { background: var(--green); }
```

---

## 13. Tab Bar

**Selector:** `.tabs` (en dashboard_enhanced)

**Estados:**
- Default → `color: var(--light)` sin border
- Hover → `color: var(--accent)`
- Active → `color: var(--accent)` + `border-bottom: 2px solid var(--accent)`

**Estructura:**
```html
<div class="tabs">
  <button class="tab active">Dashboard</button>
  <button class="tab">Matchups</button>
  <button class="tab">Items</button>
  <button class="tab">Raw Data</button>
</div>
```

[A confirmar] — selector exacto y nombres de clase del tab activo. Lo extraído fue del HTML embebido en `dashboard_enhanced.py`.

---

## 14. Skeleton / Loading State

**Spinner inline** (Draft Advisor):
```css
.spinner {
  width: 18px; height: 18px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 800ms linear infinite;
}
```

**Skeleton shimmer** (Splash Viewer):
```css
.skeleton {
  background: linear-gradient(90deg, rgba(200,155,60,0.05) 0%, rgba(200,155,60,0.15) 50%, rgba(200,155,60,0.05) 100%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
```

**Loading state en cards** (skin viewer):
```css
.skin-card.loading .skin-image-wrapper::after {
  /* spinner gold de 40x40 al centro */
}
```

---

## 15. Header

**Variantes:**
- **Header centrado** (Draft Advisor SPA): título + subtítulo + patch badge centrados.
- **Header de aplicación** (Match History, Splash Viewer): logo izquierda + breadcrumbs + acciones derecha. Sticky con `backdrop-filter: blur(10px)`.

**Estructura splash viewer:**
```html
<header class="header">
  <div class="header-left">
    <div class="logo">⚡ SPLASH GALLERY</div>
    <div class="breadcrumbs">…</div>
  </div>
  <div class="header-right">
    <div class="stats-badge">171 Campeones • 2019 Skins</div>
    <select class="hotkey-btn">…</select>
    <button class="hotkey-btn">★ Favoritos</button>
    <div class="version-badge">v1.6.4</div>
  </div>
</header>
```

**Efectos:**
- Border gradient animado (`border-flow` 3s) — claude-4-5
- Bottom line glow (`glow-pulse` 2s) — splash viewer

---

## 16. Sidebar (Splash Viewer)

**Selector:** `.sidebar`

**Estructura:**
```html
<aside class="sidebar">
  <div class="search-box">
    <input class="search-input" placeholder="Buscar campeón…">
  </div>
  <nav class="alphabet-nav">
    <div class="alphabet-title">A—Z</div>
    <div class="alphabet-grid">
      <span class="alphabet-letter">A</span>
      …
    </div>
  </nav>
  <ul class="champions-list">
    <li class="champion-item">…</li>
  </ul>
</aside>
```

**Width:** 280px fijo, sticky. Se oculta en `max-width: 1024px`.

**Custom scrollbar:**
```css
.sidebar::-webkit-scrollbar-thumb {
  background: var(--hextech-gold);
  border-radius: 4px;
}
```

---

## Resumen — componentes a portar a Claude Design

Agrupados por prioridad:

### Alta prioridad (componentes core)
1. `Button` (variants: primary, secondary, ghost, filter)
2. `Card` (variants: default, top-pick, alternative)
3. `Input` (search + form)
4. `Select` (con caret estilizado)
5. `Modal` (con backdrop blur, animaciones)
6. `Pill / Badge` (variants por color y forma)
7. `Avatar` (champion portrait, sizes)

### Media prioridad (composite)
8. `ChampionSlot` (card especializada del draft)
9. `ScoreBar` (factor breakdown bar)
10. `ExplanationBlock` (lista con bullet coloreado)
11. `Tab` (dashboard tabs)

### Baja prioridad (especializados)
12. `Sidebar` (alphabet nav + lista)
13. `Header` (con border glow effects)
14. `Skeleton / Spinner`
