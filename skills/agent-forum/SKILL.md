---
name: agent-forum
description: "Skill do ecossistema OpenCode - agent-forum"
---

# P14 — Agent Forum / Debate Moderator

## Visão Geral

Sistema de debate multiagente com moderador LLM. Permite que múltiplos agentes colaborem através de um fórum estruturado: agentes publicam análises, um moderador sintetiza e guia a discussão, e o ciclo se repete até convergência.

Extraído do `ForumEngine` do BettaFish (666ghj), generalizado para qualquer ecossistema multiagente.

## Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    ForumProtocol                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ Agent A  │  │ Agent B  │  │ Agent C  │               │
│  │ (source) │  │ (source) │  │ (source) │               │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘               │
│       │             │             │                       │
│       └──────┬──────┴──────┬──────┘                       │
│              │             │                              │
│              ▼             ▼                              │
│  ┌─────────────────────────────────────┐                  │
│  │         ForumMonitor                 │                  │
│  │  · Watches agent output channels     │                  │
│  │  · Buffers N speeches                │                  │
│  │  · Thread-safe aggregation           │                  │
│  └────────────────┬────────────────────┘                  │
│                   │                                       │
│                   ▼                                       │
│  ┌─────────────────────────────────────┐                  │
│  │       ForumModerator (LLM)           │                  │
│  │  · Sintetiza discussoes             │                  │
│  │  · Gera perguntas de profundidade   │                  │
│  │  · Identifica consenso/divergencia  │                  │
│  └────────────────┬────────────────────┘                  │
│                   │                                       │
│                   ▼                                       │
│  ┌─────────────────────────────────────┐                  │
│  │         Output (forum.log/IR)        │                  │
│  │  · Historico completo da discussao  │                  │
│  │  · Resumo final com decisoes        │                  │
│  └─────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────┘
```

## Ciclo de Debate

Cada rodada do fórum segue 4 estágios:

| Estágio | Descrição | Gatilho |
|---------|-----------|---------|
| **OPEN** | Agentes publicam análise inicial | Moderador declara tópico |
| **DISCUSS** | Agentes respondem, refinam, debatem | Buffer atinge N speeches |
| **SYNTHESIZE** | Moderador integra perspectivas | N speeches + intervalo |
| **CONCLUDE** | Relatório final consolidado | Moderador declara convergência |

## Componentes

### ForumModerator
- LLM com system prompt especializado
- 4 modos de operação: `summarize`, `challenge`, `deepen`, `conclude`
- Rastreia histórico para evitar duplicação (via `previous_summaries`)

### ForumMonitor
- Thread-safe, baseado em polling de arquivos ou IPC
- Buffer configurável (default: 5 speeches antes do moderador)
- Filtragem de erros (bloqueia ERROR blocks até próximo INFO)
- Extração de JSON multiline de logs estruturados

### Speech Schema
```python
@dataclass
class AgentSpeech:
    source: str          # agent identifier
    timestamp: str       # ISO format
    content: str         # speech body
    metadata: dict       # confidence, stance, round, stage
```

## Protocolo de Fórum

```
[HH:MM:SS] [AGENT_A] <structured content>
[HH:MM:SS] [AGENT_B] <structured content>
[HH:MM:SS] [MODERATOR] <synthesis + guidance>
```

### Regras
1. **Buffer de N speeches**: Moderador só age após N agentes falarem
2. **Bloqueio de erros**: Se um agente produz ERROR, seu bloco é ignorado até o próximo INFO
3. **Timeout**: Se não houver atividade por período configurável, fórum conclui automaticamente
4. **Thread safety**: Escrita no log usa lock mutex

## Uso

```python
from forum import Forum

forum = Forum(
    agents=["QueryEngine", "MediaEngine", "InsightEngine"],
    moderator_llm={"model": "gpt-4", "temperature": 0.6},
    buffer_size=5,
    channel="filesystem"  # ou "ipc", "memory"
)

# Iniciar debate sobre um tópico
forum.open_session(topic="Analisar impacto da política X")

# Agentes publicam (via API ou arquivo)
forum.publish("QueryEngine", "Os dados mostram tendência de alta...")

# Moderador é automaticamente invocado após N speeches
# Resultado final
report = forum.get_transcript()
```

## Integração com P10 e P11

- P11 (Process Lifecycle): `forum.start()` / `forum.stop()` via ProcessRunner
- P10 (Graph Memory Updater): Registrar sessões de debate como nós no grafo
- P12 (Filesystem IPC): Usar como canal de comunicação dos agentes

## Escala de Confiança

- 🟢 **CONFIRMADO** — Extraído diretamente do código BettaFish (monitor.py, llm_host.py)
- 🟡 **INFERIDO** — Generalização do protocolo para ecossistema Reversa
- 🔴 **LACUNA** — Integração com P10/P11 não testada em runtime

