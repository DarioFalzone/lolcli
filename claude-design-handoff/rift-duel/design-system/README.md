Rift Duel es el sistema visual para series 1v1 de League of Legends entre amigos. Toma el Hextech oscuro de LOLCLI (Pattern Library v2) y le suma un color por lado: azul para el lado izquierdo y rojo para el derecho. Sirve para mockups y pantallas de seguimiento de una serie al mejor de 3: previa, draft, partida en curso, resultado y campeón.

## Voz y contenido

- Escribí en español rioplatense, corto y directo. Cuando le hablás al jugador, con voseo: "Elegí tu pick".
- Dejá la jerga gamer sin traducir: pick, pool, First Blood, CS, Fearless, Bo3, remake.
- Botones con el verbo primero, en infinitivo: "Arrancar Partida 1", "Confirmar picks", "Cargar resultado".
- Títulos gigantes en mayúsculas ("QUEX VS MINGO", "MINGO GANA 2-1"). El resto, con mayúscula inicial: "Pool de Quex", "Partida 3".
- Formatos fijos: marcador "2-1", tiempo de partida "06:42", "100 CS", partidas "P1", "P2", "P3".
- Sin emojis y sin textos que expliquen cómo usar la pantalla: la estructura se explica sola.

## Lados y jugadores

- El lado define el color, no el jugador. `blue-side` va siempre a la izquierda y `red-side` siempre a la derecha, en todas las pantallas. En el ejemplo, Quex es el lado azul y Mingo el rojo.
- Cada lado lleva el nombre del jugador y la etiqueta "Lado azul" o "Lado rojo" en `type-micro`: el color nunca es la única señal.
- Panel de un lado: fondo `blue-side-soft` o `red-side-soft` sobre `surface-card`, borde de 1px en `blue-side` o `red-side` y texto `text-primary`.
- Relleno intenso (`blue-side`, `red-side`) solo en bloques chicos, barras y marcas; el texto encima va en `text-on-side`.
- Paneles grandes de identidad: `blue-side-deep` o `red-side-deep` con `text-primary`. Nunca `text-secondary` sobre un tono deep.
- `red-side` no significa error ni derrota. Los errores de sistema usan `state-error` y siempre llevan texto.

## Ganador, perdedor y estado de la serie

- El ganador se marca en dorado: `arc-gold` en borde y texto, `glow-gold` como brillo. Fuera de la acción principal, es el único lugar donde va `glow-gold`.
- Al perdedor se lo atenúa sin opacidad: sin el tinte ni el borde de su lado y con el nombre en `text-secondary`, así su texto sigue arriba de 4.5:1. No se lo pinta de rojo ni de `state-error`.
- Partida pendiente: `state-neutral` con el texto "Pendiente". En juego: `arc-cyan` con "En juego". Jugada: el color del lado ganador y la condición que la definió.
- Condiciones de victoria: "First Blood", "100 CS" y "Primera torre", siempre escritas. La que definió la partida va en dorado y con el minuto: "First Blood · 06:42".

## Pools y regla Fearless

- La pool de cada jugador (5 campeones) se ve siempre, del lado de ese jugador.
- Cada estado de campeón lleva texto además del color:
  - Disponible: borde `border-subtle`, nombre en `text-primary`.
  - Elegido: borde de 2px en el color del lado y pill "Elegido".
  - Usado (Fearless): retrato y nombre al 45%, en gris y tachados, con pill "Usado en P1" en `state-neutral`. Es un estado deshabilitado y la información la lleva la pill. No se puede volver a elegir en la serie.
- Retratos: placeholders cuadrados con la inicial del campeón en `type-display-md`, sobre el tono deep de su lado.

## Color

- Fondo de página `forge-black`. Cards y paneles en `surface-card`, hover y elementos elevados en `surface-raised`, modales y toasts en `surface-overlay`, inputs y encabezados de tabla en `forge-darker`.
- `arc-gold` marca jerarquía, acción principal, foco y ganador. Una sola acción principal (`btn-primary`) por pantalla.
- `arc-cyan` es solo información: reglas, ayudas, estado "En juego". Nunca identifica a un jugador.
- Texto: `text-primary` para contenido, `text-secondary` para metadata y `text-on-gold` sobre dorado. `text-tertiary` solo en placeholders.
- Todo texto cumple 4.5:1 sobre su fondo, y la nota de cada token de texto dice sobre qué fondos se lee. Dos excepciones vienen del source y se mantienen: `text-tertiary` (2.6:1, solo placeholders) y `state-error` sobre `surface-raised` (4.45:1).

