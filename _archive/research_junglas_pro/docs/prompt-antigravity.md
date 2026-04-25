# Prompt para Antigravity

Quiero que tomes este repo como una pagina analitica premium de League of Legends y ejecutes una mejora fuerte de su capa de visualizacion.

## Contexto obligatorio antes de tocar nada
Lee primero estos archivos:
- `docs/registro-tecnico.md`
- `docs/guia-operativa-junglas.md`
- `docs/paginas de graficos.md`
- `docs/deeps_searchs/search_profesionales_tierlist.md`
- `docs/deeps_searchs/Tier list analítico enciclopédico de junglas profesionales`
- `index.html`
- `.agents/rules/nuevarule.md`

## Estado actual que debes asumir
- La app activa del repo es una sola pagina autocontenida: `index.html`
- La pagina ya tiene estetica esports y retratos locales `WEBP`
- El chart actual es un bar chart custom inline bastante limitado
- El objetivo no es agregar charts por agregar, sino subir mucho el valor analitico y visual del producto

## Objetivo central
Reemplaza los graficos actuales por una capa de visualizacion mas potente usando estas dos librerias:
- Apache ECharts
- Chart.js

Quiero que les saques valor real. Si para eso tienes que crear nuevas secciones relevantes, hazlo.

## Direccion tecnica
- Usa Apache ECharts para los bloques analiticos mas complejos, interactivos o compuestos.
- Usa Chart.js para los graficos mas directos, narrativos o ligeros.
- No dupliques trabajo entre ambas librerias.
- Cada chart debe existir porque mejora lectura, comparacion o descubrimiento.
- Si un chart viejo deja de tener sentido, eliminalo.

## Lo que busco del resultado
- Mejor lectura del score y del ranking real de junglas
- Mejor explotacion de la metodologia de scoring
- Mejor presentacion de la distribucion por tier, logros y contexto competitivo
- Mas profundidad visual sin convertir la pagina en ruido
- Un resultado con criterio de producto, no solo tecnico

## Ideas de alto valor que puedes implementar si aportan
- Score breakdown por jugador o por tier
- Comparativa entre logros internacionales y domesticos
- Distribucion `LCS` vs `sin LCS`
- Timeline reconstruido con mejor visualizacion
- Heatmap o matriz de logros
- Radar comparativo entre los junglas mas historicos
- Charts que aprovechen tooltips, estados hover, leyendas y filtros

## Direccion visual
Trabaja con sensibilidad Antigravity + Opus:
- look editorial esports premium
- nada generico
- animacion con criterio
- tooltips y leyendas bien diseñados
- composicion que se vea intencional, no dashboard corporativo vacio
- conservar la identidad visual actual de la pagina y elevarla

## Restricciones
- Respeta la arquitectura compacta del repo
- Evita reintroducir una segunda app paralela
- Si incorporas librerias externas, justifica si usas CDN oficial o integracion local
- No rompas mobile
- No sacrifiques legibilidad por efecto visual
- No dejes codigo muerto, charts duplicados o secciones sin valor real

## Entregables esperados
- `index.html` mejorado
- si hace falta, assets minimos o codigo auxiliar realmente justificado
- documentacion actualizada en `docs/registro-tecnico.md`
- si cambias el criterio de graficos o la arquitectura, actualizar tambien `docs/guia-operativa-junglas.md` y `docs/paginas de graficos.md`

## Criterio de calidad
No quiero una integracion superficial de librerias. Quiero que se note por que ECharts y Chart.js merecen estar en esta pagina.

Piensa como si tuvieras que defender cada chart frente a alguien que odia el bloat:
- por que existe
- que insight nuevo aporta
- por que esa libreria es la correcta para ese bloque

## Cierre obligatorio
Cuando termines:
- limpia cualquier residuo
- deja la pagina coherente
- actualiza la documentacion
- deja claro que reemplazaste y que agregaste
