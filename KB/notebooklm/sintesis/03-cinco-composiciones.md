# 03 — Las 5 composiciones fundamentales (Metajuego Global)

> **Fuente:** `Support_Architecture_Dossier.pdf` p5 + `imagen guia de estrategia.png` + `Nación_Digital_LoL.pdf` p5

## Las 5 composiciones canónicas

El Dossier formaliza **5 arquetipos de composición** que predominan en alta competición:

| Comp | Nomenclatura PDF | Equivalente en `comp_archetypes.json` | Esencia |
|------|------------------|---------------------------------------|---------|
| **Attack Matrix** | Wombo Combo | (NUEVO) | Iniciación masiva. Multi-target CC para ganar 5v5 instantáneos. |
| **Catch** | Captura | `pick` | Eliminar objetivos desposicionados. Depende de visión asimétrica. |
| **Protect** | Hyper-Carry | `front_to_back` | Maximiza el daño de un carry escalado. |
| **Siege & Poke** | Asedio | `poke_siege` | Desgaste a distancia. Vulnerable al hard engage. |
| **Split Push** | 1-3-1 | `split` | Presión lateral constante. Requiere limpieza de oleadas y disengage. |

> **Nota:** "Attack Matrix" no estaba en `comp_archetypes.json`. Se debe extender ese JSON con esta categoría.

## Ciclo de predominancia (piedra-papel-tijera)

```
        Attack Matrix
       ↗            ↘
    Catch         Protect
       ↑            ↓
    Split          Siege
       ↖            ↙
        (Split Push)
```

**Reglas explícitas (Dossier p5):**

| Si tu equipo es… | Vencés contra… | Sos vulnerable a… |
|------------------|----------------|-------------------|
| **Attack Matrix** | Siege & Poke | Catch |
| **Catch** | Attack Matrix | Protect |
| **Protect** | Catch | Siege & Poke |
| **Siege & Poke** | Protect | Attack Matrix |
| **Split Push** | (asimétrico — depende de limpieza) | Catch en mid-game |

## Implicancia para el motor

Esta es **una nueva fuente de score** que no está en el motor actual:

### Implementación propuesta

```python
def _score_composition_predominance(allied_archetype, enemy_archetype):
    """
    +12 si tu comp vence al arquetipo enemigo
    -8 si sos vulnerable al arquetipo enemigo
    0 si es neutral
    """
    DOMINANCE = {
        "attack_matrix": {"beats": ["poke_siege"], "loses_to": ["pick"]},
        "pick":          {"beats": ["attack_matrix"], "loses_to": ["front_to_back"]},
        "front_to_back": {"beats": ["pick"], "loses_to": ["poke_siege"]},
        "poke_siege":    {"beats": ["front_to_back"], "loses_to": ["attack_matrix"]},
        "split":         {"beats": [], "loses_to": ["pick"]},
    }
    if enemy_archetype in DOMINANCE.get(allied_archetype, {}).get("beats", []):
        return 12
    if enemy_archetype in DOMINANCE.get(allied_archetype, {}).get("loses_to", []):
        return -8
    return 0
```

Este score se aplica al factor `comp_gap_fill` (peso 20%) o como un bonus separado.

## Filosofía: el draft como ingeniería

> *"La construcción de una composición debe verse como **ingeniería**, no como suma de campeones individuales. Cada composición tiene una **win condition específica**."*
> — Support Architecture Dossier, p5

Esto refuerza la lógica del campo `enabled_play_pattern` en `RecommendedPick`: cada recomendación debe explicar cuál es la **condición de victoria** que el supp habilita. No basta con decir "este es el mejor pick"; hay que decir "este pick habilita una comp Attack Matrix que vence al Siege enemigo".

## Cobertura faltante en `comp_archetypes.json`

El JSON existente cubre 5 arquetipos: `front_to_back`, `dive`, `poke_siege`, `pick`, `split`. Pero:

- ❌ Falta **`attack_matrix`** (wombo combo) como categoría independiente del `dive`
- ❌ Faltan las **reglas de predominancia** (qué arquetipo vence a cuál)
- ✅ Las preferencias por ADC y los `weight_adjustments` ya están bien

**Acción:** crear `data/draft_advisor/kb/structured/comp_predominance.json` con las reglas del ciclo, sin tocar el JSON existente para no romper compatibilidad.
