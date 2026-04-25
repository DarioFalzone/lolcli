import pytest

from riot_lol_cli.regions import get_regional_route


def test_get_regional_route_maps_la2_to_americas():
    assert get_regional_route("la2") == "americas"


def test_get_regional_route_is_case_insensitive():
    assert get_regional_route("NA1") == "americas"


def test_get_regional_route_raises_for_unknown_platform():
    with pytest.raises(ValueError):
        get_regional_route("mars1")
