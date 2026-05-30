---
name: spec-create
description: Cria spec formal para nova feature ou fase. Use ao iniciar qualquer trabalho de implementação não trivial.
disable-model-invocation: true
argument-hint: "[nome-da-feature]"
---

# Skill: spec-create

**Quando usar:** Ao iniciar uma nova feature, fase ou sprint. Pode ser invocada diretamente ou após o agente `planner` gerar um PRD aprovado.

---

## Protocolo

### Se invocada sem PRD pronto

Colete as informações mínimas antes de criar:

1. "Qual o nome e objetivo desta feature?" (1 frase clara)
2. "O que está fora do escopo?"
3. "Depende de alguma outra spec para começar?"
4. "Qual a prioridade? (alta / média / baixa)"

### Se invocada após PRD do planner

Use o conteúdo do PRD aprovado diretamente — não pergunte o que já foi respondido.

---

## Ações

1. **Gere o slug da feature** a partir do nome
   - Formato: `[tipo]-[nome]` em lowercase com hífens
   - Exemplos: `feature-auth`, `fix-payment-race`, `refactor-orders-module`

2. **Preencha o slug completo** no formato `[project-slug]::[feature-slug]`
   - Leia o `project` do front matter de `.claude/memory/MEMORY.md`

3. **Crie `.claude/specs/[feature-slug].md`**
   - Use o template `.claude/specs/_template.md` como base
   - Preencha todos os campos com as informações coletadas
   - Deixe "Como retomar" com o primeiro passo claro

4. **Atualize `.claude/specs/INDEX.md`**
   - Adicione na seção "Backlog" com slug, prioridade e dependências

5. **Confirme** os arquivos criados/atualizados ao usuário

---

## Resultado esperado

Uma spec nova em backlog, com contexto suficiente para qualquer sessão ou membro do time iniciar o trabalho sem precisar de briefing adicional.
