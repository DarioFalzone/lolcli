# Engineering Standards

Convenciones tecnicas para codigo, datos, paths, linting y limpieza.

## Python

- Python 3.9+.
- PEP 8, 4 espacios, line length 120.
- Nombres: `snake_case` para variables/funciones, `PascalCase` para clases, `UPPER_SNAKE_CASE` para constantes.
- Imports: stdlib, terceros, locales; separados por linea en blanco.
- Usar f-strings para interpolacion.
- Usar type hints donde ayuden sin volver rigido codigo interno simple.
- Docstrings publicas en espanol cuando el archivo ya documenta en espanol.

## Patrones del repo

- Paths runtime: preferir helpers de `src/riot_lol_cli/paths.py`.
- Riot payloads complejos: usar modelos Pydantic en `src/riot_lol_cli/schemas/`; evitar dict access fragil.
- CLI: `click.echo()` en comandos interactivos.
- Librerias/servidores/jobs: usar `logging`, no `print()`.
- HTML runtime de exports: templates Jinja2 en `templates/`.
- Database: modelos SQLAlchemy en `src/riot_lol_cli/database/models.py` son la fuente de verdad; `schema.sql` es referencia.

## Ruff y formato

Configuracion vigente en `pyproject.toml`:

- line length 120;
- target Python 3.9;
- `src = ["src", "scripts"]`;
- exclusiones para `.venv`, `outputs`, `templates` y `projects/legacy`.

Comandos:

```bash
ruff check src tests scripts
ruff format --check src tests scripts
```

## Dead code y archivos generados

- No borrar archivos solo porque no aparecen en un grep. Confirmar si son entry points manuales, templates, assets runtime, docs canonicas o proyectos standalone.
- `outputs/`, caches, DBs locales y artefactos generados no son fuente de verdad.
- Scripts manuales repetibles deben vivir en `scripts/`; diagnosticos one-off en `projects/dev-scratch/`.

## Frontend

- Stack: HTML, CSS y JavaScript vanilla. No hay React, bundler ni TypeScript.
- Tokens canonicos: `src/riot_lol_cli/draft_advisor/static/design-system/`.
- Identidad visual: Hextech dark, gold/cyan, dark mode, microcopy en espanol rioplatense con jerga gamer.
- En superficies visibles del Draft Advisor, usar español claro para UI, razones, perfiles y docs activas. Mantener IDs internos canónicos de Data Dragon (`Bard`, `MasterYi`) y localizar solo `display_name`/copy visible (`Bardo`, `Maestro Yi`).
- Tecnicos gamer permitidos cuando son mas entendibles que una traduccion forzada: `ADC`, `draft`, `teamfight`, `stun`, `dive`, `peel`, `poke`, `engage`, `roam`, `gank`, `matchup`, `all-in`, `frontline`, `wave`, `burst`, `scaling`.
- No duplicar paletas ni sistemas visuales si se puede extender `docs/design-system.md`.
