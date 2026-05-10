# Claude Design Prompt - LOLCLI Pattern Library

Prompt maestro para crear una libreria propia de patrones visuales de
`riot_lol_cli` en Claude Design.

## Para que sirve

Usar este documento como entrada inicial en Claude Design cuando el objetivo sea
alinear Home Hub, Draft Advisor, Meta Scraper, Jungle Meta, Items Browser, Meta
Analyzer, Splash Gallery y exports HTML bajo un mismo lenguaje visual.

Claude Design debe tratar este trabajo como una definicion de sistema visual,
no como un rediseño aislado de una pantalla.

## Que es Claude Design

Claude Design es una herramienta de Anthropic Labs para crear diseños,
prototipos interactivos, presentaciones y otros artefactos visuales mediante una
conversacion con Claude. Permite adjuntar screenshots, documentos, assets y
codigo, iterar sobre un canvas, y generar handoffs para implementacion.

Fuentes oficiales revisadas:

- https://support.claude.com/en/articles/14604416-get-started-with-claude-design
- https://www.anthropic.com/news/claude-design-anthropic-labs
- https://support.claude.com/en/articles/14604397-set-up-your-design-system-in-claude-design
- https://claude.com/resources/tutorials/using-claude-design-for-prototypes-and-ux

## Adjuntos recomendados

Adjuntar en Claude Design:

- Screenshots de Items Browser y Jungle Meta usadas como referencia visual.
- `claude-design-handoff/README.md`
- `docs/design-system.md`
- `src/riot_lol_cli/draft_advisor/static/design-system/tokens.css`
- `src/riot_lol_cli/draft_advisor/static/design-system/components.css`
- Opcional: screenshots actuales de Home Hub, Meta Scraper y Draft Advisor.

## Prompt para Claude Design

