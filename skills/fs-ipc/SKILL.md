---
name: fs-ipc
description: >
  Comunicação entre processos via filesystem (File IPC refinado). Inspirado
  pelo SimulationIPC do MiroFish-Offline (simulation_ipc.py). Usa diretórios
  commands/ + responses/ com JSON para troca de mensagens entre processos
  independentes sem sockets, pipes ou message brokers.
  Suporta polling com timeout, múltiplos tipos de comando, batch operations,
  verificação de ambiente e limpeza automática.
  Use quando precisar de IPC simples e robusto entre processos isolados.
license: MIT
compatibility: opencode
allowed-tools: Read, Grep, Glob, Bash, Write
metadata:
  author: Reversa Engine (padrão MiroFish-Offline SimulationIPC)
  version: "1.1.0"
  domain: communication
  triggers: ipc, comunicação, processo, filesystem, comando, mensagem
  role: communication
  scope: system
  output-format: json
  related-skills: process-lifecycle
  inspired-by: MiroFish-Offline simulation_ipc.py
---

# Filesystem IPC — P12 (Refinado)

Comunicação entre processos via diretórios `commands/` + `responses/`.
Inspirado pelo `SimulationIPC` do MiroFish-Offline (`simulation_ipc.py`, ~670 linhas).
Refina o padrão P2 `file-ipc` com arquitetura Client/Server completa.

## Arquitetura

```
<ipc_dir>/
├── commands/          ← Client escreve, Server lê (polling)
│   ├── <uuid>.json
│   └── ...
├── responses/         ← Server escreve, Client lê
│   ├── <uuid>.json
│   └── ...
└── env_status.json   ← Heartbeat do Server
```

### Fluxo

1. **Client**: gera UUID, escreve `command.json` em `commands/`
2. **Server**: `poll_commands()` → lê arquivo mais antigo (por mtime)
3. **Server**: processa comando (INTERVIEW, BATCH_INTERVIEW, etc.)
4. **Server**: `send_response()` → escreve `response.json`, deleta `command.json`
5. **Client**: detecta `response.json` no polling, lê, deleta ambos

## CommandTypes

| Tipo | Args esperados | Descrição |
|---|---|---|
| `INTERVIEW` | `{agent_id, prompt, platform?}` | Entrevistar um agente |
| `BATCH_INTERVIEW` | `{interviews: [{agent_id, prompt}]}` | Múltiplas entrevistas em lote |
| `CLOSE_ENV` | `{}` | Fechar ambiente de simulação |
| `CUSTOM` | `{action, payload}` | Comando genérico para uso fora de simulação |

## CommandStatus

| Status | Descrição |
|---|---|
| `PENDING` | Comando aguardando processamento |
| `PROCESSING` | Server iniciou processamento |
| `COMPLETED` | Processamento concluído com sucesso |
| `FAILED` | Processamento falhou |

## Componentes

### IPCClient (lado emissor)

Envia comandos e aguarda respostas com timeout configurável.

| Método | Descrição |
|---|---|
| `send_command(type, args, timeout, poll_interval)` | Envia comando e aguarda resposta |
| `send_interview(agent_id, prompt)` | Atalho para INTERVIEW |
| `send_batch_interview(interviews)` | Atalho para BATCH_INTERVIEW |
| `send_close_env()` | Atalho para CLOSE_ENV |
| `check_env_alive()` | Verifica heartbeat do servidor |

### IPCServer (lado receptor)

Faz polling de comandos, executa e responde.

| Método | Descrição |
|---|---|
| `start()` | Inicia servidor, atualiza env_status para "alive" |
| `stop()` | Para servidor, atualiza env_status para "stopped" |
| `poll_commands()` | Lê comando mais antigo de `commands/` |
| `send_response(response)` | Escreve resposta, deleta comando |
| `send_success(command_id, result)` | Atalho para resposta COMPLETED |
| `send_error(command_id, error)` | Atalho para resposta FAILED |

## Polling com Timeout

```python
client = IPCClient(".ipc")
try:
    response = client.send_command(
        CommandType.CUSTOM,
        {"action": "analyze", "payload": {"target": "src/"}},
        timeout=120.0,
        poll_interval=1.0
    )
    print(response.result)
except TimeoutError:
    print("Comando excedeu timeout de 120s")
```

## UUID Tracking

Cada comando recebe um `command_id` UUID v4 único. O mesmo UUID é usado no arquivo de resposta, permitindo rastreamento ponto-a-ponto.

## Verificação de Ambiente

O servidor mantém `env_status.json` com:
- `status`: "alive" | "stopped"
- `pid`: PID do processo servidor
- `started_at`: Timestamp de início
- `last_heartbeat`: Última atualização

## Limpeza Automática

- Resposta lida → arquivos `command.json` + `response.json` deletados
- Timeout → arquivo de comando deletado
- Server stop → `env_status.json` atualizado para "stopped"

## Escala de Confiança

| Nível | Descrição |
|---|---|
| **4/5 — Production** | Testado em pipelines reais multi-processo |
| **IPC local** | Sem rede, sem sockets, sem dependências |
| **Determinístico** | Polling + UUID garante rastreabilidade |
| **Auto-limpeza** | Zero resíduo após cada ciclo |

## Exemplos

```python
from skills.fs_ipc.scripts.ipc_client import IPCClient, IPCServer, CommandType

# Servidor (processo B)
server = IPCServer(".ipc")
server.start()
cmd = server.poll_commands()
if cmd:
    result = {"message": f"Processed {cmd.command_type}", "args": cmd.args}
    server.send_success(cmd.command_id, result)
server.stop()

# Cliente (processo A)
client = IPCClient(".ipc")
resp = client.send_command(CommandType.CUSTOM,
    {"action": "hello", "payload": {"text": "world"}},
    timeout=30.0
)
print(resp.status, resp.result)
```
