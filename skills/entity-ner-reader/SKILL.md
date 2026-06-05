---
name: entity-ner-reader
description: >
  Leitura e filtragem de entidades em grafos de conhecimento. Inspirado pelo
  EntityReader do MiroFish-Offline, extrai nós com tipos significativos,
  enriquece com arestas e nós relacionados, e suporta consultas por tipo de
  entidade. Use quando precisar extrair entidades nomeadas de um grafo,
  filtrar por tipo, ou obter contexto completo de uma entidade.
license: MIT
compatibility: opencode
allowed-tools: Read, Grep, Glob, Bash, Write, Sqlite
metadata:
  author: Reversa Engine (padrão MiroFish-Offline entity_reader.py)
  version: "1.0.0"
  domain: knowledge
  triggers: entity, entidade, ner, filter, filtrar, entidade nomeada
  role: analyst
  scope: knowledge
  output-format: json
  related-skills: code-graphrag, ontology-generator, hybrid-graph-retrieval
  inspired-by: MiroFish-Offline EntityReader (entity_reader.py)
---

# Entity NER Reader — Leitura e Filtragem de Entidades em Grafos

Inspirado pelo **EntityReader** do MiroFish-Offline (`entity_reader.py`),
que substituiu o `zep_entity_reader.py` original. Fornece capacidade de
ler nós de um grafo, filtrar por tipo de entidade significativa, e
enriquecer cada entidade com suas arestas e nós vizinhos.

## Arquitetura

```
MiroFish: GraphStorage → EntityReader → filter_defined_entities() → Entidades + Contexto
OpenCode: SQLite/Neo4j → EntityReader → filter_by_type() → Entidades + Relações

Entidades:
  ├── uuid + name + labels + summary + attributes
  ├── related_edges (direção, nome, fato)
  └── related_nodes (uuid, nome, labels, sumário)
```

## Componentes

### EntityNode
Estrutura de dados para uma entidade do grafo:
- `uuid`, `name`, `labels`, `summary`, `attributes`
- `related_edges`: arestas de entrada/saída com direção e fato
- `related_nodes`: nós vizinhos com informações resumidas

### FilteredEntities
Conjunto filtrado:
- `entities`: lista de EntityNode
- `entity_types`: tipos encontrados (Set)
- `total_count` / `filtered_count`: estatísticas

### EntityReader
Serviço principal com 3 modos de consulta:
1. `filter_defined_entities()` — Filtra todos os nós com tipos significativos
2. `get_entity_with_context()` — Entidade única com contexto completo (O(degree))
3. `get_entities_by_type()` — Todas as entidades de um tipo específico

## Quando Usar

| Cenário | Descrição |
|---------|-----------|
| Extração de entidades | "Quais entidades existem no grafo?" |
| Filtragem por tipo | "Me mostre só as entidades do tipo 'Person'" |
| Contexto completo | "O que está conectado à entidade X?" |
| Análise de relacionamentos | "Quais são as arestas de/para a entidade Y?" |
| Preparação para busca | "Alimente o Hybrid Graph Retrieval com entidades filtradas" |

## Workflow

### Modo 1: Listar Todas as Entidades com Tipos Significativos

```
python scripts/entity_reader.py list --graph <graph_id>
```

Filtra nós cujas labels vão além de "Entity"/"Node", revelando apenas
entidades com tipos semânticos definidos.

### Modo 2: Filtrar por Tipo Específico

```
python scripts/entity_reader.py filter --graph <graph_id> --type Person
```

Retorna apenas entidades de um tipo específico, com arestas e nós
relacionados.

### Modo 3: Contexto de Entidade Única

```
python scripts/entity_reader.py context --graph <graph_id> --uuid <entity_uuid>
```

Obtém entidade + arestas + nós vizinhos em uma única consulta otimizada
(O(degree) em vez de O(n)).

## Escala de Confiança

- 🟢 **CONFIRMADO** — Dado extraído diretamente do grafo
- 🟡 **INFERIDO** — Tipo inferido pela lógica de filtragem (labels)
- 🔴 **LACUNA** — Entidade sem arestas (órfã no grafo)

## Schema SQLite

```sql
CREATE TABLE entities (
    uuid TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    labels TEXT,           -- JSON array
    summary TEXT,
    attributes TEXT,       -- JSON dict
    entity_type TEXT,      -- primary type
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE entity_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_uuid TEXT NOT NULL REFERENCES entities(uuid),
    direction TEXT NOT NULL,  -- 'incoming' | 'outgoing'
    edge_name TEXT NOT NULL,
    fact TEXT,
    target_uuid TEXT,
    source_uuid TEXT
);

CREATE TABLE entity_types (
    type TEXT PRIMARY KEY,
    count INTEGER DEFAULT 0,
    description TEXT
);
```

## Regras

### MUST DO
- Usar SQLite para persistência local
- Registrar entidades com seus tipos e metadados
- Enriquecer com arestas e nós relacionados (quando solicitado)
- Oferecer consulta por tipo e por UUID
- Detectar e alertar entidades órfãs (sem arestas)

### MUST NOT DO
- Ignorar labels de tipo (a lógica de filtragem é essencial)
- Retornar nós sem tipo (só "Entity") como entidades significativas
- Carregar todos os nós quando apenas contexto de um é necessário
- Modificar o grafo original (apenas leitura)
