<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
  Genesis-Writer: integrado ao ecossistema v4.0
-->

# Integração Claude Code Architecture ao Genesis-Writer v5.3

## Visão Geral

O **Genesis-Writer v5.3** integra profundamente a **Claude Code Architecture** para fortalecer o harness de engenharia, permitindo que o sistema atue como um **Engenheiro Autônomo de Conhecimento** com capacidades de auto-evolução, gerenciamento robusto de contexto e execução segura de operações complexas.

## 1. Mapeamento de Componentes Claude Code → Genesis-Writer v5.3

### 1.1 Input Layer (Camada de Entrada)

**Claude Code Components:**
- User Interface
- Session Manager
- Permission Gate

**Integração ao Genesis-Writer v5.3:**

O Genesis-Writer agora implementa uma **Input Layer Aprimorada (L0)** que incorpora:

```markdown
## L0.1: User Interface Científica

A interface de entrada do Genesis-Writer aceita requisições estruturadas em formato JSON:

```json
{
  "project_type": "artigo|dissertacao|tese|livro",
  "titulo": "string",
  "tema": "string",
  "palavras_chave": ["string"],
  "metodologia": "string",
  "escopo": "string",
  "restricoes": {
    "paginas_minimas": integer,
    "paginas_maximas": integer,
    "citacoes_minimas": integer,
    "qualis_minimo": "A1|A2|B1|B2|B3|B4|B5"
  },
  "preferencias": {
    "idioma": "pt-BR|en-US",
    "formato_citacao": "ABNT|APA|Vancouver|IEEE",
    "incluir_multimedia": boolean
  }
}
```

## L0.2: Session Manager Científico

Cada projeto é gerenciado como uma **Sessão Científica** com ciclo de vida completo:

1. **Inicialização:** Cria contexto de sessão, injeta skills, inicializa memoria
2. **Execução:** Coordena 45+ agentes através de Master Agent Loop
3. **Persistência:** Salva estado entre iterações (checkpoints)
4. **Recuperação:** Permite retomar sessão interrompida
5. **Bifurcação:** Permite criar variantes (fork) de um projeto

## L0.3: Permission Gate Científico

O Permission Gate agora valida não apenas permissões de execução, mas também **Conformidade Científica**:

```yaml
# Regras de Permissão (3 Níveis)

Deny:
  - Citações fictícias ou simuladas
  - Metodologias não reconhecidas
  - Dados estatísticos não validados
  - Plágio ou autoplagio

Allow:
  - Citações verificadas em Scopus/WoS
  - Metodologias Qualis A1
  - Análises estatísticas com validação de pressupostos
  - Conteúdo original com rastreabilidade

Approve:
  - Publicação em periódico Qualis A1
  - Defesa de tese/dissertação
  - Lançamento de livro acadêmico
  - Submissão a conferência de elite
```
```

### 1.2 Knowledge Layer (Camada de Conhecimento)

**Claude Code Components:**
- Skill Registry
- Context Compressor
- Task Graph
- Memory Store

**Integração ao Genesis-Writer v5.3:**

O Genesis-Writer agora implementa uma **Knowledge Layer Aprimorada (L1)** que incorpora:

```markdown
## L1.1: Skill Registry Científico

Cada skill (habilidade) é registrada com metadados científicos:

```json
{
  "skill_id": "A4.2.1",
  "nome": "Especialista em Estudo de Caso",
  "metodologia": "Estudo de Caso",
  "raciocínios_primários": [
    "Abdutivo (Melhor Explicação)",
    "Indutivo (Padrão)",
    "Analógico (Comparação)"
  ],
  "capacidades": [
    "Seleção de casos",
    "Coleta de dados",
    "Análise temática",
    "Síntese de achados"
  ],
  "citações_esperadas": "15-25",
  "páginas_esperadas": "18-28",
  "qualis_minimo": "A1",
  "status": "ativo|inativo|em_desenvolvimento"
}
```

## L1.2: Context Compressor Científico

O Context Compressor garante que o contexto do modelo nunca exceda 92% da capacidade, mantendo coerência:

**Estratégia de 3 Camadas:**

1. **Camada 1 (Essencial):** Requisição original + Plano de escrita + Gaps identificados
2. **Camada 2 (Crítica):** Seções já escritas + Citações validadas + Raciocínios aplicados
3. **Camada 3 (Suporte):** Referências bibliográficas + Exemplos + Notas de auditoria

**Algoritmo de Compressão:**
- Se contexto > 85%: Remove Camada 3
- Se contexto > 90%: Remove Camada 3 + Sumariza Camada 2
- Se contexto > 92%: Ativa Fractional Execution (divide em chunks)

## L1.3: Task Graph Científico

Cada projeto é representado como um **Grafo de Tarefas Acíclico Dirigido (DAG)**:

```
Requisição
  ├── Diagnóstico (L0-L1)
  │   ├── Extração de Conceitos
  │   ├── Identificação de Gaps
  │   └── Seleção de Metodologia
  ├── Pesquisa (L2-L3)
  │   ├── Busca Multicanal
  │   ├── Validação de Citações
  │   └── Síntese Crítica
  ├── Escrita (L4)
  │   ├── Escrita de Seção 1
  │   ├── Escrita de Seção 2
  │   └── Escrita de Seção N
  ├── Auditoria (L5)
  │   ├── Validação de Constraints
  │   ├── Verificação de Coesão
  │   └── Avaliação Qualis A1
  └── Entrega (L6-L7)
      ├── Consolidação
      ├── Geração de Relatório
      └── Publicação
