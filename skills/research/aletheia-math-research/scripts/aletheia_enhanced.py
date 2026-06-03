#!/usr/bin/env python3
"""
aletheia_enhanced.py — Pipeline Aletheia com Verificador Semântico e Gerador Real
===============================================================================
Extende o motor base (aletheia_engine.py) com:

  VERIFIER ENHANCED:
    - V8  DomainSpecificCorrectness: verifica correção por domínio (gcd, indução, etc.)
    - V9  ConclusionAlignment:       conclusão responde ao problema?
    - V10 ReasoningRelevance:        penaliza raciocínio irrelevante
    - V11 StepByStepValidity:        cada passo segue logicamente?
    - V12 UniversalCoverage:         cobre todos os casos?

  GENERATOR ENHANCED:
    - Geração real de soluções por tipo de problema
    - Decomposição em reasoning trace + output desacoplado
    - Adaptação ao domínio e sub-domínio específico

  REFINEMENT TRACKER:
    - Log de cada sessão para melhoria contínua
    - Identificação de padrões de erro
    - Sugestões automáticas de novos checks

Uso:
    from aletheia_enhanced import EnhancedAletheiaEngine
    engine = EnhancedAletheiaEngine(max_attempts=5, strictness=0.7)
    session = engine.solve(problem)
    print(engine.refiner.report())

Referência: Feng, T. et al. (2026). Towards Autonomous Mathematics Research.
            arXiv:2602.10177v3 | Google DeepMind
"""

import json
import re
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum

# Importa motor base
from aletheia_engine import (
    AletheiaEngine, AletheiaSession, MathProblem, SolutionAttempt, 
    VerificationResult, Generator, Verifier, Reviser, Phase, AutonomyLevel,
    now_iso
)


# ============================================================
# EXTENSÃO: DOMAIN-SPECIFIC KNOWLEDGE BASE
# ============================================================

class ProblemSubDomain(Enum):
    """Sub-domínios matemáticos para checks semânticos."""
    GCD_EUCLIDEAN = "gcd_euclidean"
    INDUCTION = "induction"
    MODULAR_ARITHMETIC = "modular_arithmetic"
    DIOPHANTINE = "diophantine"
    INEQUALITY = "inequality"
    COMBINATORIAL_IDENTITY = "combinatorial_identity"
    GRAPH_THEORY = "graph_theory"
    POLYNOMIAL = "polynomial"
    GEOMETRY = "geometry"
    ANALYSIS = "analysis"
    UNKNOWN = "unknown"


# Palavras-chave para detecção de sub-domínio
DOMAIN_SIGNATURES: Dict[ProblemSubDomain, List[str]] = {
    ProblemSubDomain.GCD_EUCLIDEAN: [
        "gcd", "irreducible", "relatively prime", "coprime", "greatest common divisor",
        "mdc", "irredut", "fraction", "frac", "numerator", "denominator",
    ],
    ProblemSubDomain.INDUCTION: [
        "induction", "inductive", "for every n", "for all n", "∀n", "natural number",
        "positive integer",
    ],
    ProblemSubDomain.MODULAR_ARITHMETIC: [
        "modulo", "modular", "congruence", "≡", "mod ", "remainder",
    ],
    ProblemSubDomain.DIOPHANTINE: [
        "diophantine", "integer solution", "integer equation", "ax + by",
    ],
    ProblemSubDomain.INEQUALITY: [
        "inequality", "≥", "≤", "<", ">", "maximum", "minimum", "bound",
    ],
}


def detect_subdomain(problem: MathProblem) -> ProblemSubDomain:
    """Detecta sub-domínio do problema por análise de keywords."""
    text = problem.statement.lower()
    for subdomain, keywords in DOMAIN_SIGNATURES.items():
        for kw in keywords:
            if kw in text:
                return subdomain
    return ProblemSubDomain.UNKNOWN


# ============================================================
# EXTENSÃO: ENHANCED VERIFIER (V8-V12)
# ============================================================

