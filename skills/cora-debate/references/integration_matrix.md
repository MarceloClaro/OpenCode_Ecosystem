# Matriz de Integracao Cora-Debate (P19)

## Conexoes com o Ecossistema OpenCode v4.2

```
┌────────────────────────────────────────────────────────────────────┐
│                     P19: CORA-DEBATE                                │
│                                                                     │
│  ┌─────────────┐   ┌──────────────┐   ┌──────────────────────┐    │
│  │ cora-debate  │◄──┤ cora-qscore  │◄──┤ cora-verifier (MCP)  │    │
│  │   (skill)    │   │   (plugin)   │   │   (6 verificadores)   │    │
│  └──────┬───────┘   └──────┬───────┘   └──────────┬───────────┘    │
│         │                  │                       │                │
│         ▼                  ▼                       ▼                │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │              ECOSSISTEMA OPENCODE v4.2                     │      │
│  │                                                            │      │
│  │  P14: agent-forum (protocolo de forum)                    │      │
│  │  P15: document-ir (estruturacao de output)                │      │
│  │  P16: agent-node-pipeline (pipeline ANP)                  │      │
│  │  P17: middleware-chain (middlewares DeerFlow)              │      │
│  │  P18: PhD Auditor (Nash + Cohen + Bonferroni + Qualis)    │      │
│  │  reasoning-orchestrator (38 tipos de raciocinio)          │      │
│  │  swarm-review (revisao por enxame)                        │      │
│  │  academic-ml-pipeline (ML academico)                      │      │
│  └──────────────────────────────────────────────────────────┘      │
└────────────────────────────────────────────────────────────────────┘
```

## Tabela de Afinidades

| Origem | Destino | Afinidade | Tipo | Descricao |
|--------|---------|-----------|------|-----------|
| cora-debate | agent-forum (P14) | 0.95 | Protocolo | Herda estrutura de forum multiagente |
| cora-debate | reasoning-orchestrator | 0.90 | Raciocinio | 38 tipos alimentam debatedores |
| cora-debate | swarm-review | 0.85 | Revisao | Verificacao por enxame no estagio DEBATE |
| cora-debate | academic-ml-pipeline | 0.80 | Estatistica | V4 compartilha testes estatisticos |
| cora-debate | PhD Auditor (P18) | 0.75 | Auditoria | Nash Solver + Cohen's d |
| cora-qscore | agent-node-pipeline (P16) | 0.80 | Pipeline | Selecao de nos por Q-Score |
| cora-qscore | mirofish-sync | 0.70 | Sincronizacao | Monitora upstream ForumEngine |
| cora-verifier | code-runner | 0.95 | Execucao | Executa verificacoes Python/SymPy |
| cora-verifier | sequential-thinking | 0.85 | Raciocinio | Verifica passos de cadeia de pensamento |
| cora-verifier | academic-ml-pipeline | 0.80 | Estatistica | V4 usa SciPy compartilhado |

## Comandos Slash Integrados

| Comando | Componente | Acao |
|---------|-----------|------|
| `/debate` | cora-debate (skill) | Inicia debate completo |
| `/cora-score` | cora-qscore (plugin) | Exibe ranking Q-Score |
| `/cora-select` | cora-qscore (plugin) | Seleciona melhor agente |
| `/cora-reward` | cora-qscore (plugin) | Registra recompensa |
| `/cora-reset` | cora-qscore (plugin) | Reseta Q-Scores |
| `/cora-verify` | cora-verifier (MCP) | Executa verificador especifico |
| `/cora-health` | cora-verifier (MCP) | Verifica saude dos verificadores |

## Fluxo de Dados

```
Usuario -> /debate <topico>
  -> skill cora-debate (SKILL.md)
    -> plugin cora-qscore (seleciona agente via UCB1)
      -> reasoning-orchestrator (define tipo de raciocinio)
        -> agent-forum (protocolo de debate)
          -> MCP cora-verifier (verifica cada afirmacao)
            -> code-runner (executa SymPy/SciPy)
          <- resultado da verificacao
        <- sintese do debate
      <- atualiza Q-Score com reward
    <- calibracao Platt
  <- relatorio final verificado
Usuario <- output formatado (document-ir ou markdown)
```
