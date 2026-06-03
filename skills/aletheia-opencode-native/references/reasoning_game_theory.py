"""
Game Theory Reasoning — 15 Estratégias de Raciocínio baseadas em Teoria dos Jogos

Parte do ReasoningOrchestrator-v11 (68 tipos em 12 categorias).
Categoria: Teoria dos Jogos (15 tipos)

Cada estratégia encapsula uma abordagem de análise de conflito, cooperação,
equilíbrio e decisão racional em ambientes competitivos/colaborativos.

Aplicações em IMO:
- Problemas combinatórios com adversários
- Otimização multi-objetivo
- Estratégias construtivas com múltiplos agentes
- Análise de simetria e soluções simétricas
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Tuple, Optional, Callable
from abc import ABC, abstractmethod
import json


class GameTheoryReasoningType(Enum):
    """15 tipos de raciocínio baseados em Teoria dos Jogos"""
    
    # Estratégia e Equilíbrio
    NASH_EQUILIBRIUM = "NASH_EQUILIBRIUM"              # 1: Análise de equilíbrio de Nash
    MINIMAX_STRATEGY = "MINIMAX_STRATEGY"              # 2: Estratégia min-max (worst-case)
    PARETO_OPTIMALITY = "PARETO_OPTIMALITY"            # 3: Otimalidade de Pareto
    DOMINANT_STRATEGY = "DOMINANT_STRATEGY"            # 4: Estratégia dominante
    
    # Cooperação e Conflito
    COALITION_FORMATION = "COALITION_FORMATION"        # 5: Formação de coalizões
    ZERO_SUM_ANALYSIS = "ZERO_SUM_ANALYSIS"            # 6: Análise de soma-zero
    COOPERATIVE_SOLUTION = "COOPERATIVE_SOLUTION"      # 7: Solução cooperativa (Shapley)
    PRISONERS_DILEMMA = "PRISONERS_DILEMMA"            # 8: Dilema do Prisioneiro
    
    # Simetria e Invariância
    SYMMETRY_BREAKING = "SYMMETRY_BREAKING"            # 9: Quebra de simetria estratégica
    SYMMETRIC_EQUILIBRIUM = "SYMMETRIC_EQUILIBRIUM"    # 10: Equilíbrio simétrico
    
    # Informação e Deception
    INFORMATION_ASYMMETRY = "INFORMATION_ASYMMETRY"    # 11: Análise sob informação assimétrica
    SIGNALING_STRATEGY = "SIGNALING_STRATEGY"          # 12: Estratégia de sinalização
    
    # Dinâmica e Evolução
    EVOLUTIONARY_STABLE = "EVOLUTIONARY_STABLE"        # 13: Estratégia evolutivamente estável (ESS)
    SEQUENTIAL_GAME = "SEQUENTIAL_GAME"                # 14: Análise de jogo sequencial (backward induction)
    POTENTIAL_FUNCTION = "POTENTIAL_FUNCTION"          # 15: Função potencial (convergência)


@dataclass
class GameTheoryAnalysis:
    """Resultado da análise de Teoria dos Jogos"""
    reasoning_type: GameTheoryReasoningType
    problem_context: str
    analysis_text: str
    key_insights: List[str]
    applicability_score: float  # 0.0-1.0
    recommended_proof_direction: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class GameTheoryReasoner(ABC):
    """Base class para raciocínio de Teoria dos Jogos"""
    
    reasoning_type: GameTheoryReasoningType
    description: str
    
    @abstractmethod
    def analyze(self, problem: Any, proof: Optional[str] = None) -> GameTheoryAnalysis:
        """Analisar problema usando essa estratégia de Teoria dos Jogos"""
        pass
    
    @abstractmethod
    def is_applicable(self, problem: Any) -> bool:
        """Verificar se essa estratégia é aplicável ao problema"""
        pass


# ============================================================================
# IMPLEMENTAÇÕES CONCRETAS (15 tipos)
# ============================================================================

class NashEquilibriumReasoner(GameTheoryReasoner):
    """
    1. Nash Equilibrium — Análise de equilíbrio onde nenhum jogador melhora
    desviando unilateralmente
    """
    reasoning_type = GameTheoryReasoningType.NASH_EQUILIBRIUM
    description = "Encontrar configurações onde nenhum jogador pode melhorar sozinho"
    
    def is_applicable(self, problem: Any) -> bool:
        """Aplicável a problemas com múltiplos agentes/escolhas"""
        problem_text = getattr(problem, "problem_statement", "").lower()
        keywords = ["choose", "strategy", "player", "game", "mutual", "equilibrium"]
        return any(kw in problem_text for kw in keywords)
    
    def analyze(self, problem: Any, proof: Optional[str] = None) -> GameTheoryAnalysis:
        analysis_text = """