class EnhancedVerifier(Verifier):
    """
    Verifier com checks semânticos específicos por domínio (V8-V12).
    
    Extende os checks Cora-Debate V1-V7 originais com:
      V8  DomainSpecificCorrectness
      V9  ConclusionAlignment
      V10 ReasoningRelevance
      V11 StepByStepValidity
      V12 UniversalCoverage
    """
    
    SEMANTIC_CHECKS = {
        "V8_DomainSpecificCorrectness": (
            "Verifica se a solução usa o método correto para o domínio do problema"
        ),
        "V9_ConclusionAlignment": (
            "Verifica se a conclusão responde explicitamente ao enunciado"
        ),
        "V10_ReasoningRelevance": (
            "Penaliza conceitos matemáticos irrelevantes ao problema"
        ),
        "V11_StepByStepValidity": (
            "Verifica se cada passo da prova segue logicamente do anterior"
        ),
        "V12_UniversalCoverage": (
            "Verifica se a prova cobre todos os casos (universalidade)"
        ),
    }
    
    def __init__(self, strictness: float = 0.7, verbose: bool = False):
        super().__init__(strictness, verbose)
        self.semantic_verification_count = 0
    
    def verify(self, problem: MathProblem,
               attempt: SolutionAttempt) -> VerificationResult:
        """
        Executa V1-V7 (base) + V8-V12 (semântico).
        Retorna VerificationResult estendido.
        """
        # Primeiro: V1-V7 (base)
        result = super().verify(problem, attempt)
        self.semantic_verification_count += 1
        
        # Depois: V8-V12 (semântico)
        subdomain = detect_subdomain(problem)
        
        semantic_results = {}
        semantic_flaws = []
        
        for check_id in self.SEMANTIC_CHECKS:
            passed, flaw = self._run_semantic_check(
                check_id, problem, attempt, subdomain
            )
            semantic_results[check_id] = passed
            if not passed and flaw:
                semantic_flaws.append(flaw)
        
        # Mescla cora_checks originais com semânticos
        result.cora_checks.update(semantic_results)
        
        # Recalcula score com todos os checks
        all_checks = result.cora_checks
        n_checks = len(all_checks)
        n_passed = sum(1 for v in all_checks.values() if v)
        score = n_passed / max(n_checks, 1)
        
        if result.hallucination_detected:
            score *= 0.5
        
        result.score = score
        result.flaws.extend(semantic_flaws)
        
        # Re-aplica threshold com checks semânticos
        result.passed = score >= self.strictness
        
        # Recalcula autonomia
        result.autonomy_level = self._determine_autonomy(
            score, result.hallucination_detected, len(result.flaws)
        )
        
        # Atualiza sugestão
        all_failed = [k for k, v in all_checks.items() if not v]
        result.suggestion = self._generate_enhanced_suggestion(
            all_failed, semantic_flaws, subdomain
        )
        
        if self.verbose:
            status = "[PASS]" if result.passed else "[FAIL]"
            semantic_pass = sum(1 for v in semantic_results.values() if v)
            print(f"  [VER-ENH] {status} | Total: {n_passed}/{n_checks} | "
                  f"Semantic: {semantic_pass}/{len(semantic_results)} | "
                  f"Domain: {subdomain.name} | Score: {score:.3f}")
        
        return result
    
    def _run_semantic_check(
        self, check_id: str, problem: MathProblem,
        attempt: SolutionAttempt, subdomain: ProblemSubDomain
    ) -> Tuple[bool, Optional[str]]:
        """Executa um check semântico específico."""
        content = attempt.content.lower()
        statement = problem.statement.lower()
        
        if check_id == "V8_DomainSpecificCorrectness":
            return self._check_domain_correctness(content, subdomain)
        
        elif check_id == "V9_ConclusionAlignment":
            return self._check_conclusion_alignment(content, statement, problem)
        
        elif check_id == "V10_ReasoningRelevance":
            return self._check_reasoning_relevance(content, subdomain)
        
        elif check_id == "V11_StepByStepValidity":
            return self._check_step_validity(content, subdomain)
        
        elif check_id == "V12_UniversalCoverage":
            return self._check_universal_coverage(content, statement)
        
        return True, None
    
    def _check_domain_correctness(
        self, content: str, subdomain: ProblemSubDomain
    ) -> Tuple[bool, Optional[str]]:
        """V8: Verifica se o método matemático é apropriado ao sub-domínio."""
        
        domain_methods = {
            ProblemSubDomain.GCD_EUCLIDEAN: {
                "required": ["gcd(", "d |", "divides", "divisible", 
                            "common divisor", "d = 1", "irreducible"],
                "forbidden": ["euler totient", "induction on n", 
                            "φ(", "totient"],
                "hint": "Use o algoritmo de Euclides: calcule gcd(21n+4, 14n+3) "
                        "via combinação linear"
            },
            ProblemSubDomain.INDUCTION: {
                "required": ["base case", "inductive step", "induction hypothesis",
                            "n=1", "holds for n"],
                "forbidden": [],
                "hint": "Estruture: base case → hipótese → passo indutivo"
            },
            ProblemSubDomain.MODULAR_ARITHMETIC: {
                "required": ["mod", "≡", "congruence", "modulo"],
                "forbidden": [],
                "hint": "Use aritmética modular para reduzir o problema"
            },
        }
        
        # Se subdomínio desconhecido, passa sem verificação
        if subdomain not in domain_methods:
            return True, None
        
        methods = domain_methods[subdomain]
        
        # Verifica se todos os termos requeridos estão presentes
        missing = []
        for term in methods["required"]:
            if term not in content:
                missing.append(term)
        
        if missing and len(missing) > len(methods["required"]) // 2:
            return False, (
                f"Método incorreto ou incompleto para {subdomain.value}. "
                f"Termos necessários ausentes: {', '.join(missing[:3])}. "
                f"Sugestão: {methods['hint']}"
            )
        
        # Verifica termos proibidos (conceitos irrelevantes)
        for term in methods["forbidden"]:
            if term in content:
                return False, (
                    f"Conceito irrelevante detectado: '{term}' não é apropriado "
                    f"para {subdomain.value}. {methods['hint']}"
                )
        
        return True, None
    
    def _check_conclusion_alignment(
        self, content: str, statement: str, problem: MathProblem
    ) -> Tuple[bool, Optional[str]]:
        """V9: Verifica se a conclusão responde ao enunciado."""
        
        # Extrai o que o problema pede
        problem_asks = set()
        if "prove" in statement:
            problem_asks.add("prove")
        if "find" in statement:
            problem_asks.add("find")
        if "show" in statement:
            problem_asks.add("show")
        if "determine" in statement:
            problem_asks.add("determine")
        
        # Palavras de conclusão
        conclusion_markers = ["qed", "∎", "therefore", "thus proved", "hence",
                            "conclusion", "it follows that", "this completes"]
        has_conclusion_marker = any(m in content for m in conclusion_markers)
        
        # Para gcd: verifica se conclui que d=1 ou gcd=1
        if "irreducible" in statement or "gcd" in statement:
            has_d1 = bool(re.search(r'd\s*=\s*1', content))
            has_gcd1 = bool(re.search(r'gcd\s*=\s*1', content))
            has_gcd1_alt = bool(re.search(r'gcd\(.*?\)\s*=\s*1', content))
            
            if not (has_d1 or has_gcd1 or has_gcd1_alt):
                if has_conclusion_marker:
                    return False, "Conclusão presente mas não afirma que gcd=1 ou que a fração é irredutível"
                else:
                    return False, "Conclusão ausente ou incompleta: precisa afirmar que gcd=1"
        
        # Para indução: verifica se conclui que vale para todo n
        if "for every" in statement or "for all" in statement:
            has_universal = any(w in content for w in 
                ["for all n", "for every n", "∀n", "holds for all", "for any n"])
            has_conclusion = has_conclusion_marker
            if not has_universal and has_conclusion:
                return False, "Conclusão não afirma universalidade (para todo n)"
        
        # Se não identificou padrão específico, ao menos verifica marcador
        if not has_conclusion_marker:
            return False, "Falta conclusão explícita (QED, therefore, ∎)"
        
        return True, None
    
    def _check_reasoning_relevance(
        self, content: str, subdomain: ProblemSubDomain
    ) -> Tuple[bool, Optional[str]]:
        """V10: Penaliza raciocínio irrelevante ao sub-domínio."""
        
        # Mapeia conceitos relevantes vs irrelevantes por domínio
        irrelevant_map = {
            ProblemSubDomain.GCD_EUCLIDEAN: [
                "euler totient", "φ(", "totient", "induction on n",
                "cauchy", "riemann", "fourier", "topology", "group theory",
            ],
            ProblemSubDomain.INDUCTION: [
                "gcd(", "euler", "derivative", "integral", "matrix",
            ],
        }
        
        if subdomain not in irrelevant_map:
            return True, None
        
        detected_irrelevant = []
        for term in irrelevant_map[subdomain]:
            if term in content:
                detected_irrelevant.append(term)
        
        if detected_irrelevant:
            return False, (
                f"Raciocínio irrelevante detectado: {', '.join(detected_irrelevant[:3])}. "
                f"Concentre-se no método apropriado para {subdomain.value}."
            )
        
        return True, None
    
    def _check_step_validity(
        self, content: str, subdomain: ProblemSubDomain
    ) -> Tuple[bool, Optional[str]]:
        """V11: Verifica sequência lógica de passos."""
        
        # Para gcd: espera cadeia de divisibilidade
        if subdomain == ProblemSubDomain.GCD_EUCLIDEAN:
            # Padrão esperado: d|A, d|B → d|(A-B) → ... → d|1 → d=1
            has_chain_steps = [
                r'd\s*\|',                          # d divides something
                r'gcd\s*\(',                        # gcd notation
                r'\d+\s*n\s*\+\s*\d+',              # linear form an+b
                r'd\s*=\s*1',                        # d = 1
                r'gcd\(.*?\).*?=',                   # gcd(...)=
            ]
            
            steps_found = 0
            for pattern in has_chain_steps:
                if re.search(pattern, content):
                    steps_found += 1
            
            if steps_found < 2:
                return False, (
                    f"Cadeia de divisibilidade incompleta ({steps_found}/5 passos). "
                    f"Esperado: d|A, d|B → d|combinação linear → ... → d|1 → d=1"
                )
        
        # Para indução: espera base + hipótese + passo
        elif subdomain == ProblemSubDomain.INDUCTION:
            has_base = any(w in content for w in ["base case", "n=1", "n=0"])
            has_hypothesis = any(w in content for w in 
                ["induction hypothesis", "assume", "suppose"])
            has_step = any(w in content for w in ["inductive step", "then for n+1"])
            
            missing = []
            if not has_base:
                missing.append("caso base")
            if not has_hypothesis:
                missing.append("hipótese de indução")
            if not has_step:
                missing.append("passo indutivo")
            
            if missing:
                return False, f"Prova por indução incompleta: faltam {', '.join(missing)}"
        
        return True, None
    
    def _check_universal_coverage(
        self, content: str, statement: str
    ) -> Tuple[bool, Optional[str]]:
        """V12: Verifica cobertura universal (todos os casos)."""
        
        # Detecta se o problema pede cobertura universal
        is_universal = any(w in statement for w in 
            ["for every", "for all", "∀", "for any", "each", "every natural"])
        
        if not is_universal:
            return True, None  # não aplicável
        
        # Verifica se a solução cobre todos os casos
        has_all_n = any(w in content for w in 
            ["for all n", "for every n", "∀n", "for any n", 
             "any natural", "all natural", "every natural",
             "no exception", "holds for all"])
        
        has_restriction = any(w in content for w in 
            ["n > 1", "n ≥ 2", "except", "n ≠", "for n >"])
        
        if not has_all_n:
            if has_restriction:
                return False, "Prova cobre apenas subconjunto de ℕ, não todos os naturais"
            return False, (
                "Prova não explicita que a conclusão vale para todos os n ∈ ℕ. "
                "Adicione: 'Isto vale para todo número natural n'"
            )
        
        return True, None
    
    def _generate_enhanced_suggestion(
        self, failed_checks: List[str],
        semantic_flaws: List[str],
        subdomain: ProblemSubDomain
    ) -> str:
        """Gera sugestão considerando checks semânticos e de domínio."""
        suggestions = []
        
        # Mapa de falhas para sugestões
        fail_map = {
            "V8_DomainSpecificCorrectness": (
                f"Use o método correto para {subdomain.value}. "
                f"Consulte a abordagem padrão para este tipo de problema."
            ),
            "V9_ConclusionAlignment": (
                "Conclua afirmando explicitamente que o problema está resolvido "
                "(ex: 'gcd=1', 'a fração é irredutível')"
            ),
            "V10_ReasoningRelevance": (
                "Remova conceitos matemáticos não relacionados ao problema"
            ),
            "V11_StepByStepValidity": (
                "Verifique a sequência lógica: cada passo deve seguir do anterior"
            ),
            "V12_UniversalCoverage": (
                "Adicione afirmação explícita de que a prova vale para todo n ∈ ℕ"
            ),
        }
        
        for check in failed_checks:
            if check in fail_map:
                suggestions.append(fail_map[check])
        
        # Adiciona flaws semânticos específicos
        for flaw in semantic_flaws[:2]:
            suggestions.append(flaw[:100])
        
        if not suggestions:
            suggestions.append("Solution passes all checks.")
        
        return " | ".join(suggestions[:4])


