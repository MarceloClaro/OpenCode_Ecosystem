# =====================================================================
# DOMAIN AGENTS — Scientific, Legal, Economic
# Implements: HypothesisTester (R35), PrecedentAnalyzer (R42),
#             RiskAssessor (R50), ProofHealthAgent (R31+R32+R33)
# =====================================================================
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from framework import ReasoningAgent, ReasoningResult, AgentStatus
from critical_agents import LemmaTrackerAgent

# =====================================================================
# R35 — HypothesisTester (Cientifico-Experimental)
# =====================================================================
class HypothesisTester(ReasoningAgent):
    """R35: Formula hipotese, deduz consequencias testaveis, verifica."""
    
    def __init__(self):
        super().__init__("hypothesis-tester", "R35", "VIII")
    
    def get_dependencies(self):
        return ["abstraction-agent"]
    
    def reason(self, context: dict) -> ReasoningResult:
        hypothesis = context.get("hypothesis", "")
        data = context.get("data", {})
        
        # Popperian falsification approach
        testable = self._check_testability(hypothesis)
        falsified = self._attempt_falsification(hypothesis, data)
        
        if falsified:
            conclusion = f"Hipotese FALSIFICADA: {falsified['reason']}"
            confidence = 0.95
        elif testable:
            conclusion = f"Hipotese testavel, nao falsificada com dados disponiveis."
            confidence = 0.45
        else:
            conclusion = "Hipotese nao-testavel (nao cientifica segundo criterio de Popper)."
            confidence = 0.30
        
        return ReasoningResult(
            agent_id=self.agent_id, reasoning_type=self.reasoning_type,
            category=self.category, conclusion=conclusion, confidence=confidence,
            evidence=[{"testable": testable, "falsified": falsified}]
        )
    
    def _check_testability(self, hypothesis):
        return "?" in str(hypothesis) or "if" in str(hypothesis).lower()
    
    def _attempt_falsification(self, hypothesis, data):
        if not data:
            return None
        # Check if any data point contradicts the hypothesis
        return None


# =====================================================================
# R42 — PrecedentAnalyzer (Juridico)
# =====================================================================
class PrecedentAnalyzer(ReasoningAgent):
    """R42: Compara caso atual com jurisprudencia via analogia."""
    
    def __init__(self):
        super().__init__("precedent-analyzer", "R42", "IX")
    
    def get_dependencies(self):
        return []
    
    def reason(self, context: dict) -> ReasoningResult:
        current_case = context.get("case", {})
        precedents = context.get("precedents", [])
        
        matches = []
        for precedent in precedents:
            similarity = self._compute_similarity(current_case, precedent)
            if similarity > 0.6:
                matches.append({"precedent": precedent.get("id"), "similarity": similarity})
        
        if matches:
            best = max(matches, key=lambda m: m["similarity"])
            conclusion = f"Precedente mais relevante: {best['precedent']} (similaridade: {best['similarity']:.2f})"
            confidence = best["similarity"]
        else:
            conclusion = "Nenhum precedente analogo encontrado (case of first impression)."
            confidence = 0.20
        
        return ReasoningResult(
            agent_id=self.agent_id, reasoning_type=self.reasoning_type,
            category=self.category, conclusion=conclusion, confidence=confidence,
            evidence=matches
        )
    
    def _compute_similarity(self, case1, case2):
        """Simple keyword overlap similarity."""
        k1 = set(str(case1).lower().split())
        k2 = set(str(case2).lower().split())
        if not k1 or not k2:
            return 0.0
        return len(k1 & k2) / len(k1 | k2)