```text
Quiero que me ayudes a construir una libreria propia de patrones de diseño para el proyecto riot_lol_cli.

Contexto del producto:
riot_lol_cli es un conjunto de herramientas locales para League of Legends: Home Hub, Draft Advisor, Meta Scraper, Jungle Meta, Items Browser, Meta Analyzer, Splash Gallery y exports HTML. El frontend es HTML/CSS/JavaScript vanilla. No uses React, Vue, Tailwind obligatorio, bundlers ni TypeScript como requisito. El output util debe ser: guia visual, tokens CSS, componentes/patrones reutilizables y ejemplos HTML/CSS plain.

Objetivo:
Crear una libreria transversal de patrones de diseño para que todos los proyectos del repo compartan el mismo lenguaje visual. Hoy algunas surfaces usan estilos parecidos pero no totalmente alineados. Queremos una identidad unica, consistente y reusable, sin que cada proyecto invente su propia paleta o layout.

Estilo visual base:
Usar como referencia principal las screenshots adjuntas de Items Browser y Jungle Meta.
Mantener una estetica dark premium/gaming inspirada en League of Legends, con:
- Fondo navy profundo casi negro.
- Superficies elevadas en azul oscuro.
- Bordes finos gold/cyan con baja opacidad.
- Gold para jerarquia, CTA primario, tabs activos, highlights y foco.
- Cyan para informacion, rol, links secundarios, estado aliado o metadata.
- Tipografia display grande, condensada o italica para headers tipo "ITEMS" y "TIER LIST".
- Layouts densos pero escaneables, pensados para herramientas de analisis, no landing pages.
- Hero/cover compacto de identidad en dashboards principales, con patron diagonal sutil.
- Cards y paneles con radio bajo/medio, no excesivamente redondeados.
- Tab bars, segmented controls, search bars, badges, counters, empty states y modals como patrones centrales.
- Microinteracciones sutiles, nunca decorativas en exceso.
- Respetar prefers-reduced-motion.

Tokens actuales a respetar y consolidar:
- --arc-gold: #c89b3c
- --arc-gold-bright: #f0e6d2
- --arc-gold-dark: #785a28
- --arc-cyan: #0bc6e3
- --arc-cyan-bright: #0ac8b9
- --arc-cyan-dark: #0397ab
- --forge-black: #010a13
- --forge-dark: #0a1428
- --forge-darker: #05101c
- --surface-base: #0d1b2a
- --surface-card: #0f1923
- --surface-raised: #1b2838
- --text-primary: #f0e6d2
- --text-secondary: #a09b8c
- --state-success: #00d084
- --state-error: #ff4655
- --state-warning: #ff9a3c

Buenas practicas obligatorias:
- Diseñar para herramientas reales de uso repetido, no para marketing.
- Priorizar escaneo rapido, densidad util y jerarquia clara.
- Usar componentes accesibles: focus visible, contraste suficiente, labels, aria cuando aplique.
- Incluir estados loading, empty, error, disabled, hover, active y selected.
- Evitar spinners infinitos sin fallback.
- Evitar sistemas visuales aislados por proyecto.
- Evitar paletas nuevas salvo que sean estados semanticos justificados.
- Evitar blobs, orbs o decoracion generica.
- No usar texto visible para explicar como usar la UI; la UI debe explicarse por estructura.
- Mantener español rioplatense con jerga gamer razonable: ADC, draft, teamfight, peel, dive, scaling, jungle, tier, build, patch.
- No traducir terminos gamer universales si quedan peor.

Entregables que necesito:
1. Una definicion clara del design language de riot_lol_cli.
2. Una libreria de patrones con nombres canonicos.
3. Tokens CSS organizados por color, superficie, texto, spacing, radius, elevation, motion y estados.
4. Componentes/patrones en HTML/CSS plain:
   - App shell / dashboard shell
   - Hero compacto tipo Items/Tier List
   - Search + filters panel
   - Segmented controls y tier tabs
   - Cards de champion/item/service
   - Sidebar category panels
   - Stat strips y metric badges
   - Table/list dense pattern
   - Modal/detail drawer
   - Empty/error/loading skeleton states
   - Toast/inline status
5. Variantes por surface:
   - Home Hub: centro operacional, mas utilitario.
   - Items Browser: catalogo filtrable.
   - Jungle Meta: tier list visual con champions y builds.
   - Meta Scraper: tabla/fuentes/scraping status.
   - Draft Advisor: recomendacion con razones y picks.
6. Reglas de composicion: cuando usar hero, cards, tablas, sidebars, tabs, badges y modals.
7. Anti-patterns explicitos: que no debe hacerse en nuevos proyectos.
8. Un mini handoff to engineering con estructura de archivos recomendada:
   - tokens.css
   - patterns.css
   - components.css
   - README.md
   - ejemplos HTML autocontenidos
9. Un checklist de revision para validar que una nueva pantalla respeta el sistema.

Formato de salida:
Primero dame una guia visual compacta. Despues dame tokens CSS. Despues dame ejemplos HTML/CSS plain de los patrones principales. Finalmente dame un checklist de adopcion para el repo.

Importante:
No quiero una UI generica ni corporativa. Quiero una libreria propia, reconocible, consistente con las screenshots adjuntas y con el estilo Hextech dark premium que ya usamos.
```

## Criterios de aceptacion para la respuesta de Claude Design

La respuesta de Claude Design es util si:

- Mantiene HTML/CSS/JS vanilla como salida implementable.
- Usa los tokens `arc-*`, `forge-*`, `surface-*`, `text-*` y `state-*`.
- Diferencia patrones de dashboard, catalogo, tier list y recomendador sin crear
  paletas incompatibles.
- Incluye estados `loading`, `empty`, `error`, `disabled`, `hover`, `active` y
  `selected`.
- Incluye reglas claras de composicion y anti-patterns.
- Puede convertirse a archivos del repo sin depender de Figma, React o Tailwind.

## Handoff posterior a ingenieria

Cuando Claude Design devuelva una propuesta aceptada, implementarla como una
base incremental:

- Actualizar `src/riot_lol_cli/draft_advisor/static/design-system/` o crear una
  carpeta equivalente versionada para patrones compartidos.
- Sincronizar `docs/design-system.md` con tokens, patrones y reglas nuevas.
- Actualizar `claude-design-handoff/README.md` si cambia la guia para prompts.
- Registrar la iteracion en `bitacora_de_cambios.md`.
- Validar visualmente Home Hub, Items Browser, Jungle Meta, Meta Scraper y
  Draft Advisor antes de migrar surfaces legacy.
