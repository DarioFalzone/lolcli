# Filosofía de Pickeo de Soporte

Documento maestro que explica **cómo razona el Support Advisor**. Define pesos, prioridades, y las reglas heurísticas que el motor de scoring aplica.

## El problema

Cuando vas a pickear soporte en ranked, ves un draft con N picks ya hechos (entre aliados y enemies). Tu trabajo es elegir el soporte que **maximice el éxito del equipo** dado ese contexto. No hay un "mejor soporte absoluto" — hay el mejor soporte **para esta partida puntual**.

## Los 5 factores que decide el sistema

Basado en el `scoring_weights.json` actual (ADC mode), adaptado para soporte:

| Factor | Peso | Qué evalúa |
|--------|------|-----------|
| **Sinergia con ADC aliado** | 35% | El soporte trabaja con el ADC durante 25-30 min de lane y midgame. Esta sinergia es lo más importante. |
| **Matchup contra threats enemigos** | 20% | ¿Tu soporte puede peelear los assassins enemigos? ¿Tu engage abre el frontline enemigo? |
| **Cubrir gaps de tu comp** | 20% | Si tu equipo no tiene engage, conviene un soporte engage. Si tu ADC es squishy + immobile, conviene peel. |
| **Sinergia con jungla aliada** | 10% | Si la jungla ya provee CC (Vi, Sejuani), el soporte puede ser enchanter. Si es farm jungler (Karthus), conviene engage. |
| **Blind pick safety + Comfort** | 15% | Pickear algo que no domines en ranked es subóptimo. Premiamos comfort y blind safety. |

## Reglas heurísticas (el "sentido común" codificado)

Estas son las reglas que aplica el sistema cuando construye `strengths_in_this_draft` y `risks_in_this_draft`. Son las que un jugador experimentado seguiría intuitivamente.

### Reglas para elegir engage support

1. **Si tu ADC es burst/follow-up alto (MF, Samira, Draven, Lucian)** → engage (Leona, Nautilus) destaca.
2. **Si hay >=2 dive en enemy team** → engage es riesgoso, priorizar enchanter (Janna, Lulu, Milio).
3. **Si tu jungla es farm (Karthus, Master Yi, Kayn-blue)** → engage support compensa la falta de iniciación.
4. **Si tu top es split (Camille, Fiora, Jax)** → engage support en bot abre teamfights mientras top splittea.
5. **Si tu ADC es Caitlyn / Jhin / Varus (poke ADC)** → engage NO es óptimo. Mejor poke mage.

### Reglas para elegir enchanter

6. **Si tu ADC es hypercarry scaling (Jinx, KogMaw, Aphelios, Twitch, Vayne)** → enchanter (Lulu, Janna, Milio) es ideal.
7. **Si hay >=2 dive en enemy** → enchanters peelers (Janna, Lulu, Milio) son defensivos.
8. **Si tu comp es scaling (mid scaling + ADC scaling)** → enchanter para sobrevivir lane.
9. **Si tu jungla ya tiene engage (Vi, Sejuani, Wukong)** → enchanter es el complemento perfecto.

### Reglas para elegir poke / mage support

10. **Si tu ADC es Caitlyn / Jhin / Varus + tu mid es poke (Zoe, Xerath, Lux)** → comp de poke siege, conviene Lux/Brand/Zyra.
11. **Si la enemy comp es engage tank (Malphite + Nautilus + Sejuani)** → poke + kiting pre-objetivos.
12. **Si tu equipo NO tiene daño AP** → mage support compensa (con Brand, Zyra, Xerath).

### Reglas para elegir catcher/pick

13. **Si tu ADC es lane-dominant (Draven, Lucian) + jungla con early ganks (Elise, Lee Sin)** → Thresh, Blitz, Pyke crean snowball.
14. **Si la enemy ADC es immobile (KogMaw, Twitch)** → Blitz / Thresh la convierten en kill confirmada con un hook.

### Reglas anti-pick

15. **NO pickees Yuumi en blind pick si no sabés qué ADC tendrás** — Yuumi necesita un ADC compatible.
16. **NO pickees engage support si tu equipo no tiene follow-up** (ej. tu mid es Veigar control mage que no puede iniciar).
17. **NO pickees Soraka si la enemy comp es full assassin dive** — sustain no peelea hard CC.

## Cómo se construyen las "Razones" (output del sistema)

Cada razón en `strengths_in_this_draft` viene de evaluar:

- **Sinergia con un aliado específico**: "Tu Q sin combo con la R de Samira garantiza el wombo" (cuando hay un ADC compatible).
- **Anti-amenaza específica**: "Tu W bloquea el Q de Caitlyn que es la principal threat de poke" (cuando hay una threat enemiga puntual).
- **Cubrir gap detectado**: "Tu equipo no tenía engage, vos lo aportás con R + Q" (cuando `analyzer.py` detecta gap).

Cada razón es **específica al draft** — no es genérica. Esto es lo que diferencia el sistema de un tier list.

## Cómo se construye el "Plan de Juego"

`enabled_play_pattern` se construye combinando:

1. **`play_pattern_template`** del soporte recomendado (definido en `support_profiles.json`).
2. **Sustitución de placeholders** con datos del draft: `{allied_adc}`, `{enemy_adc}`, `{enemy_jungler}`, `{primary_threat}`.

Ejemplo template Leona: `"Lane: agresivo nivel 2 con E+Q vs {enemy_support}. Spike fuerte nivel 6 — buscar all-in con R en {enemy_adc}. Mid: roams a mid después de prios bot. Late: front-line tanky, peek vision en chokes para iniciar teamfights."`

Tras sustitución: `"Lane: agresivo nivel 2 con E+Q vs Soraka. Spike fuerte nivel 6 — buscar all-in con R en Caitlyn. Mid: ..."`.

## Lo que NO hace el sistema (limitaciones)

- **No considera bans más allá del input** — si te banean el comfort pick, decílo en el toggle.
- **No considera el ranked tier del jugador** — un Leona en Iron es diferente de un Leona en Diamond, pero el sistema asume ejecución competente.
- **No considera el patch específico de buffs/nerfs recientes** — el patch base es 16.7. Si hay un cambio reciente que invierte un matchup, hay que actualizar el JSON.
- **No considera la duración estimada de la partida** — un soporte scaling como Yuumi pierde valor en partidas de 22min.

Estas limitaciones se documentan también en `data/draft_advisor/audit/STALE_DATA_REGISTER.json`.
