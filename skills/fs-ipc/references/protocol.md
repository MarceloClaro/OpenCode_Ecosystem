# Protocolo Filesystem IPC (v1.1)

## Estrutura de Diretórios

```
<ipc_dir>/
├── commands/          ← Client escreve, Server lê
│   ├── <uuid>.json   ← Comando pendente
│   └── ...
├── responses/         ← Server escreve, Client lê
│   ├── <uuid>.json   ← Resposta ao comando
│   └── ...
└── env_status.json   ← Heartbeat do Server
```

## Formato do Comando

```json
{
  "command_id": "uuid-v4",
  "command_type": "interview|batch_interview|close_env|custom",
  "args": { ... },
  "timestamp": "2026-01-01T00:00:00"
}
```

### Campos

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `command_id` | string | sim | UUID v4 único |
| `command_type` | string | sim | Tipo do comando (enum) |
| `args` | object | sim | Argumentos específicos do tipo |
| `timestamp` | string | sim | ISO 8601 |

## Formato da Resposta

```json
{
  "command_id": "uuid-v4",
  "status": "completed|failed",
  "result": { ... },
  "error": null,
  "timestamp": "2026-01-01T00:00:01"
}
```

### Campos

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `command_id` | string | sim | UUID do comando original |
| `status` | string | sim | COMPLETED ou FAILED |
| `result` | object | não | Dados de retorno (se COMPLETED) |
| `error` | string | não | Mensagem de erro (se FAILED) |
| `timestamp` | string | sim | ISO 8601 |

## Formato do env_status.json

```json
{
  "status": "alive|stopped",
  "pid": 12345,
  "started_at": "2026-01-01T00:00:00",
  "last_heartbeat": "2026-01-01T00:00:05"
}
```

## Fluxo Completo

```
Client                          Server
  │                               │
  │  1. Gera UUID v4              │
  │  2. Escreve command.json ────→│
  │     em commands/              │
  │                               │  3. poll_commands()
  │                               │  4. Lê arquivo + antigo
  │                               │  5. Processa comando
  │                               │  6. send_response()
  │  ←──── response.json          │     (escreve response, deleta command)
  │  7. Detecta response.json     │
  │  8. Lê resultado              │
  │  9. Deleta response.json      │
  │                               │
```

## Tipos de Comando

| CommandType | args esperados | Uso |
|---|---|---|
| `INTERVIEW` | `{agent_id, prompt, platform?}` | Entrevistar agente |
| `BATCH_INTERVIEW` | `{interviews: [{agent_id, prompt}]}` | Entrevista em lote |
| `CLOSE_ENV` | `{}` | Fechar ambiente |
| `CUSTOM` | `{action, payload}` | Uso genérico |

### INTERVIEW

```json
{
  "command_id": "a1b2c3d4-...",
  "command_type": "interview",
  "args": {
    "agent_id": "scout",
    "prompt": "Analise a estrutura do diretório src/",
    "platform": "opencode"
  },
  "timestamp": "2026-01-01T00:00:00"
}
```

### BATCH_INTERVIEW

```json
{
  "command_id": "e5f6g7h8-...",
  "command_type": "batch_interview",
  "args": {
    "interviews": [
      {"agent_id": "scout", "prompt": "Mapeie src/"},
      {"agent_id": "detective", "prompt": "Revise lógica em src/core"}
    ]
  },
  "timestamp": "2026-01-01T00:00:00"
}
```

### CLOSE_ENV

```json
{
  "command_id": "i9j0k1l2-...",
  "command_type": "close_env",
  "args": {},
  "timestamp": "2026-01-01T00:00:00"
}
```

### CUSTOM (extensão genérica)

```json
{
  "command_id": "m3n4o5p6-...",
  "command_type": "custom",
  "args": {
    "action": "analyze_file",
    "payload": {
      "target": "src/main.py",
      "depth": "full"
    }
  },
  "timestamp": "2026-01-01T00:00:00"
}
```

## Polling e Timeout

- **Timeout padrão**: 60 segundos
- **Poll interval padrão**: 0.5 segundos
- **Comportamento**: Client verifica `responses/<uuid>.json` a cada `poll_interval` segundos
- **TimeOut**: Se `timeout` excedido, `send_command` levanta `TimeoutError` e deleta o comando pendente

## Limpeza

| Evento | Ação |
|---|---|
| Resposta lida com sucesso | Deleta `command.json` + `response.json` |
| Timeout | Deleta `command.json` |
| Server.stop() | Atualiza `env_status.json` para "stopped" |
| Erro de parse | Deleta arquivo corrompido, loga warning |

## Garantias

1. **Atomicidade**: Cada comando tem UUID único → sem colisão
2. **Idempotência**: Server processa um comando uma vez (deleta ao responder)
3. **Rastreabilidade**: command_id conecta comando ↔ resposta
4. **Zero dependências**: Apenas filesystem + JSON (stdlib Python)
