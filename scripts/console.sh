#!/usr/bin/env bash
# Painel de Controle e Auditoria Científica - Ecossistema OpenCode & Antigravity
# Criador: Prof. Marcelo Claro Laranjeira (https://github.com/MarceloClaro)
# ORCID: https://orcid.org/0000-0001-8996-2887
# Direcionado para pesquisa científica e rigor acadêmico internacional.

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # Sem cor

ECO_DIR="/mnt/c/Users/marce/Documents/OpenCode_Ecosystem"
PROJECTS_DIR="$ECO_DIR/projects"
TESTS_DIR="$ECO_DIR/tests"
SCRIPTS_DIR="$ECO_DIR/scripts"
AGY_BIN="/mnt/c/Users/marce/AppData/Local/agy/bin/agy.exe"
CMD_FILE="$ECO_DIR/.vocalizer_cmd"

falar() {
    local msg="$1"
    local msg_limpa=$(echo "$msg" | tr -d '"' | tr -d "'" | tr -d '`' | tr '\n' ' ' | cut -c1-300)
    echo "PLAY:$msg_limpa" > "$CMD_FILE"
}

# Saudação inicial vocalizada
falar "Painel científico atualizado e consolidado. Pronto para auditorias."

# Função para rodar auditoria rápida
executar_auditoria_silenciosa() {
    bash "$TESTS_DIR/test_environment.sh" > /dev/null 2>&1
    return $?
}

exibir_menu() {
    clear
    echo -e "${CYAN}=================================================================${NC}"
    echo -e "${CYAN}             UNIVERSIDADE & CIÊNCIA | ECOSSISTEMA CIENTÍFICO     ${NC}"
    echo -e "${CYAN}                   OpenCode & Antigravity (WSL)                  ${NC}"
    echo -e "${CYAN}                                                                 ${NC}"
    echo -e "${CYAN}   Criador: Prof. Marcelo Claro Laranjeira                       ${NC}"
    echo -e "${CYAN}   GitHub:  https://github.com/MarceloClaro                      ${NC}"
    echo -e "${CYAN}   ORCID:   https://orcid.org/0000-0001-8996-2887                ${NC}"
    echo -e "${CYAN}=================================================================${NC}"
    echo ""
    
    # Executa verificação de auditoria
    if executar_auditoria_silenciosa; then
        echo -e "Status da Auditoria: ${GREEN}[✔ GREEN - Sistema Totalmente Operacional & Auditado (Qualis A1)]${NC}"
    else
        echo -e "Status da Auditoria: ${RED}[✘ RED - Requer Intervenção / Erro na Integridade]${NC}"
    fi
    echo ""
    echo -e "${BOLD}[SISTEMA E AUDITORIA]${NC}"
    echo -e "  [1] Executar Auditoria TDD (test_environment)"
    echo -e "  [2] Diagnóstico e Depuração (opencode debug)"
    echo -e "  [3] Estatísticas de Uso e Custos (opencode stats)"
    echo ""
    echo -e "${BOLD}[ORQUESTRADORES DE IA (AGENTES)]${NC}"
    echo -e "  [4] Iniciar OpenCode Web Server (Interface Visual)"
    echo -e "  [5] Iniciar OpenCode TUI (Terminal Interface)"
    echo -e "  [6] Continuar Conversa no Antigravity CLI (agy.exe -c)"
    echo -e "  [7] Novo Prompt Interativo no Antigravity CLI (agy.exe -i)"
    echo ""
    echo -e "${BOLD}[MODELOS E PROVEDORES (LLMs)]${NC}"
    echo -e "  [8] Chat Local + RAG Híbrido + Vocalização (Ollama + Qwen)"
    echo -e "  [9] Gerenciar Provedores e Credenciais (opencode auth)"
    echo -e " [10] Listar Modelos Disponíveis (Ollama, agy, opencode)"
    echo ""
    echo -e "${BOLD}[BACKUP E COMPARTILHAMENTO]${NC}"
    echo -e " [11] Sincronizar e Backup com GitHub (Git Push)"
    echo -e " [12] Visualizar Documentação Técnica (SDD / Manual)"
    echo -e " [13] Abrir Diretório de Projetos no Explorer"
    echo -e " [14] Colar texto no OpenCode (bypass raw mode)"
    echo ""
    echo -e " Controle de Áudio (TTS):"
    echo -e "   [p] Pausar       [r] Retomar       [c] Cancelar       [t] Repetir"
    echo -e "-----------------------------------------------------------------"
    echo -e " [0] ${RED}Sair do Painel${NC}"
    echo -e "-----------------------------------------------------------------"
    echo -n "Digite a opção desejada: "
}

