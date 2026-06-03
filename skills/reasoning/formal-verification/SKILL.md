---
name: formal-verification
version: "1.0.0"
kind: python
category: reasoning
affinity: {cora-debate: 0.95, reasoning-orchestrator: 0.90, spec-016-d7-codigo: 0.85}
---

# Formal Verification — Z3 SMT Solver

Prova formal de teoremas, verificacao de modelos e raciocinio matematico assistido
por computador usando Z3 Theorem Prover (Microsoft Research).

## Capacidades

- **SMT Solving**: Satisfiability Modulo Theories (SAT + aritmetica, arrays, bitvectors)
- **Prova de Teoremas**: Verificacao formal de propriedades logicas
- **Model Checking**: Verificacao de sistemas de estados finitos
- **Otimizacao**: MAX-SMT e otimizacao sobre restricoes
- **Geracao de Contraexemplos**: Quando uma propriedade nao e valida

## Uso

```python
from skills.reasoning.formal_verification.scripts.z3_engine import Z3ReasoningEngine

engine = Z3ReasoningEngine()
result = engine.prove("x > 0 and y > 0 implies x + y > 0")
# result: {"status": "valid", "proof": "trivial", "time_ms": 2}
```

## Ficheiros

- `scripts/z3_engine.py` — Motor de raciocinio formal (Z3 wrapper)
- `scripts/smt_bridge.py` — Conversor de linguagem natural para SMT-LIB2
