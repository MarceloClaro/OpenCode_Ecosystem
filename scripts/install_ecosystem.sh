#!/usr/bin/env bash
# OpenCode Ecosystem Installer/Reproducer
# Designed to be fully reproducible on any WSL machine

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}===================================================${NC}"
echo -e "${YELLOW}   Instalação/Reprodução do Ecossistema OpenCode   ${NC}"
echo -e "${YELLOW}===================================================${NC}"

# 1. Verificar se é WSL
if ! grep -qi "microsoft" /proc/version 2>/dev/null; then
    echo -e "${RED}Erro: Este instalador deve ser executado dentro do ambiente WSL (Linux).${NC}"
    exit 1
fi

# 2. Diretório de Instalação
INSTALL_DIR="$HOME/.opencode/bin"
mkdir -p "$INSTALL_DIR"

# 3. Verificar se já está instalado
if [ -f "$INSTALL_DIR/opencode" ]; then
    echo -e "${GREEN}OpenCode já está instalado em $INSTALL_DIR/opencode.${NC}"
else
    echo -e "${YELLOW}Instalando OpenCode...${NC}"
    
    URL="https://github.com/anomalyco/opencode/releases/latest/download/opencode-linux-x64.tar.gz"
    TMP_FILE="/tmp/opencode-linux-x64.tar.gz"
    
    echo "Baixando o pacote a partir do GitHub Releases..."
    # Baixa com retentativas e tolerância a quedas de rede (MTU de WSL)
    if curl -L --retry 5 --retry-delay 2 --retry-connrefused -o "$TMP_FILE" "$URL"; then
        echo -e "${GREEN}Download concluído com sucesso.${NC}"
    else
        echo -e "${YELLOW}Falha no curl primário. Tentando com wget...${NC}"
        if wget -t 5 -O "$TMP_FILE" "$URL"; then
             echo -e "${GREEN}Download via wget concluído com sucesso.${NC}"
        else
             echo -e "${RED}Erro crítico: Não foi possível baixar o OpenCode. Verifique sua conexão de rede.${NC}"
             exit 1
        fi
    fi

    echo "Extraindo os arquivos..."
    tar -xzf "$TMP_FILE" -C /tmp/
    
    echo "Movendo executável..."
    mv /tmp/opencode "$INSTALL_DIR/"
    chmod 755 "$INSTALL_DIR/opencode"
    
    # Limpa temporários
    rm -f "$TMP_FILE" /tmp/opencode
    echo -e "${GREEN}OpenCode instalado com sucesso!${NC}"
fi

# 4. Configurar PATH no .bashrc do usuário
BASHRC="$HOME/.bashrc"
EXPORT_CMD="export PATH=\"\$HOME/.opencode/bin:\$PATH\""

if grep -qF "$INSTALL_DIR" "$BASHRC"; then
    echo -e "${GREEN}O PATH do OpenCode já está configurado no seu .bashrc.${NC}"
else
    echo "" >> "$BASHRC"
    echo "# opencode" >> "$BASHRC"
    echo "$EXPORT_CMD" >> "$BASHRC"
    echo -e "${GREEN}PATH adicionado com sucesso ao $BASHRC.${NC}"
    echo -e "${YELLOW}Por favor, execute 'source ~/.bashrc' ou reinicie o terminal para aplicar as alterações.${NC}"
fi

echo ""
echo -e "${GREEN}===================================================${NC}"
echo -e "${GREEN}   Ecosistema configurado! Pronto para uso. (GREEN) ${NC}"
echo -e "${GREEN}===================================================${NC}"
