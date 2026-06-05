# Spec: [FEATURE_SLUG]

<!--
  COMO USAR ESTE TEMPLATE:
  1. Copie para .claude/specs/[feature-slug].md
  2. Preencha os campos e remova os comentários
  3. Adicione ao INDEX.md com status "backlog"

  Ou use a skill spec-create para fazer isso automaticamente.
-->

**Status:** `backlog` | `in-progress` | `review` | `done` | `blocked`
**Slug:** `[project-slug]::[feature-slug]`
**Sprint:** [número ou nome]
**Criado em:** YYYY-MM-DD
**Última atualização:** YYYY-MM-DD

---

## Objetivo

<!-- O que esta feature entrega? Uma frase clara do valor gerado. -->
<!-- Exemplo: Autenticação JWT com refresh token para usuários B2B. -->

## Contexto técnico

<!-- Por que estamos fazendo isso? Qual problema concreto resolve? -->

## Fora do escopo

<!-- O que explicitamente NÃO será feito nesta spec. -->
<!-- Exemplo: OAuth social, 2FA — próxima sprint. -->

## Decisões técnicas

<!-- Formato: - [Decisão] — [Alternativas descartadas] — [Por quê esta] -->
<!-- Exemplo: - Refresh token em httpOnly cookie — localStorage descartado por risco XSS -->

## Dependências

- **Depende de:** [spec-slug ou "nenhuma"]
- **Bloqueia:** [spec-slug ou "nada"]

## Arquivos relevantes

<!-- Liste os arquivos principais que serão criados ou modificados -->
<!-- Exemplo:
- `src/auth/` — módulo principal
- `src/middleware/auth.ts` — validação de token
- `tests/auth.test.ts` — testes de integração
-->

## Critérios de aceite

<!-- O que deve ser verdade quando esta spec estiver done? Seja específico e verificável. -->
<!-- Exemplo:
- POST /auth/login retorna 200 com token válido dado credenciais corretas
- POST /auth/login retorna 401 com mensagem clara dado credenciais inválidas
- Token expira em 15min; refresh token em 7 dias
- Testes de integração cobrem fluxo feliz + expiração + credencial inválida
-->

## Tarefas

<!-- Checklist de implementação. Marque [x] ao concluir cada item. -->
- [ ] [Tarefa 1]
- [ ] [Tarefa 2]
- [ ] Testes escritos e passando
- [ ] PR criado e aprovado

---

## Como retomar este trabalho

> CRITICO: Preencha sempre que pausar. É o que permite qualquer dev ou sessão continuar sem briefing.

**Estado atual:** [o que já foi implementado]
**Próximo passo:** [exatamente o que fazer ao retomar — seja específico, com arquivo e linha se possível]
**Bloqueadores:** [o que impede o progresso, se houver — ou "nenhum"]

---

## Verificação

<!-- Preenchido ao concluir. Responde: como sabemos que funciona? -->
<!-- Exemplo:
- `pnpm test` — 24 testes passando, 0 falhas
- Testado manualmente: login, refresh, logout, token expirado
- PR #42 revisado e aprovado por [dev]
-->

## Notas de implementação

<!-- Contexto acumulado durante a implementação. -->
<!-- Decisões menores, gotchas, referências úteis, links. -->
<!-- Atualizado continuamente enquanto o trabalho avança. -->
