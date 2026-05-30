# P14 — Agent Forum Protocol

## Visao Geral

O Agent Forum e um protocolo de debate multiagente onde agentes especializados
discutem um topico sob moderacao de um LLM. O protocolo generaliza o ForumEngine
do BettaFish (666ghj/BettaFish), substituindo dependencias especificas (loguru,
Qwen3) por uma arquitetura agnostica de canal, moderador e buffer.

---

## 1. Ciclo de Debate (4 Estagios)

```
  IDLE ──► OPEN ──► DISCUSS ──► SYNTHESIZE ──► CLOSED
                    ▲                │
                    └────────────────┘
                    (loop ate N rodadas)
```

| Estagio | Descricao | Acao do Moderador |
|---------|-----------|-------------------|
| `IDLE` | Sessao nao iniciada | — |
| `OPEN` | Abertura: agentes apresentam analise inicial | SUMMARIZE: sintese das posicoes iniciais |
| `DISCUSS` | Discussao ativa: N speeches por rodada | DEEPEN: aprofundar pontos, apontar divergencias |
| `SYNTHESIZE` | Moderador sintetiza rodada | CHALLENGE: apontar contradicoes e lacunas |
| `CONCLUDE` | Conclusao forcada por chamada explicita | CONCLUDE: relatorio final |
| `CLOSED` | Sessao encerrada | — |

---

## 2. Componentes

### 2.1 Forum

Orquestrador principal. Mantem:
- **Canal**: meio de comunicacao entre agentes
- **Monitor**: gerencia buffer de N speeches
- **Moderador**: LLM que analisa e sintetiza
- **Historico**: transcript completo da sessao

### 2.2 Channel

Canal abstrato. Implementacoes:
- **MemoryChannel**: em memoria (programatico, threadsafe)
- **FileChannel**: via arquivos .log no filesystem

Metodos:
- `publish(speech)` — publica discurso
- `poll()` — coleta novos discursos
- `get_transcript()` — historico completo
- `clear()` — limpa canal

### 2.3 ForumMonitor

Gerencia buffer de speeches. Aciona moderador quando buffer atinge
tamanho configurado (`buffer_size`, padrao 5).

### 2.4 ForumModerator

Wrapper do LLM. Gera discursos nos modos:
- **SUMMARIZE**: sintese das posicoes
- **CHALLENGE**: apontar contradicoes
- **DEEPEN**: aprofundar analise
- **CONCLUDE**: relatorio final

---

## 3. Formato dos Discursos

### AgentSpeech (Agente)

```json
{
  "source": "QueryEngine",
  "content": "Dados mostram...",
  "timestamp": "2026-05-17T10:30:00Z",
  "speech_id": "sp-a1b2c3d4",
  "stage": "discuss",
  "confidence": 0.85,
  "stance": "supportive",
  "metadata": {}
}
```

### ModeratorSpeech (Moderador)

```json
{
  "content": "## Sintese\n\n...",
  "mode": "summarize",
  "timestamp": "2026-05-17T10:31:00Z",
  "speech_id": "mod-e5f6g7h8",
  "sources": ["sp-a1b2c3d4", "sp-i9j0k1l2"]
}
```

---

## 4. Configuracao (SessionConfig)

| Parametro | Tipo | Padrao | Descricao |
|-----------|------|--------|-----------|
| `topic` | str | — | Topico do debate |
| `agents` | list[str] | — | Nomes dos agentes participantes |
| `moderator_model` | str | `opencode/deepseek-v4-pro` | Modelo LLM do moderador |
| `moderator_temperature` | float | 0.6 | Temperatura do LLM |
| `buffer_size` | int | 5 | Speeches por rodada antes do moderador |
| `max_rounds` | int | 10 | Maximo de rodadas de discussao |
| `timeout_seconds` | int | 7200 | Timeout total da sessao |
| `language` | str | `pt-BR` | Idioma das respostas |

---

## 5. API de Uso

```python
from moderator import create_forum, Forum

# Criar forum
forum = create_forum(
    agents=["QueryEngine", "MediaEngine"],
    language="pt-BR",
)

# Abrir sessao
forum.open_session("Impacto da regulamentacao de IA no Brasil")

# Agentes publicam
forum.publish("QueryEngine", "...", confidence=0.8)
forum.publish("MediaEngine", "...", confidence=0.6)

# Moderador e automaticamente acionado quando buffer atinge limite

# Concluir
forum.conclude()

# Relatorio
report = forum.get_json_report()
print(forum.transcript)
```

---

## 6. Integracao com Ecossistema Reversa

O Agent Forum pode ser usado como:

1. **Skill autonoma**: para debates multiagente sob demanda
2. **Componente de pipeline**: integrado a P5/P9 como etapa de revisao
3. **Modo supervisor**: agente moderador avaliando qualidade de respostas
4. **Ferramenta de decisao**: consolidacao de multiplas perspectivas

### Dependencias

| Dependencia | Tipo | Uso |
|-------------|------|-----|
| P3 (Machine States) | opcional | Estado do forum como maquina de estados |
| P5 (Pipeline Orchestrator) | opcional | Forum como etapa de pipeline |
| P11 (Process Lifecycle) | opcional | Gerenciamento do processo do moderador |

---

## 7. Seguranca e Boas Praticas

- **API keys**: nunca hardcoded — use `FORUM_MODERATOR_API_KEY` env var
- **Timeout**: sempre configurar `timeout_seconds` para evitar hangs
- **Buffer**: ajustar `buffer_size` conforme numero de agentes (recomendado: N_AGENTES + 2)
- **Rate limit**: em modo moderador LLM real, considerar retry com backoff
- **Thread safety**: todas as operacoes do canal sao thread-safe via Lock

---

## 8. Modo Offline

Se `FORUM_MODERATOR_API_KEY` nao estiver configurada, o moderador opera em
modo offline/demo, gerando sinteses template sem chamar LLM. Funcional para:
- Testes de integracao
- Demonstracoes
- Desenvolvimento sem dependencia externa
