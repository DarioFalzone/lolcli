# Paginas de graficos

## Proposito
Este documento registra las librerias de charts integradas en `index.html`, sus roles, y los criterios de seleccion. Ambas librerias estan en produccion desde 2026-03-29 cargadas via CDN oficial.

## Librerias elegidas

### 1. Apache ECharts
- Sitio oficial:
  - `https://echarts.apache.org/en/index.html`
- Documentacion:
  - `https://echarts.apache.org/handbook/en/`
  - `https://echarts.apache.org/en/api.html`
- Ejemplos:
  - `https://echarts.apache.org/examples/en/index.html`
- Recursos utiles:
  - `https://echarts.apache.org/en/cheat-sheet.html`
  - `https://echarts.apache.org/en/theme-builder.html`
- Por que entra en este proyecto:
  - tiene mas de 20 tipos de graficos
  - soporta Canvas y SVG
  - maneja `dataset` y `transform`
  - sirve mejor para dashboards analiticos pesados y composiciones ricas
- Rol sugerido en esta pagina:
  - secciones analiticas complejas
  - comparativas multi-serie
  - timelines mas ricos que el bloque actual
  - visualizaciones donde valga la pena explotar interaccion, zoom, tooltip y estados

### 2. Chart.js
- Sitio oficial:
  - `https://www.chartjs.org/docs/latest/`
- API:
  - `https://www.chartjs.org/docs/latest/api/`
- Samples:
  - `https://www.chartjs.org/docs/latest/samples/information.html`
- Usage:
  - `https://www.chartjs.org/docs/latest/getting-started/usage.html`
- Performance:
  - `https://www.chartjs.org/docs/latest/general/performance.html`
- Por que entra en este proyecto:
  - es rapido de integrar
  - es muy bueno para bar, line, radar, doughnut, pie y scatter
  - tiene una capa de uso simple para graficos narrativos y compactos
- Rol sugerido en esta pagina:
  - graficos directos y faciles de leer
  - bloques livianos de resumen
  - charts donde prime claridad sobre complejidad

## Estrategia recomendada
- No usar ambas librerias para hacer exactamente el mismo trabajo.
- Usar ECharts para lo que hoy el proyecto no logra bien con JS custom:
  - comparativas ricas
  - filtros visuales
  - composicion de multiples series
  - timeline o secciones derivadas de datasets
- Usar Chart.js donde convenga mantener velocidad de implementacion y limpieza:
  - score ranking
  - distribucion por tier
  - radar de logros o premios
  - series sencillas con lectura inmediata

## Secciones potenciales de alto valor
- Reemplazo del bar chart actual por un chart real con mejor tooltip, leyenda y animacion.
- Score descompuesto por categorias:
  - logro internacional
  - titulos domesticos
  - premios individuales
  - stats competitivas
  - reputacion
- Distribucion por tier y por estatus `LCS` vs `sin LCS`.
- Timeline enriquecido con vista mas legible y comparativa por año.
- Heatmap o matriz de logros por jugador y torneo si la data de la tabla alcanza.
- Radar por jugador top para comparar perfiles de legado.

## Criterios de integracion
- La pagina activa sigue siendo `index.html`.
- El proyecto debe mantenerse compacto; cualquier incorporacion de librerias tiene que justificarse con valor real.
- Si se usan CDNs oficiales, documentar la decision.
- Si se separa codigo, evitar reabrir una segunda arquitectura paralela.
- No dejar charts redundantes: si un chart viejo queda reemplazado, debe salir del HTML final.

## Nota operativa
- Antes de tocar esta capa, leer:
  - `docs/registro-tecnico.md`
  - `docs/guia-operativa-junglas.md`
  - `docs/deeps_searchs/search_profesionales_tierlist.md`
- Despues del cambio, actualizar `docs/registro-tecnico.md`.
