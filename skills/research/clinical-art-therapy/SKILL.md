---
name: clinical-art-therapy
description: "Validacao clinica do ecossistema OpenCode no dominio da arteterapia decolonial. Pipeline de analise multiagente para pesquisa qualitativa com familiares de criancas neurodivergentes, integrando Cora-Debate, PhD Auditor e protocolos eticos (CEP/TCLE/LGPD)."
version: 1.0.0
author: ecosystem
license: MIT
tags: [clinical, art-therapy, decolonial, neurodivergence, qualitative-research, ethics, nise-da-silveira]
compatibility: deepseek-v4-pro, OpenCode, Claude Code, Cursor
user-invocable: true
---

# clinical-art-therapy v1.0 — Validacao Clinica em Arteterapia Decolonial

## Quando Usar

- **Pesquisa qualitativa em arteterapia**: Analise de sessoes terapeuticas com producao visual, textual e comportamental
- **Parentalidade atipica**: Estudos com familiares de criancas neurodivergentes (TEA, TDAH, altas habilidades)
- **Abordagem decolonial**: Pesquisas que articulam pensamento decolonial latino-americano com praticas clinicas
- **Analise de grupo terapeutico**: Investigacao de dinamicas grupais, pertencimento e redes de apoio
- **Producao artistica como dado**: Analise de desenhos, pinturas, modelagem e outras expressoes visuais
- **Etica em pesquisa qualitativa**: Submissao a CEP, elaboracao de TCLE, anonimizacao de dados
- **Revisao sistematica**: Busca estruturada em bases como PubMed, SciELO, LILACS, PePSIC
- **Triangulacao de metodos**: Integracao de dados visuais, textuais e observacionais

## Tema Central

A arteterapia decolonial, herdeira do legado de Nise da Silveira (1905-1999), propoe uma clinica que recusa a patologizacao das diferencas e valoriza a expressao criativa como via legitima de conhecimento. Inspirada pelo pensamento decolonial latino-americano (Quijano, 2000; Santos, 2019; Martin-Baro, 1994) e pela pedagogia freireana (Freire, 1987), esta abordagem posiciona o fazer artistico como pratica etico-politica que questiona as estruturas de poder produtoras de sofrimento psiquico em populacoes marginalizadas -- em especial, familiares de criancas neurodivergentes.

Este skill implementa um pipeline completo de analise clinica quanti-qualitativa, desde a triagem etica ate a geracao de relatorio, com verificacao formal interetapas por agentes especializados do ecossistema OpenCode.

---

## Indice

