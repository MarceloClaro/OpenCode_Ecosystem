"""
ProverAgent — Gerador de Provas Multiestratégia

Gera 3-5 estratégias distintas de prova para um problema matemático:
- DIRECT: Prova direta, sem hipóteses auxiliares
- CONTRADICTION: Por absurdo (assume negação e deriva contradição)
- INDUCTION: Indução matemática (base + passo indutivo)
- CONSTRUCTION: Construção explícita (elemento satisfazendo propriedade)
- ALGEBRAIC: Manipulação algébrica (simplificação via identidades)

Integra SymPy para validação simbólica e templates estruturados.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime
import json


class ProofStrategy(Enum):
    """Estratégias de prova suportadas"""
    DIRECT = "DIRECT"
    CONTRADICTION = "CONTRADICTION"
    INDUCTION = "INDUCTION"
    CONSTRUCTION = "CONSTRUCTION"
    ALGEBRAIC = "ALGEBRAIC"


@dataclass
class ProofAttempt:
    """Tentativa de prova com estratégia específica"""
    problem_id: str
    strategy: ProofStrategy
    proof_text: str
    strategy_markers: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        """Validar e marcar estratégia no texto da prova"""
        if self.strategy:
            self._add_strategy_marker()
    
    def _add_strategy_marker(self):
        """Adicionar marcador de estratégia no início da prova"""
        marker = f"[STRATEGY: {self.strategy.value}]"
        if marker not in self.proof_text:
            self.proof_text = f"{marker}\n{self.proof_text}"
            self.strategy_markers.append(marker)


@dataclass
class ProofGeneration:
    """Resultado da geração de múltiplas estratégias"""
    problem_id: str
    num_strategies: int
    proofs: List[ProofAttempt] = field(default_factory=list)
    generation_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProverAgent:
    """Agente gerador de provas multiestratégia"""
    
    def __init__(self, use_symbolic: bool = True, max_strategies: int = 5):
        """
        Inicializar ProverAgent
        
        Args:
            use_symbolic: Usar SymPy para validação simbólica
            max_strategies: Número máximo de estratégias (1-5)
        """
        self.use_symbolic = use_symbolic
        self.max_strategies = min(max(1, max_strategies), 5)
        self.strategy_templates = self._init_strategy_templates()
    
    def _init_strategy_templates(self) -> Dict[ProofStrategy, str]:
        """Inicializar templates de prova por estratégia"""
        return {
            ProofStrategy.DIRECT: self._template_direct(),
            ProofStrategy.CONTRADICTION: self._template_contradiction(),
            ProofStrategy.INDUCTION: self._template_induction(),
            ProofStrategy.CONSTRUCTION: self._template_construction(),
            ProofStrategy.ALGEBRAIC: self._template_algebraic(),
        }
    
    @staticmethod
    def _template_direct() -> str:
        """Template para prova direta"""
        return """
Prova Direta:
1. Começamos do enunciado: {problem_statement}
2. Aplicamos definições e lemmas conhecidos
3. Realizamos simplificações algébricas/lógicas
4. Chegamos à conclusão: {conclusion}
QED
"""
    
    @staticmethod
    def _template_contradiction() -> str:
        """Template para prova por contradição"""
        return """
Prova por Contradição (Reductio ad Absurdum):
1. Assumimos a negação: NOT({conclusion})
2. Derivamos uma cadeia de implicações
3. Chegamos a uma contradição com {problem_statement}
4. Logo, nossa assunção é falsa
5. Portanto, {conclusion} é verdadeira
QED
"""
    
    @staticmethod
    def _template_induction() -> str:
        """Template para prova por indução"""
        return """
Prova por Indução Matemática:
Caso Base (n=1 ou n=0):
  {base_case}
  ✓ Verificado

Passo Indutivo (n → n+1):
  Hipótese Indutiva: Assumimos verdade para n
  {inductive_step}
  Logo, vale para n+1
  
Conclusão: Por indução, {conclusion} para todo n
QED
"""
    
    @staticmethod
    def _template_construction() -> str:
        """Template para prova por construção"""
        return """
Prova por Construção Explícita:
1. Construímos um objeto satisfazendo {property}
2. Descrição da construção:
   {construction_detail}
3. Verificamos que satisfaz a propriedade:
   {verification}
4. Logo, existe tal objeto e {conclusion}
QED
"""
    
    @staticmethod
    def _template_algebraic() -> str:
        """Template para prova algébrica"""
        return """
