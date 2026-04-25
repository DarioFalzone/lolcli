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
from pathlib import Path

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
)


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
        self._priority_profiles: dict[str, PriorityProfile] = {}
        self._scoring_weights: ScoringWeightsConfig | None = None

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
        self._load_priority_profiles()
        self._load_scoring_weights()
        self._cross_validate()

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

        if errors:
            raise ValueError(
                f"Cross-validation failed with {len(errors)} errors:\n"
                + "\n".join(f"  - {e}" for e in errors)
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
        return [
            c for c in self._champion_base.values()
            if c.primary_role == role
        ]

    def get_champions_by_class(self, combat_class: CombatClass) -> list[ChampionBase]:
        """Get all champions with a given combat class."""
        return [
            c for c in self._champion_base.values()
            if c.combat_class == combat_class
        ]

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
    # Queries — Composite
    # ========================================================================

    def get_champion_display_name(self, champion_id: str) -> str:
        """Get display name for a champion, with fallback to ID."""
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
        Get ADC threat level for an enemy champion.
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
        threat = (tags.burst * 0.35 + tags.mobility * 0.25
                  + tags.pick_potential * 0.25 + tags.engage * 0.15)
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
        synergy = (tags.peel * 0.30 + tags.cc * 0.20
                   + tags.engage * 0.20 + tags.utility * 0.15
                   + tags.tankiness * 0.15)
        return min(10, max(0, round(synergy)))

    def summary(self) -> str:
        """Return a human-readable summary of loaded data."""
        return (
            f"ChampionDataService loaded:\n"
            f"  Patch: {self._patch}\n"
            f"  Schema: v{self._schema_version}\n"
            f"  Tier 1 (champion_base): {self.total_champions} champions\n"
            f"  Tier 2 (adc_profiles):  {self.total_adcs} ADCs\n"
            f"  Tier 3 (priority):      {self.total_priority} draft-impact champions\n"
            f"  Scoring weights:        {'loaded' if self._scoring_weights else 'missing'}"
        )
