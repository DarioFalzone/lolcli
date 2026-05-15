"""Sanity de los 4 adapters V3 (stubs): interfaz, status, no scrape."""

from __future__ import annotations

from riot_lol_cli.meta_scraper.adapters.leagueofgraphs import LeagueOfGraphsAdapter
from riot_lol_cli.meta_scraper.adapters.metasrc import MetaSrcAdapter
from riot_lol_cli.meta_scraper.adapters.mobalytics import MobalyticsAdapter
from riot_lol_cli.meta_scraper.adapters.tracker_gg import TrackerGgAdapter

_ADAPTERS = [
    (MetaSrcAdapter, "metasrc", "metasrc.com"),
    (MobalyticsAdapter, "mobalytics", "mobalytics.gg"),
    (LeagueOfGraphsAdapter, "leagueofgraphs", "leagueofgraphs.com"),
    (TrackerGgAdapter, "tracker_gg", "tracker.gg"),
]


def test_all_adapters_expose_platform_name():
    for cls, expected_name, _ in _ADAPTERS:
        assert cls.platform_name == expected_name


def test_all_adapters_jungle_returns_not_implemented_without_network():
    """Los stubs no hacen ninguna llamada de red."""
    for cls, expected_name, expected_host in _ADAPTERS:
        adapter = cls()
        payload = adapter.fetch_jungle_tier_list()
        assert payload["status"] == "not_implemented"
        assert payload["platform"] == expected_name
        assert expected_host in payload["source_url"]
        assert payload["champions"] == []
        assert payload["champion_count"] == 0


def test_all_adapters_champion_detail_returns_not_implemented():
    for cls, _, _ in _ADAPTERS:
        adapter = cls()
        result = adapter.fetch_champion_detail("LeeSin")
        assert result["status"] == "not_implemented"
        assert result["champion_id"] == "LeeSin"


def test_loG_has_conservative_rate_limit():
    """League of Graphs es estricto: min_delay >= 8s."""
    assert LeagueOfGraphsAdapter.min_delay >= 8.0
