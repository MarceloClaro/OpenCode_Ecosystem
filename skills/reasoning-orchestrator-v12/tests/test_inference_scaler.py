#!/usr/bin/env python
# =====================================================================
# TESTES C2 — Inference-Time Scaling
# =====================================================================
# Testes TDD para o InferenceScaler: lei de potência, alocação
# adaptativa, calibração e integração com orchestrator v12.
# =====================================================================
import sys, os, math, json
from typing import Any

# Adiciona agents ao path (necessário para import dos módulos)
_AGENTS_PATH = os.path.join(os.path.dirname(__file__), "..", "agents")
if _AGENTS_PATH not in sys.path:
    sys.path.insert(0, _AGENTS_PATH)

# =====================================================================
# C2-T1: predict_pci produz valores esperados
# =====================================================================
def test_pci_prediction():
    """predict_pci produz valores esperados para casos canônicos."""
    from inference_scaler import InferenceScaler
    
    scaler = InferenceScaler(alpha=35.0, beta=0.35)
    
    # Caso base: compute=1 → PCI=35.0
    pci_1 = scaler.predict_pci(1)
    assert abs(pci_1 - 35.0) < 0.01, f"PCI(1)={pci_1}, esperado 35.0"
    
    # compute=0 → PCI=0
    pci_0 = scaler.predict_pci(0)
    assert pci_0 == 0.0, f"PCI(0)={pci_0}, esperado 0.0"
    
    # compute=10 → PCI=35*10^0.35 ≈ 78.26
    pci_10 = scaler.predict_pci(10)
    expected_10 = 35.0 * (10 ** 0.35)
    assert abs(pci_10 - expected_10) < 0.1, f"PCI(10)={pci_10}, esperado {expected_10}"
    
    # Monotonicidade: compute maior → PCI maior
    pci_50 = scaler.predict_pci(50)
    pci_100 = scaler.predict_pci(100)
    assert pci_100 > pci_50, "PCI deve ser monotônico crescente"


# =====================================================================
# C2-T2: PCI é monotônico crescente
# =====================================================================
def test_pci_monotonic():
    """PCI cresce monotonicamente com o aumento de compute."""
    from inference_scaler import InferenceScaler
    
    scaler = InferenceScaler()
    computes = [1, 2, 5, 10, 20, 30, 50, 80, 100, 200]
    pcis = [scaler.predict_pci(c) for c in computes]
    
    for i in range(1, len(pcis)):
        assert pcis[i] > pcis[i-1], (
            f"PCI não é monotônico: PCI({computes[i]})={pcis[i]} "
            f"<= PCI({computes[i-1]})={pcis[i-1]}"
        )


# =====================================================================
# C2-T3: Retornos decrescentes
# =====================================================================
def test_diminishing_returns():
    """Ganho marginal diminui com o aumento de compute."""
    from inference_scaler import InferenceScaler
    
    scaler = InferenceScaler()
    
    # Ganho marginal em compute=10 vs compute=100
    gain_10 = scaler.marginal_gain(10, 1.0)
    gain_100 = scaler.marginal_gain(100, 1.0)
    
    assert gain_10 > gain_100, (
        f"Ganho marginal deveria diminuir: gain(10)={gain_10:.4f} "
        f"<= gain(100)={gain_100:.4f}"
    )
    
    # Ganho marginal em compute=1 vs compute=50
    gain_1 = scaler.marginal_gain(1, 1.0)
    gain_50 = scaler.marginal_gain(50, 1.0)
    
    assert gain_1 > gain_50, (
        f"Ganho marginal deveria diminuir: gain(1)={gain_1:.4f} "
        f"<= gain(50)={gain_50:.4f}"
    )


# =====================================================================
# C2-T4: Alocação soma budget total
# =====================================================================
def test_uniform_allocation():
    """Alocação adaptativa produz distribuição que soma = total_budget."""
    from inference_scaler import InferenceScaler
    
    scaler = InferenceScaler()
    
    for total in [30, 60, 100, 200]:
        allocation = scaler.allocate_budget(total_budget=total)
        total_allocated = sum(allocation.values())
        
        assert abs(total_allocated - total) < 0.1, (
            f"Alocação soma {total_allocated}, esperado {total}"
        )
        assert len(allocation) == 7, (
            f"Alocação tem {len(allocation)} fases, esperado 7"
        )


# =====================================================================
# C2-T5: Fases complexas recebem mais budget
# =====================================================================
def test_adaptive_allocation():
    """F3 (Deductive) recebe mais budget que F7 (Synthesis)."""
    from inference_scaler import InferenceScaler
    
    scaler = InferenceScaler()
    
    for total in [60, 100, 200]:
        allocation = scaler.allocate_budget(total_budget=total)
        
        # F3 tem peso 1.5, F7 tem peso 0.5
        assert allocation[3] >= allocation[7], (
            f"F3({allocation[3]:.1f}) deveria ter >= budget que "
            f"F7({allocation[7]:.1f}) para budget={total}"
        )
        
        # F3 tem peso 1.5, F1 tem peso 0.8
        assert allocation[3] >= allocation[1], (
            f"F3({allocation[3]:.1f}) deveria ter >= budget que "
            f"F1({allocation[1]:.1f}) para budget={total}"
        )


