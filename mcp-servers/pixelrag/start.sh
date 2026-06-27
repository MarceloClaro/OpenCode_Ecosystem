#!/bin/bash
# PixelRAG MCP Server - Script de Inicialização
# Uso: ./start.sh [--port PORT] [--index-dir DIR]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ECOSYSTEM_DIR="/mnt/c/Users/marce/Documents/OpenCode_Ecosystem"
PIXELRAG_INDEX_DIR="${ECOSYSTEM_DIR}/pixelrag-indexes"

# Configurações padrão
PORT=${PORT:-8080}
INDEX_DIR=${INDEX_DIR:-$PIXELRAG_INDEX_DIR}

# Criar diretório de índices
mkdir -p "$INDEX_DIR"

echo "=== PixelRAG MCP Server v1.0.0 ==="
echo "Diretório de índices: $INDEX_DIR"
echo ""

# Verificar se pixelrag está instalado
if ! command -v pixelshot &> /dev/null; then
    echo "Erro: pixelrag não encontrado. Instale com:"
    echo "  pip install pixelrag"
    exit 1
fi

# Verificar se o servidor HTTP deve ser iniciado
if [ "$1" = "--serve" ]; then
    echo "Iniciando servidor FAISS na porta $PORT..."
    pixelrag serve --index-dir "$INDEX_DIR" --port "$PORT" --host 0.0.0.0
else
    echo "Iniciando MCP Server (stdio)..."
    echo "Use --serve para iniciar o servidor HTTP"
    python3 "$SCRIPT_DIR/server.py"
fi
