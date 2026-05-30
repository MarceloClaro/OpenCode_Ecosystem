# Padrão de Construção Assíncrona

## Arquitetura

```
Caller                    GraphBuilderService          Worker Thread
  │                              │                          │
  │── build_graph_async() ──────►│                          │
  │                              │── create_task() ────────►│
  │◄──── task_id ────────────────│                          │
  │                              │                          ├─ create_graph()
  │                              │                          ├─ set_ontology()
  │── get_task(task_id) ────────►│                          ├─ split_text()
  │◄──── Task.progress ──────────│                          ├─ add_text_batches()
  │                              │                          └─ complete_task()
  │                              │
  │── get_graph_data(graph_id)──►│
  │◄──── GraphInfo ──────────────│
```

## Componentes

### TaskManager
- `create_task(type, metadata)` → task_id
- `update_task(id, status, progress, message)`
- `complete_task(id, result)`
- `fail_task(id, error)`
- `get_task(id)` → Task

### TextProcessor.split_text()
- `chunk_size`: 500 caracteres (padrão)
- `chunk_overlap`: 50 caracteres
- Quebra em espaços/pontos quando possível

### Callback de Progresso
```python
lambda msg, prog: task_manager.update_task(
    task_id, progress=20 + int(prog * 0.6), message=msg
)
```
