# Data Source Matrix

This matrix maps every game-data field used by the ADC Draft Advisor to its authoritative source-of-truth, explicitly separating player-facing labels from technical data builds.

| Field / Dataset | Current Value | Current File Location | Current Source | Authoritative Source | Status | Recommended Action |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Live Patch Label** | `16.7` (Conflated) | `champion_base.json`, `app.js` | `champion_base.json` (hardcoded origin string) | Official LoL release notes (e.g., `26.7`) | **CONFLATED** | Expose dual fields in schema: `live_patch_label` vs `static_data_version`. |
| **Static Data Version** | N/A (Missing abstraction) | `champion_base.json` | Riot DDragon API (`api/versions.json`) | Riot DDragon API (e.g., `16.7.1`) | **MISSING** | Explicitly track the build version supplying the JSON geometry. |
| **Champion Roster** | `172` champions | `champion_base.json` | Project-local manual/DDragon snapshot | Riot DDragon (`cdn/[static_data_version]/data/en_US/champion.json`) | **VALID** | Add `CanonicalChampionValidator` to cross-check total count against DDragon. |
| **ADC Roster Count**| `24` ADCs | `adc_profiles.json` | Curated expert tier mapping | Product Definition subset of DDragon | **VALID** | Maintain documented rule over ADC subset. |
| **Priority Profiles**| `41` champions | `priority_profiles.json` | Curated expert impact mapping | Project Definition subset of DDragon | **VALID** | None. |
| **KB Notes Patch** | `16.7`, `*` | `kb/research/.../*.md` Frontmatter | Manual Frontmatter | Official Live Patch Identity | **STALE RULES** | Must refer to `live_patch_label`, not `static_data_version`. |
| **UI Patch Badge** | Dynamically loaded | `index.html` (DOM), `app.js` (JS) | Backend `/health` endpoint | Computed (Tier 1 `champion_base.json`) | **MISLEADING** | Badge must show `live_patch_label`, not `static_data_version`. Add Semantic Validator. |
| **Scoring Weights** | `1.0` Schema | `scoring_weights.json` | Internal curated heuristics | Project Architecture | **VALID** | None. |
| **Draft Taxonomy** | Standard definitions| `kb/taxonomy.json` | Internal contract | Internal Rules | **VALID** | Improve product family guardrails against TFT. |
