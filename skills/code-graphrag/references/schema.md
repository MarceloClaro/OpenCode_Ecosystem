# Schema do Grafo de Conhecimento — Code GraphRAG

> Inspirado pelo GraphRAG do MiroFish (Zep Cloud graph storage).

---

## Tabelas SQLite

### `graph_nodes` — Nós do Grafo

Armazena entidades do ecossistema OpenCode.

```sql
CREATE TABLE IF NOT EXISTS graph_nodes (
    id          TEXT PRIMARY KEY,      -- ex: "agent:scout", "skill:swarm-review", "mcp:sqlite"
    type        TEXT NOT NULL,         -- agent | skill | mcp | command | module | file | interface | config
    name        TEXT NOT NULL,         -- nome legível
    description TEXT,                  -- descrição curta
    path        TEXT,                  -- caminho relativo no filesystem
    metadata    TEXT DEFAULT '{}',     -- JSON com atributos específicos do tipo
    created_at  TEXT DEFAULT (datetime('now')),
    updated_at  TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_nodes_type ON graph_nodes(type);
CREATE INDEX idx_nodes_name ON graph_nodes(name);
```

### Tipos de Nó

| Type | Descrição | Exemplo ID | metadata (exemplo) |
|------|-----------|-----------|-------------------|
| `agent` | Agente OpenCode | `agent:scout` | `{"tools": ["read","grep"], "mode": "subagent"}` |
| `skill` | Skill carregável | `skill:swarm-review` | `{"domain": "quality", "triggers": ["swarm review"]}` |
| `mcp` | Servidor MCP | `mcp:sqlite` | `{"enabled": true, "tags": ["core","database"]}` |
| `command` | Comando slash | `command:reversa` | `{"description": "Ativa framework Reversa"}` |
| `module` | Módulo/pacote | `module:skills` | `{"language": "markdown", "file_count": 42}` |
| `file` | Arquivo específico | `file:opencode.json` | `{"size": 15473, "lines": 547}` |
| `config` | Configuração | `config:state.json` | `{"format": "json", "purpose": "estado do Reversa"}` |

### `graph_edges` — Arestas do Grafo

Armazena relações entre nós.

```sql
CREATE TABLE IF NOT EXISTS graph_edges (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id   TEXT NOT NULL REFERENCES graph_nodes(id),
    target_id   TEXT NOT NULL REFERENCES graph_nodes(id),
    type        TEXT NOT NULL,     -- imports | depends_on | registers_in | extends | implements | configured_by | related_to | contains
    weight      REAL DEFAULT 1.0,  -- 0.0 (fraca) a 1.0 (forte)
    metadata    TEXT DEFAULT '{}', -- JSON com contexto da relação
    created_at  TEXT DEFAULT (datetime('now')),
    UNIQUE(source_id, target_id, type)
);

CREATE INDEX idx_edges_source ON graph_edges(source_id);
CREATE INDEX idx_edges_target ON graph_edges(target_id);
CREATE INDEX idx_edges_type ON graph_edges(type);
```

### Tipos de Aresta

| Type | Descrição | Exemplo | Peso Padrão |
|------|-----------|---------|:-----------:|
| `imports` | Importa/usa dependência | `agent:scout → skill:swarm-review` | 1.0 |
| `depends_on` | Depende funcionalmente | `command:reversa → agent:reversa` | 1.0 |
| `registers_in` | Registrado em container DI | `plugin:manus-evolve → container:plugins` | 0.8 |
| `extends` | Herda de | `agent:reversa-scout → agent:base` | 0.9 |
| `implements` | Implementa interface | `service:x → interface:IStateManager` | 0.9 |
| `configured_by` | Configurado por | `mcp:github → config:opencode.json` | 0.5 |
| `related_to` | Relação semântica | `skill:code-reviewer → skill:swarm-review` | 0.3 |
| `contains` | Contém (hierarquia) | `module:skills → skill:swarm-review` | 0.7 |

### `graph_tags` — Tags para Busca Facetada

```sql
CREATE TABLE IF NOT EXISTS graph_tags (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id TEXT NOT NULL REFERENCES graph_nodes(id),
    tag     TEXT NOT NULL,
    UNIQUE(node_id, tag)
);

CREATE INDEX idx_tags_tag ON graph_tags(tag);
CREATE INDEX idx_tags_node ON graph_tags(node_id);
```

### `graph_queries` — Histórico de Consultas (Opcional)

```sql
CREATE TABLE IF NOT EXISTS graph_queries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    query_text  TEXT NOT NULL,
    query_type  TEXT NOT NULL,    -- structural | semantic | path
    result_summary TEXT,
    executed_at TEXT DEFAULT (datetime('now'))
);
```

---

## Consultas de Exemplo

### Estruturais

```sql
-- Agentes que usam um skill específico
SELECT n.name, e.type
FROM graph_nodes n
JOIN graph_edges e ON n.id = e.source_id
WHERE e.target_id = 'skill:swarm-review' AND e.type = 'imports';

-- Dependências de um MCP
SELECT target_id, type, weight
FROM graph_edges
WHERE source_id = 'mcp:sqlite';

-- Nós por tag
SELECT n.* FROM graph_nodes n
JOIN graph_tags t ON n.id = t.node_id
WHERE t.tag IN ('security', 'quality');
```

### Path Finding (CTE Recursiva)

```sql
-- Caminho mais curto entre dois nós (até 10 hops)
WITH RECURSIVE path_finder AS (
    SELECT source_id, target_id, 1 AS depth, 
           CAST(source_id || '→' || target_id AS TEXT) AS trail
    FROM graph_edges 
    WHERE source_id = 'agent:scout'
    
    UNION ALL
    
    SELECT e.source_id, e.target_id, p.depth + 1,
           CAST(p.trail || '→' || e.target_id AS TEXT)
    FROM graph_edges e
    JOIN path_finder p ON e.source_id = p.target_id
    WHERE p.depth < 10 AND instr(p.trail, e.target_id) = 0
)
SELECT trail, depth FROM path_finder
WHERE target_id = 'mcp:filesystem'
ORDER BY depth
LIMIT 5;
```

### Métricas

```sql
-- Contagem por tipo
SELECT type, COUNT(*) as count FROM graph_nodes GROUP BY type ORDER BY count DESC;

-- Nós com mais conexões
SELECT n.id, n.name, COUNT(e.id) as edge_count
FROM graph_nodes n
JOIN graph_edges e ON n.id = e.source_id
GROUP BY n.id
ORDER BY edge_count DESC
LIMIT 10;

-- Nós órfãos (sem arestas)
SELECT n.id, n.name, n.type
FROM graph_nodes n
LEFT JOIN graph_edges e ON n.id = e.source_id OR n.id = e.target_id
WHERE e.id IS NULL;
```

---

## Manutenção

### Build Completo
```bash
python scripts/build_graph.py --rebuild
```

### Atualização Incremental
```bash
python scripts/build_graph.py --update
# Escaneia apenas arquivos modificados
```

### Verificação de Integridade
```bash
python scripts/build_graph.py --verify
# Reporta: nós órfãos, arestas quebradas, ciclos
```
