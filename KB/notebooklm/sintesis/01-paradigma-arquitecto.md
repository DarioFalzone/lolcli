# 01 — El paradigma del arquitecto

> **Fuente:** `Support_Architecture_Dossier.pdf` p2, p13 + `Nación_Digital_LoL.pdf` p4

## Tesis central

> *"Dominar el rol de soporte no es asistir al equipo; es dictar las condiciones bajo las cuales el juego puede ser jugado."*
> — Support Architecture Dossier, p13

El soporte moderno no es un acompañante. Es el **arquitecto del ritmo del juego**, ejerciendo poder sobre tres ejes:

1. **Control estructural (Drafting)** — único rol con flexibilidad para habilitar win conditions (Protección, Enganche, Asedio) sin comprometer las solo lanes.
2. **Control numérico (Economía)** — opera con el menor presupuesto pero abusa de objetos con eficiencias >100% para multiplicar el DPS aliado.
3. **Control geográfico (Macro)** — gestor de la ventaja informativa. Domina el tempo, los rebotes de oleadas y la jungle proximity.

## Métricas de proximidad (vocabulario nuevo)

Las fuentes introducen 4 métricas que aún no estaban en la KB del proyecto:

| Métrica | Definición | Lo que mide |
|---------|------------|-------------|
| **B Prox** (Bot Proximity) | % de tiempo a <2000u del Tirador | Protección directa al carry, estabilidad de línea |
| **J Prox** (Jungle Proximity) | % de tiempo a <2000u del Jungla | Capacidad de invadir, asegurar objetivos tempranos |
| **S Prox / Team Prox** | Capacidad de rotación a otras líneas y agrupamiento para escaramuzas | Macro post-laning |
| **Vision Diff** | Diferencia de visión entre equipos | Ventaja informativa, control de tempo |

**Hallazgo clave (Dossier p2, "Nota Táctica"):** *Los soportes de LCK/LPL mantienen una J Prox desproporcionadamente alta en los primeros 10 minutos.* Esto convierte al soporte en **un segundo jungla**.

## Implicancia para el motor de scoring

Esta sección **respalda** los pesos asimétricos del motor actual:
- `ally_synergy` 35% → refleja que el supp es co-driver del jungler/ADC
- `comp_gap_fill` 20% → refleja que el supp llena huecos estructurales (frontline, engage, peel, poke)
- `enemy_matchup` 20% → el supp es responsable principal de neutralizar amenazas

Lo que el motor NO captura todavía y debería:
- **J Prox boost** cuando el jungler aliado es de farm-style (Karthus, Master Yi) → un supp con mobility/initiation cubre la falta de presión jungle
- **B Prox boost** cuando el ADC aliado es scaling-frágil (Jinx, KogMaw) → un supp con peel multiplica la supervivencia

Estas heurísticas se materializan en:
- `scoring.py::_score_jungle_synergy()` (existente, refinable con J Prox)
- `scoring.py::_score_adc_synergy()` (existente, refinable con B Prox)

## Veredicto del Dossier (p13)

> Los 3 ejes del soporte forman el "código fuente" del rol:
> 1. **Control Estructural (Drafting)** — habilita win conditions
> 2. **Control Numérico (Economía)** — eficiencias >200%
> 3. **Control Geográfico (Macro)** — domina tempo y proximidad
