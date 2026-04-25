# Registro tecnico del proyecto

## Proposito
Este documento funciona como bitacora tecnica obligatoria del proyecto. Su objetivo es dejar trazabilidad de:

- que archivos existen y que rol cumplen
- que cambios se hicieron
- por que se hicieron
- que impacto tecnico o funcional dejaron
- que deuda o seguimiento queda abierto

## Regla de uso del registro
- Este archivo debe leerse antes de modificar codigo o contenido del proyecto.
- Despues de cada modificacion de archivos, se debe agregar o actualizar una entrada en este registro.
- Las entradas nuevas van arriba de las anteriores.
- No se borran entradas historicas; se corrigen o se agregan aclaraciones.
- Si un cambio crea, renombra, elimina o deja huerfanos archivos, eso debe quedar explicitado.

## Snapshot actual del repo
Fecha de snapshot: 2026-03-29

### Archivos activos
- `index.html`: pagina autocontenida de tier list de junglas elite de League of Legends. Incluye HTML, CSS inline, JS inline, tablas, grafico, timeline y metodologia.
- `img/fotos_pro_players/`: galeria local de retratos `WEBP` consumida por `index.html`.
- `docs/guia-operativa-junglas.md`: documento operativo consolidado para arquitectura, fuentes y assets.
- `docs/deeps_searchs/Tier list analitico enciclopedico de junglas profesionales`: deep research complementario con stats detalladas por torneo, meta de Worlds, head-to-head y analisis de eficiencia.
- `docs/deeps_searchs/search_profesionales_tierlist.md`: fuente de investigacion cruda para la pagina de tier list.
- `.agents/rules/nuevarule.md`: regla operativa para agentes de codificacion.
- `docs/code.gap.md`: checklist de datos inferidos pendientes de auditoría (score breakdowns).

### Hallazgos tecnicos relevantes
- `index.html` es la unica experiencia activa del repo.
- La linea de onboarding separada ya no forma parte de la arquitectura final.
- `index.html` usa Google Fonts remotas y una implementacion visual autocontenida.
- El markdown de investigacion muestra problemas de codificacion al leerse desde PowerShell; conviene normalizar UTF-8 cuando se vuelva a editar.

## Historial

### 2026-03-29 - Integración de Apache ECharts + Chart.js con temática LoL
- Motivo: reemplazar el gráfico de barras custom limitado por una capa de visualización analítica profesional que explote los datos del tier list.
- Archivos modificados: `index.html`, `docs/registro-tecnico.md`, `docs/paginas de graficos.md`
- Archivos creados: `docs/code.gap.md`
- Cambio tecnico:
  - Se cargan ECharts 5 y Chart.js 4 vía CDN oficial (`jsdelivr.net`), sin agregar archivos de vendor al repo.
  - Se eliminó el bar chart custom inline (divs + JS) de la sección 04.
  - Se agregaron 5 charts nuevos:
    1. **Score Ranking** (ECharts): bar horizontal apilado con breakdown por categoría (Internacional/Doméstico/Premios/Stats/Reputación), tooltips ricos con desglose.
    2. **Radar de Perfil Competitivo** (Chart.js): radar con selector interactivo de hasta 4 jugadores para superponer perfiles de scoring normalizado.
    3. **Distribución por Tier** (Chart.js): doughnut con colores de tier.
    4. **LCS vs Sin LCS** (Chart.js): bar comparativo horizontal de score promedio.
    5. **Mapa de Títulos Internacionales** (ECharts): scatter temporal con puntos dimensionados por importancia del torneo.
  - Se agregó CSS con estética LoL: gradientes hextech, glassmorphism oscuro con glow de partículas, tipografía Outfit para charts.
  - Se agregaron 3 nuevas secciones HTML (04, 04b, 04c) y se actualizaron los links de navegación.
  - Se creó `docs/code.gap.md` documentando datos de score breakdown inferidos pendientes de auditoría.
