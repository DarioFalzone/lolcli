# Pill

Etiqueta corta en mayúsculas para un estado: una o dos palabras.

- `pill-gold` para el ganador ("Ganó", "Campeón"), `pill-cyan` para "En juego" y `pill-neutral` para "Pendiente" y "Usado en P1".
- `pill-success`, `pill-warning` y `pill-error` son estados de sistema: guardado, falta confirmar, sin conexión. No marcan al ganador ni al perdedor.
- `pill-side` (adición de Rift Duel) toma el color del lado del ancestro `.side-blue` o `.side-red`: "Elegido".
- `pill-dashed` pone el borde punteado.
- Lo que aportás: un `<span class="pill pill-…">` con el texto. El texto siempre acompaña al color.
