# =====================================================================
# GAME THEORY AGENTS — Robust, refinable, functional
# Nash equilibrium, Minimax, Backward Induction, Shapley, Evolutionary
# =====================================================================
# References:
#   Nash (1950) — Equilibrium Points in n-Person Games (PNAS)
#   von Neumann & Morgenstern (1944) — Theory of Games and Economic Behavior
#   Selten (1965) — Subgame Perfect Equilibrium
#   Shapley (1953) — A Value for n-Person Games
#   Smith & Price (1973) — Evolutionarily Stable Strategies
# =====================================================================
import sys, os, math, itertools, json
from typing import Any, Optional
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from framework import ReasoningAgent, ReasoningResult

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# =====================================================================
# GAME THEORY ENGINE — Core computation functions
# =====================================================================

class GameTheoryEngine:
    """Pure computation engine for game theory — no LLM dependency."""
    
    @staticmethod
    def find_pure_nash(payoff_matrix_1, payoff_matrix_2=None):
        """
        Find pure Nash equilibria in a 2-player game.
        payoff_matrix_1[i][j] = payoff to player 1 when P1 plays i, P2 plays j
        """
        rows = len(payoff_matrix_1)
        cols = len(payoff_matrix_1[0])
        
        if payoff_matrix_2 is None:
            # Zero-sum: P2 payoff = -P1 payoff
            payoff_matrix_2 = [[-v for v in row] for row in payoff_matrix_1]
        
        equilibria = []
        for i in range(rows):
            for j in range(cols):
                # Check: is i best response to j?
                p1_best = True
                for i2 in range(rows):
                    if payoff_matrix_1[i2][j] > payoff_matrix_1[i][j]:
                        p1_best = False
                        break
                
                # Check: is j best response to i?
                p2_best = True
                for j2 in range(cols):
                    if payoff_matrix_2[i][j2] > payoff_matrix_2[i][j]:
                        p2_best = False
                        break
                
                if p1_best and p2_best:
                    equilibria.append((i, j, payoff_matrix_1[i][j], payoff_matrix_2[i][j]))
        
        return equilibria
    
    @staticmethod
    def find_mixed_nash(matrix_2x2):
        """Find mixed Nash for 2x2 games analytically."""
        a, b = matrix_2x2[0]
        c, d = matrix_2x2[1]
        
        # Player 1's mixed strategy: (p, 1-p)
        # Player 2's mixed strategy: (q, 1-q)
        
        denom = a - b - c + d
        if abs(denom) < 1e-10:
            return None  # Degenerate
        
        q = (d - b) / denom  # P2 plays column 0 with prob q
        p = (d - c) / denom  # P1 plays row 0 with prob p
        
        # Clip to [0,1]
        if 0 <= p <= 1 and 0 <= q <= 1:
            expected_payoff = a*p*q + b*p*(1-q) + c*(1-p)*q + d*(1-p)*(1-q)
            return {
                "p1_strategy": [p, 1-p],
                "p2_strategy": [q, 1-q],
                "expected_payoff": expected_payoff,
                "type": "mixed_nash"
            }
        return None
    
    @staticmethod
    def solve_zero_sum(matrix):
        """Minimax solution for zero-sum game using linear programming approach."""
        if not HAS_NUMPY:
            return GameTheoryEngine._minimax_simple(matrix)
        
        mat = np.array(matrix, dtype=float)
        rows, cols = mat.shape
        
        # Use linear programming to find maximin strategy
        # For player 1 (row): maximize v subject to sum_j p_j * a_ij >= v for all i
        # This is equivalent to solving via fictitious play
        
        # Simplified: use iterative method (fictitious play)
        p1_strat = np.ones(rows) / rows
        p2_strat = np.ones(cols) / cols
        
        for _ in range(1000):
            # Player 2 best response to P1
            p2_payoffs = mat.T @ p1_strat
            best_j = np.argmin(p2_payoffs)
            p2_strat = 0.95 * p2_strat + 0.05 * np.eye(cols)[best_j]
            
            # Player 1 best response to P2
            p1_payoffs = mat @ p2_strat
            best_i = np.argmax(p1_payoffs)
            p1_strat = 0.95 * p1_strat + 0.05 * np.eye(rows)[best_i]
        
        value = p1_strat @ mat @ p2_strat
        
        return {
            "p1_strategy": p1_strat.tolist(),
            "p2_strategy": p2_strat.tolist(),
            "game_value": float(value),
            "type": "zero_sum_minimax"
        }
    
    @staticmethod
    def _minimax_simple(matrix):
        """Simple minimax without numpy."""
        rows, cols = len(matrix), len(matrix[0])
        row_mins = [min(row) for row in matrix]
        col_maxs = [max(matrix[i][j] for i in range(rows)) for j in range(cols)]
        maximin = max(row_mins)
        minimax = min(col_maxs)
        
        return {
            "maximin_value": maximin,
            "minimax_value": minimax,
            "saddle_point": maximin == minimax,
            "type": "zero_sum_simple"
        }
    
    @staticmethod
    def backward_induction(game_tree):
        """Solve sequential game via backward induction (subgame perfect)."""
        # game_tree: recursive dict with "player", "payoffs", "children"
        def solve(node):
            if "payoffs" in node:
                return node["payoffs"]
            
            player = node["player"]
            children = node["children"]
            
            child_payoffs = [solve(child) for child in children]
            
            if player == 1:
                # P1 maximizes
                best_idx = max(range(len(child_payoffs)), 
                              key=lambda i: child_payoffs[i][0])
            else:
                # P2 minimizes P1 (zero-sum) or maximizes own
                best_idx = max(range(len(child_payoffs)),
                              key=lambda i: child_payoffs[i][1])
            
            return child_payoffs[best_idx], best_idx
        
        result, path = solve(game_tree)
        return {
            "subgame_perfect_payoffs": result,
            "optimal_path": path,
            "type": "backward_induction"
        }
    
    @staticmethod
    def shapley_value(coalition_values, players):
        """Compute Shapley value for cooperative game."""
        n = len(players)
        shapley = {p: 0.0 for p in players}
        
        for player in players:
            others = [p for p in players if p != player]
            for r in range(n):
                for subset in itertools.combinations(others, r):
                    coalition = tuple(sorted(subset))
                    coalition_with = tuple(sorted(list(subset) + [player]))
                    
                    marginal = coalition_values.get(coalition_with, 0) - coalition_values.get(coalition, 0)
                    weight = math.factorial(r) * math.factorial(n - r - 1) / math.factorial(n)
                    shapley[player] += weight * marginal
        
        return {"shapley_values": shapley, "type": "shapley", "efficiency": sum(shapley.values())}
    
    @staticmethod
    def replicator_dynamics(payoff_matrix, initial_pop, steps=100):
        """Simulate replicator dynamics for evolutionary game theory."""
        if not HAS_NUMPY:
            return None
        
        pop = np.array(initial_pop, dtype=float)
        pop = pop / pop.sum()
        mat = np.array(payoff_matrix, dtype=float)
        
        history = [pop.tolist()]
        
        for _ in range(steps):
            fitness = mat @ pop
            avg_fitness = pop @ fitness
            if avg_fitness > 0:
                pop = pop * fitness / avg_fitness
            pop = np.clip(pop, 0, 1)
            if pop.sum() > 0:
                pop = pop / pop.sum()
            history.append(pop.tolist())
        
        # Check for ESS (Evolutionarily Stable Strategy)
        final = history[-1]
        max_idx = np.argmax(final)
        
        return {
            "final_population": final,
            "dominant_strategy": int(max_idx),
            "converged": max(final) > 0.95,
            "history": history[::10],  # Every 10th step
            "type": "replicator_dynamics"
        }


