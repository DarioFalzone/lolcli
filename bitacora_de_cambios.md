# Bitácora de Cambios

Este documento registra los cambios significativos, refactorizaciones y evoluciones arquitectónicas del proyecto `riot_lol_cli`.

**Los agentes de IA deben actualizar este archivo luego de cada iteración significativa para mantener un registro histórico de los cambios realizados.**

---

## [2026-05-07] Fix CI Python 3.9 — from __future__ import annotations

### Que se hizo
- CI de GitHub Actions fallaba con exit code 2 (error de coleccion de pytest, no test failure).
- Causa raiz: `meta_scraper` usaba sintaxis PEP 604 (`X | None`) sin `from __future__ import annotations`. Python 3.9 evalua las anotaciones en runtime y lanza `TypeError`. Local pasaba porque el entorno es Python 3.13.
- Fix: se agrego `from __future__ import annotations` (PEP 563) al inicio de 5 archivos del modulo `meta_scraper` para hacer las anotaciones lazy y compatibles con 3.9.
- Los 132 tests siguieron pasando tras el fix. Commit: `bfa31de`.

### Archivos modificados clave
- `src/riot_lol_cli/meta_scraper/server.py` — `from __future__ import annotations`
- `src/riot_lol_cli/meta_scraper/orchestrator.py` — idem
- `src/riot_lol_cli/meta_scraper/normalizer.py` — idem
- `src/riot_lol_cli/meta_scraper/adapters/base.py` — idem
- `src/riot_lol_cli/meta_scraper/adapters/ugg.py` — idem

### Verificacion
- `pytest -q`: 132/132 OK post-fix.
- `ast.parse(..., feature_version=(3,9))` corrido sobre `src/`, `tests/`, `scripts/`: 0 errores.
- CI de GitHub Actions verde tras push.

---

## [2026-05-07] Correccion post-auditoria independiente

### Que se hizo
- Se corrigio drift documental posterior a la auditoria `f0d0d82..67c895b`: Playwright ya esta en `requirements.txt`, y el paso manual vigente es `playwright install chromium`.
- Se reemplazaron referencias operativas a `_archive/` por `projects/legacy/` y se marco `data/supports_list.json` como dato historico eliminado/absorbido.
- Se cambiaron comandos runtime activos de `src.riot_lol_cli.api_server:app` a `riot_lol_cli.api_server:app`.
- Se reforzo `tests/meta_scraper/test_adapter_name_maps.py` con asserts por plataforma para `KSante` y allowlist explicita de duplicados de U.GG.
- Se refactorizo `ScoringEngine._get_adc_priority` en helpers de bloqueo, contexto meta, vetos, core y fallbacks sin cambiar eligibilities ni scoring.
- Draft Advisor y Meta Scraper ahora exponen `create_app()` y mantienen `app = create_app()` para compatibilidad con imports y entrypoints actuales.
- Se dejo el prompt documentacional para Claude en el cierre de la iteracion, sin crear un Markdown adicional.

### Archivos modificados clave
- `src/riot_lol_cli/draft_advisor/scoring.py`
- `src/riot_lol_cli/draft_advisor/server.py`
- `src/riot_lol_cli/meta_scraper/server.py`
- `tests/meta_scraper/test_adapter_name_maps.py`
- `AGENTS.md`, `README.md`, `projects/README.md`, `docs/getting-started.md`
- `.agent/rules/security-and-testing.md`

---

## [2026-05-07] Auditoría completa, cleanup git y refactors seguros

### Que se hizo
- Auditoría documental: se confirmó que README.md, AGENTS.md, projects/README.md, docs/ y .agent/rules/ son la fuente viva sin huérfanos.
- Cleanup git monumental (392 cambios pendientes desde reorganizaciones previas) commiteado en 11 lotes lógicos:
  1. `chore(rules)`: 7 rules antiguas → 4 canónicas en `.agent/rules/`.
  2. `feat(structure)`: adopción de `projects/` con 7 activos + 5 legacy; `riot-lol-cli/` raíz movido a `projects/legacy/riot-lol-cli/` (rename detectado).
  3. `feat(meta-scraper)`: módulo nuevo en puerto 8002 con adapters OP.GG/LoLalytics/U.GG via Playwright + tests.
  4. `docs`: colapso de 35 archivos fragmentados (~9k líneas) en READMEs canónicos (`_analysis/`, `REORGANIZATION_*`, `docs/adc_tracker/`, `docs/changelog/`, `claude-design-handoff/*`).
  5. `chore(archive)`: drop de `_archive/` y `_quarantine/` (absorbidos en `projects/legacy/` + bitácora).
  6. `feat(draft-advisor,kb)`: integración NotebookLM + ADC priority policy + 7 perfiles AP-mage bot + tests draft.
  7. `feat(assets)`: refresh Data Dragon (~100 items, ~70 splash arts) + nuevo `scripts/update_ddragon_assets.py`.
  8. `chore(core)`: alineación src/ + scripts/ con docs consolidadas; drop de `*/AGENTS.md` per-módulo.
  9. `chore(config)`: AGENTS.md como mapa maestro; CLAUDE.md como shim; `logs/` ignorado; ruff y CI refrescados.
  10. `docs(handoff)`: snapshot del design system de Claude Design.
- Refactors seguros aplicados:
  - **Bug fix**: los 3 adapters de Meta Scraper mapeaban `K-Sante` → `Ksante`, pero `champion_base.json` usa `KSante` (canonical Riot). Fix en opgg.py, lolalytics.py, ugg.py.
  - **Test de consistencia**: `tests/meta_scraper/test_adapter_name_maps.py` verifica que los 3 adapters comparten targets canónicos y que cada target existe en `champion_base.json`. Atrapó el bug de KSante.
  - **Dependencias**: `playwright>=1.40.0` declarado en `requirements.txt` con nota de `playwright install chromium`.
  - **Código muerto**: drop de `data/junglers_list.json` y `data/supports_list.json` (no referenciados).
- Auditoría y actualización de CLAUDE.md + 4 rules `.agent/rules/`:
  - `CLAUDE.md` extendido con setup runtime y verificación mínima.
  - `agent-workflow.md`: removidas referencias a `_archive/`/`_quarantine/` (no existen); agregada mención al test de consistencia y a Playwright en requirements.
  - `engineering-standards.md`: actualizada lista de exclusiones de ruff.
  - `pyproject.toml`: ruff exclude limpio (sin `_archive`/`_quarantine`).
- Documentación nueva:
  - `projects/legacy/riot-lol-cli/README.md` extendido con contexto del proyecto **deshu** y referencia al frontend `outputs/claude-4-5/deshu-las-claude-4-5.html`.
  - `README.md` raíz expandido a catálogo completo con tabla de proyectos activos/legacy, capacidades por dominio, comandos clave y mapa de docs.

### Archivos modificados clave
- `README.md` - catálogo completo del repo.
- `CLAUDE.md` - shim extendido con setup runtime.
- `.agent/rules/agent-workflow.md` - alineado con realidad post-reorg.
- `.agent/rules/engineering-standards.md` - exclusiones ruff actualizadas.
- `pyproject.toml` - exclude sin `_archive`/`_quarantine`.
- `requirements.txt` - playwright>=1.40.0 declarado.
- `src/riot_lol_cli/meta_scraper/adapters/{opgg,lolalytics,ugg}.py` - fix KSante.
- `tests/meta_scraper/test_adapter_name_maps.py` - test de consistencia (nuevo).
- `projects/legacy/riot-lol-cli/README.md` - contexto deshu + frontend documentado.
- `data/{junglers_list,supports_list}.json` - eliminados (huérfanos).
- `.gitignore` - `logs/` ignorado.

