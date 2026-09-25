# StateBlock

Bloques de estado vacío y de error del source, y el skeleton de carga.

- `state-block` para vacío ("Pool sin cargar") y `state-block error` cuando algo falló: el título dice qué.
- `skeleton` mientras carga, con el alto del contenido que reemplaza. Nunca un spinner infinito: si la carga falla, pasá a `state-block error`.
- La ayuda (`.hint`) da un dato concreto, no instrucciones de uso.
- Lo que aportás: el contenedor con `.icon` (un carácter), `.title` y `.hint`.
