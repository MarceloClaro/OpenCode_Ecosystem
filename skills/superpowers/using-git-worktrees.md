<!-- SAIDA OBRIGATORIA: PORTUGUES BRASILEIRO FORMAL -->
<!-- Inspirado por: Engenharia de Software com Agentes Inteligentes (Sandeco, 2026), Cap. 3 -->

---
name: using-git-worktrees
description: Git Worktrees como rede de seguranca para agentes inteligentes. Isolamento total de experimentos, branches paralelas, commit-before-AI como disciplina obrigatoria.
version: 2.0.0
author: ecosystem
category: superpowers
inspired_by: Engenharia de Software com Agentes Inteligentes (Sandeco) / deer-flow 2.0 / opencode
compatibility: deepseek-v4-pro
migrated_at: 2026-05-07 06:10:30
updated_at: 2026-05-27
based_on_chapter: Cap. 3 - Git: o Ctrl+Z que a IA nao te da
---

# Using Git Worktrees + Safety Protocol

> "Sem Git, o agente refatora, erra e entra em loop infinito sem nenhuma forma de voltar. Com Git, cada commit e um ponto de restauracao recuperavel em segundos." — Cap. 3

## Protocolo de Seguranca: Commit + Worktree

O ciclo seguro de trabalho com agentes inteligentes:

```
1. COMMIT checkpoint (estado atual funcionando)
   git add -A && git commit -m "checkpoint: antes de [acao do agente]"

2. WORKTREE ou BRANCH (isolar experimento)
   git worktree add -b feat/experimento ../projeto-exp
   OU
   git checkout -b feat/experimento

3. AGENTE (instruir, gerar, iterar)
   # abrir agente na pasta isolada
   # experimentar livremente

4. AVALIAR (testar, revisar diff)
   git diff  # ler TUDO que foi modificado
   pytest    # ou equivalente

5. DECIDIR
   Se funcionou: git merge feat/experimento
   Se quebrou:   git restore .  (se nao commitou)
                 git revert     (se commitou)
                 git worktree remove ../projeto-exp  (se worktree)
```

## Regra de Ouro: Nunca pule o checkpoint

O agente inteligente NAO TEM MEMORIA do que o codigo era antes. Ele opera sobre o estado atual do arquivo. Para o agente, o arquivo e sempre o que esta na tela agora. So o Git preserva o historico. Sem commit antes de cada mudanca significativa, voce esta pilotando sem paraquedas.

```
🚫 NUNCA:
  - Pedir refatoracao grande sem commit previo
  - Deixar o agente "corrigir" em loop (cada correcao piora)
  - Trabalhar diretamente na main

✅ SEMPRE:
  - Commit antes de cada instrucao significativa ao agente
  - Branch ou worktree isolada para experimentos
  - Se errar: restaurar, nao insistir
```

## Worktree: Isolamento Total

Worktree e superior a branch para experimentos arriscados porque:

| Aspecto | Branch | Worktree |
|---------|--------|----------|
| Isolamento | Mesma pasta, precisa alternar | Pasta separada, paralelo real |
| Risco | Stash/checkout podem perder trabalho | Zero interferencia |
| Paralelismo | Nao (uma branch ativa por vez) | Sim (duas pastas, dois processos) |
| Limpeza | `git branch -d` | `git worktree remove` |

### Comandos Essenciais

```bash
# Criar worktree isolada para experimento
git worktree add -b feat/experimento-agente ../projeto-exp

# Listar worktrees ativos
git worktree list

# Trabalhar na worktree (abrir agente nesta pasta)
cd ../projeto-exp
# ... experimentar com agente ...

# Se funcionou: voltar ao repo original e fazer merge
cd ../projeto-original
git merge feat/experimento-agente

# Remover worktree (se nao funcionou ou ja mergeou)
git worktree remove ../projeto-exp
```

### Fluxo com Claude Code / OpenCode

```bash
# No repositorio principal
git add -A && git commit -m "checkpoint: estado estavel"
git worktree add -b feat/nova-feature ../feature-worktree

# Abrir agente NA WORKTREE (pasta separada)
cd ../feature-worktree
# Agente trabalha aqui, livremente

# Enquanto isso, no repositorio principal, voce continua normalmente
cd ../projeto-original
# Seu trabalho nao e afetado pelo agente
```

## Branches: Convencao Semantica

Use prefixos que qualquer pessoa (ou agente) entende:

```
feat/     → nova funcionalidade
fix/      → correcao de bug
refactor/ → reorganizacao sem mudanca de comportamento
chore/    → infraestrutura, config, dependencias
spec/     → documentacao de especificacao
exp/      → experimento descartavel
```

## Ciclo de Vida de uma Tarefa com Agente

```
git checkout -b feat/nova-funcionalidade
git add -A && git commit -m "checkpoint: inicio feat/nova-funcionalidade"
# ... agente trabalha ...
git diff          # revisar TUDO
pytest            # rodar testes
git add -A && git commit -m "feat: implementa [descricao]"
git checkout main
git merge feat/nova-funcionalidade
git branch -d feat/nova-funcionalidade
```

## Recuperacao de Desastres

```
# Agente quebrou tudo? Volte ao ultimo checkpoint:
git restore .

# Agente fez commit errado? Reverta:
git revert <commit-hash>

# Agente gerou lixo em arquivo especifico? Restaure so aquele:
git restore --source=<commit-bom> arquivo.py

# Precisa ver como estava antes? Inspecione sem alterar:
git switch --detach <commit-antigo>
# ... inspecionar ...
git switch main  # voltar
```

## Integracao

| Componente | Tipo | Conexao |
|-----------|------|---------|
| ai-engineering-harness | Skill | Framework completo de disciplina |
| maintenance-first | Skill | Qualidade do codigo gerado |
| subagent-driven-development | Skill | Delegacao segura |
| decisionnode | MCP | Registro de decisoes |
| memory | MCP | Contexto persistente |