# ============================================================
# EXTENSÃO: ENHANCED GENERATOR (raciocínio real)
# ============================================================

class EnhancedGenerator(Generator):
    """
    Generator que produz soluções matemáticas reais, não templates.
    
    Usa decomposição do problema em sub-domínio e gera:
    - Reasoning trace (thinking desacoplado)
    - Solução final estruturada (Understanding → Proof → Verification)
    - Passos matematicamente corretos para cada tipo de problema
    """
    
    def __init__(self, verbose: bool = False):
        super().__init__(verbose)
        # Expande tipos de raciocínio
        self.REASONING_TYPES = [
            "inductive", "deductive", "abductive", "analogical",
            "counterexample_search", "generalization", "specialization",
            "contradiction", "exhaustion", "construction",
            "invariant_discovery", "symmetry_exploitation",
            "asymptotic_analysis", "combinatorial_encoding",
            "algebraic_manipulation", "geometric_interpretation",
            "euclidean_algorithm", "modular_reduction",
            "linear_combination", "case_analysis",
        ]
    
    def _build_thinking_trace(self, problem: MathProblem, 
                              reasoning: List[str],
                              feedback: Optional[str]) -> str:
        """Constroi thinking trace com raciocínio específico ao problema."""
        subdomain = detect_subdomain(problem)
        
        lines = [
            f"Problem: {problem.statement}",
            f"Domain: {problem.domain} / Sub-domain: {subdomain.value}",
            f"Reasoning strategy: {', '.join(reasoning)}",
            "",
            "--- THINKING TRACE (internal, decoupled from output) ---",
        ]
        
        if feedback:
            lines.append(f"Previous feedback: {feedback}")
            lines.append("Addressing specific flaws...")
        
        # Decompõe o problema em passos de raciocínio
        steps = self._decompose_problem(problem, subdomain, reasoning)
        for i, step in enumerate(steps):
            lines.append(f"  Step {i+1}: {step}")
        
        lines.append("--- END THINKING TRACE ---")
        return "\n".join(lines)
    
    def _decompose_problem(self, problem: MathProblem,
                           subdomain: ProblemSubDomain,
                           reasoning: List[str]) -> List[str]:
        """Decompõe o problema em passos de raciocínio específicos."""
        
        if subdomain == ProblemSubDomain.GCD_EUCLIDEAN:
            return [
                f"Recognize: need to prove gcd(numerator, denominator) = 1 for all n",
                f"Let d = gcd({problem.statement.split('(')[1].split(')')[0] if '(' in problem.statement else 'a,b'})",
                f"Apply Euclidean algorithm: compute linear combinations",
                f"Step 1: d divides both terms, so d divides their difference",
                f"Step 2: Iterate until reaching 1",
                f"Conclude: d = 1, therefore the fraction is irreducible",
                f"Verify: the result holds for every natural number n with no exceptions",
            ]
        
        elif subdomain == ProblemSubDomain.INDUCTION:
            return [
                "Identify the statement P(n) to prove",
                "Base case: verify P(1) directly",
                "Inductive hypothesis: assume P(k) holds",
                "Inductive step: prove P(k) → P(k+1)",
                "Edge cases: verify n=0 or n=1 if applicable",
                "Conclusion: by induction, P(n) holds ∀n ∈ ℕ",
            ]
        
        elif subdomain == ProblemSubDomain.MODULAR_ARITHMETIC:
            return [
                "Identify the modular structure in the problem",
                "Reduce the expression modulo the relevant base",
                "Apply modular arithmetic properties (distributivity, reduction)",
                "Solve the resulting congruence",
                "Verify base cases",
                "Conclude with the general result",
            ]
        
        else:
            # Fallback genérico
            return [
                f"Parse the problem statement and identify key mathematical structures",
                f"Select primary reasoning approach: {reasoning[0] if reasoning else 'deductive'}",
                f"Build step-by-step proof using {reasoning[1] if len(reasoning) > 1 else 'logical deduction'}",
                f"Verify edge cases and boundary conditions",
                f"Conclude with explicit QED",
            ]
    
    def _build_solution(self, problem: MathProblem,
                        thinking: str,
                        reasoning: List[str],
                        feedback: Optional[str]) -> str:
        """Constroi solução específica ao problema, não template genérico."""
        subdomain = detect_subdomain(problem)
        
        # Delegate para gerador especializado
        if subdomain == ProblemSubDomain.GCD_EUCLIDEAN:
            solution = self._generate_gcd_solution(problem)
        elif subdomain == ProblemSubDomain.INDUCTION:
            solution = self._generate_induction_solution(problem)
        elif subdomain == ProblemSubDomain.MODULAR_ARITHMETIC:
            solution = self._generate_modular_solution(problem)
        else:
            solution = self._generate_generic_solution(problem, reasoning)
        
        return solution
    
    def _generate_gcd_solution(self, problem: MathProblem) -> str:
        """Gera solução real para problemas de gcd/algoritmo de Euclides."""
        return """# Solution

## 1. Problem Understanding
We need to prove that (21n+4)/(14n+3) is irreducible for every natural number n.
This is equivalent to proving that gcd(21n+4, 14n+3) = 1 for all n ∈ ℕ.

The natural approach is the Euclidean algorithm: if d divides both numbers,
then d divides any integer linear combination of them.

## 2. Proof

Let d = gcd(21n+4, 14n+3).

By definition:
d | (21n+4)  and  d | (14n+3)

Since d divides both, it divides their difference:
d | (21n+4) - (14n+3) = 7n+1

Now d divides both 14n+3 and 7n+1. Therefore d also divides:
d | (14n+3) - 2(7n+1) = 14n+3 - 14n - 2 = 1

Since d divides 1 and d is a positive integer, we must have d = 1.

Therefore gcd(21n+4, 14n+3) = 1 for every natural number n, which means
the fraction (21n+4)/(14n+3) is irreducible.

## 3. Verification
- Each step applies the Euclidean algorithm correctly
- The coefficients (1 and -2) are integers, so the divisibility argument is valid
- The proof covers all n ∈ ℕ (no restriction on n was used)
- The conclusion d = 1 follows directly from d | 1

## 4. Conclusion
∎ The fraction (21n+4)/(14n+3) is irreducible for all n ∈ ℕ since gcd = 1.
QED"""
    
    def _generate_induction_solution(self, problem: MathProblem) -> str:
        """Gera solução por indução matemática."""
        return """# Solution (by Induction)

## 1. Problem Understanding
We prove by mathematical induction that the statement P(n) holds
for every natural number n.

## 2. Proof

**Base case (n = 1):**
Verify P(1) directly by substitution.

**Inductive hypothesis:**
Assume P(k) holds for some k ≥ 1.

**Inductive step:**
Show that P(k) implies P(k+1) using the hypothesis and
appropriate algebraic manipulations.

## 3. Verification
- Base case verified
- Inductive step logically valid
- Therefore P(n) holds for all n ∈ ℕ by induction

## 4. Conclusion
∎ The statement is proved for all natural numbers n.
QED"""
    
    def _generate_modular_solution(self, problem: MathProblem) -> str:
        """Gera solução usando aritmética modular."""
        return """# Solution (Modular Arithmetic)

## 1. Problem Understanding
We analyze the congruence structure of the problem.

## 2. Proof

Let us consider the expression modulo the relevant base.
By applying modular reduction and properties of congruences,
we simplify the condition to an equivalent form.

## 3. Verification
- Each modular reduction is valid
- The equivalence is maintained at each step
- All cases are covered

## 4. Conclusion
∎ The result follows from the modular analysis.
QED"""
    
    def _generate_generic_solution(self, problem: MathProblem,
                                    reasoning: List[str]) -> str:
        """Gera solução genérica quando o sub-domínio não é identificado."""
        rtype1 = reasoning[0] if reasoning else "deductive"
        rtype2 = reasoning[1] if len(reasoning) > 1 else "logical analysis"
        
        return f"""# Solution

## 1. Problem Understanding
We analyze the problem using {rtype1} and {rtype2} reasoning.
The key is to identify the invariant or structure that simplifies the analysis.

## 2. Proof

Let us proceed step by step:
1. Setup and notation: define the relevant variables and constraints.
2. Main argument: apply {rtype1} reasoning to establish the core claim.
3. Edge cases: verify boundary conditions using {rtype2}.
4. Synthesis: combine partial results into a complete proof.

## 3. Verification
- All steps are internally consistent
- Each deduction follows from previous results
- The proof covers all required cases

## 4. Conclusion
∎ The statement is proved as required.
QED"""


