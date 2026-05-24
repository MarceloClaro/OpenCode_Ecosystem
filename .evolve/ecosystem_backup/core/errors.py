"""
core/errors.py — Hierarquia de Exceções do Ecossistema OpenCode.

Todas as exceções do sistema herdam de OpenCodeError, permitindo
captura uniforme e categorização por código + HTTP status.
Facilita debugging, logging estruturado e respostas de API.
"""

from __future__ import annotations

from typing import Any, Optional


class OpenCodeError(Exception):
    """Exceção base para todos os erros do OpenCode.

    Attributes:
        code: Código textual do erro (ex: ``CONFIG_ERROR``).
        http_status: Status HTTP sugerido para respostas de API.
        message: Mensagem descritiva do erro.
        original: Exceção original que causou este erro (encadeamento).
        details: Dict com informações contextuais adicionais.
    """

    code: str = "OPENCODE_ERROR"
    http_status: int = 500

    def __init__(
        self,
        message: str = "",
        *,
        original: Optional[Exception] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        self._original = original
        self._details = details or {}
        super().__init__(message)

    @property
    def message(self) -> str:
        return str(self.args[0]) if self.args else ""

    @property
    def original(self) -> Optional[Exception]:
        return self._original

    @property
    def details(self) -> dict[str, Any]:
        return self._details

    def __str__(self) -> str:
        parts = [f"[{self.code}]"]
        if self.message:
            parts.append(self.message)
        if self._original:
            parts.append(f"(caused by: {self._original})")
        return " ".join(parts)


# ── Configuração ───────────────────────────────────────────────────


class ConfigError(OpenCodeError):
    """Erro de configuração — variável de ambiente ausente, valor inválido."""
    code = "CONFIG_ERROR"
    http_status = 500


# ── Estado / Persistência ──────────────────────────────────────────


class StateError(OpenCodeError):
    """Erro de persistência de estado — SQLite, JSON file, etc."""
    code = "STATE_ERROR"
    http_status = 500


# ── Cache ──────────────────────────────────────────────────────────


class CacheError(OpenCodeError):
    """Erro no cache — TTL, espaço em disco, serialização."""
    code = "CACHE_ERROR"
    http_status = 500


# ── Validação ──────────────────────────────────────────────────────


class ValidationError(OpenCodeError):
    """Erro de validação — input inválido, schema incorreto, campo obrigatório."""
    code = "VALIDATION_ERROR"
    http_status = 400


# ── Recurso ────────────────────────────────────────────────────────


class NotFoundError(OpenCodeError):
    """Recurso solicitado não encontrado."""
    code = "NOT_FOUND"
    http_status = 404


class DuplicateError(OpenCodeError):
    """Recurso duplicado — conflito com estado existente."""
    code = "DUPLICATE"
    http_status = 409


# ── Serviço ────────────────────────────────────────────────────────


class ServiceError(OpenCodeError):
    """Erro interno de serviço — falha inesperada em lógica de negócio."""
    code = "SERVICE_ERROR"
    http_status = 500


class IntegrationError(OpenCodeError):
    """Erro de integração externa — HTTP, API de terceiros, provedor."""
    code = "INTEGRATION_ERROR"
    http_status = 502


# ── Plugin ─────────────────────────────────────────────────────────


class PluginError(OpenCodeError):
    """Erro no ciclo de vida de plugins — carga, registro, execução."""
    code = "PLUGIN_ERROR"
    http_status = 500


# ── Agente ─────────────────────────────────────────────────────────


class AgentError(OpenCodeError):
    """Erro no ciclo de vida de agentes — inicialização, execução, destruição."""
    code = "AGENT_ERROR"
    http_status = 500


# ── Skill ──────────────────────────────────────────────────────────


class SkillError(OpenCodeError):
    """Erro no carregamento ou execução de skills."""
    code = "SKILL_ERROR"
    http_status = 500


# ── Rede / Timeout ─────────────────────────────────────────────────


class TimeoutError(OpenCodeError):
    """Tempo limite de operação excedido."""
    code = "TIMEOUT"
    http_status = 504


class RateLimitError(OpenCodeError):
    """Limite de taxa excedido (HTTP 429)."""
    code = "RATE_LIMIT"
    http_status = 429


# ── Autenticação / Autorização ─────────────────────────────────────


class AuthenticationError(OpenCodeError):
    """Falha de autenticação — credenciais inválidas ou ausentes."""
    code = "AUTH_ERROR"
    http_status = 401


class AuthorizationError(OpenCodeError):
    """Falha de autorização — permissão negada."""
    code = "FORBIDDEN"
    http_status = 403
