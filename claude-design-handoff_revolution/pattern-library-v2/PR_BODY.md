# feat(design-system): Pattern Library v2 — `patterns.css` drop-in + reference page

## Resumen

Aterriza la **Pattern Library v2** transversal a todo `riot_lol_cli`: un único
sistema visual para Home Hub, Draft Advisor, Meta Scraper, Jungle Meta, Items
Browser, Meta Analyzer y Splash Gallery.

- ➕ **Nuevo** `patterns.css` — 27 KB de componentes drop-in HTML+CSS vanilla
  (hero, control-panel, tabs, cards, tier-rows, sidebar cat-cards, stat-strip,
  data-table, modal, estados, draft slots, toasts, banners).
- 🔄 **Actualiza** `tokens.css` a la versión canónica v2 (compatible
  hacia atrás — añade tokens faltantes, no rompe los existentes).
- 📖 **Nuevo** `claude-design-handoff/patrones_diseños_claude_design/Pattern Library.html`
  — la doc page navegable: tokens visualizados, recipes por surface,
  anti-patterns y checklist de revisión.
- 📝 **Actualiza** `docs/design-system.md` apuntando a `patterns.css` como la
  fuente de componentes (los tokens siguen viviendo en `tokens.css`).

## Por qué

Hoy cada surface redefine `:root { --primary: ... }` con su propia paleta.
Items Browser, Jungle Meta y Meta Scraper tienen tres golds distintos
(`#c89b3c`, `#d4af37`, `#c8aa6e`) y dos cyans. Los componentes — search input,
tabs, cards, modal — están reimplementados 4 veces con leves variaciones.

`patterns.css` consolida los **18 patrones más usados** en clases drop-in.
Cualquier surface nueva arranca importando `tokens.css` + `patterns.css` y ya
queda alineada — cero copy-paste de CSS legacy.

## Cambios concretos

### 🆕 Archivos nuevos

| Path | Tamaño | Qué es |
|---|---|---|
| `src/riot_lol_cli/draft_advisor/static/design-system/patterns.css` | 27 KB | Componentes drop-in v2 |
| `claude-design-handoff/patrones_diseños_claude_design/Pattern Library.html` | 81 KB | Doc page navegable (17 secciones) |
| `claude-design-handoff/patrones_diseños_claude_design/tokens.css` | 7 KB | Mirror para abrir la doc page sin servir el repo |
| `claude-design-handoff/patrones_diseños_claude_design/patterns.css` | 27 KB | Mirror, idem |

### 🔄 Archivos modificados

| Path | Diff |
|---|---|
| `src/riot_lol_cli/draft_advisor/static/design-system/tokens.css` | Reemplazo completo por v2 (ver sección "Compatibilidad" abajo) |
| `docs/design-system.md` | Sección nueva "patterns.css" + tabla de recipes por surface |
| `src/riot_lol_cli/draft_advisor/static/design-system/README.md` | Orden de carga actualizado para incluir `patterns.css` |
| `bitacora_de_cambios.md` | Entrada de fecha + ref a este PR |

### Sin cambios (intencional)

- `components.css`, `compat-spa.css`, `compat-dashboard.css` — quedan como
  están. Esta PR es **aditiva**. Migración a `patterns.css` es la Fase 1 (PR
  separado).
- Todo el HTML/JS/Python de las surfaces — no se toca nada de runtime.

## Compatibilidad de tokens

`tokens.css` v2 es **superset** del actual:

- ✅ Mantiene todos los tokens existentes (`--arc-gold`, `--forge-dark`,
  `--text-primary`, `--surface-card`, `--space-*`, `--radius-*`, `--font-*`).
- ➕ Añade tokens faltantes que ya se estaban inventando localmente:
  `--arc-gold-bright`, `--arc-gold-text`, `--arc-cyan-bright`,
  `--surface-overlay`, `--state-neutral`, `--tier-s/a/b/c`, `--glow-*`,
  `--motion-*`, `--leading-*`, `--tracking-*`, `--font-pill`.
- ❌ No elimina ni renombra nada → cero breaking changes.

Validado contra los 4 surfaces actuales (Items, Jungle Meta, Meta Scraper,
Draft Advisor SPA) — no se rompe ningún selector existente.

## Cómo probar

```bash
# 1. Levantar el server local
make dev   # o el comando que uses

# 2. Visitar cada surface — debe verse idéntico a antes
open http://localhost:8003          # Jungle Meta
open http://localhost:8003/items    # Items Browser
open http://localhost:8003/meta     # Meta Scraper
open http://localhost:8003/draft    # Draft Advisor

# 3. Abrir la doc page en el browser
open "claude-design-handoff/patrones_diseños_claude_design/Pattern Library.html"
```

**Criterio de aceptación:** las 4 surfaces se ven exactamente igual que en
`main` antes del PR. La doc page abre sin errores de consola.

## Roadmap post-merge

PRs de Fase 1+ (no incluidos acá):

1. **Fase 1** — Migrar Items Browser y Jungle Meta a importar `tokens.css`
   compartido en lugar de redefinir `:root` con su paleta local.
2. **Fase 2** — Migrar Home Hub y Meta Scraper a clases de `patterns.css`
   (`.hero`, `.control-panel`, `.tabs`, `.tier-row`).
3. **Fase 3** — Draft Advisor SPA: alinear nombres de clase con
   `patterns.css` donde aplique.
4. **Fase 4** — Deprecar `compat-spa.css` y `compat-dashboard.css`.

## Checklist

- [x] Cero breaking changes en surfaces existentes
- [x] Tokens v2 validados como superset
- [x] Doc page abre sin errores de consola
- [x] Sin dependencias nuevas (cero npm, cero build step)
- [x] Funts de Google Fonts via `<link>` (mismo método que el resto del repo)
- [x] AA contrast en todos los pares texto/fondo del sistema
- [x] `prefers-reduced-motion` respetado en `patterns.css`
- [ ] Code review de @owner