# =====================================================================
# GAME THEORY AGENTS
# =====================================================================

class NashEquilibriumAgent(ReasoningAgent):
    """R48: Compute pure and mixed Nash equilibria."""
    
    def __init__(self):
        super().__init__("nash-agent", "R48", "X")
        self.engine = GameTheoryEngine()
    
    def get_dependencies(self):
        return []
    
    def reason(self, context: dict) -> ReasoningResult:
        payoff_p1 = context.get("payoff_matrix_p1")
        payoff_p2 = context.get("payoff_matrix_p2")
        
        if not payoff_p1:
            return ReasoningResult(
                agent_id=self.agent_id, reasoning_type=self.reasoning_type,
                category=self.category, conclusion="Matriz de payoff nao fornecida.",
                confidence=0.0
            )
        
        # Pure Nash
        pure = self.engine.find_pure_nash(payoff_p1, payoff_p2)
        
        # Mixed Nash (for 2x2)
        mixed = None
        if len(payoff_p1) == 2 and len(payoff_p1[0]) == 2:
            mixed = self.engine.find_mixed_nash(payoff_p1)
        
        results = {"pure_equilibria": pure, "mixed_equilibrium": mixed}
        
        if pure:
            conclusion = f"{len(pure)} equilibrio(s) de Nash puro(s): {[(e[0],e[1]) for e in pure]}"
            conf = 0.90
        elif mixed:
            conclusion = f"Nenhum equilibrio puro. Equilibrio misto: P1={[round(x,3) for x in mixed['p1_strategy']]}"
            conf = 0.80
        else:
            conclusion = "Nenhum equilibrio encontrado (verificar matriz)."
            conf = 0.30
        
        return ReasoningResult(
            agent_id=self.agent_id, reasoning_type=self.reasoning_type,
            category=self.category, conclusion=conclusion, confidence=conf,
            evidence=[results]
        )


