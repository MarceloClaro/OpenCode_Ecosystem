# #############################################################################
# INICIADOR DE SERVIÇOS VIA PM2 - ECOSSISTEMA OPENCODE
# #############################################################################
# Este script inicia todos os microsserviços e daemons em segundo plano
# utilizando o gerenciador de processos PM2 com base no arquivo de config.
# #############################################################################

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ">>> INICIANDO OS SERVIÇOS DO ECOSSISTEMA OPENCODE VIA PM2" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# 1. Verifica se PM2 está instalado no sistema
if (Get-Command pm2 -ErrorAction SilentlyContinue) {
    Write-Host "[info] PM2 detectado no sistema." -ForegroundColor Green
    
    # 2. Inicia o arquivo de configuração
    Write-Host "[process] Iniciando de daemons e servidores..." -ForegroundColor Yellow
    pm2 start ecosystem.config.js
    
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Gray
    Write-Host "[OK] Processos iniciados com sucesso!" -ForegroundColor Green
    pm2 list
} else {
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Red
    Write-Host "[ERRO] PM2 não foi detectado no sistema." -ForegroundColor Red
    Write-Host "Para executar no modo de supervisão robusto, instale o PM2 executando:" -ForegroundColor White
    Write-Host "   npm install -g pm2" -ForegroundColor Yellow
    Write-Host "" -ForegroundColor White
    Write-Host "Como alternativa de fallback, você pode executar o script legado:" -ForegroundColor White
    Write-Host "   .\start_both_dashboards.ps1" -ForegroundColor Yellow
}
Write-Host "======================================================================" -ForegroundColor Cyan
