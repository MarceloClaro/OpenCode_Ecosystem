---
name: bugfix
description: "Skill do ecossistema OpenCode - bugfix"
---


name: bugfix
description: Protocolo sistemático de triage de bugs. Use ao receber report ou comportamento inesperado. Segue a sequência reproduzir→localizar→reduzir→corrigir→guardar→verificar.
disable-model-invocation: true
argument-hint: "[descrição do bug]"
---

---
name: bugfix
description: Protocolo sistemático de triage de bugs. Use ao receber report ou comportamento inesperado. Segue a sequência reproduzir→localizar→reduzir→corrigir→guardar→verificar.
disable-model-invocation: true
argument-hint: "[descrição do bug]"
---

# Skill: bugfix

**Quando usar:** Ao receber um report de bug ou comportamento inesperado. Substitui improvisação por um processo sistemático que evita corrigir sintoma em vez de causa raiz.

---

## Conteudo de Referencia

Para manter esta skill leve, dados densos foram movidos para arquivos de referencia:

- [`references/template-documentacao.md`](references/template-documentacao.md) — Template Documentacao

## Triage — execute nesta ordem, sem pular etapas

> *Detalhes em `references/etapas-triage.md`*
## Stop-the-line

Se em qualquer etapa acontecer algo inesperado:
1. **Pare** — não continue adicionando código
2. **Preserve** — salve logs, stack trace, estado atual
3. **Re-planeje** — volte ao passo 1 com a nova informação

---

## Após o fix

- Se o bug revelou uma lacuna de conhecimento: adicione entrada em `lessons.md`
- Se o fix exigiu uma decisão arquitetural: registre em `decisions.md`
- Se o padrão de fix for reutilizável em outros projetos: use a skill `/publish-pattern`

