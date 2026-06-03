"""
TDD tests for ProviderFactory — Multi-LLM provider com fallback automatico.
CT-1: test_register — registrar e recuperar provedor do registry global
CT-2: test_get — instanciar ProviderFactory e validar providers disponiveis
CT-3: test_fallback — chat com fallback automatico entre providers
CT-4: test_available — verificar disponibilidade via variavel de ambiente
"""

import os
import pytest
import sys

SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, SCRIPT_DIR)

from provider_factory import ProviderFactory, ProviderConfig, BaseProvider, _PROVIDER_REGISTRY


class DummyProvider(BaseProvider):
    def chat(self, messages, **kwargs):
        return f"dummy: {messages[-1]['content']}"


class FailProvider(BaseProvider):
    def __init__(self, config):
        super().__init__(config)
        self._api_key = "fake-key"

    def chat(self, messages, **kwargs):
        raise RuntimeError("falha simulada")


class TestProviderFactory:

    def test_register(self):
        _PROVIDER_REGISTRY["dummy_test"] = DummyProvider
        assert "dummy_test" in _PROVIDER_REGISTRY
        assert _PROVIDER_REGISTRY["dummy_test"] is DummyProvider

    def test_get(self):
        cfg = ProviderConfig(
            name="dummy_test",
            api_key_env="DUMMY_API_KEY",
            base_url="https://fake.api/v1",
            model="dummy-v1",
            priority=0,
        )
        _PROVIDER_REGISTRY["dummy_test"] = DummyProvider
        os.environ["DUMMY_API_KEY"] = "test-key"

        factory = ProviderFactory([cfg])
        assert len(factory._providers) == 1
        assert factory._providers[0].available is True

    def test_fallback(self):
        cfg_primary = ProviderConfig(
            name="dummy_test", api_key_env="PRIMARY_KEY",
            base_url="https://fake.api/v1", model="dummy-v1", priority=0,
        )
        cfg_fallback = ProviderConfig(
            name="dummy_test", api_key_env="FALLBACK_KEY",
            base_url="https://fake.api/v2", model="dummy-v2", priority=1,
        )
        _PROVIDER_REGISTRY["dummy_test"] = DummyProvider
        os.environ["PRIMARY_KEY"] = "key-1"
        os.environ["FALLBACK_KEY"] = "key-2"

        factory = ProviderFactory([cfg_primary, cfg_fallback])
        assert len(factory._providers) == 2

        result = factory.chat([{"role": "user", "content": "ola"}])
        assert "dummy:" in result

    def test_available(self):
        cfg = ProviderConfig(
            name="dummy_test", api_key_env="NONEXISTENT_KEY",
            base_url="https://fake.api/v1", model="dummy-v1", priority=0,
        )
        _PROVIDER_REGISTRY["dummy_test"] = DummyProvider

        if "NONEXISTENT_KEY" in os.environ:
            del os.environ["NONEXISTENT_KEY"]

        with pytest.raises(RuntimeError, match="Nenhum provider disponivel"):
            ProviderFactory([cfg])
