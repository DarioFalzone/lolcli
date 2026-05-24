from __future__ import annotations

from pathlib import Path

from riot_lol_cli.meta_scraper.adapters.esports.base_esports import CONTACT_EMAIL, ESPORTS_USER_AGENT
from riot_lol_cli.meta_scraper.adapters.esports.gol_gg import GolGGAdapter
from riot_lol_cli.meta_scraper.adapters.esports.leaguepedia import LeaguepediaAdapter
from riot_lol_cli.meta_scraper.adapters.esports.lol_esports_vods import LolEsportsVodsAdapter


def test_routes_do_not_expose_live_advice():
    text = Path("src/riot_lol_cli/meta_api/routes/esports.py").read_text(encoding="utf-8").lower()
    assert "live advice" not in text
    assert "@router.get(\"/live" not in text
    assert "@router.post(\"/live" not in text


def test_vods_metadata_only_no_download_method():
    adapter = LolEsportsVodsAdapter()
    assert not hasattr(adapter, "download_video")
    payload = adapter.fetch_vod_metadata("g1")
    assert "video download is prohibited" in payload["gaps"][0]


def test_rate_limits_are_strict():
    assert GolGGAdapter.min_delay >= 4.0
    assert LeaguepediaAdapter.min_delay >= 2.0


def test_user_agent_has_contact_email():
    assert CONTACT_EMAIL in ESPORTS_USER_AGENT
    assert "mailto:" in ESPORTS_USER_AGENT


def test_gol_gg_has_robots_check():
    assert hasattr(GolGGAdapter(), "robots_allowed")
