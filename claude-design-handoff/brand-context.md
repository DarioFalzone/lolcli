# Brand Context — riot_lol_cli

> Tono, voz, principios de diseño y patrones de UX recurrentes. Extraído del código real (textos UI, comentarios CSS, decisiones visuales).

## 1. Identidad visual declarada

Fuente: comentarios en CSS, patrones consistentes entre superficies.

> _"League of Legends 'Hextech meets modern dark UI'"_
> — [`styles.css:4`](../src/riot_lol_cli/draft_advisor/static/styles.css#L4)

> _"Hextech Visual Language - Riot Games Official Design System"_
> — [`templates/claude-4-5.html:12`](../templates/claude-4-5.html#L12)

**El proyecto está alineado con la identidad visual de League of Legends de Riot Games:**
- **Hextech** — la magitech de Piltover/Zaun: oro, azul cyan, líneas de circuito, glows.
- **Piltover Dark** — backgrounds navy profundos, texturas sutiles, jerarquía con luz.

Esto NO es un branding original — es una adaptación tributo del estilo oficial de LoL para un proyecto personal que usa la API de Riot. Es importante que Claude Design lo trate como un **dark theme premium gaming** y no como una marca corporativa neutral.

## 2. Voz y Tono

### 2.1 Idioma principal: **Español rioplatense (Argentina)**

Fuente: textos UI del Draft Advisor, comentarios CSS, mensajes de error.

```html
<title>Draft Advisor — League of Legends</title>
<p class="subtitle">Motor de puntuación multifactorial para selección óptima de draft</p>
<button>Recomendar Pick</button>

<div class="team-label ally">▲ Equipo Aliado (tu lado)</div>
<div class="team-label enemy">▼ Equipo Enemigo</div>

<option>Blind Pick (A ciegas)</option>
<option>Late / Counter</option>
<option>Clasificatoria Solo/Dúo</option>

<button>Mejor Teórico</button>
<button>Priorizar Pool</button>
<button>Solo del Pool</button>
```

**Tono:**
- **Técnico-experto pero accesible**. Se usan términos del juego sin explicarlos (asume audiencia que juega LoL).
- **Mezcla español + términos en inglés** que son universales en la comunidad gamer (blind pick, counter, dive, peel, gap fill).
- **Conciso**. Frases cortas. Labels en mayúsculas o capitalizadas según jerarquía.
- **Voseo argentino implícito** en algunas piezas:
  - "tu ADC", "tu equipo", "vos sos el primer parada" (en KB texto)
  - "Coordiná con tu jungla", "Spike fuerte nivel 6", "Ward defensivo"

### 2.2 Microcopy patterns observados

#### CTAs
- "Recomendar Pick" (no "Get Recommendation")
- "+ Agregar al pool"
- "Cerrar (ESC)"
- "Cargar 12 más"

#### Labels y placeholders
- "Buscar campeón..." (placeholder modal)
- "Posición de Pick" / "Tipo de Cola" / "Rol Objetivo"
- "Todos · Top · Jungla · Mid · ADC · Soporte"
- "Cargando..." (estado inicial patch badge)

#### Estados / feedback
- "Error cargando datos"
- "Parche 16.7 (Datos: 16.7.1)"
- "171 Campeones • 2019 Skins"

#### Bulleted reasons (output del scoring)
Mezcla español + términos técnicos + datos numéricos:
- "Sinergia top-tier con Samira aliada — pareja recomendada en KB."
- "Counter al dive enemigo (Zed) con tu kit de peel (9/10 anti-dive)."
- "Counters {primary_threat} dive con tu R disengage / W polymorph / R cleanse."

**Patrón típico**: `[afirmación específica]` + `[evidencia entre paréntesis con número]`.

### 2.3 Lo que NO hacer en el tono

- **NO usar formal/corporate** ("Estimado usuario", "Le invitamos a", etc.) — choca con la audiencia gamer.
- **NO traducir términos técnicos universales** del meta de LoL: "engage", "peel", "dive", "poke", "scaling", "blind pick", "wombo combo" se mantienen en inglés.
- **NO ser condescendiente**. El usuario sabe LoL. Si no sabe qué es un "engage support", no es nuestro target.
- **NO usar emojis en abundancia**. El proyecto los usa quirúrgicamente: `▲` ▼ aliado/enemy, `⚠` warnings, `✓` checkmarks, `✕` close. **Excepción**: el splash viewer usa más emojis (`⚡`, `🔀`, `★`, `?`) en botones de acciones secundarias — es coherente con la estética gamer pero pidamos consistencia.

---

## 3. Principios de diseño visibles en el código

### 3.1 Densidad de información — equilibrio jerárquico

El proyecto **muestra mucha información a la vez** pero **jerarquiza con tipografía y color**.

Ejemplo del Top Pick Card:
- Avatar 90×90 (el campeón es lo primero que se mira)
- Nombre 1.8rem weight 800 (segunda jerarquía)
- Score 2.4rem weight 800 color gold (tercera, lateral)
- 6 score bars de 6px height (cuarta, info técnica)
- 4 explanation blocks con bullets (quinta, razones específicas)

**Principio**: nunca hay un solo número grande sin contexto. Pero el contexto se prioriza visualmente para que el ojo pueda decidir qué leer.

### 3.2 Color con propósito (no decorativo)

Cada color significa algo:
- **Gold (`--hextech-gold`)** = importancia, primary action, valor (scores, badges, highlights).
- **Cyan (`--hextech-blue`)** = info, ally, links, glows secundarios.
- **Red (`--defeat`)** = enemy team, derrotas, warnings críticos, riesgos.
- **Green (`--victory`)** = victorias, strengths, success.
- **Orange (`--orange`)** = warnings (no errores, precaución).
- **Purple (`--purple`)** = decoración/mood pero sin uso semántico claro [A confirmar].

**Aplicación consistente**:
- `.team-label.ally { color: var(--blue); }` ↔ siempre cyan/azul.
- `.team-label.enemy { color: var(--red); }` ↔ siempre rojo.
- `.alt-pros` ↔ green; `.alt-cons` ↔ orange.
- `.badge` Victory/Defeat ↔ green/red.

### 3.3 Glow y luz como recurso firma

Casi todos los elementos importantes tienen **glow** (sombras radiales que parecen luz):
```css
.recommend-btn { box-shadow: 0 4px 20px rgba(200, 155, 60, 0.3); }
.top-pick-card { box-shadow: var(--shadow-gold); }
.modal { box-shadow: var(--shadow-lg), var(--shadow-gold); }
```

Esto refuerza la metáfora **"hextech magic"** del videojuego — los elementos UI parecen energía contenida.

### 3.4 Movimiento sutil y constante

El fondo nunca está completamente quieto:
- `body::before` — grid pattern animado lentamente (60s linear infinite).
- `body::after` — orbes radiales fijos (efecto ambient).
- `border-flow` en headers (3s, conmutación de gradient).
- `glow-pulse` en líneas accent (2s ease-in-out).

**Principio**: el UI tiene "vida tenue" — sugiere que el sistema "está pensando" o "tiene energía". Pero los movimientos son **lentos** (no distraen del contenido).

Excepciones — animaciones rápidas con propósito:
- Fade in/out de modales (200-300ms)
- Score bar fill (600ms cubic-bezier — las barras crecen al renderizar)
- Hover lift (transform translateY -2px en 200ms)
- Spinners (800ms-1s)

### 3.5 Componentes pesados visualmente sobre fondos pesados

El proyecto **NO escapa de la pesadez visual** — la abraza:
- Fondos con múltiples gradientes radiales superpuestos.
- Cards con triple sombra (depth-1/2/3 + glow).
- Borders dobles (sólido + glow rgba).
- Headers con border animado + bottom line glow + grid pattern superpuesto.

**Riesgo**: si un componente nuevo se diseña "minimalista flat", va a chocar visualmente. Claude Design debe respetar este nivel de "weight" visual o redefinir todo.

### 3.6 Mobile-aware pero desktop-first

Hay breakpoints (`max-width: 768px`, `1024px`) pero los layouts son **claramente diseñados para desktop**:
- Grids de 5 columnas (champion-slots) que en mobile se ven apretados.
- Sidebar de 280px que se oculta en `<1024px`.
- Containers de 1440-1600px max-width.

[A confirmar — si el target es desktop puro o si se quiere expandir a mobile-first].

---

## 4. Patrones de UX recurrentes

### 4.1 Click-to-add con placeholder explícito (`+`)

En lugar de drag-and-drop o autocomplete, todos los slots/pools usan:
```
┌─────┐
│  +  │  ← click para agregar
└─────┘
```

Visto en: champion-slots, pool-add-btn. **Reduce ambigüedad** — el usuario sabe que es interactivo.

### 4.2 Modal con search + filter chips por categoría

Patrón repetido para selección de campeones:
1. Input de búsqueda en header del modal.
2. Row de filter chips por categoría (rol, archetype).
3. Grid scrollable con resultados.

**Visto en**: Champion Picker Modal del Draft Advisor.

### 4.3 Action label = noun + scope

Las acciones nombran **qué hacen** y **a qué se aplican**:
- "Recomendar Pick" (no solo "Recomendar")
- "+ Agregar al pool"
- "✕ Cerrar Comparador"

### 4.4 Estado del sistema visible en header

Patch badge, version badge, stats badges en el header son **información ambient**: el usuario sabe en todo momento qué versión usa, qué patch trackea, cuántos datos tiene cargados.

### 4.5 Detail-on-demand (modals para profundizar)

La pantalla principal **muestra suficiente para decidir**, pero hacer click en un campeón / item / skin abre un **modal con todo el detalle**.

Visto en: Meta Dashboard (click campeón → modal stats), Splash Viewer (click skin → filmstrip).

**Principio**: progressive disclosure — no abrumar de entrada, pero permitir profundizar sin cambio de página.

### 4.6 Source attribution explícita

En el dashboard mejorado, **cada registro de datos** tiene un badge `[data_dragon]` indicando de dónde viene la información. Esto es un patrón de **transparencia / auditabilidad** importante para QA / data trust.

---

## 5. Antipatrones a evitar (cosas que ya están y queremos NO repetir)

### 5.1 Tres paletas de tokens diferentes

Como se documentó en `design-system.md`, hay tokens duplicados con nombres distintos. Esto es **deuda de diseño**. Claude Design debe **unificar a una sola fuente de verdad**.

### 5.2 HTML embebido en Python

`dashboard_enhanced.py` tiene HTML/CSS/JS como string literal en Python. Es difícil de editar y mantener. La meta es migrar todo a templates Jinja2 separados, pero **no es alcance inmediato del handoff** — Claude Design solo necesita saber que existe.

### 5.3 Estilos inline en `<style>` masivos

`templates/claude-4-5.html` tiene 2329 líneas con un `<style>` enorme inline. Funciona porque el output es un HTML autocontenido (export), pero **no es DRY** — los mismos tokens están duplicados con `splash-viewer.html`.

### 5.4 Falta de loading states en algunas operaciones async

El Draft Advisor SPA muestra spinner en el botón Recomendar pero **no en el modal de search** mientras se filtra una lista grande. [A confirmar — agregar feedback visual durante búsquedas].

---

## 6. Resumen ejecutivo del brand para Claude Design

**En una frase**: _"Dark mode premium gaming inspirado en League of Legends Hextech, denso de información jerarquizada, con glow gold/cyan como firma visual y voz técnica en español argentino para audiencia gamer experta."_

**Tres palabras clave**:
1. **Hextech** (gold + cyan + dark navy)
2. **Denso pero jerárquico** (mucha info, bien priorizada)
3. **Vivo** (movimiento sutil constante, glows, transiciones)

**Tono**: técnico, conciso, sin condescendencia, español rioplatense con vocabulario gamer mixto ES/EN.

**Audiencia**: jugador de LoL de nivel medio-avanzado. NO tutorial-friendly — asume conocimiento del juego.