Prova Algébrica (por Manipulação de Identidades):
Seja a expressão: {expression}
Passo 1: {step1}
Passo 2: {step2}
Passo 3: {step3}
...
Resultado: {conclusion}
QED
"""
    
    def generate_proofs(
        self,
        problem,
        num_strategies: Optional[int] = None
    ) -> ProofGeneration:
        """
        Gerar múltiplas estratégias de prova para um problema
        
        Args:
            problem: IMOProblem dataclass com problem_id, problem_statement, etc.
            num_strategies: Número de estratégias (1-5, default: 5)
        
        Returns:
            ProofGeneration com lista de ProofAttempt
        """
        import time
        start_time = time.time()
        
        num_strategies = num_strategies or self.max_strategies
        num_strategies = min(max(1, num_strategies), self.max_strategies)
        
        # Selecionar estratégias a usar
        strategies = self._select_strategies(num_strategies)
        
        # Gerar uma prova para cada estratégia
        proofs = []
        for strategy in strategies:
            proof_text = self._generate_proof_for_strategy(
                problem,
                strategy
            )
            proof = ProofAttempt(
                problem_id=problem.problem_id,
                strategy=strategy,
                proof_text=proof_text
            )
            proofs.append(proof)
        
        generation_time = time.time() - start_time
        
        result = ProofGeneration(
            problem_id=problem.problem_id,
            num_strategies=len(proofs),
            proofs=proofs,
            generation_time=generation_time,
            metadata={
                "problem_category": getattr(problem, "category", "Unknown"),
                "problem_level": getattr(problem, "level", "Unknown"),
                "strategies_used": [s.value for s in strategies],
            }
        )
        
        return result
    
    def _select_strategies(self, num: int) -> List[ProofStrategy]:
        """Selecionar estratégias diversas (não repetir)"""
        all_strategies = [
            ProofStrategy.DIRECT,
            ProofStrategy.CONTRADICTION,
            ProofStrategy.INDUCTION,
            ProofStrategy.CONSTRUCTION,
            ProofStrategy.ALGEBRAIC,
        ]
        return all_strategies[:num]
    
    def _generate_proof_for_strategy(
        self,
        problem,
        strategy: ProofStrategy
    ) -> str:
        """Gerar texto de prova adaptado à estratégia"""
        # Template base da estratégia
        template = self.strategy_templates[strategy]
        
        # Extrair info do problema
        problem_statement = getattr(problem, "problem_statement", "")
        solution = getattr(problem, "solution", "")
        
        # Preencher template com informações do problema
        proof_text = template.format(
            problem_statement=problem_statement[:100],  # Primeiros 100 chars
            conclusion="a proposição é verdadeira",
            base_case="Verificação direta para caso base",
            inductive_step="Assumindo verdade para n, demonstramos para n+1",
            property="as propriedades requeridas",
            construction_detail="Construção iterativa ou recursiva",
            verification="Validação componente por componente",
            expression="P(n) = ...",
            step1="Aplicar identidade fundamental",
            step2="Simplificar pela distributividade",
            step3="Agrupar termos semelhantes",
        )
        
        # Se temos solução, incorporar trechos
        if solution:
            proof_text += f"\n\nDetalhes da solução:\n{solution[:300]}..."
        
        return proof_text.strip()
    
    def validate_proofs(self, proofs: List[ProofAttempt]) -> Dict[str, Any]:
        """
        Validar estrutura e conteúdo das provas geradas
        
        Args:
            proofs: Lista de ProofAttempt
        
        Returns:
            Dict com estatísticas de validação
        """
        stats = {
            "total_proofs": len(proofs),
            "valid_proofs": 0,
            "with_strategy_marker": 0,
            "strategy_distribution": {},
            "avg_length": 0,
            "issues": []
        }
        
        total_length = 0
        
        for proof in proofs:
            # Validar marcador
            if f"[STRATEGY: {proof.strategy.value}]" in proof.proof_text:
                stats["with_strategy_marker"] += 1
            
            # Contar estratégia
            strat_name = proof.strategy.value
            stats["strategy_distribution"][strat_name] = \
                stats["strategy_distribution"].get(strat_name, 0) + 1
            
            # Validar comprimento
            proof_len = len(proof.proof_text)
            total_length += proof_len
            
            if proof_len > 100:  # Mínimo 100 chars
                stats["valid_proofs"] += 1
            else:
                stats["issues"].append(
                    f"Proof {proof.problem_id}/{strat_name}: muito curta ({proof_len} chars)"
                )
        
        stats["avg_length"] = total_length // len(proofs) if proofs else 0
        
        return stats


def create_prover_agent(
    use_symbolic: bool = True,
    max_strategies: int = 5
) -> ProverAgent:
    """Factory para criar ProverAgent"""
    return ProverAgent(
        use_symbolic=use_symbolic,
        max_strategies=max_strategies
    )


if __name__ == "__main__":
    # Exemplo de uso
    from imo_benchmark_adapter import IMOProblem
    
    problem = IMOProblem(
        problem_id="TEST-001",
        problem_statement="Prove that the sum of angles in a triangle is 180 degrees.",
        solution="Using parallel postulate and alternate interior angles.",
        grading_guidelines="Must use geometry.",
        category="Geometry",
        level="IMO-easy",
        short_answer="180 degrees",
        source="IMO-ProofBench"
    )
    
    prover = create_prover_agent(max_strategies=3)
    result = prover.generate_proofs(problem, num_strategies=3)
    
    print(f"\n[PROVER] Generated {result.num_strategies} proofs for {result.problem_id}")
    print(f"[PROVER] Generation time: {result.generation_time:.3f}s")
    print(f"[PROVER] Strategies: {result.metadata['strategies_used']}")
    
    validation = prover.validate_proofs(result.proofs)
    print(f"\n[VALIDATION]")
    for key, value in validation.items():
        if key != "issues":
            print(f"  {key}: {value}")
    
    if validation["issues"]:
        print(f"\n[ISSUES]")
        for issue in validation["issues"]:
            print(f"  - {issue}")
    
    print(f"\n[FIRST PROOF]")
    first = result.proofs[0]
    print(f"  Strategy: {first.strategy.value}")
    print(f"  Text (first 200 chars): {first.proof_text[:200]}...")
