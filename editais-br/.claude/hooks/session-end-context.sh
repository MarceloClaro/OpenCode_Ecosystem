#!/usr/bin/env bash
# Hook: SessionEnd — auto-commita arquivos de contexto (memory + specs) ao fim da sessão
#
# ATIVAR: Adicione ao .claude/settings.local.json (pessoal, gitignored):
#
#   {
#     "hooks": {
#       "SessionEnd": [{
#         "hooks": [{
#           "type": "command",
#           "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/session-end-context.sh",
#           "statusMessage": "Salvando contexto da sessão..."
#         }]
#       }]
#     }
#   }

# Executa apenas dentro de um repo git
git rev-parse --git-dir > /dev/null 2>&1 || exit 0

cd "$(git rev-parse --show-toplevel)" || exit 0

# Verifica se há mudanças não commitadas nos diretórios de contexto
CONTEXT_CHANGED=$(git status --porcelain .claude/memory/ .claude/specs/ 2>/dev/null)
[[ -z "$CONTEXT_CHANGED" ]] && exit 0

git add .claude/memory/ .claude/specs/ 2>/dev/null || exit 0

# Nada staged após o add (ex: tudo ignorado)
git diff --cached --quiet && exit 0

git commit -m "chore(context): auto-update memory and specs [session-end]" 2>/dev/null
exit 0
