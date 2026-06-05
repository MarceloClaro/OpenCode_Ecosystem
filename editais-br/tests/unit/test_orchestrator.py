"""Testes do OrchestratorAgent — Issue #20."""

from unittest.mock import MagicMock

from worker.connectors.base import EditalRaw


def test_base_agent_existe_e_eh_abc():
    """BaseAgent deve existir, ser ABC, com model e execute()."""
    from abc import ABC

    from agents.base import BaseAgent

    assert issubclass(BaseAgent, ABC)
    assert hasattr(BaseAgent, "model")
    assert hasattr(BaseAgent, "api_key")
    assert hasattr(BaseAgent, "execute")


def test_orchestrator_existe():
    """OrchestratorAgent deve ser importável."""


def make_connector_mock(editais=None):
    """Cria um conector mockado."""
    connector = MagicMock()
    connector.mode = "http"
    connector.base_url = "https://exemplo.com"
    connector.crawl_interval_hours = 24
    connector.fetch_editais.return_value = editais or [
        EditalRaw(
            titulo="Edital Teste",
            url="https://exemplo.com/edital/1",
            pdf_url="https://exemplo.com/edital/1.pdf",
            data_publicacao="2026-05-08",
        )
    ]
    return connector


def make_extractor_mock():
    """Cria um extrator mockado."""
    extractor = MagicMock()
    extractor.extract.return_value = "Texto extraído do edital."
    return extractor


def make_agent_mock():
    """Cria um agente IA mockado."""
    agent = MagicMock()
    agent.model = "deepseek-v4-flash"
    agent.api_key = "sk-test"
    agent.execute.return_value = {"titulo": "Edital Teste", "resumo": "Mockado"}
    return agent


class TestOrchestratorRun:
    """Testes do método run() do OrchestratorAgent."""

    def test_run_chama_fetch_editais(self):
        """run() deve chamar connector.fetch_editais()."""
        from pipeline.orchestrator import OrchestratorAgent

        connector = make_connector_mock()
        extractor = make_extractor_mock()
        agent = make_agent_mock()

        orch = OrchestratorAgent(
            connector=connector,
            extractor=extractor,
            agent=agent,
        )

        resultados = orch.run()
        connector.fetch_editais.assert_called_once()
        assert len(resultados) == 1

    def test_run_com_deduplicacao(self):
        """Editais duplicados (mesma URL) devem ser removidos."""
        from pipeline.orchestrator import OrchestratorAgent

        connector = make_connector_mock(editais=[
            EditalRaw(titulo="A", url="https://x.com/1"),
            EditalRaw(titulo="B", url="https://x.com/1"),  # duplicata
            EditalRaw(titulo="C", url="https://x.com/2"),
        ])
        extractor = make_extractor_mock()
        agent = make_agent_mock()

        orch = OrchestratorAgent(
            connector=connector,
            extractor=extractor,
            agent=agent,
        )

        resultados = orch.run()
        # 3 raw, mas 2 únicos (A e C)
        assert len(resultados) == 2

    def test_run_extrai_pdf_quando_pdf_url_existe(self):
        """Quando edital tem pdf_url, deve chamar extractor.extract()."""
        from pipeline.orchestrator import OrchestratorAgent

        connector = make_connector_mock()
        extractor = make_extractor_mock()
        agent = make_agent_mock()

        orch = OrchestratorAgent(
            connector=connector,
            extractor=extractor,
            agent=agent,
        )

        orch.run()
        # PDF URL existe → extractor deve ser chamado
        extractor.extract.assert_called()

    def test_run_chama_agente_para_analisar(self):
        """Após extrair, deve chamar agent.execute() com o texto."""
        from pipeline.orchestrator import OrchestratorAgent

        connector = make_connector_mock()
        extractor = make_extractor_mock()
        agent = make_agent_mock()

        orch = OrchestratorAgent(
            connector=connector,
            extractor=extractor,
            agent=agent,
        )

        orch.run()
        agent.execute.assert_called()