Análise de Equilíbrio de Nash:
1. Identificar os jogadores e suas estratégias disponíveis
2. Para cada perfil de estratégia, verificar se é equilíbrio de Nash:
   - Nenhum jogador pode melhorar o payoff desviando sozinho
3. Provar existência de pelo menos um equilíbrio
4. Caracterizar a estrutura dos equilíbrios encontrados

Em problemas matemáticos, o "equilíbrio" pode ser:
- Uma configuração de objetos matemáticos
- Um padrão que se auto-perpetua
- Uma solução estável para otimização
"""
        return GameTheoryAnalysis(
            reasoning_type=self.reasoning_type,
            problem_context=getattr(problem, "category", "Unknown"),
            analysis_text=analysis_text,
            key_insights=[
                "Procure configurações auto-estáveis",
                "Verifique desvios unilaterais",
                "Pode haver múltiplos equilíbrios"
            ],
            applicability_score=0.8,
            recommended_proof_direction="Mostrar auto-perpetuação da configuração"
        )


class MinimaxStrategyReasoner(GameTheoryReasoner):
    """
    2. Minimax Strategy — Estratégia que minimiza o pior resultado possível
    (worst-case analysis)
    """
    reasoning_type = GameTheoryReasoningType.MINIMAX_STRATEGY
    description = "Otimizar contra o pior cenário adversário"
    
    def is_applicable(self, problem: Any) -> bool:
        problem_text = getattr(problem, "problem_statement", "").lower()
        keywords = ["worst", "minimum", "maximum", "adversary", "opponent"]
        return any(kw in problem_text for kw in keywords)
    
    def analyze(self, problem: Any, proof: Optional[str] = None) -> GameTheoryAnalysis:
        analysis_text = """
Análise Min-Max (Worst-Case):
1. Formular: max_strategy min_adversary f(strategy, adversary)
2. Identificar o pior cenário para cada escolha
3. Escolher a estratégia que maximiza o payoff mínimo
4. Provar que não há alternativa melhor contra adversário ótimo

Estrutura:
- Definir espaço de estratégias próprias
- Definir espaço de adversários/cenários
- Calcular payoff para cada combinação
- Encontrar max-min
"""
        return GameTheoryAnalysis(
            reasoning_type=self.reasoning_type,
            problem_context=getattr(problem, "category", "Unknown"),
            analysis_text=analysis_text,
            key_insights=[
                "Sempre considere o pior caso",
                "Worst-case garante robustez",
                "Útil para existência de objetos"
            ],
            applicability_score=0.75,
            recommended_proof_direction="Construção robusta contra adversário"
        )


class ParetoOptimalityReasoner(GameTheoryReasoner):
    """
    3. Pareto Optimality — Configurações onde não há melhoria para todos
    (não-dominância)
    """
    reasoning_type = GameTheoryReasoningType.PARETO_OPTIMALITY
    description = "Soluções eficientes onde ninguém pode melhorar sem piorar outro"
    
    def is_applicable(self, problem: Any) -> bool:
        problem_text = getattr(problem, "problem_statement", "").lower()
        keywords = ["optimal", "efficient", "pareto", "trade-off", "improve"]
        return any(kw in problem_text for kw in keywords)
    
    def analyze(self, problem: Any, proof: Optional[str] = None) -> GameTheoryAnalysis:
        analysis_text = """
