---
schema_version: "1.0"
kb_version: "1"
id: "arch-front-to-back"
title: "Arquetipo de teamfight frontal"
type: "archetype_note"
domain: "draft_advisor"
patch: "*"
source_type: "expert_analysis"
source_url: ""
source_file: ""
created_at: "2026-04-08"
last_reviewed_at: "2026-04-08"
review_status: "reviewed"
confidence: "high"
champions: ["Jinx", "KogMaw", "Aphelios", "Twitch", "Tristana", "Vayne", "Sivir", "Xayah"]
roles: ["Bot"]
topics: ["front_to_back", "hypercarry", "teamfight", "scaling", "frontline_dependency", "peel_dependency", "positioning"]
tags: ["archetype", "comp_theory", "strategy"]
derived_from: []
supersedes: []
superseded_by: []
---

## Resumen

El teamfight frontal es el arquetipo más centrado en el ADC. La frontline aliada inicia y absorbe cooldowns enemigos mientras las fuentes de peel protegen al carry de backline, que aplica DPS sostenido desde una posición segura. Es la composición donde la elección del ADC importa más: un ADC que no aprovecha frontline y peel desperdicia toda la estrategia del equipo.

## Hallazgos Clave

- **Condiciones que definen el teamfight frontal:**
  1. El equipo aliado tiene 2+ campeones capaces de hacer frontline (tanques o bruisers con engage).
  2. El equipo aliado tiene al menos 1 fuente confiable de peel (enchanter, support con CC o tanque de peel).
  3. La condición de victoria aliada es "proteger al carry", no split-push, pick aislado ni snowball temprano.
- **Ranking de ADCs en teamfight frontal:**
  - **S-tier:** Kog'Maw (DPS más alto si está protegido), Jinx (resets + AOE), Aphelios (versatilidad de armas).
  - **A-tier:** Twitch (flanco con sigilo + R AOE), Vayne (anti-tank + auto-peel), Tristana (rango + R defensiva).
  - **B-tier:** Xayah (seguridad con R), Sivir (utilidad con R), Kai'Sa (reposicionamiento con R).
  - **C-tier (mal fit):** Ezreal (no aprovecha bien la frontline), Lucian (rango corto), Draven (necesita kills, no DPS sostenido).
- **Cadena crítica de dependencia:** Frontline absorbe -> carry pega -> peel protege al carry. Si un eslabón se rompe, la composición falla.
- **Alineación de escalado:** estas composiciones favorecen late game porque necesitan objetos tanto en frontline como en ADC.

## Implicancias de Draft

- Cuando `teamfight_shape == front_to_back`, el motor debe pesar fuerte `synergy_frontline_comp`, `synergy_peel_comp`, `teamfight_consistency` y `scaling`.
- ADCs con `dependence_on_frontline >= 7` deben recibir **bono** en este arquetipo, no penalización, porque su dependencia está satisfecha.
- ADCs autosuficientes como Ezreal o Lucian no deberían ser recomendación principal en teamfight frontal si hay alternativas mejores, porque no convierten bien la inversión en frontline/peel.
- **Propuesta de peso:** en teamfight frontal, `scaling_fit` sube +0.05 y `blind_pick_safety` baja -0.05.

## Cuándo Importa

- El equipo aliado ya eligió 2+ de: Maokai, Ornn, Sion, Nautilus, Braum, Alistar, Sejuani, Malphite.
- El support aliado es enchanter (Lulu, Janna, Soraka, Nami) y aporta la capa de peel.
- No existe amenaza real de split-push aliado que cambie el plan macro (sin Fiora o Tryndamere side-laneando).

## Advertencias

- El teamfight frontal falla contra poke extremo (Xerath + Jayce) que desgasta la frontline antes del engage.
- Si el enemigo tiene flankers como Zed o Akali con acceso lateral, la backline puede no estar realmente segura.
- En SoloQ requiere coordinación; por eso su fiabilidad cae por debajo de Diamante.

## Claims Extraíbles

- `teamfight_shape == "front_to_back"` + `adc.synergy_frontline_comp >= 8` -> `comp_gap_fill_bonus: +10`
- `teamfight_shape == "front_to_back"` + `adc.teamfight_consistency >= 7` -> `scaling_fit_bonus: +8`
- `teamfight_shape == "front_to_back"` + `adc.dependence_on_frontline >= 7` -> `convert penalty to bonus: +5` (dependencia satisfecha)
- `teamfight_shape == "front_to_back"` + `adc.id in ["Ezreal", "Lucian"]` -> `comp_gap_fill_penalty: -10` (desperdicia la estrategia)

## Campeones / Composiciones Relacionadas

- **Frontline central:** Maokai, Ornn, Sion, Malphite, Sejuani, K'Sante.
- **Peel central:** Lulu, Janna, Braum, Thresh, Nami.
- **Arquetipos que la castigan:** dive (salta la frontline), poke (desgasta desde rango), split-push (evita teamfight).
- **Notas relacionadas:** [adc-jinx-front-to-back](../adcs/adc-jinx-front-to-back.md)

## Notas de Fuente

Teoría fundamental de composiciones en League of Legends. El teamfight frontal es uno de los arquetipos más antiguos y entendidos; esta nota codifica sus implicancias para la selección de ADC en el motor de scoring.
