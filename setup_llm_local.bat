@echo off
chcp 65001 >nul
title OpenCode Ecosystem — Setup LLM Local
echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║   OpenCode Ecosystem — Configurador de LLM Local   ║
echo ║   Ollama + Modelos Otimizados para CPU            ║
echo ╚══════════════════════════════════════════════════════╝
echo.

REM ============================================
REM ETAPA 1: Verificar Ollama
REM ============================================
echo [1/5] Verificando Ollama...
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo   [ERRO] Ollama nao encontrado!
    echo   Instale de: https://ollama.com/download/windows
    pause
    exit /b 1
)
echo   [OK] Ollama encontrado

REM ============================================
REM ETAPA 2: Remover modelo pesado (opcional)
REM ============================================
echo.
echo [2/5] Otimizando modelos...
ollama list | findstr "qwen3.6:latest" >nul
if %errorlevel% equ 0 (
    echo   Modelo qwen3.6:latest (23 GB) encontrado — muito pesado para CPU.
    echo   Deseja remove-lo para liberar 23 GB? (S/N)
    set /p remove="   > "
    if /i "%remove%"=="S" (
        echo   Removendo qwen3.6:latest...
        ollama rm qwen3.6:latest
        echo   [OK] 23 GB liberados!
    ) else (
        echo   [SKIP] Mantendo qwen3.6:latest
    )
) else (
    echo   [OK] Nenhum modelo excessivamente pesado detectado
)

REM ============================================
REM ETAPA 3: Instalar modelos recomendados
REM ============================================
echo.
echo [3/5] Instalando modelos recomendados (CPU-friendly)...

echo   Baixando llama3.2:3b (Meta, 2 GB, rapido e versatil)...
ollama pull llama3.2:3b

echo   Baixando qwen2.5-coder:3b (Alibaba, 2 GB, otimo para codigo)...
ollama pull qwen2.5-coder:3b

REM ============================================
REM ETAPA 4: Verificar instalacao
REM ============================================
echo.
echo [4/5] Verificando modelos instalados...
ollama list
echo.
echo   Total de modelos disponiveis:
ollama list | find /c "GB"

REM ============================================
REM ETAPA 5: Testar modelo
REM ============================================
echo.
echo [5/5] Testando modelo llama3.2:3b...
echo.
ollama run llama3.2:3b "Responda apenas com: OK, OpenCode local funcionando!"
echo.

REM ============================================
REM CONCLUSAO
REM ============================================
echo ╔══════════════════════════════════════════════════════╗
echo ║  CONFIGURACAO CONCLUIDA!                           ║
echo ╠══════════════════════════════════════════════════════╣
echo ║  Para usar com OpenCode:                           ║
echo ║    opencode config set model ollama/llama3.2:3b     ║
echo ║    opencode config set provider ollama              ║
echo ║                                                    ║
echo ║  Modelos disponiveis:                              ║
echo ║    ollama/llama3.2:3b        (uso geral)           ║
echo ║    ollama/qwen2.5-coder:3b   (codigo)              ║
echo ║    ollama/qwen2.5-coder:7b   (codigo, ja instalado)║
echo ║    ollama/qwen3-embedding    (embeddings)          ║
echo ╚══════════════════════════════════════════════════════╝
echo.
pause
