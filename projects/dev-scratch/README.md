# Dev Scratch

Herramientas manuales y experimentos locales que no forman parte del paquete,
tests ni runtime productivo.

## Contenido

- `draft_debug_score.py`: inspeccion manual del scoring del Draft Advisor.
- `draft_test_post.py`: POST manual contra `http://localhost:8001/api/v1/draft/recommend`.

## Reglas

- No importar estos scripts desde `src/riot_lol_cli/`.
- Si un script se vuelve util y repetible, moverlo a `scripts/` o convertirlo
  en test bajo `tests/`.
- Si queda obsoleto tras una iteracion, se puede eliminar.