Otimalidade de Pareto:
1. Definir critérios de desempenho múltiplos
2. Uma solução é Pareto-ótima se não há outra melhor em todos os critérios
3. Caracterizar a fronteira de Pareto (trade-off)
4. Mostrar que a solução proposta está na fronteira

Aplicação: Problemas com múltiplos objetivos (beleza, brevidade, generalidade)
"""
        return GameTheoryAnalysis(
            reasoning_type=self.reasoning_type,
            problem_context=getattr(problem, "category", "Unknown"),
            analysis_text=analysis_text,
            key_insights=[
                "Trade-off entre objetivos",
                "Eficiência em sentido forte",
                "Múltiplos Pareto-ótimos possíveis"
            ],
            applicability_score=0.7,
            recommended_proof_direction="Mostrar não-dominância"
        )


class DominantStrategyReasoner(GameTheoryReasoner):
    """
    4. Dominant Strategy — Estratégia melhor independentemente do que outros fazem
    """
    reasoning_type = GameTheoryReasoningType.DOMINANT_STRATEGY
    description = "Ação sempre melhor, independentemente de outras escolhas"
    
    def is_applicable(self, problem: Any) -> bool:
        problem_text = getattr(problem, "problem_statement", "").lower()
        keywords = ["always", "best response", "always true", "regardless"]
        return any(kw in problem_text for kw in keywords)
    
    def analyze(self, problem: Any, proof: Optional[str] = None) -> GameTheoryAnalysis:
        analysis_text = """
Estratégia Dominante:
1. Para cada ação, verificar se é melhor que todas as alternativas
2. Em toda contingência possível
3. Ação dominante: melhor contra qualquer comportamento adversário

Estrutura de prova:
- Enumerar todas as ações alternativas
- Para cada alternativa, mostrar contraexemplo
- Concluir que ação proposta domina
"""
        return GameTheoryAnalysis(
            reasoning_type=self.reasoning_type,
            problem_context=getattr(problem, "category", "Unknown"),
            analysis_text=analysis_text,
            key_insights=[
                "Simplicidade estratégica",
                "Prova direta por comparação",
                "Robustez contra incerteza"
            ],
            applicability_score=0.65,
            recommended_proof_direction="Comparação exaustiva"
        )


class CoalitionFormationReasoner(GameTheoryReasoner):
    """
    5. Coalition Formation — Análise de como agentes se agrupam para ganho mútuo
    """
    reasoning_type = GameTheoryReasoningType.COALITION_FORMATION
    description = "Agentes se agruparão em coalizões para maximizar ganho"
    
    def is_applicable(self, problem: Any) -> bool:
        problem_text = getattr(problem, "problem_statement", "").lower()
        keywords = ["partition", "group", "coalition", "subset", "team"]
        return any(kw in problem_text for kw in keywords)
    
    def analyze(self, problem: Any, proof: Optional[str] = None) -> GameTheoryAnalysis:
        analysis_text = """
Formação de Coalizões:
1. Modelar como agentes podem se particionar
2. Para cada coalizão, calcular ganho total
3. Coalizão estável se nenhum agente prefere sair
4. Usar Valores de Shapley para divisão equitativa

Aplicação: Partições de conjuntos, decomposição de estruturas
"""
        return GameTheoryAnalysis(
            reasoning_type=self.reasoning_type,
            problem_context=getattr(problem, "category", "Unknown"),
            analysis_text=analysis_text,
            key_insights=[
                "Partições estáveis existem",
                "Ganho total vs. individual",
                "Divisão justa (Shapley)"
            ],
            applicability_score=0.7,
            recommended_proof_direction="Demonstrar estabilidade da partição"
        )


class ZeroSumAnalysisReasoner(GameTheoryReasoner):
    """
    6. Zero-Sum Analysis — Ganho de um é exatamente perda de outro
    """
    reasoning_type = GameTheoryReasoningType.ZERO_SUM_ANALYSIS
    description = "Jogos onde o total é constante: ganho-perda = 0"
    
    def is_applicable(self, problem: Any) -> bool:
        problem_text = getattr(problem, "problem_statement", "").lower()
        keywords = ["zero-sum", "win-lose", "opposite", "adversarial"]
        return any(kw in problem_text for kw in keywords)
    
    def analyze(self, problem: Any, proof: Optional[str] = None) -> GameTheoryAnalysis:
        analysis_text = """
