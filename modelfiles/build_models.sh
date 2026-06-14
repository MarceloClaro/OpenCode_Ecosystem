#!/bin/bash
# ============================================================
# OpenCode Ecosystem — Build de Modelos Customizados
# Compila todos os Modelfiles em modelos Ollama nomeados
# ============================================================

MDIR="/mnt/c/Users/marce/Documents/OpenCode_Ecosystem/modelfiles"
LOGFILE="$HOME/ollama_build.log"

echo "$(date) — Build de modelos customizados iniciado" | tee "$LOGFILE"
echo ""

build_model() {
    local NAME="$1"
    local MFILE="$2"
    local BASE_REQUIRED="$3"
    
    echo "======================================================"
    echo "🔨 Compilando: $NAME"
    echo "   Modelfile: $MFILE"
    echo "======================================================"
    
    # Verifica se o modelo base está instalado
    if ! ollama list | grep -q "$BASE_REQUIRED"; then
        echo "⚠️  Base '$BASE_REQUIRED' não instalada — pulando $NAME"
        return 1
    fi
    
    if ollama create "$NAME" -f "$MDIR/$MFILE"; then
        echo "✅ $NAME criado com sucesso!" | tee -a "$LOGFILE"
    else
        echo "❌ Falha ao criar $NAME" | tee -a "$LOGFILE"
    fi
    echo ""
}

# ---- Modelos disponíveis agora ----
build_model "opencode/qwen-coder-fast"   "Modelfile.qwen-coder-fast"  "qwen2.5-coder:1.5b"
build_model "opencode/gemma-scholar"      "Modelfile.gemma-scholar"     "gemma3:1b"

# ---- Modelos que dependem de downloads futuros ----
build_model "opencode/qwen-coder-pro"     "Modelfile.qwen-coder-pro"    "qwen2.5-coder:7b"
build_model "opencode/deepseek-reasoner"  "Modelfile.deepseek-reasoner" "deepseek-r1:7b"
build_model "opencode/phi4-orchestrator"  "Modelfile.phi4-orchestrator" "phi4-mini"

echo ""
echo "======================================================"
echo "📋 Todos os modelos disponíveis:"
ollama list
echo ""
echo "✅ Build concluído! $(date)" | tee -a "$LOGFILE"
echo "======================================================"
echo ""
echo "Para usar no OpenCode:"
echo "  opencode --model ollama/opencode/qwen-coder-fast"
echo "  opencode --model ollama/opencode/gemma-scholar"
echo "  opencode --model ollama/opencode/deepseek-reasoner"
