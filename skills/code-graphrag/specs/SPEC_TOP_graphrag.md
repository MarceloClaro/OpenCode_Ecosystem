# SPEC_TOP_graphrag — Code GraphRAG TDD Specification

**Skill:** code-graphrag  
**Source:** scripts/build_graph.py → init_db, insert_nodes, verify_integrity  
**Framework:** pytest  
**Status:** Spec-Driven

---

## CT-1: test_init — Inicializacao do banco SQLite e schema

**Objetivo:** Verificar que `init_db()` cria as tres tabelas do schema
(`graph_nodes`, `graph_edges`, `graph_tags`).

**Passos:**
1. Criar banco SQLite temporario
2. Chamar `bg.init_db(db_path)`
3. Consultar `sqlite_master` e verificar nomes das tabelas

**Esperado:** As 3 tabelas existem no banco.

---

## CT-2: test_insert_nodes — Insercao e consulta de nos

**Objetivo:** Confirmar que `insert_nodes()` persiste registros e
`clear_db()` remove todos.

**Passos:**
1. `clear_db(conn)` → limpar estado
2. `insert_nodes(conn, [node_dict])`
3. `SELECT id, name FROM graph_nodes` → row existe

**Esperado:** No inserido e recuperavel.

---

## CT-3: test_check_integrity — Verificacao de integridade do grafo

**Objetivo:** Validar que `verify_integrity()` retorna estatisticas
corretas apos inserir nos e arestas.

**Passos:**
1. Inserir 2 nos + 1 aresta
2. Chamar `verify_integrity(conn)`
3. Verificar `stats["total_nodes"] == 2` e `stats["total_edges"] == 1`

**Esperado:** Contagem correta de nos e arestas.

---

## CT-4: test_available — Constantes e geracao de reasoning nodes

**Objetivo:** Garantir que `REASONING_TYPES`, `REASONING_KEYWORDS` e
`TOOL_MCP_MAP` estao populados e `generate_reasoning_nodes()` produz
mais de 10 nos.

**Passos:**
1. Verificar `len(bg.REASONING_TYPES) > 0`
2. Verificar `len(bg.REASONING_KEYWORDS) > 0`
3. `generate_reasoning_nodes()` → `len(nodes) > 10`

**Esperado:** Motor de raciocinio populado.
