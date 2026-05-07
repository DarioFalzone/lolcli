# Draft Advisor

Proyecto activo del recomendador de picks ADC/Support basado en conocimiento
estructurado, perfiles y scoring local.

## Rutas runtime

- API FastAPI: `src/riot_lol_cli/draft_advisor/server.py`, `src/riot_lol_cli/draft_advisor/api.py`
- SPA: `src/riot_lol_cli/draft_advisor/static/`
- Motor: `src/riot_lol_cli/draft_advisor/analyzer.py`, `src/riot_lol_cli/draft_advisor/scoring.py`
- Datos: `data/draft_advisor/`
- KB estrategica: `KB/`
- Tests: `tests/draft_advisor/`

## Flujo principal

SPA -> `/api/v1/draft/*` -> `champion_data.py` -> `analyzer.py`/`scoring.py` -> JSON KB

El front arranca en modo `ADC` por defecto; `Soporte` queda como modo
seleccionable desde el control de rol objetivo.

En modo ADC, el motor aplica primero la prioridad personal+meta:

- `data/draft_advisor/personal_adc_mastery.json` define la maestria ADC del usuario, exclusiones y picks que nunca deben salir como primera opcion.
- `data/meta_scraper/normalized/latest_adc_tier.json` define el meta ADC vigente; se considera stale luego de 72 horas.
- La recomendacion principal requiere tier personal `S/A` y meta fuerte real: tier de scraping `S` o `climb_score >= 80`.
- Meta `A` con `climb_score < 80` queda como alternativa blanda (`fallback_meta_soft`), no como core.
- La KB puede vetar primeras opciones por linea, por ejemplo Nilah + Soraka contra Caitlyn + Nautilus (`fallback_lane_veto`).
- La KB tambien puede sumar bonus de matchup dentro del fit de draft; Xayah contra Malphite/Tahm Kench queda registrada como buena respuesta a engage frontal y frontline melee.
- El draft puede vetar primeras opciones aunque sean meta, por ejemplo hypercarries sin movilidad/frontline contra dive pesado (`fallback_draft_veto`).
- El fit de draft pesa 40% dentro de los candidatos que pasan gates de maestria/meta.
- Campeones detectados por scraping sin perfil local quedan reportados, no recomendados.

## Puerto

- Draft Advisor: `8001`

## Alertas conocidas

- Rosters actuales auditados: 172 campeones base, 32 perfiles ADC, 34 perfiles Support y 41 perfiles priority.
- Los perfiles y relaciones deben usar IDs canonicos de `champion_base.json` (`JarvanIV`, no `Jarvan`).
- Antes de revisar un bug visual del picker, validar `GET /api/v1/draft/health` y `GET /api/v1/draft/champions`; si devuelven 500, el front queda sin lista.
- Antes de cuestionar una recomendacion ADC, revisar los chips `Maestría`, `Meta`, `Subida`, `Scraping` y `Alternativa` que devuelve la API/UI.
- La microcopy visible debe quedar en español; se permiten tecnicismos de LoL como `draft`, `teamfight`, `stun`, `dive`, `peel`, `poke`, `engage`, `roam`, `gank`, `matchup`, `all-in`, `frontline` y `wave`.
- `KB/` no es documentacion generica del repo: solo debe absorber conocimiento estrategico util para el motor.

## Documentacion relacionada

- `docs/draft_advisor/`
- `KB/README.md`
- `.agent/rules/agent-workflow.md`
