from contextlib import contextmanager

from fastapi.testclient import TestClient

from riot_lol_cli.api_server import app
from riot_lol_cli.meta_api import dependencies


class DummyDB:
    def init_db(self):
        return None

    def get_latest_stats(self, limit=50):
        return []

    def cleanup_old_matches(self, hours=48):
        return None


class QueryStub:
    def __init__(self, result):
        self.result = result

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def all(self):
        return self.result

    def first(self):
        return self.result[0] if self.result else None


class SessionStub:
    def __init__(self, result=None):
        self.result = result or []
        self.executed = None

    def query(self, *args, **kwargs):
        return QueryStub(self.result)

    def execute(self, statement):
        self.executed = statement
        return 1


def test_stats_champion_not_found_returns_404(monkeypatch):
    monkeypatch.setattr(dependencies, "db", DummyDB())

    @contextmanager
    def fake_session_scope():
        yield SessionStub([])

    monkeypatch.setattr(dependencies, "session_scope", fake_session_scope)

    with TestClient(app) as client:
        response = client.get("/api/v1/stats/champion/Unknown")

    assert response.status_code == 404
    assert response.json()["error"] == "No data for champion: Unknown"


def test_stats_latest_unexpected_error_returns_500(monkeypatch):
    class FailingDB(DummyDB):
        def get_latest_stats(self, limit=50):
            raise RuntimeError("db exploded")

    monkeypatch.setattr(dependencies, "db", FailingDB())

    with TestClient(app) as client:
        response = client.get("/api/v1/stats/latest")

    assert response.status_code == 500
    assert response.json()["error"] == "db exploded"


def test_maintenance_status_uses_textual_sqlalchemy_query(monkeypatch):
    monkeypatch.setattr(dependencies, "db", DummyDB())
    session = SessionStub()

    @contextmanager
    def fake_session_scope():
        yield session

    monkeypatch.setattr(dependencies, "session_scope", fake_session_scope)

    with TestClient(app) as client:
        response = client.get("/api/v1/maintenance/status")

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert str(session.executed) == "SELECT 1"