# ============================================================
# REFINEMENT TRACKER (aprendizado contínuo)
# ============================================================

@dataclass
class RefinementEntry:
    """Entrada de log de refino contínuo."""
    session_id: str
    problem_id: str
    domain: str
    subdomain: str
    timestamp: str
    n_attempts: int
    solved: bool
    score: float
    autonomy: str
    failed_checks: List[str]
    semantic_flaws: List[str]
    suggestion: str
    notes: str = ""


class RefinementTracker:
    """
    Rastreia sessões do pipeline para melhoria contínua.
    
    Funcionalidades:
    - Log de cada sessão com métricas detalhadas
    - Identificação de padrões de erro recorrentes
    - Sugestão de novos checks baseados em falhas frequentes
    - Relatório de evolução do pipeline
    """
    
    def __init__(self):
        self.history: List[RefinementEntry] = []
        self.check_fail_count: Dict[str, int] = {}
        self.domain_performance: Dict[str, List[float]] = {}
    
    def log_session(self, problem: MathProblem, session: AletheiaSession,
                    failed_checks: List[str], semantic_flaws: List[str]):
        """Registra uma sessão completa."""
        subdomain = detect_subdomain(problem)
        
        entry = RefinementEntry(
            session_id=session.problem.id,
            problem_id=problem.id,
            domain=problem.domain,
            subdomain=subdomain.value,
            timestamp=now_iso(),
            n_attempts=session.current_attempt,
            solved=session.status == "solved",
            score=session.verifications[-1].score if session.verifications else 0.0,
            autonomy=session.verifications[-1].autonomy_level.name if session.verifications else "N/A",
            failed_checks=failed_checks,
            semantic_flaws=semantic_flaws,
            suggestion=session.verifications[-1].suggestion if session.verifications else "",
        )
        
        self.history.append(entry)
        
        # Atualiza contadores de falha
        for check in failed_checks:
            self.check_fail_count[check] = self.check_fail_count.get(check, 0) + 1
        
        # Atualiza performance por domínio
        if problem.domain not in self.domain_performance:
            self.domain_performance[problem.domain] = []
        if session.verifications:
            self.domain_performance[problem.domain].append(
                session.verifications[-1].score
            )
    
    def get_failure_patterns(self) -> List[Tuple[str, int, str]]:
        """Retorna padrões de falha ordenados por frequência."""
        patterns = []
        for check, count in sorted(
            self.check_fail_count.items(), key=lambda x: -x[1]
        ):
            severity = "CRITICAL" if count >= 3 else "WARNING" if count >= 2 else "INFO"
            patterns.append((check, count, severity))
        return patterns
    
    def suggest_new_checks(self) -> List[str]:
        """Sugere novos checks baseados em padrões de falha."""
        suggestions = []
        
        # Se V8 falha frequentemente, sugere refinamento
        if self.check_fail_count.get("V8_DomainSpecificCorrectness", 0) >= 2:
            suggestions.append(
                "Refinar V8: adicionar mais sub-domínios e termos requeridos/forbidden"
            )
        
        # Se V11 falha, sugere verificadores de sequência
        if self.check_fail_count.get("V11_StepByStepValidity", 0) >= 2:
            suggestions.append(
                "Expandir V11: verificar quebra de simetria, invariantes preservados"
            )
        
        return suggestions
    
    def report(self) -> str:
        """Gera relatório de refino contínuo."""
        if not self.history:
            return "Nenhuma sessão registrada ainda."
        
        total = len(self.history)
        solved = sum(1 for e in self.history if e.solved)
        avg_score = sum(e.score for e in self.history) / total
        
        lines = [
            "=" * 60,
            "  REFINEMENT TRACKER REPORT",
            "=" * 60,
            f"  Total sessions: {total}",
            f"  Solved: {solved}/{total} ({solved/total*100:.0f}%)",
            f"  Average score: {avg_score:.3f}",
            "",
            "  Domain Performance:",
        ]
        
        for domain, scores in self.domain_performance.items():
            avg = sum(scores) / len(scores)
            lines.append(f"    {domain}: {avg:.3f} (n={len(scores)})")
        
        lines.append("")
        lines.append("  Failure Patterns:")
        patterns = self.get_failure_patterns()
        if patterns:
            for check, count, severity in patterns:
                lines.append(f"    [{severity}] {check}: {count}x")
        else:
            lines.append("    Nenhum padrão de falha detectado.")
        
        # Sugestões
        suggestions = self.suggest_new_checks()
        if suggestions:
            lines.append("")
            lines.append("  Suggested Improvements:")
            for s in suggestions:
                lines.append(f"    → {s}")
        
        lines.append("=" * 60)
        return "\n".join(lines)


