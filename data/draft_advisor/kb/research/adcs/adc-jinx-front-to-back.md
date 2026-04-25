---
schema_version: "1.0"
kb_version: "1"
id: "adc-jinx-front-to-back"
title: "Jinx in Front-to-Back Compositions"
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

## Summary

Jinx is the premier front-to-back teamfight hypercarry. With rocket launcher range (at max level, 725 range), AOE splash damage, and snowballing resets on kills/assists, she is the ADC that benefits most from traditional front-to-back compositions where a frontline engages and peels while she free-hits from the backline.

## Key Findings

- Jinx's teamfight damage output scales non-linearly with protection: each additional second of uninterrupted auto-attacking in rocket form compounds AOE damage across the entire enemy team.
- Her passive (Get Excited!) converts any kill/assist into a massive movement speed + attack speed steroid, enabling pentakill chains that no other ADC can replicate.
- With 2+ frontline champions AND reliable peel (e.g., Nautilus + Maokai, or Maokai + Lulu), Jinx's theoretical teamfight DPS is the highest among all ADCs.
- Without frontline, Jinx drops from S-tier to C-tier. Her 325 base MS and zero dashes make her a free kill for any diver.

## Draft Implications

- **Pick Jinx when:** Allied team has 2+ frontline members AND at least one peel source (enchanter or CC tank). Enemy team lacks more than one mobile assassin.
- **Avoid Jinx when:** Allied team has no frontline, enemy has multiple divers (Camille + Nocturne, Zed + Vi), or the game is expected to end before 3 items.
- **Scoring impact:** Jinx's `synergy_frontline_comp: 9` and `synergy_peel_comp: 9` already reflect this, but the magnitude of the interaction is larger than the numbers suggest — she goes from unplayable to best-in-class.

## When This Matters

- Allied team has locked in 2+ of: Maokai, Ornn, Sion, Sejuani, Nautilus, Braum, Alistar, Thresh.
- Enemy team has at most 1 dive assassin (manageable with exhaust + peel).
- Game is expected to go 25+ minutes (scaling comp, not early-game-only strategy).

## Caveats

- This analysis assumes competent positioning from the Jinx player. In low elo, even with perfect comp, Jinx may int forward.
- Patch-dependent: if Jinx's items (IE, RFC, Runaan's) are nerfed, the scaling ceiling drops.
- Does not account for specific enemy ADC — lane matchup is analyzed separately.

## Extractable Claims

- `Jinx` + `frontline_count >= 2` + `peel_count >= 1` → `synergy_boost: +15` (beyond base rating)
- `Jinx` + `frontline_count == 0` → `should_not_recommend` unless no alternatives
- `Jinx` + `enemy_dive_count >= 2` → `risk: critical` regardless of allied peel

## Related Champions / Comps

- **Best frontline partners:** Maokai (W root + saplings for vision), Ornn (upgrades + engage), Nautilus (hook + passive root chain)
- **Best peel partners:** Lulu (W polymorph + R knockup), Janna (tornado + R disengage), Braum (passive stun + shield)
- **Worst enemy matchups when unprotected:** Zed, Camille, Nocturne, Vi (all point-click or undodgeable gap closers)

## Source Notes

Expert analysis based on champion kit mechanics, patch 16.7 state, and established draft theory. No specific external source — this is original strategic analysis.
