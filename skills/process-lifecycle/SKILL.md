---
name: process-lifecycle
description: >
  Gerencia o ciclo de vida completo de processos background com suporte
  cross-platform (Windows taskkill + Unix killpg/SIGTERM). Inspirado pelo
  SimulationRunner do MiroFish-Offline (simulation_runner.py).
  Inicia, monitora, pausa, retoma e finaliza processos com tracking de
  estado dual-platform e ingestão de logs em tempo real.
  Use quando precisar executar scripts Python ou binários em background
  com monitoramento de progresso, logs de saída e limpeza garantida.
license: MIT
compatibility: opencode
allowed-tools: Read, Grep, Glob, Bash, Write
metadata:
  author: Reversa Engine (padrão MiroFish-Offline SimulationRunner)
  version: "1.0.0"
  domain: process
  triggers: processo, background, runner, lifecycle, daemon, subprocess
  role: orchestrator
  scope: system
  output-format: json
  related-skills: machine-states, file-ipc, graph-memory-updater
  inspired-by: MiroFish-Offline simulation_runner.py
---

# Process Lifecycle Manager (P11)

## Visão Geral

`runner.py` implementa um gerenciador de ciclo de vida para processos
background com suporte cross-platform. Inspirado pelo `SimulationRunner`
do MiroFish-Offline (~2100 linhas em `simulation_runner.py`), este módulo
fornece controle completo sobre subprocessos: iniciação, monitoramento
por thread, parsing de logs em tempo real, pausa/resume, finalização
controlada e limpeza de recursos.

## Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    ProcessRunner (singleton)                 │
├─────────────┬───────────────┬────────────────┬──────────────┤
│  _processes │   _states     │ _monitor_threads│  IS_WINDOWS │
│  Dict[str,  │  Dict[str,    │ Dict[str,       │  bool       │
│  Popen]     │  ProcessState]│ Thread]         │             │
├─────────────┴───────┬───────┴────────────────┴──────────────┤
│                     Métodos                                │
│  start()  stop()  pause()  resume()                         │
│  get_state()  cleanup_all()  demo()                         │
│  _monitor()  _kill_process()                                │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                    ProcessState                              │
├─────────────────────────────────────────────────────────────┤
│  process_id: str               Identificador único           │
│  status: RunnerStatus          Estado atual                  │
│  pid: Optional[int]            PID do processo               │
│  started_at: Optional[str]     Timestamp de início           │
│  completed_at: Optional[str]   Timestamp de fim              │
│  current_step: int             Passo atual                   │
│  total_steps: int              Total de passos               │
│  progress_percent: float       Progresso 0-100%             │
│  error: Optional[str]          Mensagem de erro             │
│  log_path: Optional[str]       Caminho do arquivo de log    │
│  sub_status: Dict[str,bool]    Tracking dual-platform        │
└─────────────────────────────────────────────────────────────┘
```

## Estados do RunnerStatus

| Estado      | Descrição                                      |
|-------------|------------------------------------------------|
| IDLE        | Estado inicial, processo não iniciado          |
| STARTING    | Inicializando processo                         |
| RUNNING     | Processo em execução                           |
| PAUSED      | Processo pausado (SIGSTOP no Unix)             |
| STOPPING    | Processo sendo finalizado                      |
| STOPPED     | Processo finalizado normalmente                |
| COMPLETED   | Processo concluído com exit_code=0             |
| FAILED      | Processo concluído com exit_code != 0          |

## Tracking Dual-Platform

O campo `sub_status` (Dict[str, bool]) permite tracking simultâneo de
dois subsistemas ou plataformas (ex: twitter + reddit). Cada chave
representa um subsistema; o valor bool indica se foi concluído:

```json
{
  "sub_status": {
    "twitter": true,
    "reddit": false
  }
}
```

## Métodos

### start(process_id, cmd, cwd, env, total_steps, log_dir) → ProcessState
Inicia um processo em background. Cria diretório de logs, configura
ambiente (PYTHONUTF8=1, encoding=utf-8), inicia subprocess.Popen com
start_new_session=True, persiste estado em JSON, inicia thread monitor.

### stop(process_id, timeout=10) → ProcessState
Finaliza processo. Windows: `taskkill /T /PID`. Unix: `killpg(SIGTERM)`
com fallback `killpg(SIGKILL)`. Fallback genérico: process.terminate()
→ process.kill(). Define status=STOPPED.

### pause(process_id) → ProcessState
Pausa processo. Unix: SIGSTOP para o grupo. Windows: suspensão via
thread. Define status=PAUSED.

### resume(process_id) → ProcessState
Retoma processo pausado. Unix: SIGCONT para o grupo. Define
status=RUNNING.

### get_state(process_id) → Optional[ProcessState]
Retorna o estado atual, in-memory ou de arquivo JSON.

### get_actions(process_id, limit=50) → List[Dict]
Parseia o arquivo de log e extrai ações registradas. Cada ação inclui
agent_id, action_type, args, confidence, timestamp.

### get_timeline(process_id) → List[Dict]
Retorna timeline completa de eventos do processo (início, cada passo,
erros, conclusão) a partir do log.

### get_agent_stats(process_id) → Dict
Agrega estatísticas por agente: total de ações por tipo, confiança
média, taxa de sucesso.

### cleanup_logs(process_id)
Remove arquivos de log antigos do processo.

### cleanup_all()
Finaliza todos os processos e limpa threads.

## Tipos de Ação (Simulação)

| Tipo              | Descrição                           |
|-------------------|-------------------------------------|
| CREATE_POST       | Criar postagem                      |
| LIKE_POST         | Curtir postagem                     |
| REPLY_POST        | Responder postagem                  |
| RETWEET           | Retweetar                           |
| FOLLOW            | Seguir usuário                      |
| UNFOLLOW          | Deixar de seguir                    |
| SEND_MESSAGE      | Enviar mensagem direta              |
| REPORT            | Denunciar conteúdo                  |
| BLOCK             | Bloquear usuário                    |
| SEARCH            | Pesquisar conteúdo                  |
| SCRAPE            | Coletar dados                       |
| ANALYZE           | Analisar dados                      |

## Escala de Confiança

| Nível     | Valor | Descrição                            |
|-----------|-------|--------------------------------------|
| CONFIRMADO| 1.0   | Ação verificada e confirmada         |
| INFERIDO  | 0.7   | Ação inferida por padrão de log      |
| LACUNA    | 0.3   | Ação inferida com baixa confiança    |
| DESCONHEC | 0.0   | Sem informação disponível            |

## Exemplos de Uso

```python
from skills.process-lifecycle.scripts.runner import ProcessRunner, RunnerStatus

# Iniciar processo
state = ProcessRunner.start("sim1", ["python", "simulate.py"],
                            cwd="simulacoes", total_steps=50)

# Verificar status
print(ProcessRunner.get_state("sim1").to_dict())

# Pausar e retomar
ProcessRunner.pause("sim1")
ProcessRunner.resume("sim1")

# Parar
ProcessRunner.stop("sim1")

# Modo demo
ProcessRunner.demo()
```

## Arquivos

| Arquivo                  | Descrição                        |
|--------------------------|----------------------------------|
| `scripts/runner.py`      | Implementação principal          |
| `references/pseudocode.md`| Pseudocódigo e diagramas        |

## Dependências

- Python 3.10+
- `subprocess`, `threading`, `atexit` (stdlib)
- `signal` (Unix), `taskkill` (Windows)
