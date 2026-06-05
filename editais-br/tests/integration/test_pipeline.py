"""Testes de integração — Issue #44.

Requer: Docker com PostgreSQL e Redis rodando.
Executar: pytest tests/integration/ -v -m integration
"""

import os
import pytest
from pathlib import Path

pytestmark = pytest.mark.integration


@pytest.fixture
def db_session():
    """Sessão de banco real (PostgreSQL via Docker)."""
    from api.database import engine, Base, SessionLocal

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_seed_script_popula_banco(db_session):
    """Seed script deve popular banco com editais."""
    from api.models.edital import Edital
    from worker.connectors.prosas import ProsasConnector
    from pipeline.deduplicator import deduplicate

    fixture = Path(__file__).parents[1] / "fixtures" / "prosas_editais.html"
    assert fixture.exists(), "Fixture HTML não encontrado"

    html = fixture.read_text()
    connector = ProsasConnector()
    raw_editais = connector.parse(html)

    assert len(raw_editais) == 5, f"Esperado 5 editais, encontrado {len(raw_editais)}"

    # Deduplicação
    raw_dicts = [
        {"titulo": e.titulo, "url_original": e.url, "pdf_url": e.pdf_url, "data_publicacao": e.data_publicacao}
        for e in raw_editais
    ]
    unique = deduplicate(raw_dicts)
    assert len(unique) == 4, f"Deduplicação: esperado 4, encontrado {len(unique)}"

    # Salva no banco
    from api.models.portal import Portal
    portal = db_session.query(Portal).filter(Portal.nome == "prosas").first()
    if not portal:
        portal = Portal(nome="prosas", base_url="https://prosas.com.br/editais", mode="http")
        db_session.add(portal)
        db_session.flush()

    for data in unique:
        edital = Edital(
            portal_id=portal.id,
            titulo=data["titulo"],
            url_original=data["url_original"],
            status="extraido",
            raw_text=f"Texto do edital: {data['titulo']}",
        )
        db_session.add(edital)

    db_session.commit()

    count = db_session.query(Edital).count()
    assert count == 4, f"Esperado 4 no banco, encontrado {count}"


def test_pipeline_completo_com_seed(db_session):
    """Pipeline: seed → dedup → save → query funciona."""
    from api.models.edital import Edital
    from api.models.portal import Portal

    # Cadastra portal
    if not db_session.query(Portal).filter(Portal.nome == "prosas").first():
        db_session.add(Portal(nome="prosas", base_url="https://prosas.com.br/editais", mode="http"))
        db_session.commit()

    # Insere edital manual
    edital = Edital(
        portal_id=db_session.query(Portal).first().id,
        titulo="Edital de Teste Integração",
        url_original="https://prosas.com.br/editais/test-integration",
        status="analisado",
        raw_text="Texto de teste",
        valor_min=50000,
        valor_max=200000,
        eixos_tematicos=["tecnologia"],
        perfil_elegivel=["startup_early_stage"],
        status_inscricao="inscricoes_abertas",
    )
    db_session.add(edital)
    db_session.commit()

    # Query com filtros
    query = db_session.query(Edital).filter(
        Edital.eixos_tematicos.contains(["tecnologia"])
    )
    results = query.all()
    assert len(results) >= 1
    assert results[0].titulo == "Edital de Teste Integração"


@pytest.mark.skipif(not os.getenv("DEEPSEEK_API_KEY"), reason="DEEPSEEK_API_KEY não configurada")
def test_agente_deepseek_real():
    """Teste de integração com DeepSeek real."""
    from agents.extractor import ExtractorAgent

    agent = ExtractorAgent(api_key=os.getenv("DEEPSEEK_API_KEY", ""))

    texto = """
    CHAMADA PÚBLICA 01/2026 - Fomento à pesquisa
    Valor: R$ 50.000 a R$ 200.000
    Inscrições: 01/01/2026 a 31/03/2026
    Área: Tecnologia e Inovação
    Perfil: ICTs e startups early stage
    """

    result = agent.execute(texto)
    assert isinstance(result, dict), "Agente deve retornar dict"
    assert len(result) > 0, "Agente deve retornar dados"
