# Agentes disponíveis

Invoque explicitamente pelo nome. Agentes rodam em seu próprio contexto com ferramentas e permissões isoladas.

| Agente | Arquivo | Quando usar |
|--------|---------|-------------|
| `code-reviewer` | `code-reviewer.md` | Revisar código sem modificar nada — worktree isolada |
| `researcher` | `researcher.md` | Explorar repositórios grandes, mapear estrutura — worktree isolada, acumula memória |
| `planner` | `planner.md` | Gerar PRDs e planos de implementação antes de qualquer código |

## Como invocar

```
Use o agente code-reviewer para analisar o módulo de auth
Use o agente researcher para mapear como o sistema de pagamentos funciona
Use o agente planner para criar uma spec para a feature de relatórios
```

## Campos principais do frontmatter

| Campo | Descrição |
|-------|-----------|
| `description` | **Crítico** — o orquestrador lê apenas isso para decidir se delega. Use palavras-chave fortes e "Use proativamente..." |
| `tools` | Ferramentas permitidas (allowlist). Herda todas se omitido |
| `model` | `sonnet`, `opus`, `haiku`, ou `inherit` |
| `isolation: worktree` | Roda em worktree git temporária — seguro para agentes read-heavy |
| `memory: project` | Memória persistente em `.claude/agent-memory/<nome>/` — commitada no git, compartilhada com o time |
| `memory: local` | Memória persistente em `.claude/agent-memory-local/<nome>/` — gitignored, local da máquina |

## Escopos de memória

| Escopo | Local | Commitado no git? |
|--------|-------|-------------------|
| `user` | `~/.claude/agent-memory/<nome>/` | Não |
| `project` | `.claude/agent-memory/<nome>/` | Sim — compartilhado com o time |
| `local` | `.claude/agent-memory-local/<nome>/` | Não — gitignored |

## Adicionando um novo agente

Crie `.claude/agents/<nome>.md` com frontmatter YAML + corpo do system prompt.

Escreva uma `description` forte — é a única coisa que o orquestrador lê para decidir a delegação.
Use "Use proativamente" se quiser que Claude delegue automaticamente.

Referência: https://code.claude.com/docs/en/sub-agents
