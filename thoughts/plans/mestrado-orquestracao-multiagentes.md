# Mestrado: Orquestração Multiagente para Automação de Pesquisa Científica Interdisciplinar

## Meta

- **PPG**: Engenharia de Inteligência Artificial
- **Área**: Automação em pesquisa científica e raciocínio científico em orquestração de multiagentes
- **Problema**: Pesquisa interdisciplinar demanda integração de múltiplos domínios de conhecimento, cada um com métodos, vocabulários e critérios de validação próprios. Agentes de IA especializados podem orquestrar esse processo, mas carecem de raciocínio científico verificável e coordenação evolutiva entre disciplinas.
- **Solução proposta**: Framework de orquestração multiagente com motores de raciocínio científico (lógico, estatístico, causal) que automatiza ciclos de pesquisa interdisciplinar: formulação → busca → síntese → validação → evolução.

## Desired End State

Dissertação de mestrado concluída e defendida, com:
- Framework de orquestração multiagente validado experimentalmente
- Pipeline funcional de pesquisa científica automatizada em domínios interdisciplinares
- Artigo(s) publicados em veículo Qualis A1/A2
- Código-fonte aberto do framework

## Timeline (Macro)

| Fase | Período | Entregas |
|------|---------|----------|
| **F1**: Fundamentação | Sem 1-8 | Revisão sistemática, definição do problema, referencial teórico |
| **F2**: Arquitetura | Sem 5-12 | Spec do framework, ADRs, diagramas, prova de conceito |
| **F3**: Implementação | Sem 10-20 | Framework funcional, integração com motores de raciocínio |
| **F4**: Experimentos | Sem 16-24 | Design experimental, execução, coleta de dados |
| **F5**: Escrita | Sem 20-30 | Dissertação, artigos, defesa |

## Phase 1: Fundamentação Teórica

### Contexto

Revisão sistemática e definição do arcabouço teórico que sustenta a tese.

### Changes Required

1. **Revisão sistemática da literatura** (SEEKER + MASWOS)
   - Fontes: arXiv, OpenAlex, PubMed, Scopus, IEEE
   - Strings de busca: "multi-agent orchestration scientific reasoning", "AI scientist automation", "interdisciplinary research automation", "multi-agent systems literature review"
   - Critérios PRISMA para inclusão/exclusão
2. **Mapeamento do estado da arte**
   - Agentes científicos: AI Scientist (Sakana), PaperQA2, ChemCrow, BioAgent
   - Orquestração: AutoGen, CrewAI, BettaFish/MiroFish pipeline
   - Raciocínio científico: Z3, SymPy, Cora-Debate, AlphaProof
   - Interdisciplinaridade: frameworks de integração cross-domínio
3. **Definição do gap de pesquisa**
   - O que existe vs. o que falta (validação formal, coordenação evolutiva, métricas interdisciplinares)
4. **Referencial teórico**
   - Epistemologia da pesquisa interdisciplinar (Klein, Nicolescu)
   - Raciocínio científico formal (Popper, Lakatos, Kuhn)
   - Sistemas multiagente (Wooldridge, Jennings, Weiss)
   - Qualis A1: mínimo 30 referências de periódicos Qualis A1/A2

### Success Criteria

- [ ] Revisão sistemática com protocolo PRISMA documentado
- [ ] Mínimo 50 referências (30+ Qualis A1/A2, 10+ internacionais)
- [ ] Gap de pesquisa claramente definido e justificado
- [ ] Questões de pesquisa e hipóteses formuladas
- [ ] Referencial teórico integrando pelo menos 3 domínios distintos

## Phase 2: Arquitetura do Framework

### Contexto

Especificação formal do framework de orquestração multiagente com raciocínio científico.

### Changes Required

1. **Arquitetura de referência** (diagramas C4 + ADRs)
   - Camada de orquestração (meta-agente coordenador)
   - Camada de agentes especialistas (domínio-específico)
   - Camada de raciocínio científico (Z3, SymPy, Cora-Debate)
   - Camada de memória/evolução (aprendizado entre ciclos)
2. **Protocolos de comunicação inter-agentes**
   - Formato de mensagens (ACL-like)
   - Ciclo de debate (thesis → antithesis → synthesis)
   - Consenso e resolução de contradições
3. **Motores de raciocínio integrados**
   - Lógico-formal (Z3): validação de consistência interna
   - Estatístico (SymPy + bootstrap): significância e incerteza
   - Dialético (Cora-Debate): debate multiagente com verificadores
   - Causal (do-calculus): inferência causal interdisciplinar
4. **Mecanismo evolutivo**
   - Ciclos de auto-melhoria entre execuções de pesquisa
   - Banco de hipóteses verificadas e refutadas