Análise de Soma-Zero:
1. Modelar ganho de um jogador = negativo do outro
2. max_P1 min_P2 payoff(P1) = Valor do Jogo
3. Teorema minimax: Valor bem-definido
4. Estratégias ótimas mistas existem

Estrutura: Matriz de payoffs anti-simétrica
"""
        return GameTheoryAnalysis(
            reasoning_type=self.reasoning_type,
            problem_context=getattr(problem, "category", "Unknown"),
            analysis_text=analysis_text,
            key_insights=[
                "Valor do jogo bem-definido",
                "Estratégias mistas podem ser necessárias",
                "Dualidade linear"
            ],
            applicability_score=0.75,
            recommended_proof_direction="Von Neumann minimax theorem"
        )


class CooperativeSolutionReasoner(GameTheoryReasoner):
    """
    7. Cooperative Solution — Soluções assumindo colaboração (Shapley value, core)
    """
    reasoning_type = GameTheoryReasoningType.COOPERATIVE_SOLUTION
    description = "Agentes colaboram e dividem ganho de forma justa"
    
    def is_applicable(self, problem: Any) -> bool:
        problem_text = getattr(problem, "problem_statement", "").lower()
        keywords = ["share", "divide", "cooperate", "fair", "allocate"]
        return any(kw in problem_text for kw in keywords)
    
    def analyze(self, problem: Any, proof: Optional[str] = None) -> GameTheoryAnalysis:
        analysis_text = """
Solução Cooperativa (Shapley):
1. Calcular valor marginal de cada agente em cada coalizão
2. Valor de Shapley = média ponderada dos valores marginais
3. Propriedades: simetria, eficiência, nulidade, aditividade
4. Core: alocações onde nenhuma coalizão prefere sair

Aplicação: Divisão justa de recursos, atribuição de crédito
"""
        return GameTheoryAnalysis(
            reasoning_type=self.reasoning_type,
            problem_context=getattr(problem, "category", "Unknown"),
            analysis_text=analysis_text,
            key_insights=[
                "Valor de Shapley é único",
                "Pode estar no core",
                "Propriedades axiomáticas"
            ],
            applicability_score=0.65,
            recommended_proof_direction="Axiomas de Shapley"
        )


class PrisonersDilemmReasoner(GameTheoryReasoner):
    """
    8. Prisoner's Dilemma — Conflito entre interesse individual e coletivo
    """
    reasoning_type = GameTheoryReasoningType.PRISONERS_DILEMMA
    description = "Incentivos levam a resultado subótimo para todos"
    
    def is_applicable(self, problem: Any) -> bool:
        problem_text = getattr(problem, "problem_statement", "").lower()
        keywords = ["tension", "conflict", "individual", "collective", "dilemma"]
        return any(kw in problem_text for kw in keywords)
    
    def analyze(self, problem: Any, proof: Optional[str] = None) -> GameTheoryAnalysis:
        analysis_text = """
Dilema do Prisioneiro:
1. Nash Equilibrium: ambos defectam (subótimo)
2. Pareto Ótimo: ambos cooperam
3. Mecanismo de resolução: repetição, punição, reputação
4. Estrutura: 4 payoffs (mutua cooperação < defecção unilateral < solo, 
   mas > ambos defectam)
"""
        return GameTheoryAnalysis(
            reasoning_type=self.reasoning_type,
            problem_context=getattr(problem, "category", "Unknown"),
            analysis_text=analysis_text,
            key_insights=[
                "Assimetria Nash vs. Pareto",
                "Repetição pode resolver",
                "Mecanismos de enforcement"
            ],
            applicability_score=0.6,
            recommended_proof_direction="Mostrar ineficiência de equilíbrio"
        )


class SymmetryBreakingReasoner(GameTheoryReasoner):
    """
    9. Symmetry Breaking — Quebrando simetria para obter vantagem estratégica
    """
    reasoning_type = GameTheoryReasoningType.SYMMETRY_BREAKING
    description = "Rompimento de simetria leva a diferenciação e vantagem"
    
    def is_applicable(self, problem: Any) -> bool:
        problem_text = getattr(problem, "problem_statement", "").lower()
        keywords = ["symmetry", "break", "distinct", "differentiate", "asymmetry"]
        return any(kw in problem_text for kw in keywords)
    
    def analyze(self, problem: Any, proof: Optional[str] = None) -> GameTheoryAnalysis:
        analysis_text = """
