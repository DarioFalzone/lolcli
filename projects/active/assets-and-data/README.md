# Assets y Datos Riot

Proyecto transversal para recursos descargados desde Riot/Data Dragon y datos
locales compartidos por los otros subsistemas.

## Rutas runtime

- Splash arts: `assets/splash_arts/`
- Iconos de items: `assets/items/`
- Mapeos de imagen/data id: `assets/data_id_imagen/`
- Cache y manifests: `data/`
- Draft Advisor KB estructurada: `data/draft_advisor/`
- Meta Scraper snapshots: `data/meta_scraper/`

## Scripts relacionados

- `scripts/update_ddragon_assets.py`
- `scripts/download_splash_arts.py`
- `scripts/fetch_adc_champions.py`
- `scripts/fetch_matches_full.py`

## Actualizacion Data Dragon

```bash
python scripts/update_ddragon_assets.py
```

El script usa la CDN publica de Data Dragon, no requiere Riot API key y aplica rate limiting configurable. Actualiza:

- `assets/items/*.png`
- `assets/data_id_imagen/items_ddragon.csv`
- `assets/splash_arts/**/*.jpg`
- `data/ddragon-splash-catalog.json`
- `data/splash-manifest.json`
- `outputs/splash-viewer.html`

Por defecto salta variantes con `parentSkin` porque no tienen splash art independiente.
Las skins base con chromas si se descargan. Si solo se quiere actualizar assets
sin regenerar el front, usar `--skip-gallery-regenerate`.

## Criterio de movimiento

No mover `assets/` ni `data/` sin actualizar codigo y tests: son rutas runtime
compartidas por CLI, Splash Gallery, Draft Advisor y Meta Scraper.

## Deuda conocida

- Algunos datos son curados manualmente y otros generados por scripts; revisar el
  manifest o README del subsistema antes de tratarlos como fuente canonica.
- Los snapshots observados de conteos de campeones, supports o imagenes son
  informativos y pueden cambiar con el parche.
