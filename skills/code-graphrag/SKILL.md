---
name: code-graphrag
description: >
  Grafo de conhecimento do ecossistema OpenCode, inspirado pelo GraphRAG +
  Zep Cloud do MiroFish. Mapeia agentes, skills, MCPs, comandos e suas
  relações em um grafo pesquisável via SQLite. Permite buscas semânticas
  e estruturais ("o que depende de X?", "quais agentes usam Y?").
  Use quando precisar entender dependências, impacto de mudanças, ou
  navegar pelo ecossistema OpenCode de forma não-linear.
license: MIT
compatibility: opencode
allowed-tools: Read, Grep, Glob, Bash, Write
metadata:
  author: Reversa Engine (padrão MiroFish)
  version: "1.0.0"
  domain: knowledge
  triggers: graph, grafo, knowledge graph, dependências, impacto, code graph
  role: analyst
  scope: knowledge
  output-format: markdown
  related-skills: architecture-designer, spec-miner
  inspired-by: MiroFish GraphRAG + Zep Cloud (zep_tools.py, graph_builder.py)
---

# Code GraphRAG — Grafo de Conhecimento do Ecossistema

Inspirado pelo **GraphRAG** do MiroFish — um grafo de conhecimento onde
**nós** representam entidades do código e **arestas** representam relações
semânticas, permitindo buscas que vão além de texto literal.

## Arquitetura (Padrão MiroFish GraphRAG)

```
MiroFish:  Entity Extraction → Graph Building → Zep Storage → InsightForge
OpenCode:  Scanner → Node/Edge Builder → SQLite Graph → Query Engine

Nós (Nodes):
  ├── Agent       ── agente OpenCode
  ├── Skill       ── skill carregável
  ├── MCP         ── servidor MCP
  ├── Command     ── comando slash
  ├── Module      ── módulo de código
  ├── File        ── arquivo individual
  ├── Interface   ── interface/contrato
  └── Config      ── configuração

Arestas (Edges):
  ├── IMPORTS         ── importa dependência
  ├── DEPENDS_ON      ── depende de
  ├── REGISTERS_IN    ── registrado em
  ├── EXTENDS         ── estende/herda
  ├── IMPLEMENTS      ── implementa
  ├── CONFIGURED_BY   ── configurado por
  └── RELATED_TO      ── relacionado semanticamente
```

## Quando Usar

| Cenário | Descrição |
|---------|-----------|
| Análise de impacto | "O que quebra se eu mudar o MCP X?" |
| Navegação do ecossistema | "Quais agentes dependem do skill Y?" |
| Documentação | "Gere diagrama de dependências do módulo Z" |
| Refatoração | "Qual o caminho crítico entre agentes A e B?" |
| Onboarding | "Mapa completo do ecossistema para novo contribuidor" |

## Workflow

### Fase 1: BUILD — Construir o Grafo

1. **Execute o builder** (`scripts/build_graph.py`) que:
   - Escaneia `agents/` → nós do tipo Agent
   - Escaneia `skills/` → nós do tipo Skill
   - Escaneia `command/` → nós do tipo Command
   - Lê `opencode.json` → nós do tipo MCP
   - Extrai relações de `import`, `uses`, `depends_on` dos arquivos

2. **Popula as tabelas SQLite**:
   - `graph_nodes` — todos os nós com tipo e metadados
   - `graph_edges` — todas as arestas com tipo e peso
   - `graph_tags` — tags para busca facetada

3. **Verifica integridade**:
   - Nós órfãos (sem arestas)
   - Arestas para nós inexistentes
   - Ciclos no grafo

### Fase 2: QUERY — Consultar o Grafo

**Consultas Estruturais** (SQL direto):
```sql
-- Todos agentes
SELECT * FROM graph_nodes WHERE type = 'agent';

-- Dependências de um MCP específico
SELECT n.* FROM graph_nodes n
JOIN graph_edges e ON n.id = e.target_id
WHERE e.source_id = 'mcp:filesystem' AND e.type = 'depends_on';

-- Caminho entre dois nós (usando CTE recursiva)
WITH RECURSIVE path AS (
  SELECT source_id, target_id, 1 AS depth
  FROM graph_edges WHERE source_id = 'agent:scout'
  UNION ALL
  SELECT e.source_id, e.target_id, p.depth + 1
  FROM graph_edges e JOIN path p ON e.source_id = p.target_id
  WHERE p.depth < 10
)
SELECT * FROM path;
```

**Consultas Semânticas** (via mem0-mcp ou grepping tags):
```
"find all components related to security"
→ Busca por tags 'security', 'owasp', 'auth'
→ Retorna agentes, skills, MCPs relacionados
```

### Fase 3: VISUALIZE — Visualizar o Grafo

Gere representações do grafo:
- **Lista hierárquica** — "Agentes → Skills usados → MCPs dependentes"
- **Tabela de adjacência** — "Nó → Vizinhos diretos"
- **Dot/Graphviz** — Para visualização externa
- **Markdown diagram** — Diagrama ASCII para documentação

## Schema do Grafo

O schema completo está em `references/schema.md`. Resumo:

```sql
CREATE TABLE graph_nodes (
    id TEXT PRIMARY KEY,          -- ex: "agent:scout", "skill:swarm-review"
    type TEXT NOT NULL,           -- agent | skill | mcp | command | module | file | interface | config
    name TEXT NOT NULL,
    description TEXT,
    path TEXT,                    -- caminho no filesystem
    metadata JSON,                -- metadados específicos do tipo
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE graph_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL REFERENCES graph_nodes(id),
    target_id TEXT NOT NULL REFERENCES graph_nodes(id),
    type TEXT NOT NULL,           -- imports | depends_on | registers_in | extends | implements | configured_by | related_to
    weight REAL DEFAULT 1.0,     -- peso da relação (0-1)
    metadata JSON,
    UNIQUE(source_id, target_id, type)
);

CREATE TABLE graph_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id TEXT NOT NULL REFERENCES graph_nodes(id),
    tag TEXT NOT NULL,
    UNIQUE(node_id, tag)
);
```

## Output Template

````markdown
# Code GraphRAG — [consulta]

## Resultado
[descrição do que foi encontrado]

### Nós
| ID | Tipo | Nome | Descrição |
|----|------|------|-----------|

### Conexões
| Origem | Tipo | Destino | Peso |
|--------|------|---------|------|

### Caminhos (se aplicável)
[ASCII graph do caminho encontrado]

### Insights
- [observações sobre padrões descobertos]
- [dependências críticas]
- [nós órfãos ou isolados]
````

## Regras

### MUST DO
- Usar SQLite para persistência (MCP sqlite disponível)
- Registrar todo nó com tipo, nome e path
- Verificar integridade após cada build
- Oferecer consultas estruturais E semânticas
- Documentar o schema em `references/schema.md`

### MUST NOT DO
- Criar nós sem arestas (nós órfãos devem ser alertados, não criados)
- Ignorar ciclos no grafo
- Deletar o grafo sem confirmar com o usuário
- Usar busca apenas textual quando semântica for possível
