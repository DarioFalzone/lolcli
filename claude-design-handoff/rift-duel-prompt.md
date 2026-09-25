# Claude Design Prompt - Rift Duel (1v1 al mejor de 3)

Prompt para generar en Claude Design los mockups de una serie 1v1 de League of
Legends entre amigos, al mejor de 3 (ejemplo: Quex vs Mingo), con la paleta
Hextech de LOLCLI.

## Para qué sirve

Pegar el bloque "Prompt para Claude Design" como primer mensaje de un proyecto
nuevo en Claude Design. El resultado son pantallas en alta fidelidad con datos
ficticios: se ven como producto terminado, pero los datos son de ejemplo.

## Design system

- Elegir **Rift Duel** como design system del proyecto:
  https://claude.ai/artifact/2pYJqbC4tHCaMhQ5Umiu2N
- Si Claude Design no lo ofrece para elegir, el prompt ya trae los tokens que
  necesita y funciona igual.
- Base: tokens de Pattern Library v2
  (`src/riot_lol_cli/draft_advisor/static/design-system/tokens.css`) más los
  colores de lado (`blue-side-*`, `red-side-*`, `text-on-side`), agregados para
  Rift Duel.

## Adjuntos opcionales

- `src/riot_lol_cli/draft_advisor/static/design-system/tokens.css`
- `src/riot_lol_cli/draft_advisor/static/design-system/patterns.css`

## Supuestos a confirmar antes de la serie

| Tema | Supuesto |
|------|----------|
| Lados | Quex juega del lado azul (izquierda) y Mingo del rojo (derecha). No cambian en toda la serie. |
| Pool | 5 campeones por jugador, definidos antes de la serie. |
| Fearless | Cada jugador usa cada campeón de su pool una sola vez en la serie. |
| Victoria de partida | Gana el primero que consigue First Blood, 100 CS o la primera torre. |
| Serie | Mejor de 3: gana el primero que llega a 2 partidas. |
| Mapa | Carril central de la Grieta del Invocador. |
| Datos | Campeones, horario y resultados son de ejemplo: reemplazarlos por los reales. |

## Prompt para Claude Design

