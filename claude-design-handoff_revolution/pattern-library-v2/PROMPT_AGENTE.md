# Prompt para Claude local — landear Pattern Library v2 en `riot_lol_cli`

Copiá este prompt entero en Claude Code (o tu agente local) cuando estés
parado en la raíz del repo `riot_lol_cli`.

---

## Contexto

Cloud Claude diseñó la **Pattern Library v2** — un sistema visual transversal
para todas las surfaces del proyecto. Tengo un bundle con todos los archivos
necesarios. No puedo hacer push directo a `main`; necesito que abras un PR.

**Bundle:** `claude-design-handoff/pattern-library-v2/` (relativo al repo).

Estructura del bundle:

```
claude-design-handoff/pattern-library-v2/
├── PR_BODY.md            # cuerpo listo para pegar como descripción del PR
├── PROMPT_AGENTE.md      # este archivo
├── CHANGES.md            # diff resumido y plan de aplicación paso a paso
└── files/
    ├── design-system/
    │   ├── tokens.css    # v2 canónica → reemplaza la actual
    │   └── patterns.css  # NUEVO → drop-in
    └── reference/
        ├── Pattern Library.html
        ├── tokens.css     # mirror para que la doc abra standalone
        └── patterns.css   # mirror, idem
```

## Tarea

1. **Leé estos archivos en orden** (sin saltarte ninguno):
   - `claude-design-handoff/pattern-library-v2/PR_BODY.md`
   - `claude-design-handoff/pattern-library-v2/CHANGES.md`
   - `claude-design-handoff/pattern-library-v2/files/design-system/tokens.css`
   - `claude-design-handoff/pattern-library-v2/files/design-system/patterns.css`
   - El `tokens.css` actual del repo en
     `src/riot_lol_cli/draft_advisor/static/design-system/tokens.css`
   - `docs/design-system.md`
   - `src/riot_lol_cli/draft_advisor/static/design-system/README.md`
   - `bitacora_de_cambios.md`

2. **Validá compatibilidad de `tokens.css` v2** comparando con el actual.
   Confirmá que es superset (añade variables, no renombra ni elimina).
   Si encontrás algún token actual que NO esté en v2, **avisame antes de
   continuar** — no lo borres a ciegas.

3. **Aplicá los cambios exactos del bundle:**

   ```
   # NUEVO
   cp claude-design-handoff/pattern-library-v2/files/design-system/patterns.css \
      src/riot_lol_cli/draft_advisor/static/design-system/patterns.css

   # REEMPLAZO (con backup)
   cp src/riot_lol_cli/draft_advisor/static/design-system/tokens.css \
      src/riot_lol_cli/draft_advisor/static/design-system/tokens.css.bak
   cp claude-design-handoff/pattern-library-v2/files/design-system/tokens.css \
      src/riot_lol_cli/draft_advisor/static/design-system/tokens.css

   # DOC PAGE
   mkdir -p claude-design-handoff/patrones_diseños_claude_design
   cp claude-design-handoff/pattern-library-v2/files/reference/* \
      claude-design-handoff/patrones_diseños_claude_design/
   ```

4. **Editá** `docs/design-system.md` añadiendo la sección "Pattern Library
   v2 — `patterns.css`" según `CHANGES.md` (sección 4).

5. **Editá** `src/riot_lol_cli/draft_advisor/static/design-system/README.md`
   añadiendo `patterns.css` al orden de carga documentado (debajo de
   `tokens.css`, encima de `components.css`).

6. **Editá** `bitacora_de_cambios.md` con una entrada de fecha siguiendo el
   formato existente de la bitácora.

7. **Probá localmente** que las 4 surfaces se ven idénticas a antes del
   cambio:
   - Levantá el server (`make dev` o equivalente).
   - Visitá Items Browser, Jungle Meta, Meta Scraper y Draft Advisor.
   - Abrí `claude-design-handoff/patrones_diseños_claude_design/Pattern Library.html`
     en el browser y verificá que carga sin errores de consola.
   - Si rompiste algo, **rollback** con el `.bak` de `tokens.css` y avisame.

8. **Eliminá el `.bak`** de `tokens.css` solo cuando todo funcione.

9. **Creá la rama y el commit:**

   ```
   git checkout -b feat/pattern-library-v2
   git add src/riot_lol_cli/draft_advisor/static/design-system/
   git add docs/design-system.md
   git add bitacora_de_cambios.md
   git add claude-design-handoff/patrones_diseños_claude_design/
   git status   # confirmá la lista antes de commitear
   git commit -m "feat(design-system): Pattern Library v2 — patterns.css drop-in + reference page"
   ```

10. **Pusheá la rama y abrí el PR** usando `PR_BODY.md` como cuerpo:

    ```
    git push -u origin feat/pattern-library-v2
    gh pr create \
      --title "feat(design-system): Pattern Library v2 — patterns.css drop-in + reference page" \
      --body-file claude-design-handoff/pattern-library-v2/PR_BODY.md \
      --base main
    ```

11. **Reportame:**
    - URL del PR.
    - Cualquier discrepancia entre el `tokens.css` actual y v2 que detectaste.
    - Cualquier surface que se vea distinta después del cambio (no debería
      pasar; si pasa, es bug y hay que rollback antes de mergear).

## Reglas

- **No mergeés**. Yo reviso y mergeo desde GitHub.
- **No toques** `components.css`, `compat-spa.css`, `compat-dashboard.css`,
  ningún HTML, JS, Python, ni archivos de surfaces. Esta PR es solo de
  design-system + docs + bitácora.
- **No reformatees** el `tokens.css` v2 — copialo tal cual viene del bundle.
- Si encontrás conflictos con `main` actualizado, hacé `git pull --rebase`
  primero y reportame.
- Si hay algún paso ambiguo, **preguntá antes de inventar**.

## Definition of Done

- [ ] Rama `feat/pattern-library-v2` pusheada.
- [ ] PR abierto contra `main` con `PR_BODY.md` como cuerpo.
- [ ] Las 4 surfaces se ven idénticas a antes del cambio.
- [ ] La doc page abre sin errores de consola.
- [ ] Reporte de URL del PR + cualquier hallazgo entregado al usuario.