class MinimaxAgent(ReasoningAgent):
    """Zero-sum game solver with minimax."""
    
    def __init__(self):
        super().__init__("minimax-agent", "R48b", "X")
        self.engine = GameTheoryEngine()
    
    def get_dependencies(self):
        return []
    
    def reason(self, context: dict) -> ReasoningResult:
        matrix = context.get("zero_sum_matrix")
        
        if not matrix:
            # Default: Prisoner's Dilemma isn't zero-sum
            # Use Matching Pennies as test
            matrix = [[1, -1], [-1, 1]]
        
        result = self.engine.solve_zero_sum(matrix)
        
        if result.get("saddle_point") or result.get("game_value") is not None:
            value = result.get("game_value", result.get("maximin_value", 0))
            conclusion = f"Valor do jogo: {value:.3f}. Solucao minimax encontrada."
            conf = 0.85
        else:
            conclusion = "Sem ponto de sela. Estrategia mista necessaria."
            conf = 0.50
        
        return ReasoningResult(
            agent_id=self.agent_id, reasoning_type=self.reasoning_type,
            category=self.category, conclusion=conclusion, confidence=conf,
            evidence=[result]
        )


class BackwardInductionAgent(ReasoningAgent):
    """Sequential game solver — subgame perfect equilibrium."""
    
    def __init__(self):
        super().__init__("backward-induction-agent", "R48c", "X")
        self.engine = GameTheoryEngine()
    
    def get_dependencies(self):
        return []
    
    def reason(self, context: dict) -> ReasoningResult:
        game_tree = context.get("game_tree")
        
        if not game_tree:
            # Default: simple ultimatum game
            game_tree = {
                "player": 1,
                "children": [
                    {"player": 2, "children": [
                        {"payoffs": [8, 2]},  # P2 accepts
                        {"payoffs": [0, 0]}   # P2 rejects
                    ]}
                ]
            }
        
        result = self.engine.backward_induction(game_tree)
        
        conclusion = (f"Equilibrio perfeito em subjogos: payoffs={result['subgame_perfect_payoffs']}. "
                     f"Caminho otimo: {result['optimal_path']}")
        
        return ReasoningResult(
            agent_id=self.agent_id, reasoning_type=self.reasoning_type,
            category=self.category, conclusion=conclusion, confidence=0.88,
            evidence=[result]
        )


class ShapleyValueAgent(ReasoningAgent):
    """Cooperative game theory — fair division."""
    
    def __init__(self):
        super().__init__("shapley-agent", "R48d", "X")
        self.engine = GameTheoryEngine()
    
    def get_dependencies(self):
        return []
    
    def reason(self, context: dict) -> ReasoningResult:
        coalition_values = context.get("coalition_values")
        players = context.get("players")
        
        if not coalition_values or not players:
            # Default: 3-player majority game
            players = ["A", "B", "C"]
            coalition_values = {
                (): 0,
                ("A",): 0, ("B",): 0, ("C",): 0,
                ("A", "B"): 1, ("A", "C"): 1, ("B", "C"): 1,
                ("A", "B", "C"): 1
            }
        
        result = self.engine.shapley_value(coalition_values, players)
        
        values = result["shapley_values"]
        conclusion = f"Valores de Shapley: { {k: round(v,3) for k,v in values.items()} }. Eficiencia: {result['efficiency']:.3f}"
        
        return ReasoningResult(
            agent_id=self.agent_id, reasoning_type=self.reasoning_type,
            category=self.category, conclusion=conclusion, confidence=0.90,
            evidence=[result]
        )


class EvolutionaryGameAgent(ReasoningAgent):
    """Evolutionary game theory — replicator dynamics, ESS."""
    
    def __init__(self):
        super().__init__("evolutionary-agent", "R48e", "X")
        self.engine = GameTheoryEngine()
    
    def get_dependencies(self):
        return []
    
    def reason(self, context: dict) -> ReasoningResult:
        payoff_matrix = context.get("payoff_matrix")
        initial = context.get("initial_population")
        
        if not payoff_matrix:
            # Default: Hawk-Dove game
            payoff_matrix = [[0, 3], [1, 2]]  # Hawk-Dove
            initial = [0.5, 0.5]
        
        result = self.engine.replicator_dynamics(payoff_matrix, initial)
        
        if result and result["converged"]:
            strategy = result["dominant_strategy"]
            conclusion = f"Populacao convergiu para estrategia {strategy} (ESS candidate)."
            conf = 0.82
        elif result:
            conclusion = f"Populacao em equilibrio misto: {[round(x,3) for x in result['final_population']]}"
            conf = 0.70
        else:
            conclusion = "Simulacao nao disponivel (numpy requerido)."
            conf = 0.10
        
        return ReasoningResult(
            agent_id=self.agent_id, reasoning_type=self.reasoning_type,
            category=self.category, conclusion=conclusion, confidence=conf,
            evidence=[result] if result else []
        )