```text
Quiero que diseñes los mockups de "Rift Duel": una serie 1v1 de League of Legends entre amigos, al mejor de 3, que jugamos esta noche.

Contexto
- Es para un grupo de amigos, no para un producto comercial. Se va a ver en un monitor o una tele mientras jugamos, y el resultado final se comparte por WhatsApp.
- Quiero diseño de alta fidelidad, lo más cercano posible a un producto terminado, con los datos ficticios de abajo.
- Usá el design system Rift Duel. Si no lo tenés disponible, usá los tokens de este mensaje tal cual.

Reglas de la serie
- Formato: 1v1, mejor de 3. Gana la serie el primero que gana 2 partidas.
- Lados fijos: Quex juega del lado azul (siempre a la izquierda) y Mingo del lado rojo (siempre a la derecha).
- Pool predefinida: cada jugador tiene 5 campeones y la pool se ve siempre.
- Regla Fearless: cada jugador usa cada campeón de su pool una sola vez en la serie. Un campeón ya usado queda bloqueado y muestra en qué partida se usó ("Usado en P1").
- Cómo se gana una partida: el primero que consigue First Blood, 100 CS o la primera torre.

Datos de ejemplo
- Jugadores: Quex (lado azul) y Mingo (lado rojo).
- Pool de Quex: Ahri, Yasuo, Zed, Syndra, Orianna.
- Pool de Mingo: Viktor, Akali, LeBlanc, Sylas, Katarina.
- Cuándo y dónde: hoy a las 22:00, carril central de la Grieta del Invocador.
- Partida 1: Ahri (Quex) vs Viktor (Mingo). Gana Quex por First Blood a los 06:42.
- Partida 2: Zed (Quex) vs Akali (Mingo). Gana Mingo por 100 CS a los 09:15 (100 a 91).
- Partida 3: Syndra (Quex) vs LeBlanc (Mingo). Gana Mingo por primera torre a los 11:03.
- Resultado final: Mingo gana la serie 2-1.

Pantallas (escritorio 1440 × 900, modo oscuro)
1. Previa de la serie: título grande "QUEX VS MINGO" con "Mejor de 3 · Hoy 22:00", marcador 0-0, las 3 condiciones de victoria y las dos pools completas, una de cada lado. Acción principal: "Arrancar Partida 1".
2. Draft de la Partida 3: las dos pools con el estado de cada campeón (disponible, elegido ahora, usado en P1 o P2 y bloqueado por Fearless). Arriba, el marcador 1-1 y las partidas ya jugadas. Acción principal: "Confirmar picks".
3. Partida en curso (Partida 3): los dos campeones cara a cara, el cronómetro y cómo va cada jugador en las 3 condiciones: First Blood (pendiente), CS (64 contra 58, sobre 100) y primera torre (pendiente, con la vida de cada torre). Acción para cargar quién ganó y por qué condición.
4. Resultado de partida: el ganador destacado en dorado, su campeón, la condición y el minuto en que ganó, y el marcador de la serie actualizado.
5. Campeón de la serie: "MINGO GANA 2-1", resumen de las 3 partidas (campeones, condición, tiempo) y cómo quedaron las pools.
6. Tarjeta para compartir (1080 × 1920): el resultado final, lista para mandar por WhatsApp.

Además mostrá estos estados en alguna pantalla: pool sin cargar (vacía), partida todavía sin resultado y la acción principal deshabilitada.

Dirección visual
- Estética Hextech oscura inspirada en League of Legends: fondo navy casi negro, superficies azul oscuro, bordes finos dorados de baja opacidad y un patrón diagonal sutil en los encabezados.
- Dorado para jerarquía, acción principal, foco y ganador.
- Azul intenso para todo lo de Quex (lado azul) y rojo intenso para todo lo de Mingo (lado rojo): nombre, bordes, barras de progreso y paneles con tinte.
- Cyan solo para información (reglas, ayudas, datos secundarios). Nunca para un jugador.
- Tipografía: Anton itálica en mayúsculas para los títulos grandes ("QUEX VS MINGO"), Outfit para encabezados y números del marcador, Inter para el texto. Números con ancho fijo (tabular).
- Radios de 4 a 12 px, nada muy redondeado.
- Retratos de campeón: placeholders cuadrados con la inicial del campeón sobre el color de su lado. Sin splash arts ni logos oficiales de Riot.

Tokens (usar estos valores exactos)
- Fondos: forge-black #010a13, forge-darker #05101c, forge-dark #0a1428
- Superficies: surface-base #0d1b2a, surface-card #0f1923, surface-raised #1b2838, surface-overlay #1e2d3d
- Dorado: arc-gold #c89b3c, arc-gold-dark #785a28, arc-gold-text #d4b15c, arc-gold-bright #f0e6d2
- Información: arc-cyan #0bc6e3
- Texto: text-primary #f0e6d2, text-secondary #a09b8c, text-on-gold #010a13
- Lado azul (Quex): blue-side #4a97ff, blue-side-deep #143a80, blue-side-soft rgba(74, 151, 255, 0.14)
- Lado rojo (Mingo): red-side #ff5a68, red-side-deep #7a1622, red-side-soft rgba(255, 90, 104, 0.14)
- Texto sobre relleno de lado: text-on-side #010a13
- Estados: state-success #00d084, state-error #ff4655, state-warning #ff9a3c
- Bordes: border-subtle rgba(200, 155, 60, 0.12), border-metal rgba(200, 155, 60, 0.20), border-metal-strong rgba(200, 155, 60, 0.40)

Reglas que no se negocian
- Lado azul siempre a la izquierda y lado rojo siempre a la derecha, en todas las pantallas.
- El color nunca es la única señal: cada lado lleva el nombre del jugador y la etiqueta "Lado azul" o "Lado rojo", y cada estado de campeón lleva texto ("Usado en P1", "Elegido").
- Contraste mínimo 4.5:1 para texto. Sobre blue-side o red-side, texto oscuro (text-on-side). Sobre los tonos deep, solo text-primary.
- El rojo del lado rojo no significa error ni derrota. Al perdedor se lo atenúa, no se lo pinta de rojo.
- Español rioplatense, corto y con jerga gamer: pick, pool, First Blood, CS, Fearless, Bo3. Nada de textos que expliquen cómo usar la pantalla.
- Nada de degradados violetas, emojis decorativos, tarjetas con borde de color a la izquierda ni UI corporativa genérica.
- Respetar prefers-reduced-motion.

Entrega
Primero las 6 pantallas en el canvas, con los mismos datos en todas. Después, una lista corta de los componentes que usaste (por ejemplo: encabezado VS, marcador de serie, tarjeta de jugador, pool de campeones, casilla de campeón, badge de condición de victoria, tracker de partida y resultado de partida).
```

## Criterios de aceptación

La respuesta de Claude Design sirve si:

- Las 6 pantallas usan los mismos datos de ejemplo y el marcador es coherente
  entre ellas (0-0, 1-1, 2-1).
- El lado azul está a la izquierda y el rojo a la derecha en todas.
- Se ven las dos pools completas, con estados distinguibles también sin color
  (disponible, elegido, usado y bloqueado).
- Se entiende por qué ganó cada partida: condición y minuto.
- El dorado queda para jerarquía, acción principal y ganador; el cyan, solo
  para información.
- No usa splash arts ni logos oficiales de Riot.

## Cómo adaptarlo a otro duelo

- Cambiar nombres, pools, horario y resultados en "Datos de ejemplo".
- Mantener `blue-side` a la izquierda y `red-side` a la derecha: el lado define
  el color, no el jugador.
