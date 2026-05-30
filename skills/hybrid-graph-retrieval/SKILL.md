---
name: hybrid-graph-retrieval
description: >
  Três estratégias complementares de busca em grafo de conhecimento,
  inspiradas pelo GraphTools do MiroFish-Offline (graph_tools.py).
  InsightForge (mergulho profundo com decomposição de perguntas),
  PanoramaSearch (varredura ampla com contexto histórico),
  QuickSearch (busca rápida por palavra-chave).
  Use quando precisar consultar um grafo com diferentes níveis de
  profundidade: análise profunda, visão panorâmica, ou resposta rápida.
license: MIT
compatibility: opencode
allowed-tools: Read, Grep, Glob, Bash, Write
metadata:
  author: Reversa Engine (padrão MiroFish-Offline GraphTools)
  version: "1.0.0"
  domain: retrieval
  triggers: busca, graph, grafo, pesquisa, insight, panorama, quick search, graph tools
  role: searcher
  scope: retrieval
  output-format: json
  related-skills: code-graphrag, oasis-profile-gen, report-agent-react
  inspired-by: MiroFish-Offline graph_tools.py (InsightForge, PanoramaSearch, QuickSearch, InterviewResult)
---

# Hybrid Graph Retrieval — 3 Estratégias de Busca em Grafo

Inspirado pelo **GraphToolsService** do MiroFish-Offline — um conjunto
de ferramentas de recuperação de informação em grafo com três estratégias
complementares, cada uma otimizada para um cenário diferente.

## Arquitetura (Padrão GraphTools)

```
MiroFish-Offline:  GraphStorage → GraphToolsService → InsightForge / PanoramaSearch / QuickSearch
                          ↓                  ↓
                   Neo4j + Ollama       LLM Sub-question Generator

OpenCode:          SQLite/GraphRAG → HybridRetrievalEngine → 3 Search Strategies
                          ↓                        ↓
                   code-graph.db               LLM Decomposition
```

## As 3 Estratégias

### 1. 🔍 InsightForge — Análise Profunda

**Quando usar:** Perguntas complexas que exigem compreensão multidimensional.

**Pipeline:**
```
Pergunta original
  → LLM decompõe em sub-perguntas (quem, o que, por que, como)
  → Cada sub-pergunta busca no grafo (semântico + keyword)
  → Entidades relevantes são extraídas com detalhes
  → Cadeias de relacionamento são montadas
  → Resultado integrado com fatos, entidades e relações
```

**Melhoria em relação ao original:** Sub-perguntas agora incluem
dimensões pré-definidas (causa/efeito, temporal, stakeholder) além
da decomposição livre do LLM.

| Aspecto | Original | Melhoria |
|---------|----------|----------|
| Decomposição | Apenas LLM | LLM + dimensões fixas |
| Entidades | UUID-based | Nome + tipo + contexto |
| Cadeias | Simples | Com peso e direção |

### 2. 🗺️ PanoramaSearch — Visão Panorâmica

**Quando usar:** Precisa entender o contexto completo, incluindo
informações históricas/obsoletas.

**Pipeline:**
```
Consulta
  → Obtém TODOS os nós e arestas
  → Categoriza: ativo vs. histórico/expirado
  → Pontua por relevância à consulta
  → Retorna visão completa do grafo
```

**Melhoria em relação ao original:** Adiciona categorização
automática por domínio/tópico, não apenas por data.

### 3. ⚡ QuickSearch — Busca Rápida

**Quando usar:** Precisa de uma resposta rápida sem contexto adicional.

**Pipeline:**
```
Consulta → Busca semântica + keyword → Top-K resultados
```

**Melhoria em relação ao original:** Adiciona cache de consultas
frequentes e threshold de confiança configurável.

### 4. 🎯 InterviewResult — Resultado de Entrevista

Estrutura para representar respostas de múltiplos agentes simulados
entrevistados sobre um tópico.

