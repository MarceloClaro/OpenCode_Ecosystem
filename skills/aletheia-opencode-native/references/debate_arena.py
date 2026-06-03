"""
DebateArena — Debate Multi-Agente com Cora-Debate V1-V7

4 Fases estruturadas:
1. OPEN: Cada verificador apresenta posição inicial
2. DISCUSS: Debate dialético com contra-argumentos
3. SYNTHESIZE: Nash Solver para encontrar consenso
4. CONCLUDE: Resultado final com justificativas

7 Verificadores (V1-V7):
- V1: Rigor Matemático
- V2: Elegância da Prova
- V3: Clareza Pedagógica
- V4: Compacidade
- V5: Inovação
- V6: Completude
- V7: Síntese (Nash Equilibrium Solver)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Tuple, Any, Optional
from datetime import datetime
import json


class DebatePhase(Enum):
    """Fases do debate estruturado"""
    OPEN = "OPEN"
    DISCUSS = "DISCUSS"
    SYNTHESIZE = "SYNTHESIZE"
    CONCLUDE = "CONCLUDE"


class VerifierType(Enum):
    """7 Verificadores no Cora-Debate"""
    V1_RIGOR = "V1_RIGOR"                      # Rigor Matemático
    V2_ELEGANCE = "V2_ELEGANCE"                # Elegância
    V3_PEDAGOGY = "V3_PEDAGOGY"                # Clareza Pedagógica
    V4_COMPACTNESS = "V4_COMPACTNESS"          # Compacidade
    V5_INNOVATION = "V5_INNOVATION"            # Inovação
    V6_COMPLETENESS = "V6_COMPLETENESS"        # Completude
    V7_SYNTHESIS = "V7_SYNTHESIS"              # Síntese (Nash)


@dataclass
class VerifierPosition:
    """Posição de um verificador em um momento"""
    verifier_type: VerifierType
    score: float  # 0.0-1.0
    rationale: str
    phase: DebatePhase
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DebateMove:
    """Movimento no debate: argumento + contra-argumento"""
    phase: DebatePhase
    from_verifier: VerifierType
    to_verifier: VerifierType  # Alvo do contra-argumento
    argument: str
    counter_argument: str = ""


@dataclass
class DebateResult:
    """Resultado final do debate"""
    problem_id: str
    num_phases: int
    final_positions: Dict[VerifierType, VerifierPosition]
    consensus_score: float  # 0.0-1.0 (concordância)
    debate_transcript: List[DebateMove] = field(default_factory=list)
    nash_equilibrium: Optional[Dict[str, float]] = None
    conclusion_text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class VerifierMock:
    """Mock de um verificador (pode ser substituído por V7 real)"""
    
    def __init__(self, verifier_type: VerifierType):
        self.verifier_type = verifier_type
        self.current_position: Optional[VerifierPosition] = None
    
    def evaluate(
        self,
        proof_text: str,
        phase: DebatePhase,
        context: Optional[str] = None
    ) -> VerifierPosition:
        """Simular avaliação do verificador"""
        # Score base depende do verificador
        base_scores = {
            VerifierType.V1_RIGOR: 0.75,
            VerifierType.V2_ELEGANCE: 0.65,
            VerifierType.V3_PEDAGOGY: 0.60,
            VerifierType.V4_COMPACTNESS: 0.70,
            VerifierType.V5_INNOVATION: 0.55,
            VerifierType.V6_COMPLETENESS: 0.80,
            VerifierType.V7_SYNTHESIS: 0.72,
        }
        
        score = base_scores.get(self.verifier_type, 0.7)
        
        # Adicionar variação por fase
        phase_adjustments = {
            DebatePhase.OPEN: 0.0,
            DebatePhase.DISCUSS: 0.05,  # Pequeno ajuste com discussão
            DebatePhase.SYNTHESIZE: 0.10,
            DebatePhase.CONCLUDE: 0.0,
        }
        score += phase_adjustments.get(phase, 0.0)
        score = min(1.0, score)  # Capped at 1.0
        
        rationale = self._get_rationale(self.verifier_type, score)
        
        position = VerifierPosition(
            verifier_type=self.verifier_type,
            score=score,
            rationale=rationale,
            phase=phase
        )
        
        self.current_position = position
        return position
    
    @staticmethod
    def _get_rationale(verifier_type: VerifierType, score: float) -> str:
        """Gerar rationale simulado"""
        rationales = {
            VerifierType.V1_RIGOR: f"Rigor matemático: {score:.2f}/1.0 - prova logicamente consistente",
            VerifierType.V2_ELEGANCE: f"Elegância: {score:.2f}/1.0 - abordagem sofisticada e direta",
            VerifierType.V3_PEDAGOGY: f"Clareza: {score:.2f}/1.0 - explicações bem estruturadas",
            VerifierType.V4_COMPACTNESS: f"Compacidade: {score:.2f}/1.0 - prova concisa e eficiente",
            VerifierType.V5_INNOVATION: f"Inovação: {score:.2f}/1.0 - técnicas criativas aplicadas",
            VerifierType.V6_COMPLETENESS: f"Completude: {score:.2f}/1.0 - todos os casos cobertos",
            VerifierType.V7_SYNTHESIS: f"Síntese: {score:.2f}/1.0 - consenso equilibrado",
        }
        return rationales.get(verifier_type, f"Avaliação: {score:.2f}/1.0")


class DebateArena:
    """Orquestrador de debate Cora-Debate V1-V7 com 4 fases"""
    
    def __init__(self, use_real_verifiers: bool = False):
        """
        Inicializar DebateArena
        
        Args:
            use_real_verifiers: Se True, usar verificadores reais (não implementado aqui)
        """
        self.use_real_verifiers = use_real_verifiers
        
        # Inicializar 7 verificadores
        self.verifiers: Dict[VerifierType, VerifierMock] = {
            vtype: VerifierMock(vtype)
            for vtype in VerifierType
        }
        
        self.debate_moves: List[DebateMove] = []
        self.phase_positions: Dict[DebatePhase, Dict[VerifierType, VerifierPosition]] = {}
    
    def orchestrate_debate(
        self,
        problem: Any,
        proof_text: str,
        max_rounds: int = 2
    ) -> DebateResult:
        """
        Orquestrar debate completo em 4 fases
        
        Args:
            problem: IMOProblem
            proof_text: Texto da prova a debater
            max_rounds: Número de rounds de discussão
        
        Returns:
            DebateResult com consenso e posições finais
        """
        problem_id = getattr(problem, "problem_id", "Unknown")
        
        # Fase 1: OPEN - Posições iniciais
        self._phase_open(proof_text)
        
        # Fase 2: DISCUSS - Debate com contra-argumentos
        self._phase_discuss(proof_text, max_rounds)
        
        # Fase 3: SYNTHESIZE - Nash Solver
        nash_eq = self._phase_synthesize()
        
        # Fase 4: CONCLUDE - Conclusão
        conclusion = self._phase_conclude()
        
        # Calcular consensus_score
        consensus_score = self._calculate_consensus()
        
        # Montar resultado
        result = DebateResult(
            problem_id=problem_id,
            num_phases=4,
            final_positions=self.phase_positions[DebatePhase.CONCLUDE],
            consensus_score=consensus_score,
            debate_transcript=self.debate_moves,
            nash_equilibrium=nash_eq,
            conclusion_text=conclusion,
            metadata={
                "num_verifiers": len(self.verifiers),
                "max_discussion_rounds": max_rounds,
                "problem_category": getattr(problem, "category", "Unknown"),
                "problem_level": getattr(problem, "level", "Unknown"),
            }
        )
        
        return result
    
    def _phase_open(self, proof_text: str):
        """Fase 1: OPEN - Cada verificador apresenta posição inicial"""
        positions = {}
        
        for vtype, verifier in self.verifiers.items():
            position = verifier.evaluate(proof_text, DebatePhase.OPEN)
            positions[vtype] = position
        
        self.phase_positions[DebatePhase.OPEN] = positions
    
    def _phase_discuss(self, proof_text: str, max_rounds: int):
        """Fase 2: DISCUSS - Debate dialético"""
        all_vtypes = list(VerifierType)
        
        for round_num in range(max_rounds):
            # Cada verificador contra-argumenta o seguinte (ciclo)
            for i, from_vtype in enumerate(all_vtypes):
                to_vtype = all_vtypes[(i + 1) % len(all_vtypes)]
                
                move = DebateMove(
                    phase=DebatePhase.DISCUSS,
                    from_verifier=from_vtype,
                    to_verifier=to_vtype,
                    argument=f"Round {round_num + 1}: {from_vtype.value} challenges {to_vtype.value}",
                    counter_argument=f"Counter from {to_vtype.value} to {from_vtype.value}"
                )
                
                self.debate_moves.append(move)
        
        # Atualizar posições após discussão
        positions = {}
        for vtype, verifier in self.verifiers.items():
            position = verifier.evaluate(proof_text, DebatePhase.DISCUSS)
            positions[vtype] = position
        
        self.phase_positions[DebatePhase.DISCUSS] = positions
    
    def _phase_synthesize(self) -> Dict[str, float]:
        """Fase 3: SYNTHESIZE - Nash Solver para encontrar equilíbrio"""
        # Simular Nash Equilibrium Solver
        # Em realidade, seria resolvido via programação linear ou otimização
        
        positions = self.phase_positions.get(DebatePhase.DISCUSS, {})
        scores = {vtype.value: pos.score for vtype, pos in positions.items()}
        
        # Nash equilibrium simulado: média ponderada com ajustes de convergência
        nash_eq = {}
        total_score = sum(scores.values())
        
        for vtype, score in scores.items():
            # Peso proporcional ao score
            weight = score / total_score if total_score > 0 else 1.0 / len(scores)
            nash_eq[vtype] = weight
        
        # Posições finais após síntese
        positions_synthesize = {}
        for vtype, verifier in self.verifiers.items():
            position = verifier.evaluate(
                "",  # Dummy proof_text
                DebatePhase.SYNTHESIZE,
                context=f"Nash weight: {nash_eq.get(vtype.value, 0.0):.3f}"
            )
            positions_synthesize[vtype] = position
        
        self.phase_positions[DebatePhase.SYNTHESIZE] = positions_synthesize
        
        return nash_eq
    
    def _phase_conclude(self) -> str:
        """Fase 4: CONCLUDE - Conclusão final"""
        # Atualizar posições finais
        positions = {}
        for vtype, verifier in self.verifiers.items():
            position = verifier.evaluate("", DebatePhase.CONCLUDE)
            positions[vtype] = position
        
        self.phase_positions[DebatePhase.CONCLUDE] = positions
        
        # Gerar conclusão baseada em consenso
        avg_score = sum(p.score for p in positions.values()) / len(positions)
        
        conclusion = f"""
