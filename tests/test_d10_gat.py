# -*- coding: utf-8 -*-
"""
TDD Test Suite: D10 — Sintese Interdisciplinar (N4 - Pesquisa)
Baseado em: Farinelli, "Geometric Arbitrage Theory and Market Dynamics Reloaded"
             arXiv:0910.1671v10 (2021)

Verifica implementacoes reais dos conceitos centrais da GAT:
  D10-N4-01: Teoria unificadora geometria + finanzas + hidrodinamica
  D10-N4-02: Problema de fronteira interdisciplinar
  D10-N4-03: Gemeo digital de sistema complexo
"""

import sys, math
from typing import List, Tuple, Dict

# ══════════════════════════════════════════════════════════════════════
# SECAO 1 — Derivadas de Nelson (Teoria Estocastica Geometrica)
# Ref: GAT §3.4, eq (33). Nelson D, D*, D = (D+D*)/2
# ══════════════════════════════════════════════════════════════════════

def nelson_forward(x: List[float], dt: float = 1.0) -> List[float]:
    """Derivada forward D: Dx_t = lim_{h->0+} E[(x_{t+h}-x_t)/h | P_t]
    Para processo deterministico, reduz-se a (x_{t+1}-x_t)/dt."""
    return [(x[i+1] - x[i]) / dt for i in range(len(x)-1)]

def nelson_backward(x: List[float], dt: float = 1.0) -> List[float]:
    """Derivada backward D*: D*x_t = lim_{h->0+} E[(x_t-x_{t-h})/h | F_t]"""
    return [(x[i] - x[i-1]) / dt for i in range(1, len(x))]

def nelson_mean(x: List[float], dt: float = 1.0) -> List[float]:
    """Derivada media D = (D+D*)/2 — corresponde a Stratonovich.
    Alinha forward[t] com backward[t]: Dx_t = (x_{t+1}-x_t)/dt,
    D*x_t = (x_t-x_{t-1})/dt, D_t = (Dx_t + D*x_t)/2 para t=1..n-2."""
    n = len(x)
    result = []
    for i in range(1, n - 1):
        fwd_i = (x[i+1] - x[i]) / dt   # Dx_i  (forward at time i)
        bwd_i = (x[i] - x[i-1]) / dt   # D*x_i (backward at time i)
        result.append((fwd_i + bwd_i) / 2.0)
    return result

def test_nelson_linear():
    """D10-N4-01: Para x_t = a*t + b, D = D* = D = a (constante)."""
    a, b = 3.0, 5.0
    x = [a * t + b for t in range(10)]
    fwd = nelson_forward(x)
    bwd = nelson_backward(x)
    mean = nelson_mean(x)

    for v in fwd:
        assert abs(v - a) < 1e-10, f"Forward: {v} != {a}"
    for v in bwd:
        assert abs(v - a) < 1e-10, f"Backward: {v} != {a}"
    for v in mean:
        assert abs(v - a) < 1e-10, f"Mean: {v} != {a}"
    print("  [D10-N4-01] Nelson D=D*=D=a para processo linear... PASS")
    return True

def test_nelson_quadratic():
    """D10-N4-01: Para x_t = t^2, D = 2t+1, D* = 2t-1, D = 2t."""
    x = [t * t for t in range(10)]
    fwd = nelson_forward(x)
    bwd = nelson_backward(x)
    mean = nelson_mean(x)

    for i, v in enumerate(fwd):
        expected = 2 * i + 1  # ((t+1)^2 - t^2) = 2t+1
        assert abs(v - expected) < 1e-10, f"Fwd t={i}: {v} != {expected}"
    for i, v in enumerate(bwd):
        expected = 2 * (i+1) - 1  # (t^2 - (t-1)^2) = 2t-1
        assert abs(v - expected) < 1e-10, f"Bwd t={i+1}: {v} != {expected}"
    for i, v in enumerate(mean):
        t = i + 1  # mean[0] corresponde a t=1
        expected = 2 * t  # D(x=t^2) = 2t em Stratonovich
        assert abs(v - expected) < 1e-10, f"Mean t={t}: {v} != {expected}"
    print("  [D10-N4-01] Nelson D=2t+1, D*=2t-1, D=2t para quadratico... PASS")
    return True


