# Matchups Support vs Support (Lane Phase)

Quién gana lane phase contra quién. Útil cuando el enemy ya pickeó soporte y tenés que elegir el tuyo.

## Reglas generales

1. **Engage hard counterea enchanter solo** (sin frontline). Leona vs Soraka = Leona gana.
2. **Enchanter peel counterea engage solo** (sin follow-up). Janna vs Leona en late = Janna peelea + ADC dispara.
3. **Poke mage counterea melee engage en lane** si tiene rango y range. Xerath vs Leona = Xerath gana lane.
4. **Catcher vs enchanter es coinflip** — depende de skill. Hook acertado = win.

## Matchups específicos (por orden alfabético del soporte que vos pickearías)

### Janna lane phase

| Vs | Ganadora | Nota |
|----|----------|------|
| vs Leona | **Janna** | R cancelea Leona engage. Tornado interrumpe Q. Trade ganador. |
| vs Nautilus | Skill matchup | Si esquivás Q, ganás. Si comen Q, perdés. |
| vs Thresh | Skill matchup | Tornado interrumpe hook si reactionás bien. |
| vs Lux | Janna ligeramente | Janna shield niega poke Lux. Pero si Lux acierta Q, gap. |
| vs Soraka | **Janna** | Janna trade ganador con shield + AD. |
| vs Yuumi | **Janna** | Yuumi sin Janna kill threat. |

### Karma lane phase

| Vs | Ganadora | Nota |
|----|----------|------|
| vs Leona | **Karma** | Range de Q + shield speed permite kitear. |
| vs Soraka | **Karma** | Q poke + RQ = sustain insuficiente para Soraka. |
| vs Lux | Skill matchup | Ambos Q poke. Quien acierta más gana. |
| vs Janna | **Karma** | Karma daño > Janna en lane. |
| vs Brand | **Brand** | Brand burst > Karma sustain. |

### Leona lane phase

| Vs | Ganadora | Nota |
|----|----------|------|
| vs Soraka | **Leona** | E+Q nivel 2 = kill. Soraka sin escape. |
| vs Yuumi | **Leona** | Pre-attach Yuumi = E lock = kill. |
| vs Janna | **Janna** | Tornado interrumpe E. Soft counter. |
| vs Lulu | **Lulu** | W polymorph cancelea engage Leona. |
| vs Nami | Skill matchup | Bubble counterea E. Si fallás Q, perdés. |
| vs Lux | **Lux** | Q range + binding = Leona no llega. |
| vs Thresh | Skill matchup | Quien hace combo primero gana. |

### Lulu lane phase

| Vs | Ganadora | Nota |
|----|----------|------|
| vs Leona | **Lulu** | Polymorph cancelea engage. |
| vs Nautilus | **Lulu** | Polymorph cancelea hook. |
| vs Soraka | Skill matchup | Trade pasivo. |
| vs Janna | Skill matchup | Ambos peelers. Lane neutra. |
| vs Lux | **Lux** | Range > Lulu daño. |

### Lux lane phase

| Vs | Ganadora | Nota |
|----|----------|------|
| vs Leona | **Lux** | Range counterea melee. |
| vs Lulu | **Lux** | Daño > sustain Lulu. |
| vs Soraka | **Lux** | Burst > heal. |
| vs Janna | Coinflip | Ambos zone. |
| vs Brand | **Brand** | Brand sustained burn > Lux. |
| vs Xerath | **Xerath** | Range > Lux. |

### Milio lane phase

| Vs | Ganadora | Nota |
|----|----------|------|
| vs Leona | **Milio** | Range passive + Q + R cleanse = Leona engage no funciona. |
| vs Soraka | Skill matchup | Trade pasivo. |
| vs Janna | Skill matchup | Ambos enchanters. |
| vs Yuumi | **Milio** | Milio kill threat con Q. Yuumi no. |

### Nautilus lane phase

| Vs | Ganadora | Nota |
|----|----------|------|
| vs Soraka | **Nautilus** | Hook = kill. |
| vs Yuumi | **Nautilus** | Pre-attach = kill. |
| vs Lulu | **Lulu** | Polymorph cancelea hook engage. |
| vs Janna | **Janna** | Tornado interrumpe hook. |
| vs Thresh | Coinflip | Quien hookea primero gana. |

### Pyke lane phase

| Vs | Ganadora | Nota |
|----|----------|------|
| vs Soraka | **Pyke** | Stealth + hook = kill. |
| vs Lulu | **Pyke** | Hook + drag = polymorph no salva. |
| vs Leona | **Leona** | Leona tankea Pyke combo. |
| vs Thresh | Skill matchup | Quien hookea primero. |
| vs Yuumi | **Pyke** | Pre-attach Yuumi = R execute. |

### Soraka lane phase

| Vs | Ganadora | Nota |
|----|----------|------|
| vs Leona | **Leona** | All-in la mata. |
| vs Lulu | Skill matchup | Lane pasiva. |
| vs Janna | **Janna** | Trade ganador. |
| vs Karma | **Karma** | Karma poke > sustain Soraka. |
| vs Lux | **Lux** | Burst > heal. |

### Thresh lane phase

| Vs | Ganadora | Nota |
|----|----------|------|
| vs Soraka | **Thresh** | Hook = kill. |
| vs Yuumi | **Thresh** | Pre-attach = kill. |
| vs Leona | Skill matchup | Quien combos primero. |
| vs Nautilus | Skill matchup | Ambos engage. |
| vs Janna | Skill matchup | Tornado puede interrumpir hook. |
| vs Lux | Skill matchup | Si esquiva Q Lux, hookea. |

## Bullies vs Scalers

**Lane bullies** (ganan lane phase): Leona, Nautilus, Thresh, Brand, Lux, Xerath, Pyke, Karma.

**Lane scalers** (pierden lane pero escalan): Soraka, Yuumi, Janna (parcial), Milio, Lulu (parcial), Senna.

**Decisión meta**: si tu equipo es scaling, podés permitirte un soporte scaling. Si tu equipo es early/mid game spike, necesitás un bully.

## Notas para el sistema

Estos matchups se reflejan en los campos `weak_against_supports` y `strong_against_supports` de cada `support_profiles.json`. El factor `enemy_matchup` del scoring usa estos arrays para penalizar/premiar picks vs el enemy support si ya está revelado.