### Verificación
- 132 tests pasan (`pytest -q`): 129 baseline + 3 nuevos en `test_adapter_name_maps.py`.
- 11 commits lógicos sobre `main`.

---

## [2026-05-05] Draft Advisor - veto Nilah/Soraka y meta ADC estricto

### Que se hizo
- Se endurecio la politica de primera recomendacion ADC: requiere maestria `S/A` y meta fuerte real (`tier S` o `climb_score >= 80`).
- Los ADC con meta `A` y `climb_score < 80` pasan a `fallback_meta_soft`; pueden verse como alternativa, pero no compiten como core contra picks realmente fuertes.
- Se agrego la regla KB `Nilah + Soraka vs Caitlyn + Nautilus` con `score_delta -35` y `top_pick_block`, porque la linea pierde prioridad, crash, rango seguro y queda expuesta a hook/all-in.
- Se agrego una regla general para ADCs de rango muy bajo con support sustain contra bully de rango + support engage/catcher.
- Se registro el aprendizaje `Xayah vs Malphite/TahmKench` como bonus KB de matchup: Xayah gana fit contra engage frontal predecible y frontlines melee por R + plumas, sin saltarse el gate de meta/maestria.
- Se agrego `fallback_draft_veto` para impedir top picks de hypercarries sin movilidad/frontline contra dive o burst pesado, aunque sean fuertes en meta global.
- Se ajusto el perfil de Nilah para reflejar menor prioridad de linea y peor respuesta al poke/rango alto.

### Archivos modificados clave
- `src/riot_lol_cli/draft_advisor/scoring.py`
- `src/riot_lol_cli/draft_advisor/champion_data.py`
- `data/draft_advisor/kb/structured/matchup_rules.json`
- `data/draft_advisor/adc_profiles.json`
- `data/draft_advisor/kb/research/matchups/mu-nilah-soraka-vs-caitlyn-nautilus.md`
- `data/draft_advisor/kb/research/matchups/mu-xayah-vs-malphite-tahmkench.md`
- `tests/draft_advisor/test_adc_priority_policy.py`

---

## [2026-05-04] Draft Advisor - prioridad ADC, meta y lenguaje

### Que se hizo
- Se agregaron controles de politica personal ADC: `excluded_from_recommendations` y `never_top_pick`.
- Vladimir quedo excluido de recomendaciones ADC por preferencia personal del usuario.
- Ezreal puede aparecer como alternativa si corresponde, pero nunca como primera opcion.
- Se reajusto el puntaje final ADC a `30%` maestria personal, `30%` meta scraping y `40%` fit de draft para que la composicion y los matchups vuelvan a pesar fuerte dentro de los candidatos validos.
- Se cambio el badge superior de `Datos` a `Data Dragon` y se agrego hora al campo `Actualizado`, usando `last_verified_at` con timestamp ISO.
- Se retiro del header la leyenda `ADC meta pendiente/OK` para evitar ruido visual; el estado del meta ADC queda visible en los chips de cada recomendacion.
- Se agrego `data/draft_advisor/personal_adc_mastery.json` como fuente editable de la tier list personal ADC, con la captura `KB/tier list adc 04 05 2026.png` como evidencia visual y entradas dudosas en `needs_review`.
- El scoring ADC ahora aplica un gate personal+meta antes de ordenar: top pick requiere maestria `S/A` y scraping ADC `S/A`; meta `B` o inferior queda como fallback, y tier personal `B` solo entra si el scraping es `S`.
- El puntaje final ADC queda en `30%` maestria personal, `30%` meta scraping y `40%` fit de draft. La logica de draft/KB vuelve a pesar fuerte, sin permitir que picks fuera de maestria/meta dominen.
- El Draft Advisor detecta snapshot ADC faltante/stale (>72h), devuelve warning y reporta campeones del scraping sin perfil local como `meta_only_missing_profiles`.
- La API y el front exponen chips de auditoria por pick: `Maestría`, `Meta`, `Subida`, `Scraping` y `Alternativa`.
- Se actualizaron golden drafts para reflejar el nuevo contrato ADC y evitar expectativas antiguas que favorecian picks meta-bajos como Ezreal/Vayne/KogMaw.
- Se saneo lenguaje visible del Draft Advisor: `Bard` se muestra como `Bardo`, `Master Yi` como `Maestro Yi`, los perfiles activos y notas de KB del Drafter quedaron en español, y se mantiene una lista acotada de terminos gamer permitidos (`ADC`, `draft`, `teamfight`, `stun`, `dive`, `peel`, `poke`, `engage`, `roam`, `gank`, `matchup`, `all-in`, `frontline`).
- `jungler_archetypes.json` ahora usa IDs canonicos (`MasterYi`, `LeeSin`, `JarvanIV`, `RekSai`, `XinZhao`, `MonkeyKing`, `Belveth`) para evitar drift entre nombres visibles y relaciones internas.

### Archivos modificados clave
- `data/draft_advisor/personal_adc_mastery.json`
- `src/riot_lol_cli/draft_advisor/champion_data.py`
- `src/riot_lol_cli/draft_advisor/scoring.py`
- `src/riot_lol_cli/draft_advisor/schemas.py`
- `src/riot_lol_cli/draft_advisor/api.py`
- `src/riot_lol_cli/draft_advisor/static/app.js`
- `src/riot_lol_cli/draft_advisor/static/styles.css`
- `tests/draft_advisor/test_adc_priority_policy.py`
- `data/draft_advisor/kb/evals/golden_drafts.json`
- `docs/draft_advisor/README.md`
- `projects/active/draft-advisor/README.md`
- `KB/README.md`
- `.agent/rules/security-and-testing.md`

---

## [2026-05-03] Draft Advisor - fecha visible de ultimo update

### Que se hizo
- El header del Draft Advisor ahora muestra `Parche`, `Datos` y `Actualizado`, usando `last_verified_at` de `/api/v1/draft/meta/version-info`.
- Se agrego formateo local `dd/mm/aaaa` para la fecha de ultimo update y se subio el cache bust del front a `app.js?v=12`.
- Se ajusto el badge para tolerar el texto mas largo sin desbordar en pantallas chicas.

### Archivos modificados clave
- `src/riot_lol_cli/draft_advisor/static/app.js`
- `src/riot_lol_cli/draft_advisor/static/index.html`
- `src/riot_lol_cli/draft_advisor/static/styles.css`
- `docs/draft_advisor/README.md`

---

## [2026-05-03] Draft Advisor - auditoria y guardrails de datos

### Que se hizo
- Se agrego `tests/draft_advisor/test_data_integrity.py` para validar carga de `ChampionDataService`, conteos actuales y referencias con IDs canonicos en perfiles ADC/Support/Priority.
- Se documento el contrato de IDs canonicos en `.agent/rules/security-and-testing.md`, `AGENTS.md`, `docs/draft_advisor/README.md` y `projects/active/draft-advisor/README.md`.
- Se sincronizo `data_manifest.json` a `live_patch_label=16.9` y `static_data_version=16.9.1`, cubierto por el test de integridad.
- Se ajusto el scoring ADC para que Yasuo bot quede tratado como pick de nicho: requiere setup de airborne y valor real contra poke/proyectiles; queda penalizado contra dive/burst sin ese contexto.
- Se reforzo el scoring anti-tank para priorizar tank-shredders con alto anti-tank y DPS a objetivos, evitando que mages AP genericos tapen casos de Vayne/KogMaw.
- Se sincronizaron tests/evals: roster Support actual de 34 perfiles, golden draft que acepta `Kaisa` como carry movil con engage aliado, y test anti-enchanter que acepta counters hard actuales (`Camille`/`Pantheon`).
- Se limpio lint/formato dentro de `src/riot_lol_cli/draft_advisor` y `tests/draft_advisor`.