Quebra de Simetria Estratégica:
1. Problema simétrico: múltiplas soluções simétricas
2. Mecanismo de quebra: escolha arbitrária, focal point
3. Equilíbrio assimétrico emerge de simetria
4. Aplicação: Coordenação, Seleção de Equilíbrio

Estrutura de prova:
- Mostrar simetria original
- Introduzir mecanismo de quebra (pequena perturbação)
- Demonstrar equilíbrio assimétrico único
"""
        return GameTheoryAnalysis(
            reasoning_type=self.reasoning_type,
            problem_context=getattr(problem, "category", "Unknown"),
            analysis_text=analysis_text,
            key_insights=[
                "Pequenas diferenças amplificadas",
                "Focal points coordenam",
                "História importa"
            ],
            applicability_score=0.7,
            recommended_proof_direction="Perturbação e limite"
        )


class SymmetricEquilibriumReasoner(GameTheoryReasoner):
    """
    10. Symmetric Equilibrium — Equilíbrio onde todos os agentes usam mesma estratégia
    """
    reasoning_type = GameTheoryReasoningType.SYMMETRIC_EQUILIBRIUM
    description = "Equilíbrio onde todos agem identicamente"
    
    def is_applicable(self, problem: Any) -> bool:
        problem_text = getattr(problem, "problem_statement", "").lower()
        keywords = ["symmetric", "same", "identical", "uniform", "all equal"]
        return any(kw in problem_text for kw in keywords)
    
    def analyze(self, problem: Any, proof: Optional[str] = None) -> GameTheoryAnalysis:
        analysis_text = """
Equilíbrio Simétrico:
1. Procurar por estratégias σ* onde todos os agentes usam σ*
2. Verificar que σ* é melhor resposta contra si mesma
3. Vantagem: simetria reduz dimensionalidade
4. Prova: mostrar que desvios unilaterais não melhoram

Estrutura:
- Formular simetria (permutação invariante)
- Reduzir para problema unidimensional
- Resolver para σ* simétrico
- Verificar melhor resposta
"""
        return GameTheoryAnalysis(
            reasoning_type=self.reasoning_type,
            problem_context=getattr(problem, "category", "Unknown"),
            analysis_text=analysis_text,
            key_insights=[
                "Simetria simplifica análise",
                "Redução dimensional",
                "Verificação é direta"
            ],
            applicability_score=0.75,
            recommended_proof_direction="Verificação de estabilidade simétrica"
        )


class InformationAsymmetryReasoner(GameTheoryReasoner):
    """
    11. Information Asymmetry — Análise quando agentes têm informação diferente
    """
    reasoning_type = GameTheoryReasoningType.INFORMATION_ASYMMETRY
    description = "Um agente sabe algo que outros não sabem"
    
    def is_applicable(self, problem: Any) -> bool:
        problem_text = getattr(problem, "problem_statement", "").lower()
        keywords = ["information", "hidden", "private", "unknown", "knows"]
        return any(kw in problem_text for kw in keywords)
    
    def analyze(self, problem: Any, proof: Optional[str] = None) -> GameTheoryAnalysis:
        analysis_text = """
Informação Assimétrica:
1. Particionar o espaço de estados em informativamente conjuntos
2. Estratégia é função das informações privadas
3. Bayesian equilibrium: crença + equilíbrio consistentes
4. Sinalização: agentes revelam informação por ações