while true; do
    exibir_menu
    read -r opcao
    
    case $opcao in
        1)
            echo ""
            echo -e "${YELLOW}>> Executando Auditoria TDD (test_environment.sh)...${NC}"
            echo ""
            bash "$TESTS_DIR/test_environment.sh"
            echo ""
            echo -n "Pressione [Enter] para continuar..."
            read -r
            ;;
        2)
            echo ""
            echo -e "${YELLOW}>> Iniciando Ferramentas de Diagnóstico e Depuração do OpenCode...${NC}"
            echo ""
            opencode debug
            echo ""
            echo -n "Pressione [Enter] para continuar..."
            read -r
            ;;
        3)
            echo ""
            echo -e "${YELLOW}>> Buscando Estatísticas de Uso de Tokens e Custos...${NC}"
            echo ""
            opencode stats
            echo ""
            echo -n "Pressione [Enter] para continuar..."
            read -r
            ;;
        4)
            echo ""
            echo -e "${YELLOW}>> Iniciando OpenCode Web na porta 4096...${NC}"
            echo -e "O navegador abrirá automaticamente em alguns segundos."
            echo -e "Pressione Ctrl+C para encerrar o servidor e retornar ao painel."
            echo ""
            explorer.exe "http://localhost:4096" >/dev/null 2>&1 &
            cd "$PROJECTS_DIR"
            opencode web --hostname 127.0.0.1 --port 4096
            ;;
        5)
            echo ""
            echo -e "${YELLOW}>> Iniciando OpenCode TUI (Interface do Terminal)...${NC}"
            echo -e "Pressione Ctrl+C ou digite exit para sair."
            echo ""
            cd "$PROJECTS_DIR"
            opencode
            echo ""
            echo -n "Pressione [Enter] para retornar ao painel..."
            read -r
            ;;
        6)
            echo ""
            echo -e "${MAGENTA}>> Continuando a última sessão do Antigravity CLI...${NC}"
            echo -e "Para sair do prompt do Antigravity, digite /exit ou finalize o comando."
            echo ""
            cd "$ECO_DIR"
            "$AGY_BIN" -c
            echo ""
            echo -n "Pressione [Enter] para retornar ao painel..."
            read -r
            ;;
        7)
            echo ""
            echo -e "${MAGENTA}>> Iniciando nova conversa interativa no Antigravity CLI...${NC}"
            echo "Digite o prompt inicial para a sessão (ou deixe em branco para iniciar interativo):"
            read -r prompt_init
            echo ""
            cd "$ECO_DIR"
            if [ -z "$prompt_init" ]; then
                "$AGY_BIN" -i
            else
                "$AGY_BIN" -i --prompt "$prompt_init"
            fi
            echo ""
            echo -n "Pressione [Enter] para retornar ao painel..."
            read -r
            ;;
        8)
            echo ""
            echo -e "${YELLOW}>> Abrindo Chat Local com Ollama + Busca...${NC}"
            echo ""
            python3 "$SCRIPTS_DIR/chat_ollama.py"
            ;;
        9)
            echo ""
            echo -e "${YELLOW}>> Abrindo Gerenciador de Provedores e Autenticações do OpenCode...${NC}"
            echo ""
            opencode providers
            echo ""
            echo -n "Pressione [Enter] para retornar ao painel..."
            read -r
            ;;
        10)
            clear
            echo -e "${CYAN}=================================================================${NC}"
            echo -e "${CYAN}            MODELOS DE INTELIGÊNCIA ARTIFICIAL DISPONÍVEIS       ${NC}"
            echo -e "${CYAN}=================================================================${NC}"
            echo ""
            echo -e "${GREEN}[OLLAMA (LOCAL)]${NC}"
            ollama ls
            echo ""
            echo -e "${MAGENTA}[ANTIGRAVITY (AGY)]${NC}"
            "$AGY_BIN" models
            echo ""
            echo -e "${CYAN}[OPENCODE (GLOBAL)]${NC}"
            opencode models
            echo ""
            echo -e "${CYAN}=================================================================${NC}"
            echo -n "Pressione [Enter] para retornar ao painel..."
            read -r
            ;;
        11)
            echo ""
            echo -e "${YELLOW}>> Sincronizando e Criando Backup Acadêmico no GitHub...${NC}"
            echo ""
            cd "$ECO_DIR"
            git add .
            echo "Digite uma mensagem curta de commit para este backup:"
            read -r msg_commit
            if [ -z "$msg_commit" ]; then
                msg_commit="Backup acadêmico automático: $(date '+%Y-%m-%d %H:%M:%S')"
            fi
            git commit -m "$msg_commit"
            echo ""
            echo -e "${YELLOW}Enviando alterações...${NC}"
            git push -u origin main
            echo ""
            echo -n "Pressione [Enter] para continuar..."
            read -r
            ;;
        12)
            clear
            echo -e "${CYAN}=================================================================${NC}"
            echo -e "${CYAN}               DOCUMENTAÇÃO TÉCNICA DO ECOSSISTEMA               ${NC}"
            echo -e "${CYAN}=================================================================${NC}"
            echo ""
            echo "Escolha a documentação que deseja visualizar no terminal:"
            echo -e "  [1] Documento de Design de Software (SDD)"
            echo -e "  [2] Manual Acadêmico & Slides de Apresentação"
            echo -n "Opção: "
            read -r op_doc
            echo ""
            if [ "$op_doc" = "1" ]; then
                cat "$ECO_DIR/docs/sdd.md"
            elif [ "$op_doc" = "2" ]; then
                cat "$ECO_DIR/docs/manual_academic_presentation.md"
            else
                echo "Opção inválida."
            fi
            echo ""
            echo -e "${CYAN}=================================================================${NC}"
            echo -n "Pressione [Enter] para voltar ao menu..."
            read -r
            ;;
        13)
            echo ""
            echo -e "${YELLOW}>> Abrindo pasta de projetos no Windows...${NC}"
            explorer.exe "$(wslpath -w "$PROJECTS_DIR")" >/dev/null 2>&1
            sleep 1
            ;;
        14)
            echo ""
            echo -e "${YELLOW}>> Colar texto no OpenCode (bypass raw mode)${NC}"
            echo ""
            echo "Escolha o modo de colagem:"
            echo "  [a] Colar da area de transferencia (Windows Clipboard)"
            echo "  [b] Modo interativo (digitar/colar com Ctrl+D)"
            echo "  [c] Voltar ao menu"
            echo -n "Opção: "
            read -r op_paste
            case $op_paste in
                a|A)
                    bash "$SCRIPTS_DIR/opencode-paste.sh"
                    ;;
                b|B)
                    bash "$SCRIPTS_DIR/opencode-paste.sh -i"
                    ;;
                *)
                    echo ""
                    ;;
            esac
            echo ""
            echo -n "Pressione [Enter] para continuar..."
            read -r
            ;;
        p|P)
            echo "PAUSE" > "$CMD_FILE"
            ;;
        r|R)
            echo "RESUME" > "$CMD_FILE"
            ;;
        c|C)
            echo "STOP" > "$CMD_FILE"
            ;;
        t|T)
            echo "REPEAT" > "$CMD_FILE"
            ;;
        0)
            echo ""
            echo -e "${GREEN}Painel encerrado. Agradecemos pelo uso científico e profissional!${NC}"
            echo "STOP" > "$CMD_FILE"
            sleep 0.2
            falar "Painel encerrado. Até logo."
            sleep 1.5
            exit 0
            ;;
        *)
            echo ""
            echo -e "${RED}Opção inválida! Tente novamente.${NC}"
            sleep 1.5
            ;;
    esac
done
