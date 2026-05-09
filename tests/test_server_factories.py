from fastapi.testclient import TestClient

from riot_lol_cli.draft_advisor.server import create_app as create_draft_advisor_app
from riot_lol_cli.items_browser.server import create_app as create_items_browser_app
from riot_lol_cli.jungle_meta.server import create_app as create_jungle_meta_app
from riot_lol_cli.meta_api.app import create_app as create_meta_api_app
from riot_lol_cli.meta_scraper import server as meta_scraper_server
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


def test_draft_advisor_create_app_uses_isolated_services():
    first = create_draft_advisor_app()
    second = create_draft_advisor_app()

    assert first.state.draft_services is not second.state.draft_services
    assert first.state.draft_services.data_service is not second.state.draft_services.data_service


def test_meta_api_create_app_serves_health_and_openapi():
    client = TestClient(create_meta_api_app())

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"

    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    assert openapi.json()["info"]["title"].startswith("LOLCLI Meta Analyzer")


def test_meta_scraper_create_app_registers_core_routes():
    app = create_meta_scraper_app()
    paths = _route_paths(app)

    assert "/" in paths
    assert "/health" in paths
    assert "/api/v1/meta/scrape" in paths
    assert "/api/v1/meta/scrape/adc" in paths
    assert "/api/v1/meta/scrape/jungle" in paths
    assert "/api/v1/meta/jungle/tier" in paths
    assert "/api/v1/meta/jungle/champion/{champion_id}" in paths


def test_meta_scraper_create_app_serves_health_and_openapi():
    client = TestClient(create_meta_scraper_app())

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert "jungle" in health.json()

    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    assert openapi.json()["info"]["title"].startswith("Meta Scraper")


def test_meta_scraper_create_app_uses_isolated_runtime_state():
    first = create_meta_scraper_app()
    second = create_meta_scraper_app()

    assert first.state.orchestrator is not second.state.orchestrator
    assert first.state.last_scrape_result is None
    assert second.state.last_scrape_result is None


def test_meta_scraper_missing_adapters_returns_shared_playwright_message(monkeypatch):
    class EmptyOrchestrator:
        adapters = []
        is_running = False

    monkeypatch.setattr(meta_scraper_server, "_create_orchestrator", EmptyOrchestrator)
    client = TestClient(create_meta_scraper_app())

    response = client.post("/api/v1/meta/scrape")

    assert response.status_code == 503
    assert "playwright install chromium" in response.json()["detail"]
    assert "pip install playwright" not in response.json()["detail"]


def test_meta_scraper_jungle_scrape_accepts_partial_source_gaps(monkeypatch):
    class FakeAdapter:
        platform_name = "fake"

    class FakeOrchestrator:
        adapters = [FakeAdapter()]
        is_running = False

        def run_full_scrape(self, role="support"):
            return {
                "role": role,
                "champions": [],
                "source_gaps": [{"source": "opgg", "reason": "blocked"}],
            }

    monkeypatch.setattr(meta_scraper_server, "_create_orchestrator", FakeOrchestrator)
    client = TestClient(create_meta_scraper_app())

    response = client.post("/api/v1/meta/scrape/jungle")

    assert response.status_code == 200
    assert response.json()["status"] == "started"


def test_jungle_meta_create_app_registers_core_routes():
    app = create_jungle_meta_app()
    paths = _route_paths(app)

    assert "/" in paths
    assert "/health" in paths
    assert "/api/v1/jungle/tier-list" in paths
    assert "/api/v1/jungle/tier/{tier}" in paths
    assert "/api/v1/jungle/champion/{champion_id}" in paths
    assert "/api/v1/jungle/categories" in paths
    assert "/api/v1/jungle/items/abusers/{item_key}" in paths
    assert "/api/v1/jungle/items/used" in paths


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


def test_jungle_meta_categories_and_item_abusers_endpoints():
    client = TestClient(create_jungle_meta_app())

    categories = client.get("/api/v1/jungle/categories")
    assert categories.status_code == 200
    body = categories.json()
    assert "overpowered" in body
    assert "low_elo_picks" in body
    assert "bans" in body

    abusers = client.get("/api/v1/jungle/items/abusers/voltaic_sword_abusers")
    assert abusers.status_code == 200
    assert abusers.json()["count"] >= 1

    used = client.get("/api/v1/jungle/items/used")
    assert used.status_code == 200
    assert 6699 in used.json()["item_ids"]


def test_items_browser_create_app_registers_core_routes():
    app = create_items_browser_app()
    paths = _route_paths(app)

    assert "/" in paths
    assert "/health" in paths
    assert "/api/v1/items/all" in paths
    assert "/api/v1/items/groups" in paths
    assert "/api/v1/items/categories" in paths
    assert "/api/v1/items/search" in paths
    assert "/api/v1/items/{item_id}" in paths


def test_items_browser_health_and_endpoints():
    client = TestClient(create_items_browser_app())

    health = client.get("/health")
    assert health.status_code == 200
    body = health.json()
    assert body["status"] == "ok"
    assert body["service"] == "items_browser"
    assert body["current_count"] >= 700
    assert body["catalog_count"] < body["current_count"]

    voltaic = client.get("/api/v1/items/6699")
    assert voltaic.status_code == 200
    assert voltaic.json()["name_en"] == "Voltaic Cyclosword"

    search = client.get("/api/v1/items/search", params={"q": "voltaic", "lang": "en"})
    assert search.status_code == 200
    assert search.json()["count"] >= 1

    groups = client.get("/api/v1/items/groups")
    assert groups.status_code == 200
    assert "boots" in groups.json()["groups"]

    all_items = client.get("/api/v1/items/all", params={"include_deprecated": "true"})
    ids = {item["id"] for item in all_items.json()["items"]}
    assert 4633 in ids
    assert 224633 not in ids
