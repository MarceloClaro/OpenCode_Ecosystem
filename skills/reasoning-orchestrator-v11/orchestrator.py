# =====================================================================
# REASONING ORCHESTRATOR v11.0
# Pipeline de 7 fases com 68 raciocinios em 12 categorias
# =====================================================================
import sys, os, json, time
from typing import Any
from dataclasses import dataclass, field

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agents"))
from framework import (ReasoningAgent, ReasoningResult, AgentStatus, 
                        LemmaNode, REASONING_REGISTRY, get_agents_for_domain)
from critical_agents import (InductorAgent, BaseCaseAgent, ContraexemploAgent,
                              ContradictionAgent, StressTestAgent, ExhaustiveAgent,
                              CrossRefAgent, LemmaTrackerAgent)
from domain_agents import (HypothesisTester, PrecedentAnalyzer, 
                            RiskAssessor, ProofHealthAgent)
from complementary_agents import (InvariantAgent, TranslationAgent,
                                   BackwardChainAgent, DeductiveChainAgent,
                                   ModularAgent, EnumerationAgent)
from final_agents import (QuantificationalAgent, InductionAgent,
                           ReductioAgent, GeneralizationAgent)
from refined_agents import (RefinedLemmaTracker, RefinedContradictionAgent,
                             RefinedInductionAgent)
from exhaustive_fixes import (RobustNotationAgent, RobustAbstractionAgent, 
                               RobustConstructorAgent)
from game_theory_agents import (NashEquilibriumAgent, MinimaxAgent,
                                 BackwardInductionAgent, GameTheoryOrchestrator)

@dataclass
class OrchestratorState:
    problem: dict
    domain: str
    phase: int = 0
    agent_results: dict = field(default_factory=dict)
    lemma_graph: dict = field(default_factory=dict)
    pci: int = 0
    verdict: str = "PENDING"
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

class ReasoningOrchestrator:
    """Orchestrates the 7-phase reasoning pipeline."""
    
    def __init__(self):
        self.state: OrchestratorState = None
        self.lemma_tracker = RefinedLemmaTracker()
        
        # Phase → list of agent instances
        self.pipeline = {
            1: self._get_phase1_agents,  # Foundational
            2: self._get_phase2_agents,  # Inductive/Reductive
            3: self._get_phase3_agents,  # Deductive
            4: self._get_phase4_agents,  # Constructive
            5: self._get_phase5_agents,  # Refutational
            6: self._get_phase6_agents,  # Verificational
            7: self._get_phase7_agents,  # Meta-Cognitive
        }
    
    def solve(self, problem: dict, domain: str = "mathematics") -> dict:
        """Execute the full reasoning pipeline on a problem."""
        self.state = OrchestratorState(problem=problem, domain=domain)
        
        print(f"\n{'='*60}")
        print(f"REASONING ORCHESTRATOR v11.0")
        print(f"Dominio: {domain}")
        print(f"{'='*60}")
        
        for phase in range(1, 8):
            self.state.phase = phase
            agents = self.pipeline[phase]()
            self._execute_phase(phase, agents)
        
        # Compute final PCI
        health_agent = ProofHealthAgent(self.lemma_tracker)
        health_result = health_agent.reason({
            "agent_results": self.state.agent_results,
            "cora_pass_count": self.state.agent_results.get("cora_pass_count", 0)
        })
        self.state.agent_results["proofhealth-agent"] = health_result
        self.state.pci = int(health_result.confidence * 100)
        self.state.verdict = health_result.conclusion
        
        return self._summarize()
    
    def _execute_phase(self, phase_num: int, agents: list[ReasoningAgent]):
        """Execute all agents in a phase."""
        print(f"\n--- FASE {phase_num} ---")
        
        for agent in agents:
            if not agent.validate_dependencies({
                "agent_results": self.state.agent_results,
                "problem": self.state.problem,
                "lemma_graph": self.state.lemma_graph
            }):
                self.state.warnings.append(
                    f"{agent.agent_id}: dependencias nao satisfeitas — pulando"
                )
                continue
            
            try:
                result = agent.reason({
                    "problem": self.state.problem,
                    "agent_results": self.state.agent_results,
                    "lemma_graph": self.state.lemma_graph,
                    "domain": self.state.domain,
                    "claimed_answer": self.state.problem.get("claimed_answer", set()),
                    "problem_id": self.state.problem.get("id", "unknown"),
                })
                self.state.agent_results[agent.agent_id] = result
                
                status = "PASS" if result.confidence > 0.7 else ("WARN" if result.confidence > 0.4 else "FAIL")
                print(f"  [{status}] {agent.agent_id}: {result.conclusion[:80]}")
                
                if result.counterexamples:
                    self.state.errors.extend(result.counterexamples)
                if result.warnings:
                    self.state.warnings.extend(result.warnings)
                    
            except Exception as e:
                self.state.errors.append(f"{agent.agent_id}: {str(e)}")
                print(f"  [ERROR] {agent.agent_id}: {e}")
    
    def _get_phase1_agents(self):
        return [RobustNotationAgent(), RobustAbstractionAgent(), ModularAgent()]
    
    def _get_phase2_agents(self):
        return [InductorAgent(), BaseCaseAgent(), InductionAgent()]
    
    def _get_phase3_agents(self):
        return [self.lemma_tracker, DeductiveChainAgent(), 
                BackwardChainAgent(), QuantificationalAgent()]
    
    def _get_phase4_agents(self):
        return [RobustConstructorAgent(), StressTestAgent()]
    
    def _get_phase5_agents(self):
        return [RefinedContradictionAgent(), ContraexemploAgent(), ReductioAgent()]
    
    def _get_phase6_agents(self):
        return [ExhaustiveAgent(), CrossRefAgent(), EnumerationAgent()]
    
    def _get_phase7_agents(self):
        return [GeneralizationAgent()]  # ProofHealthAgent called separately
    
    def _summarize(self) -> dict:
        print(f"\n{'='*60}")
        print(f"RESUMO FINAL")
        print(f"{'='*60}")
        print(f"PCI: {self.state.pci}/100")
        print(f"Veredito: {self.state.verdict}")
        print(f"Erros: {len(self.state.errors)}")
        print(f"Avisos: {len(self.state.warnings)}")
        
        return {
            "pci": self.state.pci,
            "verdict": self.state.verdict,
            "agent_results": {
                agent_id: {
                    "conclusion": r.conclusion,
                    "confidence": r.confidence,
                    "type": r.reasoning_type
                }
                for agent_id, r in self.state.agent_results.items()
            },
            "errors": self.state.errors,
            "warnings": self.state.warnings,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        }


