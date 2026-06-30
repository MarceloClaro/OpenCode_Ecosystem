# -*- coding: utf-8 -*-
"""
TDD Test Suite: D26 — Computação Quântica & Mecânica Quântica (N1 a N4)
CORA-Eval Benchmark Tasks: D26-N1-01 a D26-N4-01
Implementa simulação vetorial de estados de qubits, portas lógicas e emaranhamento.
"""

import math
import cmath
from typing import List, Tuple

# Representação de estados quânticos de 1 qubit: [alpha, beta]
State1Q = Tuple[complex, complex]
# Representação de estados quânticos de 2 qubits: [c00, c01, c10, c11]
State2Q = Tuple[complex, complex, complex, complex]

# ══════════════════════════════════════════════════════════════════════
# MOTORES LÓGICOS QUÂNTICOS (SIMULADOR DE VETOR DE ESTADO)
# ══════════════════════════════════════════════════════════════════════

def is_normalized(state: List[complex], tol: float = 1e-6) -> bool:
    """Verifica se a soma das probabilidades de medição do estado é unitária."""
    prob_sum = sum(abs(c)**2 for c in state)
    return abs(prob_sum - 1.0) < tol

def apply_gate_1q(state: State1Q, gate: List[List[complex]]) -> State1Q:
    """Aplica uma porta quântica de 1 qubit (matriz 2x2) ao estado."""
    a, b = state
    c0 = gate[0][0]*a + gate[0][1]*b
    c1 = gate[1][0]*a + gate[1][1]*b
    return (c0, c1)

def tensor_product(state_a: State1Q, state_b: State1Q) -> State2Q:
    """Calcula o produto tensorial de dois estados de 1 qubit (a ⊗ b)."""
    a0, a1 = state_a
    b0, b1 = state_b
    return (
        a0 * b0,  # |00>
        a0 * b1,  # |01>
        a1 * b0,  # |10>
        a1 * b1   # |11>
    )

def apply_hadamard_2q_target1(state: State2Q) -> State2Q:
    """Aplica a porta Hadamard no primeiro qubit do sistema de 2 qubits (H ⊗ I)."""
    # H = 1/sqrt(2) * [[1, 1], [1, -1]]
    inv_sqrt2 = 1.0 / math.sqrt(2.0)
    c00, c01, c10, c11 = state
    
    # Novo |00> e |01> combinam antigo |00>/|01> com |10>/|11>
    n00 = inv_sqrt2 * (c00 + c10)
    n01 = inv_sqrt2 * (c01 + c11)
    n10 = inv_sqrt2 * (c00 - c10)
    n11 = inv_sqrt2 * (c01 - c11)
    return (n00, n01, n10, n11)

def apply_cnot(state: State2Q) -> State2Q:
    """Aplica a porta CNOT (Controlado-NOT) com Qubit 0 como controle e Qubit 1 como alvo."""
    # Se qubit 0 (o mais significativo, em formato |q0 q1>) for 1, inverte qubit 1.
    # Vetor de estado: [c00, c01, c10, c11] -> [c00, c01, c11, c10]
    c00, c01, c10, c11 = state
    return (c00, c01, c11, c10)

# PORTAS QUÂNTICAS PADRÃO (MATRIZES 2x2)
X_GATE = [
    [0.0, 1.0],
    [1.0, 0.0]
]

Y_GATE = [
    [0.0, -1j],
    [1j, 0.0]
]

Z_GATE = [
    [1.0, 0.0],
    [0.0, -1.0]
]

H_GATE = [
    [1.0 / math.sqrt(2), 1.0 / math.sqrt(2)],
    [1.0 / math.sqrt(2), -1.0 / math.sqrt(2)]
]

# ══════════════════════════════════════════════════════════════════════
# SUÍTE DE TESTES TDD (CORA-EVAL D26)
# ══════════════════════════════════════════════════════════════════════

def test_d26_n1_01_qubit_initialization():
    """D26-N1-01: Qubits básicos |0> e |1> são válidos e normalizados."""
    qubit_0: State1Q = (1.0 + 0j, 0.0 + 0j)
    qubit_1: State1Q = (0.0 + 0j, 1.0 + 0j)
    
    assert is_normalized(list(qubit_0)), "Estado |0> deve ser normalizado"
    assert is_normalized(list(qubit_1)), "Estado |1> deve ser normalizado"
    assert qubit_0[0] == 1.0 and qubit_0[1] == 0.0
    return True

def test_d26_n1_02_pauli_x_gate():
    """D26-N1-02: Porta Pauli-X inverte o qubit (Quantum NOT)."""
    q0: State1Q = (1.0 + 0j, 0.0 + 0j)  # |0>
    q1: State1Q = (0.0 + 0j, 1.0 + 0j)  # |1>
    
    res0 = apply_gate_1q(q0, X_GATE)
    res1 = apply_gate_1q(q1, X_GATE)
    
    assert abs(res0[0] - 0j) < 1e-9 and abs(res0[1] - 1.0) < 1e-9, "X|0> deve ser |1>"
    assert abs(res1[0] - 1.0) < 1e-9 and abs(res1[1] - 0j) < 1e-9, "X|1> deve ser |0>"
    return True

