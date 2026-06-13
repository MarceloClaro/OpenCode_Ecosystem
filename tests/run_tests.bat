@echo off
title Auditor de Ambiente - OpenCode Ecosystem
cls

echo ===================================================
echo   Iniciando Auditoria do Ecossistema no WSL...
echo ===================================================
echo.

:: Executa o script de teste dentro do WSL carregando o ambiente interativo
wsl -d Ubuntu -u marcelo bash -ic "bash /mnt/c/Users/marce/Documents/OpenCode_Ecosystem/tests/test_environment.sh"

if %ERRORLEVEL% equ 0 (
    echo.
    echo [OK] O ambiente esta 100%% configurado e funcional!
) else (
    echo.
    echo [ERRO] Foram encontradas falhas na auditoria do ambiente.
)
echo.
pause
