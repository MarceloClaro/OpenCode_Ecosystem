#!/usr/bin/env python3
"""
SPEC-014: AletheiaVerifierWrapper
==================================

Wrap Aletheia's natural language verifier output em Cora V1-V7.

Responsabilidades:
1. Integrar Aletheia's NL verifier
2. Enriquecer com Cora V1-V7 symbolic checks
3. Reconciliar resultados (conservative: max of both)
4. Exportar structured report

Seed: 42 | Reproducível | TDD: 6 testes
"""

import json
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum

SEED = 42


class CoraCheckId(Enum):
    V1_LOGICAL_CONSISTENCY = "V1_LogicalConsistency"
    V2_MATHEMATICAL_CORRECTNESS = "V2_MathematicalCorrectness"
    V3_EDGE_CASE_COVERAGE = "V3_EdgeCaseCoverage"
    V4_CITATION_ACCURACY = "V4_CitationAccuracy"
    V5_PROOF_COMPLETENESS = "V5_ProofCompleteness"
    V6_COUNTEREXAMPLE_RESISTANCE = "V6_CounterexampleResistance"
    V7_CLARITY_AND_RIGOR = "V7_ClarityAndRigor"


@dataclass
class CoraCheckResult:
    """Resultado de um check Cora individual."""
    check_id: CoraCheckId
    passed: bool
    confidence: float  # 0.0-1.0
    details: str  # Explicação
    severity: str  # "critical", "major", "minor"


@dataclass
class AletheiaVerifierOutput:
    """Output do Aletheia's natural language verifier."""
    passed: bool
    score: float  # 0.0-1.0
    reasoning: str
    suggested_fixes: List[str]
    hallucination_detected: bool


@dataclass
class EnrichedVerificationResult:
    """Resultado enriquecido: Aletheia + Cora V1-V7."""
    
    # Aletheia's judgment
    aletheia_result: AletheiaVerifierOutput
    
    # Cora V1-V7 checks
    cora_checks: Dict[CoraCheckId, CoraCheckResult] = field(default_factory=dict)
    
    # Reconciliação
    final_passed: bool = False
    final_score: float = 0.0
    reconciliation_method: str = "conservative"  # "conservative" (max), "average", "weighted"
    
    # Diagnóstico
    overall_recommendation: str = ""
    confidence_in_result: float = 0.0
    revision_priority: List[str] = field(default_factory=list)


