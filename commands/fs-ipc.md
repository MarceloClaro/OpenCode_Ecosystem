---
name: fs-ipc
description: >
  Filesystem IPC — comunicaçao entre processos via diretórios commands/ +
  responses/. Usa polling com timeout, UUID tracking e limpeza automática.
  Baseado no SimulationIPC do MiroFish-Offline (P12 refinado).
---

# `/fs-ipc` — Filesystem IPC

Comando para gerenciar comunicação entre processos via filesystem.

## Subcomandos

### `status` — Status dos diretórios IPC

```
/fs-ipc status [ipc_dir]
```

Exibe:
- Caminho do diretório IPC
- Número de comandos pendentes
- Número de respostas pendentes
- Status do servidor (env_status.json)

### `send <tipo> <args>` — Enviar comando

```
/fs-ipc send <tipo> <args_json> [ipc_dir] [timeout]
```

Argumentos:
- `tipo`: `interview`, `batch_interview`, `close_env`, `custom`
- `args_json`: JSON com argumentos do comando
- `ipc_dir`: Diretório IPC (padrão: `.ipc`)
- `timeout`: Timeout em segundos (padrão: 60)

Exemplos:
- `/fs-ipc send custom '{"action":"ping"}'` — Ping
- `/fs-ipc send interview '{"agent_id":"scout","prompt":"Analise src/"}' — Entrevistar agente
- `/fs-ipc send close_env '{}'` — Fechar ambiente

### `server [start|stop]` — Gerenciar servidor IPC

```
/fs-ipc server [start|stop] [ipc_dir]
```

- `start`: Inicia servidor em background (polling de comandos)
- `stop`: Para servidor, atualiza env_status para "stopped"

### `ping` — Verificar heartbeat

```
/fs-ipc ping [ipc_dir]
```

Verifica se o servidor está alive lendo `env_status.json`.

### `batch <file>` — Comandos em lote

```
/fs-ipc batch <arquivo_json> [ipc_dir]
```

Envia múltiplos comandos de um arquivo JSON. Formato:

```json
{
  "commands": [
    {"type": "custom", "args": {"action": "ping"}},
    {"type": "interview", "args": {"agent_id": "scout", "prompt": "..."}}
  ],
  "timeout": 120
}
```

## Exemplos

```bash
# Verificar status
/fs-ipc status

# Enviar ping
/fs-ipc send custom '{"action":"ping"}'

# Entrevistar agente
/fs-ipc send interview '{"agent_id":"scout","prompt":"Analise src/","platform":"opencode"}'

# Batch
/fs-ipc batch batch_job.json

# Gerenciar servidor
/fs-ipc server start
/fs-ipc server stop
```

## Referência

Ver `skills/fs-ipc/SKILL.md` e `skills/fs-ipc/references/protocol.md`.
