# GameResult

Resultado de una partida: quién ganó, con qué campeón, por qué condición y en qué minuto, y cómo queda la serie.

- El ganador lleva borde `arc-gold`, brillo chico y pill "Ganó". El perdedor se atenúa sin tinte ni borde de su lado y con el nombre en `text-secondary`. Nunca en rojo.
- La condición que definió la partida va arriba a la derecha, como `win-cond decided` con el minuto.
- Abajo, el marcador actualizado de la serie.
- Lo que aportás: `.game-result` con `.game-result-head`, `.game-result-body` con dos `.result-side` (`side-blue` a la izquierda y `side-red` a la derecha, cada uno `winner` o `loser`) y `.game-result-foot`.
