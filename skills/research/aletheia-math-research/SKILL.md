---
name: aletheia-math-research
description: >
  Agente de pesquisa matematica autonoma baseado em Aletheia (Feng et al., 2026).
  Implementa loop Generator-Verifier-Reviser com verificacao Cora-Debate V1-V7
  e desacoplamento thinking/output. Atinge nivel L2 (Publishable Research) em
  dominios de teoria dos numeros, combinatoria, algebra e geometria.
  Use quando precisar resolver problemas matematicos de pesquisa, gerar provas
  autonomas, ou conduzir investigacao cientifica com verificacao iterativa.
spec: "SPEC-012"
version: "1.0"
category: research
tags: [aletheia, mathematics, research, generator-verifier, cora-debate, autonomous-science]
dependencies: [SPEC-001, CORA-Eval, cora-debate, reasoning-orchestrator-v11]
tdd_suite: "scripts/aletheia_engine.py"
ct_count: 10
reference: "Feng, T. et al. (2026). Towards Autonomous Mathematics Research. arXiv:2602.10177v3."
status: active
---

# Aletheia Math Research Engine

## Arquitetura

```
PROBLEM ──▶ [GENERATOR] ──▶ [VERIFIER (Cora V1-V7)] ──▶ pass? ──▶ SOLUTION
                ▲                      │                    │
                │                      ▼ fail               │
                └────── [REVISER] ◀────┘                    │
                        (feedback loop)                     │
                max_attempts = 10 (hyperparameter)          │
```

## 3 Subagentes

| Subagente | Funcao | Inspiracao |
|-----------|--------|------------|
| **Generator** | Produz solucao em linguagem natural com 16 tipos de raciocinio | Feng et al. §2.2 |
| **Verifier** | Verifica via Cora-Debate V1-V7 + deteccao de alucinacoes | Feng et al. §2.2 |
| **Reviser** | Corrige flaws identificados pelo Verifier | Feng et al. §2.1 |

## Benchmark (5 problemas)

| ID | Dominio | Dificuldade |
|:---|:---|:---|
| IMO-2024-P1 | Number Theory | Olympiad |
| Erdos-1051 | Combinatorics | Research Open |
| FutureMath-Basic-1 | Algebra | PhD Exercise |
| Thue-Morse | Combinatorics | Olympiad |
| Goldbach-Variant | Number Theory | Research Open |

## Uso

```python
from aletheia_engine import AletheiaEngine, MathProblem

engine = AletheiaEngine(max_attempts=10, strictness=0.7)
problem = MathProblem(
    id="My-Problem",
    statement="Prove that...",
    domain="number_theory",
    difficulty="research_open"
)
session = engine.solve(problem)
print(session.status, session.final_solution)
```

## Referencia Principal

Feng, T., Trinh, T.H., Bingham, G. et al. (2026).
**Towards Autonomous Mathematics Research.**
arXiv:2602.10177v3 [cs.LG].
Google DeepMind Superhuman Reasoning Team.
