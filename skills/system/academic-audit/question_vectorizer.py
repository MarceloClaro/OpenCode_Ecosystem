#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QuestionVectorizer v1.0 — Vetorização e Seleção de Perguntas (OQS Etapa 4-7)
================================================================================
SPEC-056: Optimal Question Scanner — Componente de vetorização e seleção.

Transforma perguntas candidatas em vetores com 6 dimensões e calcula
o Convergence Score (CS) para selecionar a pergunta ótima.

Pergunta Ótima = CS* = argmax(URS + SVS - DRI - CCI)

Uso:
    from question_vectorizer import QuestionVectorizer
    qv = QuestionVectorizer()
    result = qv.analyze("Problema", ["Pergunta 1?", "Pergunta 2?"])
    print(f"Ótima: {result.optimal_question}")
"""

from __future__ import annotations

import re
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════
# TYPES & ENUMS
# ═══════════════════════════════════════════════════════════════════════

class QuestionType(Enum):
    DEFINIÇÃO = "definição"
    CAUSALIDADE = "causalidade"
    COMPARAÇÃO = "comparação"
    VALIDAÇÃO = "validação"
    FALSIFICAÇÃO = "falsificação"
    OPERACIONALIZAÇÃO = "operacionalização"
    MÉTRICA = "métrica"
    IMPACTO = "impacto"
    SEQUÊNCIA = "sequência"
    INTEGRAÇÃO = "integração"

    @classmethod
    def classify(cls, question: str) -> "QuestionType":
        """Classifica o tipo de pergunta com base em padrões linguísticos."""
        q = question.lower().strip()
        if re.search(r'\b(o que|qual é|como definir)\b', q):
            return cls.DEFINIÇÃO
        if re.search(r'\b(por que|causa|razão|motivo|origem)\b', q):
            return cls.CAUSALIDADE
        if re.search(r'\b(diferença|compara[çc]ão|versus|vs|melhor que|pior que)\b', q):
            return cls.COMPARAÇÃO
        if re.search(r'\b(é válido|funciona|é verdade|é correto|proof|prova)\b', q):
            return cls.VALIDAÇÃO
        if re.search(r'\b(e se não|falso|exceção|contraexemplo|counter)\b', q):
            return cls.FALSIFICAÇÃO
        if re.search(r'\b(como medir|como implementar|como calcular|passo a passo)\b', q):
            return cls.OPERACIONALIZAÇÃO
        if re.search(r'\b(métrica|indicador|medida|quanto|threshold)\b', q):
            return cls.MÉTRICA
        if re.search(r'\b(impacto|consequência|efeito|resultado|implicação)\b', q):
            return cls.IMPACTO
        if re.search(r'\b(próximo|depois|seguinte|sequência|ordem|etapa)\b', q):
            return cls.SEQUÊNCIA
        if re.search(r'\b(integr[ao]|síntese|unifica[rc]|combina[rc]|conexão)\b', q):
            return cls.INTEGRAÇÃO
        return cls.DEFINIÇÃO  # fallback


# ═══════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class QuestionVector:
    """Vetor de 6 dimensões representando uma pergunta."""
    direction: float        # 0-10: quão direcional é a pergunta
    scope: float            # 0-10: amplitude do escopo
    depth: float            # 0-10: profundidade investigativa
    reduction_power: float  # 0-10: poder de redução de incerteza
    dispersion_risk: float  # 0-10: risco de abrir ruído (MENOR é melhor)
    cognitive_cost: float   # 0-10: custo cognitivo (MENOR é melhor)

    def to_dict(self) -> dict[str, float]:
        return {
            "direction": round(self.direction, 1),
            "scope": round(self.scope, 1),
            "depth": round(self.depth, 1),
            "reduction_power": round(self.reduction_power, 1),
            "dispersion_risk": round(self.dispersion_risk, 1),
            "cognitive_cost": round(self.cognitive_cost, 1),
        }


@dataclass
class ScoredQuestion:
    """Pergunta com vetor completo e métricas de convergência."""
    question: str
    type: QuestionType
    vector: QuestionVector
    uncertainty_reduction: float   # URS = Uncertainty Reduction Score (0-10)
    structural_value: float        # SVS = Structural Value Score (0-10)
    dispersion_risk_index: float   # DRI = Dispersion Risk Index (0-10, MENOR melhor)
    cognitive_cost_index: float    # CCI = Cognitive Cost Index (0-10, MENOR melhor)
    convergence_score: float       # CS = Convergence Score (-20 a +20)
    rationale: str = ""


@dataclass
class QuestionAnalysisResult:
    """Resultado completo da análise de perguntas."""
    problem: str
    candidate_questions: list[ScoredQuestion]
    optimal_question: ScoredQuestion | None
    discarded: list[dict[str, str]] = field(default_factory=list)
    answer_direction_test: dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "problem": self.problem[:100],
            "total_candidates": len(self.candidate_questions),
            "optimal": {
                "question": self.optimal_question.question if self.optimal_question else None,
                "type": self.optimal_question.type.value if self.optimal_question else None,
                "convergence_score": self.optimal_question.convergence_score if self.optimal_question else None,
                "URS": round(self.optimal_question.uncertainty_reduction, 2) if self.optimal_question else None,
                "SVS": round(self.optimal_question.structural_value, 2) if self.optimal_question else None,
                "DRI": round(self.optimal_question.dispersion_risk_index, 2) if self.optimal_question else None,
                "CCI": round(self.optimal_question.cognitive_cost_index, 2) if self.optimal_question else None,
                "rationale": self.optimal_question.rationale if self.optimal_question else None,
            } if self.optimal_question else None,
            "discarded": self.discarded,
            "answer_direction_passed": self.answer_direction_test.get("passed", False),
            "timestamp": self.timestamp,
        }


# ═══════════════════════════════════════════════════════════════════════
# VECTORIZER
# ═══════════════════════════════════════════════════════════════════════

class QuestionVectorizer:
    """Vetorizador e selecionador de perguntas ótimas (OQS Etapa 4-7).

    Métricas:
        URS (Uncertainty Reduction Score): 0-10
        SVS (Structural Value Score): 0-10
        DRI (Dispersion Risk Index): 0-10 (menor é melhor)
        CCI (Cognitive Cost Index): 0-10 (menor é melhor)
        CS  (Convergence Score): URS + SVS - DRI - CCI

    Seleção:
        Q* = argmax(CS)
    """

    # Pesos para o cálculo do vetor
    TYPE_WEIGHTS: dict[QuestionType, dict[str, float]] = {
        QuestionType.DEFINIÇÃO: {"direction": 8.0, "depth": 7.0, "reduction": 8.0, "dispersion": 3.0},
        QuestionType.CAUSALIDADE: {"direction": 9.0, "depth": 9.0, "reduction": 9.0, "dispersion": 4.0},
        QuestionType.COMPARAÇÃO: {"direction": 7.0, "depth": 6.0, "reduction": 7.0, "dispersion": 5.0},
        QuestionType.VALIDAÇÃO: {"direction": 8.0, "depth": 8.0, "reduction": 9.0, "dispersion": 2.0},
        QuestionType.FALSIFICAÇÃO: {"direction": 9.0, "depth": 9.0, "reduction": 9.0, "dispersion": 3.0},
        QuestionType.OPERACIONALIZAÇÃO: {"direction": 9.0, "depth": 5.0, "reduction": 7.0, "dispersion": 2.0},
        QuestionType.MÉTRICA: {"direction": 8.0, "depth": 6.0, "reduction": 8.0, "dispersion": 2.0},
        QuestionType.IMPACTO: {"direction": 6.0, "depth": 7.0, "reduction": 7.0, "dispersion": 5.0},
        QuestionType.SEQUÊNCIA: {"direction": 7.0, "depth": 4.0, "reduction": 5.0, "dispersion": 3.0},
        QuestionType.INTEGRAÇÃO: {"direction": 6.0, "depth": 8.0, "reduction": 8.0, "dispersion": 4.0},
    }

    # Palavras que indicam profundidade
    DEPTH_INDICATORS = [
        r'\bestrutur', r'\bfundamental', r'\bessência', r'\bnúcleo',
        r'\bprincípio', r'\bteoria', r'\bparadigma', r'\bontologia',
        r'\bepistemologia', r'\bmecanismo', r'\bcausa\b', r'\borigem\b',
    ]

    # Palavras que indicam escopo amplo
    SCOPE_INDICATORS = [
        r'\btudo\b', r'\bsempre\b', r'\btodos\b', r'\bqualquer\b',
        r'\buniversal\b', r'\bgeral\b', r'\bglobal\b', r'\bsistema\b',
        r'\becossistema\b', r'\btotalidade\b',
    ]

    # Palavras que indicam risco de dispersão
    DISPERSION_INDICATORS = [
        r'\boutro\b', r'\btambém\b', r'\balém\b', r'\badicionalmente\b',
        r'\bvári[oa]s\b', r'\bmúltipl[oa]s\b', r'\bdivers[oa]s\b',
    ]

    # Palavras que indicam alto custo cognitivo
    COST_INDICATORS = [
        r'\bcomplex[oai]\b', r'\bdifícil\b', r'\bprofund[oai]\b',
        r'\b extens[oa]\b', r'\b long[oa]\b', r'\bdemorad[oa]\b',
        r'\bmuitos\b', r'\bmuitas\b',
    ]

    def __init__(self, use_answer_test: bool = True):
        self.use_answer_test = use_answer_test

    def analyze(
        self,
        problem: str,
        candidate_questions: list[str],
    ) -> QuestionAnalysisResult:
        """Executa pipeline completo de análise e seleção.

        Args:
            problem: O problema ou contexto
            candidate_questions: Lista de perguntas candidatas

        Returns:
            QuestionAnalysisResult com pergunta ótima selecionada
        """
        if not candidate_questions:
            raise ValueError("Pelo menos uma pergunta candidata é necessária")

        scored: list[ScoredQuestion] = []
        discarded: list[dict[str, str]] = []

        for question in candidate_questions:
            # Classificar tipo
            qtype = QuestionType.classify(question)

            # Vetorizar
            vector = self._vectorize(question, qtype)

            # Calcular métricas
            urs = self._calc_uncertainty_reduction(vector)
            svs = self._calc_structural_value(vector)
            dri = self._calc_dispersion_risk(vector)
            cci = self._calc_cognitive_cost(vector)
            cs = urs + svs - dri - cci

            # Rationale
            rationale = self._generate_rationale(qtype, vector, cs)

            scored.append(ScoredQuestion(
                question=question,
                type=qtype,
                vector=vector,
                uncertainty_reduction=urs,
                structural_value=svs,
                dispersion_risk_index=dri,
                cognitive_cost_index=cci,
                convergence_score=cs,
                rationale=rationale,
            ))

        # Answer Direction Test (Etapa 8)
        answer_test = self._answer_direction_test(scored, problem)

        # Filtrar perguntas que não passam no answer test
        if self.use_answer_test:
            passing = [s for s in scored if s.question in answer_test.get("passing", [])]
            failing = [s for s in scored if s.question in answer_test.get("failing", [])]
            for s in failing:
                discarded.append({
                    "question": s.question,
                    "reason": "Answer Direction Test: resposta provável não produz avanço",
                    "cs": str(round(s.convergence_score, 1)),
                })
        else:
            passing = scored

        # Selecionar ótima (argmax CS)
        optimal = max(passing, key=lambda s: s.convergence_score) if passing else None

        # Descartar as demais perguntas com CS menor
        for s in passing:
            if s.question != (optimal.question if optimal else None):
                discarded.append({
                    "question": s.question,
                    "reason": f"CS={s.convergence_score:.1f} inferior ao da pergunta ótima (CS={optimal.convergence_score:.1f})" if optimal else "Sem pergunta ótima",
                    "cs": str(round(s.convergence_score, 1)),
                })

        return QuestionAnalysisResult(
            problem=problem[:500],
            candidate_questions=scored,
            optimal_question=optimal,
            discarded=discarded,
            answer_direction_test=answer_test,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def _vectorize(
        self, question: str, qtype: QuestionType
    ) -> QuestionVector:
        """Gera vetor de 6 dimensões para a pergunta."""
        base = self.TYPE_WEIGHTS.get(qtype, self.TYPE_WEIGHTS[QuestionType.DEFINIÇÃO])

        # Direction: base + comprimento da pergunta (curta = mais direcional)
        direction = base["direction"]
        word_count = len(question.split())
        if word_count <= 5:
            direction = min(10, direction + 1.5)
        elif word_count >= 20:
            direction = max(1, direction - 1.0)

        # Depth: base + indicadores de profundidade
        depth = base["depth"]
        for pattern in self.DEPTH_INDICATORS:
            if re.search(pattern, question, re.IGNORECASE):
                depth = min(10, depth + 1.5)

        # Scope: base + indicadores de escopo
        scope = 5.0
        for pattern in self.SCOPE_INDICATORS:
            if re.search(pattern, question, re.IGNORECASE):
                scope = min(10, scope + 2.0)

        # Reduction power: base pela profundidade + tipo
        reduction_power = base["reduction"]
        # Quanto mais específica, maior redução
        if question.endswith("?"):
            reduction_power = min(10, reduction_power + 0.5)

        # Dispersion risk: base + indicadores
        dispersion_risk = base["dispersion"]
        for pattern in self.DISPERSION_INDICATORS:
            if re.search(pattern, question, re.IGNORECASE):
                dispersion_risk = min(10, dispersion_risk + 1.0)
        # Perguntas muito longas têm mais dispersão
        if word_count >= 25:
            dispersion_risk = min(10, dispersion_risk + 1.5)

        # Cognitive cost: base + complexidade lexical
        cognitive_cost = 3.0
        for pattern in self.COST_INDICATORS:
            if re.search(pattern, question, re.IGNORECASE):
                cognitive_cost = min(10, cognitive_cost + 1.0)
        # Custo maior para perguntas muito longas
        if word_count >= 20:
            cognitive_cost = min(10, cognitive_cost + 0.5)

        return QuestionVector(
            direction=round(min(10, direction), 1),
            scope=round(min(10, scope), 1),
            depth=round(min(10, depth), 1),
            reduction_power=round(min(10, reduction_power), 1),
            dispersion_risk=round(min(10, dispersion_risk), 1),
            cognitive_cost=round(min(10, cognitive_cost), 1),
        )

    def _calc_uncertainty_reduction(self, v: QuestionVector) -> float:
        """URS = ReductionPower * (1 - Dispersion/10) * Direction/10"""
        raw = v.reduction_power * (1 - v.dispersion_risk / 10) * (v.direction / 10)
        return round(min(10, raw * 2), 2)

    def _calc_structural_value(self, v: QuestionVector) -> float:
        """SVS = (Depth * Scope) / 10"""
        raw = (v.depth * v.scope) / 10
        return round(min(10, raw), 2)

    def _calc_dispersion_risk(self, v: QuestionVector) -> float:
        """DRI = DispersionRisk (diretamente, menor é melhor)"""
        return round(v.dispersion_risk, 2)

    def _calc_cognitive_cost(self, v: QuestionVector) -> float:
        """CCI = CognitiveCost (diretamente, menor é melhor)"""
        return round(v.cognitive_cost, 2)

    def _generate_rationale(
        self, qtype: QuestionType, vector: QuestionVector, cs: float
    ) -> str:
        """Gera justificativa para a pergunta."""
        parts = []

        if qtype == QuestionType.DEFINIÇÃO:
            parts.append("Pergunta de definição — busca clarear o conceito central")
        elif qtype == QuestionType.CAUSALIDADE:
            parts.append("Pergunta causal — busca a origem do fenômeno")
        elif qtype == QuestionType.VALIDAÇÃO:
            parts.append("Pergunta de validação — testa uma hipótese")
        elif qtype == QuestionType.FALSIFICAÇÃO:
            parts.append("Pergunta de falsificação — busca contraexemplos")
        elif qtype == QuestionType.OPERACIONALIZAÇÃO:
            parts.append("Pergunta operacional — busca implementação prática")
        elif qtype == QuestionType.MÉTRICA:
            parts.append("Pergunta de métrica — busca mensuração")
        elif qtype == QuestionType.INTEGRAÇÃO:
            parts.append("Pergunta integrativa — busca síntese")

        if vector.reduction_power >= 7:
            parts.append(f"Alto poder de redução de incerteza ({vector.reduction_power:.0f}/10)")
        if vector.depth >= 7:
            parts.append(f"Alta profundidade investigativa ({vector.depth:.0f}/10)")
        if vector.dispersion_risk <= 3:
            parts.append("Baixo risco de dispersão")

        parts.append(f"CS = {cs:.1f}")

        return ". ".join(parts)

    def _answer_direction_test(
        self, scored: list[ScoredQuestion], problem: str
    ) -> dict[str, Any]:
        """Etapa 8: Testa se a resposta provável da pergunta ajuda a avançar.

        Critérios heurísticos:
        1. Perguntas com CS > 0 passam
        2. Perguntas de definição sobre o núcleo do problema passam
        3. Perguntas com DRI > 7 falham (dispersão excessiva)
        """
        passing = []
        failing = []

        # Extrair palavras-chave do problema
        problem_keywords = set(
            w.lower().strip('?.,!;:') for w in problem.split()
            if len(w) > 3
        )

        for sq in scored:
            # Critério 1: CS positivo
            if sq.convergence_score <= 0:
                failing.append(sq.question)
                continue

            # Critério 2: DRI baixo
            if sq.dispersion_risk_index > 7:
                failing.append(sq.question)
                continue

            # Critério 3: CCI baixo a moderado
            if sq.cognitive_cost_index > 8:
                failing.append(sq.question)
                continue

            # Critério 4: Perguntas muito genéricas falham
            question_words = set(
                w.lower().strip('?.,!;:') for w in sq.question.split()
                if len(w) > 3
            )
            overlap = len(question_words & problem_keywords)
            if overlap == 0 and sq.convergence_score < 3:
                failing.append(sq.question)
                continue

            passing.append(sq.question)

        return {
            "passed": len(passing) > 0,
            "passing": passing,
            "failing": failing,
            "rationale": f"{len(passing)}/{len(scored)} perguntas passaram no teste de direção",
        }


# ═══════════════════════════════════════════════════════════════════════
# CONVERGENCE SCORE — Métrica exportável
# ═══════════════════════════════════════════════════════════════════════

def calculate_convergence_score(
    urs: float, svs: float, dri: float, cci: float
) -> float:
    """Calcula o Convergence Score (CS) para uma pergunta.

    Fórmula:
        CS = URS + SVS - DRI - CCI

    Onde:
        URS: Uncertainty Reduction Score (0-10)
        SVS: Structural Value Score (0-10)
        DRI: Dispersion Risk Index (0-10, menor melhor)
        CCI: Cognitive Cost Index (0-10, menor melhor)

    Interpretação:
        CS >= 10: Pergunta forte
        CS >= 5: Pergunta útil
        CS >= 0: Pergunta moderada
        CS < 0: Pergunta dispersiva ou fraca

    Returns:
        Convergence Score (intervalo teórico: -20 a +20)
    """
    cs = urs + svs - dri - cci
    return round(cs, 2)


def interpret_convergence_score(cs: float) -> str:
    """Interpreta o Convergence Score qualitativamente."""
    if cs >= 15:
        return "Ótima — pergunta com altíssimo poder de convergência"
    elif cs >= 10:
        return "Forte — pergunta com bom poder de convergência"
    elif cs >= 5:
        return "Útil — pergunta que reduz incerteza moderadamente"
    elif cs >= 0:
        return "Moderada — pergunta com valor limitado"
    elif cs >= -5:
        return "Fraca — pergunta que pode gerar mais ruído que clareza"
    else:
        return "Dispersiva — pergunta que amplia o espaço de incerteza"


# ═══════════════════════════════════════════════════════════════════════
# QUICK TEST
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    problem = (
        "Tenho uma ferramenta que reduz texto grande em representação vetorial. "
        "Isso é só resumo ou existe uma técnica nova?"
    )

    candidates = [
        "O que é resumo?",
        "Como reduzir tokens?",
        "Qual é a diferença entre resumir e preservar estrutura?",
        "Existe equivalência estrutural entre texto bruto e representação vetorial?",
    ]

    qv = QuestionVectorizer()
    result = qv.analyze(problem, candidates)

    print("=== CANDIDATAS ===")
    for sq in result.candidate_questions:
        print(f"\n  Pergunta: {sq.question}")
        print(f"  Tipo: {sq.type.value}")
        print(f"  Vetor: {sq.vector.to_dict()}")
        print(f"  URS={sq.uncertainty_reduction} SVS={sq.structural_value} DRI={sq.dispersion_risk_index} CCI={sq.cognitive_cost_index}")
        print(f"  CS={sq.convergence_score}")
        print(f"  Rationale: {sq.rationale}")

    print(f"\n=== ÓTIMA ===")
    if result.optimal_question:
        print(f"  Pergunta: {result.optimal_question.question}")
        print(f"  Tipo: {result.optimal_question.type.value}")
        print(f"  CS: {result.optimal_question.convergence_score}")
        print(f"  Justificativa: {result.optimal_question.rationale}")

    print(f"\n=== DESCARTADAS ===")
    for d in result.discarded:
        print(f"  - {d['question'][:50]}... (CS={d['cs']}, motivo: {d['reason'][:40]})")

    print(f"\n=== MÉTRICA ISOLADA ===")
    print(f"CS(URS=8, SVS=7, DRI=3, CCI=2) = {calculate_convergence_score(8, 7, 3, 2)}")
    print(f"Interpretação: {interpret_convergence_score(calculate_convergence_score(8, 7, 3, 2))}")
