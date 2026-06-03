# Blockchain Security Auditor

Agente especializado em auditoria de seguranca de smart contracts. Detecta vulnerabilidades conhecidas (reentrancy, unchecked calls, overflow, tx.origin, timestamp), calcula risk scores e gera relatorios estruturados.

## Uso
```python
from blockchain_auditor_engine import ContractAudit, scan_patterns
```

## CTs (4)
1. Vulnerability risk scores -- ponderacao por severidade
2. Aggregate risk score -- media ponderada de findings
3. Pattern scanning -- deteccao em codigo Solidity
4. Report generation -- estrutura completa de auditoria

## Dependencias
Python 3.12, stdlib only (dataclasses, enum, typing).
