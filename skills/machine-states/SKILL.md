---
name: machine-states
description: >
  Máquina de estados formal para o pipeline de engenharia reversa.
  Inspirada pelo SimulationStatus e Project do MiroFish, fornece
  transições explícitas, validação de estados e persistência automática.
  Use quando o pipeline Reversa precisar de rastreabilidade formal dos
  estágios de análise, checkpointing e garantia de sequência correta.
license: MIT
compatibility: opencode
allowed-tools: Read, Write, Bash, Sqlite
metadata:
  author: Reversa Engine (padrão MiroFish)
  version: "2.0.0"
  domain: architecture
  triggers: state machine, pipeline, state, checkpoint, stage, status, transition, workflow, lifecycle, phase
  role: orchestration
  scope: pipeline
  output-format: json
  related-skills: plan-generator, agent-smith
  inspired-by: MiroFish SimulationStatus (Projeto Python typing), simulation_manager.py, simulation_runner.py
---

# Machine States — Pipeline com Estados Explícitos

Inspirado pelo `SimulationStatus` (IntEnum) e `Project` (Pydantic dataclass)
do MiroFish, que usam estados tipados e validação automática para garantir
a integridade do pipeline de simulação.

## Máquina de Estados do Pipeline Reversa

```
                         ┌──────────────┐
                         │   CREATED    │
                         └──────┬───────┘
                                │
                         ┌──────▼───────┐
                         │   PENDING    │
                         └──────┬───────┘
                                │
                         ┌──────▼───────┐
                    ┌────┤  PREPARING   │
                    │    └──────┬───────┘
                    │           │
                    │    ┌──────▼───────┐
                    │    │   STARTING   │
                    │    └──────┬───────┘
                    │           │
              ┌─────┴─────┐   ┌─▼──────────┐  ┌──────────┐
              │  PAUSED   │◄──┤  RUNNING   ├──► STOPPING │
              └─────┬─────┘   └──┬───┬─────┘  └────┬─────┘
                    │            │   │              │
                    │       ┌────▼───▼┐       ┌────▼─────┐
                    │       │COMPLETED│       │  STOPPED │
                    │       └────┬────┘       └──────────┘
                    │            │
                    │      ┌─────▼──────┐
                    │      │  VALIDATED │
                    │      └─────┬──────┘
              ┌─────┴─────┐    │          ┌──────────────┐
              │  FAILED   │◄───┴──────────┤  ROLLED_BACK │
              └─────┬─────┘               └──────────────┘
                    │
              ┌─────▼─────┐
              │  SKIPPED  │
              └───────────┘
```

## Estados (Enum)

```python
class PipelineState(IntEnum):
    CREATED     = 0   # Entidade criada, não preparada
    PENDING     = 1   # Pipeline criado, não iniciado
    PREPARING   = 2   # Em preparação (entidades → perfis → config)
    STARTING    = 3   # Processo sendo iniciado
    RUNNING     = 4   # Processamento em andamento
    PAUSED      = 5   # Temporariamente suspenso
    STOPPING    = 6   # Parada graceful em andamento
    COMPLETED   = 7   # Fase concluída com sucesso
    STOPPED     = 8   # Parado após STOPPING
    VALIDATED   = 9   # Validado por agente de revisão
    FAILED      = 10  # Falha no processamento
    ROLLED_BACK = 11  # Revertido para estado anterior
    SKIPPED     = 12  # Pulado (não aplicável)
    BLOCKED     = 13  # Bloqueado por dependência não resolvida
```

## Transições Válidas