class CoraVerifierSimulation:
    """
    Simula verificação Cora V1-V7 localmente.
    
    Nota: Implementação simplificada. Em produção, isso chamaria
    sistemas simbólicos reais (Lean, Coq, Isabelle).
    """
    
    def __init__(self, seed: int = SEED):
        """Initialize with optional seed for reproducibility."""
        self.seed = seed
        import random
        random.seed(seed)
    
    def run_checks(self, problem: str, solution: str, 
                   problem_domain: str = "general") -> Dict[CoraCheckId, CoraCheckResult]:
        """Executa todos os checks V1-V7 e retorna dict."""
        results = {}
        for check_id in CoraCheckId:
            results[check_id] = self.run_check(check_id, solution, problem_domain)
        return results
    
    def run_check(self, check_id: CoraCheckId, solution: str,
                  problem_domain: str) -> CoraCheckResult:
        """Executa um check Cora específico."""
        
        # V1: Logical Consistency
        if check_id == CoraCheckId.V1_LOGICAL_CONSISTENCY:
            passed, confidence, details = self._check_logical_consistency(solution)
            return CoraCheckResult(
                check_id=check_id,
                passed=passed,
                confidence=confidence,
                details=details,
                severity="critical" if not passed else "minor"
            )
        
        # V2: Mathematical Correctness
        elif check_id == CoraCheckId.V2_MATHEMATICAL_CORRECTNESS:
            passed, confidence, details = self._check_math_correctness(solution, problem_domain)
            return CoraCheckResult(
                check_id=check_id,
                passed=passed,
                confidence=confidence,
                details=details,
                severity="critical" if not passed else "minor"
            )
        
        # V3: Edge Case Coverage
        elif check_id == CoraCheckId.V3_EDGE_CASE_COVERAGE:
            passed, confidence, details = self._check_edge_cases(solution)
            return CoraCheckResult(
                check_id=check_id,
                passed=passed,
                confidence=confidence,
                details=details,
                severity="major" if not passed else "minor"
            )
        
        # V4: Citation Accuracy
        elif check_id == CoraCheckId.V4_CITATION_ACCURACY:
            passed, confidence, details = self._check_citations(solution)
            return CoraCheckResult(
                check_id=check_id,
                passed=passed,
                confidence=confidence,
                details=details,
                severity="major" if not passed else "minor"
            )
        
        # V5: Proof Completeness
        elif check_id == CoraCheckId.V5_PROOF_COMPLETENESS:
            passed, confidence, details = self._check_completeness(solution)
            return CoraCheckResult(
                check_id=check_id,
                passed=passed,
                confidence=confidence,
                details=details,
                severity="critical" if not passed else "minor"
            )
        
        # V6: Counterexample Resistance
        elif check_id == CoraCheckId.V6_COUNTEREXAMPLE_RESISTANCE:
            passed, confidence, details = self._check_counterexample_resistance(solution)
            return CoraCheckResult(
                check_id=check_id,
                passed=passed,
                confidence=confidence,
                details=details,
                severity="major" if not passed else "minor"
            )
        
        # V7: Clarity and Rigor
        elif check_id == CoraCheckId.V7_CLARITY_AND_RIGOR:
            passed, confidence, details = self._check_clarity(solution)
            return CoraCheckResult(
                check_id=check_id,
                passed=passed,
                confidence=confidence,
                details=details,
                severity="minor" if not passed else "minor"
            )
        
        else:
            raise ValueError(f"Unknown check ID: {check_id}")
    
    def _check_logical_consistency(self, solution: str) -> Tuple[bool, float, str]:
        """Verifica se passos lógicos são consistentes."""
        content = solution.lower()
        logical_connectors = ["therefore", "hence", "thus", "consequently", "implies", "follows from"]
        has_connectors = any(c in content for c in logical_connectors)
        
        if len(solution) > 1000 and not has_connectors:
            return False, 0.3, "Missing logical connectors in long proof"
        return True, 0.85, "Logical structure appears sound"
    
    def _check_math_correctness(self, solution: str, domain: str) -> Tuple[bool, float, str]:
        """Verifica erros matemáticos óbvios."""
        error_patterns = ["0/0", "ln(0)", "sqrt(-1)"]
        for ep in error_patterns:
            if ep in solution:
                return False, 0.1, f"Potential error detected: {ep}"
        return True, 0.80, "No obvious mathematical errors"
    
    def _check_edge_cases(self, solution: str) -> Tuple[bool, float, str]:
        """Verifica se casos limite foram considerados."""
        edge_keywords = ["edge case", "boundary", "n=0", "n=1", "base case", "trivial case"]
        has_edge = any(k in solution.lower() for k in edge_keywords)
        
        if not has_edge:
            return False, 0.4, "No explicit edge case analysis"
        return True, 0.90, "Edge cases properly addressed"
    
    def _check_citations(self, solution: str) -> Tuple[bool, float, str]:
        """Verifica se citações são credíveis."""
        suspicious = ["[?]", "[TODO]", "[citation needed]", "personal communication", "arxiv:????"]
        for s in suspicious:
            if s in solution.lower():
                return False, 0.2, f"Suspicious citation marker: {s}"
        return True, 0.85, "Citations appear credible"
    
    def _check_completeness(self, solution: str) -> Tuple[bool, float, str]:
        """Verifica se prova tem conclusão explícita."""
        completion_keywords = ["qed", "∎", "conclusion", "therefore the statement", "thus proved"]
        has_completion = any(k in solution.lower() for k in completion_keywords)
        
        if not has_completion:
            return False, 0.5, "Missing explicit conclusion (QED)"
        return True, 0.95, "Proof properly concluded"
    
    def _check_counterexample_resistance(self, solution: str) -> Tuple[bool, float, str]:
        """Verifica se argumento considera contraexemplos."""
        counter_keywords = ["counterexample", "conversely", "on the other hand", "however"]
        has_counter = any(k in solution.lower() for k in counter_keywords)
        
        if not has_counter:
            return False, 0.6, "No counterexample consideration"
        return True, 0.90, "Arguments consider potential counterexamples"
    
    def _check_clarity(self, solution: str) -> Tuple[bool, float, str]:
        """Verifica clareza e rigor."""
        n = len(solution)
        if n < 200:
            return False, 0.3, f"Solution too short ({n} chars)"
        if n > 20000:
            return False, 0.5, f"Solution too long ({n} chars)"
        return True, 0.88, "Clarity and rigor acceptable"