DEBATE CONCLUSION:
- Average Verifier Score: {avg_score:.3f}/1.0
- Consensus Level: {self._calculate_consensus():.3f}
- All 7 verifiers agreed on: proof is valid and well-structured
- Recommended improvements: increase innovation and pedagogical clarity
"""
        
        return conclusion.strip()
    
    def _calculate_consensus(self) -> float:
        """Calcular score de consenso (acordo entre verificadores)"""
        if not self.phase_positions:
            return 0.0
        
        # Usar última fase disponível
        latest_phase = max(self.phase_positions.keys(), 
                          key=lambda x: list(DebatePhase).index(x))
        positions = self.phase_positions[latest_phase]
        
        scores = [p.score for p in positions.values()]
        
        if not scores:
            return 0.0
        
        # Consenso = 1 - (desvio padrão normalizado)
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5
        
        # Normalizar std_dev para [0, 1]
        # std_dev máximo possível é ~0.33 (scores em [0, 1])
        consensus = max(0.0, 1.0 - (std_dev / 0.33))
        
        return min(1.0, consensus)
    
    def generate_debate_report(self, result: DebateResult) -> Dict[str, Any]:
        """Gerar relatório estruturado do debate"""
        
        # Posições por fase
        phases_summary = {}
        for phase, positions in self.phase_positions.items():
            phases_summary[phase.value] = {
                vtype.value: pos.score
                for vtype, pos in positions.items()
            }
        
        # Top 3 verificadores
        final_positions = result.final_positions
        top_verifiers = sorted(
            final_positions.items(),
            key=lambda x: x[1].score,
            reverse=True
        )[:3]
        
        report = {
            "problem_id": result.problem_id,
            "debate_phases": 4,
            "num_verifiers": 7,
            "consensus_score": result.consensus_score,
            "average_score": sum(p.score for p in final_positions.values()) / len(final_positions),
            "phases_evolution": phases_summary,
            "top_3_verifiers": [
                {
                    "verifier": vtype.value,
                    "final_score": pos.score,
                    "rationale": pos.rationale
                }
                for vtype, pos in top_verifiers
            ],
            "nash_equilibrium_weights": result.nash_equilibrium,
            "conclusion": result.conclusion_text,
            "transcript_length": len(result.debate_transcript),
            "debate_moves": [
                {
                    "phase": move.phase.value,
                    "from": move.from_verifier.value,
                    "to": move.to_verifier.value,
                }
                for move in result.debate_transcript[:5]  # Primeiros 5 moves
            ]
        }
        
        return report


def create_debate_arena() -> DebateArena:
    """Factory para criar DebateArena"""
    return DebateArena(use_real_verifiers=False)


if __name__ == "__main__":
    from imo_benchmark_adapter import IMOProblem
    
    problem = IMOProblem(
        problem_id="DEBATE-001",
        problem_statement="Prove that every triangle's angle sum is 180 degrees.",
        solution="Using parallel postulate and alternate interior angles.",
        grading_guidelines="Must use geometry.",
        category="Geometry",
        level="IMO-easy",
        short_answer="180 degrees",
        source="IMO-ProofBench"
    )
    
    proof = "By the parallel postulate, a line parallel to BC through A forms alternate interior angles..."
    
    arena = create_debate_arena()
    result = arena.orchestrate_debate(problem, proof, max_rounds=1)
    
    print(f"\n[DEBATE ARENA]")
    print(f"Problem: {result.problem_id}")
    print(f"Consensus Score: {result.consensus_score:.3f}")
    print(f"Nash Equilibrium: {result.nash_equilibrium}")
    
    report = arena.generate_debate_report(result)
    print(f"\n[REPORT]")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    
    print(f"\n[CONCLUSION]")
    print(result.conclusion_text)
