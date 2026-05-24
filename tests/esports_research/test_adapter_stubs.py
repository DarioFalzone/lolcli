from __future__ import annotations

import pytest

from riot_lol_cli.meta_scraper.adapters.esports.abios import AbiosAdapter
from riot_lol_cli.meta_scraper.adapters.esports.game_client_local import GameClientLocalAdapter
from riot_lol_cli.meta_scraper.adapters.esports.lol_esports_vods import LolEsportsVodsAdapter
from riot_lol_cli.meta_scraper.adapters.esports.pandascore import PandaScoreAdapter
from riot_lol_cli.meta_scraper.adapters.esports.riot_esports_grid import RiotEsportsGridAdapter
from riot_lol_cli.meta_scraper.adapters.esports.riot_tournament_v5 import RiotTournamentV5Adapter


@pytest.mark.parametrize(
    "adapter,method",
    [
        (RiotTournamentV5Adapter(), "create_provider"),
        (RiotTournamentV5Adapter(), "create_tournament"),
        (RiotTournamentV5Adapter(), "create_code"),
        (RiotTournamentV5Adapter(), "register_callback"),
        (RiotEsportsGridAdapter(), "connect_session"),
        (RiotEsportsGridAdapter(), "subscribe_feed"),
        (PandaScoreAdapter(), "list_tournaments"),
        (PandaScoreAdapter(), "get_match_frames"),
        (PandaScoreAdapter(), "subscribe_live"),
        (AbiosAdapter(), "list_matches"),
        (AbiosAdapter(), "get_stats"),
        (GameClientLocalAdapter(), "get_live_game_data"),
        (GameClientLocalAdapter(), "get_player_list"),
    ],
)
def test_stub_methods_return_not_implemented(adapter, method):
    payload = getattr(adapter, method)()
    assert payload["status"] == "not_implemented"
    assert payload["gaps"]


def test_vod_metadata_stub_is_metadata_only():
    payload = LolEsportsVodsAdapter().fetch_vod_metadata("g1")
    assert payload["status"] == "not_implemented"
    assert payload["metadata"] is None
    assert {"game_id", "video_url", "timestamp_start", "thumbnail_url"} <= set(payload["allowed_fields"])


def test_vod_metadata_normalization():
    payload = LolEsportsVodsAdapter().normalize_metadata(
        {
            "game_id": "g1",
            "video_url": "https://lolesports.com/vod/1",
            "platform": "lolesports",
            "timestamp_start": 42,
            "duration_seconds": 1800,
            "thumbnail_url": "https://example.test/thumb.jpg",
            "language": "es",
        }
    )
    assert payload["game_id"] == "g1"
