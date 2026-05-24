"""Tests del adapter METAsrc V3.7 — extract real con BeautifulSoup."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from riot_lol_cli.meta_scraper.adapters.metasrc import (
    MetaSrcAdapter,
    _id_from_name,
    _normalize_tier,
    _to_float,
    _to_int,
    parse_html,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# parse_html con fixture sintético
# ---------------------------------------------------------------------------


def test_parse_html_sample_extrae_4_champions():
    html = _load_fixture("metasrc_jungle_sample.html")
    result = parse_html(
        html, role="jungle", patch="latest", elo="emerald_plus",
        source_url="https://www.metasrc.com/lol/na/tier-list/jungle",
    )
    assert result["status"] == "ok"
    assert result["champion_count"] == 4
    names = [c["name"] for c in result["champions"]]
    assert names == ["Wukong", "Lee Sin", "Kayn", "Nocturne"]


def test_parse_html_extrae_win_rate_pick_rate_ban_rate():
    html = _load_fixture("metasrc_jungle_sample.html")
    result = parse_html(
        html, role="jungle", patch="latest", elo="emerald_plus",
        source_url="https://x",
    )
    wukong = next(c for c in result["champions"] if c["name"] == "Wukong")
    assert wukong["win_rate"] == 54.2
    assert wukong["pick_rate"] == 8.5
    assert wukong["ban_rate"] == 12.3
    assert wukong["games"] == 45231
    assert wukong["tier"] == "S"  # S+ normaliza a S


def test_parse_html_normaliza_id_sin_espacios():
    html = _load_fixture("metasrc_jungle_sample.html")
    result = parse_html(
        html, role="jungle", patch="latest", elo="emerald_plus", source_url="https://x"
    )
    lee_sin = next(c for c in result["champions"] if c["name"] == "Lee Sin")
    assert lee_sin["id"] == "LeeSin"


def test_parse_html_vacio_retorna_gap():
    result = parse_html(
        "<html><body><p>no table here</p></body></html>",
        role="jungle", patch="latest", elo="emerald_plus", source_url="https://x",
    )
    assert result["status"] == "gap"
    assert "no_structure_match" in result["reason"]
    assert result["champions"] == []


def test_parse_html_data_attrs_strategy():
    html = """
    <html><body>
      <div data-champion="Graves" data-wr="53.1" data-pr="6.2" data-br="2.8" data-games="22000" data-tier="A"></div>
      <div data-champion="Vi" data-wr="48.5" data-pr="3.1" data-games="8000"></div>
    </body></html>
    """
    result = parse_html(
        html, role="jungle", patch="latest", elo="emerald_plus", source_url="https://x",
    )
    assert result["status"] == "ok"
    assert result["strategy"] == "data_attrs"
    graves = next(c for c in result["champions"] if c["name"] == "Graves")
    assert graves["win_rate"] == 53.1
    assert graves["tier"] == "A"


# ---------------------------------------------------------------------------
# fetch_jungle_tier_list con monkey patch de _safe_get
# ---------------------------------------------------------------------------


def test_fetch_jungle_tier_list_con_fixture():
    adapter = MetaSrcAdapter()
    html = _load_fixture("metasrc_jungle_sample.html")
    fake_response = MagicMock()
    fake_response.text = html
    adapter._safe_get = MagicMock(return_value=fake_response)

    result = adapter.fetch_jungle_tier_list(elo="emerald_plus")
    assert result["status"] == "ok"
    assert result["platform"] == "metasrc"
    assert result["role"] == "jungle"
    assert result["champion_count"] == 4
    adapter._safe_get.assert_called_once()


def test_fetch_jungle_http_error_retorna_gap():
    adapter = MetaSrcAdapter()
    adapter._safe_get = MagicMock(side_effect=RuntimeError("connection timeout"))
    result = adapter.fetch_jungle_tier_list(elo="emerald_plus")
    assert result["status"] == "gap"
    assert "http_fetch_failed" in result["reason"]
    assert result["champion_count"] == 0


def test_fetch_support_devuelve_gap():
    """METAsrc adapter solo soporta jungle en V3.7."""
    adapter = MetaSrcAdapter()
    result = adapter.fetch_support_tier_list()
    assert result["status"] == "gap"
    assert "solo soporta role=jungle" in result["reason"]


def test_fetch_champion_detail_no_implementado():
    adapter = MetaSrcAdapter()
    result = adapter.fetch_champion_detail("LeeSin")
    assert result["status"] == "not_implemented"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def test_id_from_name_sin_espacios():
    assert _id_from_name("Lee Sin") == "LeeSin"
    assert _id_from_name("Kha'Zix") == "KhaZix"
    assert _id_from_name("Dr. Mundo") == "DrMundo"


def test_to_float_acepta_pct_y_numero():
    assert _to_float("52.3%") == 52.3
    assert _to_float("48.0") == 48.0
    assert _to_float(51.5) == 51.5
    assert _to_float(None) is None
    assert _to_float("abc") is None


def test_to_int_limpia_separadores():
    assert _to_int("45,231") == 45231
    assert _to_int("100") == 100
    assert _to_int(None) is None
    assert _to_int("") is None


def test_normalize_tier_collapsa_variantes():
    assert _normalize_tier("S+") == "S"
    assert _normalize_tier("S") == "S"
    assert _normalize_tier("S-") == "S"
    assert _normalize_tier("A+") == "A"
    assert _normalize_tier("B-") == "B"
    assert _normalize_tier(None) is None
    assert _normalize_tier("GOD") == "S"


# ---------------------------------------------------------------------------
# Integración con orchestrator
# ---------------------------------------------------------------------------


def test_metasrc_integra_con_meta_soloq_extra(monkeypatch):
    """Smoke: meta_soloq_extra con MetaSrcAdapter real debe producir snapshots."""
    from riot_lol_cli.jungle_research.pipelines import meta_soloq_extra

    adapter = MetaSrcAdapter()
    html = _load_fixture("metasrc_jungle_sample.html")
    fake_response = MagicMock()
    fake_response.text = html
    adapter._safe_get = MagicMock(return_value=fake_response)

    result = meta_soloq_extra.run(
        adapters={"metasrc_jungle": adapter}, persist=False
    )
    assert len(result.snapshots) == 4
    assert result.runs[0].status == "ok"
    assert result.runs[0].champion_count == 4
