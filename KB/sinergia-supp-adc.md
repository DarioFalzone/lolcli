# Sinergia Support → ADC

La elección de soporte está dominada por la sinergia con el ADC aliado (35% del peso del scoring). Esta tabla cubre los matches más comunes.

## Tabla de sinergias (10 soportes core × ADCs comunes)

Escala 1-10. **10 = pareja S-tier**, 6 = bien sin destacar, 1 = anti-sinergia.

| Soporte ↓ / ADC → | Jinx | Kai'Sa | Aphelios | Caitlyn | MF | Samira | Draven | Lucian | Ezreal | Vayne | KogMaw | Twitch | Jhin | Varus | Senna |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Leona** (engage) | 6 | 8 | 7 | 4 | 10 | 10 | 10 | 9 | 5 | 6 | 6 | 7 | 5 | 6 | 5 |
| **Nautilus** (engage) | 8 | 9 | 8 | 6 | 9 | 9 | 9 | 9 | 6 | 7 | 8 | 8 | 6 | 7 | 6 |
| **Thresh** (catcher/engage) | 8 | 10 | 9 | 7 | 8 | 9 | 9 | 10 | 7 | 7 | 8 | 8 | 7 | 8 | 7 |
| **Pyke** (engage hybrid) | 6 | 7 | 6 | 5 | 8 | 9 | 10 | 10 | 6 | 6 | 5 | 6 | 6 | 6 | 5 |
| **Lulu** (enchanter) | 10 | 7 | 8 | 7 | 5 | 5 | 5 | 7 | 8 | 9 | 10 | 10 | 8 | 7 | 6 |
| **Janna** (enchanter) | 10 | 7 | 9 | 8 | 4 | 5 | 6 | 7 | 9 | 8 | 10 | 9 | 8 | 7 | 7 |
| **Soraka** (enchanter sustain) | 8 | 6 | 8 | 8 | 4 | 5 | 6 | 6 | 9 | 6 | 9 | 8 | 8 | 8 | 7 |
| **Milio** (enchanter range) | 10 | 6 | 9 | 8 | 5 | 5 | 5 | 7 | 8 | 7 | 10 | 9 | 9 | 8 | 7 |
| **Lux** (mage poke) | 5 | 6 | 6 | 10 | 7 | 6 | 7 | 7 | 7 | 5 | 5 | 5 | 9 | 8 | 7 |
| **Karma** (enchanter poke) | 6 | 6 | 6 | 8 | 6 | 6 | 7 | 8 | 9 | 6 | 6 | 6 | 8 | 7 | 8 |

## Razones específicas de los pares S-tier (10/10)

### Leona + MF/Samira/Draven (engage + burst)
- E+Q de Leona stunea 1.5s, suficiente para la R de MF/Samira/Draven.
- Wombo de Leona R en 4 enemies = MF R limpia o Samira ult fácil.
- Lane phase 2 nivel 2 = kill garantizada en la mayoría de matchups.

### Thresh + Kai'Sa/Lucian
- Lantern save permite a Kai'Sa ultear in y volver. Multiplica su mobility.
- Lucian + Thresh es el premier kill lane. Hook → flay → Q+E+R = doble kill.
- Versatilidad de Thresh (hook/peel/lantern) cubre los huecos de ambos ADCs.

### Lulu + Jinx/KogMaw/Twitch (enchanter + hypercarry)
- W attack speed steroid = Jinx Fishbones DPS estratosférico.
- E shield + R knockup = imposible diven a KogMaw.
- Twitch ult con Lulu shield = puede ult en 5v1 y sobrevivir.

### Janna + Jinx/KogMaw (enchanter peel hard)
- R disengage es la mejor del juego. Cualquier engage enemy se desinfla.
- Tornado interrumpe channels (Caitlyn ult, KogMaw R, Vayne tumble).
- Shield AD steroid = trade ganador en lane sin necesidad de engage.

### Milio + Jinx/KogMaw/Aphelios (range extender)
- Passive da +75 range a las autos del ADC = la diferencia entre poke ganado o perdido.
- R cleanse all CC = inmune a wombo combos.
- E shield + slow self = peel decente para divers.

### Lux + Caitlyn (poke siege)
- Q root + Caitlyn trap = combo undodgeable.
- Ambos zone control en lane = empujás torre rápido, recursos para roams o objetivos.
- E damage en Caitlyn snare = trade demoledor.

## Anti-sinergias (1-3/10) — pares a EVITAR

| Par | Por qué |
|-----|---------|
| **Yuumi + Draven** | Yuumi no proporciona kill threat en lane; Draven necesita lanes que pueda dominar. |
| **Leona + Caitlyn** | Caitlyn quiere zonear; Leona quiere all-in. Win conditions opuestas. |
| **Soraka + Draven/Samira** | Sustain no convierte ventaja en lane; ADC bully se "frustra". |
| **Lux + Vayne** | Vayne quiere late game; Lux quiere snowball lane. Ambos squishy. |
| **Pyke + KogMaw/Twitch** | Pyke quiere kills en lane; estos ADCs no se mueven hasta nivel 11. |

## Notas para el sistema

Esta tabla se traduce directamente al campo `best_with_adcs` de cada `support_profiles.json` (los pares 9-10) y opcionalmente `weak_with_adcs` para los 1-3.

El motor de scoring lee estos arrays cuando construye el factor "synergy_with_ally_adc" del scoring breakdown.
