"""Tests para AsyncRiotClient."""

import httpx
import pytest

from riot_lol_cli.api import AsyncRiotClient, RiotAPIError


@pytest.fixture
def async_client():
    return AsyncRiotClient(api_key="FAKE-KEY", platform="la2", regional="americas")


class TestAsyncRiotClient:
    @pytest.mark.asyncio
    async def test_429_retry_exhaustion(self, async_client, monkeypatch):
        """Verifica que el cliente lanza RiotAPIError tras agotar reintentos de 429."""

        class Mock429:
            status_code = 429
            headers = {"Retry-After": "0"}

        async def fake_request(*args, **kwargs):
            return Mock429()

        monkeypatch.setattr(async_client._client, "request", fake_request)

        with pytest.raises(RiotAPIError, match="429"):
            await async_client._request_json("GET", "https://example.com/test", retries=0)

    @pytest.mark.asyncio
    async def test_404_raises(self, async_client, monkeypatch):
        """Verifica que un 404 produce RiotAPIError."""

        class Mock404:
            status_code = 404
            text = "Not found"

        async def fake_request(*args, **kwargs):
            return Mock404()

        monkeypatch.setattr(async_client._client, "request", fake_request)

        with pytest.raises(RiotAPIError, match="404"):
            await async_client._request_json("GET", "https://example.com/test")

    @pytest.mark.asyncio
    async def test_200_returns_json(self, async_client, monkeypatch):
        """Verifica que un 200 parsea JSON correctamente."""

        class Mock200:
            status_code = 200

            def json(self):
                return {"puuid": "abc123"}

        async def fake_request(*args, **kwargs):
            return Mock200()

        monkeypatch.setattr(async_client._client, "request", fake_request)

        result = await async_client._request_json("GET", "https://example.com/test")
        assert result == {"puuid": "abc123"}

    @pytest.mark.asyncio
    async def test_network_error(self, async_client, monkeypatch):
        """Verifica que un error de red produce RiotAPIError."""

        async def failing_request(*args, **kwargs):
            raise httpx.ConnectError("Connection refused")

        monkeypatch.setattr(async_client._client, "request", failing_request)

        with pytest.raises(RiotAPIError, match="Error de red"):
            await async_client._request_json("GET", "https://example.com/test")
