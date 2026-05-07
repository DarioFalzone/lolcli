---
schema_version: "1.0"
kb_version: "1"
id: "mu-nilah-soraka-vs-caitlyn-nautilus"
title: "Nilah + Soraka contra Caitlyn + Nautilus"
type: "matchup_note"
domain: "draft_advisor"
patch: "16.9"
source_type: "personal_note"
source_url: ""
source_file: ""
created_at: "2026-05-05"
last_reviewed_at: "2026-05-05"
review_status: "reviewed"
confidence: "high"
champions: ["Nilah", "Soraka", "Caitlyn", "Nautilus"]
roles: ["Bot", "Support"]
topics: ["lane_matchup", "counter_pick", "anti_poke", "late_game", "positioning", "matchup"]
tags: ["rango", "prioridad", "hook", "all-in", "scaling"]
derived_from: []
supersedes: []
superseded_by: []
---

## Resumen

Nilah + Soraka no debe salir como primera recomendacion contra Caitlyn + Nautilus. Aunque Nilah pueda estar alta en maestria personal y Soraka amplifique curaciones, la linea queda sin prioridad real: Caitlyn empuja y castiga desde rango, Nautilus amenaza hook/all-in, y Nilah no puede contestar la wave sin exponerse.

## Por Que Es Mala

- **Fase de linea:** Caitlyn tiene rango y prioridad para empujar, tomar placas y controlar arbustos. Nilah necesita entrar al rango de amenaza de Nautilus para farmear o tradear.
- **Soporte aliado:** Soraka sostiene vida, pero no genera suficiente kill pressure para castigar a Caitlyn ni para impedir que Nautilus controle la zona.
- **Macro game:** sin prioridad de bot, el equipo pierde ventanas de crash para dragon, vision e invade. La linea queda jugando reactiva.
- **Late game:** Nilah sufre falta de rango si el enemigo juega front-to-back o zonea con Caitlyn. El sustain no reemplaza DPS seguro desde distancia.

## Regla Para El Motor

- `Nilah + Soraka vs Caitlyn + Nautilus` aplica `score_delta: -35`.
- La recomendacion queda marcada como `fallback_lane_veto` y no puede ser top pick si existe cualquier ADC no vetado.
- La regla general tambien aplica a ADCs de rango muy bajo con support sustain y poca presion contra bully de rango + engage.

## Pickear Nilah Solo Si

- El enemigo no tiene ADC de rango alto con prioridad.
- El soporte aliado puede forzar all-in o negar engage enemigo, por ejemplo Taric/Lulu en contexto correcto.
- El equipo ya tiene dano a distancia desde mid/top y puede jugar sin prioridad temprana de bot.
