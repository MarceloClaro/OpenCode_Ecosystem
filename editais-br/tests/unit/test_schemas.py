"""Testes do schema EditalRequisitos — Issue #21."""

from datetime import date

import pytest
from pydantic import ValidationError


def test_edital_requisitos_com_dados_minimos():
    """Deve criar com dados mínimos obrigatórios."""
    from api.schemas.edital import EditalRequisitos

    edital = EditalRequisitos(
        titulo="Edital Teste",
        financiador="FAPEG",
        url_original="https://exemplo.com/edital/1",
    )
    assert edital.titulo == "Edital Teste"
    assert edital.financiador == "FAPEG"
    assert edital.moeda == "BRL"
    assert edital.score_complexidade == 1


def test_edital_requisitos_com_todos_os_campos():
    """Deve aceitar todos os campos preenchidos."""
    from api.schemas.edital import AbrangenciaGeografica, EditalRequisitos

    edital = EditalRequisitos(
        titulo="Chamada Pública FAPEG 01/2026",
        financiador="FAPEG",
        url_original="https://fapeg.go.gov.br/chamada/01-2026",
        valor_min=100000.0,
        valor_max=500000.0,
        moeda="BRL",
        data_abertura=date(2026, 5, 1),
        data_encerramento=date(2026, 7, 31),
        eixos_tematicos=["tecnologia", "inovacao"],
        perfil_elegivel=["ict", "startup_early_stage"],
        mecanismo_financiamento="subvencao_economica",
        abrangencia_geografica=AbrangenciaGeografica(
            tipo="estadual",
            estados=["GO"],
        ),
        status="inscricoes_abertas",
        nivel_trl_min=3,
        nivel_trl_max=7,
        temas=["IA", "machine learning"],
        requisitos_obrigatorios=["CNPJ ativo", "Equipe mínima de 3 pessoas"],
        documentos_necessarios=["Projeto de pesquisa", "Currículo Lattes"],
        contrapartida_exigida=True,
        resumo="Edital de fomento à pesquisa aplicada em IA.",
        score_complexidade=3,
    )
    assert edital.valor_min == 100000.0
    assert edital.status == "inscricoes_abertas"
    assert edital.abrangencia_geografica.tipo == "estadual"


def test_trl_fora_do_range_lanca_erro():
    """TRL deve estar entre 1 e 9."""
    from api.schemas.edital import EditalRequisitos

    with pytest.raises(ValidationError):
        EditalRequisitos(
            titulo="X",
            financiador="Y",
            url_original="https://z.com",
            nivel_trl_min=0,  # inválido
        )

    with pytest.raises(ValidationError):
        EditalRequisitos(
            titulo="X",
            financiador="Y",
            url_original="https://z.com",
            nivel_trl_max=10,  # inválido
        )


def test_score_complexidade_fora_do_range_lanca_erro():
    """Score deve estar entre 1 e 5."""
    from api.schemas.edital import EditalRequisitos

    with pytest.raises(ValidationError):
        EditalRequisitos(
            titulo="X",
            financiador="Y",
            url_original="https://z.com",
            score_complexidade=6,
        )


def test_abrangencia_geografica_valida():
    """AbrangenciaGeografica deve validar os tipos."""
    from api.schemas.edital import AbrangenciaGeografica

    a = AbrangenciaGeografica(
        tipo="nacional",
        regioes=["sudeste", "nordeste"],
    )
    assert a.tipo == "nacional"
    assert "sudeste" in a.regioes

    b = AbrangenciaGeografica(
        tipo="municipal",
        estados=["SP"],
        municipios=["Campinas"],
    )
    assert b.tipo == "municipal"