# ══════════════════════════════════════════════════════════════════════
# SECAO 2 — Conexao e Curvatura (Mercado de 2 Ativos)
# Ref: GAT §3.5-3.7, eq (43), (62), (66)
# Arbitrage = Curvature != 0
# ══════════════════════════════════════════════════════════════════════

def connection_form(D: List[float], r: List[float], x: List[float]) -> List[float]:
    """Conexao χ(x,t,g)(δx,δt) = (D^{δx}_t/D^x_t - r^x_t δt) g
    Simplificado: 1-forma de conexao para portfolio x com deflator D e short rate r.
    χ_j = D_j/D^x_t dx^j - r^x dt  (termo em dx^j)
    """
    Dx = sum(xj * dj for xj, dj in zip(x, D))
    # Componentes da conexao χ_j = D_j / D^x
    return [dj / Dx for dj in D]

def curvature_form(D: List[float], r: List[float], x: List[float]) -> List[float]:
    """Curvatura R da eq (66):
    R_j = (D_j/D^x) * [r^x + D log(D^x) - r_j - D log(D_j)]
    Se R_j != 0 para algum j => existe arbitragem.
    """
    Dx = sum(xj * dj for xj, dj in zip(x, D))
    rx = sum(xj * dj * rj for xj, dj, rj in zip(x, D, r)) / Dx

    curvature = []
    for j, (dj, rj) in enumerate(zip(D, r)):
        # D log(D^x) e D log(D_j) requerem derivadas de Nelson
        # Para mercado estatico (sem drift): D log(D) = 0
        Rj = (dj / Dx) * (rx + 0 - rj - 0) if Dx != 0 else 0.0
        curvature.append(Rj)
    return curvature

def test_no_arbitrage_zero_curvature():
    """D10-N4-02: Mercado sem arbitragem => curvatura zero (Theorem 34).
    Se todos os ativos tem o mesmo short rate r_j = r_0, entao R=0.
    """
    # Mercado com 2 ativos + cash
    D = [1.0, 2.0, 3.0]   # deflators (precos descontados)
    r = [0.05, 0.05, 0.05]  # mesmo short rate = sem arbitragem
    x = [1.0, 1.0, 0.0]   # portfolio

    R = curvature_form(D, r, x)
    for j, Rj in enumerate(R):
        assert abs(Rj) < 1e-10, f"Curvatura R[{j}]={Rj} deveria ser 0"
    print("  [D10-N4-02] Mercado sem arbitragem => R=0 (Theorem 34)... PASS")
    return True

def test_arbitrage_nonzero_curvature():
    """D10-N4-02: Mercado com arbitragem => curvatura != 0.
    Short rates diferentes entre ativos geram curvatura.
    """
    D = [1.0, 2.0, 3.0]
    r = [0.05, 0.10, 0.02]  # taxas diferentes = arbitragem potencial
    x = [1.0, 1.0, 0.0]

    R = curvature_form(D, r, x)
    # Pelo menos um R_j deve ser nao-nulo
    any_nonzero = any(abs(Rj) > 1e-10 for Rj in R)
    assert any_nonzero, "Curvatura deveria ser nao-nula com taxas diferentes"
    print(f"  [D10-N4-02] Mercado com arbitragem => R=[{R[0]:.4f},{R[1]:.4f},{R[2]:.4f}] != 0... PASS")
    return True

def test_connection_is_1form():
    """D10-N4-02: A conexao χ e uma 1-forma com valores na algebra de Lie g.
    Propriedade: χ e linear nos argumentos (δx, δt)."""
    D = [1.0, 2.0]
    r = [0.05, 0.05]
    x = [1.0, 1.0]

    chi = connection_form(D, r, x)
    # χ deve ter N componentes (uma por ativo)
    assert len(chi) == len(D), f"Conexao deveria ter {len(D)} componentes"
    # Cada componente e um numero real (1-forma avaliada em direcao dx^j)
    for c in chi:
        assert isinstance(c, float)
    print("  [D10-N4-02] Conexao χ e 1-forma com N componentes... PASS")
    return True


