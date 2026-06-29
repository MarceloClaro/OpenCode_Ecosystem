# -*- coding: utf-8 -*-
"""
Testes TDD para ARCHE Reasoning Logic Tree (R28 - SPEC-057)
12 CTs validando: mapeamento, construcao RLT, validacao, exportacao, pipeline OQS
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "system", "reasoning-orchestrator"))

from arche_rlt import (
    ARCHEEngine,
    ReasoningMapper,
    RLTBuilder,
    RLTValidator,
    RLTNode,
    PeirceType,
    LogicalCycleError,
    InvalidPremiseError,
)


# === CT-057-001: Mapear tipo dedutivo para DR ===
def test_ct057_001_map_deductive_to_dr():
    mapper = ReasoningMapper()
    result = mapper.map_reasoning_type("modus_ponens")
    assert result == PeirceType.DEDUCTION_RULE, (
        f"Esperado DR, obtido {result}"
    )


# === CT-057-002: Mapear tipo abdutivo para AK ===
def test_ct057_002_map_abductive_to_ak():
    mapper = ReasoningMapper()
    result = mapper.map_reasoning_type("abduction")
    assert result == PeirceType.ABDUCTION_KNOWLEDGE, (
        f"Esperado AK, obtido {result}"
    )


# === CT-057-003: Construir RLT com 3 nos ===
def test_ct057_003_build_rlt_3_nodes():
    builder = RLTBuilder()
    steps = [
        {"premise": "Todos os humanos sao mortais", "conclusion": "Socrates e humano", "inference_type": "deduction_rule"},
        {"premise": "Socrates e humano", "conclusion": "Socrates e mortal", "inference_type": "deduction_rule"},
        {"premise": "Socrates e mortal", "conclusion": "A mortalidade se aplica a Socrates", "inference_type": "deduction_case"},
    ]
    root = builder.build_from_steps(steps)
    assert root is not None, "Root nao pode ser None"
    assert root.count_nodes() == 3, f"Esperado 3 nos, obtido {root.count_nodes()}"
    assert root.depth() == 3, f"Esperado depth 3, obtido {root.depth()}"


# === CT-057-004: Validar coerencia RLT ===
def test_ct057_004_validate_coherent_rlt():
    builder = RLTBuilder()
    steps = [
        {"premise": "Experimentos mostram correlacao", "conclusion": "Efeito observado", "inference_type": "inductive"},
        {"premise": "Efeito observado repetidamente", "conclusion": "Relacao causal provavel", "inference_type": "causal_inductive"},
        {"premise": "Relacao causal provavel", "conclusion": "Teoria confirmada", "inference_type": "hypothetico_deductive"},
    ]
    root = builder.build_from_steps(steps)
    validator = RLTValidator()
    report = validator.validate(root)
    assert report["is_valid"] is True, f"RLT deveria ser valida: {report['issues']}"
    # Coherence gaps podem ocorrer com strings curtas
    assert report["total_nodes"] == 3


# === CT-057-005: Detectar incoerencia (conclusao nao alimenta pai) ===
def test_ct057_005_detect_incoherence():
    builder = RLTBuilder()
    # Passos com palavras totalmente desconexas
    steps = [
        {"premise": "O ceu e azul", "conclusion": "A grama e verde", "inference_type": "abduction"},
        {"premise": "Carros andam na rua", "conclusion": "Passaros voam no ceu", "inference_type": "abduction"},
    ]
    root = builder.build_from_steps(steps)
    validator = RLTValidator()
    report = validator.validate(root)
    # Deve detectar gaps de coerencia
    assert report["coherence_gaps"] > 0, "Deveria detectar gaps de coerencia"


# === CT-057-006: Profundidade maxima 10 ===
def test_ct057_006_max_depth_10():
    builder = RLTBuilder()
    # Criar 12 passos
    steps = []
    for i in range(12):
        steps.append({
            "premise": f"Premissa {i}: passo anterior",
            "conclusion": f"Conclusao {i}: passo atual",
            "inference_type": "deduction_rule",
        })
    root = builder.build_from_steps(steps)
    assert root.depth() <= 10, f"Profundidade {root.depth()} excede maximo 10"


# === CT-057-007: Mapeamento dos 59 tipos conhecidos ===
def test_ct057_007_map_all_known_types():
    engine = ARCHEEngine()
    result = engine.map_all_reasoning_types()
    assert result["total_types_mapped"] >= 59, (
        f"Deveria mapear 59+ tipos, mapeou {result['total_types_mapped']}"
    )
    # Verificar que todos os 6 tipos Peirce estao representados
    assert len(result["by_peirce_type"]) >= 6, (
        f"Deveria cobrir 6 tipos Peirce, cobriu {len(result['by_peirce_type'])}"
    )


# === CT-057-008: Exportar RLT como JSON ===
def test_ct057_008_export_json():
    engine = ARCHEEngine()
    steps = [
        {"premise": "Premissa A", "conclusion": "Conclusao A", "inference_type": "deduction_rule"},
        {"premise": "Conclusao A", "conclusion": "Conclusao B", "inference_type": "inductive"},
        {"premise": "Conclusao B", "conclusion": "Conclusao C", "inference_type": "abduction"},
    ]
    result = engine.analyze_reasoning_chain(steps)
    rlt_json = json.dumps(result["rlt"], indent=2)
    parsed = json.loads(rlt_json)
    assert "id" in parsed, "JSON deve conter 'id'"
    assert "inference_type" in parsed, "JSON deve conter 'inference_type'"
    assert "children" in parsed, "JSON deve conter 'children'"
    assert len(parsed["children"]) >= 1, "Deve ter pelo menos 1 filho"


# === CT-057-009: Inferencia composta DR -> IC -> AK ===
def test_ct057_009_compound_inference():
    engine = ARCHEEngine()
    steps = [
        {"premise": "Dados observados: 10 casos", "conclusion": "Padrao identificado", "inference_type": "inductive"},
        {"premise": "Padrao identificado na amostra", "conclusion": "Regra geral formulada", "inference_type": "induction_common"},
        {"premise": "Regra geral aplicada ao novo caso", "conclusion": "Explicacao para o fenomeno", "inference_type": "abduction_knowledge"},
    ]
    result = engine.analyze_reasoning_chain(steps)
    types_used = result["validation"]["inference_types_used"]
    assert len(types_used) >= 2, (
        f"Deveria usar 2+ tipos, usou {types_used}"
    )


# === CT-057-010: RLT com confidence score propagado ===
def test_ct057_010_confidence_propagation():
    engine = ARCHEEngine()
    steps = [
        {"premise": "Fonte confiavel: 95% certo", "conclusion": "Dado A confirmado", "inference_type": "deduction_rule", "confidence": 0.95},
        {"premise": "Dado A e consistente", "conclusion": "Hipotese B suportada", "inference_type": "abduction_knowledge", "confidence": 0.85},
        {"premise": "Hipotese B explica os dados", "conclusion": "Teoria C e a melhor explicacao", "inference_type": "abduction_knowledge", "confidence": 0.80},
    ]
    result = engine.analyze_reasoning_chain(steps)
    assert result["root_confidence"] > 0, "Confianca deve ser > 0"
    assert result["root_confidence"] <= 1.0, "Confianca deve ser <= 1.0"
    # Confianca deve ser menor que a maxima dos filhos (propagacao multiplicativa)
    assert result["root_confidence"] < 0.95, (
        f"Confianca propagada {result['root_confidence']} deve ser menor que 0.95"
    )


# === CT-057-011: Detectar ciclo logico ===
def test_ct057_011_detect_logical_cycle():
    builder = RLTBuilder()
    import pytest
    # Premissa igual a conclusao (ciclo)
    steps = [
        {"premise": "Isto e um ciclo logico muito longo para ser detectado", "conclusion": "Isto e um ciclo logico muito longo para ser detectado", "inference_type": "deduction_rule"},
    ]
    with pytest.raises(LogicalCycleError):
        builder.build_from_steps(steps)


# === CT-057-012: Pipeline OQS -> ARCHE RLT ===
def test_ct057_012_pipeline_oqs_to_rlt():
    engine = ARCHEEngine()
    oqs_result = {
        "optimal_question": "Como a polimatia influencia a resiliencia cognitiva em ambientes de alta incerteza?",
        "uncertainty_categories": ["epistemica", "semantica", "metodologica"],
        "convergence_score": 0.87,
    }
    result = engine.pipeline_oqs_to_rlt(oqs_result)
    assert "optimal_question" in result, "Deve conter a pergunta otima"
    assert "rlt" in result, "Deve conter a RLT"
    assert "validation" in result, "Deve conter validacao"
    assert "convergence_score" in result, "Deve conter convergence score"
    assert result["pipeline"] == "OQS -> ARCHE RLT", "Pipeline deve ser OQS -> ARCHE RLT"


# === CT-057-013 (extra): Entrada invalida ===
def test_ct057_013_invalid_input_raises_error():
    builder = RLTBuilder()
    import pytest
    with pytest.raises(InvalidPremiseError):
        builder.build_from_steps([])


# === CT-057-014 (extra): Build from premises ===
def test_ct057_014_build_from_premises():
    builder = RLTBuilder()
    root = builder.build_from_premises(
        premises=["Dado 1: temperatura aumenta", "Dado 2: pressao aumenta", "Dado 3: volume constante"],
        conclusion="Lei dos Gases Ideais se aplica",
        inference_type="induction_common",
    )
    assert root is not None, "Root nao pode ser None"
    assert root.count_nodes() >= 2, f"Esperado 2+ nos, obtido {root.count_nodes()}"
    assert root.conclusion == "Lei dos Gases Ideais se aplica"


# === CT-057-015 (extra): Mermaid export ===
def test_ct057_015_export_mermaid():
    builder = RLTBuilder()
    steps = [
        {"premise": "P1", "conclusion": "C1", "inference_type": "deduction_rule"},
        {"premise": "C1", "conclusion": "C2", "inference_type": "inductive"},
    ]
    root = builder.build_from_steps(steps)
    mermaid = builder.to_mermaid(root)
    assert "graph TD" in mermaid, "Mermaid deve comecar com 'graph TD'"
    assert "-->" in mermaid, "Mermaid deve conter conexoes '-->'"
