---
name: psicologia-clinica
description: "Skill de análise em Psicologia Clínica: avaliação psicológica multiagente, psicodiagnóstico DSM-5/ICD-11, integração com métodos qualitativos e paradigmas fenomenológico/construtivista."
spec: "SPEC-077"
version: "1.0"
category: research
tags: [dominio, psicologia-clinica, dsm-5, psicodiagnostico, saude-mental, wise-mind, agent-mental, multiagente-clinico]
dependencies: [SPEC-077]
tdd_suite: "tests/test_r34_dominio_psicologia_clinica.py"
ct_count: 8
status: active
---

# SPEC-077 — Skill: Análise em Psicologia Clínica

## Objetivo
Aplicar o domínio da Psicologia Clínica como contexto de validação para métodos qualitativos e paradigmas epistemológicos do ecossistema. Integrar frameworks multiagente de avaliação psicológica (WiseMind, AgentMental, AI Psychiatrist Assistant) com métodos fenomenológicos, grounded theory e estudo de caso.

## CTs
| CT | Descrição | Status |
|:--:|:----------|:------:|
| CT-01 | SKILL.md existe com frontmatter | ✅ |
| CT-02 | Template: Avaliação Psicológica Multiagente (WiseMind) | ✅ |
| CT-03 | Template: Psicodiagnóstico DSM-5 Estruturado | ✅ |
| CT-04 | Template: Integração com Métodos Qualitativos | ✅ |
| CT-05 | Template: Entrevista Clínica Semi-estruturada | ✅ |
| CT-06 | Template: Análise de Psicopatologia | ✅ |
| CT-07 | Template: Integração com Neurociências Clínicas | ✅ |
| CT-08 | Template: Relatório Psicológico Baseado em Agentes | ✅ |

## Template 1: Avaliação Psicológica Multiagente (WiseMind-style)

### Arquitetura WiseMind (Wu et al., 2026, npj Digital Medicine)
1. **Reasonable Mind Agent**: Raciocínio baseado em evidências
   - Mapear sintomas para critérios DSM-5 via grafo de conhecimento estruturado
   - Realizar diagnóstico diferencial: descartar condições com base em critérios de exclusão
   - Calcular probabilidades diagnósticas: quais transtornos são mais prováveis?

2. **Emotional Mind Agent**: Comunicação empática
   - Avaliar tom emocional do paciente: angústia, ansiedade, defensividade
   - Adaptar linguagem: validar emoções vs. confrontar distorções
   - Manter aliança terapêutica: rapport e confiança

3. **Knowledge Graph (DSM-5)**: Base de conhecimento estruturada
   - Nós: sintomas, critérios, transtornos, fatores de risco
   - Arestas: critério → transtorno (relação de diagnóstico), sintoma ↔ critério
   - Inferência: dada uma combinação de sintomas, quais critérios são satisfeitos?

4. **Protocolo de Avaliação**:
   ```
   1. Anamnese inicial → Reasonable Mind Agent mapeia queixas para DSM-5
   2. Questionamento direcionado → Emotional Mind Agent adapta tom
   3. Diagnóstico diferencial → Knowledge Graph testa hipóteses
   4. Devolução → Meta-review agent integra achados
   5. Recomendação → Encaminhamento terapêutico baseado em evidências
   ```

## Template 2: Psicodiagnóstico DSM-5 Estruturado (DSM5AgentFlow-style)

### Etapas do Psicodiagnóstico
1. **Entrevista de Abertura** (10-15 min)
   - Queixa principal: "O que te traz aqui hoje?"
   - História da queixa: início, duração, fatores precipitantes
   - Impacto funcional: como afeta trabalho, relações, autocuidado?

2. **Investigação de Critérios** (DSM-5-TR)
   - Mapear sintomas para critérios diagnósticos específicos
   - Usar perguntas validadas: PHQ-9 (depressão), GAD-7 (ansiedade), MINI (entrevista diagnóstica)
   - Diferenciar: transtorno primário vs. comorbidade

3. **Diagnóstico Diferencial**
   | Condição | Sintomas-chave | Critério Exclusão |
   |:---------|:---------------|:------------------|
   | Depressão Maior | Humor deprimido, anedonia ≥2 semanas | Episódio misto, abuso de substâncias |
   | TAG | Preocupação excessiva ≥6 meses | Ataques de pânico, obsessões |
   | TEPT | Revivência, esquiva, hipervigilância | Exposição a trauma |

4. **Devolução e Plano**
   - Explicar diagnóstico em linguagem acessível
   - Propor opções de tratamento (TCC, medicamentoso, combinado)
   - Estabelecer metas terapêuticas

## Template 3: Integração com Métodos Qualitativos

1. **Fenomenologia + Psicologia Clínica** (SPEC-070 + SPEC-076)
   - Descrever estrutura da experiência do paciente: como o transtorno é vivido?
   - Identificar essências: o que é invariante na experiência? (ex.: na depressão: peso, lentificação, vazio)
   - Aplicar epoché clínica: suspender juízo diagnóstico para acessar a experiência

2. **Grounded Theory + Psicologia Clínica** (SPEC-071)
   - Desenvolver teoria substantiva sobre mecanismos de enfrentamento
   - Coding aberto: categorizar estratégias de pacientes
   - Coding axial: relacionar condições, contextos e consequências

3. **Estudo de Caso + Psicologia Clínica** (SPEC-072)
   - Descrever trajetória clínica individual em profundidade
   - Triangulação: múltiplas fontes (paciente, família, equipe, testes)
   - Análise longitudinal: mudança ao longo do tratamento

## Template 4: Entrevista Clínica Semi-estruturada

### Roteiro de Entrevista (adaptado de NICE, 2024; COREQ)
1. **Abertura** (5 min)
   - Apresentação, esclarecimento do propósito, consentimento
   - Construção de rapport: perguntas neutras iniciais

2. **Exploração da Queixa** (20-30 min)
   - Perguntas abertas: "Me conte como foi a última semana"
   - Investigação de sintomas: frequência, intensidade, duração
   - Exploração de contexto: ambiental, social, profissional

3. **História Pessoal e Familiar** (10 min)
   - Histórico de tratamento anterior
   - Antecedentes familiares de transtorno mental
   - Eventos de vida significativos

4. **Fechamento** (5 min)
   - Resumo da compreensão compartilhada
   - Próximos passos: avaliação complementar, encaminhamento
   - Validação: "Há algo mais que você gostaria de acrescentar?"

## Referências da Skill
- Wu, Y. et al. (2026). WiseMind: a knowledge-guided multi-agent framework for psychiatric diagnosis. *npj Digital Medicine*. DOI: 10.1038/s41746-026-02559-9
- Hu, J. et al. (2026). AgentMental: Interactive Multi-Agent Framework for Mental Health Assessment. *AAAI 2026*. DOI: 10.1609/aaai.v40i37.40365
- Greene et al. (2026). AI Psychiatrist Assistant. *PMLR 297*, 525-542.
- DSM5AgentFlow. (2025). Trustworthy AI Psychotherapy. arXiv:2508.11398.
- American Psychiatric Association. (2022). *DSM-5-TR*.
- Tong, A. et al. (2007). COREQ checklist. *Int J Qual Health Care*, 19(6), 349-357.
