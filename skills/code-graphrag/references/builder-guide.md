# Guia do Builder — Construindo o Grafo de Conhecimento

> Inspirado pelo `graph_builder.py` do MiroFish.

---

## Visão Geral

O builder escaneia o ecossistema OpenCode (`~/.config/opencode/`) e constrói
um grafo de conhecimento em SQLite com nós, arestas e tags.

## Fluxo de Construção

```
Scanner                     Builder                     SQLite
──────────────────────────────────────────────────────────────
  agents/*.md     ──►  parse frontmatter        ──►  INSERT nodes
  skills/*/SKILL.md──►  parse metadata + tags    ──►  INSERT nodes
  command/*.md    ──►  parse description         ──►  INSERT nodes
  opencode.json   ──►  extract MCPs + LSP        ──►  INSERT nodes
  *.md, *.json,   ──►  grep imports/dependencies ──►  INSERT edges
  *.ts, *.py                                   ──►  INSERT tags
                                                    ──►  VERIFY integrity
```

## Onde o Grafo é Armazenado

```
Database: .reversa/code-graph.db (SQLite)
Tables:   graph_nodes, graph_edges, graph_tags, graph_queries
```

## Como Executar

### 1. Build Completo (primeira vez)
```
python scripts/build_graph.py --rebuild
```
Remove o banco existente e reconstrói do zero.

### 2. Build Incremental (atualizações)
```
python scripts/build_graph.py --update
```
Escaneia apenas arquivos modificados desde o último build.

### 3. Verificação de Integridade
```
python scripts/build_graph.py --verify
```
Reporta:
- Nós órfãos (sem arestas)
- Arestas para nós inexistentes
- Ciclos no grafo
- Estatísticas (total de nós, arestas, tags)

### 4. Consulta Rápida
```
python scripts/build_graph.py --query "find all security-related components"
```
Usa busca semântica nas tags + descrições.

## Scanner de Dependências

O builder extrai relações automaticamente:

### De arquivos de agente (`agents/*.md`)
- `tools:` → relação com ferramentas MCP
- `mode:` → relação com modo de execução
- `description:` → tags extraídas por NLP básico

### De skills (`skills/*/SKILL.md`)
- `related-skills:` → arestas `related_to`
- `metadata.tags:` → populate `graph_tags`
- `metadata.domain:` → tag do domínio

### De comandos (`command/*.md`)
- `description:` → relação com agentes mencionados

### De `opencode.json`
- `mcp.*.command` → cada MCP vira um nó
- `mcp.*.tags` → tags do MCP
- `mcp.*.enabled` → metadado de status

## Algoritmo de Extração de Relações

```python
def extract_relations(file_path, content):
    relations = []
    
    # Skill -> related-skills
    if 'related-skills:' in content:
        for skill in extract_yaml_list(content, 'related-skills'):
            relations.append(('imports', f'skill:{skill}', 0.8))
    
    # Agent -> tools (MCPs)
    if 'tools:' in content:
        for tool in extract_yaml_list(content, 'tools'):
            if tool in known_mcps:
                relations.append(('depends_on', f'mcp:{tool}', 0.9))
    
    # Command -> agent references
    for agent_name in known_agents:
        if agent_name in content:
            relations.append(('depends_on', f'agent:{agent_name}', 0.5))
    
    return relations
```
