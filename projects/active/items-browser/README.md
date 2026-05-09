# Items Browser

Catalogo navegable de items de League of Legends con nombres en ingles y espanol, agrupados por uso (botas, componentes, legendarios, consumibles, trinkets, jungla, obsoletos) y filtrable por busqueda.

## Datos

Fuente de verdad: `data/items/database.json`. Generado por `scripts/update_items_database.py` desde Data Dragon (`https://ddragon.leagueoflegends.com`).

Schema por item:

```json
{
  "id": 6699,
  "name_en": "Voltaic Cyclosword",
  "name_es": "Espada ciclovoltaica",
  "plaintext_en": "...",
  "plaintext_es": "...",
  "tags": ["Damage", "ArmorPenetration", ...],
  "stats": {"FlatPhysicalDamageMod": 55},
  "gold_total": 2900,
  "gold_base": 863,
  "gold_sell": 2030,
  "purchasable": true,
  "depth": 3,
  "from": [2020, 1036, 1036],
  "into": [],
  "maps": ["11", "12", "21", "35"],
  "image": "6699.png",
  "deprecated": false
}
```

Items obsoletos (presentes en CSV legacy `assets/data_id_imagen/items_ddragon.csv` o `assets/items/*.png` pero ausentes en la version actual de DDragon) se marcan con `deprecated: true` y se exponen aparte en el grupo `deprecated`.

Data Dragon tambien incluye variantes por mapa/modo con el mismo nombre e icono
o casi el mismo item (por ejemplo Arena `224633` para Riftmaker o variantes
internas de smite `1105`-`1107`). El catalogo visual las oculta por defecto
para no mostrar duplicados; el JSON bruto se conserva y la API puede exponerlas
con `include_variants=true`.

## Quick start

```powershell
scripts\bat\items_browser.bat
```

El bat regenera la database si no existe y arranca el server en puerto 8004.

Manual:

```powershell
.\.venv\Scripts\python.exe scripts/update_items_database.py
.\.venv\Scripts\python.exe -m riot_lol_cli.items_browser.server
```

## Endpoints

| Metodo | Path | Descripcion |
|--------|------|-------------|
| `GET` | `/` | SPA |
| `GET` | `/health` | version, total/current/catalog/deprecated count |
| `GET` | `/api/v1/items/all?include_deprecated=&include_variants=` | lista completa filtrada para catalogo |
| `GET` | `/api/v1/items/{id}` | detalle individual |
| `GET` | `/api/v1/items/groups?include_variants=` | buckets por uso |
| `GET` | `/api/v1/items/categories` | tags Riot |
| `GET` | `/api/v1/items/search?q=&lang=en\|es&include_variants=` | busqueda por substring |

## Refrescar items

Cuando Riot publica nuevos items o renombra los existentes:

```powershell
.\.venv\Scripts\python.exe scripts/update_items_database.py
```

El script:

1. Resuelve la version actual de Data Dragon (versions.json).
2. Descarga `item.json` en `en_US` y `es_ES`.
3. Construye la database mezclada en `data/items/database.json`.
4. Compara contra `assets/items/*.png` y CSV legacy: items ausentes en DDragon vigente quedan marcados `deprecated: true`.
5. Descarga PNG faltantes (items nuevos) a `assets/items/`.

## Configuracion

| Var | Default |
|-----|---------|
| `LOLCLI_ITEMS_BROWSER_HOST` | `0.0.0.0` |
| `LOLCLI_ITEMS_BROWSER_PORT` | `8004` |
