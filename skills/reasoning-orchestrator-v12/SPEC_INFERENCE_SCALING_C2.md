# SPEC — Ciclo 2: Inference-Time Scaling

**Versão:** 2.0.0  
**Base:** Ciclo 1 (ParallelDispatch) — speedup 1.93x intra-fase  
**Pipeline:** ParallelDispatch → InferenceScaler → ParallelOrchestrator  
**Status:** SDD — Especificação para implementação

---

## Índice

1. [Objetivo](#1-objetivo)
2. [Arquitetura](#2-arquitetura)
3. [InferenceScaler — Contrato](#3-inferencescaler--contrato)
4. [Lei de Potência PCI(compute)](#4-lei-de-potência-pcicompute)
5. [Alocação Adaptativa por Otimização Marginal](#5-alocação-adaptativa-por-otimização-marginal)
6. [Calibração da Lei (Regressão Log-Log)](#6-calibração-da-lei-regressão-log-log)
7. [Integração com ParallelOrchestrator](#7-integração-com-parallelorchestrator)
8. [Modelo de Pesos por Fase](#8-modelo-de-pesos-por-fase)
9. [Testes TDD](#9-testes-tdd)
10. [Critérios de Aceitação](#10-critérios-de-aceitação)

---

## 1. Objetivo

Implementar alocação adaptativa de recursos de raciocínio baseada em **scaling law**: o orçamento de computação (budget) é distribuído entre as 7 fases do pipeline de forma a maximizar o **PCI (Proof Confidence Index)** resultante.

**Problema resolvido:** Na v11 e Ciclo 1, o budget é fixo por modo (Standard=60, Magnum=100) e distribuído uniformemente entre fases. Fases complexas (F3 Deductive, F5 Cross-Reference) precisam de mais recursos para atingir o mesmo PCI que fases simples (F1 Analysis, F7 Synthesis). O InferenceScaler realoca recursos dinamicamente.

**Ganho esperado:** PCI ≥ +5% sobre alocação uniforme com o mesmo budget total.

---

## 2. Arquitetura

```
ParallelOrchestrator.solve()
  │
  ├── 1. ParallelDispatch (Ciclo 1) — executa fases em paralelo
  │
  ├── 2. InferenceScaler.allocate_budget()        ← NOVO
  │       └── Distribui budget entre fases
  │       └── Otimização marginal
  │
  ├── 3. InferenceScaler.predict_pci()            ← NOVO
  │       └── Estima PCI esperado para o budget
  │
  ├── 4. InferenceScaler.calibrate()              ← NOVO
  │       └── Ajusta α, β com dados observados
  │
  ├── 5. ModeConfig atualizado com budget dinâmico
  │
  └── 6. PCI report inclui: scaling_r², budget_por_fase, ganho_marginal
```

### Fluxo de Decisão

```
Entrada: problema + modo
  │
  ▼
[1] InferenceScaler.allocate_budget(total_budget, fases)
  │   Distribuição inicial: uniforme
  │   Otimização marginal: itera até convergir
  ▼
[2] ParallelDispatch executa com budget_alocado_por_fase
  │   max_workers = f(budget_fase)
  │   timeout = f(budget_fase)
  ▼
[3] InferenceScaler.calibrate(observado)
  │   Regressão linear log-log
  │   R² como métrica de qualidade
  ▼
[4] Report final: PCI_real vs PCI_previsto, scaling_r²
```

---

## 3. InferenceScaler — Contrato

```python
class InferenceScaler:
    """
    Gerencia a scaling law para inferência: PCI = α · compute^β.
    
    Responsabilidades:
    - Prever PCI para dado nível de compute (predict_pci)
    - Alocar budget entre fases para maximizar PCI (allocate_budget)
    - Calibrar α e β a partir de dados observados (calibrate)
    - Computar ganho marginal de realocar recursos (marginal_gain)
    
    Scaling law: PCI(compute) = alpha * (compute ** beta)
    
    Onde:
    - alpha (α): fator de escala base (~35.0)
    - beta  (β): expoente da lei de potência (~0.35, típico 0.2-0.5)
    - compute: unidades de computação (budget total gasto)
    """
    
    DEFAULT_ALPHA = 35.0
    DEFAULT_BETA = 0.35
    
    # Pesos por fase (complexidade relativa)
    PHASE_WEIGHTS = {
        1: 0.8,   # Problem Analysis — simples
        2: 1.0,   # Reasoning Selection — baseline
        3: 1.5,   # Deductive Derivation — complexo
        4: 1.2,   # Inductive Verification — médio
        5: 1.4,   # Cross-Reference — complexo
        6: 1.1,   # Proof Health Check — médio
        7: 0.5,   # Synthesis — simples (1 agente)
    }
    
    def __init__(
        self,
        alpha: float = DEFAULT_ALPHA,
        beta: float = DEFAULT_BETA,
        phase_weights: dict[int, float] = None,
    ):
        ...
    
    def predict_pci(self, compute: float) -> float:
        """Prevê PCI para dado nível de compute: PCI = alpha * compute^beta."""
    
    def allocate_budget(
        self,
        total_budget: int,
        num_phases: int = 7,
        iterations: int = 50,
    ) -> dict[int, float]:
        """
        Aloca budget entre fases via otimização marginal.
        
        Algoritmo:
        1. Distribuição uniforme inicial
        2. Para cada iteração:
           a. Computa ganho marginal por fase: dPCI/d(compute_i)
           b. Move 1 unidade da fase com menor ganho para a de maior ganho
           c. Verifica convergência
        3. Retorna alocação final
        
        Returns:
            dict[fase_num, budget_alocado]
        """
    
    def marginal_gain(
        self,
        phase_budget: float,
        phase_weight: float,
    ) -> float:
        """
        Computa ganho marginal de adicionar compute a uma fase.
        
        dPCI/d(compute_i) = alpha * beta * (peso_i * compute_i)^(beta-1) * peso_i
        """
    
    def calibrate(
        self,
        observed: list[dict],
    ) -> dict:
        """
        Calibra α e β a partir de dados observados.
        
        Args:
            observed: lista de dicts com 'compute' e 'pci'
        
        Método:
        - Regressão linear em escala log-log
        - log(PCI) = log(α) + β * log(compute)
        - Mínimos quadrados ordinários
        
        Returns:
            dict com alpha, beta, r_squared, predictions
        """
    
    def allocate_mode_budget(
        self,
        mode: str,
        mode_config: dict,
    ) -> dict[str, Any]:
        """
        Aloca budget para todas as fases dado um modo.
        
        Retorna configuração estendida com:
        - phase_budgets: budget por fase
        - per_phase_workers: workers por fase
        - expected_pci: PCI esperado
        - estimated_improvement: ganho vs uniforme
        """
```

---

## 4. Lei de Potência PCI(compute)

### 4.1 Formulação

```
PCI(compute) = α · compute^β

Onde:
  α = 35.0  (PCI base para compute=1)
  β = 0.35  (lei sublinear — retornos decrescentes)
```

### 4.2 Valores Típicos

| compute | PCI previsto | Modo | Nota |
|:-------:|:------------:|------|------|
| 1 | 35.0 | — | Base |
| 10 | 78.2 | — | |
| 30 | 113.3 | Express (budget=30) | Teórico; PCI real é normalizado |
| 60 | 140.8 | Standard (budget=60) | Teórico; PCI real é normalizado |
| 100 | 164.8 | Magnum (budget=100) | Teórico; PCI real é normalizado |
| 200 | 205.3 | Research (budget=200) | Teórico; PCI real é normalizado |

**Nota:** Os valores PCI são normalizados para 0-100 internamente. A lei de potência crua produz valores >100 que são clamped.

### 4.3 Retornos Decrescentes

```python
def diminishing_threshold(self, compute: float) -> bool:
    """Retorna True se adicionar mais compute tem retorno marginal < 5%."""
    marginal = self.marginal_gain(compute, 1.0)
    # Se ganho marginal < 5% do PCI atual, retornos diminuíram
    current_pci = self.predict_pci(compute)
    return marginal / max(current_pci, 1) < 0.05
```

---

## 5. Alocação Adaptativa por Otimização Marginal

### 5.1 Algoritmo

```
Entrada: total_budget=100, num_fases=7, max_iter=50

1. Alocação inicial uniforme:
   budget_i = total_budget / num_fases  →  14.3 cada

2. Para iteração de 1 a max_iter:
   a. Para cada fase i:
        gain_i = marginal_gain(budget_i, weight_i)
      
   b. Encontra fase com maior ganho (max_gain) e menor ganho (min_gain)
   
   c. Se max_gain - min_gain < tolerância (0.001):
        → Convergiu. Break.
   
   d. Move 1 unidade:
        budget[max_gain_phase] += 1
        budget[min_gain_phase] -= 1
   
   e. Garante budget mínimo de 1 por fase

3. Retorna alocação final
```

### 5.2 Exemplo de Alocação

Modo Standard (budget=60, 7 fases):

| Fase | Peso | Uniforme | Adaptativa | Delta |
|------|:----:|:--------:|:----------:|:-----:|
| F1 (Analysis) | 0.8 | 8.6 | 6 | -2.6 |
| F2 (Selection) | 1.0 | 8.6 | 8 | -0.6 |
| F3 (Deductive) | 1.5 | 8.6 | 13 | +4.4 |
| F4 (Verification) | 1.2 | 8.6 | 10 | +1.4 |
| F5 (Cross-Ref) | 1.4 | 1.4 | 12 | +3.4 |
| F6 (Health) | 1.1 | 8.6 | 9 | +0.4 |
| F7 (Synthesis) | 0.5 | 8.6 | 2 | -6.6 |

**Insight:** F3 (Deductive) e F5 (Cross-Reference) recebem mais budget porque têm maior complexidade e maior impacto no PCI final. F7 (Synthesis) recebe menos porque é uma fase de consolidação com 1 único agente.

### 5.3 Implementação

```python
def allocate_budget(
    self,
    total_budget: int,
    num_phases: int = 7,
    iterations: int = 100,
    tolerance: float = 0.001,
    min_per_phase: int = 1,
) -> dict[int, float]:
    """
    Aloca budget via otimização marginal.
    
    Args:
        total_budget: Orçamento total (unidades arbitrárias)
        num_phases: Número de fases (default: 7)
        iterations: Máximo de iterações de otimização
        tolerance: Tolerância para convergência
        min_per_phase: Budget mínimo por fase
    
    Returns:
        dict[fase_num (1-indexed): budget_alocado]
    """
    # Inicialização uniforme
    uniform = max(total_budget // num_phases, min_per_phase)
    budget = {i: float(uniform) for i in range(1, num_phases + 1)}
    
    # Garante que soma fecha
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
        
        if gains[max_phase] - gains[min_phase] < tolerance:
            break  # Convergiu
        
        # Move 1 unidade
        if budget[min_phase] > min_per_phase:
            budget[min_phase] -= 1.0
            budget[max_phase] += 1.0
    
    return {k: round(v, 1) for k, v in budget.items()}
```

---

## 6. Calibração da Lei (Regressão Log-Log)

### 6.1 Método

Dados observados: pares (compute_i, pci_i)

1. Transformação logarítmica:
   - log_compute = log(compute_i)
   - log_pci = log(pci_i)

2. Regressão linear (mínimos quadrados ordinários):
   - log_pci = log(α) + β · log_compute
 
3. Extração dos parâmetros:
   - β = slope
   - α = exp(intercept)

4. Métrica de qualidade: R² (coeficiente de determinação)

### 6.2 Implementação

```python
def calibrate(
    self,
    observed: list[dict],
) -> dict:
    """
    Calibra α e β via regressão log-log.
    
    Args:
        observed: [{"compute": float, "pci": float}, ...]
    
    Returns:
        {
            "alpha": float,
            "beta": float,
            "r_squared": float,
            "predictions": [float, ...],
            "n_points": int,
        }
    
    Requer: R² >= 0.85 para aceitação.
    """
    import numpy as np
    
    computes = np.array([o["compute"] for o in observed])
    pcis = np.array([o["pci"] for o in observed])
    
    log_compute = np.log(np.maximum(computes, 1e-10))
    log_pci = np.log(np.maximum(pcis, 1e-10))
    
    # Regressão linear
    A = np.vstack([log_compute, np.ones_like(log_compute)]).T
    beta, log_alpha = np.linalg.lstsq(A, log_pci, rcond=None)[0]
    
    alpha = np.exp(log_alpha)
    
    # R²
    residuals = log_pci - (beta * log_compute + log_alpha)
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((log_pci - np.mean(log_pci)) ** 2)
    r_squared = 1 - ss_res / max(ss_tot, 1e-10)
    
    # Atualiza parâmetros internos
    self.alpha = float(alpha)
    self.beta = float(beta)
    
    predictions = [self.predict_pci(c) for c in computes]
    
    return {
        "alpha": float(alpha),
        "beta": float(beta),
        "r_squared": float(r_squared),
        "predictions": predictions,
        "n_points": len(observed),
    }
```

---

## 7. Integração com ParallelOrchestrator

### 7.1 Método solve() com Scaling

```python
def solve_with_scaling(
    self,
    problem: str,
    budget_override: Optional[int] = None,
) -> SolutionReport:
    """
    Executa pipeline com Inference-Time Scaling.
    
    Diferenças do solve() original:
    1. Aloca budget adaptativamente entre fases
    2. Por fase: define max_workers proporcional ao budget
    3. Registra scaling_r² no relatório
    4. Computa PCI previsto vs PCI real
    """
```

### 7.2 Mapeamento Budget → Workers

| Budget por fase | Workers recomendados |
|:---------------:|:--------------------:|
| < 5 | 1 |
| 5-10 | 2 |
| 10-15 | 3 |
| > 15 | 4 |

### 7.3 SolutionReport Estendido

```python
@dataclass
class SolutionReport:
    # ... campos existentes ...
    scaling_params: dict = field(default_factory=dict)
    # {
    #     "alpha": 35.0,
    #     "beta": 0.35,
    #     "r_squared": 0.92,
    #     "budget_per_phase": {1: 6.0, 2: 8.0, ...},
    #     "predicted_pci": 85.0,
    #     "improvement_over_uniform_pct": 5.3,
    # }
```

---

## 8. Modelo de Pesos por Fase

### 8.1 Pesos e Justificativa

| Fase | Peso | Justificativa |
|------|:----:|---------------|
| 1 — Problem Analysis | 0.8 | 3 agentes, análise inicial rápida |
| 2 — Reasoning Selection | 1.0 | Baseline, 3 agentes de seleção |
| 3 — Deductive Derivation | 1.5 | **Maior complexidade**: 4 agentes, cadeias dedutivas profundas |
| 4 — Inductive Verification | 1.2 | 2 agentes, verificação pode ser cara |
| 5 — Cross-Reference | 1.4 | **Alta complexidade**: 3 agentes, refinamento contraditório |
| 6 — Proof Health Check | 1.1 | 3 agentes, verificação exaustiva |
| 7 — Synthesis | 0.5 | **Menor**: 1 agente, consolidação simples |

### 8.2 Como os Pesos Afetam a Alocação

O ganho marginal é proporcional ao peso da fase:

```
dPCI/d(compute_i) = α · β · (w_i · compute_i)^(β-1) · w_i

Onde w_i é o peso da fase i.
```

Fases com maior peso têm maior derivada marginal e, portanto, recebem mais budget durante a otimização.

---

## 9. Testes TDD

### 9.1 Lista de Testes (C2-T1 a C2-T10)

| ID | Nome | O que testa |
|:--:|------|-------------|
| C2-T1 | `test_pci_prediction` | predict_pci(1)=35, predict_pci(0)=0 |
| C2-T2 | `test_pci_monotonic` | PCI cresce com compute (monotonicidade) |
| C2-T3 | `test_diminishing_returns` | Ganho marginal diminui com compute |
| C2-T4 | `test_uniform_allocation` | allocate_budget produz alocação que soma = total_budget |
| C2-T5 | `test_adaptive_allocation` | F3 recebe mais budget que F7 |
| C2-T6 | `test_allocation_min_per_phase` | Nenhuma fase recebe < min_per_phase |
| C2-T7 | `test_calibrate_r_squared` | R² >= 0.85 para dados sintéticos perfeitos |
| C2-T8 | `test_calibrate_alpha_beta` | α, β recuperam valores originais |
| C2-T9 | `test_allocate_mode_budget` | Modo Magnum aloca budget=100 corretamente |
| C2-T10 | `test_improvement_over_uniform` | PCI adaptativo > PCI uniforme |
| C2-T11 | `test_scaler_integration` | InferenceScaler integrado ao orchestrator |
| C2-T12 | `test_marginal_gain_formula` | Ganho marginal segue fórmula esperada |

### 9.2 Dados de Teste

```python
@pytest.fixture
def scaler():
    return InferenceScaler(alpha=35.0, beta=0.35)

@pytest.fixture
def perfect_data():
    """Dados sintéticos perfeitamente alinhados com a lei de potência."""
    return [
        {"compute": c, "pci": 35.0 * (c ** 0.35)}
        for c in [1, 2, 5, 10, 20, 30, 50, 80, 100]
    ]

@pytest.fixture
def noisy_data():
    """Dados com ruído gaussiano para testar robustez."""
    import random, math
    random.seed(42)
    base = [
        {"compute": c, "pci": 35.0 * (c ** 0.35) * (1 + random.gauss(0, 0.05))}
        for c in [1, 2, 5, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100]
    ]
    return base
```

---

## 10. Critérios de Aceitação

| ID | Critério | Meta | Medição |
|:--:|----------|:----:|---------|
| CA1 | Lei de potência R² | ≥ 0.85 | Regressão log-log |
| CA2 | Alocação adaptativa > uniforme | ≥ +5% PCI | Comparação com mesmo budget |
| CA3 | PCI previsto vs real | erro ≤ 10% | MRE (Mean Relative Error) |
| CA4 | Soma dos budgets = total | Exato | Verificação aritmética |
| CA5 | α e β recuperados na calibração | erro ≤ 1% | Dados sintéticos perfeitos |
| CA6 | Todos os testes TDD verdes | 12/12 | pytest |
| CA7 | Compatibilidade com orchestrator v12 | Sem quebras | Teste de integração |

---

## Apêndice A: Glossário

| Termo | Definição |
|-------|-----------|
| **Inference-Time Scaling** | Técnica de alocar mais compute durante inferência para melhorar qualidade |
| **Lei de Potência** | PCI = α · compute^β — relação não-linear entre compute e qualidade |
| **Otimização Marginal** | Alocação iterativa que move recursos para fases com maior retorno marginal |
| **Budget** | Unidades arbitrárias de computação (soma de agentes × tempo) |
| **PCI** | Proof Confidence Index (0-100) — métrica de qualidade da solução |
| **MRE** | Mean Relative Error — erro médio relativo entre previsto e real |
| **R²** | Coeficiente de determinação — qualidade do fit da regressão |
