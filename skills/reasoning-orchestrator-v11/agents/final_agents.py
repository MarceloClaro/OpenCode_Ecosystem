# =====================================================================
# FINAL REASONING AGENTS — Completing the 18-agent set
# R09 (Quantificational), R12 (Mathematical Induction),
# R23 (Reductio ad Absurdum), R34 (Restrictive Generalization)
# =====================================================================
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from framework import ReasoningAgent, ReasoningResult

# =====================================================================
# R09 — QuantificationalAgent (∀, ∃ manipulation)
# =====================================================================
class QuantificationalAgent(ReasoningAgent):
    """
    R09: Manipulates universal (∀) and existential (∃) quantifiers.
    
    In IMO 2024 P2: "Choose n ≡ -1 (mod φ(K))" via Euler's theorem —
    selecting a specific n that satisfies a property for ALL such n.
    
    Key operations:
    - ∀ elimination: if ∀x P(x), then P(a) for any specific a
    - ∃ introduction: if P(a), then ∃x P(x)
    - Choosing witnesses: pick n satisfying multiple congruences
    """
    
    def __init__(self):
        super().__init__("quantificational-agent", "R09", "II")
    
    def get_dependencies(self):
        return ["notation-agent"]
    
    def reason(self, context: dict) -> ReasoningResult:
        statements = context.get("quantified_statements", [])
        
        # Analyze quantifier structure
        universal = [s for s in statements if "for all" in str(s).lower() or "∀" in str(s)]
        existential = [s for s in statements if "exists" in str(s).lower() or "∃" in str(s)]
        
        if universal or existential:
            conclusion = f"Quantificadores: {len(universal)} universais, {len(existential)} existenciais."
            confidence = 0.70
        else:
            conclusion = "Nenhum quantificador explicito detectado."
            confidence = 0.20
        
        return ReasoningResult(
            agent_id=self.agent_id, reasoning_type=self.reasoning_type,
            category=self.category, conclusion=conclusion, confidence=confidence,
            evidence=[{"universal": len(universal), "existential": len(existential)}]
        )


# =====================================================================
# R12 — InductionAgent (Mathematical Induction)
# =====================================================================
class InductionAgent(ReasoningAgent):
    """
    R12: Mathematical induction — base case + inductive step.
    
    In IMO 2024 P1: "We prove tnεu = 0 for all n by strong induction"
    Base: tεu = 0. Step: assume for 1..n-1, prove for n.
    
    In IMO 2024 P3: "pn is nondecreasing and bounded ⇒ eventually constant"
    """
    
    def __init__(self):
        super().__init__("induction-agent", "R12", "III")
    
    def get_dependencies(self):
        return ["basecase-agent", "deductivechain-agent"]
    
    def reason(self, context: dict) -> ReasoningResult:
        induction_claims = context.get("induction_claims", [])
        
        valid_inductions = []
        for claim in induction_claims:
            base = claim.get("base_case")
            step = claim.get("inductive_step")
            if base and step:
                valid_inductions.append({
                    "statement": str(claim.get("property", ""))[:80],
                    "base_verified": base,
                    "step_verified": step
                })
        
        if valid_inductions:
            conclusion = f"{len(valid_inductions)} inducoes verificadas."
            confidence = 0.85 if all(v["step_verified"] for v in valid_inductions) else 0.40
        else:
            conclusion = "Nenhuma inducao detectada. Considere reducao estrutural (R13)."
            confidence = 0.15
        
        return ReasoningResult(
            agent_id=self.agent_id, reasoning_type=self.reasoning_type,
            category=self.category, conclusion=conclusion, confidence=confidence,
            evidence=valid_inductions
        )


# =====================================================================
# R23 — ReductioAgent (Reductio ad Absurdum)
# =====================================================================
class ReductioAgent(ReasoningAgent):
    """
    R23: Reductio ad absurdum — assume negation, derive contradiction.
    
    In IMO 2024 P2: "If (a,b) ≠ (1,1), then ab+1 divisible by 4 ⇒ ν₂(g)≥2,
    but Lemma says ν₂(g)≤1. Contradiction."
    
    In IMO 2024 P6: "If g(x)>0 and g(y)<0, then gpSq is infinite,
    but it should be finite. Contradiction."
    """
    
    def __init__(self):
        super().__init__("reductio-agent", "R23", "V")
    
    def get_dependencies(self):
        return ["contradiction-agent"]
    
    def reason(self, context: dict) -> ReasoningResult:
        assumption = context.get("negation_assumption", "")
        derived = context.get("derived_consequences", [])
        
        contradictions = []
        for consequence in derived:
            if self._contradicts(consequence, context):
                contradictions.append({
                    "assumption": str(assumption)[:80],
                    "consequence": str(consequence)[:80],
                    "contradiction_with": "established fact or lemma"
                })
        
        if contradictions:
            conclusion = f"Reductio valida: {len(contradictions)} contradicoes derivadas da negacao."
            confidence = 0.88
        elif assumption:
            conclusion = "Reductio iniciada mas sem contradicao derivada ainda."
            confidence = 0.25
        else:
            conclusion = "Nenhuma reductio em andamento."
            confidence = 0.10
        
        return ReasoningResult(
            agent_id=self.agent_id, reasoning_type=self.reasoning_type,
            category=self.category, conclusion=conclusion, confidence=confidence,
            evidence=contradictions
        )
    
    def _contradicts(self, consequence, context):
        known_facts = context.get("known_facts", [])
        for fact in known_facts:
            if str(consequence).lower() in str(fact).lower():
                return True
        return False


# =====================================================================
# R34 — GeneralizationAgent (Restrictive Generalization)
# =====================================================================
class GeneralizationAgent(ReasoningAgent):
    """
    R34: Determines whether a solution generalizes or is specific to the base case.
    
    In IMO 2024 P4: "The constraint AB<AC<BC was added to reduce case-sensitivity.
    Without it, there would be two more possible configurations."
    — Recognizing that the proof covers only a restricted case.
    """
    
    def __init__(self):
        super().__init__("generalization-agent", "R34", "VII")
    
    def get_dependencies(self):
        return ["basecase-agent", "abstraction-agent"]
    
    def reason(self, context: dict) -> ReasoningResult:
        solution = context.get("solution", {})
        constraints = context.get("constraints", {})
        
        analysis = self._analyze_generalization(solution, constraints)
        
        if analysis["generalizes"]:
            conclusion = f"Solucao generaliza para: {analysis['scope']}"
            confidence = 0.80
        elif analysis["restricted"]:
            conclusion = f"Solucao RESTRITA a: {analysis['scope']}. Nao generaliza alem."
            confidence = 0.75
        else:
            conclusion = "Escopo de generalizacao indeterminado."
            confidence = 0.20
        
        return ReasoningResult(
            agent_id=self.agent_id, reasoning_type=self.reasoning_type,
            category=self.category, conclusion=conclusion, confidence=confidence,
            evidence=[analysis]
        )
    
    def _analyze_generalization(self, solution, constraints):
        desc = str(solution).lower()
        
        # Heuristics for generalization scope
        has_parameter = "n" in desc or "for all" in desc
        has_restriction = "without loss" in desc or "wlog" in desc
        
        if has_parameter and not has_restriction:
            return {"generalizes": True, "restricted": False, "scope": "todos os valores do parametro"}
        elif has_restriction:
            return {"generalizes": False, "restricted": True, "scope": "caso restrito (WLOG)"}
        else:
            return {"generalizes": False, "restricted": False, "scope": "indeterminado"}
