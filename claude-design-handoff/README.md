# Claude Design Handoff

Contexto unico para importar `riot_lol_cli` a Claude Design. Reemplaza los documentos fragmentados de marca, stack, tokens, componentes y flujos.

## Prompt maestro

- `pattern-library-prompt.md`: prompt robusto para pedirle a Claude Design una libreria propia de patrones visuales transversal a todos los proyectos.
- Adjuntar junto con este README, `docs/design-system.md`, tokens/componentes CSS y screenshots actuales de Items Browser/Jungle Meta.
- El objetivo del prompt no es rediseñar una pantalla aislada, sino generar un sistema de patrones reusable para HTML/CSS/JS vanilla.

## Resumen

- Proyecto: CLI + servicios locales de analisis para League of Legends.
- Identidad visual: Hextech dark / premium gaming.
- Audiencia: jugador de LoL medio-avanzado.
- Voz: espanol rioplatense, tecnica, concisa, con jerga gamer EN/ES.
- Frontend: HTML, CSS y JavaScript vanilla; no React, no bundler, no TypeScript.

## Stack consumible por design

| Capa | Tecnologia |
|------|------------|
| Backend | Python 3.9+, FastAPI, Pydantic V2, SQLAlchemy, SQLite |
| CLI | Click |
| Templates | Jinja2 |
| Frontend | HTML/CSS/JS vanilla |
| Assets | Data Dragon, splash arts locales |
| Design tokens | CSS custom properties |

Claude Design debe generar specs visuales, tokens CSS y componentes en HTML/CSS plain. Si entrega React/Vue, hay que traducirlo manualmente.

## Identidad

Principios visuales:

- Dark mode obligatorio.
- Navy profundo como base, gold para jerarquia/acciones y cyan para informacion.
- Glow y luz como firma visual Hextech, no como decoracion aleatoria.
- Densidad alta pero jerarquizada: score, contexto y razones deben escanearse rapido.
- Movimiento sutil y respetuoso de `prefers-reduced-motion`.

Tono:

- Usar "Recomendar Pick", "tu equipo", "Equipo Enemigo", "Blind Pick", "Counter", "peel", "dive", "scaling".
- Evitar tono corporativo o tutorial basico.
- No traducir terminos gamer universales si suenan peor en espanol.

## Superficies

| Superficie | Ruta | Prioridad |
|------------|------|-----------|
| Draft Advisor SPA | `src/riot_lol_cli/draft_advisor/static/` | Alta |
| Champion Picker modal | `src/riot_lol_cli/draft_advisor/static/` | Alta |
| Top Pick / Alternatives | `src/riot_lol_cli/draft_advisor/static/` | Alta |
| Meta Dashboard | `src/riot_lol_cli/dashboard_enhanced.py` | Media |
| Match History export | `templates/claude-4-5.html` | Baja |
| Splash Gallery | `templates/splash-viewer.html` | Baja |

## Componentes base

- Card: `card`, `top-pick-card`, `alt-card`, `skin-card`.
- Buttons: primary CTA, ghost/filter, segmented controls.
- Champion slot: empty/filled, ally/enemy, remove action.
- Modal: overlay, header, search, filters, grid.
- Input/search: focus visible con gold/cyan.
- Select: nativo estilizado.
- Score bar: label, track, fill, value.
- Pill/badge: patch, tier, source, state.
- Tabs: Dashboard/Matchups/Items/Raw Data.
- Table: sortable, source badges, empty states.

## Flujos principales

Draft Advisor:

```text
Abrir /draft
  -> elegir target_role
  -> completar aliados/enemigos con modal
  -> POST /api/v1/draft/recommend
  -> leer Top Pick, alternativas y razones
```

Meta Dashboard:

```text
python scripts/setup_meta_analyzer.py
  -> python scripts/run_api.py
  -> /dashboard-enhanced
  -> tabs de tier list, matchups, items y raw data
```

Splash Gallery:

```text
download_splash_arts.py
  -> build-splash-manifest
  -> generate-splash-viewer
  -> outputs/splash-viewer.html
```

## Deuda visual conocida

- Hay historicamente varias paletas; la referencia tecnica vigente es `docs/design-system.md` y los tokens en `src/riot_lol_cli/draft_advisor/static/design-system/`.
- `dashboard_enhanced.py` mantiene HTML/CSS/JS embebido en Python.
- Algunos exports usan estilos inline grandes por necesidad offline.
- Accesibilidad: reforzar `aria`, focus trap en modales, skip link y medicion de contraste.

## Checklist para Claude Design

- Confirmar que entiende que el output util es HTML/CSS plain o tokens CSS.
- Mantener dark mode Hextech.
- No proponer React como requisito.
- Priorizar Draft Advisor antes que superficies legacy.
- Respetar microcopy en espanol rioplatense.
- Documentar cambios visuales relevantes en `docs/design-system.md` y `bitacora_de_cambios.md` si se implementan.
