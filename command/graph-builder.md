<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Inspirado pelo GraphBuilderService do MiroFish-Offline (graph_builder.py).
-->

---
description: >
  Constrói grafos de conhecimento a partir de texto + ontologia.
  Pipeline assíncrono com chunking, NER e persistência SQLite.
  Modos: build, status, data, delete.
  Uso: /graph-builder [build|status|data|delete] [--text <file>] [--ontology <json>]
  Exemplos:
    /graph-builder build --text doc.txt --ontology ontology.json
    /graph-builder status
    /graph-builder data --graph graph_20260517_123456_abc123
pinned: false
---

# Graph Builder Pipeline

Ativa o **Graph Builder Pipeline** para construir grafos.

```
/graph-builder <modo> [opções]
```

| Modo | Descrição | Opções |
|------|-----------|--------|
| `build` | Construir grafo | `--text`, `--ontology`, `--name` |
| `status` | Listar grafos | — |
| `data` | Dados de um grafo | `--graph` |
| `delete` | Deletar grafo | `--graph` |

### Exemplo de Build

```
/graph-builder build --text doc.txt --ontology ontology.json --name "Meu Grafo"
→ 🚀 Construção iniciada...
→ ✅ Grafo construído: graph_xxx
   Nós: 42 | Arestas: 21
```
