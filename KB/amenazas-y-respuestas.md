# Amenazas y Respuestas

Cómo responder con tu pick de soporte a cada tipo de comp enemiga.

## Tipos de comps enemigas

### 1. Dive Comp (Hecarim + Camille + Akali + Zed + Pyke, etc.)

**Caracterización:**
- >=3 campeones con engage long-range / dash-in / leap.
- Backline enemy es secundaria (no tienen scaling).
- Mid-game spike fuerte; necesitan capturar early.

**Threats típicas:** Vi (R), Hecarim (R), Camille (R+E), Wukong (R), Sejuani (R), Diana (R+Q), Akali (E+R), Zed (R), Nocturne (R).

**Tu objetivo como soporte:**
- Sobrevivir el dive y peelear al ADC.
- NO buscar engage propio — el dive enemy ya engagea por vos.
- Mantener ADC vivo el tiempo necesario para que el carry mate al diver.

**Soportes ideales:**
- **Janna** — R disengage cancelea dive. Tornado interrumpe Hecarim/Vi.
- **Lulu** — R knockup cancela un diver. W polymorph anula su threat.
- **Milio** — R cleanse all CC. Range passive + escape.
- **Soraka** (parcial) — sustain por daño, pero sin hard CC contra hard dive.

**Soportes a evitar:**
- Engage support (Leona, Nautilus) — vas a estar tankeando 3 dives sin peel para tu ADC.
- Poke mage (Lux, Brand) — squishy y sin peel.
- Yuumi — attached pero sin hard CC.

**Razones que el sistema generará:** "Counters {primary_threat} dive con tu R disengage / W polymorph / R cleanse."

---

### 2. Poke Comp (Caitlyn + Jhin + Xerath + Lux + Ezreal, etc.)

**Caracterización:**
- 3+ campeones con poke long-range (skillshots).
- Mid game spike no tan fuerte como dive — buscan ganar gradualmente.
- Vulnerables a engage agresivo si los pillás flat-footed.

**Threats típicas:** Caitlyn (W+Q), Jhin (W+R), Xerath (Q), Vel'Koz (Q+R), Ezreal (Q+R), Lux (Q+R), Varus (Q).

**Tu objetivo como soporte:**
- Engage hard para evitar el poke siege.
- O contra-poke para igualar.

**Soportes ideales:**
- **Leona / Nautilus / Rell** — engage hard para forzar fight close-range.
- **Alistar** — gap close + WQ + R = imposible kitear.
- **Karma / Lulu** — shields + speed = mitigás poke.
- **Janna** — tornado + W cancela channels (Caitlyn ult, Xerath W).

**Soportes a evitar:**
- Soraka — sustain no compensa poke prolongado siege.
- Yuumi — sin engage, te hacen siege gradual.
- Lux / Brand — poke vs poke = quien tiene mejor backline gana, generalmente NO vos.

**Razones que el sistema generará:** "Hard engage {Q+E} cierra distancia vs poke comp enemiga ({primary_threat})."

---

### 3. Pick Comp (Thresh + Blitz + Ahri + Karma + LeBlanc, etc.)

**Caracterización:**
- 2+ campeones con catches long-range (hooks, charms, dashes en).
- Buscan ventajas numéricas pre-fight.
- Vision control crítico.

**Threats típicas:** Blitz (Q), Thresh (Q), Pyke (Q), Ahri (E), LeBlanc (E+R), Morgana (Q), Lissandra (E+R).

**Tu objetivo como soporte:**
- Vision control para evitar hooks ciegos.
- Tools para safe-position al ADC.
- Counter-pick capability (Cleanse, Janna R, etc.).

**Soportes ideales:**
- **Janna** — R + Tornado = counter-pick. Si te hookean, R los aleja.
- **Lulu** — W polymorph counter-pick si reactiona rápido.
- **Soraka** — heal sostiene picks fallidos.
- **Thresh** — versatilidad: contra-hook + lantern save.

**Soportes a evitar:**
- Yuumi — pickeable si la detachan.
- Engage support solo (Leona) — si te catchean a vos solo, el ADC queda 1v5.

**Razones que el sistema generará:** "Tu R/W cancela hooks de {enemy_support} y peelea catches de {primary_threat}."

---

### 4. Scaling Comp (Vladimir + Vayne + Kayle + KogMaw + Soraka, etc.)

**Caracterización:**
- Late game monsters (5+ items para online).
- Lane phase débil; necesitan sobrevivir 18-22 min.
- Vulnerables a snowball early.

**Threats típicas:** Vayne (late), Kayle (16+), KogMaw (3 items), Vladimir (4 items), Veigar (full stacks), Senna (200 souls).

**Tu objetivo como soporte:**
- Snowball lane para evitar que escalen.
- O igualmente scaling si tu equipo también scalea.

**Si tu equipo es early-mid (Draven, MF, etc.):**
- **Engage support** (Leona, Nautilus) para snowball lane.
- **Catcher** (Thresh, Blitz) para forzar errores enemy.

**Si tu equipo es scaling también (Jinx, KogMaw):**
- **Enchanter** (Lulu, Janna, Milio) para sobrevivir a 25 min.

**Razones que el sistema generará:** "Snowball lane antes de que {primary_threat} escale (spike {item_X})."
"Match scaling con tu enchantment buff a {allied_adc} hypercarry."

---

### 5. Comps mixtas

Las comps reales son híbridas. El sistema usa `analyzer.py` que detecta:
- `has_dive: bool`
- `has_burst: bool`
- `has_tanks: bool`
- `has_poke: bool`
- `threat_level_to_adc: ThreatLevel`

Y combina las recomendaciones. Por ejemplo, si `has_dive=true AND has_poke=true`:
- Priorizar enchanter peel (cubre dive) con shield range (cubre poke).
- Janna o Lulu son ideales.

## Tabla resumen: Comp enemiga → Arquetipo recomendado

| Enemy Comp | Arquetipo soporte ideal | Soporte concreto |
|-----------|-------------------------|------------------|
| Dive (3+) | Enchanter peel | Janna, Lulu, Milio |
| Poke siege (3+) | Engage hard | Leona, Nautilus, Alistar |
| Pick (2+ catches) | Counter-utility | Janna, Lulu, Thresh |
| Scaling (full late) | Engage snowball | Leona, Pyke (con team early) |
| Tank-heavy frontline | Mage damage | Brand, Zyra, Lux |
| Mixed (dive + poke) | Enchanter shield | Lulu, Karma, Milio |

## Notas para el sistema

Esta lógica se implementa en `scoring._score_supp_peel_vs_threats()` y `_score_comp_gap_fill()`. Los gaps detectados por `analyzer.py` se cruzan con el `archetype` del soporte para generar el factor de score `enemy_matchup`.

Las razones específicas (`strengths_in_this_draft`) se construyen mencionando explícitamente la threat detectada y la tool del soporte que la counterea.
