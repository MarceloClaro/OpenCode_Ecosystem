<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

---
description: Target a git worktree - /worktree <branch> or off
---

Call the `worktree` tool with:
- `target`: $ARGUMENTS
- `workdir`: the current working directory (use the directory you are working in)

If no arguments provided, call `worktree` with no target to show current status.

Example: `worktree(target: "feature-branch", workdir: "/path/to/repo")`
