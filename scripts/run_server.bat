@echo off
title OpenCode Ecosystem Server
cls

echo ===================================================
echo   Iniciando OpenCode na pasta de projetos...
echo ===================================================
echo.
echo * Para encerrar o servidor, feche esta janela ou pressione Ctrl+C.
echo.

:: Aguarda 3 segundos em background e abre o navegador
start /b cmd /c "timeout /t 3 >nul && start http://localhost:4096"

:: Inicia o OpenCode no WSL apontando para a pasta projects do ecossistema
wsl -d Ubuntu -u marcelo bash -ic "cd /mnt/c/Users/marce/Documents/OpenCode_Ecosystem/projects && opencode web --hostname 127.0.0.1 --port 4096"
