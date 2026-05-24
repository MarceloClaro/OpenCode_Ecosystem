"""
core/rest_client.py — Cliente HTTP com Retry, Timeout, Logging e DI.

Wrapper padronizado sobre ``httpx`` com exponential backoff,
log estruturado e tratamento uniforme de erros mapeado para a
hierarquia de exceções do core.

Uso com DI (novo):
    container = Container.instance()
    client = RestClient(container=container, base_url="https://api.example.com")
    result = await client.get("/users")

Uso legado (compatível):
    client = RestClient("https://api.example.com", timeout=30)
    result = await client.get("/users")
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

import httpx

from core.errors import IntegrationError, TimeoutError

logger = logging.getLogger(__name__)


class RestClient:
    """Cliente HTTP reutilizável com retry automático e tratamento de erros.

    Gerencia uma conexão ``httpx.AsyncClient`` internamente, criada
    sob demanda na primeira requisição e reutilizada até o fechamento.

    Args:
        base_url: URL base para requisições (opcional).
        timeout: Timeout padrão em segundos.
        max_retries: Número máximo de tentativas por requisição.
        headers: Cabeçalhos HTTP padrão.
        container: Container DI opcional.
    """

    def __init__(
        self,
        base_url: str = "",
        timeout: float = 30.0,
        max_retries: int = 3,
        headers: Optional[dict[str, str]] = None,
        container: Any = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._default_headers = headers or {}
        self._client: Optional[httpx.AsyncClient] = None
        self._container = container

        if container is not None and not container.is_registered('http_client'):
            container.register('http_client', self)

    # --- Gerenciamento do Client ---

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self._timeout),
                follow_redirects=True,
            )
        return self._client

    async def close(self) -> None:
        """Fecha a conexão HTTP."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    # --- Métodos HTTP Públicos ---

    async def get(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> Any:
        return await self._request("GET", path, params=params, headers=headers)

    async def post(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
        data: Any = None,
        headers: Optional[dict[str, str]] = None,
    ) -> Any:
        return await self._request("POST", path, json=json, data=data, headers=headers)

    async def put(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> Any:
        return await self._request("PUT", path, json=json, headers=headers)

    async def patch(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> Any:
        return await self._request("PATCH", path, json=json, headers=headers)

    async def delete(
        self,
        path: str,
        headers: Optional[dict[str, str]] = None,
    ) -> Any:
        return await self._request("DELETE", path, headers=headers)

    # --- Método Interno ---

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
        data: Any = None,
        headers: Optional[dict[str, str]] = None,
    ) -> Any:
        url = f"{self._base_url}/{path.lstrip('/')}" if self._base_url else path
        merged_headers = {**self._default_headers, **(headers or {})}
        last_error: Optional[Exception] = None

        for attempt in range(1, self._max_retries + 1):
            try:
                client = await self._get_client()
                response = await client.request(
                    method=method, url=url, params=params,
                    json=json, content=data, headers=merged_headers or None,
                )

                if response.is_success:
                    ct = response.headers.get("content-type", "")
                    if ct.startswith("application/json"):
                        return response.json()
                    return response.text

                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", "5"))
                    logger.warning(
                        "Rate limited %s %s, retry %ds (attempt %d/%d)",
                        method, url, retry_after, attempt, self._max_retries,
                    )
                    await asyncio.sleep(retry_after)
                    continue

                if response.status_code >= 500:
                    logger.warning(
                        "Server error %d %s %s (attempt %d/%d)",
                        response.status_code, method, url, attempt, self._max_retries,
                    )
                    if attempt < self._max_retries:
                        await asyncio.sleep(2**attempt)
                        continue
                    raise IntegrationError(
                        f"{method} {url} returned HTTP {response.status_code}",
                        details={"method": method, "url": url,
                                 "status": response.status_code,
                                 "body": response.text[:300], "attempt": attempt},
                    )

                raise IntegrationError(
                    f"{method} {url} returned HTTP {response.status_code}",
                    details={"method": method, "url": url,
                             "status": response.status_code,
                             "body": response.text[:300]},
                )

            except httpx.TimeoutException as e:
                last_error = TimeoutError(
                    f"{method} {url} timed out ({self._timeout}s)",
                    original=e,
                    details={"method": method, "url": url,
                             "timeout": self._timeout, "attempt": attempt},
                )
                if attempt < self._max_retries:
                    await asyncio.sleep(2**attempt)

            except (httpx.NetworkError, httpx.ConnectError) as e:
                last_error = IntegrationError(
                    f"{method} {url} network error: {e}",
                    original=e,
                    details={"method": method, "url": url, "attempt": attempt},
                )
                if attempt < self._max_retries:
                    await asyncio.sleep(2**attempt)

            except IntegrationError:
                raise

            except Exception as e:
                last_error = IntegrationError(
                    f"{method} {url} unexpected: {e}",
                    original=e,
                    details={"method": method, "url": url, "attempt": attempt},
                )
                if attempt < self._max_retries:
                    await asyncio.sleep(2**attempt)

        if last_error:
            raise last_error
        raise IntegrationError(f"{method} {url} failed after {self._max_retries} attempts")

    # --- Context Manager ---

    async def __aenter__(self) -> RestClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    # --- Factory ---

    @classmethod
    def create(cls, base_url: str = "", timeout: float = 30.0,
               max_retries: int = 3, **kwargs: Any) -> RestClient:
        return cls(base_url=base_url, timeout=timeout,
                   max_retries=max_retries, **kwargs)

    def __repr__(self) -> str:
        return (f"RestClient(base='{self._base_url}', "
                f"timeout={self._timeout}, retries={self._max_retries})")
