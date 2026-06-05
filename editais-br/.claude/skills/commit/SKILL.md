---
name: commit
description: Formata e valida mensagens de commit seguindo Conventional Commits. Use antes de qualquer git commit para garantir consistência.
disable-model-invocation: true
---

# Skill: commit

**Quando usar:** Ao formatar mensagens de commit.

---

## Formato

```
tipo(escopo): descrição imperativa em minúsculas

[corpo opcional: o porquê da mudança, não o como]

[rodapé: breaking changes ou issues fechadas]
```

## Tipos

| Tipo | Quando usar |
|------|-------------|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `refactor` | Mudança sem alterar comportamento externo |
| `docs` | Documentação |
| `test` | Testes |
| `chore` | Build, deps, config, contexto (`.claude/`) |
| `perf` | Melhoria de performance |

## Regras

- Imperativo: "add feature" e não "added feature"
- Máximo 72 caracteres na primeira linha
- Sem ponto final na descrição
- Escopo = módulo ou área afetada (ex: `auth`, `orders`, `db`)
- Para atualizações de contexto do projeto: `chore(context): update memory/specs`

## Exemplos

```
feat(auth): add JWT refresh token rotation

fix(orders): prevent race condition on concurrent updates

refactor(db): extract cursor pagination to shared util

chore(context): update lessons with Redis invalidation pattern

docs(api): add authentication endpoint examples
```
