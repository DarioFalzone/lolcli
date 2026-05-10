# Documentacion - riot_lol_cli

Indice de documentacion activa del proyecto. El mapa operativo por proyecto vive
en `../projects/README.md`.

## Guias Principales

| Documento | Descripcion |
|-----------|-------------|
| [getting-started.md](getting-started.md) | Guia de inicio rapido para todos los subsistemas |
| [api-guide.md](api-guide.md) | Riot API y APIs locales |
| [splash-viewer.md](splash-viewer.md) | Visor de splash arts |
| [design-system.md](design-system.md) | Tokens CSS y componentes visuales |

## Subsistemas

| Documento | Descripcion |
|-----------|-------------|
| [dashboard/README.md](dashboard/README.md) | Dashboard del Meta Analyzer: tabs, filtros, endpoints y troubleshooting |
| [meta_analyzer/README.md](meta_analyzer/README.md) | Meta Analyzer: arquitectura, DB, ADC Tracker, anomalias, tier lists y API |
| [draft_advisor/README.md](draft_advisor/README.md) | Draft Advisor: API, datos, scoring y SPA |

## Documentacion por Proyecto

Los manifiestos de `../projects/active/` son la entrada recomendada cuando se
trabaja por subsistema. Incluyen rutas reales de codigo/datos, comandos, deuda
conocida y docs relacionadas.

| Proyecto | Manifest |
|----------|----------|
| CLI Match History | `../projects/active/cli-match-history/README.md` |
| Splash Gallery | `../projects/active/splash-gallery/README.md` |
| Home Hub | `../projects/active/home-hub/README.md` |
| Draft Advisor | `../projects/active/draft-advisor/README.md` |
| Meta Analyzer + Dashboard | `../projects/active/meta-analyzer-dashboard/README.md` |
| Meta Scraper | `../projects/active/meta-scraper/README.md` |
| Jungle Meta | `../projects/active/jungle-meta/README.md` |
| Items Browser | `../projects/active/items-browser/README.md` |
| Assets y datos Riot | `../projects/active/assets-and-data/README.md` |
| Junglas Pro | `../projects/active/junglas-pro/README.md` |

## Documentacion Externa a `docs/`

| Path | Uso |
|------|-----|
| `AGENTS.md` | Mapa maestro para agentes IA |
| `projects/README.md` | Mapa por proyectos activos y legacy |
| `CLAUDE.md` | Shim corto para Claude Code; reglas largas en `.agent/rules/` |
| `KB/README.md` | Base de conocimiento estrategica |
| `bitacora_de_cambios.md` | Registro de cambios significativos |
| `claude-design-handoff/README.md` | Handoff visual para Claude Design |
| `claude-design-handoff/pattern-library-prompt.md` | Prompt maestro para pedir una libreria propia de patrones visuales en Claude Design |

Los reportes antiguos de auditoria, el ADC Tracker separado y los documentos historicos duplicados fueron absorbidos en estos documentos, reglas de agentes y bitacora. No crear nuevos reportes Markdown fuera del mapa canonico salvo decision explicita.
