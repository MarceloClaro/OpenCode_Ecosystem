---
name: lgpd-dpo
description: "Agente de protecao de dados (DPO) para conformidade LGPD. Consentimento rastreavel, auditoria de tratamento, registro de operacoes. Integra com code-graph.db para rastrear fluxos de dados pessoais no ecossistema OpenCode."
---

# lgpd-dpo v1.0 — Data Protection Officer (DPO) LGPD

## Quando Usar
- **Consentimento**: Registrar, consultar e revogar consentimentos (Art. 7º, I e Art. 8º)
- **Auditoria**: Rastrear operacoes de tratamento no ecossistema OpenCode
- **Registro**: Manter registro de operacoes (Art. 37)
- **Relatorios**: Gerar relatorios de conformidade para ANPD
- **Incidentes**: Registrar e notificar incidentes (Art. 48)

## Estrutura
```
lgpd-dpo/
  SKILL.md
  dpo_agent.py          # Orquestrador DPO
  consent_manager.py    # Gerenciamento de consentimento
  audit_logger.py       # Registro de operacoes
```

## Instalação
```bash
pip install cryptography
```
