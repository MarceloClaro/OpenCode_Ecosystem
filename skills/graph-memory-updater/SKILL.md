---
name: graph-memory-updater
description: >
  Atualização em tempo real de grafos com atividades de agentes em simulação.
  Inspirado pelo GraphMemoryUpdater do MiroFish-Offline, monitora logs de
  ações de agentes (postar, curtir, comentar, seguir) e envia para o grafo
  em lotes com buffer por plataforma. Use quando precisar registrar atividades
  de simulação em um grafo de conhecimento em tempo real.
license: MIT
compatibility: opencode
allowed-tools: Read, Grep, Glob, Bash, Write, Sqlite
metadata:
  author: Reversa Engine (padrão MiroFish-Offline graph_memory_updater.py)
  version: "2.0.0"
  domain: pipeline
  triggers: memory, memória, update, atualizar, activity, atividade, agente, simulação, lifecycle, integração
  role: pipeline
  scope: realtime
  output-format: json
  related-skills: graph-builder-pipeline, entity-ner-reader, code-graphrag, machine-states, process-lifecycle, fs-ipc
  inspired-by: MiroFish-Offline GraphMemoryUpdater (graph_memory_updater.py)
---

# Graph Memory Updater — Atualização de Grafos em Tempo Real

Inspirado pelo **GraphMemoryUpdater** do MiroFish-Offline (`graph_memory_updater.py`).
Serviço que monitora ações de agentes em simulações sociais e as converte
em atualizações de grafo em tempo real, com buffer por plataforma e
processamento em lote.

## Arquitetura

```
Simulação → AgentActivity → Queue
  → Buffer por Plataforma (twitter/reddit)
    → Batch (5 atividades) → to_episode_text() → add_text() → Grafo
      → NER extrai entidades + relações da descrição textual
```

## Componentes

### AgentActivity
Dataclass representando uma ação de agente:
- `platform`: twitter / reddit
- `agent_id`, `agent_name`
- `action_type`: CREATE_POST, LIKE_POST, REPOST, FOLLOW, etc.
- `action_args` + `round_num` + `timestamp`

### to_episode_text()
Converte cada atividade em texto narrativo natural:
```
"Carlos: Posted a post: "A regulação de IA é necessária""
"Maria: Liked Carlos's post: "A regulação de IA é necessária""
"João: Followed user "Carlos""
```

### GraphMemoryUpdater
Serviço principal:
- Fila interna (`Queue`) + buffers por plataforma
- Worker thread com batch size configurável (padrão: 5)
- Retry com backoff (3 tentativas)
- Métricas: total_activities, batches_sent, failed_count, skipped_count
- Ações DO_NOTHING são automaticamente ignoradas

### GraphMemoryManager
Gerenciador de múltiplos updaters (um por simulação):
- `create_updater(simulation_id, graph_id, storage)`
- `stop_updater(simulation_id)`
- `stop_all()` — cleanup global
- `get_all_stats()` — métricas de todas as simulações

## Integração com Process Lifecycle (P11)

O GraphMemoryUpdater pode ser integrado diretamente com o `ProcessRunner` (P11)
para monitorar ações de agentes diretamente dos logs do processo.

### Ciclo de Vida Coordenado

```
ProcessRunner.start() 
  → init_subprocess() 
  → GraphMemoryManager.create_updater(sim_id, graph_id, storage)
  → updater.start_worker()

ProcessRunner._monitor()
  → A cada iteração: ler actions.jsonl
  → Para cada ação: updater.add_activity(activity)
  → Em simulation_end: platform_completed = True
  → Se ambas plataformas completas: updater.stop()

ProcessRunner.stop()
  → updater.stop()  # Flush + parada graceful
  → updater.cleanup()
```

### Método integrate_with_runner()

```python
@classmethod
def integrate_with_runner(cls, process_id: str, graph_id: str, storage):
    """
    Integra memory updater com processo gerenciado pelo ProcessRunner (P11).
    
    Args:
        process_id: ID do processo (mesmo usado no ProcessRunner)
        graph_id: ID do grafo de destino
        storage: Instância de GraphStorage
    
    Returns:
        simulation_id (str): ID para referência
    """
    # 1. Cria updater para o processo
    # 2. Registra callback no ProcessRunner para cada ação detectada
    # 3. Liga STOP do updater ao STOP do processo
    # 4. Retorna simulation_id
```

### Ciclo de Vida Agora:

| Fase | P10 (GraphMemoryUpdater) | P11 (ProcessRunner) |
|---|---|---|
| INIT | create_updater(sim_id, graph_id) | ProcessRunner.start(id, cmd) |
| WORKER START | worker thread inicia | monitor thread inicia |
| PROCESSAMENTO | add_activity() → buffer → batch → graph | parse log → detect actions |
| PLATFORM END | platform_completed | detecta simulation_end |
| ALL COMPLETE | stop_updater() | COMPLETED status |
| FORCE STOP | stop_updater() | STOP sequence |
| CLEANUP | stop_all() | cleanup_all() |