Estrutura:
- Definir estrutura de informação (quem sabe o quê)
- Análise Bayesian
- Equilíbrio de sinalização/pooling
"""
        return GameTheoryAnalysis(
            reasoning_type=self.reasoning_type,
            problem_context=getattr(problem, "category", "Unknown"),
            analysis_text=analysis_text,
            key_insights=[
                "Crenças importam",
                "Equilíbrio Bayesian",
                "Sinalização revela informação"
            ],
            applicability_score=0.65,
            recommended_proof_direction="Bayesian equilibrium consistency"
        )


class SignalingStrategyReasoner(GameTheoryReasoner):
    """
    12. Signaling Strategy — Usar ações para transmitir informação privada
    """
    reasoning_type = GameTheoryReasoningType.SIGNALING_STRATEGY
    description = "Agentes bem-informados sinalizam através de ações"
    
    def is_applicable(self, problem: Any) -> bool:
        problem_text = getattr(problem, "problem_statement", "").lower()
        keywords = ["signal", "reveal", "certify", "prove", "demonstrate"]
        return any(kw in problem_text for kw in keywords)
    
    def analyze(self, problem: Any, proof: Optional[str] = None) -> GameTheoryAnalysis:
        analysis_text = """
Estratégia de Sinalização:
1. Agente com informação privada escolhe ação observável
2. Observador infere informação da ação
3. Equilíbrio de sinalização: ação revela tipo
4. Requisito: Agentes de tipos diferentes têm diferentes preferências sobre ações

Aplicação em Prova: Demonstrar propriedade através de construção estratégica
"""
        return GameTheoryAnalysis(
            reasoning_type=self.reasoning_type,
            problem_context=getattr(problem, "category", "Unknown"),
            analysis_text=analysis_text,
            key_insights=[
                "Ações revelam tipo",
                "Custo de sinalização",
                "Separação ou pooling"
            ],
            applicability_score=0.6,
            recommended_proof_direction="Construção reveladora"
        )


class EvolutionarilyStableReasoner(GameTheoryReasoner):
    """
    13. Evolutionary Stable Strategy (ESS) — Estratégia que é robusta contra mutantes
    """
    reasoning_type = GameTheoryReasoningType.EVOLUTIONARY_STABLE
    description = "Estratégia que resiste a invasão de mutantes"
    
    def is_applicable(self, problem: Any) -> bool:
        problem_text = getattr(problem, "problem_statement", "").lower()
        keywords = ["evolve", "stable", "robust", "invasion", "mutant", "persistent"]
        return any(kw in problem_text for kw in keywords)
    
    def analyze(self, problem: Any, proof: Optional[str] = None) -> GameTheoryAnalysis:
        analysis_text = """
Estratégia Evolutivamente Estável (ESS):
1. Estratégia σ* é ESS se:
   - É melhor resposta contra população usando σ*
   - Se mutantes invadem com estratégia σ != σ*, σ* ainda domina
2. Condições matemáticas: estabilidade contra perturbações
3. Aplicação: Entender equilíbrios robustos em sistemas dinâmicos

Estrutura:
- Formular dinâmica de população
- Mostrar que σ* é ponto fixo
- Provar estabilidade local
"""
        return GameTheoryAnalysis(
            reasoning_type=self.reasoning_type,
            problem_context=getattr(problem, "category", "Unknown"),
            analysis_text=analysis_text,
            key_insights=[
                "Robustez contra invasão",
                "Equilíbrio evolucionário",
                "Dinâmica de replicador"
            ],
            applicability_score=0.7,
            recommended_proof_direction="Estabilidade de ponto fixo"
        )


class SequentialGameReasoner(GameTheoryReasoner):
    """
    14. Sequential Game — Análise de jogo onde movimentos são sequenciais (backward induction)
    """
    reasoning_type = GameTheoryReasoningType.SEQUENTIAL_GAME
    description = "Resolver jogo por indução para trás (backward induction)"
    
    def is_applicable(self, problem: Any) -> bool:
        problem_text = getattr(problem, "problem_statement", "").lower()
        keywords = ["sequence", "order", "first", "second", "move", "then"]
        return any(kw in problem_text for kw in keywords)
    
    def analyze(self, problem: Any, proof: Optional[str] = None) -> GameTheoryAnalysis:
        analysis_text = """
