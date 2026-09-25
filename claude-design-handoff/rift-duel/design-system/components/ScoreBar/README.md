# ScoreBar

Barra de progreso del source: etiqueta, riel y valor.

- El relleno por defecto es un degradé de `arc-cyan` a `arc-gold`, para métricas neutras ("Pool usada").
- `score-bar-fill side` (adición de Rift Duel) usa el color del lado del ancestro `.side-blue` o `.side-red`: el CS de cada jugador.
- El ancho del relleno es el porcentaje (`style="width: 64%"`) y el valor siempre va escrito al lado.
- Lo que aportás: `.score-factor` con `.score-factor-label`, `.score-bar-track > .score-bar-fill` y `.score-factor-value`.