```

## L1.4: Memory Store Científico

A memória persiste entre sessões, armazenando:

- **Histórico de Projetos:** Todos os projetos anteriores com seus checkpoints
- **Biblioteca de Citações:** Citações validadas com metadados (DOI, fator de impacto, índice H)
- **Padrões de Sucesso:** Configurações e estratégias que resultaram em score 10/10
- **Erros Aprendidos:** Falhas anteriores e como foram corrigidas
- **Evolução de Agentes:** Especialização emergente de cada agente baseada em feedback
```

### 1.3 Execution Layer (Camada de Execução)

**Claude Code Components:**
- Tool Dispatch
- Streaming Runtime
- Prompt Cache

**Integração ao Genesis-Writer v5.3:**

O Genesis-Writer agora implementa uma **Execution Layer Aprimorada (L3-L4)** que incorpora:

```markdown
## L3.1: Tool Dispatch Científico

O Tool Dispatch mapeia operações científicas para ferramentas especializadas:

```json
{
  "tools": {
    "search_bibliographic": {
      "handler": "A4.13.4",
      "canais": ["scopus", "arxiv", "sci-hub", "similarweb"],
      "timeout": 300,
      "retry_policy": "exponential_backoff"
    },
    "validate_citation": {
      "handler": "A5.1",
      "niveis": 7,
      "timeout": 60,
      "cache": true
    },
    "generate_section": {
      "handler": "A4.1-A4.13",
      "parallelization": true,
      "max_workers": 8
    },
    "audit_quality": {
      "handler": "A5.1-A5.9",
      "rubrica": "qualis_a1",
      "timeout": 120
    }
  }
}
```

## L3.2: Streaming Runtime Científico

A execução é feita em tempo real com streaming de resultados:

- **Percepção Contínua:** O sistema monitora o progresso de cada agente
- **Ação Adaptativa:** Ajusta estratégia baseado em feedback em tempo real
- **Observação Granular:** Registra cada decisão e resultado
- **Evolução Incremental:** Otimiza continuamente

## L3.3: Prompt Cache Científico

O Prompt Cache reutiliza prefixos estáveis para otimizar custo e latência:

- **Cache de Contexto Científico:** Requisição original + Plano de escrita (reutilizado em todas as seções)
- **Cache de Referências:** Biblioteca de citações validadas (reutilizado em todas as seções)
- **Cache de Raciocínios:** Definições dos 38 sub-tipos de raciocínio (reutilizado em todas as decisões)
```

### 1.4 Integration Layer (Camada de Integração)

**Claude Code Components:**
- MCP Runtime
- External Servers

**Integração ao Genesis-Writer v5.3:**

O Genesis-Writer agora implementa uma **Integration Layer Aprimorada (L1-L2)** que incorpora:

```markdown
## L1.5: MCP Runtime Científico

O MCP Runtime permite descoberta automática de servidores MCP para:

- **Busca Bibliográfica:** Integração com Scopus, arXiv, Semantic Scholar
- **Validação de Citações:** Integração com CrossRef, DOI.org, Google Scholar
- **Análise de Impacto:** Integração com SimilarWeb, Altmetric
- **Geração de Conteúdo Multimídia:** Integração com APIs de música, vídeo, áudio

## L1.6: External Servers Científicos

Integração com sistemas externos:

- **Sistema de Arquivos:** Armazenamento de projetos, checkpoints, relatórios
- **Git:** Versionamento de documentos, rastreamento de mudanças
- **Banco de Dados:** Persistência de citações, metadados, histórico
- **APIs Externas:** Scopus, CrossRef, arXiv, SimilarWeb, APIs de geração de mídia
```