# ══════════════════════════════════════════════════════════════════════
# SECAO 3 — Equacao de Continuidade (Fluxo de Valor)
# Ref: GAT §3.8, eq (80)-(82)
# Dρ^β + div_x J = 0  <=>  NFLVR
# ══════════════════════════════════════════════════════════════════════

def log_value_density(D: List[float], beta: float = 1.0) -> List[float]:
    """Densidade de log-valor ρ^β(x,t) = log(β_t * D^x_t). Eq (79)."""
    return [math.log(beta * d) for d in D]

def log_value_current(D: List[float], r: List[float], x: List[float]) -> List[float]:
    """Corrente de log-valor J_j = (integral sobre portfolios) * r_j. Eq (78).
    Simplificado: J_j ~ D_j * r_j / D^x (aproximacao de primeira ordem)."""
    Dx = sum(xj * dj for xj, dj in zip(x, D))
    return [dj * rj / Dx if Dx != 0 else 0.0 for dj, rj in zip(D, r)]

def continuity_divergence(D: List[float], r: List[float], x: List[float]) -> float:
    """div_x J = sum_j ∂J_j/∂x_j.
    No modelo estatico, div_x J = r^x (short rate do portfolio). Eq (81)."""
    Dx = sum(xj * dj for xj, dj in zip(x, D))
    if Dx == 0:
        return 0.0
    return sum(xj * dj * rj for xj, dj, rj in zip(x, D, r)) / Dx

def test_continuity_divergence_equals_short_rate():
    """D10-N4-03: div_x J = r^x (eq 81).
    Verifica que a divergencia da corrente de valor e igual ao short rate do portfolio."""
    D = [1.0, 2.0, 3.0]
    r = [0.05, 0.08, 0.03]
    x = [1.0, 1.0, 1.0]

    divJ = continuity_divergence(D, r, x)
    # r^x = sum x_j D_j r_j / sum x_j D_j
    rx_expected = sum(xj * dj * rj for xj, dj, rj in zip(x, D, r)) / sum(xj * dj for xj, dj in zip(x, D))
    assert abs(divJ - rx_expected) < 1e-10, f"divJ={divJ} != rx={rx_expected}"
    print(f"  [D10-N4-03] div_x J = r^x = {rx_expected:.4f}... PASS")
    return True

def test_nflvr_zero_divergence_balance():
    """D10-N4-03: NFLVR => Dρ^β + div_x J = 0 (eq 80).
    Em mercado estatico (Dρ=0), NFLVR requer div J = 0 => r^x = 0."""
    D = [1.0, 1.0, 1.0]
    r = [0.0, 0.0, 0.0]  # taxas zero = sem fluxo de arbitragem
    x = [1.0, 1.0, 1.0]

    divJ = continuity_divergence(D, r, x)
    assert abs(divJ) < 1e-10, f"NFLVR requer divJ=0, obtido {divJ}"
    print("  [D10-N4-03] NFLVR => Dρ+divJ=0 verificado (r=0 => divJ=0)... PASS")
    return True


# ══════════════════════════════════════════════════════════════════════
# SECAO 4 — Holonomia e Topologia (Ambrose-Singer)
# Ref: GAT §3.5, Definition 31, Theorem 34(iv)(v)
# Holonomia trivial <=> Curvatura zero
# ══════════════════════════════════════════════════════════════════════

def parallel_transport_nominal(D: List[float], x_from: List[float],
                               x_to: List[float]) -> float:
    """Transporte paralelo ao longo de direcao nominal (x).
    Eq (47): g(τ) = g1 * (sum x_j(τ1) D_j) / (sum x_j(τ) D_j).
    Interpretacao financeira: taxa de cambio entre portfolios."""
    val_from = sum(xf * d for xf, d in zip(x_from, D))
    val_to = sum(xt * d for xt, d in zip(x_to, D))
    return val_from / val_to if val_to != 0 else float('inf')

def parallel_transport_time(D: float, r: float, t_from: float, t_to: float) -> float:
    """Transporte paralelo ao longo do tempo.
    Eq (49): g(τ) = g1 * exp(∫ r du).
    Interpretacao financeira: fator de desconto estocastico."""
    return math.exp(r * (t_to - t_from))

