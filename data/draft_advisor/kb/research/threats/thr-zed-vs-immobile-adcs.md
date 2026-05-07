---
schema_version: "1.0"
kb_version: "1"
id: "thr-zed-vs-immobile-adcs"
title: "Zed como amenaza para ADCs inmóviles"
type: "threat_note"
domain: "draft_advisor"
patch: "*"
source_type: "expert_analysis"
source_url: ""
source_file: ""
created_at: "2026-04-08"
last_reviewed_at: "2026-04-08"
review_status: "reviewed"
confidence: "high"
champions: ["Zed", "Jinx", "KogMaw", "Aphelios", "MissFortune", "Varus", "Ashe", "Jhin", "Xayah", "Ezreal", "Kaisa", "Vayne"]
roles: ["Mid", "Bot"]
topics: ["threat", "anti_dive", "self_sufficiency", "blind_pick_safety", "burst", "positioning"]
tags: ["assassin", "counter", "survival"]
derived_from: []
supersedes: []
superseded_by: []
---

## Resumen

Zed es el arquetipo de asesino anti-ADC. Su combo W+R le da acceso garantizado a targets de backline y su burst puede borrar campeones frágiles en menos de un segundo. La amenaza que representa escala directamente con la inmovilidad del ADC: campeones sin dash, blink o untargetability mueren si no tienen peel cuando Zed tiene R.

## Hallazgos Clave

- **La R de Zed es point-click y lo vuelve no targeteable durante el dash.** El kiteo no impide la entrada inicial; la supervivencia del ADC depende de herramientas post-R.
- **Tier de supervivencia ADC contra Zed:**
  - **Puede sobrevivir solo:** Ezreal (blink con E), Xayah (R no targeteable), Kai'Sa (R + E con invisibilidad), Tristana (R knockback), Vayne (R+Q con invisibilidad).
  - **Necesita peel del equipo:** Jinx, Jhin, Ashe, Miss Fortune, Sivir, Senna.
  - **Muere si queda expuesto:** Kog'Maw, Aphelios, Varus, Draven si está atrapado cazando hachas.
- **El motor ya penaliza ADCs inmóviles** cuando `enemy.has_burst` mediante `self_peel` y `mobility`, pero la amenaza específica de Zed es más fuerte que el burst genérico por la R no targeteable.
- **El counterplay por ítems** como Zhonya o Ángel Guardián compra tiempo, pero no elimina el control de zona: Zed obliga al ADC a jugar más atrás y reduce su aporte de daño.

## Implicancias de Draft

- Si Zed está en el equipo enemigo, el motor debe preferir ADCs con `self_peel >= 6` y `mobility >= 6`.
- Kog'Maw, Aphelios y Varus deben recibir una penalización fuerte en `enemy_matchup` porque están en `worst_into` contra Zed.
- `blind_pick_safety` debe pesar más para ADCs inmóviles cuando el draft tiene información parcial, porque Zed es un mid común que puede aparecer después.

## Cuándo Importa

- El mid enemigo es Zed, confirmado o muy probable.
- El equipo enemigo tiene 2+ amenazas de asesinato, por ejemplo Zed + Nocturne o Zed + Camille.
- Tu equipo no tiene exhaust confiable ni CC dirigido para sacar a Zed del ADC.

## Advertencias

- En elos bajos, los Zed pueden no ejecutar el combo completo y la amenaza real baja.
- Si el support aliado es Lulu o Janna con exhaust, la amenaza se mitiga parcialmente, pero no desaparece.
- Esta nota es agnóstica de parche (`*`) porque la amenaza central del kit de Zed no cambia entre parches; cambian los números.

## Claims Extraíbles

- `enemy.contains("Zed")` + `adc.self_peel <= 4` -> `enemy_matchup_penalty: -15`
- `enemy.contains("Zed")` + `adc.mobility <= 3` -> `enemy_matchup_penalty: -10` (se acumula con la anterior)
- `enemy.contains("Zed")` + `adc.id in ["KogMaw", "Aphelios", "Varus"]` -> `should_not_recommend` salvo que el equipo tenga Lulu/Janna + exhaust
- `enemy.contains("Zed")` + `adc.id in ["Ezreal", "Xayah", "Kaisa"]` -> `enemy_matchup_bonus: +10`

## Campeones / Composiciones Relacionadas

- **Amenazas parecidas:** Akali (asesina sostenida), LeBlanc (mago asesino de burst), Fizz (E no targeteable), Katarina (resets).
- **Counters por peel:** Lulu (W polymorph corta combo), Janna (R disengage), exhaust (reduce burst).
- **Counters por ítems:** Zhonya (stasis), Ángel Guardián (revive con cooldown largo), Arcoescudo Inmortal (escudo al borde de muerte).

## Notas de Fuente

Teoría central de draft: la interacción entre la R de Zed y la movilidad del ADC es conocimiento fundamental de League of Legends. Esta nota lo codifica como modelo de amenaza estructurado para el motor de recomendaciones.