1. [Clinical Pipeline (8 estagios)](#1-clinical-pipeline-8-estagios)
2. [Decolonial Art Therapy Framework](#2-decolonial-art-therapy-framework)
3. [Integracao com o Ecossistema OpenCode](#3-integracao-com-o-ecossistema-opencode)
4. [Protocolo Etico](#4-protocolo-etico)
5. [Exemplo de Uso Completo](#5-exemplo-de-uso-completo)
6. [Referencias e Citacoes](#6-referencias-e-citacoes)

---

## 1. Clinical Pipeline (8 estagios)

Cada estagio do pipeline produz artefatos especificos que alimentam o estagio seguinte. O pipeline inteiro e orquestrado pelo agente Writer com verificacao cruzada pelo Cora-Debate V1-V6.

### Estagio 1: Intake e Protocolo Etico

**Entrada**: Participantes, contexto institucional, modalidade de intervencao

**Saida**: Documentos eticos aprovados (CEP, TCLE, termo de assentimento)

**Tarefas**:
1. Verificar conformidade com CNS Resolucao 466/2012 e 510/2016
2. Gerar minuta de TCLE com linguagem acessivel (5o ano de escolaridade)
3. Submeter documentacao ao Comite de Etica em Pesquisa (CEP) via Plataforma Brasil
4. Anonimizar identificadores institucionais (servico, municipio, equipe)
5. Registrar consentimentos em blockchain local (hash SHA-256 do TCLE assinado)
6. Configurar pipeline de privacidade LGPD (Lei 13.709/2018)

**Protocolos ativados**:
- SEEKER: busca de modelos de TCLE em bases do CNS
- PhD Auditor: verificacao de conformidade normativa
- Machine States: controle de estado do processo etico (rascunho -> submetido -> aprovado)

**Criterios de inclusao** (do TCC de referencia):
- Familiar cuidador primario de crianca(s) com diagnostico clinico de neurodivergencia (TEA, TDAH ou associado)
- Idade igual ou superior a 18 anos
- Participacao regular em grupo de arteterapia ha pelo menos 3 meses
- Manifestacao voluntaria de interesse apos esclarecimento completo

**Criterios de exclusao**:
- Diagnostico de transtorno psiquiatrico grave em fase aguda que comprometa comunicacao
- Nao integracao ao grupo de familiares do servico

---

### Estagio 2: Codificacao Qualitativa Multiagente

**Entrada**: Diarios de campo etnograficos, transcricoes de sessoes, registros audiovisuais

**Saida**: Matriz de codigos tematicos com niveis de confianca

**Tarefas**:
1. Segmentar o corpus em unidades de significado (trechos de 3-5 linhas)
2. Distribuir segmentos entre 49 agentes de codificacao (cada agente aplica 1 categoria analitica)
3. Cada agente produz: codigo, justificativa textual, citacao literal, nivel de confianca (0-1)
4. Agregar codigos por frequencia, co-ocorrencia e intensidade
5. Gerar matriz tematica: temas | subtemas | frequencia | confianca | citacoes

**Esquema de codificacao** (baseado no TCC):
| Codigo | Descricao |
|--------|-----------|
| SOBRECARGA_CUIDADO | Multiplas terapias, deslocamentos, gestao de agenda |
| DIAGNOSTICO_TARDIO | Periodo de vacancia diagnostica (2-4 anos) |
| IMPACTO_FINANCEIRO | Medicamentos, alimentacao especial, adaptacoes |
| ISOLAMENTO_SOCIAL | Afastamento de rede social e familiar |
| COLONIALIDADE_CUIDADO | Maternidade como sacrificio, culpabilizacao |
| LUTA_DIREITOS | BPC, mediador escolar, passe livre |
| PERTENCIMENTO_GRUPO | Identificacao com outras participantes |
| RESSIGNIFICACAO | Transformacao de experiencia individual em coletiva |
| POTENCIA_CRIATIVA | Expressao artistica como via de elaboracao |
| REDE_APOIO_INFORMAL | Vinculos que transcendem o setting terapeutico |

**Agentes de codificacao**: Cada um dos 49 agentes do MASWOS recebe um subconjunto do corpus com uma lente analitica especifica (ex.: Agente-07 foca em marcadores de colonialidade, Agente-23 foca em expressoes de pertencimento).

---

### Estagio 3: Analise de Sessao Arteterapeutica

**Entrada**: Producoes artisticas (desenhos, pinturas, modelagens), registro fotografico, notas de campo

**Saida**: Relatorio multimodal por sessao (visual + textual + comportamental)

**Tarefas**:
1. **Analise visual**: Descrever elementos compositivos (cores, formas, espaco, textura, simbolos)
2. **Analise textual**: Transcrever e codificar verbalizacoes durante o fazer artistico
3. **Analise comportamental**: Registrar postura, contato visual, tempo de imersao, interacoes
4. **Triangulacao**: Cruzar achados visuais, textuais e comportamentais por sessao
5. **Linha do tempo**: Mapear evolucao das expressoes ao longo dos encontros

**Estrutura da sessao tipo** (do TCC - 3 encontros):

| Encontro | Data | Atividade | Disparador | Material |
|----------|------|-----------|------------|----------|
| 1 | Fev/2026 | Desenho individual | "Como voce se sente sendo responsavel pelo cuidado de seu filho?" | Folha A4, lapis de cor, giz de cera |
| 2 | Mar/2026 | Pintura em tela | "Se hoje voce fosse uma cor, qual seria?" e "Como e sua relacao com seu filho no dia a dia?" | Tintas acrilicas, telas, pinceis |
| 3 | Abr/2026 | Exposicao ao ar livre + devolutiva | Compartilhamento coletivo das producoes | Trabalhos dos encontros anteriores |

**Metricas de engajamento por sessao**:
- Tempo medio de producao artistica (minutos)
- Numero de verbalizacoes espontaneas durante a atividade
- Indicadores de imersao (fluxo, concentracao, pausas)
- Interacoes entre participantes (olhares, comentarios, auxilio mutuo)
- Marcadores de resistencia ou bloqueio expressivo

---

### Estagio 4: Extracao de Padroes e Validacao Cruzada (Cora-Debate V1-V6)

**Entrada**: Matriz tematica do Estagio 2 + relatorios multimodais do Estagio 3

**Saida**: Padroes validados com pontuacao de robustez (Q-Score UCB1)

**Tarefas**:
1. **V1 - Verificador de Consistencia Interna**: Os achados de uma sessao corroboram os de outra?
2. **V2 - Verificador de Coerencia Teorica**: Os padroes encontrados alinham-se com a literatura (Malchiodi, 2012; Philippini, 2020; Silveira, 1992)?
3. **V3 - Verificador de Multiplicidade de Vozes**: Ha diversidade suficiente de perspectivas entre participantes?
4. **V4 - Verificador de Saturação Tematica**: Novos dados acrescentam informacao ou confirmam padroes ja identificados?
5. **V5 - Verificador de Vies Decolonial**: A analise reproduz hierarquias epistemica ou efetivamente as questiona?
6. **V6 - Verificador de Rastreabilidade**: Cada afirmacao tem suporte em citacao literal, nota de campo ou producao visual?

**Saida do debate**:
```yaml
padrao:
  id: "P-004"
  descricao: "Validacao experiencial pelo reconhecimento do outro"
  confianca: 0.92
  q_score: 0.88
  verificadores_aprovados: [V1, V2, V3, V5, V6]
  verificadores_reprovados: [V4]  # Amostra pequena (3 encontros, 1 grupo)
  citacoes_chave:
    - "Eu nao sabia que voce tambem passava por isso. Pensei que era so comigo."
    - "Fazia tempo que ninguem me perguntava como eu estava. So perguntam do meu filho."
  evidencia_visual: "Tela com maes de maos dadas com seus filhos (Encontro 3)"
```

---

### Estagio 5: Rigor Estatistico (PhD Auditor)

**Entrada**: Padroes validados do Estagio 4 + dados quantitativos agregados

**Saida**: Relatorio de significancia clinica (Cohen's d, bootstrap, tamanho de efeito)

**Tarefas**:
1. Calcular tamanhos de efeito para variaveis pre-post (onde aplicavel):
   - Percepcao de suporte social (escala analoga visual)
   - Nivel de estresse autorrelatado
   - Frequencia de afetos positivos/negativos nas verbalizacoes
2. Bootstrap com 10.000 reamostragens para intervalos de confianca
3. Cohen's d para magnitude do efeito da intervencao grupal
4. Correlacao de Pearson entre engajamento e desfechos
5. Analise de sensibilidade (jackknife: excluir 1 participante por vez)
6. Correcao de Bonferroni para comparacoes multiplas

**Template de saida**:
| Variavel | Pre (IC95%) | Pos (IC95%) | d de Cohen | IC bootstrap | Significancia |
|----------|-------------|-------------|------------|--------------|---------------|
| Suporte percebido | 3.2 (2.8-3.6) | 4.1 (3.7-4.5) | 0.72 | [0.31, 1.13] | p < 0.05 |
| Estresse parental | 4.5 (4.1-4.9) | 3.8 (3.4-4.2) | -0.58 | [-0.97, -0.19] | p < 0.10 |
| Afeto positivo | 2.1 (1.7-2.5) | 3.5 (3.1-3.9) | 0.95 | [0.52, 1.38] | p < 0.01 |

---

### Estagio 6: Auditoria Decolonial do Framework

**Entrada**: Todos os artefatos dos Estagios 1-5

**Saida**: Relatorio de auditoria critica com analise de estruturas de poder

**Tarefas**:
1. Identificar marcadores de colonialidade do saber nas interpretacoes produzidas
2. Verificar se a analise privilegia saberes experienciais sobre diagnosticos importados
3. Avaliar se o setting terapeutico reproduz hierarquias ou as dissolve
4. Mapear relacoes de poder entre pesquisador-participante, terapeuta-paciente
5. Conferir aderencia aos principios de Nise da Silveira:
   - Nao-diretividade (recusa a impor temas, tecnicas ou interpretacoes)
   - Valorizacao da expressao livre como autorrelato do inconsciente
   - Reconhecimento da potencia criativa independente de diagnostico
6. Verificar alinhamento com pedagogia freireana (dialogicidade, problematizacao)

**Checklist decolonial**:
- [ ] A pergunta de pesquisa parte da realidade local ou de teoria importada?
- [ ] Os criterios de "validade" consideram epistemologias do Sul (Santos, 2019)?
- [ ] Ha espaco para contradicao e ambivalencia nos achados?
- [ ] O pesquisador explicita sua propria posicionalidade?
- [ ] As participantes sao reconhecidas como especialistas de sua propria experiencia?
- [ ] A producao artistica e tratada como dado legitimo ou como "ilustracao"?
- [ ] Ha apropriacao cultural ou epistemicidio na escolha dos materiais e tecnicas?
- [ ] A devolutiva aos participantes integra o processo ou e mera formalidade?

---

### Estagio 7: Geracao de Relatorio Clinico (MASWOS)

**Entrada**: Todos os artefatos validados dos Estagios 1-6

**Saida**: Relatorio clinico decolonial estruturado (formato IMRAD + anexos)

**Tarefas**:
1. Estruturar relatorio no formato IMRAD qualitativo:
   - **Introducao**: Contexto, problema, pergunta de pesquisa
   - **Metodo**: Desenho, participantes, instrumentos, procedimentos eticos
   - **Resultados**: Tabela de dimensoes, achados, niveis de confianca (tabelas do TCC)
   - **Discussao**: Dialogo entre achados e literatura (Silveira, Quijano, Freire, Malchiodi)
   - **Consideracoes finais**: Contribuicoes, limitacoes, implicacoes
2. Incluir anexos: imagens das producoes artisticas (anonimizadas), TCLE, parecer CEP
3. Gerar versao leiga (devolutiva para participantes)
4. Exportar em formatos: PDF (ABNT NBR 6023/2025), LaTeX, DOCX
5. Validar com PhD Auditor: coerencia interna, completude, aderencia etica

**Tabelas padrao do relatorio** (do TCC):

| Dimensao | Achado | Nivel de Confianca |
|----------|--------|--------------------|
| Pertencimento | Producao artistica compartilhada gerou senso de pertencimento | Confirmado |
| Reconhecimento do outro | Similaridades nas demandas culturais criaram identificacoes imediatas | Confirmado |
| Redes de apoio | Arteterapia grupal catalisou redes informais alem dos encontros | Confirmado |
| Mediacao simbolica | Fazer artistico reduziu barreiras a expressao emocional | Confirmado |
| Validacao | Abordagem decolonial valorizou saberes experienciais | Inferido |

| Mecanismo | Descricao | Evidencia | Confianca |
|-----------|-----------|-----------|-----------|
| Validacao experiencial | Reconhecimento mutuo via producao artistica | "Pensei que era so comigo" | Confirmado |
| Mudanca de papel subjetivo | De objeto a sujeito do cuidado | "Ninguem me perguntava como eu estava" | Confirmado |
| Redes alem do setting | Vinculos que transcendem o terapeutico | Observacao de campo + Baker et al., 2022 | Confirmado |

---

### Estagio 8: Verificacao de Privacidade e Conformidade LGPD

**Entrada**: Relatorio clinico completo + dados brutos (imagens, transcricoes, diarios)

**Saida**: Relatorio de conformidade + dados anonimizados + certificacao de privacidade

**Tarefas**:
1. **Anonimizacao de identificadores diretos**:
   - Nomes proprios -> codigos alfanumericos (P001, P002...)
   - Nomes de instituicoes -> "[servico especializado]"
   - Localizacao -> "interior do Ceara" (sem detalhes)
   - Datas exatas -> mes/ano apenas
2. **Anonimizacao de identificadores indiretos**:
   - Verificar combinacoes que permitam reidentificacao (profissao + idade + diagnostico do filho)
   - Generalizar categorias ocupacionais quando necessario
3. **Hash de dados biometricos**:
   - Imagens de producoes artisticas: hash SHA-256 do arquivo original armazenado em separado
   - Registros audiovisuais: transcritos e depois deletados (manter apenas transcricao anonima)
4. **Conformidade LGPD (Lei 13.709/2018)**:
   - [ ] Base legal identificada (consentimento - art. 7o, I)
   - [ ] Finalidade especifica comunicada ao titular
   - [ ] Dados pessoais minimizados ao necessario
   - [ ] Prazos de retencao definidos (5 anos apos conclusao)
   - [ ] Direito de exclusão assegurado (art. 18, VI)
   - [ ] Registro de operacoes de tratamento mantido
   - [ ] Medidas de seguranca tecnicas e administrativas implementadas
5. **Certificacao de privacidade**: Relatorio assinado pelo PhD Auditor

---

## 2. Decolonial Art Therapy Framework

Seis dimensoes interdependentes para analise de intervencoes em arteterapia decolonial, extraidas do referencial teorico do TCC e validadas pelo Cora-Debate.

### Dimensao 1: Expressao da Identidade (autoetnografica)

**Fundamentacao**: A producao artistica como "diario visual" do inconsciente (Silveira, 1992; Jung, 2000). A imagem encarnada que contem e transforma conteudos psiquicos dolorosos (Schaverien, 1992).

**Indicadores**:
- Uso de simbolos autorreferentes (figuras humanas, autorretratos)
- Cores que expressam estados emocionais (nao necessariamente realistas)
- Narrativas visuais de trajetoria pessoal (antes/agora/depois)
- Elementos autobiograficos na composicao

**Exemplo do TCC**: Participante que desenhou "as maes do grupo juntas e de maos dadas com seus filhos" como expressao de identidade coletiva.

**Questao disparadora**: "Como voce se sente sendo responsavel pelo cuidado de seu filho?"

### Dimensao 2: Resistencia Cultural (contra-hegemonica)

**Fundamentacao**: A arteterapia decolonial parte do "nao silenciamento quanto as questoes coloniais e colonizadoras" (Graupen; Adriao, 2020). Recusa a patologizacao das diferencas como forma de resistencia epistemica.

**Indicadores**:
- Subversao de expectativas clinicas normativas
- Valorizacao de saberes e praticas culturais locais
- Recusa a categorias diagnosticas importadas como unica narrativa
- Expressao de criticas a estruturas institucionais

**Referencial**: Fanon (2008), Martin-Baro (1994), Quijano (2000), Santos (2019)

### Dimensao 3: Vinculo Cuidador (dinamicas familiares neurodivergentes)

**Fundamentacao**: Parentalidade atipica como experiencia de "se virar" (Braga dos Anjos; Araujo de Morais, 2021), marcada por sobrecarga, isolamento e luta por direitos.

**Indicadores**:
- Representacao da relacao cuidador-crianca na producao artistica
- Verbalizacoes sobre estresse, cansaco, ambivalencia
- Marcadores de isolamento social e afetivo
- Expressoes de culpabilizacao e autocobranca
- Mencoes a rede de apoio (presente ou ausente)

**Dados do TCC**: Maes apresentam niveis de estresse "significativamente superiores aos de cuidadores de criancas neurotipicas" (Alves; Gameiro; Bazi, 2022; Zanatta et al., 2014).

### Dimensao 4: Integracao Sensorial (percepcao multimodal)

**Fundamentacao**: A arteterapia como ponte entre mundo interno e externo por meio de expressoes visuais, sonoras, corporais e literarias (Malchiodi, 2012; Philippini, 2020).

**Indicadores**:
- Uso de texturas, cores, formas como canais sensoriais
- Relacao entre material artistico e estado emocional
- Preferencias sensoriais nas escolhas de materiais
- Imersao e estado de fluxo durante a producao

**Materiais utilizados** (do TCC): tintas, pinceis, papeis, telas, materiais e elementos naturais.

### Dimensao 5: Critica Institucional (sistemas de saude/educacao)

**Fundamentacao**: A distancia entre norma e pratica nas politicas publicas (Onocko-Campos; Furtado, 2006). A inclusao escolar que exclui (Mantoan, 2003).

**Indicadores**:
- Relatos de experiencia com servicos de saude e educacao
- Mencoes a barreiras burocraticas (BPC, mediador, passe livre)
- Criticas ao capacitismo institucional
- Desigualdade de acesso entre regioes (interior vs. capital)

**Contexto**: A arteterapia foi incluida na PNPICS do SUS pela Portaria 849/2017, mas sua implementacao permanece desigual e frequentemente reduzida a "ocupacao do tempo" (Philippini, 2020).

### Dimensao 6: Resiliencia Comunitaria (rede de apoio)

**Fundamentacao**: O grupo como dispositivo decolonial de cuidado (Bonafe Sei, 2010; Sousa et al., 2020). A arteterapia grupal como catalisadora de redes informais de apoio.

**Indicadores**:
- Trocas espontaneas entre participantes alem da atividade dirigida
- Formacao de vinculos que transcendem o setting terapeutico
- Sensacao de pertencimento e reconhecimento mutuo
- Empoderamento na busca e oferta de ajuda

**Achado central do TCC**: "Parentalidade atipica ressignificada: de experiencia individual de desamparo para vivencia coletiva de reconhecimento e pertencimento."

---

## 3. Integracao com o Ecossistema OpenCode

O skill clinical-art-therapy orquestra 7 capacidades do ecossistema OpenCode em pipeline:

### 3.1 SEEKER Agent -> Busca Clinica

**Ativacao**: Revisao sistematica de literatura

**Bases consultadas**:
- PubMed: arteterapia, neurodivergencia, saude mental
- SciELO: producao brasileira em arteterapia e decolonialidade
- LILACS: saude mental coletiva, PNPICS
- PePSIC: psicologia brasileira, parentalidade atipica
- CAPES Periodicos: dissertacoes e teses

**Estrategia de busca** (PICO adaptado qualitativo):
- Populacao: familiares de criancas neurodivergentes
- Interesse: arteterapia decolonial, expressao criativa
- Contexto: servico publico, grupo terapeutico, interior do Nordeste

**Descritores**: art therapy, decolonial, neurodivergence, autism, ADHD, parental stress, caregiver, group intervention, Latin America, Brazil

### 3.2 Agent Forum -> Analise Multiperspectiva

**Ativacao**: Debates sobre interpretacao de achados

**Personas do forum** (cada uma analisa o mesmo caso de angulo diferente):
| Persona | Perspectiva | Referencial |
|---------|-------------|-------------|
| Analista Junguiano | Simbolos, arquetipos, inconsciente coletivo | Jung, 2000; Silveira, 1992 |
| Clinica Decolonial | Poder, saber, epistemicidio | Quijano, 2000; Santos, 2019 |
| Neurodiversidade | Autismo como variacao, nao patologia | Bogdashina, 2016 |
| Saude Coletiva | PNPICS, SUS, redes de atencao | Amarante, 2007; Onocko-Campos, 2006 |
| Pedagogia Critica | Educacao inclusiva, Freire | Freire, 1987; Mantoan, 2003 |
| Etica em Pesquisa | CEP, TCLE, consentimento | CNS 466/2012, 510/2016 |
| Familia e Cuidado | Parentalidade, genero, sobrecarga | Stampoltzis et al., 2021; Cruz et al., 2024 |

### 3.3 Cora-Debate V1-V6 -> Verificacao Formal

**Ativacao**: Validacao de cada afirmacao clinica antes de incorporar ao relatorio

**V1 - Consistencia**: Um participante disse X na Sessao 1 e disse Y na Sessao 3? Ha contradicao ou evolucao?

**V2 - Coerencia**: O achado dialoga com Malchiodi (2012), Philippini (2020), Silveira (1992)?

**V3 - Multiplicidade**: Quantos participantes corroboram este padrao? Ha vozes dissonantes?

**V4 - Saturação**: Novas sessoes acrescentariam informacao ou confirmariam?

**V5 - Vies**: A interpretacao privilegia saber local ou impoe marco teorico externo?

**V6 - Rastreabilidade**: Cada afirmacao tem citacao, nota de campo ou registro visual?

**Criterio de aceite**: Q-Score UCB1 >= 0.75 com aprovacao em pelo menos 4 dos 6 verificadores.

### 3.4 PhD Auditor -> Validacao Estatistica

**Ativacao**: Calculo de tamanhos de efeito, bootstrap e calibracao Platt

**Metricas calculadas**:
- Cohen's d (efeito da intervencao)
- Bootstrap IC 95% (10.000 iteracoes)
- Correlacao de Pearson (engajamento x desfecho)
- Correlacao de Spearman (variaveis ordinais)
- Correcao de Bonferroni (comparacoes multiplas)
- Calibracao Platt (confianca do modelo)
- Analise de sensibilidade (jackknife)

### 3.5 MASWOS -> Geracao de Relatorio

**Ativacao**: Producao do relatorio clinico decolonial

**49 agentes** envolvidos na producao do relatorio:
- Agentes de codificacao (20): Cada um aplica 1 categoria analitica ao corpus
- Agentes de redacao (10): Introducao, metodo, resultados, discussao, conclusao
- Agentes de revisao (5): Coerencia, citacoes, normas ABNT, clareza, etica
- Agentes de traducao (3): Versao leiga, resumo, abstract
- Agentes de formato (4): LaTeX, PDF, DOCX, HTML
- Agentes de anexos (3): Imagens, tabelas, documentos eticos
- Agente orquestrador (1): Coordenacao e consistencia geral
- Agente de qualidade (1): Score final (criterio: >= 95/100)
- Agente de privacidade (1): LGPD compliance
- Agente decolonial (1): Auditoria de colonialidade

### 3.6 Machine States -> Controle de Pipeline

**Ativacao**: Rastreabilidade de estado do processo de pesquisa

**Estados**:
```
rascunho -> submetido_cep -> aprovado_cep -> coleta -> analise -> validacao -> relatorio -> arquivado
```
Cada transicao requer validacao explicita e registro em log.

### 3.7 Privacy Protocols -> Camada LGPD

**Ativacao**: Anonimizacao e conformidade legal

**Tecnicas**:
- SHA-256 hashing de identificadores
- Remocao de PII (Personally Identifiable Information)
- Generalizacao de dados indiretos
- Criptografia de dados biometricos
- Log de acesso a dados pessoais

---

## 4. Protocolo Etico

### 4.1 Checklist de Submissao ao CEP

**Documentos necessarios** (CNS 466/2012 e 510/2016):
- [ ] Folha de rosto CONEP (assinada pelo responsavel institucional)
- [ ] Projeto de pesquisa completo (formato Plataforma Brasil)
- [ ] TCLE (Termo de Consentimento Livre e Esclarecido)
- [ ] Termo de assentimento (se houver menores)
- [ ] Carta de anuencia da instituicao coparticipante
- [ ] Declaracao de concordancia dos servicos envolvidos
- [ ] Cronograma detalhado
- [ ] Orcamento financeiro
- [ ] Curriculo Lattes da equipe
- [ ] Instrumentos de coleta (roteiros, questionarios, escalas)

### 4.2 Template de TCLE (adaptado do TCC)

Elementos obrigatorios do TCLE (CNS 466/2012, III.2):

1. **Justificativa e objetivos**: "Esta pesquisa busca compreender como a arteterapia contribui para o bem-estar de familiares de criancas neurodivergentes..."
2. **Procedimentos**: "Participacao em 3 encontros mensais de arteterapia com duracao de 1 hora cada, envolvendo atividades de desenho, pintura e compartilhamento em grupo."
3. **Riscos**: "Desconforto emocional ao abordar experiencias pessoais. Garantimos acolhimento e encaminhamento se necessario."
4. **Beneficios**: "Espaco de expressao criativa, pertencimento grupal e fortalecimento de redes de apoio."
5. **Garantia de recusa**: "Liberdade de recusar ou retirar consentimento a qualquer momento, sem prejuizo ao atendimento."
6. **Confidencialidade**: "Dados anonimizados, sem identificacao em publicacoes."
7. **Ressarcimento**: "Garantia de ressarcimento de despesas decorrentes da participacao."
8. **Contato**: "Pesquisador responsavel, orientador e Comite de Etica."

### 4.3 Pipeline de Anonimizacao

```python
# Pseudocodigo do pipeline de anonimizacao
def anonimizar(participante):
    # 1. Hash de nome proprio
    id_hash = hashlib.sha256(participante.nome.encode()).hexdigest()[:8]
    codigo = f"P{int(id_hash, 16) % 1000:03d}"

    # 2. Remocao de PII diretas
    texto_anonimo = remover_pii(participante.depoimento)

    # 3. Generalizacao de dados indiretos
    texto_anonimo = generalizar_localizacao(texto_anonimo)  # "Sobral" -> "interior do CE"
    texto_anonimo = generalizar_profissao(texto_anonimo)    # "professora" -> "profissional da educacao"
    texto_anonimo = generalizar_idade(texto_anonimo)        # "34" -> "30-40 anos"
    texto_anonimo = ofuscar_diagnostico(texto_anonimo)      # "TEA nivel 2" -> "neurodivergencia"

    # 4. Anonimizacao de producoes visuais
    # - Remover metadados EXIF de fotos
    # - Hash do arquivo original para auditoria
    # - Armazenar apenas versao com metadados removidos

    return codigo, texto_anonimo
```

### 4.4 LGPD Compliance (Lei 13.709/2018)

**Bases legais aplicadas**:
- Art. 7o, I: Consentimento do titular (TCLE)
- Art. 7o, IV: Realizacao de pesquisas (garantido o anonimato)

**Direitos do titular garantidos**:
- Art. 9o: Direito de acesso aos dados
- Art. 18: Eliminacao dos dados pos-pesquisa
- Art. 18, VI: Revogacao do consentimento

**Medidas de seguranca**:
- Dados armazenados em ambiente criptografado
- Logs de acesso mantidos por 6 meses
- Acesso restrito a equipe de pesquisa
- Descarte seguro apos 5 anos (art. 16)

---

## 5. Exemplo de Uso Completo

**Cenario**: Analise de uma sessao de arteterapia grupal com 5 familiares de criancas neurodivergentes em servico de apoio pedagogico especializado no interior do Ceara.

### Passo 1: Intake

```
> Entrada: "Iniciar pipeline clinical-art-therapy para analise de sessao
  arteterapeutica com 5 participantes (4 maes, 1 pai) em servico publico
  municipal. Criancas com TEA (n=3) e TDAH (n=2). Idade dos participantes:
  28-52 anos. 3 encontros mensais de 1h cada com producao artistica."

> Acionado: Machine States -> estado = "rascunho"
> Acionado: SEEKER -> busca TCLE templates + literatura
> Acionado: PhD Auditor -> verifica conformidade CNS 466/2012
> Saida: Documentos eticos gerados, checklist CEP completo
> Estado: "submetido_cep"
```

### Passo 2: Coleta e Codificacao

```
> Entrada: Diario de campo etnografico do Encontro 1
  "Participante P001 desenhou uma arvore com raizes profundas.
  Ao compartilhar, disse: 'As vezes sinto que sozinha nao vou
  dar conta, mas olhando para o desenho vejo que tenho forca
  que nem sabia.' Participante P002 comecou a chorar ao ouvir."

> Acionado: 49 agentes de codificacao
> Agente-03 (forca/identidade): codigo = "POTENCIA_CRIATIVA",
  confianca = 0.89
> Agente-07 (colonialidade): codigo = "COLONIALIDADE_CUIDADO",
  confianca = 0.76
> Agente-12 (rede apoio): codigo = "RECONHECIMENTO_MUTUO",
  confianca = 0.94

> Saida: Matriz tematica com 23 codigos, confianca media 0.82
```

### Passo 3: Analise Multimodal da Sessao

```
> Entrada: Foto do desenho de P001 (arvore com raizes)
  + verbalizacao transcrita + nota de campo comportamental

> Analise visual:
  - Composicao: arvore centralizada, copa ampla (2/3 da pagina)
  - Cores: marrom (tronco), verde (copa), azul (ceu) - paleta natural
  - Simbolos: raizes profundas e visiveis (ancoragem, origem)
  - Espaco: figura ocupa centro, sem elementos dispersivos (foco)

> Analise textual:
  - "sozinha nao vou dar conta" -> sobrecarga (SOBRECARGA_CUIDADO)
  - "forca que nem sabia" -> autodescoberta (RESSIGNIFICACAO)

> Analise comportamental:
  - Postura: curvada durante o desenho, ereta ao compartilhar
  - Tempo de imersao: 12 min (acima da media do grupo: 8 min)
  - Interacao: P002 aproximou-se para ver o desenho antes da roda

> Triangulacao: Os tres canais convergem para narrativa de
  (re)descoberta de forca pessoal em contexto de sobrecarga.
```

### Passo 4: Validacao Cruzada

```
> Cora-Debate V1-V6 acionado para o padrao "RESSIGNIFICACAO"

V1 (Consistencia): P001 manteve narrativa de forca na Sessao 2? -> SIM
V2 (Teoria): Alinhado com Silveira (1992) "imagens do inconsciente" -> SIM
V3 (Multiplicidade): 3/5 participantes expressaram padrao similar -> SIM
V4 (Saturacao): Apenas 3 sessoes, pode nao ter saturado -> NAO
V5 (Vies decolonial): A analise nao patologiza a expressao -> SIM
V6 (Rastreabilidade): Citacao literal + foto + nota de campo -> SIM

> Q-Score UCB1 = 0.87 | Aprovado: V1, V2, V3, V5, V6
> Padrao validado com confianca alta
```

### Passo 5: Significancia Estatistica

```
> PhD Auditor acionado para calculo de efeito

Variavel: Percepcao de suporte (escala 1-5)
Pre (Sessao 1): media 3.2, DP 0.8
Pos (Sessao 3): media 4.1, DP 0.6
d de Cohen = 0.72 (efeito medio-grande)
Bootstrap IC 95%: [0.31, 1.13]

> Relatorio de significancia gerado
> Correlacao engajamento-desfecho: r = 0.64, p < 0.05
```

### Passo 6: Auditoria Decolonial

```
> Checklist decolonial aplicado ao relatorio preliminar

[OK] Pergunta parte da realidade local (familiares no interior do CE)
[OK] Saberes experienciais valorizados ("cada familiar como especialista")
[OK] Espaco para contradicao (ambivalencia acolhida)
[OK] Posicionalidade do pesquisador explicitada
[OK] Producao artistica como dado legitimo, nao ilustracao
[OK] Devolutiva integrada ao processo (Encontro 3 como exposicao)

> Relatorio de auditoria decolonial: 6/8 criterios plenamente atendidos
> Recomendacao: Fortalecer multiplicidade de vozes dissonantes
```

### Passo 7: Relatorio Final

```
> MASWOS acionado com 49 agentes
> Agentes de redacao produzem IMRAD completo
> Agentes de anexos: imagens anonimizadas + TCLE + tabelas
> Agente de qualidade: score = 96/100 (acima do limiar 95)
> Agente de privacidade: certificacao LGPD emitida
> PhD Auditor: aprovacao final

> Relatorio exportado: relatorio_clinico_arteterapia_decolonial.pdf
> Versao leiga: devolutiva_participantes.pdf
> Dados arquivados: hash SHA-256 registrado
```

### Passo 8: Privacidade e Conformidade

```
> Pipeline de anonimizacao executado:
  - 5 identificadores diretos substituidos por codigos
  - 12 PII removidas do corpus textual
  - 15 imagens de producoes artisticas com metadados EXIF removidos
  - 3 registros audiovisuais: transcricao mantida, arquivos deletados
  - Hash SHA-256 de todos os arquivos originais armazenado em cofre
  - Log de acesso registrado

> Relatorio de conformidade LGPD emitido: 12/12 criterios atendidos
> Certificado de privacidade anexado ao relatorio final
> Prazo de retencao: 5 anos (art. 16 LGPD)
> Direito de exclusão assegurado via canal de contato
```

---

## 6. Referencias e Citacoes

### Referencias do TCC de Base

- ALVES, J. S.; GAMEIRO, A. C. P.; BIAZI, P. H. G. Estresse, depressao e ansiedade em maes de autistas. *Revista Psicopedagogia*, v. 39, n. 120, p. 340-352, 2022.
- BOGDASHINA, O. *Sensory perceptual issues in autism and Asperger syndrome*. 2. ed. London: Jessica Kingsley, 2016.
- BRASIL. Portaria nº 849/2017. Inclui a arteterapia na PNPICS. *DOU*, 28 mar. 2017.
- CRUZ, A. C. B. O. A.; BAHIA, S. D.; SOUZA, J. C. P. A vida das maes de criancas com TEA. *Cuadernos de Educacion y Desarrollo*, v. 16, n. 11, e6230, 2024.
- FANON, F. *Pele negra, mascaras brancas*. Salvador: EDUFBA, 2008.
- FREIRE, P. *Pedagogia do oprimido*. 17. ed. Rio de Janeiro: Paz e Terra, 1987.
- GRAUPEN, A.; ADRIÃO, K. G. Arteterapia promovendo respiros em tempos de incertezas. *Revista Cientifica de Arteterapia Cores da Vida*, v. 27, n. 16, p. 119-129, 2020.
- JUNG, C. G. *O espirito na arte e na ciencia*. 15. ed. Petropolis: Vozes, 2000. (Obras Completas, v. 15).
- MALCHIODI, C. A. (org.). *Handbook of art therapy*. 2. ed. New York: Guilford, 2012.
- MANTOAN, M. T. E. *Inclusao escolar: o que e? Por que? Como fazer?* Sao Paulo: Moderna, 2003.
- MARTIN-BARO, I. *Writings for a liberation psychology*. Cambridge: Harvard University Press, 1994.
- MELLO, L. C. *Nise da Silveira: caminhos de uma psiquiatra rebelde*. 3. ed. Rio de Janeiro: Versal, 2014.
- ONOCKO-CAMPOS, R. T.; FURTADO, J. P. Entre a saude coletiva e a saude mental. *Cadernos de Saude Publica*, v. 22, n. 5, p. 1053-1062, 2006.
- PHILIPPINI, A. *Arteterapia: um convite ao fazer e ao sentir*. Rio de Janeiro: Wak, 2020.
- QUIJANO, A. Coloniality of power, eurocentrism, and Latin America. *Nepantla*, v. 1, n. 3, p. 533-580, 2000.
- SANTOS, B. de S. *O fim do imperio cognitivo: a afirmacao das epistemologias do Sul*. Belo Horizonte: Autentica, 2019.
- SCHAVERIEN, J. *The revealing image: analytical art psychotherapy in theory and practice*. London: Routledge, 1992.
- SILVEIRA, N. da. *Imagens do inconsciente*. Rio de Janeiro: Alhambra, 1981.
- SILVEIRA, N. da. *O mundo das imagens*. Sao Paulo: Atica, 1992.
- STAMPOLTZIS, A. et al. Mothers' experiences and challenges raising a child with autism spectrum disorder. *Brain Sciences*, v. 11, n. 3, 309, 2021.
- WORLD HEALTH ORGANIZATION. *World mental health report*. Geneva: WHO, 2022.

### Normas e Legislacao

- BRASIL. CNS Resolucao nº 466/2012. Diretrizes de pesquisas envolvendo seres humanos.
- BRASIL. CNS Resolucao nº 510/2016. Normas aplicaveis a pesquisas em Ciencias Humanas e Sociais.
- BRASIL. Lei nº 12.764/2012. Politica Nacional de Protecao dos Direitos da Pessoa com Transtorno do Espectro Autista.
- BRASIL. Lei nº 13.146/2015. Lei Brasileira de Inclusao da Pessoa com Deficiencia.
- BRASIL. Lei nº 13.709/2018. Lei Geral de Protecao de Dados Pessoais (LGPD).

---

## Notas de Versao

**v1.0.0** (2026-05-27):
- Pipeline completo de 8 estagios implementado
- Framework decolonial de 6 dimensoes (extraido do TCC de Nadielle Darc Batista Dias, 2026)
- Integracao com SEEKER, Agent Forum, Cora-Debate V1-V6, PhD Auditor, MASWOS, Machine States
- Protocolo etico completo (CEP, TCLE, LGPD)
- Exemplo de uso com caso real do TCC
- 398 linhas de especificacao operacional
