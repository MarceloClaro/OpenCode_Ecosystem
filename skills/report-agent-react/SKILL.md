---
name: report-agent-react
description: >
  Agente de relatório com cadeia ReACT (Reasoning + Acting) e reflexão
  em 3 dimensões. Inspirado pelo ReportAgent do MiroFish-Offline
  (report_agent.py). Gera relatórios estruturados seção por seção,
  cada seção passando por ciclo multi-turno de pensamento-ferramenta-
  observação-reflexão. Suporta planejamento de sumário, geração de
  seções com ReACT, e reflexão pós-geração.
  Use quando precisar gerar relatórios analíticos profundos baseados
  em dados de grafo com garantia de qualidade multi-turno.
license: MIT
compatibility: opencode
allowed-tools: Read, Grep, Glob, Bash, Write
metadata:
  author: Reversa Engine (padrão MiroFish-Offline ReportAgent)
  version: "1.0.0"
  domain: report-generation
  triggers: relatório, report, react, reflexão, reflection, agente de relatório
  role: writer
  scope: reporting
  output-format: markdown
  related-skills: code-graphrag, hybrid-graph-retrieval, oasis-profile-gen
  inspired-by: MiroFish-Offline report_agent.py (ReACT + Reflection)
---

# ReportAgent — ReACT + Reflection

Inspirado pelo **ReportAgent** do MiroFish-Offline — um sistema de
geração de relatórios preditivos que combina o padrão ReACT (Reasoning +
Acting) com um ciclo de reflexão em 3 dimensões.

## Arquitetura (Padrão ReACT + Reflection)

```
MiroFish-Offline:
  Planning Phase → Section Generation (ReACT loop) → Reflection → Final Report
       ↓                    ↓                              ↓
  GraphTools          insight_forge                    Consistency check
  Simulation Context  panorama_search                  Self-correction
                      quick_search                     Gap analysis
                      interview_agents

OpenCode:
  Query + Context → Outline Planning → ReACT Loop per Section → 3D Reflection → Markdown Report
       ↓                    ↓                              ↓
  hybrid_search.py     hybrid_search.py                  consistency.py
  (insight/panorama)   (multi-turn)                      self_correction + gaps
```

## Ciclo ReACT (por seção)

Cada seção do relatório passa pelo seguinte ciclo:

```
                     ┌──────────────────┐
                     │   Thought (T)    │ ← O que preciso saber?
                     └────────┬─────────┘
                              │
                     ┌────────▼─────────┐
                     │   Action (A)     │ ← Chamar ferramenta de busca
                     └────────┬─────────┘
                              │
                     ┌────────▼─────────┐
                     │  Observation (O) │ ← Analisar resultado
                     └────────┬─────────┘
                              │
                     ┌────────▼─────────┐
                     │  Repeat T→A→O   │ ← Até info suficiente
                     └────────┬─────────┘
                              │
                     ┌────────▼─────────┐
                     │  Final Answer (F)│ ← Escrever seção
                     └────────┬─────────┘
                              │
                     ┌────────▼─────────┐
                     │  Reflection (R)  │ ← 3 dimensões
                     └──────────────────┘
```

### 3 Dimensões de Reflexão

1. **Consistência** — O conteúdo é coerente com os dados obtidos?
   - Verifica contradições entre fatos
   - Verifica alinhamento com o contexto da simulação

2. **Autocorreção** — Há erros que precisam ser corrigidos?
   - Detecta alucinações (informação não presente nos dados)
   - Corrige imprecisões factuais

3. **Lacunas** — Faltam informações importantes?
   - Identifica perguntas não respondidas
   - Sugere buscas adicionais se necessário

## Pipeline Completo

### Fase 1: Planejamento (Planning)

```
[Requisito de Simulação + Contexto do Grafo]
  → LLM analisa cenário e estatísticas
  → Gera sumário com título, resumo e seções
  → Valida número de seções (2-5)
```

### Fase 2: Geração por Seção (ReACT Loop)

Para cada seção do sumário:

1. **Thought**: "O que preciso saber para escrever esta seção?"
2. **Action**: Chamar ferramenta (insight_forge, panorama_search, quick_search)
3. **Observation**: Analisar resultado da ferramenta
4. **Repeat**: Se informação insuficiente, volta ao passo 1
5. **Final**: Quando suficiente, gera o conteúdo da seção

### Fase 3: Reflexão (Reflection)

Após todas as seções:

1. Verificar consistência geral do relatório
2. Identificar e corrigir inconsistências
3. Apontar lacunas de informação

## Estruturas de Dados

### ReportSection
```python
{
    "title": str,       # Título da seção
    "content": str,     # Conteúdo em markdown
    "tool_calls": int,  # Qtd de chamadas de ferramenta
    "status": str       # pending | generating | completed
}
```

### ReportOutline
```python
{
    "title": str,                    # Título do relatório
    "summary": str,                  # Resumo de uma linha
    "sections": List[ReportSection]  # Lista de seções
}
```

### ReflectionResult
```python
{
    "consistency": {"score": float, "issues": List[str]},
    "self_correction": {"corrections": List[Dict]},
    "gaps": {"unanswered": List[str], "suggestions": List[str]}
}
```

## Exemplos de Uso

```bash
# Gerar relatório completo
python scripts/report_agent.py --graph mirofish_abc --requirement "Simular impacto de nova regulação de IA"

# Apenas planejar sumário
python scripts/report_agent.py plan --graph mirofish_abc --requirement "..."

# Apenas refletir sobre relatório existente
python scripts/report_agent.py reflect --input report.md
```

## Referências

- Código original: `report_agent.py` (MiroFish-Offline) — 1800+ linhas
- SKILL relacionada: `hybrid-graph-retrieval` (ferramentas de busca)
- SKILL relacionada: `code-graphrag` (fonte de dados do grafo)
- SKILL relacionada: `oasis-profile-gen` (perfis de agente para entrevistas)
