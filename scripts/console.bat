@echo off
title OpenCode Ecosystem Console
:: Inicia o Daemon de Vocalização em background
start /b powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Users\marce\Documents\OpenCode_Ecosystem\scripts\vocalizer_daemon.ps1"

:: Executa o painel de controle do ecossistema dentro do WSL Ubuntu
wsl -d Ubuntu -u marcelo env PYTHONPATH=/mnt/c/Users/marce/Documents/OpenCode_Ecosystem python3 /mnt/c/Users/marce/Documents/OpenCode_Ecosystem/menu.py

:: Envia o comando de saída para encerrar o daemon
echo EXIT > "C:\Users\marce\Documents\OpenCode_Ecosystem\.vocalizer_cmd"