| Estado Atual | Próximo Estado | Gatilho |
|---|---|---|
| `CREATED` | `PENDING` | `prepare()` |
| `PENDING` | `PREPARING` | `start_preparation()` |
| `PREPARING` | `COMPLETED` | `finish_preparation()` |
| `PREPARING` | `FAILED` | `fail(error)` |
| `PREPARING` | `STARTING` | `start_process()` |
| `STARTING` | `RUNNING` | `process_ready()` |
| `STARTING` | `FAILED` | `fail(error)` (init failed) |
| `RUNNING` | `PAUSED` | `pause()` |
| `RUNNING` | `STOPPING` | `stop()` |
| `RUNNING` | `COMPLETED` | `complete()` |
| `RUNNING` | `FAILED` | `fail(error)` |
| `PAUSED` | `RUNNING` | `resume()` |
| `PAUSED` | `STOPPING` | `stop()` |
| `STOPPING` | `STOPPED` | `stopped()` |
| `STOPPING` | `FAILED` | `fail(error)` (stop failed) |
| `COMPLETED` | `VALIDATED` | `validate()` |
| `COMPLETED` | `FAILED` | `fail(error)` (validation failed) |
| `FAILED` | `RUNNING` | `retry()` |
| `FAILED` | `ROLLED_BACK` | `rollback()` |
| `VALIDATED` | `RUNNING` | `revise()` (revision needed) |
| `RUNNING` | `BLOCKED` | `block(dependency)` |
| `BLOCKED` | `RUNNING` | `unblock()` |
| Qualquer | `SKIPPED` | `skip(reason)` |

## Comparação com MiroFish-Offline

| Estado P3 | Origem | Descrição no MiroFish |
|---|---|---|
| CREATED | SimulationStatus | Project created, preparation pending |
| PREPARING | SimulationManager | Entity reading → profile gen → config gen |
| STARTING | RunnerStatus | Subprocess being initialized |
| PAUSED | RunnerStatus | Simulation temporarily suspended |
| STOPPING | RunnerStatus | Graceful shutdown in progress |
| STOPPED | RunnerStatus | Process terminated cleanly |

## Persistência

Cada transição de estado é registrada no SQLite `.reversa/pipeline.db`:

```sql
CREATE TABLE pipeline_states (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    phase       TEXT NOT NULL,           -- fase do pipeline
    state       TEXT NOT NULL,           -- estado atual
    previous    TEXT,                     -- estado anterior
    started_at  TEXT NOT NULL,           -- ISO timestamp
    ended_at    TEXT,                     -- ISO timestamp
    duration_ms INTEGER,                 -- duração em ms
    error       TEXT,                     -- mensagem de erro (se failed)
    metadata    TEXT,                     -- JSON com contexto adicional
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## Uso no Pipeline Reversa

### Exemplo: Fase Scout

```json
{
  "phase": "scout",
  "state": "RUNNING",
  "previous": "PENDING",
  "started_at": "2026-05-17T00:00:00Z",
  "duration_ms": null,
  "error": null,
  "metadata": {
    "target": "src/",
    "files_found": 42
  }
}
```

### Exemplo: Fase Architect (falha)

```json
{
  "phase": "architect",
  "state": "FAILED",
  "previous": "RUNNING",
  "started_at": "2026-05-17T00:05:00Z",
  "ended_at": "2026-05-17T00:05:30Z",
  "duration_ms": 30000,
  "error": "Dependency not found: module 'auth' has no entry points",
  "metadata": {
    "module": "auth",
    "error_detail": "No routes defined"
  }
}
```

## Comandos

| Comando | Descrição |
|---|---|
| `/state status` | Mostra estado atual do pipeline |
| `/state log` | Histórico de transições |
| `/state advance <phase> [state]` | Avança manualmente um estado |
| `/state retry` | Tenta novamente fase com falha |
| `/state reset` | Reseta pipeline (requer confirmação) |

## Regras

### MUST DO
- Registrar TODAS as transições de estado no SQLite
- Validar transições antes de aplicá-las
- Salvar metadata relevante em cada transição
- Usar timestamps ISO 8601 com timezone

### MUST NOT DO
- Pular estados no fluxo normal (exceção: SKIPPED explícito)
- Modificar registros de estado anteriores
- Ignorar estados BLOCKED (resolver dependência antes)
- Resetar pipeline sem confirmação explícita