# =====================================================================
# C2-T6: Budget mínimo por fase
# =====================================================================
def test_allocation_min_per_phase():
    """Nenhuma fase recebe menos que min_per_phase."""
    from inference_scaler import InferenceScaler
    
    scaler = InferenceScaler()
    min_per = 1
    
    for total in [30, 60, 100, 200]:
        allocation = scaler.allocate_budget(total_budget=total, min_per_phase=min_per)
        
        for phase, budget in allocation.items():
            assert budget >= min_per, (
                f"Fase {phase} recebeu {budget}, mínimo era {min_per}"
            )


# =====================================================================
# C2-T7: Calibração com dados perfeitos — R² >= 0.85
# =====================================================================
def test_calibrate_r_squared():
    """R² >= 0.85 para dados sintéticos perfeitamente alinhados."""
    from inference_scaler import InferenceScaler
    
    scaler = InferenceScaler()
    
    # Dados perfeitos: PCI = 35.0 * compute^0.35
    observed = [
        {"compute": c, "pci": 35.0 * (c ** 0.35)}
        for c in [1, 2, 5, 10, 20, 30, 50, 80, 100]
    ]
    
    result = scaler.calibrate(observed)
    
    assert result["r_squared"] >= 0.85, (
        f"R²={result['r_squared']:.4f}, esperado >= 0.85"
    )
    assert result["n_points"] == len(observed)
    assert len(result["predictions"]) == len(observed)


# =====================================================================
# C2-T8: Calibração recupera α e β originais
# =====================================================================
def test_calibrate_alpha_beta():
    """Calibração recupera α e β com erro < 1% para dados perfeitos."""
    from inference_scaler import InferenceScaler
    
    original_alpha = 35.0
    original_beta = 0.35
    
    scaler = InferenceScaler(alpha=42.0, beta=0.5)  # Começa com valores diferentes
    
    observed = [
        {"compute": c, "pci": original_alpha * (c ** original_beta)}
        for c in [1, 2, 5, 10, 15, 20, 30, 40, 50, 60, 80, 100]
    ]
    
    result = scaler.calibrate(observed)
    
    # α e β recuperados
    alpha_error = abs(result["alpha"] - original_alpha) / original_alpha
    beta_error = abs(result["beta"] - original_beta) / original_beta
    
    assert alpha_error < 0.01, (
        f"Erro α={alpha_error:.4f} ({result['alpha']:.2f} vs {original_alpha})"
    )
    assert beta_error < 0.01, (
        f"Erro β={beta_error:.4f} ({result['beta']:.4f} vs {original_beta})"
    )


# =====================================================================
# C2-T9: Alocação por modo respeita budget
# =====================================================================
def test_allocate_mode_budget():
    """Mode budget allocation respeita budget do modo e retorna config completa."""
    from inference_scaler import InferenceScaler
    
    scaler = InferenceScaler()
    
    mode_configs = {
        "express": {"budget": 30, "max_workers": 1, "timeout": 30},
        "standard": {"budget": 60, "max_workers": 2, "timeout": 60},
        "magnum": {"budget": 100, "max_workers": 4, "timeout": 120},
        "research": {"budget": 200, "max_workers": 8, "timeout": 240},
    }
    
    for mode, config in mode_configs.items():
        result = scaler.allocate_mode_budget(mode, config)
        
        # Verifica campos retornados
        assert "phase_budgets" in result, f"Modo {mode} sem phase_budgets"
        assert "expected_pci" in result, f"Modo {mode} sem expected_pci"
        assert "improvement_pct" in result, f"Modo {mode} sem improvement_pct"
        
        # Soma dos budgets = budget total
        total = sum(result["phase_budgets"].values())
        assert abs(total - config["budget"]) < 0.1, (
            f"Modo {mode}: soma budgets {total} != {config['budget']}"
        )
        
        # improvement_pct >= 0
        assert result["improvement_pct"] >= 0, (
            f"Modo {mode}: improvement_pct < 0"
        )


