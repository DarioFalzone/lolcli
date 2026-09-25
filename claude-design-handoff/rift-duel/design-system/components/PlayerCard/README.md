# PlayerCard

Tarjeta de identidad de un jugador: lado, nombre y cómo va en la serie.

- Una por jugador, en su columna: lado azul a la izquierda y rojo a la derecha.
- Fondo con el tinte del lado (`--side-soft`) y borde en el color del lado.
- `winner` al terminar la serie: borde `arc-gold`, `glow-gold` y pill "Campeón".
- `loser`: se atenúa sin opacidad, sacándole el tinte y el borde del lado, con el nombre en `text-secondary`. Nunca en rojo.
- Lo que aportás: `.player-card` con `side-blue` o `side-red`, `.player-card-head` (`side-tag` y, si corresponde, la pill), `.player-name` y `.player-stats` (una lista `<dl>` de hasta 3 datos).
