# Sanitization Audit Report

## Executive Summary
A comprehensive data provenance and trust audit was performed against the ADC Draft Advisor system. Its primary goal was to detect data drift, stale versioning, incorrect taxonomy, specific failure modes (LoL / TFT cross-contamination, Riot docs examples copied over), and any unsupported UI claims.

**The audit confirms a major semantic source-of-truth vulnerability:** Version Concept Conflation. 
While the local system state cleanly tracks Data Dragon endpoints without corruption, it erroneously presents the technical data build version (`16.7`) to the user as if it were the official player-facing Live Patch (`26.7`). The system is NOT pristine; it lacks the semantic abstraction required to deliver a trustworthy expert-level UI.

## Exact Mismatches & Conflations Found
1. **Semantic Version Conflation (High Risk)**: The UI badge and KB frontmatter are directly populated from a singular `"patch": "16.7"` string. This is misleading. Official Riot sources expose two distinct models:
   - *Player-facing live patch label* (e.g., `26.7`)
   - *Data Dragon static asset version* (e.g., `16.7.1`)
2. **TFT & Product Mixups**: In the adjacent repository folder `proyecto lol/lol_patch_notes.json`, a mix-up with Spanish localized patch versions (using non-standard `25.17` identifiers) and TFT cross-contamination was found. While disconnected from the ADC engine, it proves the imminent danger of failing to separate game-type semantics.

## Source-of-Truth Decisions & Abstractions Required
1. **Dual-Version Modeling**: Base schema must be updated to explicitly decouple `live_patch_label` (e.g. `"26.7"`) and `static_data_version` (e.g. `"16.7.1"`).
2. **UI Integrity**: The UI patch badge must prioritize presenting the `live_patch_label`. Displaying the DDragon asset version to users compromises trust.
3. **Champion Roster Count**: DDragon `champion.json` enforces `172`.
4. **ADC / Priority Rosters**: Computed strictly based on internally curated rule logic applied to the base DDragon roster (`24` and `41` respectively) mapped in tier-2 and tier-3 structures.

## High-Risk Trust Issues & Unresolved Ambiguities
- **Misrepresented Data Context**: Stating that a Jinx synergy note is valid for patch "16.7" when the user is playing on "26.7" destroys the credibility of the Draft Advisor. The metadata schemas must migrate to the player-facing `live_patch_label`.
- **Silent Data Drift Possibility**: Loading `champion_base.json` manually during engine setup inherently trusts the file payload. Without guardrails blocking TFT data or static versions slipping into live inputs, the backend will quietly push misleading contexts.
