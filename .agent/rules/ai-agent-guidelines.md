# AI Agent Guidelines — riot_lol_cli

## Cómo trabajar en este repo como agente de IA

### Antes de hacer cambios

1. **Leé `AGENTS.md` en la raíz** para entender la arquitectura general
2. **Identificá el subsistema afectado** y leé su AGENTS.md si existe
3. **Verificá las convenciones** en `.agent/rules/` antes de escribir código
4. **No ejecutes código del repo** sin necesidad — este es un proyecto con API keys y rate limits

### Navegación del código

```
Flujo recomendado:
1. AGENTS.md (visión global)
2. src/riot_lol_cli/__init__.py (versión, exports)
3. src/riot_lol_cli/cli.py (entry point, paths)
4. El módulo específico que necesitás modificar
```

### Paths importantes

- **Entry point:** `main.py` → `src/riot_lol_cli/cli.py`
- **API client:** `src/riot_lol_cli/api.py`
- **Templates:** `templates/` (root, NO `src/riot_lol_cli/templates/`)
- **Datos:** `data/` (cache, draft_advisor, splash-manifest)
- **Config:** `config/version.json`
- **Scripts:** `scripts/` (scripts de utilidad y automatización)

### Cómo proponer cambios

1. **Una cosa a la vez:** un fix, un feature. No mezclar.
2. **Conventional Commits:** ver `.agent/rules/commit-conventions.md`
3. **No tocar paths de otros subsistemas** sin verificar dependencias cruzadas
4. **Si movés archivos:** usar `git mv` para preservar historial
5. **Si tocás `cli.py`:** verificar que `BASE_DIR` y paths derivados siguen funcionando
6. **Bitácora de Cambios:** SIEMPRE que completes una iteración significativa (ej. implementar un feature, refactorizar, resolver un bug complejo), debés actualizar el archivo `bitacora_de_cambios.md` en la raíz del repositorio agregando una nueva entrada con la fecha y un resumen detallado de lo que hiciste.

### Cosas que NO hacer

- **No hardcodear API keys** — usar `os.getenv("RIOT_API_KEY")`
- **No commitear `.env`** — está gitignored
- **No modificar `config/version.json` manualmente** — se auto-incrementa
- **No borrar archivos en `_quarantine/` o `_archive/`** — esa decisión es del usuario
- **No instalar dependencias** sin agregarlas a `requirements.txt`
- **No crear archivos en `outputs/`** — es gitignored, se genera automáticamente

### Testing

- Existen tests implementados usando `pytest` y `pytest-cov` (ver `.agent/rules/testing-guidelines.md`).
- Si agregás funcionalidad nueva, DEBÉS agregar tests.
- Para verificar que no rompiste nada, ejecutá `pytest`. La cobertura global no debe bajar del 30% (actualmente >50%).

### Idioma

- **Código:** inglés (variables, funciones, clases)
- **Documentación:** español
- **Commits:** inglés (type + scope + descripción), español en el body si hace falta
- **Comentarios en código:** español donde ya existe, inglés para código nuevo