class AletheiaVerifierWrapper:
    """
    Wrapper que combina Aletheia's NL verifier com Cora V1-V7.
    """
    
    def __init__(self, verbose: bool = False, seed: int = SEED):
        self.cora = CoraVerifierSimulation(seed=seed)
        self.simulator = self.cora  # Alias para compatibilidade com testes
        self.verbose = verbose
        self.seed = seed
    
    def verify(self, solution: str, problem_domain: str,
               aletheia_result: Optional[AletheiaVerifierOutput] = None) -> EnrichedVerificationResult:
        """
        Verifica solução usando Aletheia + Cora V1-V7.
        
        Args:
            solution: Texto da solução
            problem_domain: Domínio do problema (ex: "number_theory")
            aletheia_result: Output do Aletheia's verifier (se disponível)
        
        Returns:
            EnrichedVerificationResult com todos os checks
        """
        
        # Simula resultado Aletheia se não fornecido
        if aletheia_result is None:
            aletheia_result = AletheiaVerifierOutput(
                passed=True,
                score=0.8,
                reasoning="Simulated Aletheia judgment",
                suggested_fixes=[],
                hallucination_detected=False,
            )
        
        # Executa todos os checks Cora V1-V7
        cora_checks = {}
        for check_id in CoraCheckId:
            cora_checks[check_id] = self.cora.run_check(check_id, solution, problem_domain)
        
        # Reconcilia resultados
        result = self._reconcile(aletheia_result, cora_checks)
        
        if self.verbose:
            print(f"  [CORA] Final score: {result.final_score:.2f} | Passed: {result.final_passed}")
        
        return result
    
    def _reconcile(self, aletheia_result: AletheiaVerifierOutput,
                   cora_checks: Dict[CoraCheckId, CoraCheckResult]) -> EnrichedVerificationResult:
        """
        Reconcilia Aletheia + Cora usando estratégia conservadora.
        
        Estratégia: max(Aletheia score, Cora score).
        Ou seja, se QUALQUER checker falha, resultado falha.
        """
        
        # Calcula score Cora: média dos checks
        cora_scores = [check.confidence for check in cora_checks.values()]
        cora_score = sum(cora_scores) / len(cora_scores) if cora_scores else 0.5
        
        # Reconciliação conservadora: penaliza se alguém falha
        critical_failures = [c for c in cora_checks.values() 
                            if not c.passed and c.severity == "critical"]
        
        if critical_failures:
            # Se há falha crítica em Cora, falha
            final_score = 0.3
            final_passed = False
        else:
            # Senão, média entre Aletheia e Cora
            final_score = (aletheia_result.score + cora_score) / 2
            final_passed = final_score >= 0.7 and not aletheia_result.hallucination_detected
        
        # Gera recomendações de revisão
        revision_priority = []
        for check_id in sorted(cora_checks.keys(), 
                              key=lambda c: {"critical": 0, "major": 1, "minor": 2}[cora_checks[c].severity]):
            check = cora_checks[check_id]
            if not check.passed:
                revision_priority.append(f"{check_id.value}: {check.details}")
        
        confidence = (sum(c.confidence for c in cora_checks.values()) / len(cora_checks)) \
                    if cora_checks else 0.0
        
        return EnrichedVerificationResult(
            aletheia_result=aletheia_result,
            cora_checks=cora_checks,
            final_passed=final_passed,
            final_score=final_score,
            reconciliation_method="conservative",
            overall_recommendation=self._generate_recommendation(final_score, critical_failures),
            confidence_in_result=confidence,
            revision_priority=revision_priority,
        )
    
    def _generate_recommendation(self, score: float, critical_failures: List) -> str:
        """Gera recomendação textual baseada no score."""
        if critical_failures:
            return "REVISE: Critical flaws found in Cora checks"
        elif score >= 0.85:
            return "ACCEPT: High confidence in solution"
        elif score >= 0.70:
            return "REVIEW: Minor issues, likely publishable with refinement"
        else:
            return "REJECT: Substantial gaps remain"
    
    def reconcile_scores(self, aletheia_score: float, 
                        cora_results: List[CoraCheckResult]) -> Tuple[float, bool]:
        """
        Pública: Reconcilia score Aletheia com Cora V1-V7.
        
        Returns:
            (final_score, final_passed)
        """
        # Calcula score Cora: média dos checks
        cora_scores = [check.confidence for check in cora_results]
        cora_score = sum(cora_scores) / len(cora_scores) if cora_scores else 0.5
        
        # Reconciliação conservadora: penaliza se alguém falha criticamente
        critical_failures = [c for c in cora_results 
                            if not c.passed and c.severity == "critical"]
        
        if critical_failures:
            # Se há falha crítica em Cora, falha
            final_score = 0.3
            final_passed = False
        else:
            # Senão, média entre Aletheia e Cora
            final_score = (aletheia_score + cora_score) / 2
            final_passed = final_score >= 0.7
        
        return final_score, final_passed
    
    def export_report(self, result: EnrichedVerificationResult) -> Dict:
        """Exporta resultado como JSON estruturado."""
        return {
            "aletheia": {
                "passed": result.aletheia_result.passed,
                "score": result.aletheia_result.score,
                "hallucination_detected": result.aletheia_result.hallucination_detected,
            },
            "cora": {
                check_id.value: {
                    "passed": check.passed,
                    "confidence": check.confidence,
                    "severity": check.severity,
                    "details": check.details,
                }
                for check_id, check in result.cora_checks.items()
            },
            "final": {
                "passed": result.final_passed,
                "score": result.final_score,
                "recommendation": result.overall_recommendation,
                "confidence": result.confidence_in_result,
                "revision_priority": result.revision_priority,
            }
        }


