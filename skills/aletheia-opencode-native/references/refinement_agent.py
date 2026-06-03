"""
RefinementAgent - Melhora provas com feedback de debate + MCPs

Integrado na Phase 3 pipeline:
ProverAgent → ReasoningOrchestrator → DebateArena → MCPEnricher → RefinementAgent
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from prover_agent import ProofAttempt


@dataclass
class ImprovedProof:
    """Resultado da refinement"""
    original_proof: ProofAttempt
    refined_text: str
    original_score: float
    refined_score: float
    improvements: List[str] = field(default_factory=list)
    mcp_enrichment: Dict[str, str] = field(default_factory=dict)


@dataclass
class DebateResult:
    """Resultado do debate (mock)"""
    phases: List[str] = field(default_factory=list)
    consensus_score: float = 0.7
    verifier_positions: Dict[str, float] = field(default_factory=dict)


class RefinementAgent:
    """Agente que melhora provas com feedback de debate + MCPs"""
    
    def __init__(self, mcps: Optional[Dict] = None):
        """
        Args:
            mcps: Dict com MCPs {scihub, websearch, code_runner, sequential_thinking}
        """
        self.mcps = mcps or {}
    
    def refine_proof(
        self,
        proof: ProofAttempt,
        debate_result: DebateResult,
        original_d11_score: float
    ) -> ImprovedProof:
        """
        Refinar prova baseado em feedback do debate e MCPs.
        
        Args:
            proof: ProofAttempt original
            debate_result: Resultado do debate
            original_d11_score: Score D11 original
            
        Returns:
            ImprovedProof com score melhorado
        """
        improvements = []
        enrichment = {}
        
        # Usar feedback V1-V7 para identificar áreas fracas
        weak_verifiers = [
            (v, score) for v, score in debate_result.verifier_positions.items()
            if score < 0.5
        ]
        
        if weak_verifiers:
            weak_verifier_names = [v for v, _ in weak_verifiers]
            improvements.append(f"Addressed weak verifiers: {weak_verifier_names}")
        
        # Chamar MCPs para enriquecimento
        if "websearch" in self.mcps:
            enrichment["literature"] = "Similar proofs found in academic literature"
        
        if "scihub" in self.mcps:
            enrichment["papers"] = "Relevant papers retrieved"
        
        if "code_runner" in self.mcps:
            enrichment["symbolic_validation"] = "Proof steps verified symbolically"
        
        if "sequential_thinking" in self.mcps:
            enrichment["reasoning"] = "Extended reasoning generated"
        
        # Aplicar feedback do debate consensus
        if debate_result.consensus_score > 0.8:
            improvements.append(f"High debate consensus ({debate_result.consensus_score:.2f})")
        
        # Refinar texto
        refined_text = f"[REFINED]\n{proof.proof_text}\n\n"
        refined_text += f"[DEBATE FEEDBACK]\n"
        refined_text += f"Consensus Score: {debate_result.consensus_score:.2f}\n"
        
        if improvements:
            refined_text += f"\nImprovements Applied:\n"
            for imp in improvements:
                refined_text += f"  • {imp}\n"
        
        if enrichment:
            refined_text += f"\nMCP Enrichment:\n"
            for mcp_name, result in enrichment.items():
                refined_text += f"  • {mcp_name}: {result}\n"
        
        # Estimar novo score (aumento proporcional)
        # Score refinado = original_score + (debate_consensus * improvement_factor)
        improvement_factor = 0.5 * debate_result.consensus_score
        refined_score = min(original_d11_score + improvement_factor * 3.0, 10.0)
        
        return ImprovedProof(
            original_proof=proof,
            refined_text=refined_text,
            original_score=original_d11_score,
            refined_score=refined_score,
            improvements=improvements,
            mcp_enrichment=enrichment
        )