### 1.5 Multi-Agent Layer (Camada Multiagente)

**Claude Code Components:**
- Subagent Spawner
- Teammate Mailboxes
- FSM Protocol
- Autonomous Board
- Worktree Isolator

**Integração ao Genesis-Writer v5.3:**

O Genesis-Writer agora implementa uma **Multi-Agent Layer Aprimorada (L3)** que incorpora:

```markdown
## L3.2: Subagent Spawner Científico

O Subagent Spawner cria e delega tarefas a subagentes com contextos isolados:

```python
# Exemplo de Spawning de Subagentes

master_agent.spawn_subagent(
    agent_id="A4.2",
    task="Escrever seção de Estudo de Caso",
    context={
        "gaps": [gap1, gap2, gap3],
        "citacoes": [cit1, cit2, ...],
        "raciocinio": "Abdutivo",
        "metodologia": "Estudo de Caso"
    },
    constraints={
        "paginas": 18,
        "citacoes": 15,
        "qualis_minimo": "A1",
        "score_minimo": 9.0
    }
)
```

## L3.3: Teammate Mailboxes Científico

A comunicação entre agentes é facilitada através de mailboxes pub/sub:

```
A0.1 (Orquestrador) → A2 (Pesquisador)
  ├── Mensagem: "Pesquise gaps em IA e ética"
  └── Resposta: [gap1, gap2, gap3] + Citações validadas

A2 (Pesquisador) → A4.2 (Especialista em Estudo de Caso)
  ├── Mensagem: "Escreva seção com estes gaps e citações"
  └── Resposta: Seção completa + Score de qualidade

A4.2 (Especialista) → A5.1 (Auditor)
  ├── Mensagem: "Valide esta seção"
  └── Resposta: Validação completa + Feedback
```

## L3.4: FSM Protocol Científico

A comunicação entre agentes segue protocolo de máquina de estados finitos:

```
IDLE → REQUEST (Agente A solicita tarefa)
  ↓
WAIT (Agente B processa)
  ↓
RESPOND (Agente B retorna resultado)
  ↓
IDLE (Ciclo completo)
```

## L3.5: Autonomous Board Científico

Um mecanismo de autoatribuição com bloqueio atômico para coordenação:

```
Tarefas Disponíveis:
  - Pesquisar gap 1 (prioridade: alta)
  - Pesquisar gap 2 (prioridade: média)
  - Pesquisar gap 3 (prioridade: média)
  - Escrever seção 1 (prioridade: alta, depende de: gap1, gap2)
  - Escrever seção 2 (prioridade: média, depende de: gap3)

Agentes Disponíveis:
  - A2 (Pesquisador): Atribui-se a "Pesquisar gap 1" (alta prioridade)
  - A2.1 (Pesquisador Especializado): Atribui-se a "Pesquisar gap 2"
  - A2.2 (Pesquisador Especializado): Atribui-se a "Pesquisar gap 3"
  - A4.2 (Especialista): Aguarda conclusão de gap1 e gap2, depois atribui-se a "Escrever seção 1"
```

## L3.6: Worktree Isolator Científico

Cada tarefa é executada em ambiente isolado (branch por tarefa):

```
genesis-writer-project/
├── main/
│   ├── artigo_final.md
│   ├── referencias.md
│   └── auditoria.md
├── branch-pesquisa-gap1/
│   ├── gap1_pesquisa.md
│   ├── gap1_citacoes.md
│   └── gap1_auditoria.md
├── branch-escrita-secao1/
│   ├── secao1_draft.md
│   ├── secao1_validacao.md
│   └── secao1_auditoria.md
└── branch-auditoria-final/
    ├── auditoria_constraints.md
    ├── auditoria_qualidade.md
    └── auditoria_trilha.md
```
```

### 1.6 Observability Layer (Camada de Observabilidade)

**Claude Code Components:**
- Event Bus
- Background Executor

**Integração ao Genesis-Writer v5.3:**

O Genesis-Writer agora implementa uma **Observability Layer Aprimorada (L6)** que incorpora:

```markdown
## L6.1: Event Bus Científico

O Event Bus monitora eventos do ciclo de vida científico:

```json
{
  "events": [
    {
      "timestamp": "2026-04-18T19:30:00Z",
      "event_type": "agent_spawned",
      "agent_id": "A4.2",
      "task": "Escrever seção de Estudo de Caso",
      "status": "iniciado"
    },
    {
      "timestamp": "2026-04-18T19:35:00Z",
      "event_type": "citation_validated",
      "citation_id": "cit_001",
      "doi": "10.1038/s41591-023-01234-5",
      "status": "aprovado",
      "nivel": 7
    },
    {
      "timestamp": "2026-04-18T19:40:00Z",
      "event_type": "section_completed",
      "section_id": "sec_001",
      "score": 9.8,
      "status": "aprovado"
    }
  ]
}
```

## L6.2: Background Executor Científico

Executa tarefas em segundo plano de forma não bloqueante:

- **Validação Contínua:** Valida citações enquanto agentes escrevem
- **Feedback em Tempo Real:** Fornece feedback durante a escrita
- **Otimização Contínua:** Otimiza estratégias baseado em feedback
- **Monitoramento de Saúde:** Monitora saúde dos agentes e recursos
```

### 1.7 Output Layer (Camada de Saída)

**Claude Code Components:**
- Task Result

**Integração ao Genesis-Writer v5.3:**

O Genesis-Writer agora implementa uma **Output Layer Aprimorada (L7)** que incorpora:

```markdown
## L7.1: Task Result Científico

O resultado final é entregue de forma verificada e auditada:

```json
{
  "project_id": "proj_001",
  "titulo": "Ética em Inteligência Artificial: Uma Análise Crítica",
  "status": "completo",
  "score_final": 9.8,
  "metricas": {
    "paginas": 125,
    "citacoes": 58,
    "qualis_a1_percentage": 100,
    "tempo_total": "4 horas 32 minutos",
    "agentes_utilizados": 45,
    "subagentes_utilizados": 60
  },
  "auditoria": {
    "trilha_completa": "audit_trail_001.md",
    "citacoes_validadas": 58,
    "constraints_atendidos": 500,
    "feedback_banca": "Recomendado para publicação em Nature Machine Intelligence"
  },
  "artefatos": {
    "artigo_final": "artigo_final.md",
    "referencias": "referencias.md",
    "relatorio_qualidade": "relatorio_qualidade.md",
    "trilha_auditoria": "trilha_auditoria.md"
  }
}
```

## L7.2: Memory Store Atualizado

A memória do sistema é atualizada com os aprendizados do projeto:

- **Padrões de Sucesso:** Configurações que resultaram em 9.8/10
- **Especialização de Agentes:** A4.2 agora é especialista em Estudo de Caso com 98% de acurácia
- **Biblioteca de Citações:** 58 novas citações adicionadas e validadas
- **Evolução de Raciocínios:** Raciocínio Abdutivo foi aplicado 23 vezes com 96% de sucesso
```

## 2. Master Agent Loop Integrado (Claude Code + Genesis-Writer)

O **Master Agent Loop** agora integra os princípios do Claude Code com a orquestração científica do Genesis-Writer:

```markdown
## Master Agent Loop v5.3 (Claude Code Enhanced)

### Ciclo Contínuo: Perception → Action → Observation → Evolution

1. **Perception (Percepção):**
   - Lê requisição do usuário
   - Consulta Memory Store para contexto histórico
   - Injeta skills relevantes via Skill Registry
   - Comprime contexto se necessário via Context Compressor
   - Valida permissões via Permission Gate

2. **Action (Ação):**
   - Consulta Task Graph para próximas tarefas
   - Spawna subagentes via Subagent Spawner
   - Delega tarefas com contextos isolados via Worktree Isolator
   - Comunica entre agentes via Teammate Mailboxes
   - Coordena via Autonomous Board

3. **Observation (Observação):**
   - Monitora progresso via Event Bus
   - Valida resultados via Tool Dispatch
   - Registra decisões via Micro-Audit Protocol
   - Fornece feedback via Micro Feedback Loop
   - Atualiza Memory Store

4. **Evolution (Evolução):**
   - Analisa feedback para otimizações
   - Atualiza especialização de agentes
   - Refina estratégias de raciocínio
   - Melhora padrões de sucesso
   - Prepara para próximo ciclo
```

## 3. Benefícios da Integração Claude Code

1. **Harness Engineering Robusto:** Gerenciamento seguro e eficiente de contexto e permissões
2. **Auto-Evolução:** O sistema aprende e melhora continuamente
3. **Escalabilidade:** Suporta projetos complexos sem degradação de qualidade
4. **Rastreabilidade:** Cada operação é registrada e auditável
5. **Resiliência:** Recuperação automática de falhas
6. **Eficiência:** Reutilização de contexto e cache de prompts

---

Este protocolo de integração garante que o Genesis-Writer v5.3 opera com a robustez e eficiência do Claude Code Architecture, mantendo o rigor científico e a qualidade de elite.
