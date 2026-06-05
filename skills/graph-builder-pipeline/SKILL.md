---
name: graph-builder-pipeline
description: >
  Pipeline assíncrono de construção de grafos de conhecimento. Inspirado pelo
  GraphBuilderService do MiroFish-Offline, processa texto em chunks, extrai
  entidades e relações via NER, e persiste em Neo4j/SQLite com progresso
  rastreável via TaskManager. Use quando precisar construir um grafo a partir
  de texto bruto com ontologia pré-definida.
license: MIT
compatibility: opencode
allowed-tools: Read, Grep, Glob, Bash, Write, Sqlite
metadata:
  author: Reversa Engine (padrão MiroFish-Offline graph_builder.py)
  version: "1.0.0"
  domain: pipeline
  triggers: graph, grafo, build, construir, pipeline, chunk, batch, NER
  role: builder
  scope: pipeline
  output-format: json
  related-skills: ontology-generator, entity-ner-reader, code-graphrag, machine-states
  inspired-by: MiroFish-Offline GraphBuilderService (graph_builder.py)
---

# Graph Builder Pipeline — Construção Assíncrona de Grafos

Inspirado pelo **GraphBuilderService** do MiroFish-Offline (`graph_builder.py`).
Pipeline completo para construir grafos de conhecimento a partir de texto
bruto, usando ontologia pré-definida, chunking, NER e persistência.

## Arquitetura

```
Texto Bruto → Chunking (500 chars, 50 overlap)
  → Ontologia → Batches (3 chunks/batch)
    → NER + Embedding + Inserção (por chunk)
      → Grafo Final (Nós + Arestas)
        → GraphInfo {node_count, edge_count, entity_types}
```

## Componentes

### GraphBuilderService
Pipeline principal com execução assíncrona em background thread:

1. **create_graph(name)** → graph_id
2. **set_ontology(graph_id, ontology)** → armazena ontologia no nó do grafo
3. **add_text_batches()** → processa chunks em lotes com callback de progresso
4. **_get_graph_info()** → estatísticas finais

### GraphInfo
Dataclass com:
- `graph_id`, `node_count`, `edge_count`, `entity_types`

### TaskManager
Gerenciamento de tarefas assíncronas:
- Estados: PROCESSING → COMPLETED / FAILED
- Progresso percentual (5% → 100%)
- Mensagens de status por etapa
- Suporte a fallback com traceback

### TextProcessor.split_text()
Chunking inteligente com tamanho e overlap configuráveis.

## Quando Usar

| Cenário | Descrição |
|---------|-----------|
| Construção de grafo | "Construa um grafo a partir deste documento" |
| Pipeline NER | "Extraia entidades do texto chunk por chunk" |
| Processamento batch | "Processe grandes textos em lotes" |
| Integração com ontologia | "Use a ontologia P8 para guiar a extração" |
| Rastreabilidade | "Acompanhe o progresso da construção" |

## Workflow

### Construir Grafo (Assíncrono)

```
python scripts/graph_builder.py build --text "documento.txt" --ontology ontology.json
```

1. task_id criado → status PROCESSING
2. create_graph → graph_id
3. set_ontology → ontologia armazenada
4. Chunking (500 chars, 50 overlap)
5. Batches (3 chunks/batch) com callback
6. GraphInfo final → task COMPLETED

### Verificar Status

```
python scripts/graph_builder.py status --task <task_id>
```

### Obter Dados do Grafo

```
python scripts/graph_builder.py data --graph <graph_id>
```

## Exemplo de Uso (Python)

```python
from scripts.graph_builder import GraphBuilderService
from pathlib import Path

# Carregar ontologia
import json
ontology = json.loads(Path("ontology.json").read_text())

# Texto de entrada
text = Path("documento.txt").read_text()

# Construir
builder = GraphBuilderService(storage=my_storage)
task_id = builder.build_graph_async(
    text=text,
    ontology=ontology,
    graph_name="Meu Grafo",
    chunk_size=500,
    chunk_overlap=50,
    batch_size=3
)

# Acompanhar
task = builder.task_manager.get_task(task_id)
print(f"Status: {task.status}, Progresso: {task.progress}%")
```

## Escala de Confiança

- 🟢 **CONFIRMADO** — Dado extraído e persistido diretamente
- 🟡 **INFERIDO** — Ontologia guiou a extração (pode variar por chunk)
- 🔴 **LACUNA** — Chunk com falha (log de erro do batch)

## Regras

### MUST DO
- Executar em background thread (não bloquear o caller)
- Reportar progresso a cada batch via callback
- Usar TaskManager para rastreabilidade
- Tratar falhas por chunk (não abortar todo o batch)
- Logar cada chunk com tamanho, preview e tempo

### MUST NOT DO
- Processar texto sem ontologia (resultado será genérico)
- Ignorar falhas de chunk (registrar no log)
- Bloquear a thread principal com build síncrono
- Ultrapassar limites de memória com textos muito grandes
