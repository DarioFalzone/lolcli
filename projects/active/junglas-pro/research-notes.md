# Junglas Pro - Research Notes

Notas operativas consolidadas del proyecto standalone. Reemplaza los documentos fragmentados de `docs/` que describian guia operativa, gaps, prompts, paginas de graficos y registro tecnico.

## Linea activa

- App activa: `index.html`.
- Assets locales: `img/`.
- Investigacion extensa: `docs/deeps_searchs/`.
- No tiene servidor, build step ni tests automatizados.
- Abrir `index.html` directamente en el browser.

## Convenciones

- Mantener el proyecto compacto: pagina HTML, assets locales y notas minimas.
- No reintroducir tooling temporal, caches, scripts one-off o documentacion paralela.
- Los retratos locales finales deben permanecer en WEBP salvo decision documentada.
- Si se toca contenido analitico, actualizar esta nota o `PROJECT_HISTORY.md`.
- Si una regla sirve para el Draft Advisor, extraer solo la heuristica a `KB/`, no copiar el portal ni perfiles completos.

## Fuentes y metodologia

La investigacion principal vive en `docs/deeps_searchs/search_profesionales_tierlist.md`. La metodologia pondera:

- titulos internacionales;
- titulos domesticos;
- premios individuales;
- estadisticas competitivas;
- reputacion documentada por analistas/prensa.

Fuentes preferidas:

- LoL Esports / Riot Games para confirmaciones oficiales.
- Gol.gg para KDA, KP, champion pool y datos por torneo.
- Leaguepedia/Liquipedia para palmares y premios.
- Prensa especializada para reputacion y contexto.

## Gaps de verificacion

Datos inferidos pendientes de auditoria:

- Score breakdown por jugador: los subtotales por Internacional, Domestico, Premios, Stats y Reputacion fueron inferidos desde metodologia, player cards y deep research.
- Citas editoriales: algunas blockquotes provienen del deep research y no fueron verificadas contra el articulo original.
- Meta picks por Worlds: los conteos de picks deben cruzarse contra Gol.gg antes de tratarlos como dato final.

Tabla de score observada:

| Jugador | Total |
|---------|-------|
| Canyon | 80 |
| Oner | 80 |
| Peanut | 66 |
| Kanavi | 59 |
| Jankos | 49 |
| Xun | 46 |
| Tian | 44 |
| Blaber | 44 |
| Wei | 43 |
| Xmithie | 42 |
| Jiejie | 37 |
| Inspired | 32 |
| Svenskeren | 32 |
| Pyosik | 30 |
| Broxah | 26 |
| Spica | 19 |
| Closer | 16 |
| Tarzan | 15 |

Discrepancias conocidas:

- Canyon: revisar si Intl 30 sale de Worlds 2020 + MSI 2024 + MSI 2025 o si hay cap/bonus.
- Oner: revisar aplicacion de cap internacional si se cuentan tres Worlds.
- Los jugadores con datos parciales deben marcarse como tal en UI si se exponen subtotales.

## Capa visual y charts

La pagina usa ECharts 5 y Chart.js 4 via CDN (`jsdelivr.net`) sin vendor local. Los charts actuales o planificados deben aportar lectura analitica real:

- ranking horizontal apilado de score;
- radar comparativo de perfil competitivo;
- distribucion por tier;
- LCS vs sin LCS;
- mapa temporal de titulos internacionales.

Criterio anti-bloat: no agregar un chart si solo repite una tabla sin mejorar comparacion, tendencia o auditoria.

## Prompt historico para mejoras visuales

Cuando se delegue una mejora a otro agente, pasar este contexto:

- conservar `index.html` como app standalone;
- mantener estetica LoL/esports premium;
- no agregar framework JS ni build step sin decision explicita;
- todo dato nuevo debe indicar fuente o quedar marcado como inferido;
- actualizar esta nota al cierre.

## Registro tecnico consolidado

- 2026-03-29: se reconstruyo baseline del proyecto como tier list standalone de junglas profesionales.
- 2026-03-29: se integro deep research enciclopedico en `index.html`.
- 2026-03-29: se agregaron fotos oficiales y luego retratos locales en WEBP.
- 2026-03-29: se compacto el proyecto a una linea activa y se eliminaron herramientas temporales.
- 2026-03-29: se agrego capa de charts con ECharts/Chart.js y se documentaron gaps de verificacion.
- 2026-04-30: el proyecto fue promovido desde legacy a `projects/active/junglas-pro/`.
