---
name: project-adopt
description: "Skill do ecossistema OpenCode - project-adopt"
---


name: project-adopt
description: Onboarding para projetos existentes que recebem a estrutura Claude Code pela primeira vez. Descobre convenções do codebase antes de perguntar qualquer coisa.
disable-model-invocation: true
---

---
name: project-adopt
description: Onboarding para projetos existentes que recebem a estrutura Claude Code pela primeira vez. Descobre convenções do codebase antes de perguntar qualquer coisa.
disable-model-invocation: true
---

# Skill: project-adopt

**Quando executar:** Em projetos existentes que estão recebendo a estrutura Claude Code pela primeira vez. Invocada com `/project-adopt`.

**Diferença do `project-init`:**
- `project-init` → define convenções em projeto em branco
- `project-adopt` → descobre convenções que já existem no código — o codebase é a fonte de verdade

---



## Conteudo de Referencia

Para manter esta skill leve, dados densos foram movidos para arquivos de referencia:

- [`references/exemplo-memory.md`](references/exemplo-memory.md) — Exemplo Memory

> *Detalhes de "Protocolo" em `references/`*



## O que NÃO fazer

- Não redefinir convenções que já existem no código — descubra e siga
- Não criar specs para todo o histórico do projeto — só para o que está ativo
- Não sobrescrever um `CLAUDE.md` existente sem mostrar o diff ao usuário primeiro

---



## Contexto
Toolkit de hardening e auditoria de segurança para Linux.
28 scripts bash (~9.680 linhas). TUI interativa com Gum.



## Stack
Bash. Gum para TUI. AppArmor (perfis), Firejail (sandboxes).
Deploy: scripts locais. Distro-aware via distro.conf por módulo.


