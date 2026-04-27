# 04 — El Triángulo Moderno: Engage > Poke > Sustain > Engage

> **Fuente:** `Support_Architecture_Dossier.pdf` p6 + `Nación_Digital_LoL.pdf` p5 + `guia de estudio` glosario

## Las 3 reglas + 1 eje invertido

### Regla 1: Engage > Poke
> *"El Engage asesina rápidamente a campeones frágiles e inmóviles de Poke."*

Un Leona o Nautilus que cierra distancia con su all-in **ignora la regen del poke** y mata al supp poke (Lux, Xerath) en una rotación. El daño explosivo supera el daño residual.

### Regla 2: Poke > Sustain/Disengage
> *"El daño constante supera la regeneración; carecen de cierre de brecha."*

Un Lux con ralentizamientos y zone control desgasta indefinidamente a un Soraka/Janna que no puede cerrar distancia. La sustain mitiga 200 dmg, pero la poke aplica 150 dmg cada 5 segundos sin permitir reset.

### Regla 3: Sustain > Engage
> *"Las curaciones mitigan la ráfaga inicial, ganando la pelea extendida."*

Cuando un Leona engagea contra Soraka+ADC, las curaciones devuelven el HP perdido en el burst inicial. Sin daño sostenido aliado, el engage falla y deja al iniciador expuesto.

### Eje clave (invertido): Disengage > Engage
> ⚠ **"Wardens e interrupciones invalidan la inversión total de recursos del iniciador pesado, dejándolo expuesto."**

**Esta es la regla más poderosa para el motor.** Janna (R Monsoon), Braum (W block), Tahm Kench (W eat ally) **anulan el engage** del rival y lo dejan en posición vulnerable. Es un counter HARD.

## Diagrama del triángulo

```
                    ENGAGE
                  ╱        ╲
                 ╱          ╲ Engage→Poke (asesina frágiles)
                ╱            ╲
        Sustain→Engage        ▼
       ╲   (curaciones)        POKE
        ╲                       ╱
         ╲                     ╱
          ╲       Poke→Sustain (daño constante)
           ╲                 ╱
        SUSTAIN ◀━━━━━━━━━━╱
        (Wardens)
            ↑
    DISENGAGE invalida ENGAGE (eje invertido)
```

## Implicancia para el motor

**Esta es probablemente la nueva regla con más impacto.** El motor debe detectar el arquetipo del **enemy support** y boostear los counters apropiados.

### Pseudocódigo de la regla

```python
TRIANGLE = {
    # Tu archetype → counterea a estos archetypes enemigos
    "engage":     {"beats": ["poke"],            "loses_to": ["enchanter", "catcher"]},
    "poke":       {"beats": ["enchanter"],       "loses_to": ["engage", "catcher"]},
    "enchanter":  {"beats": ["engage", "poke"],  "loses_to": []},  # eje invertido
    "catcher":    {"beats": ["poke"],            "loses_to": ["enchanter"]},
}

def apply_triangle_bonus(my_archetype, enemy_supp_archetype):
    if enemy_supp_archetype in TRIANGLE[my_archetype]["beats"]:
        return +10  # boost score: counterea al supp enemigo
    if enemy_supp_archetype in TRIANGLE[my_archetype]["loses_to"]:
        return -8   # penaliza score: sos counter-pickeable
    return 0
```

**Ya existe en `support_archetypes.json`** un campo `archetype_vs_enemy_comp` que cubre algo parecido pero **vs comp enemiga**, NO vs supp individual. Hay que agregar la regla específica vs **enemy support archetype**.

### Nota crítica

El "Disengage > Engage" es una regla **fuerte** pero asimétrica. **Solo aplica si el supp enchanter tiene una herramienta real de disengage** (Janna R, Lulu W+R, Milio R, Renata W, Karma R+E). Soraka y Yuumi son sustain pero **no disengage** — no aplican esta regla.

## Materialización en `strategic_triangle.json`

Voy a crear `data/draft_advisor/kb/structured/strategic_triangle.json` con:

```json
{
  "triangle": {
    "engage":    { "beats": ["poke"],           "loses_to": ["enchanter_disengage", "catcher"] },
    "poke":      { "beats": ["enchanter_pure"], "loses_to": ["engage", "catcher"] },
    "enchanter_disengage": { "beats": ["engage", "poke"], "loses_to": [] },
    "enchanter_pure":      { "beats": ["engage"],         "loses_to": ["poke"] },
    "catcher":   { "beats": ["poke", "enchanter_pure"], "loses_to": ["enchanter_disengage"] }
  },
  "enchanter_disengage_supports": ["Janna", "Lulu", "Milio", "Renata", "Karma"],
  "enchanter_pure_supports":      ["Soraka", "Yuumi", "Nami"],
  "scoring": {
    "beats_bonus": 10,
    "loses_to_penalty": -8,
    "neutral": 0
  }
}
```

Esta clasificación más fina (separar enchanter "pure sustain" del enchanter "disengage") es la **diferencia que las fuentes resaltan** y que el motor actual no captura.
