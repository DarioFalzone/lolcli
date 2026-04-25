# Security Guidelines — riot_lol_cli

## Secretos y Credenciales

### Regla Fundamental
**NUNCA commitear secretos al repositorio.** Esto incluye:
- API keys de Riot Games (`RGAPI-*`)
- Tokens de cualquier servicio
- Contraseñas
- Certificados privados

### Manejo de API Key

1. La Riot API key va en `.env` (gitignored)
2. Template en `.env.example` (commiteado, sin valores reales)
3. En código, leer con `os.getenv("RIOT_API_KEY")`
4. Los dev keys de Riot expiran cada 24h — renovar en https://developer.riotgames.com/

### Verificación Pre-Commit

Antes de commitear, verificar:
```bash
# Buscar posibles secretos
grep -r "RGAPI-" --include="*.py" .
grep -r "api_key\s*=" --include="*.py" .
```

### Archivos Sensibles en .gitignore

```
.env
.env.local
.env.*.local
*.pem
*.key
config/api_key.txt
```

## Rate Limiting

- La API de Riot tiene rate limits estrictos
- El client (`api.py`) maneja `Retry-After` headers
- No hacer requests en loops sin throttling
- Para batch operations (como en `data_collector.py`), usar delays entre requests

## Base de Datos

- SQLite local (`data/meta_analyzer.db`)
- No exponer la BD a la red
- El API server solo acepta queries parametrizadas via SQLAlchemy ORM (no SQL raw)

## Dependencias

- Mantener `requirements.txt` actualizado
- Revisar versiones periódicamente por vulnerabilidades conocidas
- No instalar dependencias innecesarias