- Impacto:
  - La página pasa de un único bar chart plano a 5 visualizaciones interactivas con tooltips, leyendas, filtros y animaciones.
  - Cada chart tiene una justificación explícita contra bloat (ver `docs/paginas de graficos.md`).
  - La experiencia se siente mucho más premium y analíticamente profunda.
- Pendientes:
  - Auditar los breakdown de scores usando `docs/code.gap.md` como checklist.

### 2026-03-29 - Se restaura la guia de paginas de graficos y el prompt de Antigravity para la capa visual
- Motivo: se detecto que `docs/paginas de graficos.md` se habia eliminado sin fusion real de su contenido y hacia falta dejar un handoff formal para la nueva etapa de integracion con ECharts y Chart.js.
- Archivos modificados: `docs/registro-tecnico.md`, `docs/guia-operativa-junglas.md`
- Archivos creados: `docs/paginas de graficos.md`, `docs/prompt-antigravity.md`
- Cambio tecnico:
  - Se restauro un documento dedicado a paginas de graficos con la referencia oficial de Apache ECharts y Chart.js, sus roles sugeridos y criterios de integracion dentro de `index.html`.
  - Se creo un prompt operativo para Antigravity enfocado en reemplazar la capa de charts actual por una integracion de mayor valor analitico y visual, manteniendo la arquitectura compacta del repo.
  - Se actualizo la guia operativa para volver a incluir estos documentos como parte de la documentacion vigente.
- Impacto:
  - El criterio de seleccion de librerias de charts deja de depender de memoria conversacional y vuelve a estar persistido en `docs/`.
  - Ya existe un prompt listo para delegar la siguiente fase de mejora visual y analitica de la pagina.
- Pendientes:
  - Ejecutar la implementacion real de charts en `index.html`.
  - Validar en esa etapa que cada chart nuevo tenga un rol claro y que no quede bloat visual o tecnico.

### 2026-03-29 - Regla always-on de compactacion pre-code y post-code
- Motivo: volver obligatoria la disciplina que se uso en la compactacion final del repo para que futuros cambios no reintroduzcan lineas paralelas, tooling residual o documentacion duplicada.
- Archivos modificados: `.agents/rules/nuevarule.md`, `docs/registro-tecnico.md`
- Cambio tecnico:
  - La regla always-on ahora obliga a leer no solo `docs/registro-tecnico.md` sino tambien `docs/guia-operativa-junglas.md` antes de editar.
  - Se agrego un chequeo pre-code de compatibilidad con la arquitectura final compacta.
  - Se agrego un checklist post-code de limpieza obligatoria para borrar temporales, caches, tooling one-off, funciones sin uso, documentos redundantes y formatos obsoletos.
  - Se fijo como criterio explicito que los retratos locales finales deben permanecer en `WEBP` salvo nueva decision documentada.
- Impacto:
  - La compactacion del proyecto deja de ser una accion puntual y pasa a ser una regla operativa permanente.
  - Cualquier agente que vuelva a tocar el repo tiene que revisar encaje arquitectonico antes de codear y limpiar residuos antes de cerrar.
- Pendientes: ninguno.

### 2026-03-29 - Compactacion del repo y unificacion de la linea activa
- Motivo: reducir el proyecto a una sola linea funcional, eliminar tooling y codigo residual, y fusionar documentacion superpuesta.
- Archivos modificados: `index.html`, `docs/registro-tecnico.md`, `docs/guia-operativa-junglas.md`
- Archivos creados: `docs/guia-operativa-junglas.md`
- Archivos eliminados: `app.js`, `content.js`, `move_images.sh`, `replace_avatars.js`, `package.json`, `package-lock.json`, `scripts/`, `node_modules/`, `.npm-cache/`, `tmp/`, `docs/retratos-huggingface.md`, `docs/paginas de graficos.md`, `docs/deeps_searchs/player_data_extraction.md`, `docs/deeps_searchs/Páginas para fotos, equipos, rosters e información de LoL Esports`, `img/fotos_pro_players/canyon_ia.png`, `img/fotos_pro_players/oner_ia.png`, `img/fotos_pro_players/peanut_ia.png`
- Cambio tecnico:
  - Se definio `index.html` como unica app activa del repo.
  - Se consolido la documentacion operativa de arquitectura, fuentes, protocolo `markdown.new` y assets en un solo documento.
  - Se elimino la linea de onboarding separada y todo el tooling temporal de generacion ya innecesario despues de producir los assets finales.
  - Se eliminaron los PNG residuales para dejar solo `WEBP` en la galeria final.