# =====================================================================
# C2-T10: PCI adaptativo > PCI uniforme
# =====================================================================
def test_improvement_over_uniform():
    """Alocação adaptativa produz PCI maior que uniforme."""
    from inference_scaler import InferenceScaler
    
    scaler = InferenceScaler()
    
    for total_budget in [60, 100]:
        # Alocação uniforme
        uniform = {i: total_budget / 7 for i in range(1, 8)}
        
        # PCI com alocação uniforme
        pci_uniform = sum(
            scaler.predict_pci(uniform[i]) * scaler.phase_weights.get(i, 1.0)
            for i in range(1, 8)
        ) / sum(scaler.phase_weights.get(i, 1.0) for i in range(1, 8))
        
        # Alocação adaptativa
        adaptive = scaler.allocate_budget(total_budget=total_budget)
        pci_adaptive = sum(
            scaler.predict_pci(adaptive[i]) * scaler.phase_weights.get(i, 1.0)
            for i in range(1, 8)
        ) / sum(scaler.phase_weights.get(i, 1.0) for i in range(1, 8))
        
        assert pci_adaptive > pci_uniform * 1.005, (  # Pelo menos 0.5% melhor
            f"Budget={total_budget}: PCI adaptive={pci_adaptive:.2f} "
            f"<= uniform={pci_uniform:.2f}"
        )
        
        # improvement_pct consistente
        improvement = (pci_adaptive - pci_uniform) / pci_uniform * 100
        print(f"  Budget={total_budget}: PCI uniform={pci_uniform:.2f}, "
              f"adaptive={pci_adaptive:.2f}, improvement={improvement:.2f}%")


# =====================================================================
# C2-T11: Integração com orchestrator v12
# =====================================================================
def test_scaler_integration():
    """InferenceScaler integrado ao orchestrator para solve_with_scaling."""
    from inference_scaler import InferenceScaler
    from orchestrator_v12 import ParallelOrchestrator, OperationMode
    
    scaler = InferenceScaler()
    orchestrator = ParallelOrchestrator(mode=OperationMode.STANDARD)
    
    # Testa alocação para Standard
    mode_config = {
        "budget": 60,
        "max_workers": 2,
        "timeout": 60,
    }
    
    result = scaler.allocate_mode_budget("standard", mode_config)
    
    # Orquestrador aceita phase_budgets
    assert result["expected_pci"] > 0
    assert result["improvement_pct"] >= 0
    assert len(result["phase_budgets"]) == 7
    
    # Testa que podemos passar phase_budgets para solve
    problem = "Prove that the square root of 2 is irrational"
    
    solution = orchestrator.solve(
        problem=problem,
        budget_override=60,
    )
    
    # Relatório inclui num_agents_executed
    assert solution.num_agents_executed > 0
    assert solution.pci > 0
    assert solution.mode == "standard"


# =====================================================================
# C2-T12: Ganho marginal segue fórmula esperada
# =====================================================================
def test_marginal_gain_formula():
    """Ganho marginal = alpha * beta * (weight * compute)^(beta-1) * weight."""
    from inference_scaler import InferenceScaler
    
    alpha = 35.0
    beta = 0.35
    scaler = InferenceScaler(alpha=alpha, beta=beta)
    
    # Teste: compute=10, weight=1.0
    compute = 10.0
    weight = 1.0
    
    gain = scaler.marginal_gain(compute, weight)
    
    # Fórmula esperada: alpha * beta * (w * c)^(beta-1) * w
    expected = alpha * beta * (weight * compute) ** (beta - 1) * weight
    
    assert abs(gain - expected) < 0.0001, (
        f"Ganho={gain:.6f}, esperado={expected:.6f}"
    )
    
    # Teste: compute=5, weight=1.5
    compute2 = 5.0
    weight2 = 1.5
    
    gain2 = scaler.marginal_gain(compute2, weight2)
    expected2 = alpha * beta * (weight2 * compute2) ** (beta - 1) * weight2
    
    assert abs(gain2 - expected2) < 0.0001, (
        f"Ganho2={gain2:.6f}, esperado2={expected2:.6f}"
    )
    
    # Ganho marginal com peso maior = ganho maior (mesmo compute)
    assert gain2 > gain, (
        f"Maior peso deveria dar maior ganho: {gain2:.6f} <= {gain:.6f}"
    )


# =====================================================================
# Main
# =====================================================================
if __name__ == "__main__":
    # Executa todos os testes
    test_functions = [
        test_pci_prediction,
        test_pci_monotonic,
        test_diminishing_returns,
        test_uniform_allocation,
        test_adaptive_allocation,
        test_allocation_min_per_phase,
        test_calibrate_r_squared,
        test_calibrate_alpha_beta,
        test_allocate_mode_budget,
        test_improvement_over_uniform,
        test_scaler_integration,
        test_marginal_gain_formula,
    ]
    
    passed = 0
    failed = 0
    errors = []
    
    print("=" * 60)
    print("TESTES C2 - Inference-Time Scaling")
    print("=" * 60)
    
    for test_fn in test_functions:
        try:
            test_fn()
            print(f"  [PASS] {test_fn.__name__}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {test_fn.__name__}: {e}")
            failed += 1
            errors.append((test_fn.__name__, str(e)))
    
    print("-" * 60)
    total = passed + failed
    print(f"Total: {total} | Passou: {passed} | Falhou: {failed}")
    
    if errors:
        print("\nErros:")
        for name, err in errors:
            print(f"  - {name}: {err}")
    
    sys.exit(0 if failed == 0 else 1)
