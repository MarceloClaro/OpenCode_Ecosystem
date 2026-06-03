# Workflow Architect

Agente especializado em design de arvores de workflow. Mapeia todos os caminhos (happy path, branches, failure modes, timeout), define contratos de handoff entre servicos e valida completude.

## Uso
```python
from workflow_architect_engine import WorkflowTree, Step, HandoffContract
```

## CTs (4)
1. Workflow completeness -- deteccao de steps sem success path
2. Handoff contract validation -- schemas e endpoints REST
3. Full workflow tree -- 3 steps com todos os branches
4. Missing handoff detection -- aviso para multi-step sem handoffs

## Dependencias
Python 3.12, stdlib only (dataclasses, enum, typing).
