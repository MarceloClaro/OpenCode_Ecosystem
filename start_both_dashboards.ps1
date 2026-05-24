# #############################################################################
# INICIADOR GLOBAL DE DASHBOARDS - ECOSSISTEMA OPENCODE
# #############################################################################
# Este script inicia ambos os dashboards em janelas separadas do PowerShell:
# 1. MiroFish Local Server & Simulation (Porta 8765)
# 2. OpenCode Ecosystem Dashboard (Porta 8081)
# E abre as abas correspondentes no navegador.
# #############################################################################

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ">>> INICIANDO OS DOIS DASHBOARDS DO ECOSSISTEMA OPENCODE" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# 1. Iniciar MiroFish Local Server (Porta 8765)
Write-Host "MiroFish: Iniciando servidor de simulacao na porta 8765..." -ForegroundColor Yellow
$MiroFishCmd = "python skills/mirofish-server/scripts/mirofish_server.py --port 8765"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $MiroFishCmd -WindowStyle Normal

# 2. Iniciar OpenCode Ecosystem Dashboard (Porta 8081)
Write-Host "OpenCode: Iniciando dashboard do ecossistema na porta 8081..." -ForegroundColor Yellow
$StartDashboardPath = "nexus/scripts/start_dashboard.ps1"
Start-Process powershell -ArgumentList "-NoExit", "-File", $StartDashboardPath, "-Port", "8081" -WindowStyle Normal

# 3. Aguardar 3 segundos para inicializacao dos servidores
Start-Sleep -Seconds 3

# 4. Abrir no navegador padrao
Write-Host "Abrindo navegadores..." -ForegroundColor Green
Start-Process "http://localhost:8765"
Start-Process "http://localhost:8081"

Write-Host "----------------------------------------------------------------------" -ForegroundColor Gray
Write-Host "OK: Ambos os dashboards foram iniciados em segundo plano!" -ForegroundColor Green
Write-Host "   - MiroFish Local Server: http://localhost:8765" -ForegroundColor White
Write-Host "   - OpenCode Ecosystem:    http://localhost:8081" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor Cyan
