"""Sanity de los 4 adapters V3: interfaz + estado.

Tras V3.7 [2026-05-24]: metasrc fue activado con parse real (ya no es
stub). Tests específicos de metasrc viven en `test_adapter_metasrc.py`.
Los otros 3 (mobalytics, leagueofgraphs, tracker_gg) siguen como stubs.
"""

from __future__ import annotations

from riot_lol_cli.meta_scraper.adapters.leagueofgraphs import LeagueOfGraphsAdapter
from riot_lol_cli.meta_scraper.adapters.metasrc import MetaSrcAdapter
from riot_lol_cli.meta_scraper.adapters.mobalytics import MobalyticsAdapter
from riot_lol_cli.meta_scraper.adapters.tracker_gg import TrackerGgAdapter

# Adapters que siguen siendo stubs en V3.7. Cuando se activen (V3.8+),
# mover aca tests específicos como en `test_adapter_metasrc.py`.
_STUB_ADAPTERS = [
    (MobalyticsAdapter, "mobalytics", "mobalytics.gg"),
    (LeagueOfGraphsAdapter, "leagueofgraphs", "leagueofgraphs.com"),
    (TrackerGgAdapter, "tracker_gg", "tracker.gg"),
]


def test_all_adapters_expose_platform_name():
    """Los 4 adapters V3 declaran platform_name correcto."""
    assert MetaSrcAdapter.platform_name == "metasrc"
    for cls, expected_name, _ in _STUB_ADAPTERS:
        assert cls.platform_name == expected_name


def test_stub_adapters_jungle_returns_not_implemented_without_network():
    """Los 3 stubs no hacen llamada de red — retornan not_implemented."""
    for cls, expected_name, expected_host in _STUB_ADAPTERS:
        adapter = cls()
        payload = adapter.fetch_jungle_tier_list()
        assert payload["status"] == "not_implemented"
        assert payload["platform"] == expected_name
        assert expected_host in payload["source_url"]
        assert payload["champions"] == []
        assert payload["champion_count"] == 0


def test_stub_adapters_champion_detail_returns_not_implemented():
    for cls, _, _ in _STUB_ADAPTERS:
        adapter = cls()
        result = adapter.fetch_champion_detail("LeeSin")
        assert result["status"] == "not_implemented"
        assert result["champion_id"] == "LeeSin"


def test_metasrc_champion_detail_still_not_implemented():
    """V3.7: solo activamos jungle tier list, champion detail queda stub."""
    adapter = MetaSrcAdapter()
    result = adapter.fetch_champion_detail("LeeSin")
    assert result["status"] == "not_implemented"


def test_loG_has_conservative_rate_limit():
    """League of Graphs es estricto: min_delay >= 8s."""
    assert LeagueOfGraphsAdapter.min_delay >= 8.0
