# Documentation And Commits

## Regla central

Documentar en la **misma iteración** que el código/datos/estructura. No existe "lo documento después".

## Qué cuenta como significativo

Feature nuevo, extensión de feature, refactor visible (renombres, paths críticos), cambio operativo (puerto, comando, prerequisito), reorganización, migración de datos/tokens, **bug fix con cambio de comportamiento observable**.

## Documentos a actualizar

| Cambio | Documento |
|--------|-----------|
| Arquitectura, puerto, path crítico | `AGENTS.md` |
| Subsistema/servicio/proyecto nuevo | Home Hub (`src/riot_lol_cli/home/`) + contrato UI (`agent-workflow.md`) |
| Ownership/estructura por proyecto | `projects/README.md` |
| Setup/ejecución | `docs/getting-started.md` |
| API/schema Draft Advisor | `docs/draft_advisor/README.md` |
| API/dashboard Meta Analyzer | `docs/meta_analyzer/README.md` |
| Tokens/componentes visuales | `docs/design-system.md` |
| Estrategia de draft | `KB/` + JSON estructurado |
| **Cualquier cambio significativo** | `bitacora_de_cambios.md` |

## Bitácora — formato

```markdown
## [YYYY-MM-DD] Título breve

### Qué se hizo
- Descripción concisa de cada cambio.

### Causa raíz (si fue bug fix)
- Por qué ocurrió + qué impide que vuelva a ocurrir (test guardrail, regla, etc.).

### Archivos modificados
- `ruta/archivo` — decisión relevante.
```

## Cierre obligatorio: lista de archivos

La respuesta final al usuario **debe** terminar con:

- **Archivos creados** — bullets con paths relativos.
- **Archivos modificados** — bullets con paths relativos.

Si la lista es vacía: decir "Sin archivos nuevos/modificados". No omitir la sección. Esto da blast radius sin leer el diff.

## Conventional Commits

```
<type>(<scope>): <description>
```

Types: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `style`, `perf`.
Scopes frecuentes: `cli`, `api`, `meta`, `draft`, `dashboard`, `splash`, `db`, `scripts`, `docs`.

- Descripción imperativa, primera línea ≤72 chars.
- Un commit por cambio lógico.
- Cuerpo en español si hace falta contexto.
