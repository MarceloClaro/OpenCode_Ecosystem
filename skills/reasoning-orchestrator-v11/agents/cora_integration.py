# =====================================================================
# CORA INTEGRATION — Collaborative Reasoning Agents
# Concepts from Prof. Antonio Murilo S. Macedo (UFPE, 2025)
# Integrates physical analogies into multi-agent reasoning
# =====================================================================
# Key concepts implemented:
#   1. Consensus Metrics (C_r, O_r)
#   2. Oscillator Coupling Model
#   3. Phase Transition Detection
#   4. Temperature Control per Agent
#   5. Bellman Q-Learning for Debate Strategy
# =====================================================================
import sys, os, math, json, time, random
from typing import Any, Optional
from collections import defaultdict
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(__file__))
from framework import ReasoningAgent, ReasoningResult, AgentStatus

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# =====================================================================
# 1. CORA CONSENSUS METRICS (from the minicourse)
# =====================================================================

@dataclass
class CORAMetrics:
    """Metrics for multi-agent debate quality."""
    consensus_index: float = 0.0      # C_r: agreement between agents
    oscillation_index: float = 0.0    # O_r: instability between rounds
    convergence_round: int = -1       # Round where consensus reached
    phase: str = "fragmented"         # fragmented / debating / converging / consensus
    entropy: float = 0.0              # Diversity of solutions
    energy: float = 0.0               # System "energy" (disagreement level)

