<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Inspirado pelo EntityReader do MiroFish-Offline (entity_reader.py).
-->

---
description: >
  Extrai e filtra entidades nomeadas de grafos de conhecimento.
  Modos: list (todas), filter (por tipo), context (UUID), stats.
  Uso: /entity-ner [list|filter|context|stats] [--type <tipo>] [--uuid <id>]
  Exemplos:
    /entity-ner list
    /entity-ner filter --type Person
    /entity-ner context --uuid ent-001
    /entity-ner stats
pinned: false
---

# Entity NER Reader

Ativa o **Entity NER Reader** para extrair entidades nomeadas de grafos.

```
/entity-ner <modo> [opções]
```

| Modo | Descrição | Opções |
|------|-----------|--------|
| `list` | Todas as entidades com tipos | `--graph` |
| `filter` | Filtrar por tipo | `--type` (obrigatório) |
| `context` | Entidade com contexto completo | `--uuid` (obrigatório) |
| `stats` | Estatísticas do grafo | `--graph` |

### Exemplos

```
/entity-ner list
→ Mostra 7 entidades: Student, Professor, Journalist, University...

/entity-ner filter --type Person
→ 3 entidades: Carlos Silva, Ana Oliveira, João Pereira

/entity-ner context --uuid ent-001
→ Carlos Silva: STUDIES_AT → Universidade Federal

/entity-ner stats
→ 7 nós, 4 tipos, 5 arestas
```

