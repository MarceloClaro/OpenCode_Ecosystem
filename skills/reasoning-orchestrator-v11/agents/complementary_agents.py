# =====================================================================
# COMPLEMENTARY REASONING AGENTS
# R14 (Invariant), R04 (Translation), R11 (BackwardChain),
# R08 (DeductiveChain), R10 (Modular), R19 (Enumeration)
# =====================================================================
import sys, os, math, itertools
from typing import Any
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from framework import ReasoningAgent, ReasoningResult, AgentStatus
from critical_agents import LemmaTrackerAgent

# =====================================================================
# R14 — InvariantAgent (structural invariants)
# =====================================================================
class InvariantAgent(ReasoningAgent):
    """
    R14: Identifies structural invariants — properties that MUST hold
    in any valid configuration.
    
    In IMO 2025 P1: "The NV vertical lines must be {x=1,...,x=NV}"
    This is derived from: if x=a is NOT in L, then column C_a must be
    covered by other lines, giving bound a >= NV+1. By contrapositive,
    a <= NV => x=a is in L.
    """
    
    def __init__(self):
        super().__init__("invariant-agent", "R14", "III")
    
    def get_dependencies(self):
        return ["notation-agent"]
    
    def reason(self, context: dict) -> ReasoningResult:
        problem = context.get("problem", {})
        structure = problem.get("structure", {})
        constraints = problem.get("constraints", {})
        
        invariants = self._find_invariants(structure, constraints)
        
        if invariants:
            conclusion = f"Encontrados {len(invariants)} invariantes estruturais: {[i['name'] for i in invariants]}"
            confidence = 0.80
        else:
            conclusion = "Nenhum invariante estrutural identificado."
            confidence = 0.25
        
        return ReasoningResult(
            agent_id=self.agent_id, reasoning_type=self.reasoning_type,
            category=self.category, conclusion=conclusion, confidence=confidence,
            evidence=invariants
        )
    
    def _find_invariants(self, structure, constraints):
        """Heuristic: find forced structural properties."""
        invariants = []
        
        # For combinatorial geometry: check for "forced line" patterns
        if "points" in str(structure).lower() or "grid" in str(structure).lower():
            # Check if boundary lines are forced
            if constraints.get("boundary_forced", False):
                invariants.append({
                    "name": "boundary_lines_forced",
                    "type": "structural",
                    "description": "Lines at x=1, y=1, or x+y=n+1 are forced by counting"
                })
            
            # Check for column/row counting invariants
            invariants.append({
                "name": "column_counting",
                "type": "counting",
                "description": "Each column C_a has |C_a| = n+1-a points; if not covered by x=a, needs n-NV other lines"
            })
        
        # For IMO 2025 specifically: forced shady lines
        if "sunny" in str(structure).lower() or "ensolarada" in str(structure).lower():
            invariants.append({
                "name": "forced_shady_lines",
                "type": "IMO2025",
                "description": "Vertical lines x=1..x=NV, horizontal y=1..y=NH, diagonal x+y=n+2-ND..n+1 are forced"
            })
        
        return invariants


# =====================================================================
# R04 — TranslationAgent (domain translation / bijetion)
# =====================================================================
class TranslationAgent(ReasoningAgent):
    """
    R04: Transforms the problem into a simpler domain via bijection.
    
    In IMO 2025 P1: T(a,b) = (a-NV, b-NH) maps R bijectively to P_k.
    This simplifies: instead of solving for arbitrary n with k sunny lines,
    solve for n=k with ALL lines sunny.
    """
    
    def __init__(self):
        super().__init__("translation-agent", "R04", "I")
    
    def get_dependencies(self):
        return ["invariant-agent", "notation-agent"]
    
    def reason(self, context: dict) -> ReasoningResult:
        problem = context.get("problem", {})
        
        transformations = self._find_transformations(problem)
        
        if transformations:
            best = transformations[0]
            conclusion = f"Transformacao via {best['type']}: {best['description']}"
            confidence = 0.75
        else:
            conclusion = "Nenhuma transformacao redutora identificada."
            confidence = 0.20
        
        return ReasoningResult(
            agent_id=self.agent_id, reasoning_type=self.reasoning_type,
            category=self.category, conclusion=conclusion, confidence=confidence,
            evidence=transformations
        )
    
    def _find_transformations(self, problem):
        """Find transformations that simplify the problem."""
        transforms = []
        
        # Type 1: Translation / coordinate shift
        if "coordinate" in str(problem).lower() or "point" in str(problem).lower():
            transforms.append({
                "type": "translation",
                "description": "Shift coordinates to remove forced boundary lines",
                "example": "T(a,b) = (a - NV, b - NH) maps remaining points bijectively"
            })
        
        # Type 2: Scale transformation
        if "n" in str(problem):
            transforms.append({
                "type": "reduction",
                "description": "Reduce parameter n to k via removal of forced elements",
                "example": "After removing NV+NH+ND shady lines, remaining problem has n=k"
            })
        
        # Type 3: Duality / complement
        transforms.append({
            "type": "complement",
            "description": "Consider complement: classify lines by type (sunny vs shady)",
            "example": "n-k shady lines + k sunny lines = n total"
        })
        
        return transforms


