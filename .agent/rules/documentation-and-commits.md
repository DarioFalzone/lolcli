# Documentation And Commits

Protocolo documental y convenciones de commits.

## Regla central

La documentacion se actualiza en la misma iteracion que el codigo, datos o estructura que la origina. No existe "documentar despues".

## Que cuenta como iteracion significativa

| Tipo | Ejemplos |
|------|----------|
| Feature nuevo | Endpoint, pagina, comando o flujo |
| Extension de feature | Nuevo parametro, modo, variante o dato consumido |
| Refactor visible | Renombrar schemas, payloads, rutas o archivos criticos |
| Cambio operativo | Puerto, comando, script o prerequisito |
| Reorganizacion | Mover carpetas, fusionar docs, crear/bajar proyectos |
| Migracion de datos/tokens | JSON, pesos, tokens CSS |
| Bug fix visible | Cambia comportamiento que el usuario o agente debe conocer |

## Documentos a revisar

| Cambio | Documento obligatorio |
|--------|-----------------------|
| Arquitectura, puerto, path critico | `AGENTS.md` |
| Ownership o estructura por proyecto | `projects/README.md` |
| Docs fusionadas, movidas o canonicas | `docs/README.md` |
| Comandos de setup/ejecucion | `docs/getting-started.md` |
| API o schema Draft Advisor | `docs/draft_advisor/README.md` |
| API/dashboard Meta Analyzer | `docs/meta_analyzer/README.md` o `docs/dashboard/README.md` |
| Tokens/componentes visuales | `docs/design-system.md` |
| Estrategia de draft | `KB/` y JSON estructurado si aplica |
| Cambio significativo cualquiera | `bitacora_de_cambios.md` |

## Bitacora

Usar este formato:

```markdown
## [YYYY-MM-DD] Titulo breve

### Que se hizo
- Descripcion concisa de cada cambio principal.

### Archivos modificados clave
- `ruta/archivo` - decision relevante.
```

## Checklist post-accion (obligatorio antes de cada commit)

Esta lista es no negociable. Ejecutarla despues de cada cambio de codigo, datos o estructura, antes de commitear.

1. **Bitacora**: si el cambio es significativo (ver tabla de arriba), agregar entrada en `bitacora_de_cambios.md` con fecha, que se hizo, archivos clave y resultado de verificacion.
2. **Docs tecnicas**: si cambia un endpoint, puerto, comando, schema, path critico o prerequisito, actualizar el documento correspondiente de la tabla "Documentos a revisar".
3. **Bug fix visible**: si el fix cambia comportamiento observable por el usuario o agente, documentarlo en la bitacora con causa raiz + verificacion.
4. **CI / dependencias**: si el cambio agrega, quita o modifica una dependencia o prerequisito de sistema (e.g. playwright, Python version floor, nueva env var), verificar que `requirements.txt`, `requirements-dev.txt`, `docs/getting-started.md` y el workflow de CI reflejen el cambio.
5. **Tests**: si el fix cierra un bug reproducible, confirmar que existe o se agrego un test que lo habria atrapado. Mencionar en la bitacora.
6. **Reglas de agente**: si el cambio introduce una convencion nueva o un gotcha (e.g. nueva limitacion de version, patron obligatorio, exclusion de ruff), registrarla en la rule canonica de `.agent/rules/` correspondiente.

> **Por que**: la documentacion que no se actualiza en la misma iteracion que el codigo rota y acumula drift. Cada "lo hago despues" es deuda que ningun agente futuro puede resolver sin leer el codigo completo.

## Conventional Commits

Formato:

```text
<type>(<scope>): <description>
```

Types: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `style`, `perf`.

Scopes frecuentes: `cli`, `api`, `meta`, `draft`, `dashboard`, `splash`, `db`, `scripts`, `docs`.

Reglas:

- Descripcion en imperativo e ingles.
- Primera linea maximo 72 caracteres.
- Un commit por cambio logico.
- Cuerpo en espanol si hace falta contexto.
