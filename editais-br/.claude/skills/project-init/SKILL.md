---
name: project-init
description: "Skill do ecossistema OpenCode - project-init"
---


name: project-init
description: Onboarding da primeira sessão para projetos novos. Execute automaticamente quando MEMORY.md não tiver contexto. Entrevista o desenvolvedor e configura todos os arquivos de memória.
disable-model-invocation: true
---

---
name: project-init
description: Onboarding da primeira sessão para projetos novos. Execute automaticamente quando MEMORY.md não tiver contexto. Entrevista o desenvolvedor e configura todos os arquivos de memória.
disable-model-invocation: true
---

# Skill: project-init

**Quando executar:** Automaticamente quando `.claude/memory/MEMORY.md` não tiver contexto preenchido. Pode ser invocada manualmente com `/project-init`.

**Objetivo:** Entrevistar o desenvolvedor, configurar o projeto e popular todos os arquivos de memória para que qualquer sessão futura comece com contexto completo — sem re-explicar nada.

---



## Conteudo de Referencia

Para manter esta skill leve, dados densos foram movidos para arquivos de referencia:

- [`references/protocolo-entrevista.md`](references/protocolo-entrevista.md) — Protocolo Entrevista

> *Detalhes de "Ações após a entrevista" em `references/`*



## Exemplo de MEMORY.md gerado corretamente

```markdown
---
project: minha-api
repo: ecodelearn/minha-api
stack: Node.js + Fastify + PostgreSQL + Redis
language: pt-br
---

# minha-api — Memória do Projeto



## Contexto
API REST para gestão de pedidos B2B. Processamento de ~50k req/dia.



## Stack
Node.js + Fastify + PostgreSQL + Redis. Deploy na Railway. PNPM obrigatório.


