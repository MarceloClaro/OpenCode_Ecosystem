#!/usr/bin/env bash
# ==============================================================================
# opencode-paste.sh — Wrapper para colar texto no OpenCode CLI
# ==============================================================================
# Criador: Prof. Marcelo Claro Laranjeira (https://github.com/MarceloClaro)
#
# PROLEMA: O modo TUI do OpenCode CLI (modo raw) intercepta Ctrl+V e outras
# teclas de atalho, impedindo colagem de texto longo, código ou prompts
# multi-linha diretamente no terminal.
#
# SOLUCAO: Este wrapper usa `opencode run --file` (que NAO usa raw mode)
# para enviar o texto colado como arquivo temporario, contornando a limitacao
# do TUI e mantendo toda a capacidade de processamento do ecossistema.
#
# USO:
#   opencode-paste                  # Cola conteudo da area de transferencia
#   opencode-paste -f arquivo.txt   # Envia arquivo como prompt
#   echo "texto" | opencode-paste   # Envia texto via pipe
#   opencode-paste -i               # Modo interativo com colagem suportada
#
# Depedencias:
#   - PowerShell (Get-Clipboard) para leitura da area de transferencia Windows
#   - OpenCode CLI (opencode) instalado em /home/marcelo/.opencode/bin/opencode
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ECO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMP_DIR="/tmp/opencode-paste"
OC_BIN="${OPENCODE_BIN:-/home/marcelo/.opencode/bin/opencode}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

mkdir -p "$TEMP_DIR"

# --- Funcoes -----------------------------------------------------------------

usage() {
    echo -e "${CYAN}opencode-paste${NC} — Colar texto no OpenCode CLI (bypass raw mode)"
    echo ""
    echo "USO:"
    echo "  $0                         Cola conteudo da area de transferencia Windows"
    echo "  $0 -f <arquivo>            Envia arquivo como prompt"
    echo "  $0 -i                      Modo interativo (digitar/digitar + colar)"
    echo "  $0 -h                      Mostra esta ajuda"
    echo ""
    echo "PIPE:"
    echo "  echo 'texto' | $0          Envia texto via pipe (stdin)"
    echo "  cat arquivo.txt | $0       Envia conteudo de arquivo via pipe"
    echo ""
    echo "EXEMPLOS:"
    echo "  $0                         # Cola o que estiver na area de transf."
    echo "  $0 -f relatorio.md         # Envia relatorio.md como prompt"
    echo "  $0 -i                      # Abre editor para digitar/colar"
    echo "  pbpaste | $0               # Alternativa: pipe do clipboard"
    echo ""
    echo "DICAS:"
    echo "  Use 'opencode run -i' como alternativa mais leve ao TUI padrao."
    echo "  Use 'opencode web' para interface grafica com colagem garantida."
    exit 0
}

read_clipboard() {
    # Le da area de transferencia Windows via PowerShell
    if command -v powershell.exe &>/dev/null; then
        powershell.exe -Command "Get-Clipboard" 2>/dev/null | tr -d '\r' || true
    elif command -v xclip &>/dev/null; then
        xclip -o -selection clipboard 2>/dev/null || true
    elif command -v wl-paste &>/dev/null; then
        wl-paste 2>/dev/null || true
    else
        echo ""  # fallback: vazio
    fi
}

interactive_mode() {
    local tmpfile
    tmpfile=$(mktemp "$TEMP_DIR/prompt-XXXXXX.md")

    echo -e "${YELLOW}=== MODO INTERATIVO COM COLAGEM ===${NC}"
    echo -e "${CYAN}Digite ou cole seu texto abaixo." 
    echo -e "Pressione Ctrl+D (ou Ctrl+Z seguido de Enter no Windows) para finalizar.${NC}"
    echo ""
    echo -e "${YELLOW}--- INICIO DO TEXTO (cole aqui) ---${NC}"

    cat > "$tmpfile"

    echo ""
    echo -e "${YELLOW}--- FIM DO TEXTO ---${NC}"
    echo ""

    if [ ! -s "$tmpfile" ]; then
        echo -e "${RED}Nenhum texto digitado/colado. Cancelando.${NC}"
        rm -f "$tmpfile"
        exit 1
    fi

    local lines
    lines=$(wc -l < "$tmpfile")
    local chars
    chars=$(wc -c < "$tmpfile")
    echo -e "${GREEN}Capturadas $lines linhas, $chars caracteres. Enviando para OpenCode...${NC}"
    echo ""

    cd "$ECO_DIR"
    "$OC_BIN" run --model mimo/mimo-v2.5-pro --agent marceloclaro -f "$tmpfile"
    rm -f "$tmpfile"
}

