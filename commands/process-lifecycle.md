# /process-lifecycle — Gerenciador de Ciclo de Vida de Processos

Comando para gerenciar processos background com suporte cross-platform.

## Subcomandos

### `/process-lifecycle start <id> <cmd> [total_steps] [cwd]`

Inicia um processo em background.

| Parâmetro     | Descrição                          | Obrigatório |
|---------------|------------------------------------|-------------|
| id            | Identificador único do processo    | Sim         |
| cmd           | Comando + argumentos (entre aspas) | Sim         |
| total_steps   | Total de passos esperados          | Não (padrão: 100) |
| cwd           | Diretório de trabalho              | Não (padrão: atual) |

Exemplo:
```
/process-lifecycle start sim01 "python worker.py --rounds 50" 50
```

### `/process-lifecycle stop <id> [timeout]`

Finaliza um processo.

| Parâmetro | Descrição                    | Obrigatório |
|-----------|------------------------------|-------------|
| id        | Identificador do processo    | Sim         |
| timeout   | Timeout em segundos          | Não (padrão: 10) |

### `/process-lifecycle pause <id>`

Pausa um processo em execução.

### `/process-lifecycle resume <id>`

Retoma um processo pausado.

### `/process-lifecycle status [id]`

Exibe o estado atual de um ou todos os processos.

| Parâmetro | Descrição                         | Obrigatório |
|-----------|-----------------------------------|-------------|
| id        | Identificador (omita para listar) | Não         |

### `/process-lifecycle actions <id> [limit]`

Lista ações extraídas do log do processo.

| Parâmetro | Descrição                | Obrigatório |
|-----------|--------------------------|-------------|
| id        | Identificador do processo| Sim         |
| limit     | Máximo de ações (padrão: 50) | Não     |

### `/process-lifecycle timeline <id>`

Exibe a timeline completa de eventos do processo.

### `/process-lifecycle stats <id>`

Exibe estatísticas agregadas por agente.

### `/process-lifecycle cleanup [id]`

Remove arquivos de log. Se id for omitido, limpa todos.

## Exemplos

```
# Iniciar simulação
/process-lifecycle start tw-sim "python simulate.py --platform twitter" 100

# Verificar status
/process-lifecycle status tw-sim

# Pausar e retomar
/process-lifecycle pause tw-sim
/process-lifecycle resume tw-sim

# Analisar resultados
/process-lifecycle actions tw-sim 20
/process-lifecycle stats tw-sim

# Finalizar e limpar
/process-lifecycle stop tw-sim
/process-lifecycle cleanup tw-sim
```

## Retorno

O comando retorna JSON com:
- `status`: "ok" ou "error"
- `operation`: nome da operação
- `data`: dados da operação (estado, ações, etc.)
- `error`: mensagem de erro (se aplicável)
