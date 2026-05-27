# 🖥️ OpenCode Ecosystem com LLMs Locais — Guia Completo

> **Diagnóstico realizado em**: 24/05/2026
> **Hardware**: CPU-only (sem GPU NVIDIA detectada)
> **Sistema**: Windows 11 · Python 3.12.10 · Node.js v25 · Bun 1.3

---

## 📊 Diagnóstico do Seu PC

| Componente | Status | Detalhe |
|-----------|:------:|---------|
| Python 3.12 | ✅ | C:\Users\marce\...\Python312 |
| Node.js v25 | ✅ | v25.9.0 |
| Bun 1.3 | ✅ | 1.3.13 |
| Git | ✅ | 2.54.0 |
| Ollama | ✅ | 3 modelos instalados |
| LM Studio | ❌ | Não encontrado |
| NVIDIA GPU | ❌ | Não detectada (CPU-only) |
| torch | ✅ | Instalado |
| transformers | ✅ | Instalado |
| llama-cpp-python | ❌ | NÃO instalado |
| openai (lib) | ✅ | Instalado |

### Modelos Ollama Instalados

| Modelo | Tamanho | Viável em CPU? |
|--------|:------:|:--------------:|
| qwen3.6:latest | 23 GB | ⚠️ Muito pesado para CPU |
| qwen2.5-coder:7b | 4.7 GB | ✅ Viável (7B parâmetros) |
| qwen3-embedding | 4.7 GB | ✅ Embeddings apenas |

---

## 🎯 Solução 1: Ollama como Provider do OpenCode (RECOMENDADO)

### Passo 1: Instalar modelos otimizados para CPU

```bash
# Modelos pequenos que rodam bem em CPU (4-8 GB RAM):
ollama pull llama3.2:3b        # Meta, 3B parâmetros, ~2 GB — melhor custo-benefício
ollama pull phi3:mini           # Microsoft, 3.8B, ~2.3 GB — muito rápido
ollama pull qwen2.5:3b          # Alibaba, 3B, ~2 GB — já tem Qwen instalado
ollama pull mistral:7b          # Mistral, 7B, ~4.1 GB — qualidade superior
ollama pull gemma3:4b           # Google, 4B, ~2.5 GB — open-source Google
```

### Passo 2: Configurar OpenCode para usar Ollama

Edite `C:\Users\marce\.config\opencode\opencode.json`:

```json
{
  "model": "ollama/llama3.2:3b",
  "provider": "ollama",
  "ollama": {
    "base_url": "http://localhost:11434",
    "model": "llama3.2:3b",
    "context_size": 8192
  }
}
```

Ou via linha de comando:

```bash
opencode config set model ollama/llama3.2:3b
opencode config set provider ollama
```

### Passo 3: Testar

```bash
ollama serve            # Iniciar Ollama (se não estiver rodando)
opencode "Olá, teste de conexão local"
```

---

## 🎯 Solução 2: LM Studio (Interface Gráfica)

### Instalar

1. Baixe de https://lmstudio.ai/
2. Instale no Windows
3. Baixe um modelo pequeno (ex: `Llama-3.2-3B-Instruct-Q4_K_M.gguf`)
4. Inicie o servidor local na porta 1234

### Configurar OpenCode

```json
{
  "model": "lmstudio/Llama-3.2-3B-Instruct",
  "provider": "openai-compatible",
  "base_url": "http://localhost:1234/v1"
}
```

---

## 🎯 Solução 3: llama-cpp-python (Máximo Controle)

### Instalar

```bash
pip install llama-cpp-python
```

### Baixar modelo GGUF

```bash
# Opções de modelos GGUF (formato quantizado para CPU):
# https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF
# https://huggingface.co/bartowski/Qwen2.5-3B-Instruct-GGUF
```

### Usar com OpenCode

```python
# Script de bridge llama-cpp → OpenCode
from llama_cpp import Llama

llm = Llama(
    model_path="Llama-3.2-3B-Instruct-Q4_K_M.gguf",
    n_ctx=8192,        # contexto
    n_threads=8,        # threads CPU
    n_gpu_layers=0,     # 0 = CPU-only
)

# API compatível com OpenAI
```

