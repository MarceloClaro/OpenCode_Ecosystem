"""
Testes da Hierarquia de Excecoes (core/errors.py)

Cobre:
- OpenCodeError base: code, http_status, message, original, details
- 15 subclasses com seus codigos e HTTP status
- Encadeamento de excecoes (original)
- __str__ formatacao
"""

import pytest

from core.errors import (
    OpenCodeError,
    ConfigError,
    StateError,
    CacheError,
    ValidationError,
    NotFoundError,
    DuplicateError,
    ServiceError,
    IntegrationError,
    PluginError,
    AgentError,
    SkillError,
    TimeoutError,
    RateLimitError,
    AuthenticationError,
    AuthorizationError,
)


class TestOpenCodeErrorBase:
    """Testa a excecao base do ecossistema."""

    def test_default_attributes(self):
        err = OpenCodeError()
        assert err.code == "OPENCODE_ERROR"
        assert err.http_status == 500
        assert err.message == ""
        assert err.original is None
        assert err.details == {}

    def test_with_message(self):
        err = OpenCodeError("algo deu errado")
        assert err.message == "algo deu errado"
        assert "algo deu errado" in str(err)

    def test_with_original_exception(self):
        original = ValueError("valor invalido")
        err = OpenCodeError("falhou", original=original)
        assert err.original is original
        assert "caused by" in str(err)
        assert "valor invalido" in str(err)

    def test_with_details(self):
        err = OpenCodeError("erro", details={"key": "x", "code": 42})
        assert err.details == {"key": "x", "code": 42}

    def test_str_formatting(self):
        err = OpenCodeError("mensagem")
        assert "[OPENCODE_ERROR]" in str(err)
        assert "mensagem" in str(err)

    def test_str_with_all_parts(self):
        orig = ValueError("orig")
        err = OpenCodeError("msg", original=orig, details={"k": "v"})
        s = str(err)
        assert "[OPENCODE_ERROR]" in s
        assert "msg" in s
        assert "orig" in s

    def test_empty_message_via_args(self):
        err = OpenCodeError()
        assert err.message == ""


class TestExceptionHierarchy:
    """Testa todas as 15 subclasses + base = 16 excecoes."""

    @pytest.mark.parametrize("exc_class,expected_code,expected_http", [
        (ConfigError, "CONFIG_ERROR", 500),
        (StateError, "STATE_ERROR", 500),
        (CacheError, "CACHE_ERROR", 500),
        (ValidationError, "VALIDATION_ERROR", 400),
        (NotFoundError, "NOT_FOUND", 404),
        (DuplicateError, "DUPLICATE", 409),
        (ServiceError, "SERVICE_ERROR", 500),
        (IntegrationError, "INTEGRATION_ERROR", 502),
        (PluginError, "PLUGIN_ERROR", 500),
        (AgentError, "AGENT_ERROR", 500),
        (SkillError, "SKILL_ERROR", 500),
        (TimeoutError, "TIMEOUT", 504),
        (RateLimitError, "RATE_LIMIT", 429),
        (AuthenticationError, "AUTH_ERROR", 401),
        (AuthorizationError, "FORBIDDEN", 403),
    ])
    def test_code_and_http_status(self, exc_class, expected_code, expected_http):
        err = exc_class("test message")
        assert err.code == expected_code
        assert err.http_status == expected_http
        assert err.message == "test message"

    def test_all_are_opencode_error_subclasses(self):
        exceptions = [
            ConfigError, StateError, CacheError, ValidationError,
            NotFoundError, DuplicateError, ServiceError, IntegrationError,
            PluginError, AgentError, SkillError, TimeoutError,
            RateLimitError, AuthenticationError, AuthorizationError,
        ]
        for exc in exceptions:
            assert issubclass(exc, OpenCodeError)

    def test_all_have_different_codes(self):
        codes = [
            ConfigError, StateError, CacheError, ValidationError,
            NotFoundError, DuplicateError, ServiceError, IntegrationError,
            PluginError, AgentError, SkillError, TimeoutError,
            RateLimitError, AuthenticationError, AuthorizationError,
        ]
        unique_codes = {e.code for e in codes}
        assert len(unique_codes) == len(codes)


class TestStrRepresentation:
    """Testa a representacao em string das excecoes."""

    def test_basic_str(self):
        err = ValidationError("campo obrigatorio")
        s = str(err)
        assert "[VALIDATION_ERROR]" in s
        assert "campo obrigatorio" in s

    def test_with_original_in_str(self):
        err = NotFoundError("nao encontrado", original=KeyError("x"))
        s = str(err)
        assert "[NOT_FOUND]" in s
        assert "nao encontrado" in s
        assert "KeyError" in s or "x" in s


class TestExceptionChaining:
    """Testa encadeamento de excecoes."""

    def test_raise_from_original(self):
        try:
            try:
                raise ValueError("erro interno")
            except ValueError as e:
                raise ConfigError("configuracao invalida", original=e) from e
        except ConfigError as e:
            assert e.original is not None
            assert isinstance(e.original, ValueError)
            assert str(e.original) == "erro interno"

    def test_details_preserved_across_chain(self):
        details = {"file": "config.yaml", "line": 42}
        try:
            raise StateError("falha ao ler", details=details)
        except StateError as e:
            assert e.details == details