def test_d26_n1_03_hadamard_superposition():
    """D26-N1-03: Porta Hadamard gera superposição uniforme."""
    q0: State1Q = (1.0 + 0j, 0.0 + 0j)  # |0>
    res = apply_gate_1q(q0, H_GATE)
    
    assert is_normalized(list(res)), "Superposição deve ser normalizada"
    # Probabilidade de medir 0 ou 1 deve ser exatamente 50%
    p0 = abs(res[0])**2
    p1 = abs(res[1])**2
    assert abs(p0 - 0.5) < 1e-6, "Probabilidade de medir |0> deve ser 0.5"
    assert abs(p1 - 0.5) < 1e-6, "Probabilidade de medir |1> deve ser 0.5"
    return True

def test_d26_n2_01_pauli_z_phase():
    """D26-N2-01: Porta Pauli-Z inverte a fase relativa do estado |1>."""
    # Estado inicial: superposição (|0> + |1>)/sqrt(2)
    state = (1.0 / math.sqrt(2), 1.0 / math.sqrt(2))
    res = apply_gate_1q(state, Z_GATE)
    
    # Fase do segundo termo deve inverter: (|0> - |1>)/sqrt(2)
    assert abs(res[0] - 1.0 / math.sqrt(2)) < 1e-6
    assert abs(res[1] - (-1.0 / math.sqrt(2))) < 1e-6
    return True

def test_d26_n2_02_state_tensor_product():
    """D26-N2-02: Produto tensorial monta estados compostos de múltiplos qubits."""
    q_a = (1.0, 0.0)  # |0>
    q_b = (0.0, 1.0)  # |1>
    
    # Estado composto de 2 qubits |0> ⊗ |1> = |01>
    state_2q = tensor_product(q_a, q_b)
    
    assert is_normalized(list(state_2q)), "Estado composto deve ser normalizado"
    # |01> tem coeficiente 1.0 no índice 1, e 0.0 no restante
    assert state_2q[0] == 0.0  # |00>
    assert state_2q[1] == 1.0  # |01>
    assert state_2q[2] == 0.0  # |10>
    assert state_2q[3] == 0.0  # |11>
    return True

def test_d26_n3_01_controlled_not():
    """D26-N3-01: Porta CNOT inverte o qubit alvo se o qubit de controle for |1>."""
    # Caso 1: Controle em |0>, Alvo em |1> (Estado |01>) -> Sem alteração
    state_01 = (0.0, 1.0, 0.0, 0.0)
    res_01 = apply_cnot(state_01)
    assert res_01[1] == 1.0, "CNOT com controle |0> não deve alterar o alvo"
    
    # Caso 2: Controle em |1>, Alvo em |0> (Estado |10>) -> Inverte alvo para |11>
    state_10 = (0.0, 0.0, 1.0, 0.0)
    res_10 = apply_cnot(state_10)
    assert res_10[3] == 1.0, "CNOT com controle |1> deve inverter o alvo de |0> para |1>"
    return True

def test_d26_n3_02_bell_state_generation():
    """D26-N3-02: Geração do estado de Bell emaranhado Phi+ = (|00> + |11>)/sqrt(2)."""
    # 1. Inicia em |00>
    q0 = (1.0, 0.0)
    q1 = (1.0, 0.0)
    state = tensor_product(q0, q1)  # |00>
    
    # 2. Aplica Hadamard no Qubit de controle (qubit 0)
    state = apply_hadamard_2q_target1(state)  # (|00> + |10>)/sqrt(2)
    
    # 3. Aplica CNOT
    bell_state = apply_cnot(state)  # (|00> + |11>)/sqrt(2)
    
    assert is_normalized(list(bell_state)), "Estado de Bell deve ser normalizado"
    # Coeficientes devem ser 1/sqrt(2) para |00> e |11>, e 0 para |01> e |10>
    expected_coeff = 1.0 / math.sqrt(2.0)
    assert abs(bell_state[0] - expected_coeff) < 1e-6  # |00>
    assert abs(bell_state[1]) < 1e-9                  # |01>
    assert abs(bell_state[2]) < 1e-9                  # |10>
    assert abs(bell_state[3] - expected_coeff) < 1e-6  # |11>
    return True

def test_d26_n4_01_phase_kickback():
    """D26-N4-01: Simula o efeito de Phase Kickback em porta CNOT."""
    # Controle em |+> = (|0> + |1>)/sqrt(2)
    # Alvo em |-> = (|0> - |1>)/sqrt(2)
    q_control = (1.0/math.sqrt(2), 1.0/math.sqrt(2))
    q_target = (1.0/math.sqrt(2), -1.0/math.sqrt(2))
    
    state = tensor_product(q_control, q_target)
    res = apply_cnot(state)
    
    # Após a CNOT, a fase do alvo (-1) retroalimenta (kickback) a fase do controle,
    # fazendo o estado do controle transicionar de |+> para |->.
    # Estado composto final deve ser |-> ⊗ |-> = 1/2*(|00> - |01> - |10> + |11>)
    assert abs(res[0] - 0.5) < 1e-6
    assert abs(res[1] - (-0.5)) < 1e-6
    assert abs(res[2] - (-0.5)) < 1e-6
    assert abs(res[3] - 0.5) < 1e-6
    return True
