---
schema_version: "1.0"
kb_version: "1"
id: "mu-xayah-vs-malphite-tahmkench"
title: "Xayah contra Malphite y Tahm Kench"
type: "matchup_note"
domain: "draft_advisor"
patch: "16.9"
source_type: "personal_note"
source_url: ""
source_file: ""
created_at: "2026-05-05"
last_reviewed_at: "2026-05-05"
review_status: "reviewed"
confidence: "medium"
champions: ["Xayah", "Malphite", "TahmKench"]
roles: ["Bot", "Top", "Support"]
topics: ["anti_dive", "front_to_back", "teamfight", "positioning", "matchup"]
tags: ["R", "plumas", "engage", "warden", "frontline"]
derived_from: []
supersedes: []
superseded_by: []
---

## Resumen

Xayah gana valor contra engage frontal predecible como Malphite y contra frontlines melee como Tahm Kench. El motivo no es que sea el mejor ADC anti-tank, sino que puede negar la ventana de entrada con R, reposicionarse, y castigar el avance enemigo con la E de plumas.

## Por Que Funciona

- **Malphite:** su R marca una ventana clara de all-in. Xayah puede guardar R para esquivar la entrada o para negar el follow-up, y despues usar plumas para rootear a los que entraron.
- **Tahm Kench:** fuerza peleas lentas, frontales y de corto rango. Si Tahm camina hacia Xayah, queda expuesto a zonas de plumas y kite hacia atras.
- **Teamfight:** Xayah juega bien cuando el enemigo debe entrar en linea recta. Las plumas convierten el dive enemigo en una zona de castigo.
- **Macro game:** el valor aparece si el equipo puede pelear ordenado alrededor de objetivos. No alcanza con ganar la reaccion mecanica; hay que preparar posicion de plumas antes de dragon, Baron o torre.

## Limites De La Regla

- No convierte a Xayah en anti-tank premium. Si el problema principal es derretir dos o tres tanques, Vayne/Kog'Maw pueden ser mejores si el draft los protege.
- No compensa una linea perdida contra mucho rango o bully fuerte. Caitlyn, Draven, Sivir o poke pesado siguen siendo escenarios delicados.
- No debe empujar Xayah por encima de la politica ADC central: primero meta fuerte, luego maestria, y dentro de eso fit de draft.

## Regla Para El Motor

- `Xayah vs Malphite` aplica un bonus de matchup por negar engage frontal predecible con R y plumas.
- `Xayah vs TahmKench` aplica un bonus menor por castigar frontlines melee que caminan sobre sus plumas.
- Estos bonos solo mejoran el fit de draft; no son un override de meta ni de maestria personal.
