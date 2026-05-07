# Splash Gallery

Proyecto activo para mantener la galeria HTML de splash arts.

## Rutas runtime

- Generador/manifest: `src/riot_lol_cli/splash.py`
- Template activo: `templates/splash-viewer.html`
- Assets descargados: `assets/splash_arts/`
- Catalogo Data Dragon localizado: `data/ddragon-splash-catalog.json`
- Manifest: `data/splash-manifest.json`
- Viewer generado: `outputs/splash-viewer.html`
- JS del viewer: `assets/splash-viewer-app.js`
- Scripts relacionados: `scripts/update_ddragon_assets.py`, `scripts/download_splash_arts.py`, `scripts/bat/regenerar_splash_viewer.bat`

## Flujo principal

Data Dragon -> `assets/splash_arts/` + `data/ddragon-splash-catalog.json` -> `splash.py` -> `data/splash-manifest.json` -> `outputs/splash-viewer.html`

`scripts/update_ddragon_assets.py` regenera el catalogo, el manifest y el HTML
despues de sincronizar splash arts. El front muestra el parche Data Dragon y la
fecha de importacion desde el manifest.

## Estado observado 2026-05-02

- `data/splash-manifest.json`: 172 campeones y 2079 imagenes.
- `data/ddragon-splash-catalog.json`: Data Dragon `16.9.1`, locale `es_MX`.
- Verificadas skins recientes como `Annie Pandemonium` y `Vayne Maleficio Demoníaco`.
- Snapshot informativo, no contrato de datos.

## Deuda conocida

- Los assets dependen de Data Dragon y pueden quedar desactualizados frente al parche vivo si no se corre el updater.
- `outputs/splash-viewer.html` es generado; regenerar desde manifest/template antes de editarlo a mano.

## Documentacion relacionada

- `docs/splash-viewer.md`
- `AGENTS.md`
