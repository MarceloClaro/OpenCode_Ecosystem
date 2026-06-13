#!/usr/bin/env bash
# Chat Acadêmico Local com Ollama (Qwen 1.5B) + Busca + Vocalização (TTS)
# Criador: Prof. Marcelo Claro Laranjeira (https://github.com/MarceloClaro)
# ORCID: https://orcid.org/0000-0001-8996-2887

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

ECO_DIR="/mnt/c/Users/marce/Documents/OpenCode_Ecosystem"
PROJECTS_DIR="$ECO_DIR/projects"

falar() {
    local msg="$1"
    # Limpa aspas e quebras de linha para evitar erro de sintaxe no PowerShell
    local msg_limpa=$(echo "$msg" | tr -d '"' | tr -d "'" | tr -d '`' | tr '\n' ' ' | cut -c1-300)
    powershell.exe -NoProfile -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('$msg_limpa')" >/dev/null 2>&1 &
}

realizar_busca_interna() {
    local termo="$1"
    echo -e "${YELLOW}>> Buscando localmente em /projects por: '$termo'...${NC}"
    # Busca arquivos que contenham o termo
    local resultado=$(grep -rni --exclude-dir=".git" "$termo" "$PROJECTS_DIR" | head -n 10)
    if [ -n "$resultado" ]; then
        echo -e "${GREEN}Resultados internos encontrados!${NC}"
        echo "$resultado"
    else
        echo "Nenhum arquivo local correspondente encontrado."
    fi
}

realizar_busca_externa() {
    local termo="$1"
    echo -e "${YELLOW}>> Buscando externamente na Wikipedia por: '$termo'...${NC}"
    # Codifica espaços para a URL
    local termo_encoded=$(echo "$termo" | tr ' ' '+')
    # Faz chamada API da Wikipedia
    local url="https://pt.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch=${termo_encoded}"
    local resposta_json=$(curl -s -L -H "User-Agent: Mozilla/5.0" "$url")
    
    # Extrai trechos usando python3 (nativo em Ubuntu)
    local resultado=$(echo "$resposta_json" | python3 -c '
import sys, json
try:
    data = json.load(sys.stdin)
    search_results = data.get("query", {}).get("search", [])
    for item in search_results[:3]:
        # Remove tags HTML do snippet
        snippet = item["snippet"].replace("<span class=\"searchmatch\">", "").replace("</span>", "")
        print(f"- {item[\"title\"]}: {snippet}\n")
except Exception as e:
    print("Erro ao extrair resultados.")
')
    
    if [ -n "$resultado" ]; then
        echo -e "${GREEN}Resultados externos encontrados!${NC}"
        echo "$resultado"
    else
        echo "Nenhuma informação externa encontrada."
    fi
}

clear
echo -e "${CYAN}=================================================================${NC}"
echo -e "${CYAN}        CHAT ACADÊMICO LOCAL: OLLAMA + BUSCA + VOCALIZAÇÃO       ${NC}"
echo -e "${CYAN}   Criador: Prof. Marcelo Claro Laranjeira (ORCID)               ${NC}"
echo -e "${CYAN}=================================================================${NC}"
echo ""

falar "Bem-vindo ao Chat Acadêmico Local. O que gostaria de pesquisar hoje?"

echo -n "Digite a sua pergunta científica: "
read -r pergunta

if [ -z "$pergunta" ]; then
    echo "Pergunta vazia. Retornando..."
    exit 0
fi

echo ""
echo "Escolha o tipo de busca para enriquecer a resposta:"
echo -e " [1] ${GREEN}Busca Interna${NC} (Arquivos locais em /projects)"
echo -e " [2] ${YELLOW}Busca Externa${NC} (Wikipedia Acadêmica)"
echo -e " [3] ${CYAN}Busca Híbrida${NC} (Ambas as buscas)"
echo -e " [4] ${NC}Sem Busca${NC} (Apenas LLM Local)"
echo -n "Opção: "
read -r opcao_busca

CONTEXTO=""

case $opcao_busca in
    1)
        CONTEXTO=$(realizar_busca_interna "$pergunta")
        ;;
    2)
        CONTEXTO=$(realizar_busca_externa "$pergunta")
        ;;
    3)
        CONTEXTO_INT=$(realizar_busca_interna "$pergunta")
        CONTEXTO_EXT=$(realizar_busca_externa "$pergunta")
        CONTEXTO="[Contexto Interno]\n$CONTEXTO_INT\n\n[Contexto Externo]\n$CONTEXTO_EXT"
        ;;
    *)
        echo "Processando sem contexto adicional..."
        ;;
esac

echo ""
echo -e "${YELLOW}>> Consultando modelo local qwen2.5-coder:1.5b via Ollama...${NC}"
echo ""

# Constrói o prompt final com o contexto
PROMPT_FINAL="Você é o assistente científico do Prof. Marcelo Claro Laranjeira. Responda à pergunta do usuário de forma clara e objetiva em português do Brasil. Se houver contexto de busca fornecido abaixo, use-o para fundamentar sua resposta."
if [ -n "$CONTEXTO" ]; then
    PROMPT_FINAL="$PROMPT_FINAL\n\n[Contexto de Busca]:\n$CONTEXTO"
fi
PROMPT_FINAL="$PROMPT_FINAL\n\n[Pergunta]: $pergunta"

# Executa o Ollama passando o prompt e salvando a resposta
RESP_LLM=$(echo -e "$PROMPT_FINAL" | ollama run qwen2.5-coder:1.5b)

echo -e "${GREEN}Resposta do Modelo Local:${NC}"
echo -e "$RESP_LLM"
echo ""

# Vocaliza a resposta em background
falar "Pesquisa concluída. Aqui está a resposta sintetizada: $RESP_LLM"

echo -n "Pressione [Enter] para continuar..."
read -r