Jogo Sequencial (Backward Induction):
1. Estrutura: árvore de jogo com movimentos ordenados
2. Resolver do final para o começo (backward induction)
3. Em cada nó, agente escolhe ação que maximiza payoff futuro
4. Subgame perfect equilibrium: equilíbrio em cada subgame

Aplicação em IMO: Problemas com escolhas sucessivas, construções iterativas

Estrutura de prova:
- Definir espaço de ações em cada fase
- Fazer backward induction
- Concluir sobre ações do início
"""
        return GameTheoryAnalysis(
            reasoning_type=self.reasoning_type,
            problem_context=getattr(problem, "category", "Unknown"),
            analysis_text=analysis_text,
            key_insights=[
                "Resolver de trás para frente",
                "Subgame perfection",
                "Eliminação de ameaças não-críveis"
            ],
            applicability_score=0.75,
            recommended_proof_direction="Backward induction via recursão"
        )


class PotentialFunctionReasoner(GameTheoryReasoner):
    """
    15. Potential Function — Usar função potencial para provar convergência
    """
    reasoning_type = GameTheoryReasoningType.POTENTIAL_FUNCTION
    description = "Função que decresce com melhoras, garante convergência"
    
    def is_applicable(self, problem: Any) -> bool:
        problem_text = getattr(problem, "problem_statement", "").lower()
        keywords = ["convergence", "fixed point", "stable", "invariant", "potential"]
        return any(kw in problem_text for kw in keywords)
    
    def analyze(self, problem: Any, proof: Optional[str] = None) -> GameTheoryAnalysis:
        analysis_text = """
Função Potencial (Potential Function):
1. Definir função Φ: estado → número real
2. Propriedade: quando agente melhora, Φ decresce
3. Φ limitada abaixo → convergência a ciclo/ponto fixo
4. Ordinal potential para espaços discretos

Aplicação: Provar terminação de algoritmos, existência de equilíbrio

