"""
phd_auditor.py - PhD Auditor para validacao cientifica de estruturas de prova

Avalia qualidade cientifica das provas geradas (mesmo incompletas)
usando 10 dimensoes independentes com verificadores V1-V7.

Inspirado por Cora-Debate V1-V6 + PhD Auditor do MiroFish.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
import math


class VerifierType(Enum):
    """7 tipos de verificadores especializados"""
    V1_LOGIC = "logic_checker"           # Verifica consistencia logica
    V2_STRUCTURE = "structure_checker"   # Verifica estrutura do teorema
    V3_COMPLETENESS = "completeness"     # Verifica integridade (sorry count)
    V4_RIGOR = "rigor_checker"          # Verifica rigor matematico
    V5_STYLE = "style_checker"          # Verifica estilo Lean idiomatico
    V6_COVERAGE = "coverage_checker"    # Verifica cobertura de casos
    V7_INFERENCE = "inference_checker"  # Verifica inferencias implicitas


class ScientificDimension(Enum):
    """10 dimensoes independentes de avaliacao cientifica"""
    LOGICAL_CORRECTNESS = "logical_correctness"        # 0-10: fatos logicamente coerentes?
    THEOREM_STRUCTURE = "theorem_structure"            # 0-10: estrutura theorem/lemma clara?
    HYPOTHESIS_CLARITY = "hypothesis_clarity"          # 0-10: hipoteses explicitas?
    CONCLUSION_CLARITY = "conclusion_clarity"          # 0-10: conclusao clara?
    PROOF_COMPLETENESS = "proof_completeness"          # 0-10: sorry count? (inverso)
    PROOF_RIGOR = "proof_rigor"                       # 0-10: passos logicos justificados?
    CASE_ANALYSIS = "case_analysis"                   # 0-10: analise de casos adequada?
    INDUCTION_VALIDITY = "induction_validity"         # 0-10: inducao bem-formada?
    LEAN_IDIOMATICITY = "lean_idiomaticity"           # 0-10: codigo Lean idiomatico?
    MATHEMATICAL_INSIGHT = "mathematical_insight"    # 0-10: tem insight/novidade?


@dataclass
class VerifierScore:
    """Score de um verificador em uma dimensao"""
    verifier: VerifierType
    dimension: ScientificDimension
    score: float  # [0, 10]
    confidence: float  # [0, 1]
    evidence: str  # Justificativa
    timestamp: str


@dataclass
class DimensionScore:
    """Score agregado de uma dimensao (media ponderada de verificadores)"""
    dimension: ScientificDimension
    avg_score: float  # [0, 10]
    min_score: float
    max_score: float
    num_verifiers: int
    verifier_scores: List[VerifierScore]


@dataclass
class ProofAuditResult:
    """Resultado completo da auditoria de uma prova"""
    problem_id: str
    domain: str
    statement: str
    lean_code: str
    natural_proof: str
    
    # Scores por dimensao
    dimension_scores: Dict[str, DimensionScore]
    overall_score: float  # [0, 100]
    
    # Categorias derivadas
    proof_quality_tier: str  # "A" (85+), "B" (70-84), "C" (55-69), "D" (<55)
    confidence: float  # [0, 1]
    
    # Diagnostico
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    
    timestamp: str


class PhDAuditor:
    """PhD Auditor para validacao cientifica multiagente"""
    
    def __init__(self):
        self.verifiers = {
            VerifierType.V1_LOGIC: self._verify_logic,
            VerifierType.V2_STRUCTURE: self._verify_structure,
            VerifierType.V3_COMPLETENESS: self._verify_completeness,
            VerifierType.V4_RIGOR: self._verify_rigor,
            VerifierType.V5_STYLE: self._verify_style,
            VerifierType.V6_COVERAGE: self._verify_coverage,
            VerifierType.V7_INFERENCE: self._verify_inference,
        }
    
    def audit_proof(
        self,
        problem_id: str,
        domain: str,
        statement: str,
        lean_code: str,
        natural_proof: str
    ) -> ProofAuditResult:
        """Audita uma prova em todas as 10 dimensoes com 7 verificadores"""
        
        import datetime
        timestamp = datetime.datetime.utcnow().isoformat()
        
        # Executar todos os 7 verificadores em paralelo (simulado sequencial)
        dimension_scores = {}
        all_verifier_scores = []
        
        for dimension in ScientificDimension:
            scores_for_dim = []
            
            for verifier_type, verify_func in self.verifiers.items():
                score = verify_func(
                    problem_id, domain, statement, lean_code, natural_proof, dimension
                )
                scores_for_dim.append(score)
                all_verifier_scores.append(score)
            
            # Agregar scores dessa dimensao
            avg = sum(s.score for s in scores_for_dim) / len(scores_for_dim)
            min_s = min(s.score for s in scores_for_dim)
            max_s = max(s.score for s in scores_for_dim)
            
            dimension_scores[dimension.value] = DimensionScore(
                dimension=dimension,
                avg_score=avg,
                min_score=min_s,
                max_score=max_s,
                num_verifiers=len(scores_for_dim),
                verifier_scores=scores_for_dim
            )
        
        # Calcular overall score (media de todas as dimensoes)
        overall = sum(ds.avg_score for ds in dimension_scores.values()) / len(dimension_scores)
        
        # Determinar tier e confianca
        if overall >= 85:
            tier = "A"
            conf = 0.90
        elif overall >= 70:
            tier = "B"
            conf = 0.75
        elif overall >= 55:
            tier = "C"
            conf = 0.60
        else:
            tier = "D"
            conf = 0.40
        
        # Diagnostico
        strengths, weaknesses, recommendations = self._diagnose(
            dimension_scores, lean_code, natural_proof
        )
        
        return ProofAuditResult(
            problem_id=problem_id,
            domain=domain,
            statement=statement,
            lean_code=lean_code,
            natural_proof=natural_proof,
            dimension_scores=dimension_scores,
            overall_score=overall,
            proof_quality_tier=tier,
            confidence=conf,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            timestamp=timestamp
        )
    
    def _verify_logic(self, pid, domain, stmt, code, proof, dim: ScientificDimension) -> VerifierScore:
        """V1: Verifica consistencia logica"""
        
        if dim == ScientificDimension.LOGICAL_CORRECTNESS:
            # Verificar contradicoes basicas
            has_contradiction = "False" in code and "True" in code and "and False" in code
            score = 3.0 if has_contradiction else 7.5
            evidence = "Sem contradicoes booleanas detectadas" if score > 5 else "Potencial contradicao"
        
        elif dim == ScientificDimension.HYPOTHESIS_CLARITY:
            # Verificar se hipoteses estao explicitas
            hypothesis_count = code.count("(") - code.count("sorry")
            score = min(10.0, hypothesis_count)
            evidence = f"Encontradas {int(hypothesis_count)} hipoteses explicitas"
        
        else:
            score = 5.0
            evidence = "Dimensao nao avaliada por V1"
        
        return VerifierScore(
            verifier=VerifierType.V1_LOGIC,
            dimension=dim,
            score=score,
            confidence=0.75,
            evidence=evidence,
            timestamp=""
        )
    
    def _verify_structure(self, pid, domain, stmt, code, proof, dim: ScientificDimension) -> VerifierScore:
        """V2: Verifica estrutura do teorema"""
        
        if dim == ScientificDimension.THEOREM_STRUCTURE:
            # Verificar presenca de theorem/lemma
            has_theorem = "theorem" in code or "lemma" in code
            score = 8.0 if has_theorem else 4.0
            evidence = "Estrutura theorem/lemma presente" if has_theorem else "Falta estrutura basica"
        
        elif dim == ScientificDimension.CONCLUSION_CLARITY:
            # Verificar clareza da conclusao (presenca de := ou by)
            has_proof_start = ":=" in code or "by" in code
            score = 7.5 if has_proof_start else 3.0
            evidence = "Conclusao com prova iniciada" if has_proof_start else "Conclusao sem corpo de prova"
        
        else:
            score = 5.0
            evidence = "Dimensao nao avaliada por V2"
        
        return VerifierScore(
            verifier=VerifierType.V2_STRUCTURE,
            dimension=dim,
            score=score,
            confidence=0.80,
            evidence=evidence,
            timestamp=""
        )
    
    def _verify_completeness(self, pid, domain, stmt, code, proof, dim: ScientificDimension) -> VerifierScore:
        """V3: Verifica integridade (sorry count)"""
        
        if dim == ScientificDimension.PROOF_COMPLETENESS:
            # Contar sorries
            sorry_count = code.count("sorry")
            total_lines = len(code.split("\n"))
            
            # Score inverso: menos sorry = melhor
            sorry_ratio = sorry_count / max(total_lines, 1)
            score = max(0.0, 10.0 * (1.0 - sorry_ratio))
            
            evidence = f"{sorry_count} sorry(s) em {total_lines} linhas (taxa: {sorry_ratio:.1%})"
        
        else:
            score = 5.0
            evidence = "Dimensao nao avaliada por V3"
        
        return VerifierScore(
            verifier=VerifierType.V3_COMPLETENESS,
            dimension=dim,
            score=score,
            confidence=0.95,
            evidence=evidence,
            timestamp=""
        )
    
    def _verify_rigor(self, pid, domain, stmt, code, proof, dim: ScientificDimension) -> VerifierScore:
        """V4: Verifica rigor matematico"""
        
        if dim == ScientificDimension.PROOF_RIGOR:
            # Verificar presenca de tactics rigorosos (ring, field, decide, etc)
            rigorous_tactics = ["ring", "field_simp", "decide", "simp", "norm_num", "omega"]
            tactic_count = sum(code.count(t) for t in rigorous_tactics)
            score = min(10.0, 3.0 + tactic_count)
            evidence = f"Encontradas {tactic_count} tactics rigorosos"
        
        elif dim == ScientificDimension.CASE_ANALYSIS:
            # Verificar presenca de analise de casos
            has_cases = "cases" in code or "match" in code or "if" in code
            score = 7.0 if has_cases else 4.0
            evidence = "Analise de casos presente" if has_cases else "Sem analise de casos detectada"
        
        else:
            score = 5.0
            evidence = "Dimensao nao avaliada por V4"
        
        return VerifierScore(
            verifier=VerifierType.V4_RIGOR,
            dimension=dim,
            score=score,
            confidence=0.70,
            evidence=evidence,
            timestamp=""
        )
    
    def _verify_style(self, pid, domain, stmt, code, proof, dim: ScientificDimension) -> VerifierScore:
        """V5: Verifica estilo Lean idiomatico"""
        
        if dim == ScientificDimension.LEAN_IDIOMATICITY:
            # Verificar convencoes Lean
            idiom_score = 5.0
            
            # Preferencias Lean 4
            if "def" in code:
                idiom_score += 1.0
            if "theorem" in code:
                idiom_score += 1.5
            if "where" in code:
                idiom_score += 0.5
            if "fun" in code:
                idiom_score += 1.0
            if "calc" in code:
                idiom_score += 1.5
            
            score = min(10.0, idiom_score)
            evidence = f"Score idiomatico calculado: {score:.1f}/10"
        
        else:
            score = 5.0
            evidence = "Dimensao nao avaliada por V5"
        
        return VerifierScore(
            verifier=VerifierType.V5_STYLE,
            dimension=dim,
            score=score,
            confidence=0.65,
            evidence=evidence,
            timestamp=""
        )
    
    def _verify_coverage(self, pid, domain, stmt, code, proof, dim: ScientificDimension) -> VerifierScore:
        """V6: Verifica cobertura de casos"""
        
        if dim == ScientificDimension.CASE_ANALYSIS:
            # Detectar quantos casos sao tratados
            case_keywords = ["cases", "match", "if", "ite"]
            case_count = sum(code.count(kw) for kw in case_keywords)
            score = min(10.0, 2.0 + case_count * 1.5)
            evidence = f"Detectadas {case_count} construcoes de case"
        
        elif dim == ScientificDimension.INDUCTION_VALIDITY:
            # Verificar se ha inducao
            has_induction = "induction" in code or "Nat.recOn" in code or "Nat.casesOn" in code
            score = 8.0 if has_induction else 3.0
            evidence = "Inducao detectada" if has_induction else "Sem inducao (pode nao ser necessario)"
        
        else:
            score = 5.0
            evidence = "Dimensao nao avaliada por V6"
        
        return VerifierScore(
            verifier=VerifierType.V6_COVERAGE,
            dimension=dim,
            score=score,
            confidence=0.68,
            evidence=evidence,
            timestamp=""
        )
    
    def _verify_inference(self, pid, domain, stmt, code, proof, dim: ScientificDimension) -> VerifierScore:
        """V7: Verifica inferencias implicitas"""
        
        if dim == ScientificDimension.MATHEMATICAL_INSIGHT:
            # Detectar se ha insight/tecnicas nao-triviais
            insight_markers = ["calc", "ring", "field_simp", "nlinarith", "omega", "decide"]
            insight_count = sum(code.count(m) for m in insight_markers)
            score = min(10.0, 3.0 + insight_count)
            evidence = f"Detectadas {insight_count} tecnicas avancadas"
        
        elif dim == ScientificDimension.HYPOTHESIS_CLARITY:
            # Hipoteses sao explicitas ou implicitas?
            explicit_hyp = code.count("assume") + code.count("intro")
            implicit_hyp = code.count("(") - explicit_hyp
            score = 5.0 + (explicit_hyp / max(implicit_hyp, 1))
            score = min(10.0, score)
            evidence = f"{explicit_hyp} hipoteses explicitas, {implicit_hyp} implicitas"
        
        else:
            score = 5.0
            evidence = "Dimensao nao avaliada por V7"
        
        return VerifierScore(
            verifier=VerifierType.V7_INFERENCE,
            dimension=dim,
            score=score,
            confidence=0.60,
            evidence=evidence,
            timestamp=""
        )
    
    def _diagnose(self, dim_scores: Dict, code: str, proof: str) -> Tuple[List[str], List[str], List[str]]:
        """Gera diagnostico: forca/fraqueza/recomendacoes"""
        
        strengths = []
        weaknesses = []
        recommendations = []
        
        # Analisar por dimensao
        for dim_name, dim_score in dim_scores.items():
            if dim_score.avg_score >= 8.0:
                strengths.append(f"{dim_name}: excelente ({dim_score.avg_score:.1f}/10)")
            elif dim_score.avg_score <= 4.0:
                weaknesses.append(f"{dim_name}: fraco ({dim_score.avg_score:.1f}/10)")
        
        # Recomendacoes baseadas em fraquezas
        sorry_count = code.count("sorry")
        if sorry_count > 0:
            recommendations.append(f"Remover {sorry_count} placeholder(s) sorry")
        
        if "Nat.recOn" not in code and "induction" not in code and "Nat.casesOn" not in code:
            recommendations.append("Considerar inducao se aplicavel ao dominio")
        
        if "calc" not in code and len(code) > 200:
            recommendations.append("Usar 'calc' para provas com multiplos passos")
        
        if len(strengths) == 0:
            strengths.append("Estrutura basica presente")
        
        return strengths, weaknesses, recommendations
    
    def batch_audit(self, proofs: List[Dict]) -> List[ProofAuditResult]:
        """Audita multiplas provas"""
        results = []
        for proof in proofs:
            result = self.audit_proof(
                problem_id=proof['problem_id'],
                domain=proof['domain'],
                statement=proof['statement'],
                lean_code=proof['lean_code'],
                natural_proof=proof['natural_proof']
            )
            results.append(result)
        return results


if __name__ == "__main__":
    # Teste simples
    auditor = PhDAuditor()
    
    test_proof = {
        'problem_id': 'A0004',
        'domain': 'combinatorics',
        'statement': 'For any finite set S with n elements, |P(S)| = 2^n',
        'lean_code': '''theorem power_set_cardinality (S : Finset Nat) : 
  (Finset.powerset S).card = 2 ^ S.card := by
  sorry''',
        'natural_proof': 'Proof by induction on |S|. Base case: empty set has 1 subset. Inductive case: ...'
    }
    
    result = auditor.audit_proof(**test_proof)
    
    print(f"\nProof: {result.problem_id}")
    print(f"Overall Score: {result.overall_score:.1f}/100")
    print(f"Tier: {result.proof_quality_tier}")
    print(f"Confidence: {result.confidence:.0%}")
    print(f"\nDimensions:")
    for dim_name, dim_score in result.dimension_scores.items():
        print(f"  {dim_name}: {dim_score.avg_score:.1f}/10")
