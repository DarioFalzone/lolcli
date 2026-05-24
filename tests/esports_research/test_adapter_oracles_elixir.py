from __future__ import annotations

from tests.esports_research.conftest import load_text_fixture

from riot_lol_cli.meta_scraper.adapters.esports.oracles_elixir import OraclesElixirAdapter, parse_csv_text


class _TextResponse:
    text = load_text_fixture("oracles_elixir_sample.csv")


def test_parse_csv_text_counts_rows():
    rows = parse_csv_text(load_text_fixture("oracles_elixir_sample.csv"))
    assert len(rows) == 2
    assert rows[0]["playername"] == "Viper"


def test_fetch_csv_downloads_expected_url(monkeypatch):
    adapter = OraclesElixirAdapter()
    seen = {}

    def fake_get(url, **kwargs):
        seen["url"] = url
        return _TextResponse()

    monkeypatch.setattr(adapter, "_safe_get", fake_get)
    payload = adapter.fetch_csv(year=2025, filename="sample.csv")
    assert seen["url"].endswith("/sample.csv")
    assert payload["row_count"] == 2


def test_fetch_tournaments_filters_league(monkeypatch):
    adapter = OraclesElixirAdapter()
    monkeypatch.setattr(adapter, "fetch_csv", lambda year: {"csv_text": load_text_fixture("oracles_elixir_sample.csv")})
    payload = adapter.fetch_tournaments("LCK", "2025")
    assert payload["row_count"] == 2


def test_lookup_methods_return_gaps():
    adapter = OraclesElixirAdapter()
    assert adapter.fetch_matches("x")["status"] == "gap"
    assert adapter.fetch_game_detail("x")["status"] == "gap"
    assert adapter.fetch_draft("x")["status"] == "gap"
