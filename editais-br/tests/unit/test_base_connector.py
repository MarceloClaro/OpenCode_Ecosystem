"""Testes do BaseConnector — Issue #4."""

from abc import ABC
from dataclasses import fields

import pytest


def test_editalraw_eh_dataclass():
    """EditalRaw deve ser um dataclass."""
    from worker.connectors.base import EditalRaw

    edital = EditalRaw(
        titulo="Edital Teste",
        url="https://exemplo.com/edital",
        pdf_url=None,
        data_publicacao="2026-05-08",
    )
    assert edital.titulo == "Edital Teste"
    assert edital.url == "https://exemplo.com/edital"
    assert edital.pdf_url is None
    assert edital.data_publicacao == "2026-05-08"


def test_base_connector_eh_abc():
    """BaseConnector deve ser uma classe abstrata."""
    from worker.connectors.base import BaseConnector

    assert issubclass(BaseConnector, ABC)


def test_base_connector_nao_pode_ser_instanciado_diretamente():
    """Não deve ser possível instanciar BaseConnector sem implementar métodos abstratos."""
    from worker.connectors.base import BaseConnector

    with pytest.raises(TypeError):
        BaseConnector()  # type: ignore


def test_subclasse_concreta_funciona():
    """Uma subclasse concreta que implementa os métodos abstratos deve funcionar."""
    from worker.connectors.base import BaseConnector, EditalRaw

    class MeuConector(BaseConnector):
        mode = "http"
        base_url = "https://exemplo.com"
        crawl_interval_hours = 24

        def fetch_editais(self) -> list[EditalRaw]:
            return [
                EditalRaw(
                    titulo="Edital 1",
                    url="https://exemplo.com/1",
                    pdf_url=None,
                    data_publicacao="2026-01-01",
                )
            ]

        def parse(self, content: str) -> list[EditalRaw]:
            return []

    connector = MeuConector()
    assert connector.mode == "http"
    assert connector.base_url == "https://exemplo.com"

    editais = connector.fetch_editais()
    assert len(editais) == 1
    assert editais[0].titulo == "Edital 1"


def test_editalraw_tem_todos_os_campos():
    """EditalRaw deve ter os 4 campos obrigatórios."""
    from worker.connectors.base import EditalRaw

    nomes_campos = {f.name for f in fields(EditalRaw)}
    obrigatorios = {"titulo", "url", "pdf_url", "data_publicacao"}
    assert obrigatorios.issubset(nomes_campos), f"Faltam: {obrigatorios - nomes_campos}"
