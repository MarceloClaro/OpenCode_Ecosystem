# -*- coding: utf-8 -*-
"""
RUMI Causal Discovery Pipeline — R28
Inspirado em RUMI (subhansh-dev/rumi): 21 fases de descoberta,
raciocinio causal (Pearl), torneio de hipoteses e revisao adversarial.

Implementa pipeline simplificado:
  1. Geracao de hipoteses causais
  2. Teste de hipoteses (correlacao -> causalidade)
  3. Torneio de hipoteses (selecao da melhor)
  4. Revisao adversarial
"""

import uuid
import json
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime


class HypothesisStatus(Enum):
    PROPOSED = "proposed"           # Proposta
    TESTING = "testing"             # Em teste
    CONFIRMED = "confirmed"         # Confirmada
    REFUTED = "refuted"             # Refutada
    INCONCLUSIVE = "inconclusive"   # Inconclusiva


@dataclass
class CausalHypothesis:
    """Hipotese causal unica"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    cause: str = ""
    effect: str = ""
    mechanism: str = ""
    confidence: float = 0.5
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    evidence: List[str] = field(default_factory=list)
    score: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "cause": self.cause,
            "effect": self.effect,
            "mechanism": self.mechanism,
            "confidence": round(self.confidence, 4),
            "status": self.status.value,
            "evidence_count": len(self.evidence),
            "score": round(self.score, 4),
            "created_at": self.created_at,
        }


@dataclass
class CausalGraph:
    """Grafo causal simples (DAG)"""
    nodes: List[str] = field(default_factory=list)
    edges: List[Tuple[str, str, float]] = field(default_factory=list)  # (cause, effect, weight)

    def add_edge(self, cause: str, effect: str, weight: float = 1.0) -> None:
        if cause not in self.nodes:
            self.nodes.append(cause)
        if effect not in self.nodes:
            self.nodes.append(effect)
        self.edges.append((cause, effect, weight))

    def to_dict(self) -> Dict:
        return {
            "nodes": self.nodes,
            "edges": [
                {"cause": c, "effect": e, "weight": round(w, 4)}
                for c, e, w in self.edges
            ],
        }


class CausalGenerator:
    """
    Gerador de hipoteses causais.

    Usa heuristicas para gerar hipoteses a partir de variaveis observadas.
    """

    @staticmethod
    def generate_from_variables(variables: List[str],
                                 observed_correlations: Optional[Dict[str, float]] = None) -> List[CausalHypothesis]:
        """Gera hipoteses causais a partir de lista de variaveis"""
        hypotheses = []
        correlations = observed_correlations or {}

        for i, cause in enumerate(variables):
            for j, effect in enumerate(variables):
                if i == j:
                    continue

                # Score baseado em correlacao (se disponivel)
                pair_key = f"{cause}->{effect}"
                corr = correlations.get(pair_key, 0.3)

                hypothesis = CausalHypothesis(
                    cause=cause,
                    effect=effect,
                    mechanism=f"{cause} influencia {effect}",
                    confidence=min(0.9, abs(corr)),
                    status=HypothesisStatus.PROPOSED,
                    score=abs(corr),
                )
                hypotheses.append(hypothesis)

        return hypotheses

    @staticmethod
    def generate_with_mechanism(cause: str, effect: str,
                                 mechanism: str, confidence: float = 0.7) -> CausalHypothesis:
        """Gera hipotese causal com mecanismo explicito"""
        return CausalHypothesis(
            cause=cause,
            effect=effect,
            mechanism=mechanism,
            confidence=min(1.0, max(0.1, confidence)),
            score=confidence,
        )


class CausalTester:
    """
    Testador de hipoteses causais.

    Simula testes: correlacao, direcao temporal, consistencia logica.
    """

    @staticmethod
    def test_hypothesis(hypothesis: CausalHypothesis,
                        test_data: Optional[Dict] = None) -> CausalHypothesis:
        """Testa uma hipotese causal"""
        data = test_data or {}

        # Simular teste de correlacao
        simulated_correlation = data.get(
            f"{hypothesis.cause}->{hypothesis.effect}",
            hypothesis.confidence * 0.8 + 0.1,
        )

        # Simular teste de direcao temporal
        temporal_plausibility = data.get(
            f"temporal:{hypothesis.cause}>{hypothesis.effect}",
            0.7,
        )

        # Simular consistencia com conhecimento existente
        consistency = data.get("consistency", 0.8)

        # Pontuacao composta
        test_score = (
            simulated_correlation * 0.4 +
            temporal_plausibility * 0.35 +
            consistency * 0.25
        )

        hypothesis.score = round(test_score, 4)

        if test_score >= 0.7:
            hypothesis.status = HypothesisStatus.CONFIRMED
            hypothesis.evidence.append(
                f"Teste confirmatorio: correlacao={simulated_correlation:.2f}, "
                f"temporal={temporal_plausibility:.2f}"
            )
        elif test_score >= 0.4:
            hypothesis.status = HypothesisStatus.INCONCLUSIVE
        else:
            hypothesis.status = HypothesisStatus.REFUTED

        hypothesis.confidence = round(test_score, 4)
        return hypothesis

    @staticmethod
    def tournament(proposals: List[CausalHypothesis],
                   top_k: int = 3) -> List[CausalHypothesis]:
        """
        Torneio de hipoteses: seleciona as melhores.

        Usa score composto: confianca * status_bonus.
        """
        scored = []
        for h in proposals:
            status_bonus = {
                HypothesisStatus.CONFIRMED: 1.0,
                HypothesisStatus.INCONCLUSIVE: 0.5,
                HypothesisStatus.REFUTED: 0.1,
                HypothesisStatus.PROPOSED: 0.3,
                HypothesisStatus.TESTING: 0.4,
            }
            final_score = h.score * status_bonus.get(h.status, 0.3)
            scored.append((final_score, h))

        scored.sort(key=lambda x: -x[0])
        return [h for _, h in scored[:top_k]]


class AdversarialReviewer:
    """
    Revisor adversarial que busca refutar hipoteses.

    Simula um "advogado do diabo" cientifico.
    """

    @staticmethod
    def review(hypothesis: CausalHypothesis) -> Dict:
        """Revisa uma hipotese adversarialmente"""
        issues = []

        # Verificar causalidade reversa
        if hypothesis.confidence < 0.5:
            issues.append(f"Baixa confianca ({hypothesis.confidence:.2f}): "
                          f"causalidade reversa nao descartada")

        # Verificar confundidores
        if len(hypothesis.evidence) < 2:
            issues.append("Evidencia insuficiente: possivel confundidor nao controlado")

        # Verificacao de mecanismo
        if not hypothesis.mechanism or len(hypothesis.mechanism) < 10:
            issues.append("Mecanismo causal nao especificado: explicacao superficial")

        # Verificacao de reproducao
        if hypothesis.score < 0.6:
            issues.append(f"Score baixo ({hypothesis.score:.2f}): "
                          f"resultado pode nao ser reproduzivel")

        severity = "low"
        if len(issues) >= 3:
            severity = "high"
        elif len(issues) >= 1:
            severity = "medium"

        return {
            "hypothesis_id": hypothesis.id,
            "cause": hypothesis.cause,
            "effect": hypothesis.effect,
            "issues": issues,
            "total_issues": len(issues),
            "severity": severity,
            "passed": len(issues) == 0,
        }


class RUMIEngine:
    """
    Motor principal RUMI Causal Discovery.

    Pipeline:
      1. Generate: Gerar hipoteses causais de variaveis
      2. Test: Testar cada hipotese
      3. Tournament: Selecionar melhores
      4. Adversarial: Revisar adversarialmente
      5. Output: Grafo causal final
    """

    def __init__(self):
        self.generator = CausalGenerator()
        self.tester = CausalTester()
        self.reviewer = AdversarialReviewer()

    def discover(self, variables: List[str],
                 test_data: Optional[Dict] = None,
                 top_k: int = 5) -> Dict:
        """
        Pipeline completo de descoberta causal.

        Args:
            variables: Lista de variaveis observadas
            test_data: Dados de teste (correlacoes, etc.)
            top_k: Numero de hipoteses no resultado final

        Returns:
            Dict com hipoteses, grafo causal e revisoes
        """
        # 1. Generate
        hypotheses = self.generator.generate_from_variables(variables)
        initial_count = len(hypotheses)

        # 2. Test
        tested = []
        for h in hypotheses:
            tested.append(self.tester.test_hypothesis(h, test_data))

        # 3. Tournament
        winners = self.tester.tournament(tested, top_k=top_k)

        # 4. Adversarial Review
        reviews = []
        for h in winners:
            reviews.append(self.reviewer.review(h))

        # 5. Build causal graph
        graph = CausalGraph()
        for h in winners:
            if h.status == HypothesisStatus.CONFIRMED:
                graph.add_edge(h.cause, h.effect, h.confidence)

        passed_review = sum(1 for r in reviews if r["passed"])

        return {
            "total_hypotheses_generated": initial_count,
            "total_tested": len(tested),
            "confirmed": len([h for h in tested if h.status == HypothesisStatus.CONFIRMED]),
            "refuted": len([h for h in tested if h.status == HypothesisStatus.REFUTED]),
            "top_hypotheses": [h.to_dict() for h in winners],
            "adversarial_reviews": reviews,
            "adversarial_pass_rate": round(passed_review / max(1, len(reviews)), 4),
            "causal_graph": graph.to_dict(),
            "pipeline_steps": ["generate", "test", "tournament", "adversarial_review", "graph_build"],
        }

    def analyze_causal_claim(self, cause: str, effect: str,
                              mechanism: str, confidence: float = 0.7) -> Dict:
        """
        Analisa uma reivindicacao causal especifica.

        Gera hipotese, testa, revisa adversarialmente e retorna resultado.
        """
        hypothesis = self.generator.generate_with_mechanism(
            cause, effect, mechanism, confidence
        )

        tested = self.tester.test_hypothesis(hypothesis)
        review = self.reviewer.review(tested)

        return {
            "hypothesis": tested.to_dict(),
            "status": tested.status.value,
            "review": review,
            "passed_adversarial": review["passed"],
            "recommendation": (
                "Aceitar" if review["passed"] and tested.status == HypothesisStatus.CONFIRMED
                else "Rejeitar" if tested.status == HypothesisStatus.REFUTED
                else "Requer mais evidencias"
            ),
        }
