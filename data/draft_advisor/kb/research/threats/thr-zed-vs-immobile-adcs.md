---
schema_version: "1.0"
kb_version: "1"
id: "thr-zed-vs-immobile-adcs"
title: "Zed as a Threat to Immobile ADCs"
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

## Summary

Zed is the archetype ADC-killer assassin. His W+R combo provides guaranteed access to any backline target, and his burst combo deletes squishies in < 1 second. The threat level Zed poses to ADCs is directly proportional to their immobility — champions without dashes, blinks, or untargetability frames are essentially dead on R cooldown.

## Key Findings

- **Zed R is point-click and untargetable during the dash.** No amount of kiting skill prevents the initial gap close. The ADC's survival depends entirely on post-R tools.
- **ADC survival tier vs Zed:**
  - **Can self-survive:** Ezreal (E blink), Xayah (R untargetable), Kai'Sa (R + E stealth), Tristana (R knockback), Vayne (R+Q stealth)
  - **Needs team peel:** Jinx, Jhin, Ashe, Miss Fortune, Sivir, Senna
  - **Dead on sight:** Kog'Maw, Aphelios, Varus, Draven (if axes are mid-catch)
- **The scoring engine already penalizes immobile ADCs** when `enemy.has_burst` via the `self_peel` and `mobility` factors, but the **Zed-specific threat** is more acute than generic burst because of the untargetable R dash.
- **Itemization counterplay** (Zhonya's, Guardian Angel) delays death by 2.5s but does not prevent the zone control — Zed forces ADC to play 600 units further back, reducing their damage contribution.

## Draft Implications

- When Zed is picked on enemy team, the recommendation engine should strongly prefer ADCs with `self_peel >= 6` and `mobility >= 6`.
- Kog'Maw, Aphelios, and Varus should have their enemy_matchup score heavily penalized (they are in `worst_into` for Zed).
- The `blind_pick_safety` score for immobile ADCs should carry extra weight when draft information is partial (Zed is a common mid pick that may not be visible early).

## When This Matters

- Enemy mid laner is Zed (confirmed or suspected).
- Enemy team has 2+ assassination threats (Zed + Nocturne, Zed + Camille).
- Your team lacks reliable exhaust or targeted CC to peel Zed off ADC.

## Caveats

- In lower elos, Zed players may not execute the full combo, reducing the threat.
- If allied support is Lulu/Janna with exhaust, the threat is partially mitigated but not eliminated.
- This note is patch-agnostic (`*`) because Zed's fundamental kit threat doesn't change between patches — only numbers shift.

## Extractable Claims

- `enemy.contains("Zed")` + `adc.self_peel <= 4` → `enemy_matchup_penalty: -15`
- `enemy.contains("Zed")` + `adc.mobility <= 3` → `enemy_matchup_penalty: -10` (stacks with above)
- `enemy.contains("Zed")` + `adc.id in ["KogMaw", "Aphelios", "Varus"]` → `should_not_recommend` unless team has Lulu/Janna + exhaust
- `enemy.contains("Zed")` + `adc.id in ["Ezreal", "Xayah", "Kaisa"]` → `enemy_matchup_bonus: +10`

## Related Champions / Comps

- **Similar threats:** Akali (sustain assassin), LeBlanc (burst mage assassin), Fizz (E untargetable), Katarina (resets)
- **Peel counters:** Lulu (W polymorph stops combo), Janna (R disengage), exhaust (reduces burst by 40%)
- **Item counters:** Zhonya's (2.5s stasis), Guardian Angel (revive but 5min CD), Immortal Shieldbow (shield on lethal)

## Source Notes

Core draft theory — Zed's R interaction with ADC mobility is fundamental League of Legends knowledge. This analysis codifies it into a structured threat model for the recommendation engine.
