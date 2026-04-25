# Remediation & Sanitization Plan

## 1. Structural Schema Fixes (Dual-Version Modeling)
The immediate priority is to break the conflation between technical asset versions and player-facing reality.
- **Action**: Update `champion_base.json` schema to require two distinct fields: `live_patch_label` (e.g., `"26.7"`) and `static_data_version` (e.g., `"16.7.1"`).
- **Action**: Retrofit `kb_schemas.py` and existing KB notes to map to `live_patch_label`.
- **Action**: Update the backend `/health` endpoint to supply both versions.

## 2. Files to Deprecate / Mark Stale
- Explicitly deprecate reliance on external web scrapers (like `notas_parche/*`) that exhibit severe product contamination (TFT overlap) and mismatch mapping (e.g., `25.17`).

## 3. Architecture Upgrades (Validation Guardrails)
To guarantee the system stays semantically clear and synchronized, four critical validation checkpoints will be built natively into the pipeline:

1. **`SemanticVersionValidator` (Replaces `PatchResolver`)**: 
   A strict guardrail that asserts `live_patch_label` != `static_data_version`. If a curator attempts to input a DDragon major version (e.g., `16.x`) as the player-facing patch in a year where `26.x` is live, the validation suite crashes to protect UI integrity.
2. **`CanonicalChampionValidator`**:
   Cross-checks local data payload length and identifier keys against the specific DDragon realm identified by `static_data_version`. Throws schema violations if any ID in `champion_base.json` is missing or maliciously inserted.
3. **`DataFreshnessValidator`**:
   Iterates over KB research artifacts. Any KB document with a `live_patch_label` tagged strictly older than a configurable tolerance (e.g., `> 2` major patches delta) produces a stale-warning flagged for manual curation review.
4. **`ProductFamilyValidator`**:
   A regex constraint filter protecting against LoL vs TFT mixups within automated pipeline ingestions. Blocks ingestion of external data containing "TFT" references or overlapping Set identifiers.

## 4. Testing & Wiring
- Refactor `app.js` to intelligently display the `live_patch_label` in the patch badge, restoring user credibility.
- Deploy a targeted test suite injecting known conflated datasets (e.g., setting `live=16.7` and `static=16.7.1`) to ensure the `SemanticVersionValidator` aggressively handles the failure mode.
