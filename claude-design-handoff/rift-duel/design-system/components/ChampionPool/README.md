# ChampionPool

La pool de un jugador: 5 casillas de campeón con su estado, bajo un encabezado con el lado, el nombre y cuántos quedan disponibles.

- Una por jugador, en su columna: la del lado azul a la izquierda y la del rojo a la derecha. Se ve siempre, también durante la partida.
- El contador dice cuántos campeones quedan sin usar ("3 de 5 disponibles").
- Pensada para columnas de 560px o más. Más angosta, la pill del estado pasa a dos líneas en vez de salirse de la casilla.
- Pool vacía: reemplazá la grilla por un `state-block` "Pool sin cargar".
- Lo que aportás: `.champ-pool` con `side-blue` o `side-red`, `.champ-pool-head` (`side-tag`, `<h3>` y `.champ-pool-count`) y `.champ-pool-grid` con 5 `champ-tile`.
