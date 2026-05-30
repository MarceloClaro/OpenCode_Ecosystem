<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Inspirado pelo simulation_config_generator.py do MiroFish.
-->

---
description: >
  Gera plano de engenharia reversa em etapas (Scope → Modules → Tasks →
  Dependencies → Resources), inspirado pelo gerador de configuração de
  simulação em 4 etapas do MiroFish.
  Uso: /generate-plan [target] [--depth=...] [--focus=...]
  Exemplos:
    /generate-plan                        — gera plano para o projeto atual
    /generate-plan ./src                  — gera plano para diretório específico
    /generate-plan --depth=essential      — plano essencial (rápido)
    /generate-plan --depth=detailed       — plano detalhado
    /generate-plan --focus=security       — foco em segurança
---

# Generate Plan — Gerar Plano de Engenharia Reversa

Ativa o **Plan Generator Agent**, que aplica o padrão de geração em etapas
do MiroFish para criar planos de análise executáveis.

## Como funciona

```
/generate-plan [target] [--depth=...] [--focus=...]
```

### Parâmetros

| Parâmetro | Opções | Padrão | Descrição |
|-----------|--------|--------|-----------|
| target | caminho | `.` | Diretório alvo |
| `--depth` | essential, complete, detailed | complete | Profundidade da análise |
| `--focus` | all, security, performance, architecture | all | Foco da análise |

## Pipeline (5 Stages)

```
/generate-plan
  Stage 1/5 🔍 SCOPE     → Tipo, stack, profundidade, foco
  Stage 2/5 📦 MODULES   → Módulos identificados e classificados
  Stage 3/5 📋 TASKS     → Tarefas por módulo
  Stage 4/5 🔗 DEPS      → Grafo de dependências
  Stage 5/5 📊 RESOURCES → Tokens, tempo, checkpoints
```

## Exemplo

```
$ /generate-plan --depth=detailed --focus=security

🔍 Stage 1/5: Projeto web (Python/Flask + Vue 3)
📦 Stage 2/5: 12 módulos identificados (5 core, 4 support, 3 config)
📋 Stage 3/5: 28 tarefas geradas
🔗 Stage 4/5: Pipeline principal (8 stages) + 6 tarefas paralelas
📊 Stage 5/5: ~1.2M tokens estimados, ~8 checkpoints sugeridos

📄 Plano salvo: _reversa_sdd/plan/security-audit-plan.md
```
