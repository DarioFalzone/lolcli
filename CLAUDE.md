# riot_lol_cli — Instrucciones para Claude Code

## Qué es este proyecto

CLI + servicios web en Python para League of Legends. Subsistemas:
- **Draft Advisor** (FastAPI, puerto 8001) — recomienda picks ADC/Support en ranked
- **Meta Analyzer** (FastAPI, puerto 8000) — tier lists, matchups, anomaly detection
- **CLI** — match history, generación de HTML estáticos, splash arts gallery

Stack frontend: **HTML + CSS + JS vanilla**. Sin React, sin bundler, sin TypeScript.

Documentación completa: [`AGENTS.md`](AGENTS.md) | [`docs/getting-started.md`](docs/getting-started.md)

---

## Comandos habituales

```bash
# Activar entorno (Windows)
.venv\Scripts\activate

# Draft Advisor (puerto 8001)
python -m riot_lol_cli.draft_advisor.server
# → http://localhost:8001/draft

# Meta Analyzer API (puerto 8000)
python scripts/run_api.py
# → http://localhost:8000/dashboard-enhanced

# Tests
pytest
pytest --cov=src/riot_lol_cli --cov-report=term-missing

# Linting
ruff check src/ --fix

# Match history (requiere API key en .env)
python main.py --platform la2 --summoner "Nombre#TAG" --html-template claude-4-5

# Regenerar splash viewer
python -m riot_lol_cli.cli build-splash-manifest
python -m riot_lol_cli.cli generate-splash-viewer
```

---

## ⚠️ REGLA ANTIDRAFT DOCUMENTACIONAL

**Toda iteración significativa debe actualizar la documentación antes del commit final.**
Ver protocolo completo: [`.agent/rules/documentation-protocol.md`](.agent/rules/documentation-protocol.md)

### Qué actualizar y cuándo

| Cambio | Documentos a actualizar |
|--------|------------------------|
| Nuevo feature / subsistema | `bitacora_de_cambios.md` + `docs/` del subsistema + `AGENTS.md` si cambia arquitectura |
| Nuevo endpoint API | `docs/draft_advisor/README.md` o `docs/meta_analyzer/README.md` |
| Cambio en comandos de ejecución | `docs/getting-started.md` |
| Cambio en design system / tokens | `docs/design-system.md` |
| Cambio en schemas Pydantic | `docs/draft_advisor/README.md` (sección payload) |
| Nuevo archivo de datos JSON | `docs/draft_advisor/README.md` (sección Datos) |
| Bug fix significativo | `bitacora_de_cambios.md` |
| Refactor de arquitectura | `AGENTS.md` + `bitacora_de_cambios.md` |

### Formato para bitacora_de_cambios.md

```markdown
## [YYYY-MM-DD] Título breve del cambio

### Qué se hizo
- bullet con lo concreto

### Archivos modificados clave
- `ruta/archivo.py` — qué cambió y por qué
```

---

## Convenciones rápidas

- **Commits:** Conventional Commits (`feat/fix/refactor/docs/chore`) — ver [`.agent/rules/commit-conventions.md`](.agent/rules/commit-conventions.md)
- **Python:** snake_case, PascalCase para clases, UPPER_SNAKE para constantes
- **CSS tokens:** `--arc-*` (gold/cyan), `--forge-*` (fondos), `--state-*` (error/success/warning)
- **Idioma código:** inglés. Documentación: español.
- **Tests:** obligatorios para features nuevos. Coverage ≥ 30%.

---

## Paths críticos

```
src/riot_lol_cli/draft_advisor/   → Draft Advisor (motor principal)
  ├── static/                     → Frontend SPA
  │   ├── design-system/          → Tokens CSS canónicos
  │   ├── styles.css              → Estilos SPA
  │   └── app.js                  → Lógica frontend
  ├── scoring.py                  → Motor de scoring ADC+Support
  ├── schemas.py                  → Modelos Pydantic V2
  └── champion_data.py            → Loader de JSONs

data/draft_advisor/               → Knowledge base en JSON
  ├── champion_base.json          → 171 campeones
  ├── adc_profiles.json           → 24 perfiles ADC
  ├── support_profiles.json       → 10 soportes (fase 1, pendiente 14 más)
  └── scoring_weights.json        → Pesos del motor

KB/                               → Base de conocimiento estratégico (markdown)
templates/                        → Jinja2 para exports HTML estáticos
docs/                             → Documentación técnica del proyecto
.agent/rules/                     → Convenciones y reglas para agentes IA
```

---

## Upgrades conocidos (NO implementar sin pedido explícito)

- **Pool de Campeones**: comentado en `index.html` — backend ya implementado
- **14 soportes fase 2**: Blitzcrank, Rakan, Rell, Alistar, Nami, Yuumi, Renata, Zyra, Brand, Xerath, Vel'Koz, Swain, Senna, Bard
- **Accesibilidad ARIA**: botones icon-only sin `aria-label`, sin `prefers-reduced-motion` en SPA
- **Migración tokens SPA NO MIGRAR**: `--bg-primary`, `--text-primary`, `--green` tienen valores distintos al canónico
- **Dashboard a Jinja2**: `dashboard_enhanced.py` tiene HTML embebido en f-string Python
