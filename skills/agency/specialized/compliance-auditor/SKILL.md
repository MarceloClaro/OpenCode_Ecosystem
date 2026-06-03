# Compliance Auditor

Agente especializado em auditoria de compliance tecnico (SOC 2, ISO 27001, HIPAA, PCI-DSS). Realiza gap assessment, rastreamento de evidencias e analise de severidade de findings.

## Uso
```python
from compliance_auditor_engine import ComplianceFramework, Control, Finding
```

## CTs (4)
1. Framework readiness score -- % de controles conformes
2. Finding severity tracking -- score ponderado por severidade
3. Evidence addition -- anexo de evidencias a findings
4. Risk summary aggregation -- consolidacao cross-control

## Dependencias
Python 3.12, stdlib only (dataclasses, enum, typing, datetime).