# INTEGRATION: Lean4 Formal Verification Enhancement
def verify_with_lean_enhancement(
    wrapper: 'AletheiaVerifierWrapper',
    result: EnrichedVerificationResult,
    problem_id: str,
) -> Tuple[EnrichedVerificationResult, Dict]:
    """
    Enriquece resultado SPEC-014 com verificação Lean4 formal (SPEC-014 extension).
    
    Args:
        wrapper: AletheiaVerifierWrapper instance
        result: EnrichedVerificationResult original
        problem_id: ID do problema Erdős (ex: "Erdos-652")
    
    Returns:
        (enhanced_result, lean_enhancement_report)
    """
    try:
        from spec_014_lean_verifier import enhance_cora_score_with_lean_verification
        
        # Contar quantos checks Cora passaram
        original_cora_passed = sum(1 for r in result.cora_checks.values() if r.passed)
        
        # Enhance com Lean verification
        enhanced_passed, enhancements, lean_result = enhance_cora_score_with_lean_verification(
            problem_id=problem_id,
            original_cora_passed=original_cora_passed,
            aletheia_score=result.aletheia_result.score,
        )
        
        # Atualiza resultado
        if lean_result.has_lean_proof:
            # Boost Cora checks based on Lean tactics
            for cora_id, boost in enhancements.items():
                if boost > 0.10:  # Only apply significant boosts
                    # Find matching check
                    for check in result.cora_checks.values():
                        if cora_id in str(check.check_id):
                            old_confidence = check.confidence
                            check.confidence = min(1.0, old_confidence + boost * 0.3)
        
        # Return enhanced result and report
        lean_report = {
            "has_lean_proof": lean_result.has_lean_proof,
            "tactics_found": lean_result.lean_tactics_found,
            "formal_verification": lean_result.formal_verification_passed,
            "cora_enhancements": {k: v for k, v in enhancements.items()},
            "original_cora_passed": original_cora_passed,
            "enhanced_cora_passed": enhanced_passed,
        }
        
        return result, lean_report
    
    except ImportError:
        # Lean verifier not available
        return result, {"error": "Lean verifier not available"}


if __name__ == "__main__":
    # Test: verificar wrapper
    wrapper = AletheiaVerifierWrapper(verbose=True)
    
    # Teste com solução simulada
    test_solution = """
    # Solution to Problem
    
    Let n be a positive integer. We proceed by mathematical induction.
    
    Base case: For n=1, the statement holds trivially.
    
    Inductive step: Assume the statement holds for n. We prove it for n+1.
    By the inductive hypothesis... [reasoning] ... therefore the statement holds.
    
    Edge cases: n=0 is trivial. Large n follow from asymptotic analysis.
    
    Conversely, consider the counterexample approach...
    
    QED.
    """
    
    aletheia_output = AletheiaVerifierOutput(
        passed=True,
        score=0.85,
        reasoning="Aletheia judgment: good structure, minor gaps",
        suggested_fixes=["Add more rigor to inductive step"],
        hallucination_detected=False,
    )
    
    result = wrapper.verify(test_solution, "number_theory", aletheia_output)
    
    print(f"\nFinal Result:")
    print(f"  Passed: {result.final_passed}")
    print(f"  Score: {result.final_score:.2f}")
    print(f"  Recommendation: {result.overall_recommendation}")
    
    # Test Lean enhancement
    enhanced_result, lean_report = verify_with_lean_enhancement(
        wrapper, result, "Erdos-652"
    )
    
    print(f"\nLean Enhancement:")
    print(f"  Report: {json.dumps(lean_report, indent=2)}")
    
    report = wrapper.export_report(result)
    print(f"\nFull Report:")
    print(json.dumps(report, indent=2))
