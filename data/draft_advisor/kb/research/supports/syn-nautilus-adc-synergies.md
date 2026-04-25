---
schema_version: "1.0"
kb_version: "1"
id: "syn-nautilus-adc-synergies"
title: "Nautilus Synergies with ADC Champions"
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

## Summary

Nautilus is a premier engage support with the highest CC density of any support champion. His hook (Q) + passive root + E slow + R point-click knockup provides a guaranteed 3-4 second CC chain on a single target. This makes him the ideal support for ADCs who need targets locked down to deal damage, while also providing strong peel through the same CC tools.

## Key Findings

- **Nautilus provides both engage AND peel** — unlike Leona who is primarily engage, Nautilus's passive auto-root and E slow can be used defensively to peel divers.
- **ADC synergy tier with Nautilus:**
  - **S-tier:** Kai'Sa (R follow-up on hook), Samira (needs CC for S-rank), Aphelios (free-hit during CC), Jinx (protected hypercarry)
  - **A-tier:** Miss Fortune (R during CC), Draven (guaranteed axes during lockdown), Jhin (W follow-up CC chain)
  - **B-tier:** Ezreal (doesn't need the engage, wastes Nautilus's strengths), Vayne (prefers enchanter for scaling)
  - **C-tier:** Kog'Maw (too fragile for Nautilus's aggressive engage timing — Lulu is strictly better)
- **Nautilus's R is the most reliable ADC-peel tool against assassins** — it's point-click, can't be dodged, and knocks up everyone in the path.
- **The scoring engine captures this** via `synergy_engage_support` but misses the dual-nature: Nautilus is as good at peeling as engaging.

## Draft Implications

- When Nautilus is an allied support, the engine should favor ADCs with `synergy_engage_support >= 7`.
- Specifically, Kai'Sa + Nautilus should receive a synergy bonus because Kai'Sa R + Nautilus hook is one of the strongest 2v2 combos in the game.
- Ezreal + Nautilus is a draft mismatch: Ezreal doesn't need engage or peel, and Nautilus is wasted sitting back.
- Kog'Maw + Nautilus is suboptimal — Kog'Maw needs a babysitting enchanter, not an engage tank.

## When This Matters

- Nautilus is locked in as allied support (slots 1-4).
- Enemy bot lane is a squishy mage support + scaling ADC (Nautilus punishes these lanes hardest).
- Team needs both engage and peel from a single support pick.

## Caveats

- Nautilus is hook-reliant in lane — missing Q significantly reduces his pressure.
- Against Morgana (E spell shield) or Sivir (E spell shield), Nautilus's engage is nullified.
- In very high elo, players position to avoid Nautilus hook range, reducing his effectiveness.

## Extractable Claims

- `ally.contains("Nautilus")` + `adc.synergy_engage_support >= 7` → `ally_synergy_bonus: +8`
- `ally.contains("Nautilus")` + `adc.id == "Kaisa"` → `ally_synergy_bonus: +12` (specific duo synergy)
- `ally.contains("Nautilus")` + `adc.id == "Ezreal"` → `ally_synergy_penalty: -5` (draft mismatch)
- `ally.contains("Nautilus")` + `adc.id == "KogMaw"` → `ally_synergy_penalty: -8` (wants enchanter)

## Related Champions / Comps

- **Similar supports:** Leona (more aggressive, less peel), Thresh (more versatile, less guaranteed CC), Alistar (similar tankiness, WQ combo)
- **Enemy counters:** Morgana (E blocks hook), Sivir (E blocks hook), Ezreal (E dodges hook)
- **Best in comps with:** Front-to-back teamfight, pick comps, early-aggression strategies

## Source Notes

Expert analysis based on champion kit interactions and established bot lane duo theory. Nautilus's CC chain math (Q 1s + passive 0.5-1.5s + E slow + R 1s knockup) is well-documented in LoL Wiki.
