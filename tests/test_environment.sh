#!/usr/bin/env bash
# Test-Driven Development (TDD) Environment Auditor for OpenCode Ecosystem

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FAILED=0

echo -e "${YELLOW}===================================================${NC}"
echo -e "${YELLOW}   Iniciando Auditoria do Ecossistema OpenCode...  ${NC}"
echo -e "${YELLOW}===================================================${NC}"
echo ""

# T1: Verificar se estamos rodando no WSL Linux
echo -n "T1: Verificando se o ambiente é WSL Linux... "
if grep -qi "microsoft" /proc/version 2>/dev/null; then
    echo -e "${GREEN}[PASS]${NC}"
else
    echo -e "${RED}[FAIL]${NC} (Ambiente não é WSL)"
    FAILED=1
fi

# T2: Verificar se o usuário ativo é marcelo
echo -n "T2: Verificando se o usuário é marcelo... "
CURRENT_USER=$(whoami)
if [ "$CURRENT_USER" = "marcelo" ]; then
    echo -e "${GREEN}[PASS]${NC} ($CURRENT_USER)"
else
    echo -e "${RED}[FAIL]${NC} (Usuário ativo é $CURRENT_USER, esperado marcelo)"
    FAILED=1
fi

# T3: Verificar se o executável opencode está acessível no PATH
echo -n "T3: Verificando se o opencode está no PATH... "
# Carrega o .bashrc para simular shell interativo
source "$HOME/.bashrc" 2>/dev/null || true
OPENCODE_PATH=$(which opencode 2>/dev/null)
if [ -n "$OPENCODE_PATH" ]; then
    echo -e "${GREEN}[PASS]${NC} ($OPENCODE_PATH)"
else
    echo -e "${RED}[FAIL]${NC} (opencode não está no PATH)"
    FAILED=1
fi

# T4: Verificar se a execução do opencode funciona
echo -n "T4: Testando execução de 'opencode --version'... "
if command -v opencode >/dev/null 2>&1; then
    VERSION=$(opencode --version 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$VERSION" ]; then
        echo -e "${GREEN}[PASS]${NC} (Versão: $VERSION)"
    else
        echo -e "${RED}[FAIL]${NC} (Erro ao executar 'opencode --version')"
        FAILED=1
    fi
else
    echo -e "${RED}[FAIL]${NC} (Comando 'opencode' indisponível)"
    FAILED=1
fi

# T5: Verificar se a pasta de projetos está acessível e possui permissão de escrita
echo -n "T5: Verificando pasta de projetos do ecossistema... "
PROJECTS_DIR="/mnt/c/Users/marce/Documents/OpenCode_Ecosystem/projects"
if [ -d "$PROJECTS_DIR" ]; then
    # Testa permissão de escrita
    TEST_FILE="$PROJECTS_DIR/.write_test"
    touch "$TEST_FILE" 2>/dev/null
    if [ -f "$TEST_FILE" ]; then
        rm "$TEST_FILE"
        echo -e "${GREEN}[PASS]${NC} (Pasta acessível com escrita)"
    else
        echo -e "${RED}[FAIL]${NC} (Sem permissão de escrita em $PROJECTS_DIR)"
        FAILED=1
    fi
else
    echo -e "${RED}[FAIL]${NC} (Pasta $PROJECTS_DIR não encontrada)"
    FAILED=1
fi

# T6: Verificar se os scripts de RAG e Vocalização existem
echo -n "T6: Verificando scripts de RAG e Vocalização... "
CHAT_SCRIPT="/mnt/c/Users/marce/Documents/OpenCode_Ecosystem/scripts/chat_ollama.py"
DAEMON_SCRIPT="/mnt/c/Users/marce/Documents/OpenCode_Ecosystem/scripts/vocalizer_daemon.ps1"
TEST_CHAT_SCRIPT="/mnt/c/Users/marce/Documents/OpenCode_Ecosystem/tests/test_chat_ollama.py"

if [ -f "$CHAT_SCRIPT" ] && [ -f "$DAEMON_SCRIPT" ] && [ -f "$TEST_CHAT_SCRIPT" ]; then
    echo -e "${GREEN}[PASS]${NC} (chat_ollama.py, vocalizer_daemon.ps1, test_chat_ollama.py OK)"
else
    echo -e "${RED}[FAIL]${NC} (Faltam scripts de RAG ou Vocalização)"
    FAILED=1
fi

echo ""
echo -e "${YELLOW}===================================================${NC}"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}  AUDITORIA CONCLUÍDA: TODOS OS TESTES PASSARAM! (GREEN) ${NC}"
    echo -e "${YELLOW}===================================================${NC}"
    exit 0
else
    echo -e "${RED}  AUDITORIA FALHOU: CORRIJA AS FALHAS ACIMA (RED) ${NC}"
    echo -e "${YELLOW}===================================================${NC}"
    exit 1
fi
