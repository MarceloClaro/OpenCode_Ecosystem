---
name: symbolic-math
version: "1.0.0"
kind: python
category: reasoning
affinity: {spec-009-d1-matematica: 0.95, spec-010-d2-fisica: 0.90, reasoning-orchestrator: 0.85}
---

# Symbolic Mathematics — SymPy Engine

Computacao simbolica para algebra, calculo, equacoes diferenciais e logica
matematica usando SymPy 1.14.

## Capacidades

- **Algebra Simbolica**: Simplificacao, expansao, fatoracao
- **Calculo**: Derivadas, integrais (definidas/indefinidas), limites, series
- **Equacoes**: Resolucao simbolica de sistemas lineares e nao-lineares
- **Logica Booleana**: Algebra proposicional, tabelas verdade, simplificacao
- **Matrizes**: Operacoes simbolicas, autovalores, decomposicoes
- **Geometria**: Transformacoes, coordenadas, trigonometria simbolica

## Uso

```python
from skills.reasoning.symbolic_math.scripts.sympy_engine import SymPyEngine

engine = SymPyEngine()
result = engine.solve("x**2 + 2*x + 1 = 0")
# result: {"solutions": [-1], "multiplicity": 2}

engine.prove_identity("sin(x)**2 + cos(x)**2 = 1")
# result: {"valid": True}
```

## Ficheiros

- `scripts/sympy_engine.py` — Motor de computacao simbolica
- `scripts/latex_bridge.py` — Conversao LaTeX ↔ SymPy
