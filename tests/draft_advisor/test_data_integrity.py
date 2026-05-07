from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from riot_lol_cli.draft_advisor.champion_data import ChampionDataService
from riot_lol_cli.draft_advisor.server import app


@pytest.fixture(scope="module")
def data_service() -> ChampionDataService:
    return ChampionDataService()


def test_champion_data_service_loads_current_rosters(data_service: ChampionDataService) -> None:
    assert data_service.total_champions == 172
    assert data_service.total_adcs == 32
    assert data_service.total_supports == 34
    assert data_service.total_priority == 41
    assert data_service.live_patch_label == "16.9"
    assert data_service.static_data_version == "16.9.1"


def test_profile_references_use_canonical_champion_ids(data_service: ChampionDataService) -> None:
    champion_ids = data_service.get_all_champion_ids()
    errors: list[str] = []

    for adc_id, profile in data_service.get_all_adc_profiles().items():
        if adc_id != profile.id:
            errors.append(f"adc profile key/id mismatch: {adc_id} != {profile.id}")
        for ref in profile.best_with:
            if ref not in champion_ids:
                errors.append(f"ADC {adc_id} best_with uses non-canonical id {ref}")
        for ref in profile.worst_into:
            if ref not in champion_ids:
                errors.append(f"ADC {adc_id} worst_into uses non-canonical id {ref}")

    for support_id, profile in data_service.get_all_support_profiles().items():
        if support_id != profile.id:
            errors.append(f"support profile key/id mismatch: {support_id} != {profile.id}")
        for field_name in (
            "best_with_adcs",
            "worst_with_adcs",
            "strong_against_supports",
            "weak_against_supports",
        ):
            for ref in getattr(profile, field_name):
                if ref not in champion_ids:
                    errors.append(f"Support {support_id} {field_name} uses non-canonical id {ref}")

    for priority_id, profile in data_service.get_all_priority_profiles().items():
        if priority_id != profile.id:
            errors.append(f"priority profile key/id mismatch: {priority_id} != {profile.id}")
        if priority_id not in champion_ids:
            errors.append(f"Priority profile {priority_id} is missing from champion_base")

    assert errors == []


def test_localized_display_names_keep_canonical_ids(data_service: ChampionDataService) -> None:
    assert data_service.get_champion_display_name("Bard") == "Bardo"
    assert data_service.get_champion_display_name("MasterYi") == "Maestro Yi"

    bard_profile = data_service.get_support_profile("Bard")
    assert bard_profile is not None
    assert bard_profile.display_name == "Bardo"


def test_champion_picker_api_smoke_loads_rosters() -> None:
    client = TestClient(app)

    health = client.get("/api/v1/draft/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    champions = client.get("/api/v1/draft/champions")
    assert champions.status_code == 200
    payload = champions.json()
    assert len(payload) == health.json()["total_champions"]
    assert any(champion["id"] == "Seraphine" for champion in payload)
    assert any(champion["id"] == "JarvanIV" for champion in payload)
    assert any(champion["id"] == "Bard" and champion["display_name"] == "Bardo" for champion in payload)
    assert any(champion["id"] == "MasterYi" and champion["display_name"] == "Maestro Yi" for champion in payload)