---

## 📊 Comparativo: Qual modelo escolher?

| Modelo | Tamanho | RAM Necessária | Velocidade CPU | Qualidade | Recomendado Para |
|--------|:------:|:------------:|:------------:|:-------:|-----------------|
| **llama3.2:3b** | 2 GB | 4 GB | ⚡ Rápido | ⭐⭐⭐⭐ | ⭐ Uso geral |
| **phi3:mini** | 2.3 GB | 4 GB | ⚡⚡ Muito rápido | ⭐⭐⭐ | Tarefas simples |
| **qwen2.5:3b** | 2 GB | 4 GB | ⚡ Rápido | ⭐⭐⭐⭐ | Código + texto |
| **mistral:7b** | 4.1 GB | 8 GB | 🐢 Lento | ⭐⭐⭐⭐⭐ | Qualidade máxima |
| **gemma3:4b** | 2.5 GB | 6 GB | ⚡ Rápido | ⭐⭐⭐⭐ | Google ecosystem |
| **qwen2.5-coder:7b** | 4.7 GB | 8 GB | 🐢 Lento | ⭐⭐⭐⭐⭐ | Já instalado! |

> **Recomendação**: Comece com `llama3.2:3b` (equilíbrio velocidade/qualidade). Se tiver 8+ GB RAM livre, use `mistral:7b` para qualidade superior.

---

## 🔧 Script de Configuração Automatizada

Crie o arquivo `setup_local_llm.bat`:

```batch
@echo off
echo ========================================
echo OpenCode Ecosystem - Setup LLM Local
echo ========================================
echo.

REM 1. Instalar modelo recomendado
echo [1/4] Instalando llama3.2:3b (Meta, 2GB)...
ollama pull llama3.2:3b

REM 2. Instalar modelo de codigo (ja tem Qwen)
echo [2/4] Instalando qwen2.5-coder:3b (leve)...
ollama pull qwen2.5-coder:3b

REM 3. Testar Ollama
echo [3/4] Testando Ollama...
ollama run llama3.2:3b "Responda apenas: OK" 

REM 4. Configurar OpenCode
echo [4/4] Configurando OpenCode...
echo.
echo Agora execute:
echo   opencode config set model ollama/llama3.2:3b
echo   opencode config set provider ollama
echo.
echo ========================================
echo PRONTO! OpenCode rodando com LLM local.
echo ========================================
pause
```

---

## ⚡ Comandos Rápidos

```bash
# Ver modelos instalados
ollama list

# Iniciar servidor Ollama
ollama serve

# Testar um modelo
ollama run llama3.2:3b "Explique Teoria dos Jogos em 1 frase"

# Remover modelo pesado (libera 23 GB!)
ollama rm qwen3.6:latest

# Instalar modelo recomendado
ollama pull llama3.2:3b

# Ver uso de RAM dos modelos
ollama ps
```

---

## 🚨 Avisos e Recomendações

1. **qwen3.6:latest (23 GB)** — Remova! Consome 23 GB de disco e é inviável em CPU. Use `ollama rm qwen3.6:latest`
2. **qwen2.5-coder:7b (4.7 GB)** — Mantenha! Já instalado e funcional para código
3. **Sem GPU** — Prefira modelos de 3B-4B parâmetros (2-3 GB). Modelos 7B+ serão muito lentos
4. **Contexto** — CPU-only limita o contexto a 4K-8K tokens. O deepseek-v4-pro oferece 200K — considere isso ao migrar
5. **Híbrido** — Use LLM local para tarefas simples e deepseek-v4-pro (nuvem gratuita) para tarefas complexas

---

> **Conclusão**: Seu PC está pronto para rodar OpenCode com LLMs locais! Instale `llama3.2:3b` e configure o provider Ollama. Para tarefas que exigem contexto grande (200K), mantenha o deepseek-v4-pro como fallback.
