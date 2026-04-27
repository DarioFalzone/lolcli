# 02 — Jerarquía de Pick Order

> **Fuente:** `Support_Architecture_Dossier.pdf` p3, p4 + `imagen guia de estrategia.png`

## Pirámide de riesgo en el draft

Las fuentes establecen una jerarquía explícita sobre **qué rol DEBE tener el último pick** en cada bando:

```
                    🔺 Top Lane                    Riesgo crítico (B5/R5)
                  ▲ Mid & Soporte ▲                Riesgo moderado (B3/R3/B4)
                ▲▲▲ ADC & Jungla ▲▲▲              Seguro para Blind Pick (R1/B1/B2)
```

### Riesgo crítico — Top Lane (B5/R5)
> *"La Isla del Counter. Un matchup desfavorable aquí vuelve la partida injugable, perdiendo el control del mapa y las oleadas."*

Top tiene la **menor influencia inmediata** sobre bot lane pero la **mayor punición por counter-pick**: un mal matchup en Top significa que el carrilero no puede acercarse a los súbditos, perdiendo XP y oro. **El carrilero superior con counter-pick tiene una tasa de victoria sustancialmente mayor.**

### Riesgo moderado — Mid & Soporte (B3/R3/B4)
> *"Selecciones de utilidad o flex picks. Un counter aquí es difícil, pero la línea aún se puede jugar mediante roaming o sustain."*

El soporte se sitúa en **riesgo moderado**: si te contra-pickean, tenés salidas tácticas (roaming, freeze, juego de visión). No es ideal pero no es catastrófico.

### Seguro para Blind Pick — ADC & Jungla (R1/B1/B2)
> *"Impacto mitigable por el equipo. Las selecciones más seguras para abrir el draft."*

ADCs y junglas tienden a tener kits versátiles. Un Caitlyn vs Lucian sigue siendo jugable. Un Lee Sin vs Vi también.

## Sistema de Llamada y Respuesta

> **Bando Azul (B1-B3):** Hace la "llamada" — Power Pick del meta + consolidación del núcleo (Jungla/ADC).
>
> **Bando Rojo (R1-R3):** Da la "respuesta" — selecciones dobles para asegurar sinergias de Bot Lane.
>
> **R5 — El último pick rojo:** Es **el activo más valioso del draft.** Define la línea asimétrica ganadora.

### Implicancia táctica para el supp

Si **el target_role es support y el pick_position es late** (R5 o equivalente), el motor debe:

1. Priorizar **counter-picks específicos** sobre blind-pick safety
2. Boostear `enemy_matchup` (peso ↑ del 20% al ~30% para esa run)
3. Bajar `blind_pick_safety` (peso ↓ del 5% al ~2% para esa run)

Esto ya está parcialmente implementado en `scoring.py::_pick_position_adjustment()` pero la KB lo respalda con autoridad.

## Flex Picks — la herramienta del bando rojo

El Dossier (p4) destaca campeones que **rompen la estructura del rival** porque pueden jugar en múltiples roles:

- **Seraphine** (Mid/Sup/ADC)
- **Poppy** (Top/Jg/Sup)
- **Karma** (Mid/Sup)
- **Senna** (ADC/Sup)
- **Bard** (Sup/Jg en off-meta)

Estos picks **obligan al enemigo a gastar bans subóptimos o seleccionar counters equivocados**.

> En el motor, esto justifica que campeones flex tengan un **bonus de blind_pick_safety** porque su versatilidad complica al enemigo predecir el rol final.

## Directriz del Analista (Dossier p3)

> *"Ceder el último pick del carril superior no es sumisión: es optimización de recursos y protección de win conditions."*

Es decir, en el draft profesional **se prioriza dar el R5 al Top** para minimizar el riesgo crítico, no a otros roles. El supp generalmente juega en B3/R3/B4 donde el counter es manejable.
