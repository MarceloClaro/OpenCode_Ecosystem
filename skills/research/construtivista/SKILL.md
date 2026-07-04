---
name: construtivista
description: "Skill de análise construtivista: ciclo de aprendizagem (assimilação-acomodação), design construtivista para MAS, protocol enforcement e evolução em runtime."
spec: "SPEC-074"
version: "1.0"
category: research
tags: [paradigma, construtivista, piaget, epistemologia-genetica, mas-design, runtime-evolution]
dependencies: [SPEC-074]
tdd_suite: "tests/test_r32_paradigmas.py"
ct_count: 7
status: active
---

# SPEC-074 — Skill: Análise Construtivista

## Objetivo
Aplicar o paradigma construtivista à análise e design de sistemas multi-agente: ciclos de aprendizagem (assimilação-acomodação), design de protocolos emergentes, gerenciamento de entropia evolutiva e enforcement mecânico de protocolos.

## CTs
| CT | Descrição | Status |
|:--:|:----------|:------:|
| CT-01 | SKILL.md existe com frontmatter | ✅ |
| CT-02 | Template: Ciclo de Aprendizagem Construtivista (assimilação-acomodação) | ✅ |
| CT-03 | Template: Design Construtivista para MAS | ✅ |
| CT-04 | Protocolo de mechanical enforcement (Harmonist) | ✅ |
| CT-05 | Template: Análise de entropia evolutiva (LSS) | ✅ |
| CT-06 | Template: Mapa de equilibração progressiva | ✅ |
| CT-07 | Template: Avaliação de auto-organização semântica | ✅ |

## Template 1: Ciclo de Aprendizagem Construtivista (Piaget)

### Fases do Ciclo
1. **Assimilação**: O agente interpreta nova informação dentro de esquemas existentes
   - Identificar esquema ativo: qual estrutura de conhecimento atual está sendo aplicada?
   - Mapear estímulo: como o input se encaixa no esquema existente?
   - Documentar tensão: há resistência ou conflito cognitivo?

2. **Desequilíbrio**: Conflito cognitivo entre esquema atual e nova experiência
   - Identificar anomalia: o que não se encaixa?
   - Medir gap: diferença entre predição e observação
   - Registrar perturbação: intensidade do desequilíbrio (1-5)

3. **Acomodação**: Modificação do esquema para incorporar nova informação
   - Propor novo esquema: como reestruturar?
   - Testar em ambiente simulado: quais as consequências?
   - Consolidar: integrar ao repertório do agente

4. **Equilibração**: Estabilização do novo esquema
   - Validar consistência interna: o novo esquema é coerente?
   - Verificar generalização: aplica-se a outros contextos?
   - Registrar evolução: documentar a transformação

## Template 2: Design Construtivista para MAS (CDM-S Adaptado)

### Princípios CDM-S (Thórisson et al.)
1. **Decomposição funcional**: Separar o sistema em componentes com responsabilidades claras
2. **Encapsulamento de conhecimento**: Cada componente encapsula seu próprio domínio de conhecimento
3. **Interação mediada por protocolos**: Componentes comunicam-se via protocolos explícitos
4. **Evolução por experiência**: O sistema modifica seu comportamento baseado em interações passadas
5. **Múltiplas perspectivas**: Cada agente mantém seu próprio modelo do mundo
6. **Coordenação emergente**: A coordenação global emerge de interações locais
7. **Reflexão sobre o próprio conhecimento**: O sistema monitora e modifica seus próprios esquemas
8. **Aprendizado ativo**: O sistema busca ativamente novas experiências
9. **Avaliação contínua**: O sistema avalia constantemente a adequação de seus esquemas

### Protocolo de Mechanical Enforcement (Harmonist-style)
```
1. Declarar protocolo: definir regras em frontmatter (strict/persona)
2. Implementar hooks: sessionStart, afterFileEdit, subagentStart, subagentStop, stop
3. Mecanismo de gate: stop hook retorna followup_message e recusa completar turno
4. Verificação: auditoria pós-turno de conformidade com protocolo
5. Registro: logging de todas as violações de protocolo para análise evolutiva
```

## Template 3: Análise de Entropia Evolutiva (LSS)

### Três Camadas de Entropia
1. **Context Entropy** (View/Context Engineering)
   - Gerenciar ambiente de execução
   - Manter Views relevantes para a tarefa
   - Controlar span de atenção do sistema

2. **Self-Organization Entropy** (Structure Engineering)
   - Organizar artefatos e agentes
   - Habilitar descoberta dinâmica de capacidades
   - Gerenciar binding dinâmico entre componentes

3. **Evolutionary Entropy** (Evolution Engineering)
   - Gerenciar lifecycle de artefatos auto-reescritos
   - Controlar taxa de mutação estrutural
   - Preservar identidade funcional durante evolução

## Template 4: Mapa de Equilibração Progressiva

| Nível | Estado | Descrição | Ação do Agente |
|:-----:|:-------|:----------|:---------------|
| N0 | Equilibração inicial | Esquemas estáveis, sem conflito | Operação normal |
| N1 | Perturbação | Anomalia detectada | Registrar anomalia |
| N2 | Desequilíbrio | Esquema existente falha | Iniciar busca |
| N3 | Exploração | Novos padrões testados | Experimentação ativa |
| N4 | Acomodação | Novo esquema formado | Reestruturação |
| N5 | Equilibração majorante | Novo equilíbrio, mais complexo | Consolidação |

## Template 5: Avaliação de Auto-Organização Semântica

1. **Topologia dinâmica**: O sistema reconfigure sua estrutura de comunicação baseado na tarefa?
2. **Especialização emergente**: Os agentes desenvolvem papéis especializados sem design prévio?
3. **Memória de longo prazo**: O sistema retém e reutiliza experiências passadas?
4. **Reflexão**: O sistema monitora seu próprio processo de aprendizagem?
5. **Transferência**: O sistema aplica conhecimento de um domínio em outro?

## Referências da Skill
- GammaLabTechnologies. (2026). Harmonist: Portable AI agent orchestration. GitHub.
- Zhang et al. (2026). LSS: Loosely-Structured Software. arXiv:2603.15690.
- Thórisson, K. et al. CDM-S: Constructionist Design Methodology for Simulation.
- Piaget, J. (1970). Genetic Epistemology. Columbia University Press.
- von Glasersfeld, E. (1995). Radical Constructivism. Routledge.
- Huang, Y. (2026). Eco-Evolve. Preprints 2026030129.
