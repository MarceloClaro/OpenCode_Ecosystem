# academic-audit: Auditoria Acadêmica Caixa Branca com Rastreamento Minucioso

**Status**: v1.0.0 | **Categoria**: system | **Tipo**: Auditoria + Logging

## Descrição

Sistema completo de auditoria acadêmica caixa branca que registra **todas** as interações do pesquisador com o ecossistema OpenCode, fornecendo rastreabilidade minuciosa de cada afirmação → evidência → decisão. Compatível com protocolo TSAC (87 palavras banidas), padrões Qualis A1 e paradigmas epistemológicos múltiplos.

## Componentes

| Módulo | Arquivo | Função |
|--------|---------|--------|
| **InteractionLogger** | `interaction_logger.py` | Logging caixa branca de todas as interações (JSONL imutável) |
| **AcademicAuditTrail** | `academic_audit_trail.py` | Trilha de auditoria: parágrafo → evidência → fonte |
| **TokenEconomyMonitor** | `token_economy_monitor.py` | Monitor de consumo de tokens por nível (1/2/3) |

## Uso Rápido

```python
from interaction_logger import get_logger
from academic_audit_trail import AcademicAuditTrail
from token_economy_monitor import TokenEconomyMonitor

# Iniciar sessão
logger = get_logger()
logger.set_paradigm("Pragmatista (mista)")
logger.set_level(2)  # Standard Paper

# Trilha de auditoria
trail = AcademicAuditTrail()
trail.set_paradigm("Pragmatista (mista)")

# Registrar parágrafo + evidência
trail.record_paragraph("P12", "A IA generativa tem transformado...")
trail.record_evidence("P12", "10.1038/s41524-017-0032-0", 
    claim="IA generativa na ciência dos materiais",
    source_type="doi", confidence=0.95)

# Verificar TSAC
trail.run_tsac_check("P12")

# Gerar relatório
report = trail.generate_audit_report(format="markdown")
trail.save()

# Monitor de tokens
monitor = TokenEconomyMonitor(level=2)
monitor.record_usage("INT-0001", estimated_input=500, estimated_output=200)
print(monitor.get_efficiency_report())

# Fechar sessão
logger.close_session()
```

## Estratégias de Economia de Tokens (3 Níveis)

| Nível | Nome | Agentes | Orçamento/Sessão | Economia |
|:-----:|------|:------:|:----------------:|:--------:|
| 1 | Magnum/Tese/Qualis A1 | 43 | 500K tokens | Nenhuma (rigor máximo) |
| 2 | Standard Paper/Q1-Q2 | 20 | 200K tokens | Exigida |
| 3 | Short Communication | 10 | 50K tokens | Máxima |

## Protocolo TSAC

Lista de 87 palavras banidas detectadas automaticamente. Exemplos: "crucial", "essencialmente", "notavelmente", "fundamentalmente", "intrinsecamente".

## Rastreabilidade

Cada interação gera um registro JSONL imutável com:
- `session_id` único
- `interaction_id` sequencial
- Hash SHA-256 para integridade
- Timestamp UTC-3
- Roteamento completo (domínio, fonte, confiança)
- Decisões do pipeline

## Arquivos

- `interaction_logger.py` — Logger caixa branca (append-only JSONL)
- `academic_audit_trail.py` — Trilha de auditoria acadêmica
- `token_economy_monitor.py` — Monitor de economia de tokens