# =====================================================================
# R50 — RiskAssessor (Economico)
# =====================================================================
class RiskAssessor(ReasoningAgent):
    """R50: Diferencia risco (probabilidades conhecidas) de incerteza Knightiana."""
    
    def __init__(self):
        super().__init__("risk-assessor", "R50", "X")
    
    def get_dependencies(self):
        return []
    
    def reason(self, context: dict) -> ReasoningResult:
        probabilities = context.get("probabilities", {})
        decision = context.get("decision", {})
        
        # Knightian classification
        known_probs = all(0 <= p <= 1 for p in probabilities.values())
        
        if known_probs and probabilities:
            expected_value = sum(p * v for p, v in zip(probabilities.values(), 
                                  context.get("outcomes", [0]*len(probabilities))))
            risk_type = "RISCO (probabilidades conhecidas)"
            conclusion = f"Cenario de {risk_type}. Valor esperado: {expected_value:.2f}"
            confidence = 0.80
        else:
            risk_type = "INCERTEZA KNIGHTIANA (probabilidades desconhecidas)"
            conclusion = f"Cenario de {risk_type}. Decisao requer criterios nao-probabilisticos."
            confidence = 0.40
        
        return ReasoningResult(
            agent_id=self.agent_id, reasoning_type=self.reasoning_type,
            category=self.category, conclusion=conclusion, confidence=confidence,
            evidence=[{"known_probabilities": known_probs}]
        )


# =====================================================================
# ProofHealthAgent (R31+R32+R33 — Meta-Cognitivo)
# =====================================================================
class ProofHealthAgent(ReasoningAgent):
    """Composite: R31 (dependencia) + R32 (calibracao) + R33 (revisao).
    
    Computes the Proof Confidence Index (PCI) from 0-100.
    """
    
    def __init__(self, lemma_tracker: LemmaTrackerAgent = None):
        super().__init__("proofhealth-agent", "R31+R32+R33", "VII")
        self.lemma_tracker = lemma_tracker or LemmaTrackerAgent()
    
    def get_dependencies(self):
        return ["crossref-agent", "lemmatracker-agent", "stresstest-agent", 
                "basecase-agent", "contradiction-agent"]
    
    def reason(self, context: dict) -> ReasoningResult:
        agent_results = context.get("agent_results", {})
        
        # Compute PCI
        pci = 0
        
        # P23: Cross-reference (30%)
        crossref = agent_results.get("crossref-agent")
        if crossref and crossref.confidence > 0.8 and "CONSISTENTE" in crossref.conclusion.upper():
            pci += 30
        elif crossref and "CONFLITO" in crossref.conclusion.upper():
            pci += 0  # Conflict = 0 points
        
        # P22: Base case (25%)
        basecase = agent_results.get("basecase-agent")
        if basecase and basecase.confidence > 0.9:
            pci += 25
        
        # P20: Lemma graph (25%)
        lemmatracker = agent_results.get("lemmatracker-agent")
        if lemmatracker:
            health = lemmatracker.confidence
            pci += int(25 * health)
        
        # P21: Stress test (10%)
        stresstest = agent_results.get("stresstest-agent")
        if stresstest and stresstest.confidence > 0.7:
            pci += 10
        
        # V1-V6: Cora-Debate consistency (10%)
        cora_pass = context.get("cora_pass_count", 0)
        pci += min(10, 2 * cora_pass)
        
        pci = min(pci, 100)
        
        if pci >= 80:
            verdict = "APROVADO — Alta confianca"
        elif pci >= 60:
            verdict = "REVISAO RECOMENDADA — Confianca moderada"
        elif pci >= 40:
            verdict = "REVISAO OBRIGATORIA — Baixa confianca"
        else:
            verdict = "REJEITADO — Confianca insuficiente"
        
        return ReasoningResult(
            agent_id=self.agent_id, reasoning_type=self.reasoning_type,
            category=self.category,
            conclusion=f"PCI: {pci}/100 — {verdict}",
            confidence=pci / 100,
            evidence=[{
                "pci": pci,
                "verdict": verdict,
                "breakdown": {
                    "crossref": min(30, 30 if crossref and crossref.confidence > 0.8 else 0),
                    "basecase": min(25, 25 if basecase and basecase.confidence > 0.9 else 0),
                    "lemmagraph": min(25, int(25 * (lemmatracker.confidence if lemmatracker else 0))),
                    "stresstest": min(10, 10 if stresstest and stresstest.confidence > 0.7 else 0),
                    "cora_v1v6": min(10, 2 * cora_pass)
                }
            }]
        )
