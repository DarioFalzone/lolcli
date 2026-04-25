# Análisis de Dependencias

**Fecha:** 2026-04-23

## Dependencias Python (requirements.txt)

| Paquete | Versión Mínima | Uso | Notas |
|---------|---------------|-----|-------|
| click | >= 8.0.0 | CLI framework | Estable, bien mantenido |
| requests | >= 2.25.0 | HTTP client para Riot API | Podría actualizarse a >= 2.31.0 |
| sqlalchemy | >= 2.0.0 | ORM para meta analyzer DB | Versión moderna (2.x) |
| fastapi | >= 0.109.0 | API backend | Versión reciente |
| uvicorn[standard] | >= 0.27.0 | ASGI server | Con extras para performance |
| pydantic | >= 2.0.0 | Validación de datos | Versión moderna (2.x) |
| python-multipart | >= 0.0.6 | Form data parsing | Requerido por FastAPI |
| jinja2 | >= 3.1.0 | Template engine | Para HTML generation |
| Pillow | >= 10.0.0 | Procesamiento de imágenes (paleta de colores en `cli.py`) | Agregado en reorg 2026-04-24 |
| pytest | >= 7.4.0 | Testing | Instalado pero sin tests escritos |
| pytest-asyncio | >= 0.21.0 | Testing async | Para tests de FastAPI |
| python-dotenv | >= 1.0.0 | Variables de entorno | Lee .env automáticamente |

## Dependencias Implícitas (no en requirements.txt)

| Paquete | Usado en | Notas |
|---------|----------|-------|
| **sqlite3** | `verify_adc_tracker.py` | Stdlib, no necesita instalación |

## Observaciones

### Positivo
- Las versiones mínimas son razonablemente modernas
- No hay dependencias con vulnerabilidades conocidas graves (por inspección)
- SQLAlchemy 2.x y Pydantic 2.x son las versiones actuales

### Cambios Aplicados en Reorg 2026-04-24
1. ✅ **Pillow agregado** a `requirements.txt` (`Pillow>=10.0.0`)
2. ✅ **Alembic removido** de `requirements.txt` (no había migraciones definidas)

### Mejoras Recomendadas (futuras)
1. **Pinear versiones máximas** para reproducibilidad: `click>=8.0.0,<9.0.0`
2. **Separar dev dependencies:** Mover pytest y pytest-asyncio a `requirements-dev.txt`
3. **requests podría ser httpx:** Para soporte async nativo con FastAPI. No urgente.

## Dependencias Externas (APIs y Servicios)

| Servicio | Uso | Autenticación |
|----------|-----|---------------|
| Riot Games API | Summoner-V4, Match-V5, Account-V1 | API Key (24h dev tokens) |
| Data Dragon CDN | Assets estáticos (imágenes, datos de campeones) | Sin auth |
| SQLite (local) | Base de datos meta analyzer | Sin auth |