Estrutura:
- Definir Φ (geralmente soma de payoffs ou função de energria)
- Mostrar: melhora individual → Φ decresce
- Concluir: processo termina em equilíbrio
"""
        return GameTheoryAnalysis(
            reasoning_type=self.reasoning_type,
            problem_context=getattr(problem, "category", "Unknown"),
            analysis_text=analysis_text,
            key_insights=[
                "Função energia/potencial",
                "Convergência garantida",
                "Ordinal vs. cardinal"
            ],
            applicability_score=0.8,
            recommended_proof_direction="Função potencial com cota inferior"
        )


# ============================================================================
# ORCHESTRATOR: Seletor Automático de Raciocínios de Teoria dos Jogos
# ============================================================================

class GameTheoryOrchestrator:
    """Orquestrador que seleciona automaticamente quais raciocínios GT aplicar"""
    
    def __init__(self):
        """Inicializar todos os 15 raciocínios"""
        self.reasoners: Dict[GameTheoryReasoningType, GameTheoryReasoner] = {
            GameTheoryReasoningType.NASH_EQUILIBRIUM: NashEquilibriumReasoner(),
            GameTheoryReasoningType.MINIMAX_STRATEGY: MinimaxStrategyReasoner(),
            GameTheoryReasoningType.PARETO_OPTIMALITY: ParetoOptimalityReasoner(),
            GameTheoryReasoningType.DOMINANT_STRATEGY: DominantStrategyReasoner(),
            GameTheoryReasoningType.COALITION_FORMATION: CoalitionFormationReasoner(),
            GameTheoryReasoningType.ZERO_SUM_ANALYSIS: ZeroSumAnalysisReasoner(),
            GameTheoryReasoningType.COOPERATIVE_SOLUTION: CooperativeSolutionReasoner(),
            GameTheoryReasoningType.PRISONERS_DILEMMA: PrisonersDilemmReasoner(),
            GameTheoryReasoningType.SYMMETRY_BREAKING: SymmetryBreakingReasoner(),
            GameTheoryReasoningType.SYMMETRIC_EQUILIBRIUM: SymmetricEquilibriumReasoner(),
            GameTheoryReasoningType.INFORMATION_ASYMMETRY: InformationAsymmetryReasoner(),
            GameTheoryReasoningType.SIGNALING_STRATEGY: SignalingStrategyReasoner(),
            GameTheoryReasoningType.EVOLUTIONARY_STABLE: EvolutionarilyStableReasoner(),
            GameTheoryReasoningType.SEQUENTIAL_GAME: SequentialGameReasoner(),
            GameTheoryReasoningType.POTENTIAL_FUNCTION: PotentialFunctionReasoner(),
        }
    
    def select_applicable_reasonings(
        self,
        problem: Any,
        proof: Optional[str] = None,
        top_k: int = 3
    ) -> List[GameTheoryAnalysis]:
        """
        Selecionar os K melhores raciocínios de teoria dos jogos aplicáveis
        
        Args:
            problem: IMOProblem
            proof: Texto da prova (opcional)
            top_k: Quantos raciocínios retornar (default: 3)
        
        Returns:
            Lista de GameTheoryAnalysis ordenada por applicability_score
        """
        analyses = []
        
        for reasoning_type, reasoner in self.reasoners.items():
            if reasoner.is_applicable(problem):
                analysis = reasoner.analyze(problem, proof)
                analyses.append(analysis)
        
        # Ordenar por applicability_score (decrescente)
        analyses.sort(key=lambda x: x.applicability_score, reverse=True)
        
        return analyses[:top_k]
    
    def generate_recommendation_report(
        self,
        problem: Any,
        proof: Optional[str] = None
    ) -> Dict[str, Any]:
        """Gerar relatório completo de recomendações"""
        analyses = self.select_applicable_reasonings(problem, proof, top_k=15)
        
        report = {
            "problem_id": getattr(problem, "problem_id", "Unknown"),
            "category": getattr(problem, "category", "Unknown"),
            "applicable_reasonings": len(analyses),
            "top_3": [
                {
                    "reasoning_type": a.reasoning_type.value,
                    "applicability_score": a.applicability_score,
                    "recommended_direction": a.recommended_proof_direction,
                    "key_insights": a.key_insights,
                }
                for a in analyses[:3]
            ],
            "all_applicable": [
                {
                    "reasoning_type": a.reasoning_type.value,
                    "applicability_score": a.applicability_score,
                }
                for a in analyses
            ],
            "suggested_proof_strategy": f"Combine os 3 raciocínios top: {', '.join(a.reasoning_type.value for a in analyses[:3])}"
        }
        
        return report


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    from imo_benchmark_adapter import IMOProblem
    
    # Problema de exemplo
    problem = IMOProblem(
        problem_id="GT-001",
        problem_statement="""
        Two players play a game on a grid. Player 1 chooses a strategy, then Player 2 observes
        and responds optimally. Show that there exists an equilibrium strategy for Player 1
        that guarantees at least X payoff regardless of Player 2's response.
        """,
        solution="By minimax theorem and backward induction...",
        grading_guidelines="Must use game theory.",
        category="Combinatorics",
        level="IMO-hard",
        short_answer="Minimax equilibrium exists",
        source="IMO-ProofBench"
    )
    
    # Orchestrador
    orchestrator = GameTheoryOrchestrator()
    
    # Selecionar raciocínios aplicáveis
    analyses = orchestrator.select_applicable_reasonings(problem, top_k=5)
    
    print("\n[GAME THEORY ORCHESTRATOR]")
    print(f"Problem: {problem.problem_id} ({problem.category})")
    print(f"\nAplicáveis: {len(analyses)} raciocínios")
    
    for i, analysis in enumerate(analyses, 1):
        print(f"\n{i}. {analysis.reasoning_type.value}")
        print(f"   Score: {analysis.applicability_score:.2f}")
        print(f"   Direction: {analysis.recommended_proof_direction}")
        print(f"   Insights: {', '.join(analysis.key_insights[:2])}")
    
    # Relatório completo
    report = orchestrator.generate_recommendation_report(problem)
    print(f"\n[RECOMMENDATION REPORT]")
    print(json.dumps(report, indent=2, ensure_ascii=False))