### Archivos modificados clave
- `src/riot_lol_cli/draft_advisor/scoring.py`
- `src/riot_lol_cli/draft_advisor/api.py`
- `tests/draft_advisor/test_data_integrity.py`
- `tests/draft_advisor/test_antimeta.py`
- `tests/draft_advisor/test_notebook_kb.py`
- `data/draft_advisor/data_manifest.json`
- `data/draft_advisor/kb/evals/golden_drafts.json`
- `.agent/rules/security-and-testing.md`
- `docs/draft_advisor/README.md`
- `projects/active/draft-advisor/README.md`

---

## [2026-05-03] Draft Advisor - fix carga de campeones

### Que se hizo
- Se corrigio un drift de IDs en `data/draft_advisor/adc_profiles.json`: `Seraphine.best_with` apuntaba a `Jarvan`, pero el ID canonico en `champion_base.json` es `JarvanIV`.
- El error rompia la validacion cruzada de `ChampionDataService` y hacia que `/api/v1/draft/health` y `/api/v1/draft/champions` devolvieran `500`, dejando vacio el selector del front.
- Se verifico nuevamente la API local: health queda `ok` y el endpoint de campeones devuelve `172` campeones.

### Archivos modificados clave
- `data/draft_advisor/adc_profiles.json`

---

## [2026-05-03] Draft Advisor — 7 nuevos perfiles ADC de magos AP bot lane

### Que se hizo
- Se corrio el Meta Scraper y se analizó el snapshot ADC completo (58 campeones, 3 fuentes, patch 16.9).
- Se identificaron 7 picks S/A tier sin perfil en `adc_profiles.json` — el Drafter los ignoraba completamente porque el scoring solo itera sobre `_adc_profiles.keys()`.
- Se crearon perfiles curados para: **Vladimir** (CS 84, WR 55%), **Karthus** (CS 82, WR 54.6%), **Seraphine** (CS 82, WR 54.6%), **Swain** (CS 77, WR 53.8%), **Veigar** (CS 75, WR 53.5%), **Ziggs** (CS 73, WR 53%), **Yasuo** (CS 64, WR 52.7%).
- Yasuo recibió teoría estratégica completa desde la KB del proyecto: condiciones de pick (airborne support, comp de Attack), counter proyectiles con Windwall, gestión de oleada (crash wave / evitar slow push enemigo).
- Se agregó `off_roles: ["Bot"]` a Vladimir, Karthus y Swain en `champion_base.json` (los otros ya lo tenían).
- Tendencia meta identificada: el patch 16.9 favorece **magos AP en bot lane** — Vladimir, Karthus, Seraphine se suman a Brand como picks tier S con la nueva runa.
- Servidor reiniciado para cargar los 32 perfiles ADC activos.

### Archivos modificados clave
- `data/draft_advisor/adc_profiles.json` — 7 perfiles nuevos; total: 25 → 32 perfiles
- `data/draft_advisor/champion_base.json` — off_roles Bot agregado a Vladimir, Karthus, Swain

---

## [2026-05-03] Draft Advisor default ADC

### Que se hizo
- Se dejo `ADC` seleccionado por defecto en el selector de rol objetivo del front del Draft Advisor.
- Se elimino la leyenda `ADC (Tirador)` y toda referencia visible a `Tirador` en el front activo.
- Se alineo el estado inicial JS (`targetRole: 'adc'`) con el valor seleccionado en HTML.
- Se actualizo la leyenda del resumen a `Amenaza Enemiga al ADC`.
- Se actualizo el cache bust del front a `app.js?v=11`.

### Archivos modificados clave
- `src/riot_lol_cli/draft_advisor/static/index.html`
- `src/riot_lol_cli/draft_advisor/static/app.js`
- `docs/draft_advisor/README.md`
- `projects/active/draft-advisor/README.md`

---

## [2026-05-02] Actualizacion Data Dragon assets 16.9.1

### Que se hizo
- Se agrego `scripts/update_ddragon_assets.py` para sincronizar items, CSV de items y splash arts desde Data Dragon con rate limiting configurable.
- Se actualizo la version default de Data Dragon a `16.9.1`.
- Se regenero `assets/data_id_imagen/items_ddragon.csv` y se descargaron `705` iconos de items.
- Se descargaron `61` splash arts faltantes en total y se regenero `data/splash-manifest.json` con `172` campeones y `2079` imagenes, alineado al catalogo oficial de skins base.
- Se agrego `data/ddragon-splash-catalog.json` con parche Data Dragon, fecha de importacion, locale y nombres localizados de skins para el front.
- Se regenero `outputs/splash-viewer.html` con badge visible de parche/importacion.
- Se corrigio el updater para saltar variantes `parentSkin` por defecto sin excluir skins base que tienen chromas.
- Se agrego alias de CDN para `Fiddlesticks` -> `FiddleSticks`, resolviendo los 3 splash faltantes del parche.
- Se elimino el duplicado legacy `Shyvana_Ironscale_Shyvana.jpg`; el asset canonico actual es `Shyvana_Shyvana_Ironscale.jpg`.
- Se verificaron skins recientes como `Annie Pandemonium` y `Vayne Maleficio Demoníaco`.
- Se auditaron filtros y ordenamientos del front: busqueda ahora cubre campeones y skins en `es_MX`/`en_US` sin depender de acentos, familias filtra sobre nombres localizados e ingleses, el modal usa la misma lista filtrada que la grilla, el orden default usa `skinNum` y el shuffle deterministico ya no genera indices negativos.

### Archivos modificados clave
- `scripts/update_ddragon_assets.py` - nuevo actualizador canonico de assets Data Dragon.
- `src/riot_lol_cli/settings.py` - default Data Dragon `16.9.1`.
- `assets/items/`, `assets/data_id_imagen/items_ddragon.csv`, `assets/splash_arts/` - assets actualizados.
- `data/ddragon-splash-catalog.json`, `data/splash-manifest.json`, `outputs/splash-viewer.html` - derivados regenerados.

---

## [2026-05-02] Limpieza y unificacion de Markdown

### Que se hizo
- Se consolidaron las reglas de agentes en cuatro documentos canonicos dentro de `.agent/rules/`.
- `CLAUDE.md` quedo como shim corto y `AGENTS.md` sigue como entrypoint raiz para agentes.
- ADC Tracker se absorbio dentro de `docs/meta_analyzer/README.md` y se elimino su carpeta documental separada.
- Los reportes de seguridad y auditoria de datos se absorbieron en `.agent/rules/security-and-testing.md` y `docs/draft_advisor/README.md`.
- KB NotebookLM se redujo a un unico `KB/notebooklm/sintesis/README.md`; las notas sueltas de fuentes y jungla se integraron en `KB/README.md`.
- Junglas Pro consolido sus docs operativas en `projects/active/junglas-pro/research-notes.md`.
- El handoff visual para Claude Design quedo unificado en `claude-design-handoff/README.md`.
- Se elimino la copia paralela de docs historicas; ese material quedo absorbido en bitacora y luego en `projects/legacy/`.

