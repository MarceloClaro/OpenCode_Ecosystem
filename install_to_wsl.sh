#!/bin/bash
# ==============================================================================
# OpenCode Ecosystem - WSL Deployment Script
# Migra o ecossistema e as engines de validação N3.5+ para o ambiente Linux/WSL
# ==============================================================================

echo "🚀 Iniciando deploy do OpenCode Ecosystem para o WSL..."

# Diretório base no WSL
WSL_BASE_DIR="$HOME/opencode-ecosystem"

# Cria a estrutura de diretórios do ecossistema no WSL
mkdir -p "$WSL_BASE_DIR/.opencode/engines"
mkdir -p "$WSL_BASE_DIR/.evolve"
mkdir -p "$WSL_BASE_DIR/.impact/sroi"
mkdir -p "$WSL_BASE_DIR/.tdd-sdd"

echo "📂 Diretórios criados em $WSL_BASE_DIR"

# Define o diretório de origem no Windows 
# (No WSL, o drive C: fica montado em /mnt/c)
WINDOWS_SRC="/mnt/c/Users/marce/AppData/Local/agy/bin"

if [ -d "$WINDOWS_SRC/.opencode" ]; then
    echo "🔄 Sincronizando engines e pipelines..."
    cp -r "$WINDOWS_SRC/.opencode/"* "$WSL_BASE_DIR/.opencode/"
    echo "✅ Engines de Orquestração, Multi-Reasoning e Potentiality Scanner copiadas."
else
    echo "⚠️ Diretório de origem do Windows não encontrado. Certifique-se de que o caminho /mnt/c/Users/marce/AppData/Local/agy/bin existe."
fi

# Ajusta permissões
chmod +x "$WSL_BASE_DIR/.opencode/run_potentiality.js" 2>/dev/null || true

echo "=============================================================================="
echo "✅ Deploy no WSL concluído com sucesso!"
echo " "
echo "Para testar o Potentiality Scanner com a nova Inferência Bayesiana, execute:"
echo "  cd $WSL_BASE_DIR"
echo "  node .opencode/run_potentiality.js"
echo "=============================================================================="
