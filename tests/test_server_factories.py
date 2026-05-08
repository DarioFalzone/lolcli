from fastapi.testclient import TestClient

from riot_lol_cli.draft_advisor.server import create_app as create_draft_advisor_app
from riot_lol_cli.jungle_meta.server import create_app as create_jungle_meta_app
from riot_lol_cli.meta_scraper.server import create_app as create_meta_scraper_app


def _route_paths(app) -> set[str]:
    return {route.path for route in app.routes}


def test_draft_advisor_create_app_registers_core_routes():
    app = create_draft_advisor_app()
    paths = _route_paths(app)

    assert "/draft" in paths
    assert "/api/v1/draft/health" in paths
    assert "/api/v1/draft/recommend" in paths


def test_draft_advisor_create_app_serves_root_and_health():
    client = TestClient(create_draft_advisor_app())

    root = client.get("/", follow_redirects=False)
    assert root.status_code in {302, 307}
    assert root.headers["location"] == "/draft"

    health = client.get("/api/v1/draft/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"


def test_meta_scraper_create_app_registers_core_routes():
    app = create_meta_scraper_app()
    paths = _route_paths(app)

    assert "/" in paths
    assert "/health" in paths
    assert "/api/v1/meta/scrape" in paths
    assert "/api/v1/meta/scrape/adc" in paths


def test_meta_scraper_create_app_serves_health_and_openapi():
    client = TestClient(create_meta_scraper_app())

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    assert openapi.json()["info"]["title"].startswith("Meta Scraper")


def test_jungle_meta_create_app_registers_core_routes():
    app = create_jungle_meta_app()
    paths = _route_paths(app)

    assert "/" in paths
    assert "/health" in paths
    assert "/api/v1/jungle/tier-list" in paths
    assert "/api/v1/jungle/tier/{tier}" in paths
    assert "/api/v1/jungle/champion/{champion_id}" in paths


def test_jungle_meta_create_app_serves_health_and_openapi():
    client = TestClient(create_jungle_meta_app())

    health = client.get("/health")
    assert health.status_code == 200
    data = health.json()
    assert data["status"] == "ok"
    assert data["service"] == "jungle_meta"

    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    assert openapi.json()["info"]["title"].startswith("Jungle Metagame")
