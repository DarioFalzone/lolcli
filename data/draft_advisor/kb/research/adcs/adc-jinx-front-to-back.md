---
schema_version: "1.0"
kb_version: "1"
id: "adc-jinx-front-to-back"
title: "Jinx en composiciones de teamfight frontal"
type: "adc_champion_note"
domain: "draft_advisor"
patch: "16.7"
source_type: "expert_analysis"
source_url: ""
source_file: ""
created_at: "2026-04-08"
last_reviewed_at: "2026-04-08"
review_status: "reviewed"
confidence: "high"
champions: ["Jinx", "Lulu", "Nautilus", "Maokai", "Braum", "Janna", "Thresh"]
roles: ["Bot"]
topics: ["front_to_back", "hypercarry", "peel_dependency", "scaling", "teamfight", "frontline_dependency"]
tags: ["positioning", "synergy", "late_game"]
derived_from: []
supersedes: []
superseded_by: []
---

## Resumen

Jinx es una hypercarry premium para teamfight frontal. Con el rango del lanzacohetes, daño AOE y resets de velocidad al participar en kills, es uno de los ADCs que más aprovecha una composición donde la frontline inicia y peelea mientras ella pega desde backline.

## Hallazgos Clave

- El daño de Jinx en teamfight escala de forma no lineal con la protección: cada segundo extra de autos ininterrumpidos con cohetes multiplica daño AOE sobre todo el equipo enemigo.
- Su pasiva convierte cualquier kill o asistencia en una ventana enorme de velocidad de movimiento y velocidad de ataque, habilitando cadenas de resets que pocos ADCs pueden igualar.
- Con 2+ campeones de frontline y peel confiable (por ejemplo Nautilus + Maokai, o Maokai + Lulu), su DPS teórico en teamfight está entre los más altos del rol.
- Sin frontline, Jinx cae de S-tier a C-tier. Su velocidad base baja y ausencia de dash la dejan expuesta contra cualquier diver.

## Implicancias de Draft

- **Elegí Jinx cuando:** tu equipo tiene 2+ fuentes de frontline y al menos una fuente de peel (enchanter o tanque con CC). El enemigo no tiene más de un asesino móvil.
- **Evitá Jinx cuando:** tu equipo no tiene frontline, el enemigo tiene múltiples divers (Camille + Nocturne, Zed + Vi), o la partida parece resolverse antes de 3 ítems.
- **Impacto de scoring:** `synergy_frontline_comp: 9` y `synergy_peel_comp: 9` ya reflejan el patrón, pero la magnitud real es mayor: Jinx pasa de muy castigable a win condition central.

## Cuándo Importa

- El equipo aliado ya eligió 2+ de: Maokai, Ornn, Sion, Sejuani, Nautilus, Braum, Alistar, Thresh.
- El enemigo tiene como máximo 1 asesino de dive, manejable con exhaust + peel.
- La partida apunta a 25+ minutos, con composición de escalado y no solo snowball temprano.

## Advertencias

- El análisis asume posicionamiento competente. En elos bajos, Jinx puede regalarse incluso con composición perfecta.
- Depende de parche: si los ítems de Jinx bajan mucho, su techo de escalado también baja.
- No evalúa matchup específico contra el ADC enemigo; eso se analiza en otra capa.

## Claims Extraíbles

- `Jinx` + `frontline_count >= 2` + `peel_count >= 1` -> `synergy_boost: +15` (más allá del rating base)
- `Jinx` + `frontline_count == 0` -> `should_not_recommend` salvo que no haya alternativas
- `Jinx` + `enemy_dive_count >= 2` -> `risk: critical` incluso con peel aliado

## Campeones / Composiciones Relacionadas

- **Mejores socios de frontline:** Maokai (W root + saplings para visión), Ornn (mejoras + engage), Nautilus (hook + cadena de root pasivo).
- **Mejores socios de peel:** Lulu (W polymorph + R knockup), Janna (tornado + R disengage), Braum (stun pasivo + escudo).
- **Peores amenazas si no está protegida:** Zed, Camille, Nocturne, Vi.

## Notas de Fuente

Análisis experto basado en mecánicas del kit, estado de parche 16.7 y teoría de draft establecida. No usa una fuente externa específica; es análisis estratégico original.
