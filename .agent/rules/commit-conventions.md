# Commit Conventions — riot_lol_cli

## Formato

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <descripción corta>

[cuerpo opcional]

[footer opcional]
```

## Types

| Type | Uso |
|------|-----|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de bug |
| `docs` | Solo documentación |
| `refactor` | Cambio de código sin fix ni feature |
| `chore` | Mantenimiento, dependencias, configs |
| `test` | Tests |
| `style` | Formato, whitespace (sin cambio de lógica) |
| `perf` | Mejora de performance |

## Scopes Comunes

| Scope | Área |
|-------|------|
| `cli` | CLI principal y commands |
| `api` | Riot API client |
| `meta` | Meta Analyzer |
| `draft` | Draft Advisor |
| `dashboard` | Dashboard HTML |
| `splash` | Splash Arts Viewer |
| `db` | Database / models |
| `scripts` | Scripts de utilidad |

## Ejemplos

```
feat(draft): add support for support synergy scoring
fix(api): handle 429 rate limit with exponential backoff
docs(meta): update META_ANALYZER_GUIA_COMPLETA with new anomaly types
chore: update requirements.txt with pinned versions
refactor(db): extract session management to context manager
```

## Reglas

- Descripción en imperativo: "add", "fix", "update" (no "added", "fixing")
- Máximo 72 caracteres en la primera línea
- Idioma: inglés para el mensaje, español en el cuerpo si hace falta contexto
- Un commit por cambio lógico. No mezclar fix + feat en el mismo commit.