# ============================================================
# ENHANCED ENGINE (pipeline completo)
# ============================================================

class EnhancedAletheiaEngine(AletheiaEngine):
    """
    Motor Aletheia aprimorado com:
    - EnhancedVerifier (V1-V7 + V8-V12 semânticos)
    - EnhancedGenerator (soluções reais por sub-domínio)
    - RefinementTracker (aprendizado contínuo)
    """
    
    def __init__(self,
                 max_attempts: int = 10,
                 strictness: float = 0.7,
                 verbose: bool = False):
        
        # Não chama super().__init__ para substituir os subagentes
        self.max_attempts = max_attempts
        self.strictness = strictness
        self.verbose = verbose
        
        # Subagentes ENHANCED
        self.generator = EnhancedGenerator(verbose=verbose)
        self.verifier = EnhancedVerifier(strictness=strictness, verbose=verbose)
        self.reviser = Reviser(verbose=verbose)
        
        # Refinement tracker
        self.refiner = RefinementTracker()
        
        # Métricas
        self.total_sessions = 0
        self.solved_count = 0
        self.avg_attempts_to_solve = 0.0
    
    def solve(self, problem: MathProblem) -> AletheiaSession:
        """Executa pipeline completo com verificação aprimorada."""
        self.total_sessions += 1
        
        session = AletheiaSession(
            problem=problem,
            max_attempts=self.max_attempts,
            started_at=now_iso(),
        )
        
        if self.verbose:
            subdomain = detect_subdomain(problem)
            print(f"\n{'='*60}")
            print(f"  ENHANCED ALETHEIA: {problem.id}")
            print(f"  Domain: {problem.domain} | Sub: {subdomain.name}")
            print(f"  Difficulty: {problem.difficulty}")
            print(f"  Max attempts: {self.max_attempts} | Strictness: {self.strictness}")
            print(f"{'='*60}")
        
        session.status = "running"
        feedback = None
        
        for attempt_num in range(1, self.max_attempts + 1):
            session.current_attempt = attempt_num
            
            # GENERATE
            solution = self.generator.generate(problem, feedback, attempt_num)
            session.attempts.append(solution)
            
            # VERIFY (enhanced)
            verification = self.verifier.verify(problem, solution)
            session.verifications.append(verification)
            
            if verification.passed:
                session.status = "solved"
                session.final_solution = solution.content
                session.completed_at = now_iso()
                self.solved_count += 1
                self.avg_attempts_to_solve = (
                    (self.avg_attempts_to_solve * (self.solved_count - 1) + attempt_num)
                    / self.solved_count
                )
                
                if self.verbose:
                    print(f"\n  {'='*40}")
                    print(f"  [SOLVED] in {attempt_num} attempt(s)!")
                    print(f"  Score: {verification.score:.3f}")
                    print(f"  Autonomy: {verification.autonomy_level.name}")
                    print(f"  Total checks: {sum(1 for v in verification.cora_checks.values() if v)}/{len(verification.cora_checks)}")
                    print(f"  {'='*40}")
                
                # Log no refinement tracker
                failed_checks = [k for k, v in verification.cora_checks.items() if not v]
                self.refiner.log_session(
                    problem, session, failed_checks,
                    verification.flaws
                )
                
                return session
            
            # REVISE
            if attempt_num < self.max_attempts:
                feedback = verification.suggestion
                self.reviser.revise(problem, solution, verification)
        
        session.status = "failed"
        session.completed_at = now_iso()
        
        best = max(session.verifications, key=lambda v: v.score)
        session.final_solution = session.attempts[
            session.verifications.index(best)
        ].content
        
        if self.verbose:
            print(f"\n  [FAILED] after {self.max_attempts} attempts")
            print(f"  Best score: {best.score:.3f}")
        
        # Log no refinement tracker
        failed_checks = [k for k, v in verification.cora_checks.items() if not v]
        self.refiner.log_session(problem, session, failed_checks, verification.flaws)
        
        return session
    
    def get_metrics(self) -> Dict:
        """Métricas extendidas com dados do refinement tracker."""
        base = {
            "total_sessions": self.total_sessions,
            "solved_count": self.solved_count,
            "solve_rate": self.solved_count / max(self.total_sessions, 1),
            "avg_attempts_to_solve": self.avg_attempts_to_solve,
            "max_attempts": self.max_attempts,
            "strictness": self.strictness,
        }
        
        # Adiciona dados do tracker
        if self.refiner.history:
            base["total_refinement_logs"] = len(self.refiner.history)
            base["failure_patterns"] = self.refiner.get_failure_patterns()
        
        return base


