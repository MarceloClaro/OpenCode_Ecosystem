---
name: dados-qualitativos
description: "Skill de coleta e gestão de dados qualitativos: entrevistas, grupos focais, observação, narrativas, diários, COREQ checklist, triangulação, protocolos de coleta."
spec: "SPEC-078"
version: "1.0"
category: research
tags: [dados, qualitativos, entrevista, grupo-focal, observacao, diario, coreq, triangulacao]
dependencies: [SPEC-078]
tdd_suite: "tests/test_r34_dados_qualitativos.py"
ct_count: 8
status: active
---

# SPEC-078 — Skill: Coleta e Gestão de Dados Qualitativos

## Objetivo
Prover protocolos operacionais para coleta de dados qualitativos em 6 modalidades: entrevistas, grupos focais, observação, narrativas, diários e documentos. Integrar com métodos fenomenológico, grounded theory, estudo de caso e pesquisa-ação.

## CTs
| CT | Descrição | Status |
|:--:|:----------|:------:|
| CT-01 | SKILL.md existe com frontmatter | ✅ |
| CT-02 | Template: Entrevista Semiestruturada (protocolo) | ✅ |
| CT-03 | Template: Grupo Focal (moderação + análise) | ✅ |
| CT-04 | Template: Observação (participante e não participante) | ✅ |
| CT-05 | Template: COREQ Checklist (32 itens) | ✅ |
| CT-06 | Template: Triangulação de Dados Qualitativos | ✅ |
| CT-07 | Template: Diários e Registros Reflexivos | ✅ |
| CT-08 | Template: Qualidade e Rigor em Dados Qualitativos | ✅ |

## Template 1: Entrevista Semiestruturada (Protocolo Completo)

### Etapas da Coleta
1. **Planejamento**
   - Definir objetivo: o que a entrevista precisa capturar?
   - Elaborar roteiro: 8-12 perguntas abertas, agrupadas por tema
   - Pilotar: testar com 1-2 participantes para ajustar fluência

2. **Recrutamento e Amostragem**
   - Amostragem intencional: selecionar participantes com experiência relevante
   - Tamanho: 15-30 entrevistas para saturação (Guest et al., 2006)
   - Critérios de inclusão/exclusão explícitos

3. **Condução**
   - Duração: 45-90 min (ideal 60 min)
   - Registro: gravação de áudio (com consentimento) + notas de campo
   - Técnicas: escuta ativa, sondagem ("Me conte mais sobre..."), clarificação

4. **Pós-Coleta**
   - Transcrição: verbatim, com marcações de pausa e ênfase
   - De-identificação: remover nomes, locais, dados identificáveis
   - Member checking: devolver transcrição ao participante para validação

### Roteiro Modelo (adaptável)
```
Tema 1: Experiência
1. Me conte como foi sua experiência com [fenômeno].
2. O que foi mais marcante para você?
3. Como você se sentiu durante [evento específico]?

Tema 2: Significado
4. O que [fenômeno] significa para você?
5. Como essa experiência mudou sua forma de ver [aspecto]?
6. Que valores ou crenças foram tocados por essa experiência?

Tema 3: Contexto
7. Como [contexto] influenciou sua experiência?
8. Que pessoas ou recursos foram importantes?
9. O que você faria diferente se pudesse?

Fechamento
10. Há algo mais que você gostaria de compartilhar?
```

## Template 2: Grupo Focal

### Estrutura da Sessão
1. **Composição**: 6-12 participantes, homogêneos no tema, diversos em perspectivas
2. **Duração**: 60-120 min (ideal 90 min)
3. **Moderação**: 1 moderador + 1 observador/notas
4. **Roteiro**: 5-7 perguntas amplas, com sondagens

### Fases do Grupo Focal
| Fase | Duração | Atividade |
|:-----|:-------:|:----------|
| Abertura | 10 min | Apresentações, regras, consentimento |
| Aquecimento | 10 min | Pergunta geral para todos responderem |
| Discussão 1 | 20 min | Pergunta central: explorar tema principal |
| Discussão 2 | 20 min | Pergunta de aprofundamento: contrastes e divergências |
| Discussão 3 | 15 min | Pergunta de síntese: o que ficou? |
| Fechamento | 15 min | Resumo, validação com grupo, agradecimentos |

### Análise de Grupo Focal
1. Transcrição: identificar falantes, sobreposições, tom emocional
2. Mapeamento de consensos: temas com alta concordância
3. Mapeamento de divergências: pontos de tensão ou discordância
4. Dinâmica de grupo: quem falou mais/quem ficou em silêncio?
5. Citação representativa: selecionar falas que capturam o tema

## Template 3: Observação (Participante e Não Participante)

### Tipos de Observação
| Tipo | Papel do Pesquisador | Uso Típico |
|:-----|:---------------------|:------------|
| Participante | Membro do grupo | Etnografia, pesquisa-ação |
| Não participante | Espectador externo | Estudo de comportamento naturalístico |
| Sistemática | Categorias pré-definidas | Observação estruturada |
| Etnográfica | Imersão prolongada | Antropologia, estudos culturais |

### Protocolo de Observação
1. **Pré-observação**: definir foco, categorias, duração
2. **Registro**: notas de campo descritivas (o que vi/ouvi) + reflexivas (o que pensei/senti)
3. **Periodicidade**: mínimo 3 sessões para capturar variação
4. **Saturação**: quando novas observações não acrescentam informação

## Template 4: COREQ Checklist (32 itens)

### Domínio 1: Equipe de Pesquisa e Reflexividade (8 itens)
1. Características da equipe: formação, experiência, vínculo com tema
2. Relação com participantes: conhecimento prévio, percepção do entrevistador

### Domínio 2: Desenho do Estudo (15 itens)
3. Amostragem: intencional, snowball, conveniência
4. Coleta: local, duração, saturação, devolução de transcrições
5. Instrumentos: roteiro, perguntas-guia, repetição de entrevistas

### Domínio 3: Análise e Resultados (9 itens)
6. Análise: número de codificadores, software, temas derivados
7. Resultados: citações representativas, coerência entre dados e achados

## Referências da Skill
- Chand, S.P. (2025). Methods of Data Collection in Qualitative Research. *AERE*, 6(1), 303-317.
- Frontiers in Research Metrics. (2026). Data collection methods in qualitative research. DOI: 10.3389/frma.2026.1778160
- NICE. (2024). Conduct of qualitative research studies. *NICE RWE Framework*.
- Tong, A. et al. (2007). COREQ checklist. *Int J Qual Health Care*, 19(6), 349-357.
- Braun, V. & Clarke, V. (2006). Using thematic analysis in psychology. *Qual Res Psychol*, 3(2), 77-101.
- Charmaz, K. (2014). *Constructing Grounded Theory* (2nd ed.). SAGE.
- Flick, U. (2022). *An Introduction to Qualitative Research* (7th ed.). SAGE.
