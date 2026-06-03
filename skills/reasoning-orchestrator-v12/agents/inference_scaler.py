#!/usr/bin/env python
# =====================================================================
# INFERENCE SCALER — Parallel Thinking Engine v12.0 / Ciclo 2
# =====================================================================
# Inference-Time Scaling: alocação adaptativa de compute baseada em
# scaling law PCI = α · compute^β com otimização marginal.
#
# Dependências:
#   - orchestrator_v12.py (PhaseReport, OperationMode)
# =====================================================================
import sys, os, math
from dataclasses import dataclass, field
from typing import Any, Optional


# =====================================================================
# SCALING LAW
# =====================================================================

class InferenceScaler:
    """
    Gerencia alocação adaptativa de recursos de raciocínio baseada em
    scaling law: PCI(compute) = alpha * compute^beta.
    
    A lei de potência governa como o Proof Confidence Index (PCI)
    escala com a quantidade de computação (budget) investida:
    - alpha (α): fator de escala base (~35.0)
    - beta  (β): expoente da lei (~0.35, típico 0.2-0.5)
    - lei sublinear: β < 1 → retornos decrescentes
    
    Uso típico:
        scaler = InferenceScaler()
        pci = scaler.predict_pci(compute=60)  # PCI esperado
        budget = scaler.allocate_budget(total_budget=100)  # Otimização
        cal = scaler.calibrate(observed_data)  # Calibração
    """
    
    DEFAULT_ALPHA = 35.0
    DEFAULT_BETA = 0.35
    
    # Pesos de complexidade por fase (1 = baseline)
    # Fases com maior peso recebem mais budget na otimização marginal
    PHASE_WEIGHTS = {
        1: 0.8,   # Problem Analysis — 3 agentes, análise inicial leve
        2: 1.0,   # Reasoning Selection — baseline
        3: 1.5,   # Deductive Derivation — 4 agentes, cadeias profundas
        4: 1.2,   # Inductive Verification — 2 agentes, verificação
        5: 1.4,   # Cross-Reference — 3 agentes, refinamento contraditório
        6: 1.1,   # Proof Health Check — 3 agentes, verificação
        7: 0.5,   # Synthesis — 1 agente, consolidação simples
    }
    
    def __init__(
        self,
        alpha: float = DEFAULT_ALPHA,
        beta: float = DEFAULT_BETA,
        phase_weights: Optional[dict[int, float]] = None,
    ):
        """
        Inicializa o InferenceScaler.
        
        Args:
            alpha: Fator de escala da lei de potência (PCI base)
            beta: Expoente da lei de potência (0.2-0.5 típico)
            phase_weights: Pesos de complexidade por fase (1-7)
        """
        self.alpha = alpha
        self.beta = beta
        self.phase_weights = phase_weights or dict(self.PHASE_WEIGHTS)
    
    # ------------------------------------------------------------------
    # PREDIÇÃO PCI
    # ------------------------------------------------------------------
    
    def predict_pci(self, compute: float) -> float:
        """
        Prevê PCI para dado nível de compute: PCI = alpha * compute^beta.
        
        Args:
            compute: Unidades de computação (budget)
        
        Returns:
            PCI previsto (não normalizado, pode ser > 100)
        """
        if compute <= 0:
            return 0.0
        return self.alpha * (compute ** self.beta)
    
    # ------------------------------------------------------------------
    # GANHO MARGINAL
    # ------------------------------------------------------------------
    
    def marginal_gain(
        self,
        phase_budget: float,
        phase_weight: float,
    ) -> float:
        """
        Computa ganho marginal de adicionar compute a uma fase.
        
        dPCI/d(compute_i) = α · β · (w_i · compute_i)^(β-1) · w_i
        
        Args:
            phase_budget: Budget atual da fase
            phase_weight: Peso de complexidade da fase
        
        Returns:
            Ganho marginal (derivada) em unidades de PCI por unidade de compute
        """
        if phase_budget <= 0:
            # Próximo de zero: limite da derivada tende a infinito
            # Mas usamos um valor grande finito para evitar divisão por zero
            return self.alpha * self.beta * (phase_weight ** self.beta) * (1e-10 ** (self.beta - 1))
        
        weighted = phase_weight * phase_budget
        return self.alpha * self.beta * (weighted ** (self.beta - 1)) * phase_weight
    
    def diminishing_threshold(self, compute: float, threshold: float = 0.05) -> bool:
        """
        Verifica se retornos já diminuíram abaixo do threshold.
        
        Args:
            compute: Nível atual de compute
            threshold: Fração do PCI atual abaixo da qual considera
                       que retornos diminuíram (default: 5%)
        
        Returns:
            True se ganho marginal / PCI_atual < threshold
        """
        if compute <= 0:
            return False
        gain = self.marginal_gain(compute, 1.0)
        pci = self.predict_pci(compute)
        return (gain / max(pci, 1e-10)) < threshold
    
    # ------------------------------------------------------------------
    # ALOCAÇÃO ADAPTATIVA
    # ------------------------------------------------------------------
    
    def allocate_budget(
        self,
        total_budget: int,
        num_phases: int = 7,
        iterations: int = 100,
        tolerance: float = 0.001,
        min_per_phase: int = 1,
    ) -> dict[int, float]:
        """
        Aloca budget entre fases via otimização marginal.
        
        Algoritmo:
        1. Distribuição uniforme inicial
        2. Para cada iteração:
           a. Computa ganho marginal por fase
           b. Move 1 unidade da fase com menor ganho para a de maior ganho
           c. Verifica convergência (diferença entre max e min < tolerance)
        3. Garante budget mínimo por fase
        
        Args:
            total_budget: Orçamento total a distribuir
            num_phases: Número de fases (default: 7)
            iterations: Máximo de iterações de otimização
            tolerance: Tolerância para convergência
            min_per_phase: Budget mínimo por fase
        
        Returns:
            dict[fase_num (1-indexed): budget_alocado]
        """
        if total_budget < num_phases * min_per_phase:
            # Budget insuficiente: distribui igualmente com mínimo
            return {i: float(min_per_phase) for i in range(1, num_phases + 1)}
        
        # Alocação inicial uniforme
        uniform = max(total_budget // num_phases, min_per_phase)
        budget = {i: float(uniform) for i in range(1, num_phases + 1)}
        
        # Distribui resto para as primeiras fases
        remaining = total_budget - sum(budget.values())
        for i in range(1, num_phases + 1):
            if remaining <= 0:
                break
            budget[i] += 1.0
            remaining -= 1
        
        # Otimização marginal iterativa
        for _ in range(iterations):
            gains = {}
            for i in range(1, num_phases + 1):
                weight = self.phase_weights.get(i, 1.0)
                gains[i] = self.marginal_gain(budget[i], weight)
            
            max_phase = max(gains, key=gains.get)
            min_phase = min(gains, key=gains.get)
            
            # Verifica convergência
            if gains[max_phase] - gains[min_phase] < tolerance:
                break
            
            # Move 1 unidade da fase menos produtiva para a mais produtiva
            if budget[min_phase] > min_per_phase:
                budget[min_phase] -= 1.0
                budget[max_phase] += 1.0
            else:
                # Se a fase com menor ganho já está no mínimo,
                # move da segunda pior
                sorted_phases = sorted(gains, key=gains.get)
                for candidate in sorted_phases:
                    if budget[candidate] > min_per_phase:
                        budget[candidate] -= 1.0
                        budget[max_phase] += 1.0
                        break
                else:
                    # Ninguém pode ceder budget → convergiu
                    break
        
        return {k: round(v, 1) for k, v in budget.items()}
    
    # ------------------------------------------------------------------
    # CALIBRAÇÃO
    # ------------------------------------------------------------------
    
    def calibrate(self, observed: list[dict]) -> dict:
        """
        Calibra α e β a partir de dados observados via regressão log-log.
        
        Método:
        1. Transformação logarítmica: log(compute), log(PCI)
        2. Regressão linear: log(PCI) = log(α) + β · log(compute)
        3. Extração: β = slope, α = exp(intercept)
        
        Args:
            observed: Lista de dicts [{"compute": float, "pci": float}, ...]
        
        Returns:
            dict com alpha, beta, r_squared, predictions
        """
        n = len(observed)
        if n < 3:
            return {
                "alpha": self.alpha,
                "beta": self.beta,
                "r_squared": 0.0,
                "predictions": [],
                "n_points": n,
                "error": "Precisa de pelo menos 3 pontos para calibrar",
            }
        
        # Extrai vetores
        computes = [max(o["compute"], 1e-10) for o in observed]
        pcis = [max(o["pci"], 1e-10) for o in observed]
        
        # Transformação logarítmica
        log_computes = [math.log(c) for c in computes]
        log_pcis = [math.log(p) for p in pcis]
        
        # Métricas amostrais
        nf = float(n)
        mean_x = sum(log_computes) / nf
        mean_y = sum(log_pcis) / nf
        
        # Regressão linear (mínimos quadrados)
        cov_xy = sum((x - mean_x) * (y - mean_y)
                     for x, y in zip(log_computes, log_pcis))
        var_x = sum((x - mean_x) ** 2 for x in log_computes)
        
        if var_x < 1e-15:
            return {
                "alpha": self.alpha,
                "beta": self.beta,
                "r_squared": 0.0,
                "predictions": [],
                "n_points": n,
                "error": "Variância zero nos computes",
            }
        
        beta_hat = cov_xy / var_x
        log_alpha_hat = mean_y - beta_hat * mean_x
        
        # R²
        residuals = [y - (beta_hat * x + log_alpha_hat)
                     for x, y in zip(log_computes, log_pcis)]
        ss_res = sum(r ** 2 for r in residuals)
        ss_tot = sum((y - mean_y) ** 2 for y in log_pcis)
        r_squared = 1.0 - ss_res / max(ss_tot, 1e-15)
        
        # Atualiza parâmetros internos
        self.alpha = math.exp(log_alpha_hat)
        self.beta = beta_hat
        
        # Gera predições
        predictions = [self.predict_pci(c) for c in computes]
        
        return {
            "alpha": round(self.alpha, 4),
            "beta": round(self.beta, 4),
            "r_squared": round(r_squared, 6),
            "predictions": [round(p, 2) for p in predictions],
            "n_points": n,
        }
    
    # ------------------------------------------------------------------
    # ALOCAÇÃO POR MODO
    # ------------------------------------------------------------------
    
    def allocate_mode_budget(
        self,
        mode: str,
        mode_config: dict,
    ) -> dict[str, Any]:
        """
        Aloca budget para todas as fases dado um modo de operação.
        
        Args:
            mode: Nome do modo ("express", "standard", "magnum", "research")
            mode_config: Dict com config do modo (budget, max_workers, timeout)
        
        Returns:
            dict com:
            - phase_budgets: budget por fase (alocação adaptativa)
            - expected_pci: PCI esperado para este modo
            - improvement_pct: melhoria percentual vs alocação uniforme
            - mode: nome do modo
        """
        total_budget = mode_config.get("budget", 60)
        
        # Alocação adaptativa
        phase_budgets = self.allocate_budget(total_budget=total_budget)
        
        # Alocação uniforme (baseline)
        uniform = {i: total_budget / 7 for i in range(1, 8)}
        
        # PCI com alocação adaptativa (média ponderada por pesos)
        pci_adaptive = sum(
            self.predict_pci(phase_budgets[i]) * self.phase_weights.get(i, 1.0)
            for i in range(1, 8)
        ) / sum(self.phase_weights.get(i, 1.0) for i in range(1, 8))
        
        # PCI com alocação uniforme
        pci_uniform = sum(
            self.predict_pci(uniform[i]) * self.phase_weights.get(i, 1.0)
            for i in range(1, 8)
        ) / sum(self.phase_weights.get(i, 1.0) for i in range(1, 8))
        
        # Melhoria percentual
        if pci_uniform > 0:
            improvement = (pci_adaptive - pci_uniform) / pci_uniform * 100
        else:
            improvement = 0.0
        
        # Mapeamento budget → workers por fase
        per_phase_workers = {}
        for phase, bgt in phase_budgets.items():
            if bgt < 5:
                per_phase_workers[phase] = 1
            elif bgt < 10:
                per_phase_workers[phase] = 2
            elif bgt < 15:
                per_phase_workers[phase] = 3
            else:
                per_phase_workers[phase] = 4
        
        return {
            "mode": mode,
            "total_budget": total_budget,
            "phase_budgets": phase_budgets,
            "per_phase_workers": per_phase_workers,
            "expected_pci": round(pci_adaptive, 2),
            "uniform_pci": round(pci_uniform, 2),
            "improvement_pct": round(improvement, 2),
        }


# =====================================================================
# FUNÇÃO DE CONVENIÊNCIA
# =====================================================================

def create_scaler_for_mode(
    mode: str,
    alpha: float = InferenceScaler.DEFAULT_ALPHA,
    beta: float = InferenceScaler.DEFAULT_BETA,
) -> tuple[InferenceScaler, dict]:
    """
    Cria um InferenceScaler configurado para um modo de operação.
    
    Args:
        mode: "express", "standard", "magnum", "research"
        alpha: Fator de escala (default: 35.0)
        beta: Expoente da lei (default: 0.35)
    
    Returns:
        (scaler, mode_allocation)
    """
    MODE_CONFIGS = {
        "express": {"budget": 30, "max_workers": 1, "timeout": 30},
        "standard": {"budget": 60, "max_workers": 2, "timeout": 60},
        "magnum": {"budget": 100, "max_workers": 4, "timeout": 120},
        "research": {"budget": 200, "max_workers": 8, "timeout": 240},
    }
    
    config = MODE_CONFIGS.get(mode.lower(), MODE_CONFIGS["standard"])
    scaler = InferenceScaler(alpha=alpha, beta=beta)
    allocation = scaler.allocate_mode_budget(mode, config)
    
    return scaler, allocation


# =====================================================================
# MAIN — Demonstração e autoverificação
# =====================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("INFERENCE SCALER — Demonstration")
    print("=" * 60)
    
    scaler = InferenceScaler()
    
    # 1. Lei de potência
    print("\n--- 1. Lei de Potência PCI(compute) ---")
    for c in [1, 5, 10, 30, 60, 100, 200]:
        pci = scaler.predict_pci(c)
        gain = scaler.marginal_gain(c, 1.0)
        dim = " ✓" if scaler.diminishing_threshold(c) else ""
        print(f"  compute={c:3d}: PCI={pci:7.2f},  marginal_gain={gain:.4f}{dim}")
    
    # 2. Alocação adaptativa
    print("\n--- 2. Alocação Adaptativa por Modo ---")
    for mode_name, cfg in [
        ("express", {"budget": 30, "max_workers": 1, "timeout": 30}),
        ("standard", {"budget": 60, "max_workers": 2, "timeout": 60}),
        ("magnum", {"budget": 100, "max_workers": 4, "timeout": 120}),
        ("research", {"budget": 200, "max_workers": 8, "timeout": 240}),
    ]:
        result = scaler.allocate_mode_budget(mode_name, cfg)
        budgets = ", ".join(f"F{i}={result['phase_budgets'][i]:.0f}"
                           for i in range(1, 8))
        print(f"  {mode_name:8s} (budget={cfg['budget']:3d}): "
              f"PCI_esp={result['expected_pci']:.1f}, "
              f"improvement={result['improvement_pct']:.1f}%")
        print(f"           budgets: [{budgets}]")
    
    # 3. Calibração
    print("\n--- 3. Calibração (dados sintéticos perfeitos) ---")
    observed = [
        {"compute": c, "pci": 35.0 * (c ** 0.35)}
        for c in [1, 2, 5, 10, 20, 30, 50, 80, 100]
    ]
    cal = scaler.calibrate(observed)
    print(f"  α recuperado: {cal['alpha']:.4f} (original: 35.0)")
    print(f"  β recuperado: {cal['beta']:.4f} (original: 0.35)")
    print(f"  R²: {cal['r_squared']:.6f}")
    print(f"  Pontos: {cal['n_points']}")
    
    # 4. Diminishing returns por modo
    print("\n--- 4. Diminishing Returns Threshold ---")
    for c in [10, 30, 60, 100, 200]:
        dim = scaler.diminishing_threshold(c)
        gain = scaler.marginal_gain(c, 1.0)
        pci = scaler.predict_pci(c)
        ratio = gain / pci * 100
        print(f"  compute={c:3d}: gain/PCI={ratio:.2f}%, "
              f"diminishing={dim}")
    
    print("\n✅ InferenceScaler pronto para integrar com ParallelOrchestrator v12.")