## Métricas Agregadas (P10 + P11)

Quando integrado com P11, as seguintes métricas estão disponíveis:

| Métrica | Fonte | Descrição |
|---|---|---|
| total_activities | P10 | Atividades enfileiradas |
| batches_sent | P10 | Lotes enviados ao grafo |
| failed_count | P10 | Atividades com falha |
| skipped_count | P10 | Ações DO_NOTHING ignoradas |
| current_round | P11 | Rodada atual da simulação |
| total_rounds | P11 | Total de rodadas |
| progress_percent | P11 | Progresso geral |
| twitter_actions_count | P11 | Ações no Twitter |
| reddit_actions_count | P11 | Ações no Reddit |
| runner_status | P11 | Estado do processo |

## Ações Suportadas

| Ação | Descrição | Template |
|------|-----------|----------|
| `CREATE_POST` | Publicar post | "Posted: {content}" |
| `LIKE_POST` | Curtir post | "Liked {author}'s post: {content}" |
| `DISLIKE_POST` | Rejeitar post | "Disliked {author}'s post: {content}" |
| `REPOST` | Repostar | "Reposted {author}'s post: {content}" |
| `QUOTE_POST` | Citar com comentário | "Quoted {author}'s post, commented: {comment}" |
| `FOLLOW` | Seguir usuário | "Followed user {name}" |
| `CREATE_COMMENT` | Comentar | "Commented on {author}'s post: {content}" |
| `LIKE_COMMENT` | Curtir comentário | "Liked {author}'s comment: {content}" |
| `SEARCH_POSTS` | Buscar posts | "Searched for {query}" |
| `SEARCH_USER` | Buscar usuário | "Searched for user {name}" |
| `MUTE` | Silenciar | "Muted user {name}" |
| `DO_NOTHING` | Ignorado | — |

## Quando Usar

| Cenário | Descrição |
|---------|-----------|
| Simulação ao vivo | "Registre as ações dos agentes em tempo real no grafo" |
| Log de atividades | "Converta logs de simulação em entidades do grafo" |
| Múltiplas plataformas | "Buffer por plataforma com processamento em lote" |
| Rastreabilidade | "Mantenha histórico de ações dos agentes" |
| Análise pós-simulação | "Consulte o grafo para entender interações" |

## Workflow

### Iniciar Monitoramento

```
python scripts/memory_updater.py start --graph <graph_id>
```

1. Cria GraphMemoryUpdater com buffer vazio
2. Inicia worker thread em background
3. Aceita atividades via add_activity()

### Adicionar Atividade

```python
activity = AgentActivity(
    platform="twitter",
    agent_id=1,
    agent_name="Carlos",
    action_type="CREATE_POST",
    action_args={"content": "A regulação de IA é necessária"},
    round_num=5,
    timestamp="2026-05-17T12:00:00Z"
)
updater.add_activity(activity)
```

### Parar e Flush

```
python scripts/memory_updater.py stop --simulation <sim_id>
```

- Envia atividades restantes na queue e buffers
- Para a worker thread
- Loga estatísticas finais

### Integrar com P11 (Process Lifecycle)

```
python scripts/memory_updater.py integrate --process <process_id> --graph <graph_id>
```

1. Cria GraphMemoryUpdater
2. Registra no ProcessRunner como callback de ações
3. Liga stop_updater() ao stop do processo
4. Retorna simulation_id para consulta

### Consultar Métricas Agregadas

```
python scripts/memory_updater.py stats --simulation <sim_id>
```

1. Coleta métricas do P10 (total_activities, batches_sent, etc.)
2. Coleta métricas do P11 (current_round, progress, etc.)
3. Retorna relatório combinado

## Escala de Confiança

- 🟢 **CONFIRMADO** — Atividade registrada e enviada ao grafo com sucesso
- 🟡 **INFERIDO** — Descrição textual da ação (pode perder nuances)
- 🔴 **LACUNA** — Atividade que falhou após todas as retentativas

## Regras

### MUST DO
- Usar buffer por plataforma (twitter/reddit independentes)
- Batch size mínimo de 5 atividades antes de enviar
- Retry com backoff exponencial (até 3 tentativas)
- Ignorar DO_NOTHING (não poluir o grafo)
- Fornecer métricas detalhadas (enviados, falhas, ignorados)

### MUST NOT DO
- Enviar atividades uma a uma (ineficiente para o grafo)
- Bloquear a simulação enquanto envia (thread separada)
- Perder atividades ao parar (flush obrigatório)
- Ignorar falhas de rede sem retry
- Permitir que updaters órfãos consumam memória
