#!/usr/bin/env python3
"""
test_optimal_question_scanner.py — SPEC-039: Optimal Question Scanner TDD Suite

8 Critical Tests:
  OQS-001: ProblemIntake normaliza problema bruto e extrai objeto
  OQS-002: UncertaintyScanner identifica incertezas no texto
  OQS-003: StructuralNoiseFilter remove ruído preservando núcleo
  OQS-004: QuestionCandidateGenerator gera 10 tipos de perguntas
  OQS-005: ConvergenceScorer calcula CS = URS + SVS - DRI - CCI
  OQS-006: OptimalQuestionScanner seleciona pergunta com maior CS
  OQS-007: OQS aplicado a problema real (SCE vs resumo)
  OQS-008: Métricas documentadas e auditáveis

Uso: python specs/test_optimal_question_scanner.py
"""

import json, sys
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
SCANNER_DIR = BASE_DIR / "skills" / "system" / "academic-audit"
sys.path.insert(0, str(SCANNER_DIR))

from optimal_question_scanner import (
    OptimalQuestionScanner, ProblemIntake, UncertaintyScanner,
    StructuralNoiseFilter, QuestionCandidateGenerator,
    ConvergenceScorer, ProblemState, QuestionCandidate, OQSResult,
    QuestionType,
)


class CTResult:
    def __init__(self, ct_id, name, passed, detail="", evidence=None):
        self.ct_id = ct_id; self.name = name; self.passed = passed
        self.detail = detail; self.evidence = evidence


# ═══════════════════════════════════════════════════════════════════════════
# CTs
# ═══════════════════════════════════════════════════════════════════════════

def oqs_001_problem_intake() -> CTResult:
    intake = ProblemIntake()
    state = intake.intake(
        "Preciso entender sobre compressão estrutural de textos no contexto "
        "de processamento de linguagem natural. Isso é apenas resumo ou existe "
        "uma técnica nova?"
    )
    
    if not state.object_of_analysis:
        return CTResult("OQS-001", "ProblemIntake extrai objeto", False, "vazio")
    if "compressão" not in state.object_of_analysis.lower():
        return CTResult("OQS-001", "Objeto contém 'compressão'", False, state.object_of_analysis)
    
    return CTResult("OQS-001", "ProblemIntake funciona", True,
                    f"obj={state.object_of_analysis[:50]}, scope={state.scope}")


def oqs_002_uncertainty_scanner() -> CTResult:
    scanner = UncertaintyScanner()
    state = ProblemState("", "Não sei como validar se a compressão preserva estrutura. "
                         "Qual métrica usar? Ainda não defini o threshold ideal.", "", "")
    uncertainties = scanner.scan(state)
    
    if len(uncertainties) == 0:
        return CTResult("OQS-002", "UncertaintyScanner detecta incertezas", False, "0")
    
    return CTResult("OQS-002", f"UncertaintyScanner encontra {len(uncertainties)} incertezas", True,
                    str(uncertainties[:2]))


def oqs_003_noise_filter() -> CTResult:
    noise_filter = StructuralNoiseFilter()
    state = ProblemState("", "Obviamente a compressão é simples. "
                         "Claramente não há complexidade aqui. "
                         "A proposta consiste em preservar funções essenciais.", "", "")
    filtered = noise_filter.filter(state)
    
    if len(filtered.noise_elements) == 0:
        return CTResult("OQS-003", "NoiseFilter detecta ruído", False, "0")
    
    return CTResult("OQS-003", f"NoiseFilter remove {len(filtered.noise_elements)} ruídos", True,
                    f"noise={filtered.noise_elements[:3]}, core={filtered.structural_core[:60]}")


def oqs_004_question_generator() -> CTResult:
    gen = QuestionCandidateGenerator()
    state = ProblemState("", "", "compressão estrutural", "processamento de linguagem natural")
    candidates = gen.generate(state)
    
    if len(candidates) != 10:
        return CTResult("OQS-004", f"Gera 10 perguntas (obtido: {len(candidates)})", False, str(len(candidates)))
    
    types = {c.qtype for c in candidates}
    if len(types) != 10:
        return CTResult("OQS-004", f"10 tipos distintos (obtido: {len(types)})", False, str(types))
    
    return CTResult("OQS-004", "QuestionGenerator gera 10 perguntas de tipos distintos", True,
                    f"tipos={len(types)}")


