# Guía operativa del proyecto

## Estado activo
- La aplicación activa es [index.html](/e:/Nueva%20carpeta/index.html).
- La galería visual usa solo assets locales en `img/fotos_pro_players/`.
- El formato vigente para retratos es `WEBP`.

## Arquitectura final
- `index.html`: documento autocontenido con HTML, CSS y JS inline.
- `img/fotos_pro_players/`: retratos locales de los 18 jugadores.
- `docs/registro-tecnico.md`: bitácora obligatoria.
- `docs/paginas de graficos.md`: referencia de librerias y paginas oficiales para la capa de charts.
- `docs/deeps_searchs/search_profesionales_tierlist.md`: fuente cruda de investigación.
- `docs/deeps_searchs/Tier list analítico enciclopédico de junglas profesionales`: investigación analítica expandida.
- `docs/prompt-antigravity.md`: contexto operativo para handoff.

## Fuentes de contenido recomendadas
- Oficiales:
  - `lolesports.com`
  - Riot Press / Riot Assets
  - LoL Esports Flickr
  - sitios y redes oficiales de los equipos
- De referencia competitiva:
  - Leaguepedia
  - Liquipedia
  - `gol.gg`

## Protocolo `markdown.new`
- Usarlo cuando una wiki tenga demasiado HTML o ruido estructural.
- Sintaxis:
  - `https://markdown.new/<url-original>`
- Ejemplos:
  - `https://markdown.new/https://liquipedia.net/leagueoflegends/Oner`
  - `https://markdown.new/https://lol.fandom.com/wiki/Canyon`
- Prioridad de uso:
  - oficiales primero para roster actual, anuncios, assets y branding
  - wiki + `markdown.new` para historial, carrera, torneos y contexto enciclopédico

## Assets visuales
- Slugs activos:
  - `canyon`, `oner`, `peanut`, `kanavi`, `jankos`, `xun`, `tian`, `blaber`, `wei`, `xmithie`, `jiejie`, `inspired`, `svenskeren`, `pyosik`, `broxah`, `spica`, `closer`, `tarzan`
- Convención:
  - `img/fotos_pro_players/<slug>_ia.webp`
- Estado actual:
  - `index.html` referencia 18 imágenes locales
  - no quedan referencias remotas para avatares

## Nota sobre generación IA
- Los retratos finales quedaron generados y guardados localmente.
- La ruta gratis que funcionó fue Hugging Face `hf-inference` con generación `text-to-image`.
- El resultado es visualmente consistente para la página, pero no garantiza parecido exacto al jugador real.
- El tooling temporal de generación no forma parte de la arquitectura final del repo.

## Mantenimiento
- Antes de cualquier cambio, leer `docs/registro-tecnico.md`.
- Después de cualquier cambio, actualizar `docs/registro-tecnico.md`.
- Si se vuelve a abrir una línea de generación de imágenes, hacerlo como tooling temporal y no como dependencia permanente del proyecto, salvo que vuelva a ser un requisito activo.
