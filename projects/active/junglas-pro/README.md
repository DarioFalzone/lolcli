# Junglas Pro

Proyecto activo standalone de investigacion sobre junglas profesionales de
League of Legends.

## Proposito

Mantener una pagina y documentos de investigacion sobre jugadores, metodologia
de tier list, fuentes consultadas y material visual asociado.

## Rutas reales

- Portal HTML: `projects/active/junglas-pro/index.html`
- Notas de investigacion consolidadas: `projects/active/junglas-pro/research-notes.md`
- Deep research completo: `projects/active/junglas-pro/docs/deeps_searchs/`
- Imagenes: `projects/active/junglas-pro/img/`
- Reglas heredadas del proyecto: `projects/active/junglas-pro/.agents/`
- Historial de promocion: `projects/active/junglas-pro/PROJECT_HISTORY.md`

## Flujo principal

`research-notes.md` + `docs/deeps_searchs/` -> curacion manual -> `index.html` -> consulta local en browser.

## Comandos

No tiene servidor ni build step obligatorio. Abrir `index.html` directamente en
el navegador.

## Relacion con KB

La investigacion completa queda en este proyecto. Solo se debe copiar a `KB/`
contenido estrategico reutilizable por el Draft Advisor, como arquetipos de
jungla, patrones de presion, pathing o sinergias bot/jungla.

## Deuda conocida

- El contenido viene de una etapa standalone y puede usar convenciones distintas
  a las del repo principal.
- Las fuentes y rankings deben revisarse antes de tratarse como datos vigentes.
- No tiene tests automatizados.

## Documentacion interna

- `research-notes.md`: operacion, gaps de verificacion, charts, prompts historicos y registro tecnico consolidado.
- `PROJECT_HISTORY.md`: historial de promocion desde legacy a proyecto activo.
- `docs/deeps_searchs/`: investigacion extensa original; no es doc operacional del repo principal.
