---
name: clinical-case-study
description: "Pipeline automatizado para producao de Estudo de Caso Clinico. Gera as 5 secoes obrigatorias (Descricao, Referencial Teorico, Manejo Clinico, Evolucao, Consideracoes Finais) com auditoria caixa branca, TSAC, anti-IA e referencias ABNT com DOI."
user-invocable: true
tags: [psicologia, clinica, estudo-de-caso, TCC, auditoria]
integrated_with: [AcademicAuditTrail, ResearcherScore, NoologicalScanner]
---

# Estudo de Caso Clinico — Pipeline Automatizado

Gera estudos de caso clinico seguindo o roteiro padrao de 5 secoes.

## Estrutura

1. **Descricao do Caso**: contextualizacao, instrumentos, hipoteses diagnosticas
2. **Referencial Teorico**: fundamentacao com citacoes DOI
3. **Manejo Clinico**: estrategias, tecnicas, relacao terapeutica
4. **Evolucao do Caso**: progresso, desafios, follow-up
5. **Consideracoes Finais**: sintese, limitacoes, contribuicoes + Referencias ABNT

## Uso

```python
from clinical_case_study import ClinicalCasePipeline
pipeline = ClinicalCasePipeline(domain="psicologia", paradigm="Fenomenologico")
pipeline.run(case_data={...})
```

## Auditoria Integrada

- TSAC (87 palavras banidas)
- Anti-IA (score >= 95)
- Referencias ABNT com DOI clicavel
- Trilha de evidencias (JSONL + SHA-256)
