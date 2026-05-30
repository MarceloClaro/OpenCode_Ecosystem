<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Inspirado pelo ReportAgent do MiroFish-Offline (report_agent.py).
-->

---
description: >
  Gera relatórios analíticos com cadeia ReACT + reflexão em 3 dimensões.
  Inspirado pelo ReportAgent do MiroFish-Offline. Suporta geração completa,
  planejamento de sumário e reflexão sobre relatórios existentes.
  Uso: /report-agent [--graph <id>] --requirement "<cenário>" [--output <file>]
  Modos: full (padrão), plan, reflect
  Exemplos:
    /report-agent --graph mirofish_abc --requirement "Impacto da regulação de IA"
    /report-agent plan --graph mirofish_abc --requirement "Cenário"
    /report-agent reflect --input report.md
pinned: false
---

# ReportAgent — ReACT + Reflection

Ativa o **Report Agent** para gerar relatórios analíticos com raciocínio
multi-turno e verificação de qualidade.

## Como funciona

```
/report-agent [modo] [opções]
```

### Modos

| Modo | Descrição | Uso |
|---|---|---|
| `full` (padrão) | Geração completa: planning → ReACT → reflection | `--graph <id> --requirement "<texto>"` |
| `plan` | Apenas planejar sumário | `--graph <id> --requirement "<texto>"` |
| `reflect` | Refletir sobre relatório existente | `--input report.md` |

### Opções

| Opção | Descrição | Padrão |
|---|---|---|
| `--graph <id>` | ID do grafo | mirofish_abc |
| `--requirement <texto>` | Cenário/contexto da simulação | — |
| `--output <file>` | Arquivo de saída | stdout |
| `--input <file>` | Arquivo de entrada (reflect) | — |
| `--mock` | Usar dados simulados | true |

### Fluxo

```
1. Planning
   Requisito + Grafo → LLM → Sumário (título + seções)

2. ReACT (por seção)
   Thought → Action (busca) → Observation → Repeat → Final Answer

3. Reflection
   Consistência (score) + Autocorreção (fixes) + Lacunas (gaps)
```
