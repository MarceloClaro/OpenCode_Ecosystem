<!-- SAIDA OBRIGATORIA: PORTUGUES BRASILEIRO FORMAL -->
<!-- Toda resposta ao usuario DEVE ser em portugues do Brasil formal. -->
<!-- Contexto em chines para eficiencia de tokens. Responda em PT-BR formal. -->
<!-- Inspirado por: Engenharia de Software com Agentes Inteligentes (Sandeco, 2026) -->

---
name: ai-engineering-harness
description: Agent Harness: commit-antes-de-agent, worktree isolada, SDD+TDD obrigatorio. O freio que transforma velocidade IA em engenharia sustentavel.
version: 1.0.0
author: ecosystem
category: superpowers
inspired_by: Engenharia de Software com Agentes Inteligentes (Sandeco) / deer-flow 2.0
compatibility: deepseek-v4-pro
created_at: 2026-05-27
based_on_chapters: Cap.1-6 do livro "Engenharia de Software com Agentes Inteligentes"
---

# AI Engineering Harness

> "IA amplifica o que ja existe. Se existe metodo, amplifica qualidade. Se existe caos, amplifica caos." — Cap. 2

O Agent Harness e o conjunto de regras, hooks e configuracoes que transforma um agente generico em um colaborador especializado no seu processo. Sem harness, voce esta fazendo vibe coding. Com harness, voce esta fazendo AI Engineering.

## Regra Zero: Nunca pule o Git

**Antes de qualquer mudanca significativa solicitada a um agente, crie um ponto de restauracao.**

```
fluxo seguro:
  git add -A && git commit -m "checkpoint: antes de [acao]"
  > instruir agente
  > avaliar resultado
  se funcionou: git commit -m "feat: [descricao]"
  se quebrou:   git restore .  (ou git revert se ja commitou)
```

Sem Git, o agente nao tem memoria do que o codigo era antes. Sem checkpoint, voce nao tem como voltar. Velocidade sem reversibilidade e carro sem freio.

## Regra 1: Worktree para experimentos de risco

Para qualquer mudanca que envolva refatoracao grande, nova arquitetura ou abordagem incerta:

```
git worktree add -b feat/experimento ../projeto-exp
# abrir agente na pasta ../projeto-exp
# experimentar livremente
# se funcionar: merge
# se nao funcionar: git worktree remove ../projeto-exp
```

O worktree isola completamente o experimento. O codigo principal continua intocado, utilizavel e seguro. Voce nao precisa de confianca cega no agente. Precisa de isolamento.

## Regra 2: Spec antes de codigo (SDD)

Nunca instrua um agente a "criar um sistema de login". Instrua-o com uma especificacao:

```
# Spec minima antes de codificar:
- O que o sistema deve fazer? (comportamento esperado)
- Quem vai usar? (perfis de usuario)
- Quais as restricoes? (seguranca, performance, escala)
- Quais os casos de borda? (entrada invalida, timeout, conflito)
- Como verificar que funciona? (criterios de aceitacao)
```

O agente implementa o que foi especificado. Se a spec estava errada, o agente implementa o erro com eficiencia impecavel. Velocidade na direcao errada nao e produtividade.

## Regra 3: Teste como contrato da spec

- Escreva o teste antes do codigo (TDD classico)
- O teste e a traducao executavel da spec: se o teste passa, a spec foi atendida
- Peca ao agente para gerar testes para cada criterio de aceitacao
- Nunca aceite codigo sem teste que cubra o comportamento esperado

Piramide de testes na era dos agentes:
- Unitarios: o agente gera para cada funcao/metodo (base da piramide)
- Integracao: o agente gera para cada endpoint/fluxo (meio da piramide)
- E2E: humano revisa cenarios criticos (topo da piramide)

## Regra 4: Revisao humana obrigatoria

O agente sugere. O humano decide. Regras:
- Leia o diff antes de aceitar (git diff)
- Rode os testes (pytest / npm test / cargo test)
- Questione: "isso faz sentido para o contexto real do negocio?"
- Questione: "alguem consegue manter isso daqui a 6 meses?"
- Se nao entendeu o que o agente fez, nao aceite

## Regra 5: Branches com convencao semantica

Use prefixos que o agente e o time entendem:
- `feat/` — nova funcionalidade
- `fix/` — correcao de bug
- `refactor/` — refatoracao sem mudanca de comportamento
- `chore/` — infraestrutura, configuracao
- `spec/` — documentacao de especificacao

## Checklist Anti-Vibe-Coding

Antes de cada interacao significativa com o agente, verifique:

- [ ] Fiz commit do estado atual? (ponto de restauracao)
- [ ] Criei branch isolada para esta mudanca?
- [ ] Tenho spec minima documentada (o que, para quem, restricoes)?
- [ ] Se for experimento arriscado, usei worktree isolada?
- [ ] O agente recebeu contexto suficiente (regras de negocio, dados reais)?
- [ ] Revisei o diff antes de aceitar?
- [ ] Rodei os testes depois da mudanca?
- [ ] Se algo quebrou, reverti imediatamente (nao pedi pro agente "corrigir" em loop)?

Se marcou tudo, esta fazendo AI Engineering. Se pulou metade, esta fazendo vibe coding.

## O que NUNCA fazer

- Pedir "cria um sistema de [X]" sem spec previa
- Aceitar codigo do agente sem ler o diff
- Deixar o agente "corrigir" em loop sem checkpoint intermediario
- Confundir "funcionou local" com "pronto para producao"
- Usar "somos ageis" como desculpa para pular testes e documentacao
- Assumir que o agente sabe as regras de negocio nao documentadas

## Workflow Completo

```
1. SPEC    → Documentar requisitos minimos (o que, quem, restricoes)
2. COMMIT  → git commit do estado atual (ponto de restauracao)
3. BRANCH  → Criar branch isolada ou worktree
4. AGENT   → Instruir agente com a spec + contexto
5. REVIEW  → Ler diff, questionar, entender
6. TEST    → Rodar testes, verificar bordas
7. DECIDE  → Se ok: merge + commit. Se nao: restore/revert
8. REPEAT  → Proximo incremento
```

## Integracao

| Componente | Tipo | Conexao |
|-----------|------|---------|
| using-git-worktrees | Skill | Isolamento de experimentos |
| test-driven-development | Skill | Teste como contrato |
| subagent-driven-development | Skill | Delegacao segura |
| verification-before-completion | Skill | Validacao final |
| decisionnode | MCP | Registro de decisoes |
| memory | MCP | Contexto persistente |
| sequential-thinking | MCP | Raciocinio estruturado |

## Referencias

| Arquivo | Conteudo |
|---------|----------|
| references/anti-vibe-coding-checklist.md | Checklist detalhada por tipo de tarefa |
| references/spec-template-minima.md | Template de spec minima obrigatoria |
