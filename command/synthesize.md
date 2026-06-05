<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Inspirado pelo ReportAgent ReACT do MiroFish (99KB).
-->

---
description: >
  Ativa o Synthesis Agent — meta-agente que consolida outputs de múltiplos
  agentes em documentação coesa e rastreável. Inspirado pelo ReportAgent
  ReACT do MiroFish. Coleta, cruza referências, identifica lacunas e gera
  artefatos consolidados.
  Uso: /synthesize [--target=...] [--output=...]
  Exemplos:
    /synthesize                          — consolida todos outputs disponíveis
    /synthesize --target=swarm           — sintetiza apenas o último Swarm Review
    /synthesize --target=reversa         — sintetiza a análise Reversa atual
    /synthesize --output=exec-summary    — gera apenas sumário executivo
---

# Synthesize — Consolidar Achados de Agentes

Ativa o **Synthesis Agent**, meta-agente que aplica o padrão ReACT
(Reasoning + Acting) do MiroFish para consolidar outputs de múltiplos
agentes.

## Como funciona

```
/synthesize [--target=...] [--output=...]
```

### Alvos (--target)

| Alvo | O que consolida |
|------|----------------|
| (vazio) | Todos outputs disponíveis em `_reversa_sdd/` |
| `swarm` | Apenas o último Swarm Review |
| `reversa` | Apenas outputs da pipeline Reversa |
| `audit` | Todos outputs de segurança + performance |

### Outputs (--output)

| Output | Gera |
|--------|------|
| (vazio) | Relatório completo + gap analysis + confidence matrix |
| `exec-summary` | Apenas sumário executivo |
| `gap-analysis` | Apenas lacunas identificadas |
| `confidence` | Apenas matriz de confiança |

## Pipeline

```
/synthesize
  1. PLAN    → estrutura baseada nos inputs disponíveis
  2. SEARCH  → cruza referências entre agentes
  3. GENERATE→ seção por seção
  4. REFLECT → auto-revisão com regeneração se necessário
  5. COMPILE → artefatos em _reversa_sdd/synthesis/
```

## Exemplo

```
$ /synthesize --target=swarm

📥 Coletando inputs: swarm-review-report.md
📋 PLAN: 5 seções identificadas
🔍 SEARCH: 12 referências cruzadas
✍️ GENERATE: gerando seções...
🔄 REFLECT: 1 seção regenerada (consistência)
📦 COMPILE: 3 artefatos gerados

📊 Métricas: 28 afirmações (🟢 18 | 🟡 7 | 🔴 3)
📄 _reversa_sdd/synthesis/
```
