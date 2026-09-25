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

El prompt para Claude Design está en `../rift-duel-prompt.md`.

## Cómo verlo

- **Página oficial:** https://claude.ai/artifact/2pYJqbC4tHCaMhQ5Umiu2N. Es privada: se abre con la cuenta de claude.ai dueña del artifact.
- **Local:** abrir `gallery.html` con doble clic. Es autocontenido: lleva el CSS adentro, no usa iframes ni JavaScript, y se ve igual aunque lo copies a otra carpeta o lo abras desde un visor de archivos. Solo necesita internet para las fuentes de Google Fonts.
- **Regenerar la galería** después de cambiar algo en `design-system/`:

```powershell
python claude-design-handoff/rift-duel/build_gallery.py
```

## Si cambiás el design system

La versión que usa Claude es la del artifact. Si editás `design-system/`, hay que
volver a publicar esos archivos en el artifact; si alguien lo edita desde la
página, hay que traer los cambios acá.
