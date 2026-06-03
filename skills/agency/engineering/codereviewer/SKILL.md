---
category: agency
kind: python
version: "1.0.0"
---

# CodeReviewer — Motor de Revisao de Codigo

Evolucao Round 14 (Agency Engineering). Motor de revisao de codigo baseado em regras extraido do agente `engineering-code-reviewer` do repositorio agency-agents.

## Proposito
Analisar codigo-fonte para detectar code smells, complexidade excessiva, padroes inseguros e duplicacao. Opera offline com Python 3.12 stdlib.

## Uso
```python
from codereviewer_engine import CodeReviewer

engine = CodeReviewer()
if engine.available:
    complexity = engine.analyze_complexity(source)
    smells = engine.detect_smells(source)
    security = engine.detect_security_issues(source)
    dups = engine.detect_duplication(source)
```

## Integracao OpenCode
- **MCPs**: code-runner, eslint, sequential-thinking
- **Skills**: code-review, swarm-review, cora-debate
- **Categoria**: agency/engineering
