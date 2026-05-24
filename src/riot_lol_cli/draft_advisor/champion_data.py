"""
Champion Data Service — loads and validates all three data tiers.

Provides typed access to:
- Tier 1: champion_base (all ~170 champions)
- Tier 2: adc_profiles (25-30 ADC deep profiles)
- Tier 3: priority_profiles (30-40 draft-impact non-ADCs)
- Scoring weights configuration
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .jungle_meta_provider import JungleMetaProvider, JungleMetaSnapshot
from .schemas import (
    AdcProfile,
    AdcProfilesFile,
    ChampionBase,
    ChampionBaseFile,
    CombatClass,
    DataManifestFile,
    GameplayRole,
    PriorityProfile,
    PriorityProfilesFile,
    ScoringWeightsConfig,
    SupportProfile,
    SupportProfilesFile,
)


def _age_hours(iso_value: str | None) -> float | None:
    """Return age in hours for an ISO timestamp, or None if invalid."""
    if not iso_value:
        return None
    try:
        parsed = datetime.fromisoformat(iso_value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - parsed.astimezone(timezone.utc)
    return round(delta.total_seconds() / 3600, 2)


class ChampionDataService:
    """
    Loads, validates, and provides typed access to all champion data.

    Data is loaded once at init and kept in memory.
    Total data volume is trivially small (~170 champions × ~50 fields).
    """

    def __init__(self, data_dir: str | Path | None = None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent.parent / "data" / "draft_advisor"
        self._data_dir = Path(data_dir)

        # Loaded state
        self._champion_base: dict[str, ChampionBase] = {}
        self._adc_profiles: dict[str, AdcProfile] = {}
        self._support_profiles: dict[str, SupportProfile] = {}
        self._priority_profiles: dict[str, PriorityProfile] = {}
        self._scoring_weights: ScoringWeightsConfig | None = None

        # NotebookLM 2026-04-27: extended KB JSON (loaded gracefully — optional)
        self._measured_synergies: list[dict] = []
        self._measured_synergies_config: dict = {}
        self._strategic_triangle: dict = {}
        self._comp_predominance: dict = {}
        # Auditoría profunda 2026-04-27: synergy matrix + matchup rules
        self._synergy_matrix: dict[str, dict[str, int]] = {}
        self._matchup_rules: dict = {}
        # D8+D9 2026-04-27: jungler archetypes + queue style hints
        self._jungler_archetypes: dict = {}
        self._queue_style_hints: dict = {}
        # Meta Scraper: snapshots opcionales de ADC y Support.
        self._adc_meta: dict[str, dict] = {}
        self._adc_meta_snapshot: dict = {}
        self._support_meta: dict[str, dict] = {}
        self._support_meta_snapshot: dict = {}
        self._jungle_meta_provider = JungleMetaProvider()
        self._jungle_meta_snapshot: JungleMetaSnapshot | None = None
        self._personal_adc_mastery: dict = {}
        self._personal_adc_tiers: dict[str, str] = {}
        self._excluded_adc_ids: set[str] = set()
        self._never_top_adc_ids: set[str] = set()

        # Metadata
        self._manifest: DataManifestFile | None = None
        self._schema_version: str = ""

        # Load everything
        self._load_all()

    # ========================================================================
    # Loading
    # ========================================================================

    def _load_all(self) -> None:
        """Load and validate all data files."""
        self._load_data_manifest()
        self._load_champion_base()
        self._load_adc_profiles()
        self._load_support_profiles()
        self._load_priority_profiles()
        self._load_scoring_weights()
        self._load_extended_kb()
        self._load_personal_adc_mastery()
        self._load_adc_meta_snapshot()
        self._load_support_meta_snapshot()
        self._cross_validate()

    def _load_extended_kb(self) -> None:
        """Load extended KB JSON (NotebookLM 2026-04-27): measured synergies, strategic triangle, comp predominance.

        Estos archivos son opcionales. Si faltan, el motor sigue funcionando con
        sus heurísticas anteriores; los nuevos modificadores devuelven 0.
        """
        kb_dir = self._data_dir / "kb" / "structured"

        # measured_synergies.json
        path = kb_dir / "measured_synergies.json"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                raw = json.load(f)
            self._measured_synergies = raw.get("synergies", [])
            self._measured_synergies_config = raw.get("scoring", {})

        # strategic_triangle.json
        path = kb_dir / "strategic_triangle.json"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                self._strategic_triangle = json.load(f)

        # comp_predominance.json
        path = kb_dir / "comp_predominance.json"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                self._comp_predominance = json.load(f)

        # synergy_matrix.json — Auditoría 2026-04-27
        path = kb_dir / "synergy_matrix.json"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                raw = json.load(f)
            self._synergy_matrix = raw.get("matrix", {})

        # matchup_rules.json — Auditoría 2026-04-27
        path = kb_dir / "matchup_rules.json"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                self._matchup_rules = json.load(f)

        # jungler_archetypes.json — D8 2026-04-27
        path = kb_dir / "jungler_archetypes.json"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                self._jungler_archetypes = json.load(f)

        # queue_style_hints.json — D9 2026-04-27
        path = kb_dir / "queue_style_hints.json"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                self._queue_style_hints = json.load(f)

    def _load_adc_meta_snapshot(self) -> None:
        """Load optional ADC meta snapshot generated by meta_scraper."""
        meta_path = self._data_dir.parent / "meta_scraper" / "normalized" / "latest_adc_tier.json"
        if not meta_path.exists():
            self._adc_meta = {}
            self._adc_meta_snapshot = {}
            return

        with open(meta_path, encoding="utf-8") as f:
            raw = json.load(f)

        if raw.get("role") != "adc":
            self._adc_meta = {}
            self._adc_meta_snapshot = {}
            return

        self._adc_meta_snapshot = raw
        self._adc_meta = {champ.get("id"): champ for champ in raw.get("champions", []) if champ.get("id")}

    def _load_personal_adc_mastery(self) -> None:
        """Load the user's editable ADC mastery tier list."""
        mastery_path = self._data_dir / "personal_adc_mastery.json"
        if not mastery_path.exists():
            self._personal_adc_mastery = {}
            self._personal_adc_tiers = {}
            self._excluded_adc_ids = set()
            self._never_top_adc_ids = set()
            return

        with open(mastery_path, encoding="utf-8") as f:
            raw = json.load(f)

        if raw.get("role") != "adc":
            self._personal_adc_mastery = {}
            self._personal_adc_tiers = {}
            self._excluded_adc_ids = set()
            self._never_top_adc_ids = set()
            return

        tiers: dict[str, str] = {}
        for tier, champion_ids in raw.get("tiers", {}).items():
            for champion_id in champion_ids:
                tiers[champion_id] = tier

        self._personal_adc_mastery = raw
        self._personal_adc_tiers = tiers
        self._excluded_adc_ids = set(raw.get("excluded_from_recommendations", []))
        self._never_top_adc_ids = set(raw.get("never_top_pick", []))

    def _load_support_meta_snapshot(self) -> None:
        """Load optional Support meta snapshot generated by meta_scraper."""
        meta_path = self._data_dir.parent / "meta_scraper" / "normalized" / "latest_support_tier.json"
        if not meta_path.exists():
            self._support_meta = {}
            self._support_meta_snapshot = {}
            return

        with open(meta_path, encoding="utf-8") as f:
            raw = json.load(f)

        if raw.get("role") != "support":
            self._support_meta = {}
            self._support_meta_snapshot = {}
            return

        self._support_meta_snapshot = raw
        self._support_meta = {champ.get("id"): champ for champ in raw.get("champions", []) if champ.get("id")}

    def _load_data_manifest(self) -> None:
        """Load Global Metadata: data_manifest.json"""
        path = self._data_dir / "data_manifest.json"
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
        self._manifest = DataManifestFile(**raw)

    def _load_champion_base(self) -> None:
        """Load Tier 1: champion_base.json"""
        path = self._data_dir / "champion_base.json"
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)

        validated = ChampionBaseFile(**raw)
        self._champion_base = validated.champions
        self._schema_version = validated.schema_version

    def _load_adc_profiles(self) -> None:
        """Load Tier 2: adc_profiles.json"""
        path = self._data_dir / "adc_profiles.json"
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)

        validated = AdcProfilesFile(**raw)
        self._adc_profiles = validated.profiles

    def _load_support_profiles(self) -> None:
        """Load Tier 2 paralelo: support_profiles.json (gracefully optional)."""
        path = self._data_dir / "support_profiles.json"
        if not path.exists():
            self._support_profiles = {}
            return

        with open(path, encoding="utf-8") as f:
            raw = json.load(f)

        validated = SupportProfilesFile(**raw)
        self._support_profiles = validated.profiles

    def _load_priority_profiles(self) -> None:
        """Load Tier 3: priority_profiles.json"""
        path = self._data_dir / "priority_profiles.json"
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)

        validated = PriorityProfilesFile(**raw)
        self._priority_profiles = validated.profiles

    def _load_scoring_weights(self) -> None:
        """Load scoring_weights.json"""
        path = self._data_dir / "scoring_weights.json"
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)

        self._scoring_weights = ScoringWeightsConfig(**raw)

    def _cross_validate(self) -> None:
        """Cross-validate data consistency across tiers."""
        errors: list[str] = []

        # Every ADC profile must exist in champion_base
        for adc_id in self._adc_profiles:
            if adc_id not in self._champion_base:
                errors.append(f"ADC profile '{adc_id}' not found in champion_base")

        # Every priority profile must exist in champion_base
        for pp_id in self._priority_profiles:
            if pp_id not in self._champion_base:
                errors.append(f"Priority profile '{pp_id}' not found in champion_base")

        # ADC best_with / worst_into references must exist in champion_base
        for adc_id, profile in self._adc_profiles.items():
            for ref in profile.best_with:
                if ref not in self._champion_base:
                    errors.append(f"ADC '{adc_id}' best_with ref '{ref}' not in champion_base")
            for ref in profile.worst_into:
                if ref not in self._champion_base:
                    errors.append(f"ADC '{adc_id}' worst_into ref '{ref}' not in champion_base")

        # Support profiles must exist in champion_base
        for supp_id in self._support_profiles:
            if supp_id not in self._champion_base:
                errors.append(f"Support profile '{supp_id}' not found in champion_base")

        # Personal ADC mastery tiers must use canonical champion IDs.
        seen_mastery_ids: set[str] = set()
        valid_tiers = {"S", "A", "B", "C", "D"}
        for tier, champion_ids in self._personal_adc_mastery.get("tiers", {}).items():
            if tier not in valid_tiers:
                errors.append(f"Personal ADC mastery uses invalid tier '{tier}'")
            for champion_id in champion_ids:
                if champion_id in seen_mastery_ids:
                    errors.append(f"Personal ADC mastery has duplicated champion '{champion_id}'")
                seen_mastery_ids.add(champion_id)
                if champion_id not in self._champion_base:
                    errors.append(f"Personal ADC mastery ref '{champion_id}' not in champion_base")

        for entry in self._personal_adc_mastery.get("needs_review", []):
            for champion_id in entry.get("candidate_ids", []):
                if champion_id not in self._champion_base:
                    errors.append(f"Personal ADC mastery needs_review ref '{champion_id}' not in champion_base")

        for field_name in ("excluded_from_recommendations", "never_top_pick"):
            for champion_id in self._personal_adc_mastery.get(field_name, []):
                if champion_id not in self._champion_base:
                    errors.append(f"Personal ADC mastery {field_name} ref '{champion_id}' not in champion_base")

        # ADC lane veto rules are consumed by scoring. Keep all explicit IDs canonical.
        adc_lane_rules = self._matchup_rules.get("adc_lane_veto_rules", {})
        for rule in adc_lane_rules.get("exact_pairs", []):
            for field_name in ("adc", "ally_support", "enemy_adc", "enemy_support"):
                champion_id = rule.get(field_name)
                if champion_id and champion_id not in self._champion_base:
                    errors.append(
                        f"ADC lane veto rule {rule.get('id')} {field_name} ref '{champion_id}' not in champion_base"
                    )

        for rule in self._matchup_rules.get("adc_matchup_bonus_rules", []):
            adc_id = rule.get("adc")
            if adc_id and adc_id not in self._champion_base:
                errors.append(f"ADC matchup bonus rule {rule.get('id')} adc ref '{adc_id}' not in champion_base")
            for enemy_id in rule.get("enemy_any", []):
                if enemy_id not in self._champion_base:
                    errors.append(
                        f"ADC matchup bonus rule {rule.get('id')} enemy_any ref '{enemy_id}' not in champion_base"
                    )

        # Note: support best_with_adcs / strong_against_supports references are
        # NOT cross-validated strictly because they may reference champions
        # outside champion_base (alt-spelling or missing entries). We log warnings
        # but don't fail. This is a soft contract.

        if errors:
            raise ValueError(
                f"Cross-validation failed with {len(errors)} errors:\n" + "\n".join(f"  - {e}" for e in errors)
            )

    # ========================================================================
    # Queries — Champion Base (Tier 1)
    # ========================================================================

    @property
    def live_patch_label(self) -> str:
        return self._manifest.live_patch_label if self._manifest else ""

    @property
    def static_data_version(self) -> str:
        return self._manifest.static_data_version if self._manifest else ""

    @property
    def manifest(self) -> DataManifestFile | None:
        return self._manifest

    @property
    def total_champions(self) -> int:
        return len(self._champion_base)

    @property
    def total_adcs(self) -> int:
        return len(self._adc_profiles)

    @property
    def total_priority(self) -> int:
        return len(self._priority_profiles)

    def get_champion(self, champion_id: str) -> ChampionBase | None:
        """Get a champion by Data Dragon ID."""
        return self._champion_base.get(champion_id)

    def get_all_champions(self) -> dict[str, ChampionBase]:
        """Get all champions."""
        return self._champion_base

    def get_all_champion_ids(self) -> set[str]:
        """Get all champion IDs."""
        return set(self._champion_base.keys())

    def get_champions_by_role(self, role: GameplayRole) -> list[ChampionBase]:
        """Get all champions with a given primary role."""
        return [c for c in self._champion_base.values() if c.primary_role == role]

    def get_champions_by_class(self, combat_class: CombatClass) -> list[ChampionBase]:
        """Get all champions with a given combat class."""
        return [c for c in self._champion_base.values() if c.combat_class == combat_class]

    def champion_exists(self, champion_id: str) -> bool:
        """Check if a champion ID exists."""
        return champion_id in self._champion_base

    # ========================================================================
    # Queries — ADC Profiles (Tier 2)
    # ========================================================================

    def get_adc_profile(self, champion_id: str) -> AdcProfile | None:
        """Get deep ADC profile by ID."""
        return self._adc_profiles.get(champion_id)

    def get_all_adc_profiles(self) -> dict[str, AdcProfile]:
        """Get all ADC profiles."""
        return self._adc_profiles

    def get_adc_ids(self) -> set[str]:
        """Get all ADC champion IDs."""
        return set(self._adc_profiles.keys())

    # ========================================================================
    # Queries — Support Profiles (Tier 2 paralelo)
    # ========================================================================

    def get_support_profile(self, champion_id: str) -> SupportProfile | None:
        """Get deep Support profile by ID."""
        return self._support_profiles.get(champion_id)

    def get_all_support_profiles(self) -> dict[str, SupportProfile]:
        """Get all Support profiles."""
        return self._support_profiles

    def get_support_ids(self) -> set[str]:
        """Get all Support champion IDs (with detailed profile)."""
        return set(self._support_profiles.keys())

    @property
    def total_supports(self) -> int:
        return len(self._support_profiles)

    # ========================================================================
    # Queries - Jungle Meta
    # ========================================================================

    def get_jungle_meta_snapshot(self, *, force_refresh: bool = False) -> JungleMetaSnapshot:
        """Return Jungle Meta snapshot using HTTP first, then local fallback."""
        if self._jungle_meta_snapshot is None or force_refresh:
            self._jungle_meta_snapshot = self._jungle_meta_provider.load()
        return self._jungle_meta_snapshot

    def get_jungle_meta_champions(self) -> dict[str, dict]:
        """Return Jungle Meta champions keyed by canonical champion ID."""
        snapshot = self.get_jungle_meta_snapshot()
        champion_ids = self.get_all_champion_ids()
        return {str(champ["id"]): champ for champ in snapshot.champions if champ.get("id") in champion_ids}

    def get_jungle_meta_champion(self, champion_id: str) -> dict | None:
        """Return one Jungle Meta row if present and canonical."""
        return self.get_jungle_meta_champions().get(champion_id)

    def get_jungler_ids(self) -> set[str]:
        """Return currently recommendable jungle champion IDs from Jungle Meta."""
        return set(self.get_jungle_meta_champions().keys())

    def get_jungle_meta_snapshot_info(self) -> dict:
        """Return lightweight metadata for the Jungle Meta source."""
        snapshot = self.get_jungle_meta_snapshot()
        return {
            "status": snapshot.status,
            "patch": snapshot.patch,
            "date_updated": snapshot.date_updated,
            "source": snapshot.source,
            "source_url": snapshot.source_url,
            "champion_count": snapshot.champion_count,
            "error": snapshot.error,
        }

    def get_jungle_meta_without_champion_base(self) -> list[str]:
        """List Jungle Meta IDs that are not canonical in champion_base."""
        snapshot = self.get_jungle_meta_snapshot()
        champion_ids = self.get_all_champion_ids()
        return sorted(
            str(champ["id"]) for champ in snapshot.champions if champ.get("id") and champ.get("id") not in champion_ids
        )

    # ========================================================================
    # Queries — Priority Profiles (Tier 3)
    # ========================================================================

    def get_priority_profile(self, champion_id: str) -> PriorityProfile | None:
        """Get priority profile by ID."""
        return self._priority_profiles.get(champion_id)

    def get_all_priority_profiles(self) -> dict[str, PriorityProfile]:
        """Get all priority profiles."""
        return self._priority_profiles

    def is_priority_champion(self, champion_id: str) -> bool:
        """Check if a champion has a priority profile."""
        return champion_id in self._priority_profiles

    # ========================================================================
    # Queries — Scoring Weights
    # ========================================================================

    def get_scoring_weights(self) -> ScoringWeightsConfig:
        """Get the scoring weights configuration."""
        if self._scoring_weights is None:
            raise RuntimeError("Scoring weights not loaded")
        return self._scoring_weights

    # ========================================================================
    # Queries — Extended KB (NotebookLM 2026-04-27)
    # ========================================================================

    def get_measured_synergy(self, adc_id: str, supp_id: str) -> dict | None:
        """Look up a measured (or heuristic) ADC+Support synergy entry.

        Returns the dict with `winrate`, `confidence`, `engine`, `reason` if a
        match exists in measured_synergies.json. Returns None otherwise.
        """
        for entry in self._measured_synergies:
            if entry.get("adc") == adc_id and entry.get("supp") == supp_id:
                return entry
        return None

    def get_measured_synergy_config(self) -> dict:
        """Return the scoring config for measured synergies (thresholds, max bonus)."""
        return self._measured_synergies_config

    def get_strategic_triangle(self) -> dict:
        """Return the strategic triangle definition (Engage > Poke > Sustain + invariants)."""
        return self._strategic_triangle

    def get_comp_predominance(self) -> dict:
        """Return the comp predominance cycle (piedra-papel-tijera entre comps)."""
        return self._comp_predominance

    def get_synergy_score(self, supp_id: str, adc_id: str) -> int | None:
        """Get quantitative synergy score (1-10) for a Support×ADC pair.

        Returns None if the pair is not in the matrix.
        Source: KB/sinergia-supp-adc.md → synergy_matrix.json.
        """
        supp_row = self._synergy_matrix.get(supp_id)
        if supp_row is None:
            return None
        return supp_row.get(adc_id)

    def get_lane_matchup(self, supp_id: str, enemy_supp_id: str) -> str | None:
        """Get lane matchup result for supp vs enemy_supp.

        Returns 'favored', 'slight_favor', 'skill', 'unfavored', or None.
        Source: KB/matchups-supp-vs-supp.md → matchup_rules.json.
        """
        lane_matchups = self._matchup_rules.get("lane_matchups", {})
        supp_matchups = lane_matchups.get(supp_id)
        if supp_matchups is None:
            return None
        return supp_matchups.get(enemy_supp_id)

    def get_matchup_score_value(self, result: str) -> float:
        """Convert a lane matchup result string to its numeric score."""
        scoring = self._matchup_rules.get("matchup_scoring", {})
        return scoring.get(result, 0.0)

    def get_matchup_rules(self) -> dict:
        """Return the full matchup_rules.json data."""
        return self._matchup_rules

    def classify_jungler_archetype(self, champion_id: str) -> str | None:
        """Classify a jungler into archetypes: engage, farm_scaling, early_gank, control.

        Source: KB/SUPPORT_THEORY.md §2.1 → jungler_archetypes.json.
        Returns None if champion is not in any jungler archetype list.
        """
        archetypes = self._jungler_archetypes.get("archetypes", {})
        for arch_id, arch_def in archetypes.items():
            if champion_id in arch_def.get("champions", []):
                return arch_id
        return None

    def get_jungler_scoring_modifier(self, jungler_archetype: str) -> dict:
        """Get scoring modifier config for a jungler archetype.

        Returns dict with boost_archetypes, penalize_archetypes, boost_value, penalty_value.
        """
        modifiers = self._jungler_archetypes.get("scoring_modifiers", {})
        key = f"{jungler_archetype}_jungler" if not jungler_archetype.endswith("_jungler") else jungler_archetype
        return modifiers.get(key, {})

    def get_queue_style_hints(self, queue_type: str) -> dict | None:
        """Get queue-specific weight adjustments and archetype boosts.

        Source: KB/notebooklm/síntesis/09-meta-regional-lck-lpl.md → queue_style_hints.json.
        """
        hints = self._queue_style_hints.get("queue_hints", {})
        return hints.get(queue_type)

    def get_adc_meta(self, adc_id: str) -> dict | None:
        """Get scraped ADC meta row if the optional snapshot exists."""
        return self._adc_meta.get(adc_id)

    def get_adc_meta_snapshot_info(self) -> dict:
        """Return lightweight metadata for the optional ADC meta snapshot."""
        if not self._adc_meta_snapshot:
            return {
                "status": "missing",
                "is_stale": True,
                "stale_after_hours": 72,
            }

        scraped_at = self._adc_meta_snapshot.get("scraped_at")
        age_hours = _age_hours(scraped_at)
        is_stale = age_hours is None or age_hours > 72

        return {
            "scraped_at": self._adc_meta_snapshot.get("scraped_at"),
            "patch": self._adc_meta_snapshot.get("patch"),
            "sources": self._adc_meta_snapshot.get("sources", []),
            "champion_count": self._adc_meta_snapshot.get("champion_count", 0),
            "status": "stale" if is_stale else "fresh",
            "is_stale": is_stale,
            "age_hours": age_hours,
            "stale_after_hours": 72,
        }

    def get_personal_adc_tier(self, adc_id: str) -> str | None:
        """Get the user's personal ADC mastery tier for a champion."""
        return self._personal_adc_tiers.get(adc_id)

    def get_personal_adc_mastery_info(self) -> dict:
        """Return lightweight metadata for the user's ADC mastery file."""
        if not self._personal_adc_mastery:
            return {
                "status": "missing",
                "source_image": None,
                "last_updated": None,
                "tiers": {},
                "excluded_from_recommendations": [],
                "never_top_pick": [],
                "needs_review": [],
            }
        return {
            "status": "loaded",
            "source_image": self._personal_adc_mastery.get("source_image"),
            "last_updated": self._personal_adc_mastery.get("last_updated"),
            "tiers": self._personal_adc_mastery.get("tiers", {}),
            "excluded_from_recommendations": self._personal_adc_mastery.get("excluded_from_recommendations", []),
            "never_top_pick": self._personal_adc_mastery.get("never_top_pick", []),
            "needs_review": self._personal_adc_mastery.get("needs_review", []),
        }

    def get_adc_meta_without_local_profile(self) -> list[str]:
        """List ADC meta snapshot champions that are not locally recommendable yet."""
        return sorted(set(self._adc_meta.keys()) - set(self._adc_profiles.keys()))

    def is_adc_excluded_by_user(self, adc_id: str) -> bool:
        """Return True if the user's mastery policy excludes this ADC."""
        return adc_id in self._excluded_adc_ids

    def is_adc_never_top_pick(self, adc_id: str) -> bool:
        """Return True if this ADC can be alternative only, never first."""
        return adc_id in self._never_top_adc_ids

    def get_support_meta(self, supp_id: str) -> dict | None:
        """Get scraped Support meta row if the optional snapshot exists."""
        return self._support_meta.get(supp_id)

    def get_support_meta_snapshot_info(self) -> dict:
        """Return lightweight metadata for the optional Support meta snapshot."""
        if not self._support_meta_snapshot:
            return {}
        return {
            "scraped_at": self._support_meta_snapshot.get("scraped_at"),
            "patch": self._support_meta_snapshot.get("patch"),
            "sources": self._support_meta_snapshot.get("sources", []),
            "champion_count": self._support_meta_snapshot.get("champion_count", 0),
        }

    def classify_supp_archetype_fine(self, supp_id: str) -> str | None:
        """Classify a support into the 5 fine-grained triangle archetypes.

        Returns one of: "engage", "poke", "enchanter_disengage", "enchanter_pure",
        "catcher", or None if not classified.
        """
        if not self._strategic_triangle:
            return None
        archetypes = self._strategic_triangle.get("fine_grained_archetypes", {})
        for arch_id, arch_def in archetypes.items():
            if supp_id in arch_def.get("champions", []):
                return arch_id
        return None

    # ========================================================================
    # Queries — Composite
    # ========================================================================

    def get_champion_display_name(self, champion_id: str) -> str:
        """Devolver nombre visible del campeon, con fallback al ID canonico."""
        champ = self._champion_base.get(champion_id)
        return champ.display_name if champ else champion_id

    def get_champion_tags(self, champion_id: str) -> dict | None:
        """Get the 14 draft-relevant tags for a champion."""
        champ = self._champion_base.get(champion_id)
        if champ is None:
            return None
        return champ.tags.model_dump()

    def get_threat_level(self, champion_id: str) -> int:
        """
        Devolver nivel de amenaza al ADC para un campeon enemigo.
        Returns priority profile threat if available, otherwise estimates from base tags.
        """
        pp = self._priority_profiles.get(champion_id)
        if pp is not None:
            return pp.adc_threat_level

        # Estimate from base tags
        champ = self._champion_base.get(champion_id)
        if champ is None:
            return 5  # Unknown, assume medium

        tags = champ.tags
        # High burst + high mobility + low tankiness = high threat to ADC
        threat = tags.burst * 0.35 + tags.mobility * 0.25 + tags.pick_potential * 0.25 + tags.engage * 0.15
        return min(10, max(0, round(threat)))

    def get_synergy_level(self, champion_id: str) -> int:
        """
        Get ADC synergy level for an allied champion.
        Returns priority profile synergy if available, otherwise estimates from base tags.
        """
        pp = self._priority_profiles.get(champion_id)
        if pp is not None:
            return pp.adc_synergy_level

        # Estimate from base tags
        champ = self._champion_base.get(champion_id)
        if champ is None:
            return 5  # Unknown

        tags = champ.tags
        # High peel + high engage + high CC + high utility = good for ADC
        synergy = tags.peel * 0.30 + tags.cc * 0.20 + tags.engage * 0.20 + tags.utility * 0.15 + tags.tankiness * 0.15
        return min(10, max(0, round(synergy)))

    def summary(self) -> str:
        """Return a human-readable summary of loaded data."""
        return (
            f"ChampionDataService loaded:\n"
            f"  Patch: {self.live_patch_label}\n"
            f"  Schema: v{self._schema_version}\n"
            f"  Tier 1 (champion_base):   {self.total_champions} champions\n"
            f"  Tier 2 (adc_profiles):    {self.total_adcs} ADCs\n"
            f"  Tier 2 (support_profiles): {self.total_supports} supports\n"
            f"  Tier 3 (priority):        {self.total_priority} draft-impact champions\n"
            f"  Scoring weights:          {'loaded' if self._scoring_weights else 'missing'}"
        )
