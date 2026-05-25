# Jungle Research - Decisiones (ADRs)

Decisiones globales que afectan a múltiples fases del roadmap. Cada una se
escribe corta y con la recomendación actual; cuando una decisión cambia,
se actualiza la fila (no se borra el histórico).

> Documentos hermanos:
> - [jungle-research-status.md](jungle-research-status.md) — estado actual.
> - [jungle-research-roadmap.md](jungle-research-roadmap.md) — fases futuras.

## ADR-1: Storage final

**Decisión**: JSON con rotación → SQLite cuando se dispare V8 → PostgreSQL
solo si Home Hub se sube a un host compartido.

**Trigger del switch a SQLite**: cuando
`data/meta_analyzer/jungle_research/champion_meta_snapshots/history/` supere
los 500 archivos. Hoy estamos por debajo.

**Por qué no PG ya**: añade dependencia operativa (postgres en local), y los
queries cross-snapshot ("WR promedio en los últimos 30 patches") siguen siendo
ad-hoc. SQLite tiene un orden de magnitud menos fricción y cubre el caso.

## ADR-2: Scraping con Playwright

**Decisión**: permitido, con rate limit estricto y respetando `robots.txt`.

**Reglas duras**:
- `min_delay >= 4s` por adapter (heredado de `BaseAdapter`).
- Respetar `Retry-After` siempre.
- User-Agent identificable cuando aplica (Leaguepedia, etc.).
- Nunca bypass de captcha/login.
- HTML raw como fallback (guardado en bronze/) para debug.

**Por qué**: Meta Scraper ya lo usa para U.GG/LoLalytics. Es la única forma
viable de cubrir SPAs (Mobalytics, Tracker.gg). Sin Playwright, V3.9/V3.10
serían imposibles.

## ADR-3: RIOT_API_KEY

**Decisión**: dev key rotada manualmente por ahora. Aplicar a prod key
permanente cuando V2.5-V2.7 se estabilice.

**Estado actual**: el riot bridge degrada con gap controlado si no hay key
(no rompe). La cadena `pro_accounts → match_history → pro_presence` queda
pendiente sin key.

**Por qué**: prod key tiene proceso de aplicación de Riot (review manual,
tiempo). No vale invertir en eso hasta que el resto del flujo esté probado
con dev key.

## ADR-4: Localización UI

**Decisión**: nombres canónicos (Riot ID, PUUID, jungle, etc.) en inglés;
copy en español rioplatense.

**Por qué**: los nombres canónicos vienen de la doc de Riot/Data Dragon
(intraducibles sin perder precisión). El copy del cockpit es para el
operador (vos), que prefiere español. Sin migración a i18n por ahora.

## ADR-5: Visibilidad desde Home Hub

**Decisión**: el Home Hub (`:8080`) linkea directamente al tab
`#jungle-research` del cockpit.

**Estado**: hecho (verificado al cerrar V1).

## ADR-6: Snapshots inmutables + rotación

**Decisión**: nunca pisar `latest.json`. Antes de cada write, mover el
contenido viejo a `backups/<timestamp>.json` y registrar el merge en
`history/<timestamp>_merged.json`.

**Por qué**: si un scraping introduce datos rotos, hay que poder volver al
estado anterior sin git. Y la historia evolutiva es valor analítico (V8
queries cross-snapshot).

**Implementado en**: `jungle_research/json_storage.py`
(`_write_json_atomic` + helpers de rotación).

## ADR-7: Gap controlado vs error

**Decisión**: si una fuente falla, devolver 200 + `gaps: [reason]`. Nunca
500 al UI.

**Por qué**: el cockpit debe seguir mostrando lo que sí funciona aunque
una fuente esté caída. UX > correctitud HTTP estricta. Los gaps quedan
visibles en sub-vista Fuentes para diagnóstico.

**Aplica también a**: `esports_research` (Codex respetó el patrón).

## ADR-8: Encoding UTF-8 sin BOM

**Decisión**: TODOS los archivos generados (JSON, MD, HTML) deben ser UTF-8
sin BOM.

**Guard**: `tests/test_no_mojibake.py` rompe build si entra mojibake o BOM.

**Trampa conocida**: `PowerShell Set-Content -Encoding UTF8` agrega BOM.
Usar `[System.IO.File]::WriteAllText()` o las helpers de Python
(`_write_json_atomic`).

## ADR-9: Cero datos inventados

**Decisión**: si una fuente no tiene datos para una entidad, devolver el
campo como `null` o omitirlo. Nunca rellenar con valor default que el
operador podría tomar como real.

**Excepción**: scores numéricos del scoring pueden ser 0 cuando no hay
fuente (el operador lo lee como "sin señal" y el `confidence_score` lo
refleja).
