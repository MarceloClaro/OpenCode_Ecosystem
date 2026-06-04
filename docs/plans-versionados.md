# Plans Versionados — Protocolo de Ciclo de Vida

## O que é

`PLANS.md` é o artifact rastreável de ciclo de vida de planos. Cada `/plan` gera um plano detalhado em `thoughts/plans/{name}.md` E sincroniza um resumo versionado em `PLANS.md`.

## Estrutura

- **`PLANS.md`** (raiz do repositório): plano ativo — progresso, decisões, bloqueadores, contexto crítico
- **`thoughts/plans/{nome}.md`**: plano detalhado gerado por `/plan`
- **`thoughts/plans/archive/PLANS-v{n}-{YYYY-MM-DD}.md`**: snapshot versionado do `PLANS.md` anterior

## Ciclo de Vida

### Criação

1. `/plan` gera plano detalhado em `thoughts/plans/{nome}.md`
2. Sincroniza resumo para `PLANS.md` com:
   - Meta (criado, atualizado, status, versão)
   - Goal
   - Progress (Done / In Progress / Blocked)
   - Key Decisions
   - Blockers
   - Next Steps
   - Critical Context
   - Relevant Files

### Atualização

1. Ao marcar tarefa `[x]`, atualizar `PLANS.md` → Progress
2. Ao tomar decisão, adicionar em Key Decisions com rationale
3. Ao encontrar bloqueador, registrar em Blockers
4. Incrementar versão (`v2`, `v3`, ...) e atualizar campo `Atualizado`

### Archive (antes de overwrite)

Antes de sobrescrever `PLANS.md` com novo plano:

1. Copiar `PLANS.md` → `thoughts/plans/archive/PLANS-v{n}-{YYYY-MM-DD}.md`
2. Só então escrever novo conteúdo

### Consulta por Agentes

**TODO agente DEVE** ao iniciar uma sessão:

1. Ler `PLANS.md` se existir
2. Identificar fase/tarefa `← CURRENT`
3. Verificar bloqueadores que afetam seu trabalho
4. Não iniciar trabalho novo sem consultar estado atual

## State Machine

Herda integralmente as regras de `plan-protocol/reference/state-machine.md`:

- Apenas UMA fase `[IN PROGRESS]` por vez
- Apenas UMA tarefa com `← CURRENT`
- Mover marcador imediatamente ao iniciar trabalho
- Marcar `[x]` na conclusão
- Transições: `not-started → in-progress → complete | blocked`

## Convenções de Formato

### Meta
```
- Criado: YYYY-MM-DD
- Atualizado: YYYY-MM-DD
- Status: not-started | in-progress | complete | blocked
- Versão: v1
```

### Progress
```
### Done
- [x] Tarefa concluída

### In Progress
- [ ] Tarefa em andamento ← CURRENT

### Blocked
- [ ] Tarefa bloqueada (bloqueador: motivo)
```

### Key Decisions
```
| Decisão | Rationale | Data |
|---------|-----------|------|
```

### Blockers
```
| Blocker | Impacto | Status | Resolução |
|---------|---------|--------|-----------|
```
