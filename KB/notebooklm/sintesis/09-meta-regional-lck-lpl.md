# 09 — Meta regional: LCK vs LPL

> **Fuente:** `Support_Architecture_Dossier.pdf` p12 + `Nación_Digital_LoL.pdf` p10

## Las dos vías

| Eje | LCK (Vía Coreana) | LPL (Vía China) |
|-----|-------------------|-----------------|
| **Filosofía** | Macro estructural y eficiencia | Agresión incesante, caos controlado |
| **Win condition** | Reducción de errores, control preciso de oleadas, eficiencia de oro | Skirmishes 5v5 continuas, "el que no inicia, pierde" |
| **Arquetipos dominantes** | Wardens, Utility (Renata, Tahm Kench, Bard) | Engage duro (Rell, Alistar, Leona) |
| **Filosofía cultural** | Individualismo Endémico vs Colectivismo Jerárquico (NA/EU vs CN) |
| **Tempo de juego** | Setup → ejecución calculada | Skirmish → snowball → snowball |

## Citas clave

### LCK
> *"Enfoque en reducción de errores, control preciso de oleadas y eficiencia de oro. Arquetipos dominantes: Utility, Wardens, control de mapa."*
> — Dossier p12

### LPL
> *"Enfoque en skirmishes continuas y peleas 5v5. **El que no inicia, pierde.** Arquetipos dominantes: Iniciación pesada, Engage duro."*
> — Dossier p12

## Nota del Analista (texto literal del Dossier p12)

> *"El estilo local define tu draft. Un soporte pasivo en un entorno hiper-agresivo pierde por atrición."*

Esta cita es **operativamente importante** para el motor. Si el contexto del usuario (`queue_type`, `region` implícito) sugiere una región/estilo, el motor debería **priorizar arquetipos compatibles**.

## Diferencia cultural complementaria

> **Fuente complementaria:** `Nación_Digital_LoL.pdf` p10 — "Psicología Regional"

- **NA / EU — Individualismo Endémico**: jugadores como "islas". Roles de alto impacto asumen carrear solos. **Alta fricción por falta de cooperación.** Implicancia: en SoloQ NA/EU, supp con alta `solo_queue_reliability` es más valioso que en LPL.
- **China — Colectivismo Jerárquico**: jungla = autoridad máxima. Carrileros sacrifican ventajas personales para asegurar el dominio del núcleo. **Garantiza retribución colectiva.** Implicancia: en SoloQ KR/CN, los engage supports que coordinan con jungla son más fuertes.

## Implicancia para el motor

### Mapeo `queue_type` → estilo regional implícito

El campo `queue_type` ya existe (`ranked_solo`, `ranked_flex`, `clash`, `normal`). Podemos extender la heurística:

```python
QUEUE_STYLE_HINTS = {
    "ranked_solo": {
        "description": "Estilo individualista (NA/EU/LATAM) — alta fricción, supps con solo_queue_reliability ↑",
        "boost_traits": ["solo_queue_reliability", "self_carry"],
        "preferred_archetypes": ["enchanter", "engage"],  # consistencia
    },
    "ranked_flex": {
        "description": "Equipo coordinado — supps de team utility ↑",
        "boost_traits": ["team_utility", "engage_strength"],
        "preferred_archetypes": ["engage", "catcher", "enchanter_disengage"],
    },
    "clash": {
        "description": "Coordinación máxima — meta picks ↑",
        "boost_traits": ["scaling", "teamfight_consistency"],
        "preferred_archetypes": ["engage", "catcher", "poke"],
    },
    "normal": {
        "description": "Casual — comfort > teoría",
        "boost_traits": ["execution_simplicity", "blind_pick_safety"],
    },
}
```

Esta heurística **NO se implementa en este sprint** (no se requiere data nueva), pero queda registrado como upgrade futuro.

## Meta-conclusión

> *"Las mecánicas son universales; la cultura dicta la ejecución del software."*
> — Nación_Digital_LoL.pdf, p10

Aplicado al motor: **los pesos del scoring son universales** (35% ally_synergy, 20% comp_gap_fill, etc.). Pero las **preferencias de arquetipo** pueden modularse según el contexto de queue/región.

Esto refuerza la decisión arquitectónica original: NO hardcodear el meta en el código, sino exponerlo via JSON (`scoring_weights.json`, `comp_archetypes.json`, etc.) para iterar sin recompilar.