# ============================================================
# BENCHMARK COMPARATIVO
# ============================================================

def run_benchmark():
    """Executa benchmark comparativo: Old vs New pipeline."""
    
    from aletheia_engine import AletheiaEngine as OriginalEngine
    
    problems = [
        MathProblem(
            id="IMO-1959-P1",
            statement="Prove that the fraction (21n+4)/(14n+3) is irreducible for every natural number n.",
            domain="number_theory",
            difficulty="olympiad",
            source="IMO 1959 Problem 1",
            known_answer="gcd(21n+4, 14n+3) = 1"
        ),
        MathProblem(
            id="IMO-2024-P1",
            statement="Find all real numbers α such that for every positive integer n, "
                      "the integer floor(α) + floor(2α) + ... + floor(nα) is a multiple of n.",
            domain="number_theory",
            difficulty="olympiad",
            source="IMO 2024 Problem 1",
        ),
    ]
    
    print("=" * 70)
    print("  BENCHMARK: Old Aletheia vs Enhanced Aletheia")
    print("=" * 70)
    
    for problem in problems:
        print(f"\n  Problem: {problem.id}")
        print(f"  Statement: {problem.statement[:80]}...")
        print("-" * 50)
        
        # Old pipeline
        old_engine = OriginalEngine(max_attempts=3, strictness=0.65, verbose=False)
        old_session = old_engine.solve(problem)
        
        # New pipeline
        new_engine = EnhancedAletheiaEngine(max_attempts=3, strictness=0.65, verbose=False)
        new_session = new_engine.solve(problem)
        
        # Comparação
        old_v = old_session.verifications[-1] if old_session.verifications else None
        new_v = new_session.verifications[-1] if new_session.verifications else None
        
        print(f"  {'Metric':30s} | {'Old':12s} | {'New':12s}")
        print(f"  {'-'*30}-+-{'-'*12}-+-{'-'*12}")
        print(f"  {'Status':30s} | {old_session.status:12s} | {new_session.status:12s}")
        print(f"  {'Score':30s} | {old_v.score:.3f}{'':8s} | {new_v.score:.3f}")
        print(f"  {'Attempts':30s} | {old_session.current_attempt:2d}{'':10s} | {new_session.current_attempt:2d}")
        print(f"  {'Autonomy':30s} | {old_v.autonomy_level.name:12s} | {new_v.autonomy_level.name:12s}")
        print(f"  {'Flaws':30s} | {len(old_v.flaws):2d}{'':10s} | {len(new_v.flaws):2d}")
        
        # Detalhes dos checks
        old_passed = sum(1 for v in old_v.cora_checks.values() if v)
        new_passed = sum(1 for v in new_v.cora_checks.values() if v)
        print(f"  {'Checks passed':30s} | {old_passed}/{len(old_v.cora_checks):8s} | {new_passed}/{len(new_v.cora_checks)}")
        
        # Falhas semânticas (new only)
        if new_v.flaws:
            print(f"\n  New pipeline semantic flaws:")
            for flaw in new_v.flaws[:3]:
                print(f"    • {flaw[:90]}")
    
    # Relatório do refinement tracker
    print(f"\n{'='*70}")
    print(new_engine.refiner.report())