def oqs_005_convergence_scorer() -> CTResult:
    scorer = ConvergenceScorer()
    state = ProblemState("", "", "compressão estrutural", "PLN")
    
    candidates = [
        QuestionCandidate("O que é compressão estrutural?", QuestionType.DEFINITION, "", 0.5, 0.5, 0.5, 0.5, 0.3, 0.3),
        QuestionCandidate("Qual o impacto da compressão?", QuestionType.IMPACT, "", 0.5, 0.5, 0.5, 0.5, 0.3, 0.3),
    ]
    
    scored = scorer.score(candidates, state)
    
    if scored[0].convergence_score <= scored[1].convergence_score:
        return CTResult("OQS-005", "Definição tem CS > Impacto", False,
                        f"def={scored[0].convergence_score}, imp={scored[1].convergence_score}")
    
    # CS should be between -1 and 2
    for c in scored:
        if c.convergence_score < -1 or c.convergence_score > 3:
            return CTResult("OQS-005", f"CS entre -1 e 3 (obtido: {c.convergence_score})", False, "")
    
    return CTResult("OQS-005", "ConvergenceScorer funciona", True,
                    f"best={scored[0].qtype.value} CS={scored[0].convergence_score:.2f}")


def oqs_006_optimal_selection() -> CTResult:
    oqs = OptimalQuestionScanner()
    
    result = oqs.scan(
        "Preciso entender sobre compressão estrutural de textos. "
        "Isso é apenas resumo ou existe uma técnica nova? "
        "Qual métrica usar para validar a preservação estrutural?"
    )
    
    if not result.optimal_question:
        return CTResult("OQS-006", "OQS seleciona pergunta ótima", False, "None")
    
    if result.optimal_question.convergence_score <= 0:
        return CTResult("OQS-006", "CS > 0", False, f"CS={result.optimal_question.convergence_score}")
    
    return CTResult("OQS-006", f"Pergunta ótima: {result.optimal_question.text[:60]}...", True,
                    f"CS={result.optimal_question.convergence_score:.2f}, "
                    f"tipo={result.optimal_question.qtype.value}, "
                    f"risco={result.remaining_risk}")


def oqs_007_real_problem() -> CTResult:
    """OQS-007: Aplicado ao problema real da proposta (SCE vs resumo)."""
    oqs = OptimalQuestionScanner()
    
    problem = (
        "Tenho uma ferramenta que reduz texto grande em representação vetorial. "
        "Isso é só resumo ou existe uma técnica nova? "
        "Qual é a diferença entre resumir e preservar estrutura?"
    )
    
    result = oqs.scan(problem)
    
    # The optimal question should be about definition or comparison
    if result.optimal_question.qtype not in (QuestionType.DEFINITION,
                                               QuestionType.COMPARISON,
                                               QuestionType.VALIDATION):
        return CTResult("OQS-007", "Pergunta ótima é definição/comparação/validação", False,
                        f"tipo={result.optimal_question.qtype.value}")
    
    return CTResult("OQS-007", f"Problema real resolvido: '{result.optimal_question.text[:80]}...'", True,
                    f"CS={result.optimal_question.convergence_score:.2f}, "
                    f"descartadas={len(result.discarded_questions)}")


def oqs_008_metrics() -> CTResult:
    oqs = OptimalQuestionScanner()
    metrics = oqs.metrics
    
    required = ["URS", "SVS", "DRI", "CCI", "CS"]
    missing = [m for m in required if m not in metrics]
    
    if missing:
        return CTResult("OQS-008", f"Métricas documentadas (faltam: {missing})", False, "")
    
    return CTResult("OQS-008", "5 métricas documentadas e auditáveis", True,
                    f"URS={metrics['URS'][:40]}...")


# ═══════════════════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════════════════

def run_all() -> tuple[list[CTResult], int, int]:
    cts = [
        oqs_001_problem_intake(),
        oqs_002_uncertainty_scanner(),
        oqs_003_noise_filter(),
        oqs_004_question_generator(),
        oqs_005_convergence_scorer(),
        oqs_006_optimal_selection(),
        oqs_007_real_problem(),
        oqs_008_metrics(),
    ]
    passed = sum(1 for ct in cts if ct.passed)
    failed = sum(1 for ct in cts if not ct.passed)
    return cts, passed, failed


def main():
    import argparse
    parser = argparse.ArgumentParser(description="SPEC-039 OQS TDD Suite")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    cts, passed, failed = run_all()

    if args.json:
        print(json.dumps({"spec": "SPEC-039", "total": len(cts), "passed": passed, "failed": failed,
                          "results": [{"ct_id": ct.ct_id, "name": ct.name, "passed": ct.passed, "detail": ct.detail} for ct in cts]},
                         indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*80}")
        print(f"  SPEC-039 Optimal Question Scanner — TDD Suite")
        print(f"  PASS: {passed}  |  FAIL: {failed}  |  Total: {len(cts)}")
        print(f"{'='*80}\n")
        for ct in cts:
            status = "PASS" if ct.passed else "FAIL"
            print(f"  [{status}] {ct.ct_id}: {ct.name}")
            if ct.detail:
                print(f"       {ct.detail}")
        print(f"\n{'='*80}")
        if failed == 0:
            print(f"  RESULTADO: [APROVADO]  |  {passed}/{len(cts)} (100%)")
        else:
            print(f"  RESULTADO: [{failed} FALHAS]  |  {passed}/{len(cts)}")
        print(f"{'='*80}\n")
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()