### Archivos modificados clave
- `.agent/rules/*.md` - nueva taxonomia de reglas para agentes.
- `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/README.md`, `projects/README.md` - indices alineados a la estructura reducida.
- `docs/meta_analyzer/README.md`, `docs/draft_advisor/README.md` - absorcion de docs tecnicas redundantes.
- `KB/README.md`, `KB/notebooklm/sintesis/README.md` - KB consolidada sin notas sueltas redundantes.
- `projects/active/junglas-pro/research-notes.md` y `claude-design-handoff/README.md` - proyectos standalone con docs atomizadas.

---

## [2026-05-02] Scripts bat — levantamiento de frontends

### Que se hizo
- Se creo `scripts/bat/draft_advisor.bat`: launcher individual para el Draft Advisor (puerto 8001), siguiendo el mismo patron que `meta_scraper.bat` (verifica venv, setea PYTHONPATH, imprime URLs).
- Se creo `scripts/bat/levantar_todo.bat`: bat maestro idempotente que levanta los 3 servidores Python (Draft Advisor :8001, Meta Scraper :8002, Meta Analyzer :8000) en ventanas CMD minimizadas con titulo, y abre los 4 frontends en el navegador por defecto. Antes de arrancar cada servidor verifica si el puerto ya esta ocupado con `netstat` y lo omite si esta corriendo — permite correrlo varias veces sin duplicar procesos.
- Frontends cubiertos por el bat maestro:
  - `http://localhost:8001/draft` — Draft Advisor SPA
  - `http://localhost:8002` — Meta Scraper dashboard
  - `outputs/splash-viewer.html` — galeria de splash arts (HTML estatico)
  - `projects/active/junglas-pro/index.html` — Junglas Pro viewer (HTML estatico)

### Archivos nuevos / modificados
- `scripts/bat/draft_advisor.bat` — launcher standalone Draft Advisor; corre el proceso oculto y redirige stdout/stderr a `logs/draft_advisor.log` y `logs/draft_advisor.err`
- `scripts/bat/levantar_todo.bat` — bat maestro idempotente; lanza los 3 servidores como procesos ocultos (sin ventanas CMD) via PowerShell `Start-Process -WindowStyle Hidden -RedirectStandardOutput/Error`, luego abre los 4 frontends en el navegador
- `logs/` — directorio creado en tiempo de ejecucion para los logs de cada servidor

---

## [2026-05-02] Traduccion completa al español — Draft Advisor (scoring + perfiles ADC/Support)

### Que se hizo
- Se tradujeron al español rioplatense las 6 funciones generadoras de texto del modo ADC en `scoring.py`: `_generate_strengths()`, `_generate_risks()`, `_generate_play_pattern()`, `_generate_one_liner()`, `_compare_advantages()`, `_compare_disadvantages()`. El modo Support ya estaba en español.
- Se reescribieron todos los campos de texto usuario-visible de los 24 perfiles ADC en `adc_profiles.json`: `strengths`, `weaknesses`, `draft_notes`, `power_spikes`.
- Se tradujeron 20 de los 34 perfiles Support en `support_profiles.json` que estaban en inglés: Leona, Nautilus, Thresh, Pyke, Lulu, Janna, Soraka, Milio, Lux, Karma, Yuumi, Renata, Zyra, Brand (sup), Xerath, Vel'Koz, Swain, Senna, Bard, Sona. Los 14 restantes ya estaban en español.
- Todos los `patch` actualizados a "16.9" y `last_updated` a "2026-05-02".
- El servidor Draft Advisor requiere reinicio para aplicar los cambios (usa módulos en memoria).

### Archivos modificados clave
- `src/riot_lol_cli/draft_advisor/scoring.py` — 6 funciones ADC: strings de fortalezas, riesgos, patron de juego, one-liner, ventajas/desventajas comparativas
- `data/draft_advisor/adc_profiles.json` — 24 perfiles ADC completamente traducidos
- `data/draft_advisor/support_profiles.json` — 20 perfiles Support traducidos de inglés a español

---

## [2026-05-02] Brand ADC — perfil curado + meta integrado desde snapshot

### Que se hizo
- Se agrego el perfil ADC de Brand a `adc_profiles.json` (patch 16.9). Brand es un mago AP jugado en bot lane, actualmente tier S con 54%+ WR en las 3 fuentes. Perfil: anti_tank=10, synergy_engage_support=10, execution_difficulty=7, solo_queue_stability=5.
- Se agrego `"Bot"` al `off_roles` de Brand en `champion_base.json` para que aparezca en el filtro de rol del picker del Draft Advisor.
- Se disparo un scraping ADC fresco que confirmo Brand en el snapshot con WR=54.19%, climb_score=81.02, tier S (fuentes: OP.GG, LoLalytics, U.GG).
- El motor de scoring aplica automaticamente el meta bonus maximo (+12) a Brand en `solo_queue_reliability` via `_score_adc_climb_meta_bonus()`.
- Resultado verificado: Brand aparece como alternativa #1 en drafts con soporte engage (Leona/Nautilus) y enemigos tankudos.

### Archivos modificados clave
- `data/draft_advisor/adc_profiles.json` - nuevo perfil Brand ADC, patch actualizado a 16.9
- `data/draft_advisor/champion_base.json` - off_roles Brand: agregado "Bot"

---

## [2026-05-01] Meta Scraper multi-fuente + integración Support en Draft Advisor

### Que se hizo
- Se agrego el adapter `ugg.py` para U.GG (tabla React `.rt-tr`/`.rt-td`, links `/lol/champions/{slug}/build/`).
- Se corrigio el adapter `lolalytics.py` para ADC: la extraccion de stats pasó a basarse en indices de celda fijos (WR=child[5], PR=child[6], BR=child[7]) en lugar de buscar `%` en el texto libre, que no funcionaba para el endpoint bot lane.
- El Meta Scraper ahora opera con 3 fuentes simultaneas (OP.GG, LoLalytics, U.GG) para ADC y Support.
- Se agrego la integracion de snapshot de Support al Draft Advisor: `champion_data.py` carga `latest_support_tier.json` de forma opcional; `scoring.py` aplica `_score_support_meta_bonus()` acotado a `[-10, +12]` en `_score_supp_solo_queue()`, paralelo a lo que ya existia para ADC.
- Se extendiò el dashboard del Meta Scraper (puerto 8002): tabs Soporte/ADC, columna Climb Score visible solo en ADC, boton Actualizar que dispara el endpoint correcto segun el tab activo.

### Archivos modificados clave
- `src/riot_lol_cli/meta_scraper/adapters/ugg.py` - nuevo adapter U.GG
- `src/riot_lol_cli/meta_scraper/adapters/lolalytics.py` - fix extraccion ADC por indice de celda
- `src/riot_lol_cli/meta_scraper/server.py` - registro de UggAdapter
- `src/riot_lol_cli/meta_scraper/static/index.html` y `app.js` - tabs rol, climb_score, scrape por rol
- `src/riot_lol_cli/draft_advisor/champion_data.py` - carga opcional de support meta snapshot
- `src/riot_lol_cli/draft_advisor/scoring.py` - `_score_support_meta_bonus()`

