# MatchTracker

Seguimiento de la partida en juego: los dos campeones cara a cara, el cronómetro y cómo va cada jugador en las tres condiciones de victoria.

- Una fila por condición: la etiqueta al centro y cada lado en su columna. Las barras crecen desde el centro hacia afuera, en el color del lado.
- Cada valor va escrito ("64 CS", "Torre 81%") y lo que todavía no pasó dice "Pendiente". En la fila de torre, cada lado muestra la vida de su propia torre.
- El cronómetro usa números tabulares; el estado "En juego" va en `pill-cyan`.
- Abajo va la acción para cargar el resultado: `btn-secondary` durante la partida, `btn-primary` cuando terminó.
- Lo que aportás: `.match-tracker` con `.match-tracker-head`, `.match-tracker-body` (`.tracker-champs` y un `.tracker-row` por condición, con `.tracker-cell` `side-blue` y `side-red`) y `.match-tracker-foot`.
