<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Inspirado pelo OntologyGenerator do MiroFish-Offline (ontology_generator.py).
-->

---
description: >
  Gera ontologias (tipos de entidades e relacionamentos) para grafos
  de conhecimento a partir de textos. Modos: generate, validate, schema.
  Uso: /ontology-gen [generate|validate|schema] [--text <file>] [--requirement "<req>"]
  Exemplos:
    /ontology-gen generate --text documento.txt --requirement "Simular regulação de IA"
    /ontology-gen validate --input ontology.json
    /ontology-gen schema --input ontology.json
pinned: false
---

# Ontology Generator

Ativa o **Ontology Generator** para criar definições de tipos.

```
/ontology-gen <modo> [opções]
```

| Modo | Descrição | Opções |
|------|-----------|--------|
| `generate` | Gerar ontologia | `--text`, `--requirement`, `--output` |
| `validate` | Validar ontologia | `--input` |
| `schema` | Gerar SQL | `--input`, `--output` |

### Exemplos

```
/ontology-gen generate --text artigo.txt --requirement "Academia"
→ 10 entity types + 7 edge types (domínio: academic)

/ontology-gen generate --text lei.txt --requirement "Regulação de IA"
→ 10 entity types + 7 edge types (domínio: regulation)

/ontology-gen validate --input ontology.json
→ ✅ Ontologia válida

/ontology-gen schema --input ontology.json
→ Schema SQL gerado
```