## [2026-05-01] Meta Scraper ADC para climb y ajuste del Draft Advisor

### Que se hizo
- Se extendio Meta Scraper para scrapear tier lists de ADC ademas de Support desde los adapters existentes de OP.GG y LoLalytics.
- Se agrego normalizacion por rol y `climb_score` basado en winrate, pickrate y banrate.
- Se agregaron endpoints `GET /api/v1/meta/adc/tier`, `GET /api/v1/meta/adc/champion/{champion_id}` y `POST /api/v1/meta/scrape/adc`.
- El Draft Advisor ahora carga opcionalmente `data/meta_scraper/normalized/latest_adc_tier.json` y usa sus stats como ajuste acotado de `solo_queue_reliability` para recomendaciones ADC.

### Archivos modificados clave
- `src/riot_lol_cli/meta_scraper/` - scraping/normalizacion ADC y endpoints nuevos.
- `src/riot_lol_cli/draft_advisor/champion_data.py` y `scoring.py` - consumo opcional del snapshot ADC.
- `tests/meta_scraper/test_normalizer.py` - cobertura de `climb_score` y merge ADC.
- `AGENTS.md`, `docs/draft_advisor/README.md`, `projects/active/*/README.md` - documentacion sincronizada.

## [2026-04-30] Reorganizacion hibrida por proyecto y absorcion de analysis

### Que se hizo
- Se promovio la investigacion de junglas desde legacy a `projects/active/junglas-pro/` como proyecto activo standalone.
- Se actualizo `projects/README.md` como indice principal por proyecto y se quitaron referencias a Junglas Pro desde legacy.
- Se absorbio la informacion vigente de los reportes de auditoria en `AGENTS.md`, `projects/README.md`, `docs/README.md`, reglas de agentes, KB y esta bitacora.
- Se agrego una nota en KB para definir que conocimiento de jungla puede entrar al Draft Advisor sin copiar la investigacion completa.
- Se elimino la carpeta de auditoria como fuente activa tras distribuir sus decisiones, inventario, testing, CI/linting y dead-code en documentos canonicos.

### Archivos modificados clave
- `projects/active/junglas-pro/README.md` - manifiesto del proyecto activo de junglas.
- `projects/README.md` - mapa operacional hibrido y resumen historico.
- `AGENTS.md`, `README.md`, `docs/README.md` - indices actualizados sin carpeta de auditoria separada.
- Reglas de testing/coding - absorcion de notas de CI, Ruff y dead code.
- KB - politica de absorcion estrategica desde Junglas Pro.

## [2026-04-30] Organizacion del repo por proyectos y limpieza documental

### Que se hizo
- Se agrego `projects/` como mapa operativo por proyectos activos y legacy.
- Se crearon manifiestos para CLI Match History, Splash Gallery, Meta Analyzer + Dashboard, Draft Advisor, Meta Scraper y assets/datos Riot.
- Se movieron proyectos no runtime a `projects/legacy/`: copia antigua `riot-lol-cli`, investigacion de junglas profesionales, scraper de items/Data Dragon, screenshots ADC y proyectos de notas de parche.
- Se agruparon scripts manuales sueltos en `projects/dev-scratch/` y se elimino el directorio `scratch/` vacio.
- Se alinearon `README.md`, `AGENTS.md`, `docs/README.md`, reglas de agentes y reportes de auditoria con la nueva estructura.
- Se reemplazo `scripts/bat/ROADMAP_DOCUMENTACION.sh` por un roadmap breve apuntando a docs canonicas actuales.
- Se fusionaron `REORGANIZATION_LOG.md` y `REORGANIZATION_REPORT.md` en un historial de reorganizacion luego absorbido por docs canonicas.

### Archivos modificados clave
- `projects/README.md` y `projects/active/*/README.md` - mapa por proyectos.
- `projects/legacy/` - proyectos historicos agrupados.
- `AGENTS.md` - mapa maestro actualizado con la organizacion por proyectos.
- Reglas de agentes - regla explicita de revisar `AGENTS.md`, `projects/README.md` y `docs/README.md`.
- `README.md`, `CLAUDE.md`, `docs/README.md` y reportes de auditoria previos - documentacion alineada.

---

## [2026-04-30] Actualizacion exhaustiva de AGENTS.md como mapa maestro

### Que se hizo
- Se reescribio `AGENTS.md` raiz como documento canonico para agentes: arquitectura, subsistemas, flujos runtime, datos, APIs, tests, docs vivas, gotchas y deuda conocida.
- Se documento el estado real del working tree, incluyendo `meta_api`, `meta_scraper`, `rendering.py`, `splash.py`, la copia legacy ahora ubicada en `projects/legacy/riot-lol-cli/` y el drift actual de datos.

### Archivos modificados clave
- `AGENTS.md` — pasa a ser el mapa maestro exhaustivo del repositorio para agentes IA.
- `bitacora_de_cambios.md` — registra esta iteracion documental segun el protocolo antidraft.

---

## [2026-04-30] Consolidacion de Markdown activos en docs/

### Que se hizo
- Se fusionaron los documentos redundantes de dashboard, Meta Analyzer y ADC Tracker en READMEs canonicos por subsistema.
- Se actualizo `docs/README.md` para apuntar a la nueva estructura documental activa.
- Los documentos originales completos se preservaron temporalmente en archivo historico para no perder detalle.

### Archivos modificados clave
- `docs/dashboard/README.md` — guia canonica del dashboard.
- `docs/meta_analyzer/README.md` — guia canonica del Meta Analyzer.
- ADC Tracker - guia canonica inicial, luego absorbida en Meta Analyzer.
- `docs/README.md` — indice actualizado de documentacion activa.

---

## [2026-04-28 — sesión 2] Meta Scraper — Subsistema de extracción de datos de meta de soporte

### Motivación

Los `support_profiles.json` están basados en curación manual experta, pero los datos quedan desactualizados con cada parche. Este subsistema automatiza la recolección de winrates, pickrates, banrates y tier lists desde plataformas de estadísticas externas (LoLalytics, OP.GG).

### Nuevo subsistema: `meta_scraper` (puerto 8002)

**Arquitectura de 3 capas:**
1. **Capa 1 (XHR):** intercepción de APIs internas JSON — la más limpia y rápida
2. **Capa 2 (HTML parsing):** parsing de HTML server-side con BeautifulSoup
3. **Capa 3 (Playwright):** browser headless con stealth para sitios con anti-bot agresivo

**Archivos nuevos:**
- `src/riot_lol_cli/meta_scraper/__init__.py` — módulo raíz
- `src/riot_lol_cli/meta_scraper/server.py` — FastAPI en :8002 (7 endpoints + frontend)
- `src/riot_lol_cli/meta_scraper/orchestrator.py` — orquestador con retry y rate-limiting
- `src/riot_lol_cli/meta_scraper/normalizer.py` — merge multi-plataforma + tier calculation
- `src/riot_lol_cli/meta_scraper/adapters/base.py` — BaseAdapter con User-Agent rotation + humanized delays
- `src/riot_lol_cli/meta_scraper/adapters/lolalytics.py` — Playwright para LoLalytics (SPA, necesita JS)
- `src/riot_lol_cli/meta_scraper/adapters/opgg.py` — Playwright para OP.GG (403 a HTTP directo)
- `src/riot_lol_cli/meta_scraper/static/index.html` — dashboard midnight navy con tier list
- `src/riot_lol_cli/meta_scraper/static/styles.css` — score bars, tier badges, glassmorphism
- `src/riot_lol_cli/meta_scraper/static/app.js` — renderizado + filtros + scraping trigger

