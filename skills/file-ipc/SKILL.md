---
name: file-ipc
description: >
  Sistema de comunicação entre processos via filesystem (IPC file-based),
  inspirado pelo simulation_ipc.py do MiroFish. Permite que agentes OpenCode
  se comuniquem com ferramentas externas (MCPs, scripts, subprocessos) de
  forma assíncrona, sem depender de message brokers (Redis, RabbitMQ).
  Use quando precisar de comunicação simples e confiável entre processos,
  especialmente em cenários onde MCPs síncronos não são adequados.
license: MIT
compatibility: opencode
allowed-tools: Read, Write, Glob, Bash
metadata:
  author: Reversa Engine (padrão MiroFish)
  version: "1.0.0"
  domain: infrastructure
  triggers: ipc, communication, async communication, file-based ipc
  role: infrastructure
  scope: communication
  output-format: json
  related-skills: agent-smith, devops-engineer
  inspired-by: MiroFish simulation_ipc.py (protocolo de comunicação file-based)
---

# File IPC — Comunicação entre Processos via Filesystem

Inspirado pelo `simulation_ipc.py` do MiroFish, que implementa comunicação
assíncrona entre o servidor Flask e os subprocessos de simulação (Twitter +
Reddit) usando **apenas arquivos JSON em disco**.

## Arquitetura (Padrão MiroFish)

```
┌──────────────┐     Commands/     ┌──────────────────┐
│              │ ─────────────────►│                  │
│   Cliente    │   command_001.json │   Servidor       │
│   (emissor)  │   command_002.json │   (processador)  │
│              │◄───────────────── │                  │
└──────────────┘     Responses/    └──────────────────┘
                     response_001.json
                     response_002.json
```

## Quando Usar

| Cenário | Alternativa | File IPC |
|---------|-------------|----------|
| MCP síncrono demora | Aumentar timeout | Usar File IPC async |
| MCP não disponível | Esperar | Usar script autônomo via File IPC |
| Teste/desenvolvimento | Setup complexo | File IPC zero-config |
| Pipeline multi-etapas | Orquestrador caro | File IPC simples |

## Protocolo

### Formato do Comando

```json
{
  "id": "cmd-uuid",
  "type": "analyze_file | search_pattern | run_query | custom",
  "args": {
    "target": "path/to/file",
    "params": {}
  },
  "timestamp": "2026-05-17T00:00:00Z",
  "ttl": 300
}
```

### Formato da Resposta

```json
{
  "id": "cmd-uuid",
  "status": "completed | failed | running",
  "result": {},
  "error": null,
  "timestamp": "2026-05-17T00:00:10Z",
  "duration_ms": 10000
}
```

### Diretórios

```
.ipc/
├── commands/          ← Comandos pendentes (cliente escreve)
│   ├── cmd-001.json
│   └── cmd-002.json
├── responses/         ← Respostas (servidor escreve)
│   ├── cmd-001.json
│   └── cmd-002.json
├── archive/           ← Comandos/respostas processados
└── locks/             ← Lock files para evitar race conditions
```

## Workflow

### Cliente (quem envia o comando)

1. Gera UUID para o comando
2. Escreve JSON em `.ipc/commands/{uuid}.json`
3. Polla `.ipc/responses/{uuid}.json` em intervalos de 200ms
4. Timeout após TTL configurado (padrão 300s)
5. Lê resposta e processa

### Servidor (quem executa o comando)

1. Monitora `.ipc/commands/` por novos arquivos
2. Lê comando, executa ação correspondente
3. Escreve resposta em `.ipc/responses/{uuid}.json`
4. Move comando para `.ipc/archive/`

## Comandos Suportados

| Tipo | Descrição | Args |
|------|-----------|------|
| `analyze_file` | Analisa arquivo | `target`, `depth` |
| `search_pattern` | Busca padrão | `pattern`, `path` |
| `run_query` | Executa SQL | `query`, `params` |
| `execute_script` | Roda script | `script`, `args` |
| `ping` | Health check | — |

## Tratamento de Erros

- **Timeout**: Cliente marca como `failed` após TTL
- **Lock**: Arquivos `.lock` previnem leitura concorrente
- **Stale**: Comandos não processados após 1h são arquivados automaticamente
- **Orphan**: Respostas sem comando correspondente são ignoradas

## Output

Resultados retornados como JSON e registrados em `.ipc/log/`.

## Regras

### MUST DO
- Sempre usar UUIDs únicos para comandos
- Implementar polling com backoff (200ms → 500ms → 1s)
- Respeitar TTL configurado
- Limpar comandos/respostas após processamento
- Usar lock files para evitar race conditions

### MUST NOT DO
- Processar comandos sem UUID
- Ignorar TTL (comandos podem ficar órfãos)
- Escrever diretamente nos diretórios do servidor
- Usar File IPC para comunicação intra-sessão (preferir variáveis locais)