### Success Criteria

- [ ] Spec publicada com diagramas C4 (nível 1-3)
- [ ] Mínimo 5 ADRs registradas
- [ ] Prova de conceito funcional (2 domínios, 3 agentes)
- [ ] Protocolo de comunicação formalmente definido

## Phase 3: Implementação

### Contexto

Construção do framework integrado ao ecossistema.

### Changes Required

1. **Orquestrador central** (BettaFish-style middleware chain)
   - Pipeline: Busca → Síntese → Validação → Reflexão → Evolução
   - Estado rastreável via ANP (Agent Node Pipeline)
   - Middlewares: cache, logging, rate-limit, fallback
2. **Agentes especialistas**
   - Agente de domínio A (ex.: biomedicina)
   - Agente de domínio B (ex.: ciência da computação)
   - Agente de síntese interdisciplinar
   - Agente de validação (raciocínio científico)
3. **Integração com fontes acadêmicas**
   - MCPs: latest-science, research-mcp, sura-papers, arxiv-mcp, scihub
   - Busca paralela cross-fonte com deduplicação
4. **Interface de experimentação**
   - CLI + API REST
   - Logs estruturados para auditoria

### Success Criteria

- [ ] Pipeline completo executa ciclo de pesquisa do início ao fim
- [ ] Agentes consultam 5+ fontes acadêmicas
- [ ] Raciocínio científico integrado (mín. 2 motores)
- [ ] Testes unitários e de integração (TDD, pytest)

## Phase 4: Experimentos

### Contexto

Validação experimental do framework em cenários interdisciplinares reais.

### Changes Required

1. **Design experimental**
   - Domínios: computação + biomedicina (ou segundo domínio definido)
   - Perguntas de pesquisa interdisciplinares (mín. 10)
   - Baseline: execução manual vs. orquestrada
2. **Métricas**
   - Precisão das sínteses (expert review com rubrica)
   - Cobertura interdisciplinar (número de domínios integrados)
   - Tempo de execução vs. qualidade
   - Reprodutibilidade dos resultados
3. **Execução e coleta**
   - 3+ rodadas por cenário
   - Logs estruturados para análise estatística
4. **Análise estatística**
   - Testes de hipótese (t, ANOVA, Wilcoxon)
   - Tamanho de efeito (Cohen's d, η²)
   - Visualizações (boxplots, barplots com IC)

### Success Criteria

- [ ] Framework supera baseline manual em 2+ métricas principais
- [ ] Resultados publicáveis (análise estatística completa)
- [ ] Reprodutibilidade demonstrada (3+ replicações)
- [ ] Dados brutos e scripts de análise disponíveis

## Phase 5: Escrita e Defesa

### Contexto

Produção da dissertação e artigos para Qualis A1.

### Changes Required

1. **Artigo 1** (submissão antes da defesa)
   - Foco: arquitetura do framework
   - Veículo alvo: periódico Qualis A1
2. **Artigo 2** (opcional, após defesa)
   - Foco: resultados experimentais
3. **Dissertação**
   - Estrutura IMRAD (ou conforme PPG)
   - Elementos obrigatórios: introdução, referencial, metodologia, resultados, discussão, conclusão
4. **Simulação de banca** (agent-forum)
   - 3 personas: orientador, avaliador interno, avaliador externo
   - 16+ perguntas simuladas
   - Iterações de correção até confiança ≥ 9.0

### Success Criteria

- [ ] Dissertação completa (formato ABNT)
- [ ] Artigo submetido a periódico Qualis A1
- [ ] Defesa simulada com score ≥ 9.0
- [ ] Todos os scripts e dados compartilháveis (repositório público)

## Risks and Mitigations

| Risco | Probabilidade | Impacto | Mitigação |
|-------|:-----------:|:-------:|-----------|
| Escopo muito amplo | Média | Alto | Delimitar 2 domínios específicos |
| APIs acadêmicas instáveis | Alta | Médio | Cache local + fallback |
| Qualidade da síntese abaixo do esperado | Média | Alto | Expert review + iterações corretivas |
| Prazo apertado para defesa | Média | Alto | Priorizar funcionalidade core, postergar features extras |

## Dependencies

- **Ecossistema OpenCode** (já instalado: agent-forum, cora-debate, reasoning-orchestrator, SEEKER, MASWOS, ANP)
- **MCPs acadêmicos**: latest-science, research-mcp, sura-papers, arxiv-mcp, scihub (todos configurados)
- **Motores de raciocínio**: Z3, SymPy (instalados); Cora-Debate (integrado)
- **Orientador(a) do PPG** a ser consultado para validação do tema
