"""
ProviderFactory — Multi-LLM provider com fallback automatico.

Extraido de SandeClaw (specs/architecture.md secao 2.7, PRD.md RF-03).
Padrao Factory + Strategy: instancia provedores LLM por configuracao,
com fallback transparente quando o primario falha.

Integracao OpenCode:
  - Substitui chamadas diretas a APIs de LLM espalhadas pelo ecossistema
  - Unifica Gemini, DeepSeek, Groq (e outros) sob interface comum
  - Habilita troca dinamica sem alterar codigo consumidor
  - Fallback com retry + backoff exponencial evita falhas catastroficas
"""

from __future__ import annotations

import os
import json
import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

logger = logging.getLogger(__name__)

MAX_RETRIES = 2
BACKOFF_BASE = 1.5


@runtime_checkable
class SupportsChat(Protocol):
    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str: ...


@dataclass
class ProviderConfig:
    name: str
    api_key_env: str
    base_url: str
    model: str
    priority: int = 0
    timeout_s: int = 120
    max_retries: int = MAX_RETRIES


class BaseProvider(ABC):
    def __init__(self, config: ProviderConfig) -> None:
        self.config = config
        self._api_key: str = os.environ.get(config.api_key_env, "")

    @property
    def available(self) -> bool:
        return bool(self._api_key)

    @abstractmethod
    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str: ...

    def _http_post(self, payload: dict[str, Any]) -> dict[str, Any]:
        data = json.dumps(payload).encode("utf-8")
        req = Request(
            self.config.base_url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._api_key}",
            },
        )
        try:
            with urlopen(req, timeout=self.config.timeout_s) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code}: {body[:500]}") from exc
        except URLError as exc:
            raise RuntimeError(f"Connection error: {exc.reason}") from exc


class GeminiProvider(BaseProvider):
    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        contents: list[dict[str, Any]] = []
        system_instruction: str | None = None

        for msg in messages:
            role = msg["role"]
            if role == "system":
                system_instruction = msg["content"]
                continue
            parts = [{"text": msg["content"]}]
            if role == "assistant":
                contents.append({"role": "model", "parts": parts})
            else:
                contents.append({"role": "user", "parts": parts})

        payload: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.7),
                "maxOutputTokens": kwargs.get("max_tokens", 4096),
            },
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        result = self._http_post(payload)
        return result["candidates"][0]["content"]["parts"][0]["text"]


class DeepSeekProvider(BaseProvider):
    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4096),
        }
        result = self._http_post(payload)
        return result["choices"][0]["message"]["content"]


class GroqProvider(DeepSeekProvider):
    pass


_PROVIDER_REGISTRY: dict[str, type[BaseProvider]] = {
    "gemini": GeminiProvider,
    "deepseek": DeepSeekProvider,
    "groq": GroqProvider,
}


class ProviderFactory:
    """
    Fabrica de provedores LLM com fallback automatico.

    Uso:
        factory = ProviderFactory([
            ProviderConfig(name="gemini", api_key_env="GEMINI_API_KEY",
                           base_url="https://generativelanguage.googleapis.com/...",
                           model="gemini-2.0-flash", priority=0),
            ProviderConfig(name="deepseek", api_key_env="DEEPSEEK_API_KEY",
                           base_url="https://api.deepseek.com/v1/chat/completions",
                           model="deepseek-chat", priority=1),
        ])
        response = factory.chat([{"role": "user", "content": "Ola"}])
    """

    def __init__(self, configs: list[ProviderConfig]) -> None:
        sorted_cfgs = sorted(configs, key=lambda c: c.priority)
        self._providers: list[BaseProvider] = []
        for cfg in sorted_cfgs:
            cls = _PROVIDER_REGISTRY.get(cfg.name)
            if cls is None:
                logger.warning("Provider desconhecido: %s — ignorado", cfg.name)
                continue
            provider = cls(cfg)
            if provider.available:
                self._providers.append(provider)
                logger.info(
                    "Provider registrado: %s (prioridade %d)", cfg.name, cfg.priority
                )
            else:
                logger.info(
                    "Provider %s sem API key — pulado (env: %s)",
                    cfg.name,
                    cfg.api_key_env,
                )

        if not self._providers:
            raise RuntimeError(
                "Nenhum provider disponivel. Verifique as variaveis de ambiente."
            )

    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        last_error: Exception | None = None
        for provider in self._providers:
            for attempt in range(provider.config.max_retries + 1):
                try:
                    return provider.chat(messages, **kwargs)
                except Exception as exc:
                    last_error = exc
                    logger.warning(
                        "Provider %s falhou (tentativa %d/%d): %s",
                        provider.config.name,
                        attempt + 1,
                        provider.config.max_retries + 1,
                        exc,
                    )
                    if attempt < provider.config.max_retries:
                        delay = BACKOFF_BASE ** (attempt + 1)
                        time.sleep(delay)
            logger.error(
                "Provider %s esgotou retries — passando ao fallback",
                provider.config.name,
            )

        raise RuntimeError(
            f"Todos os providers falharam. Ultimo erro: {last_error}"
        )

    @classmethod
    def from_env(cls, prefix: str = "LLM_") -> "ProviderFactory":
        """
        Constroi a fabrica a partir de variaveis de ambiente.

        Formato esperado:
          LLM_PROVIDERS=gemini,deepseek
          LLM_GEMINI_API_KEY=...
          LLM_GEMINI_MODEL=gemini-2.0-flash
          LLM_GEMINI_PRIORITY=0
          LLM_DEEPSEEK_API_KEY=...
          LLM_DEEPSEEK_MODEL=deepseek-chat
          LLM_DEEPSEEK_PRIORITY=1
        """
        names = os.environ.get(f"{prefix}PROVIDERS", "gemini").split(",")
        configs: list[ProviderConfig] = []
        base_urls: dict[str, str] = {
            "gemini": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            "deepseek": "https://api.deepseek.com/v1/chat/completions",
            "groq": "https://api.groq.com/openai/v1/chat/completions",
        }
        for name in names:
            name = name.strip()
            api_key = os.environ.get(f"{prefix}{name.upper()}_API_KEY", "")
            model = os.environ.get(
                f"{prefix}{name.upper()}_MODEL",
                {"gemini": "gemini-2.0-flash", "deepseek": "deepseek-chat", "groq": "llama-3.3-70b"}.get(name, ""),
            )
            priority = int(os.environ.get(f"{prefix}{name.upper()}_PRIORITY", "0"))
            base_url_template = base_urls.get(name, "")
            base_url = os.environ.get(
                f"{prefix}{name.upper()}_BASE_URL",
                base_url_template.format(model=model, key="${API_KEY}"),
            )

            configs.append(
                ProviderConfig(
                    name=name,
                    api_key_env=f"{prefix}{name.upper()}_API_KEY",
                    base_url=base_url,
                    model=model,
                    priority=priority,
                )
            )
        return cls(configs)

    def register_provider(
        self, name: str, cls: type[BaseProvider]
    ) -> None:
        _PROVIDER_REGISTRY[name] = cls
        logger.info("Provider type '%s' registrado no registry global", name)