```json
{
  "interview_topic": "Impacto das mudanças climáticas",
  "interview_questions": ["O que você pensa sobre...", "Como isso afeta..."],
  "selected_agents": [{"name": "Dr. Silva", "role": "Cientista"}, ...],
  "interviews": [
    {"agent_name": "Dr. Silva", "agent_role": "Cientista", "question": "...", "response": "..."}
  ],
  "selection_reasoning": "Selecionados por diversidade de perspectiva",
  "summary": "Análise consolidada das entrevistas"
}
```

## Quando Usar Cada Estratégia

| Estratégia | Cenário | Profundidade | Velocidade | Cobertura |
|-----------|---------|-------------|-----------|-----------|
| **InsightForge** | Análise complexa, relatórios | Máxima | Lenta | Focada |
| **PanoramaSearch** | Contexto geral, histórico | Média | Média | Máxima |
| **QuickSearch** | Perguntas simples, FAQ | Mínima | Rápida | Limitada |
| **InterviewResult** | Múltiplas perspectivas | Alta | Variável | Agentes selecionados |

## Workflow

### Fase 1: INSPECIONAR — Conhecer o Grafo

Antes de buscar, entenda a estrutura:
- Tipos de nós disponíveis (Agent, Skill, MCP, File, etc.)
- Tipos de arestas (DEPENDS_ON, IMPORTS, EXTENDS, etc.)
- Estatísticas: total de nós, arestas, densidade

### Fase 2: SELECIONAR — Escolher a Estratégia

```
Pergunta curta (< 5 palavras)?                   → QuickSearch
Pergunta complexa ("Qual o impacto de X em Y?")  → InsightForge
"Me mostre tudo sobre X" / contexto histórico    → PanoramaSearch
"Entreviste os agentes sobre X"                  → InterviewResult
```

### Fase 3: EXECUTAR — Chamar o Script

```bash
# InsightForge
python scripts/hybrid_search.py insight --graph <id> --query "Pergunta complexa"

# PanoramaSearch
python scripts/hybrid_search.py panorama --graph <id> --query "Contexto geral"

# QuickSearch
python scripts/hybrid_search.py quick --graph <id> --query "busca rápida"

# InterviewResult (simulado)
python scripts/hybrid_search.py interview --profiles profiles.json --topic "Tópico"
```

## Estruturas de Dados

### SearchResult
```python
{
    "facts": List[str],        # Fatos encontrados (texto)
    "edges": List[Dict],        # Arestas com origem/destino/nome/fato
    "nodes": List[Dict],        # Nós com uuid/nome/labels/summary
    "query": str,               # Consulta original
    "total_count": int          # Total de resultados
}
```

### InsightForgeResult (estende SearchResult)
```python
{
    # ...SearchResult fields...
    "sub_queries": List[str],           # Sub-perguntas geradas
    "semantic_facts": List[str],         # Fatos semânticos agrupados
    "entity_insights": List[Dict],       # Entidades com fatos relacionados
    "relationship_chains": List[str]     # Cadeias: "A --[relação]--> B"
}

### PanoramaResult
```python
{
    "all_nodes": List[NodeInfo],
    "all_edges": List[EdgeInfo],
    "active_facts": List[str],       # Fatos válidos atualmente
    "historical_facts": List[str],   # Fatos expirados/históricos
    "total_nodes": int,
    "total_edges": int
}
```

## Exemplos de Uso

```bash
# Análise profunda de impacto
/hybrid-search insight --graph mirofish_abc --query "Qual o impacto das novas políticas de privacidade?"

# Visão panorâmica
/hybrid-search panorama --graph mirofish_abc --query "privacidade"

# Busca rápida
/hybrid-search quick --graph mirofish_abc --query "GDPR"

# Entrevistar agentes
/hybrid-search interview --profiles profiles.json --topic "Privacidade de dados"
```

## Referências

- Código original: `graph_tools.py` (MiroFish-Offline)
- Estruturas: `InsightForgeResult`, `PanoramaResult`, `SearchResult`, `InterviewResult`, `AgentInterview`
- SKILL relacionada: `code-graphrag` (fonte de dados do grafo)
- SKILL relacionada: `report-agent-react` (consumidor de buscas profundas)
