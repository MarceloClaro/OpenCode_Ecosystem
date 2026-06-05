"""
Testes do RestClient (core/rest_client.py)

Cobre:
- GET / POST / PUT / PATCH / DELETE
- JSON response parsing
- Text response fallback
- Rate limiting (429) com retry
- Server error (5xx) com retry
- Timeout (httpx.TimeoutException)
- Network error (httpx.ConnectError)
- Esgotamento de retries
- Context manager (async with)
- Factory method create()
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.rest_client import RestClient
from core.errors import IntegrationError, TimeoutError


@pytest.fixture
def mock_client():
    """Cria um mock de httpx.AsyncClient."""
    with patch("httpx.AsyncClient") as mock:
        client_instance = AsyncMock()
        mock.return_value = client_instance
        yield client_instance


@pytest.fixture
def rest():
    """RestClient limpo."""
    client = RestClient(base_url="https://api.example.com", timeout=5, max_retries=2)
    yield client
    # cleanup
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            loop.create_task(client.close())
    except RuntimeError:
        pass


class TestRestClientHttpMethods:
    """Testa os metodos HTTP basicos."""

    @pytest.mark.asyncio
    async def test_get_json(self, rest, mock_client):
        mock_response = AsyncMock()
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"result": "ok"}
        mock_client.request.return_value = mock_response

        result = await rest.get("/data", params={"page": 1})
        assert result == {"result": "ok"}
        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["method"] == "GET"

    @pytest.mark.asyncio
    async def test_get_text(self, rest, mock_client):
        mock_response = AsyncMock()
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.text = "plain text response"
        mock_client.request.return_value = mock_response

        result = await rest.get("/text")
        assert result == "plain text response"

    @pytest.mark.asyncio
    async def test_post_json(self, rest, mock_client):
        mock_response = AsyncMock()
        mock_response.is_success = True
        mock_response.status_code = 201
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"id": 42}
        mock_client.request.return_value = mock_response

        result = await rest.post("/items", json={"name": "test"})
        assert result == {"id": 42}
        args, kwargs = mock_client.request.call_args
        assert kwargs["method"] == "POST"
        assert kwargs["json"] == {"name": "test"}

    @pytest.mark.asyncio
    async def test_put(self, rest, mock_client):
        mock_response = AsyncMock()
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"updated": True}
        mock_client.request.return_value = mock_response

        result = await rest.put("/items/1", json={"name": "new"})
        assert result == {"updated": True}

    @pytest.mark.asyncio
    async def test_patch(self, rest, mock_client):
        mock_response = AsyncMock()
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"patched": True}
        mock_client.request.return_value = mock_response

        result = await rest.patch("/items/1", json={"field": "val"})
        assert result == {"patched": True}

    @pytest.mark.asyncio
    async def test_delete(self, rest, mock_client):
        mock_response = AsyncMock()
        mock_response.is_success = True
        mock_response.status_code = 204
        mock_response.headers = {}
        mock_response.text = ""
        mock_client.request.return_value = mock_response

        result = await rest.delete("/items/1")
        # 204 sem corpo retorna string vazia
        assert result == ""


class TestRestClientRetry:
    """Testa comportamento de retry."""

    @pytest.mark.asyncio
    async def test_rate_limit_retry(self, rest, mock_client):
        """429 deve retry com Retry-After."""
        mock_429 = AsyncMock()
        mock_429.is_success = False
        mock_429.status_code = 429
        mock_429.headers = {"Retry-After": "0"}

        mock_ok = AsyncMock()
        mock_ok.is_success = True
        mock_ok.status_code = 200
        mock_ok.headers = {"content-type": "application/json"}
        mock_ok.json.return_value = {"success": True}

        mock_client.request.side_effect = [mock_429, mock_ok]
        result = await rest.get("/rate-limited")
        assert result == {"success": True}
        assert mock_client.request.call_count == 2

    @pytest.mark.asyncio
    async def test_server_error_retry(self, rest, mock_client):
        """5xx deve retry com backoff."""
        mock_500 = AsyncMock()
        mock_500.is_success = False
        mock_500.status_code = 500
        mock_500.headers = {}
        mock_500.text = "Internal Error"

        mock_ok = AsyncMock()
        mock_ok.is_success = True
        mock_ok.status_code = 200
        mock_ok.headers = {"content-type": "application/json"}
        mock_ok.json.return_value = {"ok": True}

        mock_client.request.side_effect = [mock_500, mock_ok]
        result = await rest.get("/retry")
        assert result == {"ok": True}
        assert mock_client.request.call_count == 2

    @pytest.mark.asyncio
    async def test_all_retries_exhausted(self, rest, mock_client):
        """Apos esgotar retries, deve levantar IntegrationError."""
        mock_500 = AsyncMock()
        mock_500.is_success = False
        mock_500.status_code = 500
        mock_500.headers = {}
        mock_500.text = "Server Error"

        mock_client.request.return_value = mock_500

        with pytest.raises(IntegrationError, match="500"):
            await rest.get("/fail")
        assert mock_client.request.call_count == rest._max_retries

    @pytest.mark.asyncio
    async def test_timeout_retry(self, rest, mock_client):
        """Timeout deve retry e depois levantar TimeoutError."""
        from httpx import TimeoutException
        mock_client.request.side_effect = TimeoutException("timeout")

        with pytest.raises(TimeoutError, match="timed out"):
            await rest.get("/slow")
        assert mock_client.request.call_count == rest._max_retries

    @pytest.mark.asyncio
    async def test_network_error_retry(self, rest, mock_client):
        """Network error deve retry."""
        from httpx import ConnectError
        mock_client.request.side_effect = ConnectError("connection refused")

        with pytest.raises(IntegrationError, match="network error"):
            await rest.get("/down")
        assert mock_client.request.call_count == rest._max_retries


class TestRestClientErrors:
    """Testa tratamento de erros."""

    @pytest.mark.asyncio
    async def test_4xx_no_retry(self, rest, mock_client):
        """4xx que nao seja 429 nao deve retry."""
        mock_400 = AsyncMock()
        mock_400.is_success = False
        mock_400.status_code = 400
        mock_400.headers = {}
        mock_400.text = "Bad Request"
        mock_client.request.return_value = mock_400

        with pytest.raises(IntegrationError, match="400"):
            await rest.get("/bad-request")
        assert mock_client.request.call_count == 1  # sem retry

    @pytest.mark.asyncio
    async def test_4xx_with_details(self, rest, mock_client):
        mock_403 = AsyncMock()
        mock_403.is_success = False
        mock_403.status_code = 403
        mock_403.headers = {}
        mock_403.text = "Forbidden"
        mock_client.request.return_value = mock_403

        try:
            await rest.get("/forbidden")
        except IntegrationError as e:
            assert e.http_status == 502  # IntegrationError
            assert e.details["status"] == 403
            assert e.details["method"] == "GET"


class TestRestClientContextManager:
    """Testa async context manager."""

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        with patch("httpx.AsyncClient") as mock:
            client_instance = AsyncMock()
            mock.return_value = client_instance

            mock_response = AsyncMock()
            mock_response.is_success = True
            mock_response.status_code = 200
            mock_response.headers = {"content-type": "application/json"}
            mock_response.json.return_value = {"ok": True}
            client_instance.request.return_value = mock_response

            async with RestClient("https://api.test", timeout=5) as client:
                result = await client.get("/ping")
                assert result == {"ok": True}

            client_instance.aclose.assert_called_once()


class TestRestClientFactory:
    """Testa factory method."""

    def test_create(self):
        client = RestClient.create(
            base_url="https://api.test",
            timeout=10,
            max_retries=5,
        )
        assert client._base_url == "https://api.test"
        assert client._timeout == 10
        assert client._max_retries == 5

    def test_repr(self):
        client = RestClient("https://api.test", timeout=15, max_retries=3)
        r = repr(client)
        assert "RestClient" in r
        assert "api.test" in r
        assert "timeout=15" in r
        assert "retries=3" in r