- Impacto:
  - El repo queda reducido a la pagina activa, sus assets locales y la documentacion minima necesaria.
  - La documentacion deja de estar partida en varias notas parcialmente redundantes.
- Pendientes: ninguno en esta limpieza.

### 2026-03-29 - Generacion completa de retratos locales con Hugging Face gratis y cierre de migracion en HTML
- Motivo: completar la galeria local sin depender de billing pago de OpenAI o de providers prepago en Hugging Face.
- Archivos modificados: `index.html`, `docs/retratos-huggingface.md`, `docs/registro-tecnico.md`
- Archivos generados: `img/fotos_pro_players/kanavi_ia.webp`, `img/fotos_pro_players/jankos_ia.webp`, `img/fotos_pro_players/xun_ia.webp`, `img/fotos_pro_players/tian_ia.webp`, `img/fotos_pro_players/blaber_ia.webp`, `img/fotos_pro_players/wei_ia.webp`, `img/fotos_pro_players/xmithie_ia.webp`, `img/fotos_pro_players/jiejie_ia.webp`, `img/fotos_pro_players/inspired_ia.webp`, `img/fotos_pro_players/svenskeren_ia.webp`, `img/fotos_pro_players/pyosik_ia.webp`, `img/fotos_pro_players/broxah_ia.webp`, `img/fotos_pro_players/spica_ia.webp`, `img/fotos_pro_players/closer_ia.webp`, `img/fotos_pro_players/tarzan_ia.webp`
- Cambio tecnico:
  - La primera prueba de `image-to-image` con `Qwen/Qwen-Image-Edit` usando token de Hugging Face fue ruteada a `fal-ai` y fallo por exigir creditos prepago.
  - Se ejecuto una ruta gratis real con `hf-inference` + `black-forest-labs/FLUX.1-schnell` en modo `text-to-image`, generando los 15 retratos faltantes en `WEBP`.
  - Se actualizaron todas las referencias restantes de `index.html` para consumir assets locales en `img/fotos_pro_players/`.
- Impacto:
  - La pagina activa quedo con `18` referencias locales y `0` referencias remotas para avatares de jugadores.
  - La migracion a galeria local quedo funcionalmente cerrada.
- Riesgos y notas:
  - La ruta gratis produce retratos estilizados coherentes, pero no garantiza parecido exacto con el jugador real.
  - Algunos retratos siguen inventando insignias o marcas en la camiseta aunque el prompt lo desincentive.

### 2026-03-29 - Pipeline local con Hugging Face para retratos IA por lote
- Motivo: reemplazar la ruta bloqueada por billing de OpenAI con un flujo reproducible basado en Hugging Face para generar retratos IA locales de los junglas faltantes.
- Archivos modificados: `package.json`, `package-lock.json`, `docs/registro-tecnico.md`
- Archivos creados: `scripts/generate-hf-jungler-portraits.mjs`, `docs/retratos-huggingface.md`
- Cambio tecnico:
  - Se instalaron las dependencias `@huggingface/inference` y `sharp`.
  - Se agrego un script Node por lote que descarga las fotos de referencia actuales, llama a `imageToImage` via Hugging Face, convierte la salida a `WEBP` y la guarda en `img/fotos_pro_players/`.
  - El script soporta control por entorno para `provider`, `model`, intervalo, limite, slugs concretos, variantes, overwrite y sincronizacion opcional de `index.html`.
  - Se documento el uso operativo con `HF_TOKEN` y el comando compatible con este equipo (`cmd /c npm run ...`).
