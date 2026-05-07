# Legacy Projects

Este directorio agrupa proyectos, copias y experimentos que conviven en el repo
pero no forman parte del runtime activo de `src/riot_lol_cli/`.

## Criterio

- Se preservan para consulta historica o reutilizacion futura.
- No se deben modificar salvo una tarea explicita sobre ese proyecto legacy.
- Si un legacy vuelve a estar activo, crear primero un manifest en
  `projects/active/` y actualizar `AGENTS.md`.

## Contenido esperado

- `riot-lol-cli/`: copia antigua/no activa del paquete.
- `ddragon-item-scraper/`: scraper legacy de items/Data Dragon.
- `adc-screenshots/`: experimento de screenshots ADC.
- `patch-notes-scraper-v33a/`: scraper legacy de notas de parche.
- `patch-notes-web-v33b/`: web/proyecto legacy de notas de parche.

Nota: la investigacion de junglas profesionales fue promovida a
`projects/active/junglas-pro/` el 2026-04-30.
