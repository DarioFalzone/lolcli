# SeriesScore

Marcador de la serie: partidas ganadas por lado y el estado de cada partida.

- Va al centro, entre las columnas de cada lado, en todas las pantallas de la serie.
- Cada partida es un `game-pip` con texto: `won` más `side-blue` o `side-red` y el nombre del ganador; `live` con "En juego"; sin modificador, "Pendiente" en `state-neutral`.
- Las victorias (`series-wins`) van en el color del lado, con números tabulares.
- Lo que aportás: `.series-score` con dos `.series-side` (`side-blue` a la izquierda, `side-red` a la derecha), `.series-mid` con `.series-format` y la lista `.series-games`, y un `aria-label` con el marcador en texto.