**Datos:**
- `data/meta_scraper/` — JSON timestamped organizado por plataforma (raw/) y normalizado (normalized/)
- `data/meta_scraper/manifest.json` — índice de snapshots

**Decisiones de diseño:**
- JSON con timestamp como "BD momentánea" (no SQL) — decisión del usuario
- Design system reutilizado del Draft Advisor (tokens.css, compat-spa.css)
- Ambas plataformas requieren Playwright porque no ofrecen API pública y bloquean httpx directo

### Tests
- **11 tests nuevos** en `tests/meta_scraper/test_normalizer.py` (tier calc, name normalization, merge), 11/11 passing

### Documentación
- `AGENTS.md` actualizado con nuevo subsistema, puerto 8002, entry point
- `docs/getting-started.md` actualizado con sección Meta Scraper

---

## [2026-04-28] Definición de SSoT para Scraping de Datos

### Qué se hizo
- **Migración y Extensión:** Se restauró el archivo en cuarentena y se integró a la base de conocimiento.
- Se amplió la lista original (U.GG, OP.GG, LoLalytics, Blitz.gg, Mobalytics, Probuilds.net, METAsrc) incorporando 4 nuevas fuentes de alto nivel.
- **Nuevas fuentes agregadas:** Onetricks.gg (datos OTP), LeagueOfGraphs (macro estadísticas), Gol.gg (Pro Play), y DeepLoL.gg (análisis de impacto temprano).
- Se definió este documento como *Single Source of Truth* (SSoT) para guiar la construcción de los futuros adaptadores de scraping.

### Archivos clave
- **[NUEVO]** Nota SSoT para extracción de datos en KB, luego absorbida en `KB/README.md`.
- **[ELIMINADO]** Archivo legacy de referencias de paginas tras su migración.

---

## [2026-04-27 — sesión 3b] D6-D9: item_path, Crash & Move, jungler classification, queue hints

### D6: item_path en support_profiles
- **[NUEVO]** `ItemPath` model en `schemas.py` (evolution, core_items, situational_items, boots, first_back)
- Inyectado `item_path` a los **27 soportes** basado en la economía asimétrica (KB síntesis 06)
- 5 evoluciones mapped: Bloodsong (AD), Solstice Sleigh (engage tank), Celestial Opposition (warden), Zaz'Zak's (mage), Dream Maker (enchanter)

### D7: Crash & Move en play_pattern_template
- **4 roamers** (Pyke, Bard, Thresh, Rakan): templates enriquecidos con Crash & Move + 3 Chequeos
- **4 anchored** (Soraka, Yuumi, Milio, Sona): templates con B-Prox alta + "Crash & Move NO aplica"
- Fuente: KB/notebooklm/sintesis/07 y 08

### D8: Jungler archetype classification
- **[NUEVO]** `jungler_archetypes.json` con 4 arquetipos: engage, farm_scaling, early_gank, control
- **[NUEVO]** `classify_jungler_archetype()` + `get_jungler_scoring_modifier()` en champion_data.py
- **Wiring**: `_score_supp_ally_synergy()` ahora usa clasificación explícita (JSON) con fallback a heurística por tags
- Scoring modifiers: engage_jg → boost enchanter/poke, farm_jg → boost engage/catcher

### D9: queue_style_hints
- **[NUEVO]** `queue_style_hints.json` con 4 colas: ranked_solo, ranked_flex, clash, normal
- **Weight adjustments**: se aplican en `_compute_weights()` (ej: clash → ally_synergy +5%, blind_pick -5%)
- **Archetype boosts**: flat bonus en raw scores (ej: clash engage +4pts, normal enchanter +2pts)
- Fuente: KB/notebooklm/sintesis/09 (meta regional LCK/LPL)

### Tests
- 51 → **66 tests** (+15 nuevos: 4 D6 + 3 D7 + 5 D8 + 3 D9), 0 regresiones

---


## [2026-04-27 — sesión 3] Auditoría profunda KB → Código (12 drift issues)

### Fuentes auditadas
- 8 archivos markdown KB, 2 PDFs (via 9 síntesis NotebookLM), 1 infografía, 1 guía de estudio

### Drift Issues Resueltos

| # | Issue | Fix |
|---|-------|-----|
| D1 | Tabla sinergias 10×15 no alimentaba el motor | **[NUEVO]** `synergy_matrix.json` + `get_synergy_score()` + integrado en scoring |
| D2 | Sona mencionada en SUPPORT_THEORY pero sin perfil | **[NUEVO]** perfil Sona en `support_profiles.json` (27 totales) |
| D3 | `engage.loses_to` no incluía warden | **FIX** `strategic_triangle.json` v1.2 — bidireccionalidad completa |
| D4 | `arquetipos-de-soporte.md` no mencionaba Warden | **FIX** reescritura completa con §5 Warden + tabla 5 arquetipos |
| D5 | 50 matchups lane individuales no codificados | **FIX** `matchup_rules.json` poblado con matchups + scoring numérico |
| D10 | `enchanter_pure.beats: []` (debería beat engage) | **FIX** ahora `beats: ["engage"]` per SUPPORT_THEORY §4 |
| D11 | `filosofia-de-pickeo.md` decía 5 factores (eran 6) | **FIX** actualizada tabla a 6 factores con pesos v1.1 |

### Archivos nuevos
- `data/draft_advisor/kb/structured/synergy_matrix.json` — 26 soportes × 15+ ADCs cuantitativo

### Archivos modificados
- `strategic_triangle.json` v1.1→v1.2: +Bard a catcher, +Senna a enchanter_pure, bidireccionalidad
- `matchup_rules.json` v1.0→v1.2: +50 matchups lane individuales, bullies/scalers
- `support_profiles.json`: +Sona (27 total)
- `champion_data.py`: +loaders synergy_matrix + matchup_rules, +4 accessors
- `scoring.py`: synergy_matrix integrada en `_score_supp_ally_synergy()`, lane matchups en `_score_supp_enemy_matchup()`
- `KB/arquetipos-de-soporte.md`: +§5 Warden, subdivisions enchanter
- `KB/filosofia-de-pickeo.md`: tabla 5→6 factores

### Tests
- 36 → **49 tests** (+13 nuevos, 0 regresión)

---

## [2026-04-27 — sesión 2b] Phase 3: 26 soportes + endpoint triángulo + ajuste de pesos

### Cambios

**`data/draft_advisor/support_profiles.json`** (Phase 1 → Phase 3):
- 9 perfiles nuevos: Yuumi, Renata, Zyra, Brand, Xerath, Vel'Koz, Swain, Senna, Bard
- Total: **26 soportes** (Engage 4, Enchanter 8, Poke/Mage 6, Warden 2, Catcher 6)
- Cada perfil incluye: 21 stats numéricas, sinergias ADC, counter-matchups, play_pattern_template en español

**`data/draft_advisor/scoring_weights.json`** (v1.0 → v1.1):
- `ally_synergy`: 0.25 → 0.30 (alineado con KB/filosofia que prioriza sinergia ADC al 30-35%)
- `blind_pick_safety`: 0.10 → 0.05 (compensación; la safety importa menos con información)
- Justificación: la sinergia con el ADC es el factor #1 del soporte (KB doc)

