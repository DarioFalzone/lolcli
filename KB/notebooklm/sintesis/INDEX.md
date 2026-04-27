# Síntesis NotebookLM — Knowledge Base extendida del Draft Advisor

> **Fuentes procesadas (2026-04-27):**
> - `KB/notebooklm/Support_Architecture_Dossier.pdf` — 13 páginas, "El Dossier del Analista: Arquitectura del Rol de Soporte"
> - `KB/notebooklm/Nación_Digital_LoL.pdf` — 12 páginas, "Análisis Sistémico y Sociocultural"
> - `KB/notebooklm/imagen guia de estrategia de seleccion y macrogame.png` — infografía maestra
> - `KB/notebooklm/guia de estudio estrategia de soporte` — guía de estudio + glosario

Esta síntesis destila los hallazgos de las fuentes en **conocimiento procesable** por el motor de scoring del Draft Advisor. Cada archivo cubre un eje específico y referencia las páginas de origen.

## Índice

| # | Documento | Eje | Aplicación en el motor |
|---|-----------|-----|------------------------|
| 01 | [Paradigma del arquitecto](01-paradigma-arquitecto.md) | Macrogame > Microgame | Justifica el peso de `ally_synergy` (35%) y `comp_gap_fill` (20%) |
| 02 | [Jerarquía de Pick Order](02-jerarquia-pick-order.md) | Drafting | Refina el factor `pick_position` (blind/early/late) |
| 03 | [Las 5 composiciones fundamentales](03-cinco-composiciones.md) | Meta-comps | Extiende `comp_archetypes.json` con predominancia |
| 04 | [Triángulo Engage > Poke > Sustain](04-triangulo-engage-poke-sustain.md) | Counter-pick táctico | **Nueva regla de scoring** — boost cuando el supp counterea al arquetipo enemigo |
| 05 | [Sinergias medidas con WR](05-sinergias-medidas.md) | Parejas ADC+Supp | **Nueva fuente de boost** — `measured_synergies.json` |
| 06 | [Economía asimétrica](06-economia-asimetrica.md) | Itemización | Informa `play_pattern_template` (item path) |
| 07 | [Regla de los 3 Chequeos](07-roaming-3-chequeos.md) | Macro post-laning | Material para `coaching/03-roaming-mastery.md` |
| 08 | [Ecosistema Crash & Move](08-crash-and-move.md) | Wave management | Material para `coaching/04-laning-fundamentals.md` |
| 09 | [Meta regional LCK vs LPL](09-meta-regional-lck-lpl.md) | Estilo regional | Sugerencia de estilo según `queue_type` |

## Resumen ejecutivo (TL;DR)

1. **El soporte es arquitecto, no asistente.** Domina drafting (control estructural), economía (control numérico) y macro (control geográfico). Su poder en el motor justifica los pesos asimétricos en favor de `ally_synergy` y `comp_gap_fill`.
2. **El triángulo es la regla más poderosa**: Engage > Poke, Poke > Sustain, Sustain > Engage. Eje invertido: **Disengage > Engage** (Wardens invalidan iniciadores). El motor debe boostear cuando el supp counterea al arquetipo enemigo.
3. **Las sinergias medidas son data, no opinión**: Samira+Nautilus 53.7% WR, Lucian+Nami 54.0%, Ashe+Seraphine 54.7%, Jinx+Thresh 54.3%. Estas parejas ganan score independiente de la heurística.
4. **El R5 (último pick rojo) es el activo más valioso del draft**. Si el target_role es support y la posición es `late`, el motor debe priorizar counter-pick específico.
5. **Las composiciones tienen predominancia tipo piedra-papel-tijera**: Attack > Siege, Siege > Protect, Protect > Catch, Catch > Attack. El motor puede usar esto cuando detecta el arquetipo enemigo.

## Archivos generados a partir de esta síntesis

**Datos estructurados (consumidos por scoring.py):**
- `data/draft_advisor/kb/structured/measured_synergies.json` — parejas con WR comprobado
- `data/draft_advisor/kb/structured/strategic_triangle.json` — triángulo + eje Disengage>Engage
- `data/draft_advisor/kb/structured/comp_predominance.json` — ciclo Attack > Siege > Protect > Catch

**Cambios en código:**
- `scoring.py` → función `_score_measured_synergy()` y `_apply_strategic_triangle()`
- `champion_data.py` → loader de los 3 nuevos JSON

Ver [`bitacora_de_cambios.md`](../../../bitacora_de_cambios.md) para la entrada del commit.
