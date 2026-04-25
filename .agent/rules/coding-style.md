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
- **API clients:** Clase wrapper con métodos que retornan dicts
- **CLI commands:** Click decorators con `@cli.command()`
- **HTML generation:** Jinja2 templates en `templates/`
- **DB access:** SQLAlchemy ORM con `DatabaseManager.get_session()`

## HTML/Templates

- Templates Jinja2 con extensión `.html`
- CSS y JS embebidos en los templates (no archivos separados, excepto draft_advisor/static/)
- Diseño Hextech (tema oscuro LoL) con colores: `#010a13`, `#0a1628`, `#c89b3c`, `#f0e6d2`
