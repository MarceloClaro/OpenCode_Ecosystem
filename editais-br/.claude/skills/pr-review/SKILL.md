---
name: pr-review
description: Checklist para abrir ou revisar pull request. Valida qualidade do código, spec, testes e segurança antes de abrir ou aprovar qualquer PR.
disable-model-invocation: true
---

# Skill: pr-review

**Quando usar:** Antes de abrir um PR ou ao revisar o PR de outra pessoa.

---

## Checklist — abertura de PR

### Código
- [ ] Solução mais simples possível para o problema?
- [ ] Nenhum erro de `lessons.md` repetido?
- [ ] Sem código morto, logs de debug ou comentários temporários
- [ ] Nomes autoexplicativos — sem abreviações obscuras

### Spec
- [ ] Todas as tarefas da spec marcadas como concluídas?
- [ ] Spec atualizada com status `review`?
- [ ] `INDEX.md` atualizado?

### Testes
- [ ] Casos feliz e de erro cobertos?
- [ ] Nenhum teste comentado ou skipado sem justificativa?

### Segurança
- [ ] Nenhuma credencial ou secret hardcoded?
- [ ] Inputs de usuário validados nas bordas do sistema?

### O PR em si
- [ ] Título no formato `tipo(escopo): descrição` — ex: `feat(auth): add JWT refresh`
- [ ] Descrição: O QUÊ mudou + POR QUÊ (não como)
- [ ] PR atômico — uma mudança lógica por PR

---

## Checklist — revisão de PR alheio

- [ ] Objetivo da mudança está claro?
- [ ] Abordagem consistente com `decisions.md`?
- [ ] Conflita com algo em `lessons.md`?
- [ ] O código seria compreensível em 6 meses?
- [ ] Algo aprendido nesta revisão merece ir para `lessons.md`?

---

## Após aprovação

Mova a spec correspondente para status `done` e atualize o `INDEX.md` com a data e link do PR.
