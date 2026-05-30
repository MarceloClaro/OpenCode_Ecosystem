---
name: anp
description: "Executa o pipeline ANP (Agent Node Pipeline) para processar consultas através de nós tipados em pipeline."
aliases:
  - "/anp"
  - "/pipeline"
  - "anp"
usage: "/anp [consulta] ou /pipeline [consulta]"
metadata:
  author: Reversa Engine
  version: "1.0.0"
  pattern-id: P16
  domain: agent-framework
  agent: reversa-anp
---

# Comando: /anp

Executa o **Agent Node Pipeline (ANP)** — um pipeline de nós tipados que
processa consultas através de 4 fases: Planejamento → Pesquisa → Refinamento → Entrega.

## Uso

```
/anp <consulta>
/pipeline <consulta>
```

## Exemplos

```
/anp Quais as tendências de IA para 2026?
/pipeline Analisar o mercado de agentes autônomos
```

## Fluxo

1. StructureNode planeja seções do relatório
2. SearchNode busca dados externos
3. SummaryNode sumariza resultados
4. ReflectNode identifica lacunas (loop de reflexão)
5. FormatNode produz saída final

## Dependências

- Python scripts em `skills/agent-node-pipeline/scripts/`
- `LLMClient` configurado (OPENAI_API_KEY ou fallback offline)
