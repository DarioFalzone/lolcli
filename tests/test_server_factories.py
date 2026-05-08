from riot_lol_cli.draft_advisor.server import create_app as create_draft_advisor_app
from riot_lol_cli.meta_scraper.server import create_app as create_meta_scraper_app


def _route_paths(app) -> set[str]:
    return {route.path for route in app.routes}


def test_draft_advisor_create_app_registers_core_routes():
    app = create_draft_advisor_app()

    paths = _route_paths(app)

    assert "/draft" in paths
    assert "/api/v1/draft/health" in paths
    assert "/api/v1/draft/recommend" in paths


def test_meta_scraper_create_app_registers_core_routes():
    app = create_meta_scraper_app()

    paths = _route_paths(app)

    assert "/" in paths
    assert "/health" in paths
    assert "/api/v1/meta/scrape" in paths
    assert "/api/v1/meta/scrape/adc" in paths
