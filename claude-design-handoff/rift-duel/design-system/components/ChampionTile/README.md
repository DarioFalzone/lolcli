# ChampionTile

Casilla de un campeón de la pool: retrato placeholder con la inicial, nombre y estado. Deriva de `.slot` y `.champ-card` del source.

- Estados, siempre con texto: disponible (sin pill), `picked` con pill `pill-side` "Elegido" y `used` con pill `pill-neutral` "Usado en P1" (regla Fearless).
- En `used`, el retrato y el nombre quedan atenuados, en gris y tachados. Es un estado deshabilitado: la información la lleva la pill.
- El retrato es un placeholder con la inicial sobre el tono deep del lado. Si después hay imágenes, van dentro de `.champ-portrait` con `object-fit: cover`. Nada de splash arts oficiales.
- Lo que aportás: `.champ-tile` con `side-blue` o `side-red` (o dentro de un ancestro con esa clase), `.champ-portrait` con la inicial, `.champ-name` y la pill del estado.