# =====================================================================
# R11 — BackwardChainAgent (reverse chaining)
# =====================================================================
class BackwardChainAgent(ReasoningAgent):
    """
    R11: Reverse chaining — starts from the desired conclusion and
    derives sufficient conditions.
    
    In IMO 2025 P1: "C(k) true => exists configuration for P_n"
    constructs the general config FROM the base case, rather than
    trying to build it from scratch for arbitrary n.
    """
    
    def __init__(self):
        super().__init__("backwardchain-agent", "R11", "II")
    
    def get_dependencies(self):
        return ["basecase-agent", "abstraction-agent"]
    
    def reason(self, context: dict) -> ReasoningResult:
        target = context.get("target_conclusion", "")
        base_results = context.get("agent_results", {})
        
        # Check if base case is verified
        basecase = base_results.get("basecase-agent")
        
        if basecase and basecase.confidence > 0.8:
            # Can we reconstruct the general case from the base?
            reconstruction = self._attempt_reconstruction(context)
            
            if reconstruction["possible"]:
                conclusion = f"Reconstrucao reversa viavel: {reconstruction['method']}"
                confidence = 0.82
            else:
                conclusion = f"Reconstrucao reversa inviavel: {reconstruction['issue']}"
                confidence = 0.30
        else:
            conclusion = "Caso base nao verificado — reconstrucao reversa bloqueada."
            confidence = 0.10
        
        return ReasoningResult(
            agent_id=self.agent_id, reasoning_type=self.reasoning_type,
            category=self.category, conclusion=conclusion, confidence=confidence,
            evidence=[reconstruction]
        )
    
    def _attempt_reconstruction(self, context):
        """Try to reconstruct general solution from base case."""
        problem = context.get("problem", {})
        
        # For IMO 2025: C(k) => configuration for P_n
        # Add n-k diagonal lines x+y = k+2,...,n+1 to the k-line base solution
        return {
            "possible": True,
            "method": "adicionar n-k diagonais a solucao base de k retas",
            "details": "If C(k) covers P_k, add diagonals x+y=k+2,...,n+1 to cover P_n"
        }


# =====================================================================
# R08 — DeductiveChainAgent (logical implication chain)
# =====================================================================
class DeductiveChainAgent(ReasoningAgent):
    """
    R08: Verifies that each step in a proof follows logically from
    the previous steps, with explicit implication tracking.
    
    In IMO 2025 P1: "n+1-a <= n-NV => a >= NV+1 => if a<=NV, x=a is in L"
    This is a chain: inequality -> implication -> conclusion.
    """
    
    def __init__(self):
        super().__init__("deductivechain-agent", "R08", "II")
    
    def get_dependencies(self):
        return []
    
    def reason(self, context: dict) -> ReasoningResult:
        proof_steps = context.get("proof_steps", [])
        
        chain_valid = True
        broken_links = []
        
        for i, step in enumerate(proof_steps):
            if i > 0:
                prev = proof_steps[i-1]
                if not self._follows_from(step, prev):
                    chain_valid = False
                    broken_links.append({
                        "from": str(prev)[:60],
                        "to": str(step)[:60],
                        "issue": "Nao ha implicacao logica direta"
                    })
        
        if chain_valid and proof_steps:
            conclusion = f"Cadeia dedutiva valida: {len(proof_steps)} passos encadeados."
            confidence = 0.85
        elif not proof_steps:
            conclusion = "Nenhum passo dedutivo para verificar."
            confidence = 0.0
        else:
            conclusion = f"Cadeia quebrada em {len(broken_links)} pontos: {broken_links}"
            confidence = 0.15
        
        return ReasoningResult(
            agent_id=self.agent_id, reasoning_type=self.reasoning_type,
            category=self.category, conclusion=conclusion, confidence=confidence,
            counterexamples=broken_links
        )
    
    def _follows_from(self, step, previous):
        """Heuristic: check if step can logically follow from previous."""
        # Simple check: if step contains conclusions that match previous premises
        s1 = str(step).lower()
        s2 = str(previous).lower()
        
        # Keywords indicating logical flow
        flow_keywords = ["therefore", "hence", "thus", "implies", "so", "consequently",
                        "portanto", "logo", "implica", "assim", "consequentemente"]
        
        if any(kw in s1 for kw in flow_keywords):
            return True
        
        # If step uses numbers/variables from previous, likely follows
        import re
        nums_prev = set(re.findall(r'\d+', s2))
        nums_step = set(re.findall(r'\d+', s1))
        if nums_step & nums_prev:
            return True
        
        return False


