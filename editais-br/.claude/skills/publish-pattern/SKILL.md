---
name: publish-pattern
description: Publica padrões reutilizáveis no global-index do claude-memories. Use quando uma solução se provar genuinamente reutilizável em outros projetos.
disable-model-invocation: true
---

# Skill: publish-pattern

**Quando usar:** Quando uma solução se provar genuinamente reutilizável em outros projetos. Use com critério — só o que realmente economizaria tempo ou evitaria erros em um contexto diferente.

---

## Critérios para publicar

Publique se a solução:
- Resolveu um problema não óbvio
- É independente do contexto específico deste projeto
- Economizaria tempo ou evitaria erros em outro projeto

Não publique:
- Soluções muito específicas do domínio do negócio
- Workarounds temporários
- O que já está no global-index

---

## Formato da entrada

```markdown
### [Nome do Padrão] — [data]
**Origem:** `[project-slug]`
**Problema:** [o que resolvia — 1 frase]
**Solução:** [a abordagem — 2-3 frases]
**Por que funciona:** [raciocínio curto]
**Reutilizável quando:** [condições ou contexto]
**Detalhes:** [link para o arquivo no repo de origem]
```

---

## Ações

1. Leia `.claude/memory/MEMORY.md` para confirmar o `project-slug`
2. Acesse `claude-memories/global-index.md`
3. Adicione a entrada na seção de categoria correspondente
4. Commit no `claude-memories`: `docs(global-index): add [nome] from [project-slug]`
5. Registre também em `.claude/memory/patterns.md` do projeto atual

---

## Exemplo de entrada publicada

```markdown
### Cursor Pagination em tabelas grandes — 2026-03-04
**Origem:** `minha-api`
**Problema:** Offset pagination causava degradação de performance com >50k registros
**Solução:** Cursor baseado em `(created_at, id)` com índice composto — evita full scan
**Por que funciona:** O banco filtra a partir de um ponto fixo em vez de pular N linhas
**Reutilizável quando:** Qualquer endpoint com paginação em tabela de alto volume
**Detalhes:** ecodelearn/minha-api → .claude/memory/lessons.md#cursor-pagination
```
