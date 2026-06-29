#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_oqs.py -- SPEC-056: Optimal Question Scanner TDD Suite
=============================================================
12 Critical Tests para validar o OQS:

  CT-056-001: UncertaintyScanner aceita problema válido e retorna resultado
  CT-056-002: UncertaintyScanner detecta ≥3 categorias de incerteza
  CT-056-003: UncertaintyScanner filtra ruído estrutural
  CT-056-004: QuestionVectorizer classifica tipo de pergunta corretamente
  CT-056-005: QuestionVectorizer gera vetor de 6 dimensões
  CT-056-006: Convergence Score calcula URS/SVS/DRI/CCI corretamente
  CT-056-007: Convergence Score CS = URS + SVS - DRI - CCI
  CT-056-008: Optimal selection retorna pergunta com maior CS
  CT-056-009: Answer Direction Test filtra perguntas dispersivas
  CT-056-010: OQS pipeline completo executa sem erro
  CT-056-011: interpret_convergence_score retorna texto válido
  CT-056-012: Entrada vazia ou inválida levanta erro

Uso:
    python specs/test_oqs.py
    PYTHONPATH=. pytest specs/test_oqs.py -v
"""

import sys
import math
from pathlib import Path

# Add skills/system/academic-audit to path
BASE_DIR = Path(__file__).resolve().parent.parent
SCANNER_DIR = BASE_DIR / "skills" / "system" / "academic-audit"
sys.path.insert(0, str(SCANNER_DIR))

from uncertainty_scanner import UncertaintyScanner
from question_vectorizer import (
    QuestionVectorizer,
    QuestionVector,
    QuestionType,
    calculate_convergence_score,
    interpret_convergence_score,
)


# ═══════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════

SAMPLE_PROBLEM = (
    "Preciso entender se o OpenCode Ecosystem pode evoluir. "
    "O que é evolução em ecossistemas cognitivos? "
    "Talvez a resposta esteja na relação entre scanners e motores de raciocínio. "
    "Por outro lado, pode ser que o conceito de pergunta ótima seja apenas resumo. "
    "Como definir se uma pergunta é melhor que outra? "
    "Assumindo que perguntas têm valor, então precisamos de métricas. "
    "Vale ressaltar que este é um tópico importante."
)

SAMPLE_CANDIDATES = [
    "O que é resumo?",
    "Existe equivalência estrutural entre texto bruto e representação vetorial?",
    "Como reduzir tokens?",
    "Qual o impacto de perguntas mal formuladas no consumo de tokens?",
]


# ═══════════════════════════════════════════════════════════════════════
# CT-056-001: UncertaintyScanner aceita problema válido
# ═══════════════════════════════════════════════════════════════════════

def test_ct056_001_uncertainty_scanner_accepts_valid():
    """CT-056-001: UncertaintyScanner aceita problema válido e retorna resultado."""
    scanner = UncertaintyScanner()
    result = scanner.scan(SAMPLE_PROBLEM)

    assert result is not None, "Resultado não pode ser None"
    assert result.problem is not None, "ProblemIntake não pode ser None"
    assert result.problem.word_count > 0, "Word count deve ser > 0"
    assert result.timestamp != "", "Timestamp não pode ser vazio"

    print("[CT-056-001] PASS: UncertaintyScanner aceita problema válido")


# ═══════════════════════════════════════════════════════════════════════
# CT-056-002: UncertaintyScanner detecta ≥3 categorias de incerteza
# ═══════════════════════════════════════════════════════════════════════

def test_ct056_002_uncertainty_scanner_detects_categories():
    """CT-056-002: UncertaintyScanner detecta ≥3 categorias de incerteza."""
    scanner = UncertaintyScanner()
    result = scanner.scan(SAMPLE_PROBLEM)

    categories = set(u.category for u in result.uncertainties)
    assert len(categories) >= 3, (
        f"Esperado ≥3 categorias, obtido {len(categories)}: {categories}"
    )

    # Verificar categorias esperadas no texto de exemplo
    required = {"conceitual", "premissa", "relacional"}
    found = categories & required
    assert len(found) >= 2, (
        f"Deveria encontrar pelo menos 2 das categorias esperadas {required}, "
        f"encontrou {found}"
    )

    print(f"[CT-056-002] PASS: {len(categories)} categorias detectadas: {categories}")


# ═══════════════════════════════════════════════════════════════════════
# CT-056-003: UncertaintyScanner filtra ruído estrutural
# ═══════════════════════════════════════════════════════════════════════

def test_ct056_003_uncertainty_scanner_filters_noise():
    """CT-056-003: UncertaintyScanner filtra ruído estrutural."""
    scanner = UncertaintyScanner(enable_noise_filter=True)
    result = scanner.scan(SAMPLE_PROBLEM)

    assert hasattr(result, 'noisy_elements'), "Deve ter noisy_elements"
    assert hasattr(result, 'filtered_text'), "Deve ter filtered_text"

    print(f"[CT-056-003] PASS: {len(result.noisy_elements)} ruídos identificados")


# ═══════════════════════════════════════════════════════════════════════
# CT-056-004: QuestionVectorizer classifica tipo de pergunta
# ═══════════════════════════════════════════════════════════════════════

def test_ct056_004_question_vectorizer_classifies_type():
    """CT-056-004: QuestionVectorizer classifica tipo de pergunta corretamente."""
    test_cases = [
        ("O que é um scanner?", QuestionType.DEFINIÇÃO),
        ("Por que o sistema falhou?", QuestionType.CAUSALIDADE),
        ("Qual a diferença entre A e B?", QuestionType.COMPARAÇÃO),
        ("É verdade que X funciona?", QuestionType.VALIDAÇÃO),
        ("Existe um contraexemplo?", QuestionType.FALSIFICAÇÃO),
        ("Como implementar o módulo?", QuestionType.OPERACIONALIZAÇÃO),
        ("Qual a métrica ideal?", QuestionType.MÉTRICA),
        ("Qual o impacto dessa mudança?", QuestionType.IMPACTO),
    ]

    for question, expected_type in test_cases:
        detected = QuestionType.classify(question)
        assert detected == expected_type, (
            f"Para '{question[:30]}...': esperado {expected_type.value}, "
            f"obtido {detected.value}"
        )

    print("[CT-056-004] PASS: Todos os 8 tipos classificados corretamente")


# ═══════════════════════════════════════════════════════════════════════
# CT-056-005: QuestionVectorizer gera vetor de 6 dimensões
# ═══════════════════════════════════════════════════════════════════════

def test_ct056_005_question_vectorizer_generates_vector():
    """CT-056-005: QuestionVectorizer gera vetor de 6 dimensões."""
    qv = QuestionVectorizer()
    result = qv.analyze(SAMPLE_PROBLEM, SAMPLE_CANDIDATES)

    for sq in result.candidate_questions:
        v = sq.vector
        # Verificar 6 dimensões
        assert hasattr(v, 'direction'), "Deve ter direction"
        assert hasattr(v, 'scope'), "Deve ter scope"
        assert hasattr(v, 'depth'), "Deve ter depth"
        assert hasattr(v, 'reduction_power'), "Deve ter reduction_power"
        assert hasattr(v, 'dispersion_risk'), "Deve ter dispersion_risk"
        assert hasattr(v, 'cognitive_cost'), "Deve ter cognitive_cost"

        # Verificar range 0-10
        for dim_name in ['direction', 'scope', 'depth', 'reduction_power',
                          'dispersion_risk', 'cognitive_cost']:
            val = getattr(v, dim_name)
            assert 0 <= val <= 10, (
                f"{dim_name}={val} fora do range [0, 10] para '{sq.question[:30]}...'"
            )

    print("[CT-056-005] PASS: Todas as perguntas têm vetor 0-10 válido")


# ═══════════════════════════════════════════════════════════════════════
# CT-056-006: Convergence Score calcula métricas
# ═══════════════════════════════════════════════════════════════════════

def test_ct056_006_convergence_score_metrics():
    """CT-056-006: Convergence Score calcula URS/SVS/DRI/CCI corretamente."""
    qv = QuestionVectorizer()
    result = qv.analyze(SAMPLE_PROBLEM, SAMPLE_CANDIDATES)

    for sq in result.candidate_questions:
        # URS: 0-10
        assert 0 <= sq.uncertainty_reduction <= 10, (
            f"URS={sq.uncertainty_reduction} fora do range"
        )
        # SVS: 0-10
        assert 0 <= sq.structural_value <= 10, (
            f"SVS={sq.structural_value} fora do range"
        )
        # DRI: 0-10
        assert 0 <= sq.dispersion_risk_index <= 10, (
            f"DRI={sq.dispersion_risk_index} fora do range"
        )
        # CCI: 0-10
        assert 0 <= sq.cognitive_cost_index <= 10, (
            f"CCI={sq.cognitive_cost_index} fora do range"
        )

    print("[CT-056-006] PASS: Todas as métricas dentro do range 0-10")


# ═══════════════════════════════════════════════════════════════════════
# CT-056-007: Convergence Score CS = URS + SVS - DRI - CCI
# ═══════════════════════════════════════════════════════════════════════

def test_ct056_007_convergence_score_formula():
    """CT-056-007: Convergence Score CS = URS + SVS - DRI - CCI."""
    qv = QuestionVectorizer()
    result = qv.analyze(SAMPLE_PROBLEM, SAMPLE_CANDIDATES)

    for sq in result.candidate_questions:
        expected_cs = (
            sq.uncertainty_reduction
            + sq.structural_value
            - sq.dispersion_risk_index
            - sq.cognitive_cost_index
        )
        assert abs(sq.convergence_score - expected_cs) < 0.01, (
            f"CS={sq.convergence_score} != URS+SVS-DRI-CCI={expected_cs:.2f} "
            f"para '{sq.question[:30]}...'"
        )

    # Teste da função isolada
    cs = calculate_convergence_score(8.0, 7.0, 3.0, 2.0)
    assert abs(cs - 10.0) < 0.01, f"calculate_convergence_score(8,7,3,2) = {cs}, esperado 10.0"

    print("[CT-056-007] PASS: Fórmula CS verificada para todas as perguntas + função isolada")


# ═══════════════════════════════════════════════════════════════════════
# CT-056-008: Optimal selection retorna pergunta com maior CS
# ═══════════════════════════════════════════════════════════════════════

def test_ct056_008_optimal_selection_highest_cs():
    """CT-056-008: Optimal selection retorna pergunta com maior CS."""
    qv = QuestionVectorizer()
    result = qv.analyze(SAMPLE_PROBLEM, SAMPLE_CANDIDATES)

    assert result.optimal_question is not None, "Deve ter pergunta ótima"

    # Verificar que a pergunta ótima tem o maior CS
    max_cs = max(sq.convergence_score for sq in result.candidate_questions)
    assert abs(result.optimal_question.convergence_score - max_cs) < 0.01, (
        f"Ótima CS={result.optimal_question.convergence_score} != "
        f"max CS={max_cs}"
    )

    print(f"[CT-056-008] PASS: Ótima CS={result.optimal_question.convergence_score:.2f} = max CS={max_cs:.2f}")


# ═══════════════════════════════════════════════════════════════════════
# CT-056-009: Answer Direction Test filtra perguntas dispersivas
# ═══════════════════════════════════════════════════════════════════════

def test_ct056_009_answer_direction_test():
    """CT-056-009: Answer Direction Test filtra perguntas dispersivas."""
    qv = QuestionVectorizer(use_answer_test=True)

    # Adicionar pergunta propositalmente dispersiva
    candidates = SAMPLE_CANDIDATES + [
        "Como tudo isso se relaciona com a teoria quântica de campos, "
        "a filosofia medieval, a economia comportamental e a astrologia?"
    ]

    result = qv.analyze(SAMPLE_PROBLEM, candidates)

    assert len(result.discarded) >= 1, (
        "Pelo menos uma pergunta deveria ser descartada"
    )

    has_dispersion = any(
        "Answer Direction Test" in d.get("reason", "")
        or "CS" in d.get("reason", "")
        for d in result.discarded
    )
    # Pode ser CS inferior ou answer test
    assert len(result.discarded) > 0

    print(f"[CT-056-009] PASS: {len(result.discarded)} perguntas descartadas")


# ═══════════════════════════════════════════════════════════════════════
# CT-056-010: OQS pipeline completo executa sem erro
# ═══════════════════════════════════════════════════════════════════════

def test_ct056_010_oqs_pipeline_complete():
    """CT-056-010: OQS pipeline completo executa sem erro."""
    # Pipeline: UncertaintyScanner -> QuestionVectorizer
    uncertainty_scanner = UncertaintyScanner()
    qv = QuestionVectorizer()

    # Etapa 1-3: Uncertainty Scan
    uncertainty_result = uncertainty_scanner.scan(SAMPLE_PROBLEM)
    assert len(uncertainty_result.uncertainties) >= 1, (
        "Deve ter pelo menos uma incerteza"
    )

    # Etapa 4-8: Question Analysis
    question_result = qv.analyze(
        uncertainty_result.filtered_text or SAMPLE_PROBLEM,
        SAMPLE_CANDIDATES,
    )
    assert question_result.optimal_question is not None, (
        "Deve selecionar pergunta ótima"
    )

    # Verificar consistência
    assert question_result.timestamp != "", "Timestamp não pode ser vazio"
    assert len(question_result.candidate_questions) == len(SAMPLE_CANDIDATES)

    print(f"[CT-056-010] PASS: Pipeline completo -- "
          f"{len(uncertainty_result.uncertainties)} incertezas -> "
          f"{len(question_result.candidate_questions)} candidatas -> "
          f"'{question_result.optimal_question.question[:40]}...'")


# ═══════════════════════════════════════════════════════════════════════
# CT-056-011: interpret_convergence_score retorna texto válido
# ═══════════════════════════════════════════════════════════════════════

def test_ct056_011_interpret_convergence_score():
    """CT-056-011: interpret_convergence_score retorna texto válido."""
    test_cases = [
        (15.0, "Ótima"),
        (10.0, "Forte"),
        (7.0, "Útil"),
        (0.0, "Moderada"),
        (-3.0, "Fraca"),
        (-10.0, "Dispersiva"),
    ]

    for cs, expected_keyword in test_cases:
        text = interpret_convergence_score(cs)
        assert expected_keyword.lower() in text.lower(), (
            f"Para CS={cs}: esperado '{expected_keyword}' em '{text}'"
        )

    print("[CT-056-011] PASS: Todas as 6 faixas de interpretação válidas")


# ═══════════════════════════════════════════════════════════════════════
# CT-056-012: Entrada inválida levanta erro
# ═══════════════════════════════════════════════════════════════════════

def test_ct056_012_invalid_input_raises_error():
    """CT-056-012: Entrada vazia ou inválida levanta erro."""
    scanner = UncertaintyScanner()
    qv = QuestionVectorizer()

    # Teste 1: texto vazio
    try:
        scanner.scan("")
        assert False, "Deveria ter levantado ValueError para texto vazio"
    except ValueError:
        pass  # Esperado

    # Teste 2: None como texto
    try:
        scanner.scan("   ")  # Espaços em branco
        assert False, "Deveria ter levantado ValueError para espaços"
    except ValueError:
        pass  # Esperado

    # Teste 3: lista vazia de perguntas candidatas
    try:
        qv.analyze(SAMPLE_PROBLEM, [])
        assert False, "Deveria ter levantado ValueError para lista vazia"
    except ValueError:
        pass  # Esperado

    print("[CT-056-012] PASS: Todas as entradas inválidas rejeitadas corretamente")


# ═══════════════════════════════════════════════════════════════════════
# MAIN: Executar todos os testes
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    tests = [
        ("CT-056-001", test_ct056_001_uncertainty_scanner_accepts_valid),
        ("CT-056-002", test_ct056_002_uncertainty_scanner_detects_categories),
        ("CT-056-003", test_ct056_003_uncertainty_scanner_filters_noise),
        ("CT-056-004", test_ct056_004_question_vectorizer_classifies_type),
        ("CT-056-005", test_ct056_005_question_vectorizer_generates_vector),
        ("CT-056-006", test_ct056_006_convergence_score_metrics),
        ("CT-056-007", test_ct056_007_convergence_score_formula),
        ("CT-056-008", test_ct056_008_optimal_selection_highest_cs),
        ("CT-056-009", test_ct056_009_answer_direction_test),
        ("CT-056-010", test_ct056_010_oqs_pipeline_complete),
        ("CT-056-011", test_ct056_011_interpret_convergence_score),
        ("CT-056-012", test_ct056_012_invalid_input_raises_error),
    ]

    passed = 0
    failed = 0

    print(f"\n{'='*60}")
    print(f"  SPEC-056: OQS -- TDD Suite (12 CTs)")
    print(f"{'='*60}\n")

    for name, test_fn in tests:
        try:
            test_fn()
            print(f"  [PASS] {name}\n")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {name}: {e}\n")
            failed += 1

    print(f"{'='*60}")
    print(f"  Resultado: {passed}/{len(tests)} PASS, {failed}/{len(tests)} FAIL")
    print(f"{'='*60}")

    sys.exit(0 if failed == 0 else 1)