# =====================================================================
# INTEGRATED GAME THEORY ORCHESTRATOR
# =====================================================================

class GameTheoryOrchestrator:
    """Runs all game theory agents on a problem and synthesizes results."""
    
    def __init__(self):
        self.agents = {
            "nash": NashEquilibriumAgent(),
            "minimax": MinimaxAgent(),
            "backward": BackwardInductionAgent(),
            "shapley": ShapleyValueAgent(),
            "evolutionary": EvolutionaryGameAgent(),
        }
    
    def analyze(self, game_spec: dict) -> dict:
        """Run full game theory analysis."""
        results = {}
        
        for name, agent in self.agents.items():
            result = agent.reason({"problem": game_spec, **game_spec})
            results[name] = {
                "conclusion": result.conclusion,
                "confidence": result.confidence,
                "evidence": result.evidence
            }
        
        # Synthesize
        conflicts = []
        if results["nash"]["confidence"] > 0.7 and results["minimax"]["confidence"] > 0.7:
            ne = results["nash"]["evidence"]
            mm = results["minimax"]["evidence"]
            # Check consistency
            if ne and mm:
                pass  # Could compare values
        
        return {
            "agent_results": results,
            "conflicts": conflicts,
            "synthesis": self._synthesize(results)
        }
    
    def _synthesize(self, results):
        confidences = [r["confidence"] for r in results.values()]
        avg_conf = sum(confidences) / len(confidences) if confidences else 0
        
        if avg_conf > 0.8:
            return "Alta confianca na analise de teoria dos jogos."
        elif avg_conf > 0.5:
            return "Confianca moderada — alguns agentes requerem mais dados."
        else:
            return "Baixa confianca — fornecer matrizes de payoff para melhorar."


# =====================================================================
# TEST: Classic game theory scenarios
# =====================================================================

def test_game_theory():
    """Test all game theory agents on classic scenarios."""
    orchestrator = GameTheoryOrchestrator()
    
    print("=" * 60)
    print("GAME THEORY AGENTS — TEST SUITE")
    print("=" * 60)
    
    # Test 1: Prisoner's Dilemma
    print("\n[TEST 1] Prisoner's Dilemma")
    pd = {
        "payoff_matrix_p1": [[3, 0], [5, 1]],  # T>R>P>S
        "payoff_matrix_p2": [[3, 5], [0, 1]],
        "zero_sum_matrix": None,
    }
    result = NashEquilibriumAgent().reason({"problem": pd, **pd})
    print(f"  Nash: {result.conclusion} (conf={result.confidence:.2f})")
    
    # Test 2: Matching Pennies (zero-sum)
    print("\n[TEST 2] Matching Pennies (Zero-Sum)")
    mp = {"zero_sum_matrix": [[1, -1], [-1, 1]]}
    result = MinimaxAgent().reason({"problem": mp, **mp})
    print(f"  Minimax: {result.conclusion} (conf={result.confidence:.2f})")
    
    # Test 3: Shapley value
    print("\n[TEST 3] Shapley Value (3-player majority)")
    result = ShapleyValueAgent().reason({"problem": {}})
    print(f"  Shapley: {result.conclusion} (conf={result.confidence:.2f})")
    
    # Test 4: Evolutionary (Hawk-Dove)
    print("\n[TEST 4] Hawk-Dove Evolutionary Game")
    result = EvolutionaryGameAgent().reason({"problem": {}})
    print(f"  Evolutionary: {result.conclusion} (conf={result.confidence:.2f})")
    
    # Test 5: Backward Induction
    print("\n[TEST 5] Backward Induction (Ultimatum Game)")
    result = BackwardInductionAgent().reason({"problem": {}})
    print(f"  Backward: {result.conclusion} (conf={result.confidence:.2f})")
    
    # Full orchestrator
    print("\n" + "=" * 60)
    print("FULL GAME THEORY ORCHESTRATOR")
    print("=" * 60)
    full = orchestrator.analyze(pd)
    print(f"  Synthesis: {full['synthesis']}")
    for name, r in full["agent_results"].items():
        print(f"  {name}: {r['conclusion'][:60]}...")

if __name__ == "__main__":
    test_game_theory()
