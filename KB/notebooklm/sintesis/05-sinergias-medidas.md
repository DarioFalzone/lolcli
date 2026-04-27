# 05 — Sinergias estructurales medidas (con winrate)

> **Fuente:** `Support_Architecture_Dossier.pdf` p7 — "El Código del 2v2"

## Las 4 parejas medidas (datos de Patch 2025.X, LCK + LPL)

El Dossier presenta **4 sinergias 2v2 con winrate comprobado >53%**, que el motor debe aplicar como **boost duro** independiente de las heurísticas blandas.

### 1. Samira & Nautilus — 53.7% WR
> **Motor Airborne**: Samira requiere **levantamientos** para activar su pasiva (`Daredevil Impulse`). Nautilus provee **3 fuentes de CC compatibles**: Q (Dredge Line), R (Depth Charge), pasiva (Staggering Blow). Cada CC genera un punto de Daredevil para Samira.

**Mecánica clave:** la R de Samira (`Inferno Trigger`) requiere mantener proximidad de combate. Nautilus la consigue con engage en cadena.

### 2. Lucian & Nami — 54.0% WR
> **Motor de Ráfaga**: La E de Nami (`Tidecaller's Blessing`) **desencadena la pasiva de Lucian** (`Lightslinger`), que dispara un segundo proyectil con AP scaling. Nami buffa + activa pasiva = double-shot empoderado.

**Mecánica clave:** dos sources lo activan: la E (buff directo) Y la W (`Ebb and Flow` heal+poke). En lane se traduce en burst trades imposibles de igualar para el rival.

### 3. Ashe & Seraphine — 54.7% WR
> **Motor de Enraizamiento**: La pasiva de Ashe (`Frost Shot`) **ralentiza con cada AA**. La E de Seraphine (`Beat Drop`) **enraíza si el target ya está ralentizado**. Combo natural: 1 AA de Ashe → root garantizado de Seraphine.

**Mecánica clave:** esta es la sinergia con el **WR más alto de las 4** (54.7%) porque el hard CC del root es prácticamente automático en lane.

### 4. Jinx & Thresh — 54.3% WR
> **Motor de Reposicionamiento**: La linterna de Thresh (`Dark Passage`) **compensa la nula movilidad de Jinx**. Su gancho (Q `Death Sentence`) asegura las trampas (E `Flame Chompers`) de Jinx en lane.

**Mecánica clave:** Jinx es una de las ADCs más inmóviles del juego (sin dash). Thresh provee escape (W) + setup (Q+E) + peel (R box). Es la pareja "manual" pero con WR alto demostrando ejecución consistente.

## Cómo aplicar al motor

Estas 4 parejas son **datos duros**. No son opinión heurística, son evidencia de WR. El motor debe:

1. **Detectar la pareja**: si el ADC aliado y el supp candidato forman una pareja medida → boost
2. **Boost asimétrico**: cuanto mayor el WR observado, mayor el boost

### Implementación propuesta

```python
# data/draft_advisor/kb/structured/measured_synergies.json
{
  "synergies": [
    {
      "adc": "Samira",     "supp": "Nautilus",  "winrate": 0.537,
      "engine": "airborne",
      "reason": "Samira requires airborne for passive; Nautilus provides 3 CC sources."
    },
    {
      "adc": "Lucian",     "supp": "Nami",      "winrate": 0.540,
      "engine": "burst",
      "reason": "Nami's E triggers Lucian's Lightslinger passive (double-shot)."
    },
    {
      "adc": "Ashe",       "supp": "Seraphine", "winrate": 0.547,
      "engine": "rooted",
      "reason": "Ashe slows with every AA; Seraphine's E roots slowed targets."
    },
    {
      "adc": "Jinx",       "supp": "Thresh",    "winrate": 0.543,
      "engine": "repositioning",
      "reason": "Thresh lantern + hook setup compensates Jinx's lack of mobility."
    }
  ],
  "scoring": {
    "wr_to_bonus": "linear interpolation: 50%→0pts, 55%→15pts"
  }
}
```

```python
def _score_measured_synergy(adc_id, supp_id):
    """Lookup en measured_synergies.json. Si hay match con WR >50%, devuelve bonus
       interpolado: cada punto de WR sobre 50% = +3 score (hasta 15pts a 55%)."""
    pair = find_pair(adc_id, supp_id)
    if pair is None:
        return 0
    excess_wr = max(0, pair.winrate - 0.50) * 100  # ej: 53.7 → 3.7
    return min(15, excess_wr * 3)  # ej: 3.7 * 3 = 11.1pts
```

## Nota: estas 4 parejas no son exhaustivas

Las fuentes mencionan estas 4 como **muestras representativas** de motores estructurales. Hay otras parejas conocidas no medidas en el Dossier que igual pueden inferirse heurísticamente:

- **Draven + Pyke** (engine: execute para snowball)
- **Caitlyn + Lux** (engine: poke+root combo)
- **Vayne + Janna** (engine: peel for hypercarry)
- **Kog'Maw + Lulu** (engine: buff for hyper-carry)
- **MissFortune + Leona** (engine: hard engage + R nuke)

Estas pueden agregarse al JSON con un campo `confidence: "heuristic"` (sin WR comprobado) y un bonus menor (ej: +6 vs +11). El motor debe distinguir entre `confidence: "measured"` y `confidence: "heuristic"`.

## Implementación final en `measured_synergies.json`

Mezclar:
- Las **4 medidas** del Dossier con WR exacto
- ~10-15 **heurísticas conocidas** de la pro scene con WR estimado/null

Ver el archivo generado en [`data/draft_advisor/kb/structured/measured_synergies.json`](../../../data/draft_advisor/kb/structured/measured_synergies.json).