## Tipografía

- `type-hero`: Anton itálica en mayúsculas, solo para el título gigante ("QUEX VS MINGO") y el campeón de la serie.
- `type-display-*` (Outfit) para títulos, marcador y cronómetro. Los números van con `font-variant-numeric: tabular-nums`.
- `type-body-*` (Inter) para el resto. Etiquetas en mayúsculas con `type-caption-sm`, `type-micro` o `type-pill`.
- Las tres familias salen de Google Fonts: Inter 400–700, Outfit 500–900 y Anton 400.

## Espacio, radios y layout

- Espaciado en pasos de 4px, de `space-1` a `space-20`. Padding de card `space-5`, de panel `space-4` y del hero `space-12` × `space-8`.
- Radios chicos o medianos: `radius-sm` en botones y casillas, `radius-md` en cards, `radius-lg` en hero y modales, `radius-pill` en pills y barras.
- Botones y controles miden al menos `touch-target` (44px) de alto.
- Pantallas de escritorio en `container-2xl` (1440px): lado azul en la columna izquierda, marcador al centro y lado rojo a la derecha.

## Bordes, sombras y brillo

- Bordes finos dorados de baja opacidad: `border-subtle` por defecto, `border-metal` en controles y `border-metal-strong` en hover y activo.
- `elevation-1` para cards, `elevation-2` en hover y `elevation-4` para modales.
- El brillo es la firma Hextech, no decoración: `glow-gold` solo en la acción principal y en el ganador.
- Foco de teclado con `focus-ring`. Dentro de modales da 2.9:1 sobre `surface-overlay`, así que ahí sumale `border-color: var(--arc-gold)` al control con foco.
- El hero lleva el patrón diagonal sutil del source: líneas a 45° cada 60px, en dorado al 4%.

## Movimiento

- Transiciones cortas: 120ms para hover de controles, 180ms por defecto y 600ms para llenar barras de progreso.
- Respetá `prefers-reduced-motion`: sin desplazamientos ni brillos animados.
- Nada de spinners infinitos: skeleton mientras carga y, si falla, un bloque de error con texto.

## Imágenes e íconos

- No hay logo: el nombre va en tipografía, con `type-hero`.
- El source no define un set de íconos: usá texto. Para cerrar, el carácter "×".
- Nada de splash arts ni logos oficiales de Riot: los retratos son placeholders con la inicial.

## Componentes

Todos son HTML + CSS: las clases viven en `components/bundle.css` y no hay JavaScript. Las previews son versiones estáticas.

- Del source (Pattern Library v2), sin cambios: Button, Segmented, Pill, Banner (con toast), StateBlock (con skeleton), Card, StatStrip, DataTable y ScoreBar.
- Adiciones intencionales de Rift Duel, porque el source no tiene nada para un duelo por lados: VersusHero, SeriesScore, PlayerCard, ChampionTile, ChampionPool, WinCondition, MatchTracker y GameResult.
- Las adiciones se pintan con `side-blue` y `side-red`, que definen `--side`, `--side-soft` y `--side-deep`. También se agregaron `side-tag` (la etiqueta "Lado azul" o "Lado rojo"), `pill-side` y la variante `score-bar-fill side`.

## No sincronizado

- No se trajeron los colores `tier-*` ni los patrones de tier list (Tier tabs, Tier row): Rift Duel no tiene tier lists.
- Tampoco los patrones del source que un duelo no usa: control panel, input y search, tabs con contador, cat-card, entity-card, modal, y champ-card y slot (los reemplaza ChampionTile).
- Los tiempos de movimiento (`motion-*`, `ease-out`) no tienen familia de tokens y viven en `components/bundle.css`.
- Las fuentes no tienen archivos en el sistema: se cargan desde Google Fonts.