**`src/riot_lol_cli/draft_advisor/api.py`** — 2 endpoints nuevos:
- `GET /api/v1/draft/strategic-triangle/{champion_id}` — inspección del triángulo estratégico
- `GET /api/v1/draft/champions/supports` — roster completo de soportes con fine-grained archetype

### Tests

- **36/36 tests passing** (sin regresión)

---

## [2026-04-27 — sesión 2] Auditoría de drift + expansión triángulo estratégico + comp predominance consumido

### Motivación

Auditoría completa del Draft Advisor post-integración de NotebookLM. Se detectaron 6 issues de drift entre KB, datos estructurados y código. Esta sesión los corrige e implementa funcionalidad nueva.

### Hallazgos de Drift (6 issues)

| # | Drift | Severidad | Estado |
|---|-------|-----------|--------|
| 1 | `comp_predominance.json` cargado en `champion_data.py` pero **nunca consumido** en scoring | Alta | ✅ Corregido |
| 2 | `support_archetypes.json` tiene `engage_hybrid` (Pyke) no mapeado en strategic_triangle | Media | ✅ Pyke ya estaba en `catcher` fine-grained |
| 3 | `matchup_rules.json` vacío (235 bytes, `rules: []`) | Alta | ✅ Poblado con reglas archetype-vs-comp |
| 4 | KB/SUPPORT_THEORY.md define Warden (Braum, Taric, TahmKench) sin entrada en strategic_triangle | Alta | ✅ Añadido archetype `warden` |
| 5 | Tests fallan por `ModuleNotFoundError` (falta PYTHONPATH en pyproject.toml) | Alta | ✅ Añadido `pythonpath = ["src"]` |
| 6 | KB/filosofia pesos (35% ally, 20% enemy, 20% gap, 10% jungle, 15% blind) difieren de scoring_weights.json (25/20/10/20/10/15) | Baja | ℹ️ Documentado como diferencia de diseño |

### Cambios de Código

**`data/draft_advisor/kb/structured/strategic_triangle.json`** (v1.0 → v1.1):
- Nuevo archetype `warden`: `["Braum", "Taric", "TahmKench"]`
- Warden beats: engage, catcher. Loses_to: poke.
- Rakan añadido a `catcher` (faltaba).
- Catcher ahora `loses_to: ["engage", "warden"]` (antes solo engage).

**`data/draft_advisor/kb/structured/matchup_rules.json`** (vacío → poblado):
- `archetype_vs_enemy_comp` con 5 reglas (vs_dive, vs_poke, vs_pick, vs_scaling, vs_tank).
- Warden incluido en `best_archetypes` para dive y pick comps.
- `lane_bullies` y `lane_scalers` clasificados.

**`src/riot_lol_cli/draft_advisor/scoring.py`**:
- `_apply_comp_predominance_bonus()` — nuevo método que consume comp_predominance.json.
- `_teamfight_shape_to_comp_type()` — mapea TeamfightShape a comp type keys.
- `_score_supp_comp_gap_fill()` — ahora llama a `_apply_comp_predominance_bonus()` y reconoce `WARDEN` en frontline check.

**`src/riot_lol_cli/draft_advisor/champion_data.py`**:
- `get_comp_predominance()` — nuevo accessor público para comp_predominance data.

**`pyproject.toml`**:
- `pythonpath = ["src"]` en `[tool.pytest.ini_options]` — fix de PYTHONPATH para tests.

### Tests

- 9 tests nuevos en `test_notebook_kb.py` (warden classification, triangle interactions, comp predominance).
- **36/36 tests passing** (incluido regression suite).

---

## [2026-04-27] KB extendida con material NotebookLM + nuevas reglas de scoring

### Motivación

Dario sumó 4 fuentes pesadas a `KB/notebooklm/` (2 PDFs, 1 infografía, 1 guía de estudio en texto plano) extraídos de NotebookLM. Las fuentes contienen conceptos avanzados que el motor del Draft Advisor no estaba aplicando: el triángulo estratégico fino (Engage > Poke > Sustain con eje invertido Disengage > Engage), sinergias 2v2 con winrate medido, predominancia entre las 5 composiciones canónicas, y vocabulario nuevo (J Prox, B Prox, Crash & Move, Regla de los 3 Chequeos).

### Cambios

**KB humano (markdown):**
- 10 docs nuevos en `KB/notebooklm/sintesis/` (INDEX + 9 ejes temáticos): paradigma del arquitecto, jerarquía de pick order, las 5 composiciones, triángulo Engage/Poke/Sustain, sinergias medidas, economía asimétrica, regla de los 3 chequeos, Crash & Move, meta regional LCK vs LPL.
- `KB/README.md` extendido con sección "Material extendido NotebookLM".

**Datos estructurados (3 JSON nuevos consumidos por el motor):**
- `data/draft_advisor/kb/structured/measured_synergies.json` — 4 sinergias 2v2 con WR medido (Samira+Naut 53.7%, Lucian+Nami 54.0%, Ashe+Sera 54.7%, Jinx+Thresh 54.3%) + 10 heurísticas pro-scene. Confidence dual: `measured` vs `heuristic` con bonus diferenciado.
- `data/draft_advisor/kb/structured/strategic_triangle.json` — Triángulo fine-grained: subdivide enchanter en `enchanter_disengage` (Janna, Lulu, Milio, Renata, Karma) vs `enchanter_pure` (Soraka, Yuumi, Nami). Aplica el eje invertido Disengage > Engage (Wardens invalidan iniciadores).
- `data/draft_advisor/kb/structured/comp_predominance.json` — Ciclo piedra-papel-tijera entre las 5 comps (Attack > Siege > Protect > Catch > Attack > Siege; Split asimétrica).

**Lógica del motor (scoring.py):**
- `_score_measured_synergy(adc_id, supp_id)` — busca pareja en JSON, devuelve bonus interpolado por WR (cada 1pp sobre 50% = +3 score, hasta 15pts).
- `_apply_strategic_triangle(my_archetype, enemy_supp_archetype)` — devuelve +10 si counterea, -8 si es counter-pickeable.
- Integración en `_recommend_support()` como bonificadores aditivos al `enemy_matchup` y `ally_synergy`.

### Archivos modificados clave
- `KB/README.md` — sección "Material extendido NotebookLM"
- `src/riot_lol_cli/draft_advisor/scoring.py` — 2 funciones nuevas + integración en pipeline de scoring
- `src/riot_lol_cli/draft_advisor/champion_data.py` — loaders de los 3 JSON nuevos
- `docs/draft_advisor/README.md` — sección "Reglas de scoring (sinergias medidas + triángulo)"

---

## [2026-04-26] UI Redesign — Draft Advisor SPA (dark navy, WCAG AA, i18n parcial)

### Motivación

La UI tenía fondos grises demasiado claros, barras de score de 6px ilegibles, tarjetas de alternativas con layout roto (texto desbordando columnas de 2-col), y términos de UI en inglés (MEDIUM, LOW, HIGH) mezclados con la interfaz en español.

### Cambios

