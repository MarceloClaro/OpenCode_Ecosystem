---
name: fileipc
description: >
  Comunicação entre processos via filesystem (IPC sem dependências).
  Permite enviar comandos para processos externos e aguardar respostas
  de forma assíncrona.
usage: /fileipc <subcommand> [args]
subcommands:
  - status: Verifica status dos diretórios IPC
  - send <type> [args_json]: Envia comando via IPC
  - server start: Inicia servidor IPC local
  - server stop: Para servidor IPC local
  - ping: Testa conectividade do IPC
  - cleanup: Limpa comandos órfãos (>1h)
examples:
  - /fileipc status
  - /fileipc send ping
  - /fileipc send analyze_file {"target": "src/"}
  - /fileipc server start
---

# /fileipc

Comando de comunicação entre processos via filesystem.

## Subcomandos

### /fileipc status

Exibe o estado atual dos diretórios IPC:

```
📂 IPC Status
  Commands:    3 pendentes
  Responses:   1 disponível
  Archive:     12 processados
  Locks:       0 ativos
  Total IPC:   238 comandos no histórico
```

### /fileipc send <type> [args]

Envia um comando e aguarda resposta:

```
/fileipc send ping
  → Response: {"pong": true, "time": "2026-05-17T00:00:10Z"}

/fileipc send analyze_file {"target": "src/"}
  → Response: {"files": 24, "lines": 5600, ...}
```

### /fileipc server [start|stop]

Gerencia o servidor IPC local:

```
/fileipc server start
  → FileIPC Server started
  → Handlers: ping, analyze_file, search_pattern

/fileipc server stop
  → FileIPC Server stopped
```

### /fileipc ping

Teste rápido de conectividade:

```
/fileipc ping
  → ✅ IPC ativo (2.3ms de latência)
```

### /fileipc cleanup

Remove comandos órfãos (mais de 1 hora sem processamento):

```
/fileipc cleanup
  → 3 comandos órfãos removidos
```

## Integração com Script Externo

```bash
# Via terminal
python skills/file-ipc/scripts/ipc_client.py client analyze_file '{"target": "."}'

# Resultado
{
  "id": "cmd-abc123",
  "status": "completed",
  "result": {
    "directory": ".",
    "files": 128,
    "total_size": 5242880
  },
  "duration_ms": 1500
}
```
