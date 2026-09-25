# Segmented

Selector compacto del source; en Rift Duel sirve para moverse entre P1, P2 y P3.

- La opción activa lleva `aria-pressed="true"` (o la clase `active`) y se pinta en `arc-gold` con texto `forge-black`.
- Hasta 4 opciones cortas.
- Lo que aportás: un contenedor `.segmented` con `role="group"` y `aria-label`, y un `<button>` por opción.