- **`compat-spa.css`**: paleta midnight navy (`--bg-primary: #04080f`, `--bg-card: #091520`), bordes más visibles, texto secundario más contrastado para WCAG AA.
- **`styles.css`**: barras de score `6px → 10px`, labels `130px → 182px`, valores en Outfit Bold. Alt cards rediseñadas con `.alt-info` + `.alt-score-number` + `.alt-compare` vertical. Nuevas clases `.comp-badge`. Reduced-motion explícito.
- **`app.js`**: `threatLevelEs()` y `confidenceEs()` traducen nivel de amenaza y confianza a español. `scoreBarGradient()` colorea barras dinámicamente. `renderAlternatives()` con nuevo HTML. `renderDraftSummary()` con `.comp-badge` en lugar de estilos inline.
- **Accesibilidad**: `aria-label` en `.modal-close` y `.remove-btn`. Desktop-first documentado en `CLAUDE.md`.

### Archivos modificados
- `src/riot_lol_cli/draft_advisor/static/design-system/compat-spa.css`
- `src/riot_lol_cli/draft_advisor/static/styles.css`
- `src/riot_lol_cli/draft_advisor/static/app.js`
- `src/riot_lol_cli/draft_advisor/static/index.html`
- `CLAUDE.md`

---

## [2026-04-26] Design System Unificado + Support Advisor MVP

### Support Advisor (target_role: ADC | SUPPORT)

Se extendió el Draft Advisor para recomendar **Soportes** además de ADCs, sin clonar el módulo. Cambios:

- **`schemas.py`**: `AdvisorMode` enum, `SupportProfile` model, `SupportArchetype` enum, `target_role` en `DraftState`.
- **`champion_data.py`**: carga de `support_profiles.json`, helpers `get_support_ids()`, `get_support_profile()`.
- **`scoring.py`**: refactor `recommend()` enruta por `target_role`. Nuevo `_recommend_support()` con 6 factores de scoring (ally_synergy 35%, enemy_matchup 20%, comp_gap_fill 20%, scaling_fit 15%, solo_queue 10%).
- **`api.py`**: endpoint `GET /api/v1/draft/champions/supports`.
- **Data**: `data/draft_advisor/support_profiles.json` (10 soportes core), `data/draft_advisor/kb/structured/support_archetypes.json`; el antiguo `data/supports_list.json` fue absorbido y eliminado en la limpieza 2026-05-07.
- **KB/**: 6 documentos de base de conocimiento estratégico (filosofía, arquetipos, sinergias, matchups, game plans, amenazas).
- **Frontend**: `state.targetRole`, select de Rol Objetivo, payload incluye `target_role`.

**Soportes fase 1:** Leona, Nautilus, Thresh, Lulu, Janna, Soraka, Milio, Lux, Pyke, Karma.
**Fase 2 pendiente:** 14 soportes adicionales (Blitzcrank, Rakan, Rell, Alistar, Nami, Yuumi, Renata, Zyra, Brand, Xerath, Vel'Koz, Swain, Senna, Bard).

### Design System — Migración completa de tokens CSS

Se unificó la paleta de tokens de las 4 surfaces (Draft Advisor SPA, Match History, Splash Viewer, Dashboard) bajo un sistema canónico.

**Archivos nuevos en `static/design-system/`:**
- `tokens.css` — 169 líneas, tokens canónicos `--arc-*`, `--forge-*`, `--state-*`
- `components.css` — 506 líneas, clases `.btn`, `.card`, `.pill`, `.score-bar`
- `compat-spa.css` — aliases legacy para el SPA (tokens con valores distintos al canónico)
- `compat-dashboard.css` — aliases legacy para el Dashboard (referencia)

**Migración por surface:**
- Splash Viewer: `--hextech-* → --arc-*`, `--piltover-* → --forge-*`, 16 familias
- Match History: ídem + `--victory/--defeat → --state-success/--state-error`, 18 familias
- SPA (styles.css + app.js): 7 familias migradas, NO MIGRAR tokens quedan via compat-spa
- Dashboard (f-string Python): `--accent/--secondary/--dark/--danger` renombrados

**Componentes adoptados en el SPA:**
- `.btn .btn-primary` en "Recomendar Pick"
- `.btn .btn-ghost` en role-filters del modal y modal-close
- `.pill .pill-gold` en patch-badge

**Pool de Campeones comentado** en `index.html` como upgrade futuro (backend ya implementado).

**Documentación generada:**
- `docs/design-system.md` — referencia completa del sistema de tokens y componentes
- `docs/draft_advisor/README.md` — actualizado con Support Advisor, endpoints, flujo
- `docs/getting-started.md` — sección Draft Advisor actualizada con flujo de uso real

---

## [2026-04-24] Modernización Arquitectónica y Estabilización

Hemos completado exitosamente las tareas de estabilización y modernización descritas en el plan post-refactorización. El repositorio ha pasado de ser un conjunto de scripts con algunas inconsistencias a un paquete moderno y escalable.

### 1. Limpieza de Linting (Ruff)
Se corrigieron todos los errores residuales reportados por `ruff`:
- Importaciones rotas de tipado (`DraftState`, `RecommendationOutput`) resueltas usando `TYPE_CHECKING` guards para evitar dependencias circulares.
- Variables muertas eliminadas en los scripts de descarga de splash arts.
- Solucionado el manejo de excepciones genéricas (`bare except`) en el validador de frescura de datos.

Además, se **amplió la configuración de Ruff** en `pyproject.toml` agregando reglas más estrictas (`I` para ordenamiento automático de imports y `UP` para modernización de sintaxis antigua como `typing.Dict`). Todo el código fue auto-formateado bajo este nuevo estándar.

### 2. API Client Modernizado (`httpx`)
El cliente original `api.py` fue ampliado con una versión asíncrona robusta.
- Se agregó la clase `AsyncRiotClient` que usa `httpx.AsyncClient`.
- Implementa **backoff exponencial real asíncrono** usando `asyncio.sleep()` en lugar de bloquear el thread cuando Riot responde con `429 Rate Limit`.
- El cliente original síncrono fue conservado por compatibilidad estricta con la CLI, pero su manejo de rate-limits fue pulido bajo el mismo estándar.
- Se agregaron tests asíncronos con mocks completos usando `pytest-asyncio`.

### 3. Schemas Estrictos (Pydantic V2)
El corazón de la recolección de datos era frágil por usar diccionarios anidados. 
- Se crearon modelos Pydantic V2 en `src/riot_lol_cli/schemas/riot_api.py` para parsear fuertemente el payload de `Match-V5`.
- Incluyen `extra="allow"` como blindaje: si Riot Games añade campos nuevos el día de mañana a las partidas, el parser no se romperá en producción.
- El `MetaDataCollector` (tanto en su versión file como db) ahora instancia estos objetos y usa factorías para destilar los stats de forma tipada, logrando evitar `KeyErrors` accidentales si un stat no viene.

### 4. Transición a Logging Estándar
Todos los módulos que corren como servidores o jobs de fondo (`api_server.py`, `server.py` del Draft, `data_collector_db.py`, `tier_generator.py`) pasaron de usar `print()` a utilizar `logging` estándar de Python.
- Los logs ahora tienen niveles reales (`INFO`, `WARNING`, `ERROR`).
- Módulos CLI interactivos (como los comandos `click`) mantienen su output limpio.

### 5. Testing y Cobertura (`pytest-cov`)
- Se incluyó `pytest-cov` a las herramientas de desarrollo.
- Se escribieron pruebas para los nuevos modelos de Pydantic y el cliente asíncrono.
- La ejecución de `pytest` indica que **todos los tests pasan** y la **cobertura del código en `src/` subió a >50%**.
- Hemos integrado este reporte a la nueva base de GitHub Actions (`ci.yml`) que ahora fallará si la cobertura baja de 30%.