file_mode() {
    local file="$1"
    if [ ! -f "$file" ]; then
        echo -e "${RED}Arquivo nao encontrado: $file${NC}"
        exit 1
    fi
    echo -e "${GREEN}Enviando arquivo '$file' para OpenCode...${NC}"

    local lines chars
    lines=$(wc -l < "$file")
    chars=$(wc -c < "$file")
    echo -e "${CYAN}$lines linhas, $chars caracteres${NC}"
    echo ""

    cd "$ECO_DIR"
    "$OC_BIN" run --model mimo/mimo-v2.5-pro --agent marceloclaro -f "$file"
}

clipboard_mode() {
    local tmpfile
    tmpfile=$(mktemp "$TEMP_DIR/clipboard-XXXXXX.md")

    echo -e "${YELLOW}Lendo da area de transferencia...${NC}"
    read_clipboard > "$tmpfile"

    if [ ! -s "$tmpfile" ]; then
        echo -e "${RED}Area de transferencia vazia ou inacessivel.${NC}"
        echo -e "${YELLOW}Dica: Copie o texto antes de executar o comando.${NC}"
        echo -e "${YELLOW}Alternativa: Use '$0 -i' para digitar/colar manualmente.${NC}"
        echo -e "${YELLOW}Alternativa 2: Use 'cat arquivo | $0' para enviar via pipe.${NC}"
        rm -f "$tmpfile"
        exit 1
    fi

    local lines chars
    lines=$(wc -l < "$tmpfile")
    chars=$(wc -c < "$tmpfile")
    echo -e "${GREEN}$lines linhas, $chars caracteres lidos da area de transferencia.${NC}"
    echo -e "${CYAN}Primeiras linhas:${NC}"
    head -5 "$tmpfile"
    if [ "$lines" -gt 5 ]; then
        echo -e "${CYAN}... (+$(($lines - 5)) linhas)${NC}"
    fi
    echo ""

    echo -e "${YELLOW}Enviando para OpenCode...${NC}"
    echo ""

    cd "$ECO_DIR"
    "$OC_BIN" run --model mimo/mimo-v2.5-pro --agent marceloclaro -f "$tmpfile"
    rm -f "$tmpfile"
}

pipe_mode() {
    local tmpfile
    tmpfile=$(mktemp "$TEMP_DIR/pipe-XXXXXX.md")

    cat > "$tmpfile"

    if [ ! -s "$tmpfile" ]; then
        echo -e "${RED}Nenhum dado recebido via pipe.${NC}"
        rm -f "$tmpfile"
        exit 1
    fi

    local lines chars
    lines=$(wc -l < "$tmpfile")
    chars=$(wc -c < "$tmpfile")
    echo -e "${GREEN}$lines linhas, $chars caracteres recebidos via pipe.${NC}"
    echo ""

    cd "$ECO_DIR"
    "$OC_BIN" run --model mimo/mimo-v2.5-pro --agent marceloclaro -f "$tmpfile"
    rm -f "$tmpfile"
}

# --- Main --------------------------------------------------------------------

# Verifica se o opencode existe
if [ ! -x "$OC_BIN" ]; then
    echo -e "${RED}OpenCode CLI nao encontrado em $OC_BIN${NC}"
    echo -e "${YELLOW}Defina OPENCODE_BIN ou instale o opencode.${NC}"
    exit 1
fi

# Sem argumentos: tenta clipboard
if [ $# -eq 0 ]; then
    # Se estiver em pipe, usa pipe
    if [ ! -t 0 ]; then
        pipe_mode
    else
        clipboard_mode
    fi
    exit $?
fi

# Processa argumentos
while getopts ":f:ih" opt; do
    case $opt in
        f) file_mode "$OPTARG" ;;
        i) interactive_mode ;;
        h) usage ;;
        *) usage ;;
    esac
done
