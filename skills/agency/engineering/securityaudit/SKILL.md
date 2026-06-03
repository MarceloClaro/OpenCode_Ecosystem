---
category: agency
kind: python
version: "1.0.0"
---

# SecurityAuditEngine — Motor de Auditoria de Seguranca

Evolucao Round 14 (Agency Engineering). Motor de auditoria estatica extraido do agente `engineering-security-engineer` do repositorio agency-agents.

## Proposito
Detectar secrets hardcoded, SQL injection, XSS e deficiencias de autenticacao em codigo-fonte. Opera offline com Python 3.12 stdlib.

## Uso
```python
from securityaudit_engine import SecurityAuditEngine

engine = SecurityAuditEngine()
if engine.available:
    secrets = engine.detect_secrets(source)
    sqli = engine.detect_sql_injection(source)
    xss = engine.detect_xss(source)
    auth = engine.audit_authentication(source)
```

## Integracao OpenCode
- **MCPs**: eslint, code-runner, sequential-thinking
- **Skills**: security-reviewer, secure-code-guardian, security-and-hardening
- **Categoria**: agency/engineering
