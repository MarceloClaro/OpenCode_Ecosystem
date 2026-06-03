"""CTs para Document Generator Engine -- 4 testes criticos de geracao de documentos."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from document_generator_engine import Template, OutputFormat, Document, DocumentGenerator


def test_ct1_template_variable_extraction():
    """CT-01: Extracao automatica de variaveis do template."""
    template = Template(
        name="invoice",
        content="Fatura #{{number}}\nCliente: {{client_name}}\nValor: R$ {{amount}}",
        format=OutputFormat.PLAIN,
    )

    assert template.required_vars == {"number", "client_name", "amount"}
    assert template.has_unresolved is True


def test_ct2_template_filling():
    """CT-02: Preenchimento de template substitui todas as variaveis."""
    template = Template(
        name="report",
        content="Relatorio: {{title}}\nData: {{date}}\nAutor: {{author}}",
    )

    filled = template.fill({
        "title": "Vendas Q4",
        "date": "2026-06-03",
        "author": "Sistema",
    })

    assert "{{" not in filled
    assert "Vendas Q4" in filled
    assert "2026-06-03" in filled
    assert "Sistema" in filled


def test_ct3_document_generation_pipeline():
    """CT-03: Pipeline completo de registro e geracao de documento."""
    gen = DocumentGenerator()
    template = Template(
        name="welcome_email",
        content="Ola {{user_name}},\n\nBem-vindo ao {{platform_name}}!\n\nEquipe {{team}}",
    )

    ok = gen.register_template(template)
    assert ok is True
    assert gen.template_count == 1

    doc = gen.generate("welcome_email", {
        "user_name": "Marcelo",
        "platform_name": "OpenCode",
        "team": "AI Engineering",
    })

    assert doc is not None
    assert doc.template_name == "welcome_email"
    assert "Marcelo" in doc.content
    assert "OpenCode" in doc.content
    assert doc.word_count > 3
    assert doc.has_metadata is True


def test_ct4_missing_variable_detection():
    """CT-04: Deteccao de variaveis faltantes antes da geracao."""
    gen = DocumentGenerator()
    gen.register_template(Template(
        name="contract",
        content="CONTRATO #{{contract_id}}\nParte A: {{party_a}}\nParte B: {{party_b}}\nValor: {{value}}",
    ))

    missing = gen.check_missing_vars("contract", {"contract_id", "party_a"})
    assert missing == ["party_b", "value"]

    missing = gen.check_missing_vars("contract", {"contract_id", "party_a", "party_b", "value"})
    assert missing == []

    doc = gen.generate("contract", {
        "contract_id": "C-001",
        "party_a": "Empresa A",
        "party_b": "Empresa B",
        "value": "R$ 50.000,00",
    })
    assert doc is not None
    assert "C-001" in doc.content
    assert "{{" not in doc.content
