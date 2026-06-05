import numpy as np

def find_nash_equilibrium(payoff_matrix_a, payoff_matrix_b):
    """
    Encontra equilíbrios de Nash em estratégias puras para um jogo de dois jogadores.
    """
    rows, cols = payoff_matrix_a.shape
    nash_equilibria = []

    for i in range(rows):
        for j in range(cols):
            # Jogador 1 (linhas) não quer mudar
            is_p1_best = payoff_matrix_a[i, j] == np.max(payoff_matrix_a[:, j])
            # Jogador 2 (colunas) não quer mudar
            is_p2_best = payoff_matrix_b[i, j] == np.max(payoff_matrix_b[i, :])

            if is_p1_best and is_p2_best:
                nash_equilibria.append((i, j))
    
    return nash_equilibria

def analyze_prisoners_dilemma():
    # Matriz de Payoff (Cooperar, Desertar)
    # Valores: (3,3) CC, (0,5) CD, (5,0) DC, (1,1) DD
    p1_payoff = np.array([[3, 0], [5, 1]])
    p2_payoff = np.array([[3, 5], [0, 1]])
    
    equilibria = find_nash_equilibrium(p1_payoff, p2_payoff)
    return {
        "game": "Prisoner's Dilemma",
        "nash_equilibria": equilibria,
        "insight": "O equilíbrio de Nash (Desertar, Desertar) é subótimo em relação à cooperação mútua."
    }

if __name__ == "__main__":
    result = analyze_prisoners_dilemma()
    print(f"Análise de Teoria dos Jogos: {result}")
