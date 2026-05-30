---
title: "Cora-Debate — Verificação Simbólica V1-V7"
version: "4.6"
verifiers: 7
self_consistency_k: 7
confidence_threshold: 0.95
---

# Cora-Debate — Verificação Simbólica

## Arquitetura

```
┌──────────────────────────────────────────────────────────────────┐
│                  CORA-DEBATE V1-V7 PIPELINE                        │
│                                                                   │
│  ARGUMENTO ──▶ [V1] ──▶ [V2] ──▶ [V3] ──▶ [V4] ──▶ [V5]         │
│                Lógica   Semântica  Ref      Stats    Cross         │
│                  │         │        │        │        │           │
│                  └─────────┴────────┴────────┴────────┘           │
│                                    │                              │
│                                    ▼                              │
│                              [V6] ──▶ [V7]                       │
│                            Complet.   Original.                   │
│                                │         │                        │
│                                └────┬────┘                        │
│                                     │                             │
│                                     ▼                             │
│                          Q-SCORE UCB1                             │
│                     (seleção adaptativa)                          │
│                                     │                             │
│                                     ▼                             │
│                          SELF-CONSISTENCY K=7                     │
│                     (temperatura adaptativa)                      │
│                                     │                             │
│                                     ▼                             │
│                          CALIBRAÇÃO PLATT                         │
│                     (probabilidade calibrada)                     │
└──────────────────────────────────────────────────────────────────┘
```

## Verificadores

| ID | Nome | Descrição | Tipo | Threshold |
|:--:|------|-----------|:----:|:---------:|
| V1 | Consistência Lógica | Detecta contradições formais (p∧¬p) | Formal | 0.98 |
| V2 | Coerência Semântica | Verifica encadeamento semântico entre sentenças | NLP | 0.95 |
| V3 | Validação de Referências | Cross-check DOIs, autores, títulos | CrossRef | 0.97 |
| V4 | Rigor Estatístico | Verifica p-valores, intervalos de confiança | Stats | 0.96 |
| V5 | Correlação Cruzada | Valida relações entre variáveis reportadas | Pearson | 0.94 |
| V6 | Completude Argumentativa | Verifica se todas as premissas estão cobertas | Struct | 0.93 |
| V7 | Originalidade | Detecta similaridade com fontes existentes | PlagCheck | 0.99 |

## Self-Consistency (K=7)

```
Temperatura 0.1 ──▶ Run 1 ──▶ Score 0.98
Temperatura 0.2 ──▶ Run 2 ──▶ Score 0.97
Temperatura 0.3 ──▶ Run 3 ──▶ Score 0.96
Temperatura 0.4 ──▶ Run 4 ──▶ Score 0.95
Temperatura 0.5 ──▶ Run 5 ──▶ Score 0.94
Temperatura 0.6 ──▶ Run 6 ──▶ Score 0.93
Temperatura 0.7 ──▶ Run 7 ──▶ Score 0.92
                           │
                           ▼
                    VOTO MAJORITÁRIO
                    Calibração Platt
                           │
                           ▼
                    SCORE FINAL
```

## Integração com Agent Forum

```
Forum Engine (P14) ──▶ Debate ──▶ Argument Graph
                                      │
                                      ▼
                              Cora-Debate V1-V7
                                      │
                              ┌───────┴───────┐
                              ▼               ▼
                        Q-Score Update    AutoEvolve Learn
```

## Resultados

| Métrica | Valor |
|---------|:-----:|
| Verificações totais | 38/38 |
| Precisão V1-V7 | 96.4% |
| Recall | 95.1% |
| F1-Score | 95.7% |
| ECE (Expected Calibration Error) | 0.26 |
| Latência média | 2.3s |
