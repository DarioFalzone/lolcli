# Rift Duel

Design system para series 1v1 de League of Legends entre amigos (ejemplo: Cuex
vs Mingo, al mejor de 3). Es el Hextech de la Pattern Library v2 más un color por
lado: azul a la izquierda y rojo a la derecha.

## Qué hay en esta carpeta

| Ruta | Qué es |
|------|--------|
| `design-system/` | Copia versionada de los archivos del artifact Rift Duel: `tokens.json`, `README.md` (reglas de uso), `design-system.json` (índice) y `components/` (`bundle.css`, previews y README de cada componente, y la portada). |
| `build_gallery.py` | Genera `gallery.html` a partir de `design-system/`. |
| `gallery.html` | Galería local generada y autocontenida: portada, colores, tipografía y los 17 componentes. No editar a mano. |
| `fixture.json` | Datos del fixture del torneo: evento, jugadores, pools y resultados. Es lo que se edita. |
| `build_fixture.py` | Valida `fixture.json` y genera `fixture.html`; con `--pages` arma la rama `gh-pages`. |
| `fixture.html` | Fixture generado. No editar a mano. |
| `serve_fixture.py` | Servidor local: `/` abre el fixture y `/assets/` sirve los splash del repo. |

El prompt para Claude Design está en `../rift-duel-prompt.md`.

## Cómo verlo

- **Página oficial:** https://claude.ai/artifact/2pYJqbC4tHCaMhQ5Umiu2N. Es privada: se abre con la cuenta de claude.ai dueña del artifact.
- **Local:** abrir `gallery.html` con doble clic. Es autocontenido: lleva el CSS adentro, no usa iframes ni JavaScript, y se ve igual aunque lo copies a otra carpeta o lo abras desde un visor de archivos. Solo necesita internet para las fuentes de Google Fonts.
- **Regenerar la galería** después de cambiar algo en `design-system/`:

```powershell
python claude-design-handoff/rift-duel/build_gallery.py
```

## Fixture del torneo

`fixture.html` muestra cada enfrentamiento con el design system. Arriba va el VersusHero, con el avatar de cada jugador y su pool de 3 campeones debajo del nombre. Después vienen el SeriesScore y un GameResult por partida (P1 a P3). El CSS va adentro y no usa JavaScript.

- **Nombres:** el jugador del lado azul va en dorado metálico y el del lado rojo en plateado, estilo LoL, con brillo. En el marcador y en los resultados, el nombre va en dorado o plateado liso. Al perdedor de la serie se lo atenúa.
- **Pool:** tarjetas grandes (16:10) con el splash Classic de cada campeón y el nombre encima. Las usadas siguen viéndose, apenas atenuadas, con la marca "Usado en Pn". Los lugares sin campeón muestran "Por elegir".
- **Plantilla:** `fixture.json` arranca limpio: 01 Cuex vs Mingo y 02 a 10 con "Jugador NN", pools vacías y partidas sin cargar ("Pendiente"). Se completa a medida que llegan los datos.

- **Levantarlo local:** `scripts\bat\rift_duel.bat` regenera `fixture.html` y lo sirve en **http://localhost:8007/** (puerto configurable con `LOLCLI_RIFT_DUEL_PORT`). El navegador se abre recién cuando el servidor está escuchando. La ventana negra tiene que quedar abierta: si la cerrás, se cae el servidor. Se corta con Ctrl+C. Si cambian los datos con el servidor andando, alcanza con regenerar y refrescar la página. Sin el `.bat`:

```powershell
python claude-design-handoff/rift-duel/serve_fixture.py --build --open
```

  El `.bat` busca Python en este orden: `.venv` de la carpeta, `.venv` del clon principal (si se corre desde un git worktree), el lanzador `py` y `python`. Si no levanta, la ventana dice por qué: no encontró Python o el puerto está ocupado por otro programa (en ese caso, `set LOLCLI_RIFT_DUEL_PORT=8017`).

  Abrir `fixture.html` con doble clic también funciona, porque las imágenes se buscan en `../../assets/`.
- **GitHub Pages:** **https://dariofalzone.github.io/lolcli/**. Sale de la rama `gh-pages`, que tiene `index.html`, los splash que usa el fixture (en `assets/splash_arts/`, solo si hay campeones cargados) y `.nojekyll`. Es pública. Se activa una sola vez: Settings → Pages → Build and deployment → Source "Deploy from a branch" → Branch `gh-pages` / `(root)` → Save. Para publicar una versión nueva:

```powershell
git fetch origin gh-pages
git worktree add ..\lolcli-pages gh-pages   # solo la primera vez; después: git -C ..\lolcli-pages pull
python claude-design-handoff/rift-duel/build_fixture.py --pages ..\lolcli-pages
git -C ..\lolcli-pages add -A
git -C ..\lolcli-pages commit -m "chore(pages): update fixture"
git -C ..\lolcli-pages push
```

- **Datos:** todo sale de `fixture.json`. El HTML no se toca a mano.
- **Regenerar** después de cambiar los datos:

```powershell
python claude-design-handoff/rift-duel/build_fixture.py
```

- **Validación:** antes de generar, el script revisa:
  - que cada pool tenga hasta 3 campeones distintos (lo que falta queda "Por elegir");
  - la regla Fearless;
  - que nadie siga jugando después de llegar a 2;
  - el formato `mm:ss` del tiempo y la condición de victoria;
  - que cada campeón exista en `data/ddragon-splash-catalog.json`. Si hay un error de tipeo, sugiere el nombre correcto.

  Si algo falla, lista todos los errores y deja el `fixture.html` anterior como estaba.
- **Imágenes:** cada campeón muestra su splash Classic de `assets/splash_arts/<id>/`; el archivo sale de `data/ddragon-splash-catalog.json` (`skinNum` 0). No hace falta internet. Si falta un splash, el script avisa y se ve la inicial.
- **Campeones actuales:** el catálogo local es de la versión 16.9.1 (172 campeones). Para bajar los que salieron después, corré el script del repo en una PC o sesión con acceso a `ddragon.leagueoflegends.com`. Baja solo lo que falta y actualiza el catálogo:

```powershell
$env:PYTHONPATH = "src"; python scripts/update_ddragon_assets.py --skip-items
```

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
