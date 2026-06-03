---
name: reasoning-orchestrator
category: system
version: "1.0.0"
kind: python
description: "OpenCode Reasoning Orchestrator v9.0 — 68 tipos de raciocínio (58 base + 10 Teoria dos Jogos). Integrado com AuditSystem, TokenEconomy e DataOrchestrator. Use para selecionar framework lógico, nível de profundidade e matriz de interseção com validação de diversidade de raciocínio."
user-invocable: true
license: MIT
compatibility: OpenCode, Claude Code, Cursor, Gemini CLI
metadata:
  author: OpenCode Ecosystem
  version: "9.0.0"
  evolved_from: "v8.0 (Nexus) + v6.1 (Z-Notation)"
  game_theory_strategies: 10
  total_reasoning_types: 68
  integrated_with: ["TokenEconomyMonitor", "ResearcherScore", "DataOrchestrator"]
allowed-tools: Read Edit Write Glob Grep Bash Task SequentialThinking
---

# 🧠 Reasoning Orchestrator Nexus v9.0 — +Teoria dos Jogos

Motor de inteligência analítica integrando **68 tipos de raciocínio** (58 base + 10 Teoria dos Jogos) em arquitetura de 4 níveis de profundidade (L1-L4). A partir da v9.0, a **Teoria dos Jogos** é categoria de primeira classe, integrada com o Agent Forum (P14) e o PhD Auditor (P18).

## 🚀 Protocolo Nexus — Checkpoint Obrigatório

1. **Nível de Publicação**: N1 Magnum (43 agentes), N2 Standard (~20), N3 Express (10)
2. **Profundidade (L1-L4)**: Consulte `references/depth_levels.md`
3. **Matriz de Raciocínio**: Selecione tipos em `references/reasoning_types.md`
4. **Teoria dos Jogos**: Aplique `references/game_theory.md` para decisões estratégicas
5. **Eficiência de Tokens**: Aplique as 7 estratégias em `references/token_efficiency.md`
6. **Auditoria**: Registre escolha de raciocínio via `reasoning_audit_bridge.py`

## 📊 Níveis de Publicação (Integrados ao TokenEconomyMonitor)

| Nível | Nome | Agentes | Orçamento Tokens | Raciocínios Mínimos |
|:-----:|------|:------:|:----------------:|:-------------------:|
| N1 | Magnum/Qualis A1 | 43 | 500K | 5+ (incluir 1 Teoria dos Jogos) |
| N2 | Standard/Q1-Q2 | ~20 | 200K | 3+ |
| N3 | Express | 10 | 50K | 1-2 |

## 🎮 Teoria dos Jogos — 10 Estratégias (Nova Categoria v9.0)

| # | Estratégia | Aplicação | Prof. |
|:--:|-----------|----------|:-----:|
| 1 | **Equilíbrio de Nash** | Estratégia ótima dado oponente racional | L3 |
| 2 | **Dilema do Prisioneiro** | Cooperação vs traição em sistemas multiagente | L3 |
| 3 | **Soma Zero** | Ganho de um = perda do outro (competição) | L2 |
| 4 | **Tit-for-Tat (Olho por Olho)** | Cooperação condicional iterada | L2 |
| 5 | **Stackelberg (Líder-Seguidor)** | Vantagem do primeiro movimento | L3 |
| 6 | **Barganha (Nash Bargaining)** | Divisão ótima de recursos escassos | L3 |
| 7 | **Sinalização** | Informação assimétrica entre agentes | L3 |
| 8 | **Evolutivo** | Seleção natural de estratégias em populações | L4 |
| 9 | **Bayesiano (Harsanyi)** | Jogos com informação incompleta | L4 |
| 10 | **Cooperativo (Shapley)** | Formação de coalizões e valor marginal | L4 |

## 🛠️ Recursos (Progressive Disclosure)

- `references/reasoning_types.md`: 68 tipos (58 base + 10 Game Theory)
- `references/game_theory.md`: Guia completo de Teoria dos Jogos
- `references/token_efficiency.md`: 7 estratégias de economia
- `references/depth_levels.md`: Arquitetura L1-L4
- `references/intersection_matrix.md`: Combinações domínio-raciocínio
- `../reasoning_audit_bridge.py`: Bridge com AuditSystem (ResearcherScore + TokenEconomy)
