# Coding Style — riot_lol_cli

## Python

- **Standard:** PEP 8
- **Indentation:** 4 espacios
- **Line length:** 120 caracteres máximo (no 79)
- **Imports:** stdlib primero, luego terceros, luego locales. Separados por línea en blanco.
- **Strings:** Usar f-strings para interpolación. Comillas dobles para strings en general.
- **Type hints:** Usar donde sea práctico. No obligatorio en funciones internas simples.
- **Docstrings:** En español. Formato Google-style para funciones públicas.

## Naming

| Tipo | Convención | Ejemplo |
|------|-----------|---------|
| Variables | snake_case | `match_data` |
| Funciones | snake_case | `get_summoner_by_name()` |
| Clases | PascalCase | `RiotClient`, `DatabaseManager` |
| Constantes | UPPER_SNAKE_CASE | `BASE_DIR`, `DATA_DRAGON_VERSION` |
| Archivos | snake_case | `data_collector.py` |
| Directorios | snake_case o kebab-case | `meta_analyzer/`, `draft_advisor/` |

## Patterns del Proyecto

- **Path resolution:** Usar `Path(__file__).parent` para paths relativos al módulo
- **Config loading:** JSON files en `config/` o `data/`
- **API clients:** Clases wrappers (`RiotClient` síncrono con `requests`, `AsyncRiotClient` asíncrono con `httpx`). Ambas implementan backoff exponencial para 429.
- **Data Validation:** Modelos estrictos `Pydantic V2` en `src/riot_lol_cli/schemas/` para mapear respuestas de la API de Riot (ej. Match-V5). ¡No usar diccionarios crudos (dict access) para parsear respuestas complejas!
- **CLI commands:** Click decorators con `@cli.command()`
- **HTML generation:** Jinja2 templates en `templates/`
- **DB access:** SQLAlchemy ORM con `DatabaseManager.get_session()`

## Logging y Linting

- **Logging:** Prohibido usar `print()` en librerías o servidores en segundo plano (`api_server`, `data_collector`). Usar el módulo `logging` de Python. `print()` y `click.echo()` solo están permitidos en los comandos interactivos de la CLI.
- **Ruff:** El proyecto usa Ruff como linter y formatter. Se aplican reglas estrictas incluyendo ordenamiento de imports (`I`) y actualización de sintaxis moderna (`UP`). Por ejemplo, usar `dict` y `list` en lugar de `typing.Dict` y `typing.List`.

## HTML/Templates

- Templates Jinja2 con extensión `.html`
- CSS y JS embebidos en los templates (no archivos separados, excepto draft_advisor/static/)
- Diseño Hextech (tema oscuro LoL) con colores: `#010a13`, `#0a1628`, `#c89b3c`, `#f0e6d2`