- Impacto:
  - El proyecto ya tiene un pipeline local mantenible para continuar la migracion de retratos sin depender del CLI previo de OpenAI.
  - La conversion final a `WEBP` queda integrada en el mismo flujo.
- Pendientes:
  - Todavia no se ejecuto un lote real con Hugging Face en este repo porque falta configurar `HF_TOKEN`.
  - Queda validar en practica que el modelo elegido mantenga bien identidad y, si hace falta, ajustar `HF_MODEL` o `HF_PROVIDER`.

### 2026-03-29 - Activacion de WEBP local para el lote inicial de retratos IA
- Motivo: alinear la pagina activa con la convencion final de assets locales `WEBP` sin depender de URLs remotas para el lote ya disponible.
- Archivos modificados: `index.html`, `docs/registro-tecnico.md`
- Cambio tecnico:
  - Se detecto que ya existian en el repo los archivos `img/fotos_pro_players/canyon_ia.webp`, `img/fotos_pro_players/oner_ia.webp` y `img/fotos_pro_players/peanut_ia.webp`.
  - Se actualizaron las referencias de `index.html` para que `Canyon`, `Oner` y `Peanut` consuman esos `WEBP` locales en lugar de sus `PNG`.
  - No se tocaron medidas de UI porque el baseline correcto ya estaba activo: `72px` para cards grandes y `56px` para cards compactas.
- Impacto:
  - El lote local realmente integrado en la experiencia activa ya usa el formato final previsto por la migracion.
  - Se reduce el peso de carga de los tres retratos migrados respecto a sus `PNG` equivalentes y queda mas consistente la convencion de nombres.
- Pendientes:
  - Persisten 15 jugadores con referencia remota; la estrategia continua siendo fallback mixto hasta generar o incorporar sus retratos locales aprobados.
  - Los `PNG` originales de este lote se mantienen temporalmente en el repo como respaldo no consumido por `index.html`; evaluar limpieza cuando el batch local este mas consolidado.

### 2026-03-29 - Avance real de la migracion a retratos locales y protocolo markdown.new
- Motivo: ejecutar el lote actualmente viable de la migracion a galeria local de retratos y dejar documentado el protocolo de recoleccion IA-friendly.
- Archivos modificados: `index.html`, `docs/registro-tecnico.md`, `docs/deeps_searchs/Páginas para fotos, equipos, rosters e información de LoL Esports`
- Cambio tecnico:
  - Se confirmo el baseline visual ya activo en `index.html`: avatares grandes en `72px` y compactos en `56px`; no hizo falta ampliar mas.
  - Se reemplazaron las referencias remotas de `Oner` y `Peanut` por assets locales existentes en `img/fotos_pro_players/`, alineando el lote local actual de tres jugadores: `Canyon`, `Oner` y `Peanut`.
  - Se expandio la guia de `markdown.new` y se formalizo como protocolo operativo con sintaxis, casos de uso, ejemplos y criterio de preferencia entre fuentes oficiales y wiki.
  - Se verifico el estado real de assets locales existentes: `canyon_ia.png`, `oner_ia.png`, `peanut_ia.png`.
- Impacto:
  - El proyecto reduce dependencia remota en el bloque superior del tier list y deja un camino claro para seguir migrando jugador por jugador.
  - La metodologia de extraccion IA-friendly queda mas precisa y reutilizable para futuras investigaciones.
- Pendientes:
  - La conversion final de estos tres assets a `WEBP` no pudo ejecutarse dentro del sandbox actual por limitaciones de tooling/permisos; por ahora el lote local queda en `PNG`.
  - Restan 15 jugadores con referencias remotas; la estrategia sigue siendo fallback mixto hasta completar nuevas generaciones locales.

