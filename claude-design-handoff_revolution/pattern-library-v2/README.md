# Pattern Library v2 — Bundle de handoff

Cloud Claude generó este bundle. Local Claude (o vos) lo aplica al repo y
abre el PR. Sin push directo a main.

## Qué hay acá

```
pattern-library-v2/
├── README.md              # este archivo
├── PR_BODY.md             # cuerpo listo para pegar en GitHub
├── PROMPT_AGENTE.md       # prompt para tu Claude local — copialo entero
├── CHANGES.md             # plan granular paso a paso
├── CONTEXT.md             # memoria de proyecto: decisiones, descartes, roadmap
└── files/
    ├── design-system/
    │   ├── tokens.css     # v2 canónica → reemplaza la actual del repo
    │   └── patterns.css   # NUEVO → drop-in
    └── reference/
        ├── Pattern Library.html  # doc page navegable (17 secciones)
        ├── tokens.css            # mirror para abrir la doc standalone
        └── patterns.css          # mirror, idem
```

## Cómo usar

1. **Bajá el bundle** al root de tu repo `riot_lol_cli` (debe quedar como
   `<repo>/claude-design-handoff/pattern-library-v2/`).
2. **Abrí Claude Code** parado en la raíz del repo.
3. **Pegá entero** el contenido de `PROMPT_AGENTE.md` como prompt inicial.
4. Claude local va a:
   - Validar compatibilidad de tokens.
   - Aplicar los cambios.
   - Probar las 4 surfaces.
   - Abrir un PR contra `main` usando `PR_BODY.md` como cuerpo.
5. **Vos revisás y mergeás** desde GitHub.

## Resumen del cambio

- ➕ `patterns.css` — 18 patrones drop-in HTML+CSS vanilla.
- 🔄 `tokens.css` → v2 (superset compatible — cero breaking).
- 📖 Doc page de referencia con tokens, demos y checklist.
- 📝 Updates a `docs/design-system.md`, `README.md` del DS y `bitacora_de_cambios.md`.

**Sin cambios en:** `components.css`, `compat-*.css`, ningún HTML / JS /
Python de surfaces. Esta PR es 100% aditiva.

## Si algo sale mal

`tokens.css` se reemplaza con backup `.bak`. Si alguna surface se ve
distinta después del cambio:

```bash
mv src/riot_lol_cli/draft_advisor/static/design-system/tokens.css.bak \
   src/riot_lol_cli/draft_advisor/static/design-system/tokens.css
```

…y reportá la diff que detectaste para que ajustemos antes de re-aplicar.
