---
category: agency
kind: python
version: "1.0.0"
---

# MinimalChangeEngine — Validador de Diffs Minimos

Evolucao Round 14 (Agency Engineering). Motor de validacao de diffs extraido do agente `engineering-minimal-change-engineer` do repositorio agency-agents.

## Proposito
Analisar patches/diffs para detectar scope creep, refatoracoes prematuras e mudancas cosméticas desnecessarias.

## Uso
```python
from minimalchange_engine import MinimalChangeEngine

engine = MinimalChangeEngine()
if engine.available:
    scope = engine.check_scope(diff_text, ["src/auth.py"])
    refactor = engine.detect_premature_refactor(diff_text)
    entropy = engine.measure_entropy(diff_text)
    ratio = engine.validate_change_ratio(diff_text)
```

## Integracao OpenCode
- **MCPs**: diff, filesystem, sequential-thinking
- **Skills**: incremental-implementation, code-review, decisionnode
- **Categoria**: agency/engineering
