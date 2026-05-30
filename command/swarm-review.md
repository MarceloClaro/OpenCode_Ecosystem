<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Inspirado pelo motor de simulação multi-agente OASIS do MiroFish.
-->

---
description: >
  Ativa o Swarm Review — revisão de código por enxame de agentes especializados
  (Segurança, Performance, Arquitetura). Inspirado pelo OASIS multi-agent
  simulation do MiroFish (60.9K ★ GitHub). Cada agente analisa independentemente,
  debate divergências e produz relatório consolidado.
  Uso: /swarm-review [target]
  Exemplos:
    /swarm-review                  — revisa o último commit
    /swarm-review src/file.js      — revisa arquivo específico
    /swarm-review --pr=42          — revisa PR #42
    /swarm-review --quick          — modo rápido (2 agentes: security + perf)
    /swarm-review --full           — modo completo (3 agentes, debate obrigatório)
---

# Swarm Review — Revisão por Enxame de Agentes

Ativa o **Swarm Review Agent**, que orquestra um enxame de agentes especializados
para revisão de código multi-perspectiva, inspirado pelo motor de simulação
social **OASIS** do MiroFish.

## Como funciona

```
/swarm-review [target] [--quick|--full]
```

### Modos

| Modo | Agentes | Quando usar |
|------|---------|-------------|
| `--quick` (padrão) | Segurança + Performance | Code review diário |
| `--full` | Segurança + Performance + Arquitetura | PRs críticos, auditorias |

### Alvos

| Alvo | Descrição |
|------|-----------|
| (vazio) | Último commit |
| `caminho/arquivo.js` | Arquivo específico |
| `--pr=42` | PR #42 do repositório atual |
| `diretório/` | Todos arquivos no diretório |

## Pipeline

1. **Análise Paralela** — Cada agente analisa o código independentemente
2. **Debate** — Agentes confrontam achados, resolvem conflitos
3. **Síntese** — Relatório consolidado com score e veredito
4. **Entrega** — Salvo em `_reversa_sdd/swarm-review-report.md`

## Exemplo

```
$ /swarm-review src/controllers/user.js --full

🛡️ Segurança: 3 achados (1 crítico)
⚡ Performance: 2 achados (1 importante)
🏗️ Arquitetura: 1 achado (sugestão)

📊 Score: 78/100 — ⚠️ Aceitável com ressalvas
📄 Relatório: _reversa_sdd/swarm-review-report.md
```
