<!-- SAIDA OBRIGATORIA: PORTUGUES BRASILEIRO FORMAL -->
<!-- Inspirado por: Engenharia de Software com Agentes Inteligentes (Sandeco, 2026), Cap. 1-2 -->

# Checklist Anti-Vibe-Coding por Tipo de Tarefa

> "O problema do vibe coding nao esta na IA. Esta na ausencia de processo." — Cap. 1

## Nova Funcionalidade

- [ ] Spec documentada: o que faz, para quem, com quais restricoes
- [ ] Criterios de aceitacao definidos (como verificar que funciona)
- [ ] Commit checkpoint antes de iniciar
- [ ] Branch `feat/` criada
- [ ] Testes escritos antes da implementacao (TDD)
- [ ] Codigo gerado revisado (git diff lido)
- [ ] Testes passam
- [ ] Nao introduziu regressao (testes antigos continuam passando)
- [ ] Merge + commit descritivo

## Correcao de Bug

- [ ] Bug reproduzido e documentado (como reproduzir, o que acontece, o que deveria acontecer)
- [ ] Commit checkpoint antes de iniciar
- [ ] Branch `fix/` criada
- [ ] Teste que reproduz o bug escrito PRIMEIRO (Red)
- [ ] Agente instruido a fazer o teste passar (Green)
- [ ] Verificar que a correcao nao quebrou outro comportamento
- [ ] Merge + commit descritivo

## Refatoracao

- [ ] Comportamento atual documentado (o que o codigo faz hoje)
- [ ] Testes atuais passam (linha de base)
- [ ] Commit checkpoint
- [ ] Branch `refactor/` ou worktree isolada
- [ ] Agente instruido com restricao: "mantenha o comportamento exato, apenas reorganize"
- [ ] Todos os testes existentes continuam passando
- [ ] Nenhum comportamento novo foi introduzido
- [ ] Merge ou descarte se nao melhorou

## Experimento / Proof of Concept

- [ ] Worktree isolada (NAO branch no repositorio principal)
- [ ] Sem expectativa de merge imediato
- [ ] Criterio de sucesso definido ("se X funcionar, vale a pena continuar")
- [ ] Criterio de descarte definido ("se Y nao funcionar em N horas, abandonar")
- [ ] Se funcionar: documentar aprendizados, decidir se merge
- [ ] Se nao funcionar: remover worktree, zero impacto

## Deploy / Entrega

- [ ] Todos os testes passam no ambiente de stage
- [ ] Testes de integracao cobrem os fluxos criticos
- [ ] Rollback documentado e testado
- [ ] Nao ha mudancas nao commitadas
- [ ] Deploy incremental (nao big bang)
- [ ] Monitoramento ativo nas primeiras horas
- [ ] Se algo quebrar: reverter IMEDIATAMENTE, diagnosticar depois

## Sinais de Alerta (Vibe Coding Detectado)

- [ ] Voce nao leu o diff antes de aceitar (3+ vezes na sessao)
- [ ] Nao ha spec, so prompts soltos ("faz um sistema de...")
- [ ] O agente esta "corrigindo" em loop ha mais de 3 iteracoes
- [ ] Codigo funciona local mas ninguem sabe por que
- [ ] Nao ha testes cobrindo o novo comportamento
- [ ] Branch principal foi modificada diretamente, sem branch isolada
- [ ] Voce nao consegue explicar a arquitetura do que foi gerado

Se 2+ sinais apareceram: PARE. Faca um commit do que funciona. Reavalie com spec.
