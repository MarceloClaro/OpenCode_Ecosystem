# Skills disponíveis

Invoque diretamente com `/nome-da-skill` ou deixe Claude invocar automaticamente quando relevante (exceto quando `disable-model-invocation: true`).

| Skill | Diretório | Quando usar |
|-------|-----------|-------------|
| `/project-init` | `project-init/` | Primeira sessão — projeto novo em branco |
| `/project-seal` | `project-seal/` | Após project-init + primeira spec — commita e publica o setup |
| `/project-adopt` | `project-adopt/` | Projeto existente recebendo a estrutura pela primeira vez |
| `/spec-create` | `spec-create/` | Iniciar nova feature ou fase |
| `/bugfix` | `bugfix/` | Report de bug — triage sistemático até fix verificado |
| `/pr-review` | `pr-review/` | Antes de abrir ou revisar um PR |
| `/commit` | `commit/` | Formatar e validar mensagem de commit |
| `/deploy` | `deploy/` | Antes de qualquer deploy |
| `/publish-pattern` | `publish-pattern/` | Publicar padrão reutilizável no global-index |

## Estrutura

Cada skill é um diretório com `SKILL.md` como entrypoint:

```
.claude/skills/<nome-da-skill>/
├── SKILL.md        ← instruções + frontmatter YAML (obrigatório)
├── examples/       ← exemplos de output (opcional)
└── scripts/        ← scripts que Claude pode executar (opcional)
```

## Campos do frontmatter (em SKILL.md)

| Campo | Descrição |
|-------|-----------|
| `name` | Nome do slash-command (ex: `deploy` → `/deploy`) |
| `description` | O que a skill faz — Claude usa isso para decidir quando aplicar |
| `disable-model-invocation` | `true` = só você pode invocar (Claude não dispara automaticamente) |
| `allowed-tools` | Ferramentas que Claude pode usar sem pedir permissão quando a skill está ativa |
| `model` | Override de modelo para esta skill |
| `context: fork` | Roda em contexto isolado de subagente |
| `argument-hint` | Dica exibida no autocomplete (ex: `[nome-da-feature]`) |

## Como invocar

```
/project-init
/spec-create user-authentication
/bugfix checkout page crashes on mobile
/deploy staging
```

## Como adicionar uma nova skill

```bash
mkdir -p .claude/skills/minha-skill
# Crie SKILL.md com frontmatter + instruções
```

Referência: https://code.claude.com/docs/en/skills
