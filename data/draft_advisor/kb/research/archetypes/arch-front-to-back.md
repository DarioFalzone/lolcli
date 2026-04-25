---
schema_version: "1.0"
kb_version: "1"
id: "arch-front-to-back"
title: "Front-to-Back Teamfight Archetype"
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

## Summary

Front-to-back is the most ADC-centric teamfight archetype. The team's frontline engages and absorbs enemy cooldowns while peelers protect the backline carry, who outputs maximum sustained DPS from safety. This is the composition where ADC champion selection matters most — the wrong ADC in a front-to-back comp wastes the entire team's strategy.

## Key Findings

- **Defining conditions for front-to-back:**
  1. Allied team has 2+ members who can effectively frontline (tanks, bruisers with engage)
  2. Allied team has at least 1 reliable peel source (enchanter, CC support, or peeling tank)
  3. Allied win condition is "protect the carry" — not split-push, not pick, not early-game snowball
- **ADC ranking in front-to-back:**
  - **S-tier:** Kog'Maw (highest DPS if protected), Jinx (resets + AOE), Aphelios (weapon versatility)
  - **A-tier:** Twitch (stealth flank + R AOE), Vayne (tank shred + self-peel), Tristana (range + R self-peel)
  - **B-tier:** Xayah (R safety), Sivir (R utility), Kai'Sa (R reposition)
  - **C-tier (poor fit):** Ezreal (doesn't utilize frontline well), Lucian (short range wastes frontline), Draven (needs kills, not sustained DPS)
- **The critical dependency chain:** Frontline absorbs → Carry DPS's → Peel protects carry. If any link breaks, the comp fails.
- **Scaling alignment:** Front-to-back comps inherently favor late game because they require items on both frontline and ADC to function.

## Draft Implications

- When `teamfight_shape == front_to_back`, the scoring engine should heavily weight `synergy_frontline_comp`, `synergy_peel_comp`, `teamfight_consistency`, and `scaling`.
- ADCs with `dependence_on_frontline >= 7` should get a **bonus** in this archetype (not a penalty) because their dependency is being satisfied.
- Conversely, self-sufficient ADCs (Ezreal, Lucian) should not be recommended in front-to-back comps because they waste the team's investment in frontline/peel.
- **Weight adjustment proposal:** In front-to-back, `scaling_fit` weight should increase by +0.05, `blind_pick_safety` should decrease by -0.05.

## When This Matters

- Allied team has locked in 2+ of: Maokai, Ornn, Sion, Nautilus, Braum, Alistar, Sejuani, Malphite.
- Allied support is an enchanter (Lulu, Janna, Soraka, Nami) providing the peel layer.
- No split-push threat exists in the allied team (no Fiora, no Tryndamere side-laning).

## Caveats

- Front-to-back fails against extreme poke (Xerath + Jayce) that chips the frontline before engagement.
- If enemy has flankers (Zed, Akali side-access), the backline may not be truly safe regardless of frontline.
- In solo queue, front-to-back requires team coordination that may not exist — this reduces its reliability below Diamond.

## Extractable Claims

- `teamfight_shape == "front_to_back"` + `adc.synergy_frontline_comp >= 8` → `comp_gap_fill_bonus: +10`
- `teamfight_shape == "front_to_back"` + `adc.teamfight_consistency >= 7` → `scaling_fit_bonus: +8`
- `teamfight_shape == "front_to_back"` + `adc.dependence_on_frontline >= 7` → `convert penalty to bonus: +5` (dependency satisfied)
- `teamfight_shape == "front_to_back"` + `adc.id in ["Ezreal", "Lucian"]` → `comp_gap_fill_penalty: -10` (wastes comp strategy)

## Related Champions / Comps

- **Core frontline champions:** Maokai, Ornn, Sion, Malphite, Sejuani, K'Sante
- **Core peel champions:** Lulu, Janna, Braum, Thresh, Nami
- **Counter archetypes:** Dive comps (bypass frontline), poke comps (chip from range), split-push (avoid teamfight entirely)
- **Related notes:** [adc-jinx-front-to-back](adc-jinx-front-to-back.md)

## Source Notes

Fundamental League of Legends comp theory. Front-to-back is the oldest and most well-understood teamfight archetype. This note codifies the ADC selection implications for the scoring engine.
