# ==============================================================================
# .bash_aliases — Aliases e funcoes do OpenCode Ecosystem
# Criador: Prof. Marcelo Claro Laranjeira
# ==============================================================================

# --- OpenCode CLI: atalhos ---------------------------------------------------

# oc: inicia OpenCode TUI (modo interativo padrao)
alias oc='opencode'

# ocpaste: cola texto da area de transferencia no OpenCode (bypass raw mode)
alias ocpaste='/mnt/c/Users/marce/Documents/OpenCode_Ecosystem/scripts/opencode-paste.sh'

# ocrun: executa opencode run com modelo e agente padrao
alias ocrun='opencode run --model mimo/mimo-v2.5-pro --agent marceloclaro'

# ocruni: executa opencode run em modo interativo (split-footer, aceita colagem)
alias ocruni='opencode run --model mimo/mimo-v2.5-pro --agent marceloclaro --interactive'

# ocweb: abre interface web do OpenCode
alias ocweb='opencode web --port 4096 --hostname 127.0.0.1'

# ocattach: conecta a sessao existente
alias ocattach='opencode attach'

# ocdebug: ferramentas de diagnostico
alias ocdebug='opencode debug'

# ocstats: estatisticas de uso
alias ocstats='opencode stats'

# ocup: atualiza opencode
alias ocup='opencode upgrade'

# --- OpenCode Ecosystem: atalhos ---------------------------------------------

ECO_DIR="/mnt/c/Users/marce/Documents/OpenCode_Ecosystem"

# eco: abre o diretorio do ecossistema
alias eco="cd '$ECO_DIR'"

# eco-painel: abre o painel de controle
alias eco-painel="bash '$ECO_DIR/scripts/console.sh'"

# eco-test: executa suite de testes
alias eco-test="bash '$ECO_DIR/tests/test_environment.sh'"

# eco-status: mostra status do ecossistema
alias eco-status="git -C '$ECO_DIR' log --oneline -5 && echo '---' && git -C '$ECO_DIR' status --short"

# eco-push: commit + push rapido
eco-push() {
    cd "$ECO_DIR"
    git add .
    git commit -m "${1:-Auto-commit: $(date '+%Y-%m-%d %H:%M')}" && git push
}

# eco-pull: pull rapido
alias eco-pull="cd '$ECO_DIR' && git pull"

# --- Funcao: ocpp (OpenCode Paste com preview) -------------------------------
# Uso: ocpp                      # cola clipboard
#      ocpp <texto>              # envia texto como argumento
#      cat arquivo | ocpp        # envia via pipe
ocpp() {
    if [ $# -gt 0 ]; then
        # Texto passado como argumento
        opencode run --model mimo/mimo-v2.5-pro --agent marceloclaro "$*"
    elif [ ! -t 0 ]; then
        # Dados via pipe
        local tmpfile
        tmpfile=$(mktemp /tmp/ocpaste-XXXXXX.txt)
        cat > "$tmpfile"
        echo -e "\033[1;32mRecebido via pipe. Enviando para OpenCode...\033[0m"
        opencode run --model mimo/mimo-v2.5-pro --agent marceloclaro -f "$tmpfile"
        rm -f "$tmpfile"
    else
        # Le da area de transferencia Windows
        if command -v powershell.exe &>/dev/null; then
            local tmpfile
            tmpfile=$(mktemp /tmp/ocpaste-XXXXXX.txt)
            echo -e "\033[1;33mLendo da area de transferencia Windows...\033[0m"
            powershell.exe -Command "Get-Clipboard" 2>/dev/null | tr -d '\r' > "$tmpfile"
            if [ -s "$tmpfile" ]; then
                echo -e "\033[1;32mEncontrado texto. Enviando para OpenCode...\033[0m"
                opencode run --model mimo/mimo-v2.5-pro --agent marceloclaro -f "$tmpfile"
            else
                echo -e "\033[1;31mArea de transferencia vazia. Copie o texto primeiro.\033[0m"
                echo "Dica: use 'ocpp texto' ou 'echo texto | ocpp'"
            fi
            rm -f "$tmpfile"
        else
            echo -e "\033[1;31mPowerShell nao encontrado. Use: echo texto | ocpp\033[0m"
        fi
    fi
}

# --- Atalhos de produtividade ------------------------------------------------

alias c='clear'
alias h='history'
alias ..='cd ..'
alias ...='cd ../..'

# --- Git conveniencia --------------------------------------------------------

alias gs='git status --short'
alias gl='git log --oneline --graph -20'
alias gd='git diff'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
