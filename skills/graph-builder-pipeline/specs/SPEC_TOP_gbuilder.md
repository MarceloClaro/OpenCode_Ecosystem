# SPEC_TOP_gbuilder — GraphBuilder TDD Specification

**Skill:** graph-builder-pipeline  
**Source:** scripts/graph_builder.py → GraphBuilderService, TaskManager, TextProcessor  
**Framework:** pytest  
**Status:** Spec-Driven

---

## CT-1: test_init — TaskManager e MockGraphStorage

**Objetivo:** Verificar que `TaskManager` cria e recupera tarefas, e
`MockGraphStorage` inicializa banco SQLite.

**Passos:**
1. `TaskManager()` → `_tasks` vazio
2. `create_task("test")` → task_id com prefixo "task_"
3. `get_task(task_id)` → `status == PENDING`

**Esperado:** Task manager funcional.

---

## CT-2: test_text_processor — Chunking com overlap

**Objetivo:** Confirmar que `TextProcessor.split_text()` divide texto
em chunks de tamanho controlado, com overlap configurado, e trata
entradas vazias/curtas.

**Passos:**
1. Texto de ~300 chars, chunk_size=100, overlap=20 → `len(chunks) > 1`
2. Texto vazio → `[]`
3. Texto curto (< chunk_size) → `[texto]`

**Esperado:** Chunking correto em todos os casos.

---

## CT-3: test_build_graph — build_graph_async com acompanhamento

**Objetivo:** Validar que `build_graph_async()` inicia worker thread,
processa chunks, e completa com status `COMPLETED`.

**Passos:**
1. `builder.build_graph_async(text, ontology, graph_name="TestGraph")`
2. Poll ate `task.status in (COMPLETED, FAILED)` com timeout de 10s
3. Verificar `task.status == COMPLETED` e `task.result["graph_id"]`

**Esperado:** Construcao assincrona concluida com sucesso.

---

## CT-4: test_available — CRUD de grafos via MockGraphStorage

**Objetivo:** Garantir que `create_graph()`, `get_graph_info()`,
`get_graph_data()` e `delete_graph()` funcionam corretamente.

**Passos:**
1. `create_graph("TestGraph")` → graph_id
2. `get_graph_info(graph_id)` → retorna dados
3. `get_graph_data(graph_id)` → contem "episodes"
4. `delete_graph(graph_id)` → `get_graph_info` retorna node_count=0

**Esperado:** Ciclo CRUD completo funcional.
