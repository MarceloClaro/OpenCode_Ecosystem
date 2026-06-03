# Automation Governance Architect

Agente especializado em governanca de automacoes. Avalia riscos via regras configuraveis, gerencia cadeias de aprovacao com roles obrigatorios e valida se uma automacao pode prosseguir.

## Uso
```python
from automation_governance_engine import GovernanceEngine, GovernanceRule, ApprovalChain
```

## CTs (4)
1. Rule evaluation -- operadores >, <, ==, !=, in, contains
2. Risk assessment pipeline -- multiplas regras, risco maximo
3. Approval chain validation -- roles obrigatorios e opcionais
4. End-to-end governance -- risco + aprovacao combinados

## Dependencias
Python 3.12, stdlib only (dataclasses, enum, typing).
