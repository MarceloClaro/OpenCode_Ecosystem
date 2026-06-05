<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Inspirado pelo OASIS Profile Generator do MiroFish-Offline
  (oasis_profile_generator.py + simulation_config_generator.py).
-->

---
description: >
  Gera perfis de agente IA (personas OASIS) a partir de entidades de grafos
  de conhecimento. Inspirado pelo OASIS Profile Generator do MiroFish-Offline.
  Suporta geração a partir do GraphRAG, arquivos JSON, ou entradas diretas.
  Uso: /oasis-profile [--graph <id>] [--input <file>] [--output <file>] [--parallel <n>] [--template <name>] [--validate <file>] [--config <file>]
  Exemplos:
    /oasis-profile --graph mirofish_abc --entity-types Person --parallel 5
    /oasis-profile --input entities.json --output profiles.json
    /oasis-profile --validate profiles.json
    /oasis-profile --config profiles.json --requirement "Debate sobre IA"
pinned: true
---

# OASIS Profile Generator — Personas de Agente para Simulação

Ativa o **OASIS Profile Agent** para converter entidades de grafos em
personas detalhadas de agente (bio, persona, interesses, MBTI, tópicos,
estilo de fala, comportamentos por plataforma).

## Como funciona

```
/oasis-profile [opções]
```

### Opções

| Opção | Descrição | Padrão |
|-------|-----------|--------|
| `--graph <id>` | ID do grafo no GraphRAG | — |
| `--entity-types "A,B"` | Tipos de entidade para filtrar | "Person" |
| `--input <file>` | Arquivo JSON de entrada | — |
| `--output <file>` | Arquivo de saída | profiles.json |
| `--parallel <n>` | Geração em paralelo | 3 |
| `--template <name>` | Template de prompt | default |
| `--validate <file>` | Validar schema dos perfis | — |
| `--config <file>` | Gerar config de simulação | — |
| `--requirement <text>` | Requisito para config | — |

### Fluxo

```
Entidades (grafo/JSON)
  → Template + LLM → Perfis individuais
  → Validação de schema
  → Exportação (JSON/CSV)
  → [Opcional] Config de simulação via LLM
```