### 2026-03-29 - Aumento de avatares UI y Documentación de protocolo markdown.new
- Motivo: Darle más tamaño y presencia a las fotos de los junglas y estandarizar un método limpio de consulta IA para portales como Liquipedia.
- Archivos modificados: `index.html`, `docs/registro-tecnico.md`, `docs/deeps_searchs/Páginas para fotos...`
- Cambio tecnico:
  - CSS (`index.html`): Modificación de `.player-avatar` de 56px a 72px e incremento proporcional del `border-radius` a 18px. Modificación de `.player-avatar.small` de 42px a 56px (radius 14px).
  - Documentación: Se testeó exitosamente y se documentó el uso del prefijo `https://markdown.new/` directamente contra la URL base (`liquipedia.net/leagueoflegends/[player]`) para convertir HTML ruidoso a Markdown plano dentro del visor de los agentes.
- Impacto: Las caras de los jugadores tienen más impacto visual en el Tier List. El proyecto tiene un método formal para investigar players sin romperse con DOMs gigantes.
- Pendientes: 
  - La red neuronal de dibujo está con sus servidores de cuota colapsados ("No capacity"). La generación local de los 18 retratos IA en `/img/fotos_pro_players/` tuvo que pausarse temporalmente y deberá retomarse en breve. Las imágenes continúan siendo traídas de Wiki mientras tanto.

### 2026-03-29 - Extracción e integración de fotos oficiales de jugadores
- Motivo: Completar la enciclopedia visual reemplazando los avatares de texto (iniciales) con fotografías comprobables de los jugadores (S a C tier).
- Archivos modificados: `index.html`, `docs/registro-tecnico.md`, creaciones en `docs/deeps_searchs/`
- Cambio tecnico:
  - Se crearon documentos de investigación indicando de dónde extraer fotos oficiales (Leaguepedia, Liquipedia, LoL Esports Flickr).
  - Se actualizó el HTML de las cards de todos los players (18 en total).
  - CSS: Se agregó la clase `.avatar-img` con `width:100%; height:100%; object-fit:cover; border-radius:inherit` para que las fotos llenen los anillos S, A, B y C.
  - HTML: Se reemplazaron `<span class="avatar-text">XX</span>` por `<img src="..." class="avatar-img" onerror="..." />`. Se usa el evento `onerror` para mantener resiliencia si algún enlace de wiki falla, volviendo a mostrar iniciales.
- Impacto: 11 jugadores lucen ahora imágenes profesionales directas (Canyon, Oner, Jankos, etc.), mejorando la estética esports general de la página sin romper la UI. Los 7 restantes muestran con elegancia sus inicales como fallback en caso de bloqueos.
- Pendientes: 
  - Hostear en el futuro de manera local imágenes de los restantes (Pyosik, Svenskeren, etc.) en `/img/` para depender menos de enlaces de terceros.

### 2026-03-29 - Integracion del deep research enciclopedico en index.html
- Motivo: incorporar datos verificados del deep research (stats por torneo, meta de Worlds, head-to-head, citas analiticas, eficiencia) para hacer la pagina mucho mas rica y extensa.
- Archivos modificados: `index.html`, `docs/registro-tecnico.md`
- Archivos leidos como fuente: `docs/deeps_searchs/Tier list analitico enciclopedico de junglas profesionales`, `docs/search_profesionales_tierlist.md`
- Cambio tecnico:
  - CSS: se agregan ~40 lineas de estilos nuevos para secciones meta-grid, h2h-grid, eff-grid, player-quote, stats-ext, stat-chip.
  - HTML - Player cards S-tier (Canyon, Oner): se agregan stat-chips con KDA, WR%, CSPM, DPM, VSPM, Gold%, FB% verificados de gol.gg + citas de Inven Global.
  - HTML - Player cards A-tier (Peanut, Kanavi): stats de Worlds 2017/2022/2025 + cita de Kanavi.
  - HTML - Player cards B-tier (Jankos, Xun, Tian, Jiejie, Inspired, Svenskeren, Pyosik + otros): notas enriquecidas con datos de torneos, pools de campeones y contexto analitico.
  - HTML - Player cards C-tier (Broxah, Spica, Closer, Tarzan): stats de Worlds con pools alineados a meta del año.
  - HTML - Nueva seccion 07 "Meta de Jungla por Worlds": 9 cards (2017-2025) con tipo de meta, picks dominantes y cantidad de juegos.
  - HTML - Nueva seccion 08 "Head-to-Head Internacional": 4 cruces documentados (Canyon vs Oner, Canyon vs Jiejie, Kanavi vs Oner, Jankos vs Tian) con resultado de serie y contexto.
  - HTML - Nueva seccion 09 "Eficiencia: Oportunidad vs Resultado": ranking de 4 jugadores con mejor ratio de conversion competitiva (Oner, Pyosik, Jiejie, Xun).
  - Nav: se agregan links a las 3 secciones nuevas (Meta x Worlds, H2H, Eficiencia).
  - JS: se actualizan selectores del IntersectionObserver para incluir .meta-card, .h2h-card, .eff-card al scroll reveal.
