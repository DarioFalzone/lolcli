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
