---
name: logic-programming
version: "1.0.0"
kind: python
category: reasoning
affinity: {reasoning-orchestrator: 0.90, cora-debate: 0.85, hybrid-graph-retrieval: 0.80}
---

# Logic Programming — miniKanren Relational Engine

Programacao logica relacional para deducao automatica, consultas em bases
de conhecimento e resolucao de problemas combinatorios via unificacao.

## Capacidades

- **Programacao Relacional**: Relacoes bidirecionais (entrada ↔ saida)
- **Unificacao**: Resolucao de sistemas de equacoes logicas
- **Backtracking**: Busca exaustiva com retorno automatico
- **Geracao**: Geracao de todas as solucoes possiveis
- **Prolog-style**: Sintaxe declarativa estilo Prolog em Python

## Uso

```python
from skills.reasoning.logic_programming.scripts.kanren_engine import KanrenEngine

engine = KanrenEngine()
result = engine.query("parent(john, mary) and parent(mary, ann). ancestor(X, Y) :- parent(X, Y)")
# result: {"solutions": [{"X": "john", "Y": "mary"}, {"X": "john", "Y": "ann"}]}
```

## Ficheiros

- `scripts/kanren_engine.py` — Motor de programacao logica
- `scripts/knowledge_base.py` — Base de conhecimento com persistencia SQLite