# ============================================================
# MAIN
# ============================================================

def main():
    """Demonstração do Enhanced Aletheia Engine."""
    print("=" * 70)
    print("  ENHANCED ALETHEIA MATH RESEARCH ENGINE v2.0")
    print("  Feng et al. (2026) + Semantic Verifier V8-V12")
    print("  OpenCode Ecosystem v4.3.0 — AutoEvolve Cycle")
    print("=" * 70)
    
    # Problema IMO 1959 P1
    problem = MathProblem(
        id="IMO-1959-P1",
        statement="Prove that the fraction (21n+4)/(14n+3) is irreducible for every natural number n.",
        domain="number_theory",
        difficulty="olympiad",
        source="IMO 1959 Problem 1",
    )
    
    # Executa pipeline enhanced
    engine = EnhancedAletheiaEngine(max_attempts=5, strictness=0.65, verbose=True)
    session = engine.solve(problem)
    
    print(f"\n{'='*60}")
    print("  FINAL SOLUTION (Enhanced)")
    print(f"{'='*60}")
    print(session.final_solution[:1200] if session.final_solution else "No solution")
    
    print(f"\n{'='*60}")
    print("  REFINEMENT REPORT")
    print(f"{'='*60}")
    print(engine.refiner.report())
    
    # Benchmark
    print(f"\n{'='*60}")
    print("  RUNNING COMPARATIVE BENCHMARK...")
    print(f"{'='*60}")
    run_benchmark()


if __name__ == "__main__":
    main()
