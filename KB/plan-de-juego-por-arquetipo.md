# Plan de Juego por Arquetipo

Templates del campo `enabled_play_pattern` que devuelve el sistema. Cada template describe **lane → midgame → late** para que el jugador sepa exactamente qué hacer con el soporte recomendado.

Los placeholders entre llaves se sustituyen con datos del draft real:
- `{allied_adc}` → nombre del ADC aliado
- `{enemy_adc}` → nombre del ADC enemigo
- `{enemy_support}` → soporte enemigo (si está pickeado)
- `{primary_threat}` → threat principal detectada por el analyzer
- `{ally_jungler}` → jungla aliada

## Template: Engage Support (Leona / Nautilus / Rell / Alistar)

**Lane (0-14 min):**
> Lane: presión nivel 2 buscando E+Q vs {enemy_support}. Mantené ward en tribush para evitar gank de {enemy_jungler}. Spike fuerte nivel 6 — buscar all-in con R en {enemy_adc}, especialmente si está empujado. Coordiná con {ally_jungler} para gank con CC chain.

**Midgame (14-25 min):**
> Mid: después de prio bot tower, roam a mid o seguí con {ally_jungler} en objetivos. Tu R abre teamfights cerca de drake/herald. Mantené visión en pixel y tribush antes de cada objetivo.

**Late (25+ min):**
> Late: front-line tanky en chokes. Espera el momento donde podás pegar R en >=2 enemies. Si {primary_threat} (assassin) intenta diven a {allied_adc}, vos sos su primer parada — usá tu HP para absorber damage.

---

## Template: Enchanter Support (Lulu / Janna / Soraka / Milio / Nami)

**Lane (0-14 min):**
> Lane: posicionamiento tras minions. Trade pasivo con E shield/heal y autos cuando hay oportunidad. NO buscar engage — tu ADC {allied_adc} prioriza farming seguro. Ward defensivo en tribush. Si {enemy_support} es engage (Leona, Nautilus), usar W/heal el momento exacto del engage.

**Midgame (14-25 min):**
> Mid: stick to {allied_adc}. Roams largos = pérdida de XP y golds. Si tu ADC quiere participar en obj, vos lo escoltás. R tuya solo en momentos críticos: o salvar al ADC, o cerrar la kill.

**Late (25+ min):**
> Late: vivís y morís con {allied_adc}. Posicionamiento detrás de él/ella. Si {primary_threat} (dive/assassin) entra al backline, full peel: R + W + flash si necesario. NUNCA inicies un fight — esperá a que el enemy commitee.

---

## Template: Poke / Mage Support (Lux / Brand / Zyra / Xerath / Vel'Koz)

**Lane (0-14 min):**
> Lane: poke constante con Q desde max range. Aprovechá que {enemy_support} es {archetype enemy} para zonear. Coordiná Q+E con autos de {allied_adc} para poke chains. Tu objetivo: HP del enemy ADC al 50% antes de nivel 6. Spike nivel 6 — R combo en kill window.

**Midgame (14-25 min):**
> Mid: empujá tower bot con waveclear. Después roam mid o river para visión. Coordiná con {ally_jungler} en herald/drake. Tu daño AP es crítico para el equipo si no hay otro mage.

**Late (25+ min):**
> Late: posicionamiento backline lateral (NO con el ADC). Tu rol: poke pre-fight, kitear, daño en teamfights desde rango max. CUIDADO con dive: tenés bajo HP/peel — flash defensivo o Zhonya si tenés.

---

## Template: Catcher / Pick Support (Thresh / Blitzcrank / Pyke / Rakan)

**Lane (0-14 min):**
> Lane: presión con threat de hook. {enemy_adc} se posicionará defensivo — capitalizá zoneo para que {allied_adc} farmee free. Buscá hooks oportunistas (cuando el enemy va por CS, después de habilidad whifeada). Coordiná con {ally_jungler} para gank — un hook = gank confirmado.

**Midgame (14-25 min):**
> Mid: roams a mid/river. Tu pick potential decide el midgame. Vision control en river y junglas enemigas. Un hook en team neutral = ace win.

**Late (25+ min):**
> Late: pick comp depende de catches pre-fight. Posicionamiento agresivo PERO con escape ready (lantern Thresh / R-W cancel Pyke / E Rakan). NUNCA inicies un teamfight 5v5 frontal — siempre buscá pick antes.

---

## Templates específicos por soporte (overrides)

Algunos soportes tienen plan de juego único que merece su propio template.

### Pyke (engage hybrid + roam)

**Lane:**
> Lane: stealth (W) en el bush para hook engage. Pre-6 farmeás ZERO — sos puro support gold. Spike nivel 6 — R execute window (HP enemy < 35%). Coordiná con {ally_jungler}.

**Mid:**
> Mid: roams agresivos a top y mid (TP en R+W stealth). Tu objetivo: kills en otras lanes. Cada R execute te da gold compartido para {allied_adc}.

**Late:**
> Late: inicias picks con E+Q, R execute en HP bajo. Falls off vs full tanks — buscá squishies.

### Soraka (sustain + global)

**Lane:**
> Lane: heal + Q poke. Defensivo extremo. Stick al ADC. NUNCA seas pickeable.

**Mid:**
> Mid: stay con ADC. R global para salvar split o objetivos cross-map.

**Late:**
> Late: posicionamiento absurdamente atrás. R global para sostener teamfight. Si te pillan, perdés. Flash always.

### Yuumi (attached scaling)

**Lane:**
> Lane: defensivo extremo pre-6. Attach al ADC. Detached solo para auto poke seguro. Trade con E + autos.

**Mid:**
> Mid: stick a ADC. Tu W passive escala AD/AP — sos un buff item andante.

**Late:**
> Late: full attach a hypercarry. Tu R puede salvar fights perdidos. NO te detachés en teamfights — sos pickeable.

---

## Cómo se construye el play_pattern dinámico

El motor de scoring sigue este algoritmo:

1. Leer `play_pattern_template` del soporte top pick (`support_profiles.json`).
2. Sustituir placeholders con datos del `DraftState` actual.
3. Si hay condiciones especiales (ej. enemy comp dive heavy), agregar advertencia: "⚠ Cuidado: enemy team tiene 3 dive — no inicies sin todos los allies presentes."
4. Truncar a ~250 palabras para que entre en la card del frontend.

Esto se hace en `scoring._generate_play_pattern_supp()`.