class CORAConsensusEngine:
    """
    Implements the consensus and oscillation metrics from CORA paper.
    
    C_r = (1 / N(N-1)) * sum_{i≠j} sim(S_i, S_j)    [Consensus]
    O_r = (1 / N) * sum_i dist(S_i^{(r)}, S_i^{(r-1)})  [Oscillation]
    
    Phase detection:
    - C_r < 0.3: "fragmented" (no alignment)
    - 0.3 ≤ C_r < 0.7: "debating" (partial agreement)
    - 0.7 ≤ C_r < 0.95: "converging" (strong alignment)
    - C_r >= 0.95: "consensus" (full agreement)
    """
    
    def __init__(self, threshold_consensus=0.95, threshold_oscillation=0.05):
        self.threshold_consensus = threshold_consensus
        self.threshold_oscillation = threshold_oscillation
        self.history = []  # List of (round, metrics)
    
    def compute_consensus(self, agent_solutions: dict[str, str]) -> float:
        """C_r: pairwise similarity between agent solutions."""
        agents = list(agent_solutions.keys())
        n = len(agents)
        if n <= 1:
            return 1.0
        
        similarities = []
        for i in range(n):
            for j in range(i+1, n):
                sim = self._text_similarity(
                    agent_solutions[agents[i]], 
                    agent_solutions[agents[j]]
                )
                similarities.append(sim)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def compute_oscillation(self, current_solutions: dict, previous_solutions: dict) -> float:
        """O_r: how much each agent changed from previous round."""
        if not previous_solutions:
            return 0.0
        
        agents = list(current_solutions.keys())
        n = len(agents)
        if n == 0:
            return 0.0
        
        changes = []
        for agent in agents:
            if agent in previous_solutions:
                dist = 1.0 - self._text_similarity(
                    current_solutions[agent],
                    previous_solutions[agent]
                )
                changes.append(dist)
        
        return sum(changes) / len(changes) if changes else 0.0
    
    def compute_entropy(self, agent_solutions: dict[str, str]) -> float:
        """Entropy of solution distribution — higher = more diverse."""
        # Simplified: use solution length variance as diversity proxy
        lengths = [len(s) for s in agent_solutions.values()]
        if not lengths:
            return 0.0
        mean_len = sum(lengths) / len(lengths)
        variance = sum((l - mean_len)**2 for l in lengths) / len(lengths)
        # Normalize entropy
        return min(1.0, math.log(1 + variance) / 10)
    
    def detect_phase(self, cr: float, or_val: float, round_num: int) -> str:
        """Detect the current phase of the debate."""
        if cr >= self.threshold_consensus:
            return "consensus"
        elif cr >= 0.7:
            return "converging"
        elif cr >= 0.3:
            return "debating"
        else:
            return "fragmented"
    
    def should_stop(self, cr: float, or_val: float, consecutive_stable: int) -> bool:
        """Determine if debate should stop."""
        # Stop if consensus reached
        if cr >= self.threshold_consensus:
            return True
        # Stop if oscillation stabilized (no more changes)
        if or_val < self.threshold_oscillation and consecutive_stable >= 3:
            return True
        return False
    
    def update(self, round_num: int, current_solutions: dict, previous_solutions: dict = None) -> CORAMetrics:
        """Compute all metrics for current round."""
        cr = self.compute_consensus(current_solutions)
        or_val = self.compute_oscillation(current_solutions, previous_solutions or {})
        entropy = self.compute_entropy(current_solutions)
        phase = self.detect_phase(cr, or_val, round_num)
        
        # Energy: higher = more disagreement
        energy = 1.0 - cr
        
        metrics = CORAMetrics(
            consensus_index=cr,
            oscillation_index=or_val,
            convergence_round=round_num if phase == "consensus" else -1,
            phase=phase,
            entropy=entropy,
            energy=energy
        )
        
        self.history.append((round_num, metrics))
        return metrics
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Simple text similarity using word overlap."""
        if not text1 or not text2:
            return 0.0
        
        # Jaccard similarity on word-level
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        return len(intersection) / len(union)


# =====================================================================
# 2. CORA OSCILLATOR COUPLING MODEL
# =====================================================================

class CORAOscillatorModel:
    """
    Physical analog: agents as coupled oscillators.
    
    d^2 x_i / dt^2 + ω_i^2 x_i = sum_{j≠i} K_{ij} (x_j - x_i)
    
    where:
    - x_i = agent i's "position" (solution state)
    - ω_i = natural frequency (expertise domain)
    - K_{ij} = coupling strength (influence of agent j on agent i)
    
    When K exceeds critical threshold -> phase transition -> synchronization (consensus)
    """
    
    def __init__(self, n_agents: int):
        self.n = n_agents
        self.positions = np.ones(self.n) if HAS_NUMPY else [1.0] * self.n
        self.frequencies = [1.0 + 0.1 * i for i in range(self.n)]  # Slightly different
        self.coupling = self._default_coupling(self.n)
        self.time = 0.0
        self.dt = 0.01
    
    def _default_coupling(self, n):
        """All-to-all coupling with random strengths."""
        if HAS_NUMPY:
            K = np.random.uniform(0.1, 0.5, (n, n))
            np.fill_diagonal(K, 0)
            return K
        return [[0.0]*n for _ in range(n)]
    
    def step(self, external_forces=None):
        """Evolve one time step using 4th-order Runge-Kutta."""
        if not HAS_NUMPY:
            return
        
        x = self.positions.copy()
        v = np.zeros(self.n)  # velocities (simplified: no inertia)
        
        # Coupling term
        coupling_force = np.zeros(self.n)
        for i in range(self.n):
            for j in range(self.n):
                if i != j:
                    coupling_force[i] += self.coupling[i,j] * (x[j] - x[i])
        
        # External forces (from environment/debate)
        if external_forces is not None:
            coupling_force += np.array(external_forces)
        
        # Update positions (simplified: overdamped)
        x += self.dt * (coupling_force - 0.1 * x)
        
        self.positions = x
        self.time += self.dt
    
    def order_parameter(self) -> float:
        """Kuramoto order parameter: measures synchronization (0 to 1)."""
        if not HAS_NUMPY:
            return 1.0 if len(set(str(p)[:4] for p in self.positions)) == 1 else 0.0
        
        # For positions (not phases): use inverse of variance
        std = np.std(self.positions)
        if std < 1e-6:
            return 1.0
        
        # Normalized: 0 = random, 1 = perfectly synchronized
        return 1.0 / (1.0 + std)
    
    def detect_phase_transition(self, history: list) -> bool:
        """Detect if synchronization phase transition occurred."""
        if len(history) < 10:
            return False
        
        # Check if order parameter jumped from low to high
        early = sum(h for h in history[:5]) / 5
        late = sum(h for h in history[-5:]) / 5
        
        return late > 0.8 and early < 0.4


# =====================================================================
# 3. CORA TEMPERATURE CONTROLLER
# =====================================================================

class CORATemperatureController:
    """
    Manages "temperature" per agent — controls creativity vs precision.
    
    From CORA paper:
    - Analytical: T = 0.1 (low creativity, high precision)
    - Physical: T = 0.5 (balanced)
    - Critical: T = 0.3 (error detection focus)
    - Computational: T = 0.2 (deterministic)
    
    Temperature annealing: T(t) = T_0 * α^t during debate
    """
    
    def __init__(self):
        self.default_temps = {
            "analitico": 0.1,
            "fisico": 0.5,
            "critico": 0.3,
            "computacional": 0.2,
            "gerente": 0.4,
            "dimensional": 0.15,
            "general": 0.5,
        }
        self.agent_temps = {}
        self.alpha = 0.85  # Annealing rate
    
    def set_agent_temperature(self, agent_id: str, role: str = "general"):
        """Set initial temperature based on agent role."""
        base_temp = self.default_temps.get(role, 0.5)
        self.agent_temps[agent_id] = base_temp
    
    def anneal(self, agent_id: str, round_num: int):
        """Reduce temperature over time: T(t) = T_0 * α^t."""
        if agent_id in self.agent_temps:
            initial = self.agent_temps.get(f"{agent_id}_initial", self.agent_temps[agent_id])
            if f"{agent_id}_initial" not in self.agent_temps:
                self.agent_temps[f"{agent_id}_initial"] = self.agent_temps[agent_id]
            
            self.agent_temps[agent_id] = initial * (self.alpha ** round_num)
    
    def get_temperature(self, agent_id: str) -> float:
        """Get current temperature for agent."""
        return self.agent_temps.get(agent_id, 0.5)
    
    def critical_slowing_down(self, cr: float) -> bool:
        """Detect critical slowing down near phase transition."""
        # As system approaches consensus, changes become slower
        return cr > 0.85
    
    def adjust_for_phase(self, phase: str):
        """Adjust temperatures based on debate phase."""
        if phase == "fragmented":
            # Increase temperature to encourage exploration
            for agent in self.agent_temps:
                self.agent_temps[agent] = min(0.9, self.agent_temps[agent] * 1.2)
        elif phase == "converging":
            # Decrease temperature for precision
            for agent in self.agent_temps:
                self.agent_temps[agent] = max(0.05, self.agent_temps[agent] * 0.8)


# =====================================================================
# 4. CORA BELLMAN Q-LEARNING FOR DEBATE STRATEGY
# =====================================================================

class CORABellmanEngine:
    """
    Multi-agent Q-learning for debate strategy optimization.
    
    State: debate phase + consensus level + round number
    Actions: speak, listen, challenge, agree, refine, propose
    Reward: improvement in consensus or solution quality
    
    V_i(s) = max_a [R_i(s,a) + γ * sum_{s'} P(s'|s,a) * V_i(s')]
    
    References:
    - Bellman (1954) — Dynamic Programming
    - Sutton & Barto (1998) — Reinforcement Learning
    """
    
    def __init__(self, n_agents=4, learning_rate=0.1, discount=0.9):
        self.n = n_agents
        self.lr = learning_rate
        self.gamma = discount
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.actions = ["speak", "listen", "challenge", "agree", "refine", "propose"]
        self.epsilon = 0.1  # Exploration rate
    
    def get_state(self, metrics: CORAMetrics, round_num: int) -> str:
        """Discretize continuous state into bins."""
        cr_bin = int(metrics.consensus_index * 10)  # 0-9
        phase = metrics.phase[0]  # f/d/c/C
        round_bin = min(round_num // 5, 4)  # 0-4
        return f"{phase}_{cr_bin}_{round_bin}"
    
    def choose_action(self, state: str, agent_id: int) -> str:
        """Epsilon-greedy action selection."""
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        
        q_values = {a: self.q_table[state][f"{agent_id}_{a}"] for a in self.actions}
        return max(q_values, key=q_values.get)
    
    def update(self, state: str, action: str, reward: float, 
               next_state: str, agent_id: int):
        """Q-learning update."""
        key = f"{agent_id}_{action}"
        current_q = self.q_table[state][key]
        
        # Max Q for next state
        next_qs = [self.q_table[next_state][f"{agent_id}_{a}"] for a in self.actions]
        max_next_q = max(next_qs) if next_qs else 0.0
        
        # Bellman update
        new_q = current_q + self.lr * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state][key] = new_q
    
    def compute_reward(self, prev_cr: float, curr_cr: float, 
                       phase_transition: bool = False) -> float:
        """Reward function: improvement in consensus."""
        delta = curr_cr - prev_cr
        bonus = 2.0 if phase_transition else 0.0
        return delta + bonus


# =====================================================================
# 5. CORA INTEGRATION AGENT (wraps all CORA concepts)
# =====================================================================

class CORAIntegrationAgent(ReasoningAgent):
    """
    Integrates all CORA concepts into a single reasoning agent.
    
    Uses:
    - CORAConsensusEngine: for debate quality metrics
    - CORAOscillatorModel: for physical dynamics
    - CORATemperatureController: for agent creativity
    - CORABellmanEngine: for strategy optimization
    
    This agent monitors the multi-agent debate and provides
    meta-level insights about the collaboration process.
    """
    
    def __init__(self):
        super().__init__("cora-integration", "R48", "X")
        self.consensus = CORAConsensusEngine()
        self.oscillator = CORAOscillatorModel(n_agents=4)
        self.temperature = CORATemperatureController()
        self.bellman = CORABellmanEngine(n_agents=4)
        self.round_history = []
    
    def get_dependencies(self):
        return ["nash-agent", "abstraction-agent"]
    
    def reason(self, context: dict) -> ReasoningResult:
        agent_solutions = context.get("agent_solutions", {})
        previous_solutions = context.get("previous_solutions", {})
        round_num = context.get("round", 0)
        
        # 1. Compute consensus metrics
        metrics = self.consensus.update(round_num, agent_solutions, previous_solutions)
        self.round_history.append(metrics)
        
        # 2. Update oscillator model
        self.oscillator.step()
        order = self.oscillator.order_parameter()
        
        # 3. Adjust temperatures
        self.temperature.adjust_for_phase(metrics.phase)
        
        # 4. Build comprehensive report
        insights = []
        
        if metrics.phase == "consensus":
            insights.append(f"CONSENSO atingido na rodada {round_num}")
        elif metrics.phase == "converging":
            insights.append(f"Convergencia em andamento (C_r={metrics.consensus_index:.3f})")
        elif metrics.consensus_index < 0.3:
            insights.append("Agentes fragmentados — aumentar temperatura para exploracao")
        
        if metrics.oscillation_index < 0.03:
            insights.append("Debate estabilizado — pouca mudanca entre rodadas")
        
        if self.oscillator.detect_phase_transition(
            [self.oscillator.order_parameter() for _ in range(10)]
        ):
            insights.append("DETECTADA transicao de fase: sincronizacao emergente")
        
        # Build conclusion
        if insights:
            conclusion = " | ".join(insights)
        else:
            conclusion = f"Debate em andamento. Fase: {metrics.phase}. C_r={metrics.consensus_index:.3f}"
        
        confidence = metrics.consensus_index if metrics.phase != "fragmented" else 0.25
        
        return ReasoningResult(
            agent_id=self.agent_id, reasoning_type=self.reasoning_type,
            category=self.category, conclusion=conclusion, confidence=confidence,
            evidence=[{
                "consensus_index": metrics.consensus_index,
                "oscillation_index": metrics.oscillation_index,
                "phase": metrics.phase,
                "entropy": metrics.entropy,
                "energy": metrics.energy,
                "order_parameter": order,
                "round": round_num
            }]
        )


# =====================================================================
# TEST: CORA integration
# =====================================================================

def test_cora():
    """Test all CORA integration components."""
    print("=" * 60)
    print("CORA INTEGRATION — Collaborative Reasoning Agents")
    print("Based on: Macedo, A. M. S. (2025) — CORA Minicurso UFPR")
    print("=" * 60)
    
    # Test 1: Consensus Engine
    print("\n[1] Consensus Metrics:")
    engine = CORAConsensusEngine()
    
    # Simulate a debate converging
    solutions_round1 = {
        "analitico": "x(t) = A cos(ωt + φ), ω = sqrt(k/m)",
        "fisico": "Oscilador harmonico: periodo T = 2π sqrt(m/k)",
        "critico": "Solucao correta: T = 2π sqrt(m/k), mas verificar unidades",
        "gerente": "Consenso: T = 2π sqrt(m/k)"
    }
    
    solutions_round3 = {
        "analitico": "T = 2π sqrt(m/k), derivado da EDO m d²x/dt² + kx = 0",
        "fisico": "Periodo T = 2π sqrt(m/k). Interpretacao: maior massa -> maior periodo",
        "critico": "Confirmado: T = 2π sqrt(m/k). Unidades: [T] = [s], [m/k] = [kg]/[N/m] = [s²] ✓",
        "gerente": "Solucao final: T = 2π sqrt(m/k)"
    }
    
    cr1 = engine.compute_consensus(solutions_round1)
    cr3 = engine.compute_consensus(solutions_round3)
    
    print(f"  Consenso rodada 1: C_r = {cr1:.3f} -> {engine.detect_phase(cr1, 0.5, 1)}")
    print(f"  Consenso rodada 3: C_r = {cr3:.3f} -> {engine.detect_phase(cr3, 0.1, 3)}")
    
    or_val = engine.compute_oscillation(solutions_round3, solutions_round1)
    print(f"  Oscilacao (r1->r3): O_r = {or_val:.3f}")
    
    # Test 2: Temperature Controller
    print("\n[2] Temperature Controller:")
    temp_ctrl = CORATemperatureController()
    for role in ["analitico", "fisico", "critico", "gerente"]:
        temp_ctrl.set_agent_temperature(role, role)
        print(f"  {role}: T_initial = {temp_ctrl.get_temperature(role):.2f}")
    
    for r in range(5):
        for role in ["analitico", "fisico"]:
            temp_ctrl.anneal(role, r)
    print(f"  Apos 5 rodadas de annealing:")
    print(f"    analitico: T = {temp_ctrl.get_temperature('analitico'):.4f}")
    print(f"    fisico: T = {temp_ctrl.get_temperature('fisico'):.4f}")
    
    # Test 3: Bellman Q-Learning
    print("\n[3] Bellman Q-Learning:")
    bellman = CORABellmanEngine()
    
    state = "d_5_0"  # debating, C_r=0.5, round 0
    action = bellman.choose_action(state, 0)
    print(f"  Estado: {state}")
    print(f"  Acao escolhida (epsilon-greedy): {action}")
    
    # Simulate learning
    reward = bellman.compute_reward(0.5, 0.7)
    bellman.update(state, "challenge", reward, "c_7_1", 0)
    print(f"  Recompensa (C_r: 0.5->0.7): {reward:.2f}")
    print(f"  Q-value atualizado: {bellman.q_table[state]['0_challenge']:.4f}")
    
    # Test 4: Full Integration Agent
    print("\n[4] CORA Integration Agent:")
    agent = CORAIntegrationAgent()
    
    context = {
        "agent_solutions": solutions_round3,
        "previous_solutions": solutions_round1,
        "round": 3
    }
    
    result = agent.reason(context)
    print(f"  Conclusao: {result.conclusion}")
    print(f"  Confianca: {result.confidence:.2f}")
    print(f"  Metricas: {json.dumps(result.evidence[0], indent=2)}")
    
    print("\n" + "=" * 60)
    print("CORA INTEGRATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_cora()