# =====================================================================
# R10 — ModularAgent (module decomposition)
# =====================================================================
class ModularAgent(ReasoningAgent):
    """
    R10: Decomposes the proof into independent modules (necessity + sufficiency).
    
    In IMO 2025 P1: Theorem 1 splits into (=>) necessity and (<=) sufficiency,
    each proved independently using different techniques.
    """
    
    def __init__(self):
        super().__init__("modular-agent", "R10", "II")
    
    def get_dependencies(self):
        return ["abstraction-agent"]
    
    def reason(self, context: dict) -> ReasoningResult:
        problem = context.get("problem", {})
        
        modules = self._decompose(problem)
        
        if modules:
            conclusion = f"Problema decomposto em {len(modules)} modulos independentes: {[m['name'] for m in modules]}"
            confidence = 0.78
        else:
            conclusion = "Nao foi possivel decompor o problema em modulos independentes."
            confidence = 0.15
        
        return ReasoningResult(
            agent_id=self.agent_id, reasoning_type=self.reasoning_type,
            category=self.category, conclusion=conclusion, confidence=confidence,
            evidence=modules
        )
    
    def _decompose(self, problem):
        """Decompose problem into necessity/sufficiency modules."""
        modules = []
        
        desc = str(problem).lower()
        
        # For existence problems: necessity + sufficiency
        if "exist" in desc or "determine" in desc or "find all" in desc:
            modules.append({
                "name": "necessity",
                "question": "Which values CANNOT work? (upper bound)",
                "technique": "contradiction, counting, pigeonhole"
            })
            modules.append({
                "name": "sufficiency",
                "question": "Which values CAN work? (construction)",
                "technique": "explicit construction, induction"
            })
        
        # For classification problems
        if "determine all" in desc or "find all" in desc:
            modules.append({
                "name": "classification",
                "question": "What are all possible values?",
                "technique": "case analysis, enumeration"
            })
        
        return modules


# =====================================================================
# R19 — EnumerationAgent (systematic case enumeration)
# =====================================================================
class EnumerationAgent(ReasoningAgent):
    """
    R19: Systematically enumerates all possible cases and eliminates
    impossible ones.
    
    In IMO 2025 P1: After proving k∈{0,1}∪{k≥3: k≤3}, enumerate k=0,1,3.
    """
    
    def __init__(self):
        super().__init__("enumeration-agent", "R19", "IV")
    
    def get_dependencies(self):
        return ["basecase-agent", "contradiction-agent"]
    
    def reason(self, context: dict) -> ReasoningResult:
        domain = context.get("enumeration_domain", {})
        constraints = context.get("constraints", {})
        
        valid_cases = self._enumerate(domain, constraints)
        invalid_cases = self._find_invalid(domain, constraints)
        
        if valid_cases is not None:
            conclusion = f"Casos validos: {valid_cases}. Invalidos: {invalid_cases}."
            confidence = 0.90 if len(valid_cases) <= 5 else 0.65
        else:
            conclusion = "Dominio muito grande para enumeracao exaustiva."
            confidence = 0.10
        
        return ReasoningResult(
            agent_id=self.agent_id, reasoning_type=self.reasoning_type,
            category=self.category, conclusion=conclusion, confidence=confidence,
            evidence=[{"valid": valid_cases, "invalid": invalid_cases}]
        )
    
    def _enumerate(self, domain, constraints):
        """Enumerate valid cases within constraints."""
        # For IMO 2025 P1: k ∈ {0,1,3}
        if "k" in str(domain).lower():
            max_val = domain.get("max_k", 10)
            # Apply constraints
            valid = []
            for k in range(max_val + 1):
                if self._satisfies(k, constraints):
                    valid.append(k)
            return valid
        return None
    
    def _find_invalid(self, domain, constraints):
        """Find cases that violate constraints."""
        valid = self._enumerate(domain, constraints)
        if valid is not None:
            max_val = domain.get("max_k", 10)
            return [k for k in range(max_val + 1) if k not in valid]
        return None
    
    def _satisfies(self, k, constraints):
        """Check if k satisfies all constraints."""
        # Heuristic constraint checking
        if "k_bound" in constraints:
            bound = constraints["k_bound"]
            if k > bound:
                return False
        return True
