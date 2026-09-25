# Button

Botones del source: `btn-primary` para la única acción principal de la pantalla, `btn-secondary` y `btn-ghost` para el resto.

- `btn-primary` una sola vez por pantalla, para lo que la pantalla viene a hacer: "Arrancar Partida 1", "Confirmar picks".
- `btn-secondary` para acciones de apoyo ("Cargar resultado") y `btn-ghost` para las de baja prioridad ("Ver reglas").
- Texto con el verbo primero, en infinitivo.
- Deshabilitado con el atributo `disabled` (o `aria-disabled="true"`): queda al 45% de opacidad. Usalo mientras falten datos, por ejemplo hasta que los dos jugadores eligen pick.
- `btn-icon` (del source) es el botón cuadrado de 44px para una sola acción con un carácter, como "×".
- Lo que aportás: un `<button type="button" class="btn btn-primary">` (o la variante) con el texto.