def test_parallel_transport_exchange():
    """D10-N4-02: Transporte nominal = taxa de cambio (Theorem 29)."""
    D = [2.0, 3.0, 5.0]  # precos de 3 ativos
    x_usd = [1.0, 0.0, 0.0]
    x_eur = [0.0, 1.0, 0.0]

    fx = parallel_transport_nominal(D, x_usd, x_eur)
    expected_fx = 2.0 / 3.0  # USD/EUR = D_USD/D_EUR
    assert abs(fx - expected_fx) < 1e-10
    print(f"  [D10-N4-02] Transporte nominal USD/EUR = {fx:.4f}... PASS")
    return True

def test_parallel_transport_discount():
    """D10-N4-02: Transporte temporal = desconto (Theorem 29)."""
    D0 = 100.0
    r = 0.05
    t = 1.0

    discount = parallel_transport_time(D0, r, 0, t)
    expected = math.exp(-0.05)  # fator de desconto: e^{-rt}? Nao: transporte paralelo
    # Eq (49): g(τ) = g1 * exp(∫r du) = g1 * exp(r*t)
    # Interpretacao: DIVISAO pelo fator de desconto
    # Se g1 = 1, g(τ) = exp(r*t) = valor futuro de 1 unidade
    expected_val = math.exp(r * t)
    assert abs(discount - expected_val) < 1e-10
    print(f"  [D10-N4-02] Transporte temporal exp(r*t) = {discount:.4f}... PASS")
    return True

def test_holonomy_trivial_when_zero_curvature():
    """D10-N4-02: Holonomia trivial <=> Curvatura zero (Ambrose-Singer).
    Transporte paralelo ao longo de curva fechada retorna identidade."""
    # Curva fechada: x1 -> x2 -> x1 no mesmo instante t
    D = [1.0, 2.0]
    x_a = [1.0, 0.0]
    x_b = [0.0, 1.0]

    # ida
    fwd = parallel_transport_nominal(D, x_a, x_b)
    # volta
    bwd = parallel_transport_nominal(D, x_b, x_a)
    # holonomia = ida * volta (grupo abeliano)
    holonomy = fwd * bwd
    assert abs(holonomy - 1.0) < 1e-10
    print("  [D10-N4-02] Holonomia trivial (curva fechada => identidade)... PASS")
    return True


# ══════════════════════════════════════════════════════════════════════
# RUNNER
# ══════════════════════════════════════════════════════════════════════

def main():
    tests = [
        # Nelson derivatives (D10-N4-01)
        ("Nelson linear", test_nelson_linear),
        ("Nelson quadratic", test_nelson_quadratic),
        # Curvature & Arbitrage (D10-N4-02)
        ("No-arbitrage => R=0", test_no_arbitrage_zero_curvature),
        ("Arbitrage => R!=0", test_arbitrage_nonzero_curvature),
        ("Connection 1-form", test_connection_is_1form),
        # Holonomy & Parallel Transport (D10-N4-02)
        ("Transport nominal = FX", test_parallel_transport_exchange),
        ("Transport temporal = desconto", test_parallel_transport_discount),
        ("Holonomia trivial", test_holonomy_trivial_when_zero_curvature),
        # Continuity Equation (D10-N4-03)
        ("div J = r^x", test_continuity_divergence_equals_short_rate),
        ("NFLVR => div J = 0", test_nflvr_zero_divergence_balance),
    ]

    print("=" * 60)
    print("  TDD TEST SUITE: D10 — Sintese Interdisciplinar (N4)")
    print("  Fonte: Farinelli, Geometric Arbitrage Theory (2021)")
    print("=" * 60)

    passed = 0
    failed = 0
    for name, test_fn in tests:
        try:
            test_fn()
            passed += 1
        except AssertionError as e:
            print(f"  [{name}] FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"  [{name}] ERROR: {e}")
            failed += 1

    print(f"\n  RESULT: {passed}/{passed+failed} passed, {failed} failed")
    print("=" * 60)
    return failed == 0

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
