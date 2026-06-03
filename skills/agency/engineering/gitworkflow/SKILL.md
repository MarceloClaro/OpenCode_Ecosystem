---
category: agency
kind: python
version: "1.0.0"
---

# GitWorkflowEngine — Validador de Fluxo Git

Evolucao Round 14 (Agency Engineering). Motor de validacao de fluxo Git extraido do agente `engineering-git-workflow-master` do repositorio agency-agents.

## Proposito
Validar nomes de branches, mensagens de commit (Conventional Commits), atomicidade de commits e estrategias de merge.

## Uso
```python
from gitworkflow_engine import GitWorkflowEngine

engine = GitWorkflowEngine()
if engine.available:
    branch = engine.validate_branch_name("feat/SCRUM-123-login")
    commit = engine.validate_commit_message("fix(auth): resolve expiry")
    atomic = engine.detect_non_atomic(commits)
    merge = engine.analyze_merge_strategy(git_log)
```

## Integracao OpenCode
- **MCPs**: github, diff, sequential-thinking
- **Skills**: conventional-git, git-workflow-and-versioning
- **Categoria**: agency/engineering