# =====================================================================
# TEST: IMO 2025 Problem 1 — Verification
# =====================================================================
def test_imo2025():
    """Test the orchestrator on IMO 2025 Problem 1."""
    orchestrator = ReasoningOrchestrator()
    
    problem = {
        "id": "IMO-2025-P1",
        "description": "Determinar k validos para n retas com k ensolaradas",
        "n": 3,
        "domain": "combinatorial",
        "structure": {"type": "combinatorial_geometry", "elements": ["lines", "points", "grid"]},
        "constraints": {"boundary_forced": True, "sunny_condition": "slope not in {0, infinity, -1}"},
        "claimed_answer": {0, 1, 3},  # CORRECT answer per Evan Chen + DeepMind
        "statements": [
            "The NV vertical lines must be {x=1,...,x=NV} (forced by column counting)",
            "T(a,b) = (a-NV, b-NH) maps remaining points bijectively to P_k",
            "|B_k| = 3k-3. A sunny line intersects boundary at most twice. 3k-3 <= 2k -> k <= 3.",
        ],
        "proof_steps": [
            "n+1-a <= n-NV",
            "a >= NV+1",
            "if a <= NV, then x=a must be in L (contrapositive)",
            "Therefore NV vertical lines are forced: {x=1,...,x=NV}"
        ],
        "claims": ["k ∈ {0,1,3}", "k=2 is impossible", "C(k) reduces to core case"],
        "construction": {"type": "diagonal+sunny", "k": 3, "lines": ["y=x", "2x+y=5", "x+2y=5"]},
        "base_n": 3,
        "test_n": [3, 4, 5],
        "exhaustive_n": 5,
        "enumeration_domain": {"max_k": 5},
        "target_conclusion": "k ∈ {0,1,3} for all n >= 3",
    }
    
    result = orchestrator.solve(problem, domain="mathematics")
    return result

if __name__ == "__main__":
    result = test_imo2025()
    print(f"\nFinal PCI: {result['pci']}/100")
    print(f"Veredito: {result['verdict']}")
    
    if result["errors"]:
        print(f"\nERROS DETECTADOS:")
        for e in result["errors"]:
            print(f"  - {e}")
    
    # Export
    with open("orchestrator_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print("\nResultado exportado: orchestrator_result.json")
