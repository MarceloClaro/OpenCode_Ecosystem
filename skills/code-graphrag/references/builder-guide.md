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

---

## Estado Atual do Grafo (01/06/2026)

### Estatísticas

| Métrica | Valor |
|---------|-------|
| Nós totais | 176 |
| Arestas totais | 30 |
| Tags | 112 |
| Agents | 79 |
| MCPs | 42 |
| Skills | 28 |
| Commands | 27 |

### Distribuição de Arestas

| Tipo | Qtd | Origem → Destino |
|------|-----|-----------------|
| `references` | 14 | Skill descrições → agents/MCPs (cross-reference scan) |
| `depends_on` | 9 | command:reversa → agent:reversa-* (9 sub-agentes) |
| `affinity` | 7 | agent:pypi-searcher → agents + mcp:decisionnode + skill:decisionnode |

### Mudanças na Lógica de Build

**scan_commands refatorado**
- Antes: lista hardcoded de 9 agentes reversa
- Agora: `get_reversa_agent_names(base_dir)` varre `agents/*.md` dinamicamente
- Crawler busca padrão `reversa-*` no body do markdown

**Nova função `cross_reference_scan`** (pós-processamento)
- Executa APÓS todos os nós inseridos no banco
- Consulta `graph_nodes` por entidades conhecidas (agents, MCPs)
- Varre descrições de skills e commands procurando menções textuais
- Cria arestas `references` (weight=0.6)
- Proteções: evita autoligação, ignora nomes <4 chars, deduplica via UNIQUE

**Correção de afinidades multi-tipo**
- Antes: affinity criava apenas `agent:{name}` — quebrava para MCPs/skills (ex: `decisionnode`)
- Agora: tenta 3 prefixos (`agent:`, `mcp:`, `skill:`) e arestas quebradas são removidas automaticamente

**Remoção automática de arestas quebradas**
- `verify_integrity()` agora deleta arestas source/target inexistentes
- 11 arestas quebradas removidas no último rebuild

### Problemas Conhecidos

1. **144 nós órfãos (82%)** — esperado para grafo esparso; apenas `pypi-searcher.md` e `reversa.md` têm conectividade. Skills/MCPs sem cross-reference ficam isolados.
2. **Emojis quebram console Windows** — workaround: `python -X utf8`
3. **`fase1_analise/` diretório + `run_queries.py` não existem** — precisa ser criado para script de query padronizado
4. **Tools não mapeiam MCPs** — mapping manual seria necessário; postergado para versão futura

### Exemplo de Arestas no Grafo

```
# affinity (pypi-searcher → agentes próximos)
agent:pypi-searcher -> agent:architect (w=0.85)
agent:pypi-searcher -> mcp:decisionnode (w=0.9)
agent:pypi-searcher -> skill:decisionnode (w=0.9)

# depends_on (comando → agentes)
command:reversa -> agent:reversa-scout (w=0.7)
command:reversa -> agent:reversa-archaeologist (w=0.7)

# references (skill → agentes/MCPs)
skill:decisionnode -> mcp:decisionnode (w=0.6)
skill:mirofish-sync -> agent:reversa-scout (w=0.6)
skill:reasoning-orchestrator-v12 -> mcp:sequential-thinking (w=0.6)
```

### Arquivos Relevantes

| Arquivo | Função |
|---------|--------|
| `scripts/build_graph.py` | Orquestrador principal (647 linhas) |
| `.reversa/code-graph.db` | Banco SQLite do grafo |
| `grafo_agentes.json` | Output JSON com 176 nós / 30 arestas |
| `references/schema.md` | Documentação do schema |
| `SKILL.md` | Skill principal do code-graphrag |

### Próximos Passos Sugeridos

1. Criar `fase1_analise/run_queries.py` — script de query padronizado para extrair subgrafos
2. Adicionar arestas `tools` com tabela de correspondência manual tool→MCP
3. Enriquecer descrições de skills para melhorar matching no cross-reference scan
4. Considerar graph embedding (Node2Vec / GraphSAGE) para similaridade semântica entre nós
