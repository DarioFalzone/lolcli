# CLI Match History

Proyecto activo para consultar partidas de League of Legends, enriquecerlas con
Data Dragon y exportar reportes HTML.

## Rutas runtime

- Entry point humano: `main.py`
- CLI Click: `src/riot_lol_cli/cli.py`
- Riot API client: `src/riot_lol_cli/api.py`
- Cache de partidas: `data/cache/`
- Rendering HTML: `src/riot_lol_cli/rendering.py`
- Templates activos: `templates/`
- Outputs generados: `outputs/`

## Flujo principal

`main.py` -> `cli.py` -> `api.py`/cache -> `rendering.py` -> `templates/` -> `outputs/`

## Comandos

```bash
python main.py --platform la2 --summoner "Nombre#TAG"
python -m riot_lol_cli.cli --platform la2 --summoner "Nombre#TAG"
python main.py generate --read-json data/cache/matches.json --html-template claude-4-5
```

## Deuda conocida

- Los outputs HTML son generados y no son fuente de verdad.
- Los templates activos viven en `templates/` raiz; no usar templates legacy bajo copias archivadas.

## Documentacion relacionada

- `AGENTS.md`
- `docs/getting-started.md`
- `docs/api-guide.md`
