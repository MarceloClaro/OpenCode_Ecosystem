# Protocolo File IPC — Especificação Técnica

> Inspirado pelo `simulation_ipc.py` do MiroFish.

---

## Visão Geral

File IPC é um protocolo de comunicação assíncrona entre processos usando
exclusivamente o filesystem como barramento de mensagens. Não requer
nenhuma dependência além de um sistema de arquivos compartilhado.

## Formato das Mensagens

### Commands (escritos pelo cliente)

```json
{
  "id": "cmd-550e8400-e29b-41d4-a716-446655440000",
  "type": "analyze_file",
  "args": {
    "target": "src/main.py",
    "depth": "full"
  },
  "metadata": {
    "agent": "reversa-scout",
    "session": "sess-001",
    "priority": 5
  },
  "timestamp": "2026-05-17T00:00:00.000Z",
  "ttl": 300
}
```

### Responses (escritos pelo servidor)

```json
{
  "id": "cmd-550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "result": {
    "files": 12,
    "lines": 3420,
    "language": "python"
  },
  "error": null,
  "metadata": {
    "processor": "file-analyzer",
    "version": "1.0"
  },
  "timestamp": "2026-05-17T00:00:10.000Z",
  "duration_ms": 10000
}
```

## Estados de um Comando

```
CREATED → (escrito em commands/)
    ↓
PENDING → (servidor detectou)
    ↓
RUNNING → (servidor processando)
    ↓
COMPLETED → (resposta em responses/)
    ↓
ARCHIVED → (movido para archive/)
```

## Polling e Timeout

### Estratégia de Polling (cliente)

```
Intervalo inicial: 200ms
Após 5 tentativas sem resposta: 500ms
Após 20 tentativas sem resposta: 1s
Timeout total: TTL configurado (padrão 300s)
```

### Tratamento de Timeout

```python
if time_since_creation > command['ttl']:
    write_response(id, 'failed', error='timeout')
    archive_command(id)
    return None
```

## Lock File Protocol

Para evitar race conditions em escritas concorrentes:

```python
def acquire_lock(lock_path, timeout=5):
    """Tenta adquirir lock. Retorna True se conseguiu."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return True
        except FileExistsError:
            time.sleep(0.1)
    return False

def release_lock(lock_path):
    """Libera lock."""
    if os.path.exists(lock_path):
        os.remove(lock_path)
```

## Referência Rápida

### Comandos Built-in

| Comando | Descrição | Args | Exemplo |
|---------|-----------|------|---------|
| `ping` | Health check | — | `{"type": "ping"}` |
| `analyze_file` | Análise de arquivo | `target`, `depth` | `{"target": "file.py", "depth": "full"}` |
| `search_pattern` | Busca regex | `pattern`, `path` | `{"pattern": "class \\w+", "path": "src/"}` |
| `run_query` | SQL query | `query` | `{"query": "SELECT * FROM graph_nodes"}` |
| `execute` | Script arbitrário | `command`, `args` | `{"command": "echo hello"}` |
| `cancel` | Cancela comando | `cancel_id` | `{"cancel_id": "cmd-xxx"}` |

### Status Codes

| Status | Descrição |
|--------|-----------|
| `created` | Comando escrito no disco |
| `pending` | Servidor detectou, aguardando processamento |
| `running` | Servidor está processando |
| `completed` | Execução concluída com sucesso |
| `failed` | Execução falhou |
| `cancelled` | Cancelado pelo cliente |
| `timeout` | Excedeu TTL sem resposta |

### Códigos de Erro

| Código | Significado |
|--------|-------------|
| `ERR_TIMEOUT` | Comando expirou |
| `ERR_NOT_FOUND` | Arquivo/diretório não encontrado |
| `ERR_PERMISSION` | Sem permissão para ler/escrever |
| `ERR_INVALID_ARGS` | Argumentos inválidos |
| `ERR_INTERNAL` | Erro interno do servidor |
| `ERR_CANCELLED` | Comando cancelado |

## Exemplo Completo

### Cliente (Python)

```python
from file_ipc import FileIPCClient

client = FileIPCClient(ipc_dir=".ipc")
cmd_id = client.send_command("analyze_file", {
    "target": "src/main.py",
    "depth": "full"
})
response = client.wait_response(cmd_id, timeout=60)
if response["status"] == "completed":
    print(response["result"])
```

### Servidor (Python)

```python
from file_ipc import FileIPCServer

server = FileIPCServer(ipc_dir=".ipc")

@server.on("analyze_file")
def handle_analyze(args):
    path = Path(args["target"])
    return {
        "files": 1,
        "lines": len(path.read_text().splitlines()),
        "language": path.suffix
    }

server.start(poll_interval=0.5)
```
