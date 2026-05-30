---
title: "PhD Auditor — Validação Estatística Rigorosa"
version: "4.6"
components: [NashSolver, StatisticalRigor, QualisA1Auditor, SensitivityAnalyzer, IMRADFormatter]
---

# PhD Auditor — Validação Estatística

## Arquitetura

```
┌──────────────────────────────────────────────────────────────────┐
│                    PHD AUDITOR — ARQUITETURA                       │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  INPUT: Artigo Acadêmico (LaTeX/PDF/Markdown)             │    │
│  └──────────────────────────────────────────────────────────┘    │
│                              │                                    │
│                              ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  STAGE 1: NashSolver                                      │    │
│  │  ┌────────────────────────────────────────────────────┐  │    │
│  │  │ Payoff Matrix N×M → Nash Equilibrium              │  │    │
│  │  │ Algoritmo: Lemke-Howson + Enumeração de suportes  │  │    │
│  │  │ Output: Perfil de equilíbrio (σ₁*, σ₂*, ..., σₙ*) │  │    │
│  │  └────────────────────────────────────────────────────┘  │    │
│  └──────────────────────────────────────────────────────────┘    │
│                              │                                    │
│                              ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  STAGE 2: StatisticalRigor                               │    │
│  │  ┌────────────────────────────────────────────────────┐  │    │
│  │  │ Cohen's d: |μ₁-μ₂|/σ_pooled                        │  │    │
│  │  │ Bonferroni: p < α/k                                 │  │    │
│  │  │ Power Analysis: 1-β ≥ 0.80                          │  │    │
│  │  │ Confidence Intervals: 95% CI                        │  │    │
│  │  │ Shapiro-Wilk: Teste de normalidade                  │  │    │
│  │  └────────────────────────────────────────────────────┘  │    │
│  └──────────────────────────────────────────────────────────┘    │
│                              │                                    │
│                              ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  STAGE 3: QualisA1Auditor                                │    │
│  │  ┌────────────────────────────────────────────────────┐  │    │
│  │  │ 7 critérios ponderados:                            │  │    │
│  │  │ [25%] Originalidade  [20%] Metodologia             │  │    │
│  │  │ [15%] Literatura     [15%] Resultados              │  │    │
│  │  │ [10%] Discussão      [10%] Formatação              │  │    │
│  │  │ [5%]  Relevância                                   │  │    │
│  │  └────────────────────────────────────────────────────┘  │    │
│  └──────────────────────────────────────────────────────────┘    │
│                              │                                    │
│                              ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  STAGE 4: SensitivityAnalyzer                            │    │
│  │  ┌────────────────────────────────────────────────────┐  │    │
│  │  │ OAT (One-At-a-Time): varia cada parâmetro ±10%     │  │    │
│  │  │ Tornado Plot: ordena por impacto                    │  │    │
│  │  │ Robustness Score: 0-100                             │  │    │
│  │  └────────────────────────────────────────────────────┘  │    │
│  └──────────────────────────────────────────────────────────┘    │
│                              │                                    │
│                              ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  STAGE 5: IMRADFormatter                                 │    │
│  │  ┌────────────────────────────────────────────────────┐  │    │
│  │  │ Introduction → Methods → Results → Discussion      │  │    │
│  │  │ TSAC (87 banned words) + CJK zero-tolerance        │  │    │
│  │  └────────────────────────────────────────────────────┘  │    │
│  └──────────────────────────────────────────────────────────┘    │
│                              │                                    │
│                              ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  OUTPUT: Score Qualis A1 + Audit Trail + PDF              │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

## NashSolver — Equilíbrio de Nash

| Parâmetro | Valor |
|-----------|-------|
| Jogadores | N (2-10) |
| Estratégias | M (2-100) |
| Algoritmo | Lemke-Howson |
| Complexidade | O(Mⁿ) |
| Convergência | Garantida para jogos finitos |

### Exemplo: Payoff Matrix 2×2

| | Coluna A | Coluna B |
|---|:---:|:---:|
| **Linha A** | (3,2) | (0,0) |
| **Linha B** | (0,0) | (2,3) |

**Equilíbrios:** (A,A) e (B,B) — Jogo de Coordenação

## StatisticalRigor

| Teste | Fórmula | Threshold |
|-------|---------|:---------:|
| Cohen's d | $d = \frac{|\bar{x}_1 - \bar{x}_2|}{s_{pooled}}$ | \|d\| ≥ 0.8 (large) |
| Bonferroni | $p_{adj} = p \times k$ | p < 0.05/k |
| Power | $1-\beta = P(\text{reject } H_0 \mid H_1)$ | ≥ 0.80 |
| Shapiro-Wilk | $W = \frac{(\sum a_i x_{(i)})^2}{\sum (x_i - \bar{x})^2}$ | p > 0.05 |
| Mann-Whitney | $U = n_1 n_2 + \frac{n_1(n_1+1)}{2} - R_1$ | Não-paramétrico |

## QualisA1Auditor — 7 Critérios

```
┌───────────────────────────────────────────────────────────┐
│                 QUALIS A1 SCORING                          │
│                                                            │
│  Originalidade   ██████████████████████████ 25%  24/25     │
│  Metodologia     ████████████████████       20%  19/20     │
│  Literatura      ████████████████           15%  14/15     │
│  Resultados      ████████████████           15%  14/15     │
│  Discussão       ██████████                 10%   9/10     │
│  Formatação      ██████████                 10%  10/10     │
│  Relevância      █████                      5%   5/5      │
│  ─────────────────────────────────────────                │
│  TOTAL                                      100%  95/100   │
└───────────────────────────────────────────────────────────┘
```

## Configuração

```bash
python skills/agent-forum/scripts/phd_auditor.py \
  --input artigo.pdf \
  --mode full \
  --nash-players 2 \
  --bonferroni-correction 10 \
  --qualis-threshold 95
```
