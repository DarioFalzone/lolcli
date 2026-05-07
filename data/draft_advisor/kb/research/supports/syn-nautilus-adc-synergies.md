---
schema_version: "1.0"
kb_version: "1"
id: "syn-nautilus-adc-synergies"
title: "Sinergias de Nautilus con campeones ADC"
type: "support_synergy_note"
domain: "draft_advisor"
patch: "16.7"
source_type: "expert_analysis"
source_url: ""
source_file: ""
created_at: "2026-04-08"
last_reviewed_at: "2026-04-08"
review_status: "reviewed"
confidence: "high"
champions: ["Nautilus", "Jinx", "Kaisa", "Aphelios", "Samira", "Draven", "MissFortune", "Ezreal", "Vayne", "KogMaw"]
roles: ["Support", "Bot"]
topics: ["engage_synergy", "synergy", "lane_matchup", "teamfight", "peel_dependency"]
tags: ["support", "engage", "cc_chain", "all_in"]
derived_from: []
supersedes: []
superseded_by: []
---

## Resumen

Nautilus es un support de engage premium con una de las densidades de CC más altas del rol. Q hook + root pasivo + slow de E + R point-click generan una cadena de CC de 3 a 4 segundos sobre un objetivo. Eso lo vuelve ideal para ADCs que necesitan targets quietos para convertir daño, y también le da peel fuerte usando las mismas herramientas.

## Hallazgos Clave

- **Nautilus aporta engage y peel**: a diferencia de Leona, que es más linealmente engage, Nautilus puede usar root pasivo y slow de E de forma defensiva para sacar divers de encima.
- **Tier de sinergia ADC con Nautilus:**
  - **S-tier:** Kai'Sa (follow-up con R al hook), Samira (necesita CC para S-rank), Aphelios (pega libre durante CC), Jinx (hypercarry protegido).
  - **A-tier:** Miss Fortune (R durante CC), Draven (hachas garantizadas durante lockdown), Jhin (follow-up con W).
  - **B-tier:** Ezreal (no necesita tanto engage y desperdicia parte del kit), Vayne (prefiere enchanter para escalar).
  - **C-tier:** Kog'Maw (demasiado frágil para el timing agresivo de Nautilus; Lulu suele ser mejor).
- **La R de Nautilus es de las herramientas más confiables de peel contra asesinos:** es point-click, difícil de esquivar y levanta a quienes estén en la trayectoria.
- **El motor captura parte de esto** con `synergy_engage_support`, pero la doble naturaleza engage/peel merece peso adicional.

## Implicancias de Draft

- Cuando Nautilus es support aliado, el motor debe favorecer ADCs con `synergy_engage_support >= 7`.
- Kai'Sa + Nautilus merece bono específico porque R de Kai'Sa + hook de Nautilus es uno de los combos 2v2 más fuertes.
- Ezreal + Nautilus es un mismatch de draft: Ezreal no necesita tanto engage ni peel, y Nautilus se desperdicia si juega atrás.
- Kog'Maw + Nautilus es subóptimo: Kog'Maw necesita babysitting de enchanter, no un tanque de engage.

## Cuándo Importa

- Nautilus está lockeado como support aliado en los slots 1-4.
- La bot lane enemiga es support mago frágil + ADC de escalado.
- El equipo necesita engage y peel desde un mismo pick de support.

## Advertencias

- Nautilus depende del hook en línea; fallar Q reduce mucho su presión.
- Morgana con E o Sivir con E pueden anular el engage.
- En elo muy alto, los jugadores respetan el rango del hook y reducen su eficacia.

## Claims Extraíbles

- `ally.contains("Nautilus")` + `adc.synergy_engage_support >= 7` -> `ally_synergy_bonus: +8`
- `ally.contains("Nautilus")` + `adc.id == "Kaisa"` -> `ally_synergy_bonus: +12` (sinergia específica de dupla)
- `ally.contains("Nautilus")` + `adc.id == "Ezreal"` -> `ally_synergy_penalty: -5` (mismatch de draft)
- `ally.contains("Nautilus")` + `adc.id == "KogMaw"` -> `ally_synergy_penalty: -8` (prefiere enchanter)

## Campeones / Composiciones Relacionadas

- **Supports parecidos:** Leona (más agresiva, menos peel), Thresh (más versátil, menos CC garantizado), Alistar (tanque similar, combo WQ).
- **Counters enemigos:** Morgana (E bloquea hook), Sivir (E bloquea hook), Ezreal (E esquiva hook).
- **Mejor en composiciones con:** teamfight frontal, composiciones de pick, estrategias de agresión temprana.

## Notas de Fuente

Análisis experto basado en interacciones de kits y teoría establecida de duplas de bot lane. La cadena de CC de Nautilus está bien documentada: Q + pasiva + E + R.