- Impacto: la pagina pasa de ~1207 lineas a ~1440+ lineas. El contenido analitico se enriquece sustancialmente con datos verificados de gol.gg y Leaguepedia, citas editoriales, y analisis de eficiencia. Todas las secciones nuevas son responsive y tienen animaciones de scroll.
- Pendientes:
  - El deep research marca datos como "N/D" o "parciales" para algunos jugadores (Blaber internacionales, Wei Tournament Results, Tian dataset completo). Si se consigue data adicional, actualizar las cards correspondientes.
  - Considerar agregar una seccion de champion pool visual (top 5 por jugador con winrate) si se obtiene la data completa.

### 2026-03-29 - Se agrega prompt operativo para Antigravity
- Motivo: transferir a Antigravity el contexto de trabajo, las reglas de documentacion y el estado actual del repo en un formato reutilizable.
- Archivos modificados: `docs/prompt-antigravity.md`, `docs/registro-tecnico.md`
- Cambio tecnico: se crea un prompt especifico para Antigravity alineado con la regla `.agents/rules/nuevarule.md` y con la snapshot actual del proyecto.
- Impacto: cualquier handoff hacia Antigravity puede arrancar con contexto de repo y con la obligacion explicita de mantener la documentacion actualizada.
- Pendientes: actualizar este prompt si cambia la arquitectura del repo o la modalidad de trabajo.

### 2026-03-29 - Se crea el registro tecnico y la regla obligatoria de documentacion
- Motivo: establecer trazabilidad tecnica y una disciplina de documentacion permanente para cualquier agente que modifique el proyecto.
- Archivos modificados: `docs/registro-tecnico.md`, `.agents/rules/nuevarule.md`
- Cambio tecnico: se agrega esta bitacora y se formaliza una regla always-on que obliga a revisar `docs/` antes de tocar archivos y a mantener la documentacion al dia despues de cada cambio.
- Impacto: a partir de este punto cualquier cambio deberia dejar registro documental en el mismo ciclo de trabajo.
- Pendientes: aplicar la regla de forma consistente en todas las tareas futuras.

### 2026-03-29 - Baseline reconstruida desde el estado actual del repo
- Motivo: documentar lo que ya existe para no arrancar la bitacora desde cero.
- Archivos relevados: `index.html`, `app.js`, `content.js`, `docs/search_profesionales_tierlist.md`
- Cambio tecnico registrado: el proyecto hoy contiene dos lineas funcionales visibles.
  - Una pagina principal autocontenida en `index.html` centrada en una tier list de junglas de LoL.
  - Una implementacion separada de portal de onboarding sostenida por `app.js` + `content.js`.
- Impacto: el registro deja explicitado que el repo no esta unificado en una sola experiencia y que existe codigo de onboarding no conectado a la pagina principal actual.
- Pendientes: decidir si ambas lineas conviviran, si una reemplaza a la otra, o si hace falta una limpieza de archivos no usados.

## Plantilla para futuras entradas
Usar este formato minimo:

### YYYY-MM-DD - Titulo breve del cambio
- Motivo:
- Archivos modificados:
- Cambio tecnico:
- Impacto:
- Pendientes:
