# Rift Duel

Design system para series 1v1 de League of Legends entre amigos (ejemplo: Quex
vs Mingo, al mejor de 3). Es el Hextech de la Pattern Library v2 más un color por
lado: azul a la izquierda y rojo a la derecha.

## Qué hay en esta carpeta

| Ruta | Qué es |
|------|--------|
| `design-system/` | Copia versionada de los archivos del artifact Rift Duel: `tokens.json`, `README.md` (reglas de uso), `design-system.json` (índice) y `components/` (`bundle.css`, previews y README de cada componente, y la portada). |
| `build_gallery.py` | Genera `gallery.html` a partir de `design-system/`. |
| `gallery.html` | Galería local generada y autocontenida: portada, colores, tipografía y los 17 componentes. No editar a mano. |
| `fixture.json` | Datos del fixture del torneo: evento, jugadores, pools y resultados. Es lo que se edita. |
| `build_fixture.py` | Valida `fixture.json` y genera `fixture.html`. |
| `fixture.html` | Fixture generado y autocontenido. No editar a mano. |

El prompt para Claude Design está en `../rift-duel-prompt.md`.

## Cómo verlo

- **Página oficial:** https://claude.ai/artifact/2pYJqbC4tHCaMhQ5Umiu2N. Es privada: se abre con la cuenta de claude.ai dueña del artifact.
- **Local:** abrir `gallery.html` con doble clic. Es autocontenido: lleva el CSS adentro, no usa iframes ni JavaScript, y se ve igual aunque lo copies a otra carpeta o lo abras desde un visor de archivos. Solo necesita internet para las fuentes de Google Fonts.
- **Regenerar la galería** después de cambiar algo en `design-system/`:

```powershell
python claude-design-handoff/rift-duel/build_gallery.py
```

## Fixture del torneo

`fixture.html` muestra cada enfrentamiento con el design system. Arriba va el VersusHero, con el avatar de cada jugador y su pool de 3 campeones debajo del nombre. Después vienen el SeriesScore y un GameResult por partida (P1 a P3). Es autocontenido como la galería: se abre con doble clic y los estados se ven sin JavaScript.

- **Datos:** todo sale de `fixture.json`. El HTML no se toca a mano.
- **Regenerar** después de cambiar los datos:

```powershell
python claude-design-handoff/rift-duel/build_fixture.py
```

- **Validación:** antes de generar, el script revisa:
  - que cada pool tenga 3 campeones distintos;
  - la regla Fearless;
  - que nadie siga jugando después de llegar a 2;
  - el formato `mm:ss` del tiempo y la condición de victoria;
  - que cada campeón exista en `data/ddragon-splash-catalog.json`. Si hay un error de tipeo, sugiere el nombre correcto.

  Si algo falla, lista todos los errores y deja el `fixture.html` anterior como estaba.
- **Íconos:** los campeones reales muestran su ícono de Data Dragon, en la versión del catálogo. Si no hay internet, se ve la inicial. Los placeholders `Campeón 01` muestran el número.

### Cómo pasar los datos por el chat

El primer jugador va del lado azul (izquierda) y el segundo del rojo (derecha):

```text
03 | Juan vs Pedro
Juan: Ahri, Zed, Yasuo
Pedro: Lux, Syndra, Viktor
P1: gana Juan · Zed vs Lux · First Blood · 05:10
En juego: P2
```

Condiciones de victoria: First Blood, 100 CS o Primera torre.

## Si cambiás el design system

La versión que usa Claude es la del artifact. Si editás `design-system/`, hay que
volver a publicar esos archivos en el artifact; si alguien lo edita desde la
página, hay que traer los cambios acá.
