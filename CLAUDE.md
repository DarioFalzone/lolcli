# Claude Code Shim

Claude Code debe usar este archivo solo como puntero de arranque.

1. Leer `AGENTS.md` en la raiz como mapa maestro del repo.
2. Leer `projects/README.md` para ubicar el proyecto logico afectado.
3. Leer las reglas canonicas en `.agent/rules/`:
   - `agent-workflow.md`
   - `engineering-standards.md`
   - `documentation-and-commits.md`
   - `security-and-testing.md`
4. Actualizar `bitacora_de_cambios.md` en toda iteracion significativa.

No crear ni mantener reglas largas especificas de Claude en este archivo. Las reglas operativas viven en `.agent/rules/` y `AGENTS.md` sigue siendo el entrypoint comun para agentes.
