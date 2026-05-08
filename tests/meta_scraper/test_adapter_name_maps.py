"""Consistencia entre los maps de nombres de los 3 adapters.

Cada adapter (OP.GG, LoLalytics, U.GG) tiene su propio map porque cada platform
slugifica los nombres distinto en sus URLs. Pero los TARGETS canonicales (los
champion ids de Riot) deberian ser identicos en los 3. Este test detecta drift
cuando alguien agrega un campeon nuevo a un adapter pero olvida los otros.
"""

import json
from collections import Counter
from pathlib import Path

from riot_lol_cli.meta_scraper.adapters.lolalytics import _LOLALYTICS_NAME_MAP
from riot_lol_cli.meta_scraper.adapters.opgg import _OPGG_NAME_MAP
from riot_lol_cli.meta_scraper.adapters.ugg import _UGG_NAME_MAP


def _canonical_targets(name_map: dict) -> set:
    return set(name_map.values())


class TestAdapterNameMapConsistency:
    def test_ksante_platform_slugs_map_to_riot_canonical_id(self):
        assert _OPGG_NAME_MAP["k'sante"] == "KSante"
        assert _LOLALYTICS_NAME_MAP["ksante"] == "KSante"
        assert _UGG_NAME_MAP["k-sante"] == "KSante"

    def test_opgg_and_lolalytics_share_targets(self):
        assert _canonical_targets(_OPGG_NAME_MAP) == _canonical_targets(_LOLALYTICS_NAME_MAP)

    def test_opgg_and_ugg_share_targets(self):
        assert _canonical_targets(_OPGG_NAME_MAP) == _canonical_targets(_UGG_NAME_MAP)

    def test_duplicate_targets_are_explicitly_allowed(self):
        allowed_duplicates = {
            "opgg": {},
            "lolalytics": {},
            "ugg": {"Nunu": {"nunu", "nunu-willump"}},
        }

        for name_map, label in (
            (_OPGG_NAME_MAP, "opgg"),
            (_LOLALYTICS_NAME_MAP, "lolalytics"),
            (_UGG_NAME_MAP, "ugg"),
        ):
            counts = Counter(name_map.values())
            duplicated_targets = {target for target, count in counts.items() if count > 1}
            assert duplicated_targets == set(allowed_duplicates[label])

            for target in duplicated_targets:
                keys = {key for key, value in name_map.items() if value == target}
                assert keys == allowed_duplicates[label][target]

    def test_targets_are_valid_champion_ids(self):
        repo_root = Path(__file__).resolve().parents[2]
        champion_base_path = repo_root / "data" / "draft_advisor" / "champion_base.json"
        if not champion_base_path.exists():
            return
        champion_base = json.loads(champion_base_path.read_text(encoding="utf-8"))
        valid_ids = set(champion_base.get("champions", champion_base).keys())
        for name_map, label in (
            (_OPGG_NAME_MAP, "opgg"),
            (_LOLALYTICS_NAME_MAP, "lolalytics"),
            (_UGG_NAME_MAP, "ugg"),
        ):
            unknown = _canonical_targets(name_map) - valid_ids
            assert not unknown, f"{label} mapea a ids no canonicos: {unknown}"
