# Script PowerShell para executar Phase B com ProofGeneratorV2

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  PHASE B: Geração de Provas com Templates V2" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date
Write-Host "Inicialização: $($startTime.ToString('dd/MM/yyyy HH:mm:ss'))"
Write-Host ""

# Diretório
$scriptDir = "C:\Users\marce\OpenCode_Ecosystem\aletheia-superhuman-validation"
Set-Location $scriptDir

# Criar resultados dir
if (-not (Test-Path "results")) { New-Item -ItemType Directory -Name "results" | Out-Null }

# Executar Phase B
Write-Host "Executando: python scripts/pipeline_phase_b.py" -ForegroundColor Yellow
Write-Host "Saída: results/phase_b_v2_run.log" -ForegroundColor Yellow
Write-Host ""

# Run with output capture
& python scripts/pipeline_phase_b.py 2>&1 | Tee-Object -FilePath "results/phase_b_v2_run.log"

$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  FASE B COMPLETO" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "Duração: $($duration.ToString('F1'))s"
Write-Host "Log: results/phase_b_v2_run.log"
Write-Host ""

# Verificar resultado
if (Test-Path "results/pipeline_phase_b_results.json") {
    Write-Host "✓ Resultados salvos: results/pipeline_phase_b_results.json" -ForegroundColor Green
    
    # Mostrar summary
    $json = Get-Content "results/pipeline_phase_b_results.json" -Raw | ConvertFrom-Json
    Write-Host ""
    Write-Host "Summary:" -ForegroundColor Yellow
    Write-Host "  Sucesso: $($json.summary.success_count)"
    Write-Host "  Parcial: $($json.summary.partial_count)"
    Write-Host "  Falha: $($json.summary.failed_count)"
} else {
    Write-Host "⚠ Aguardando resultados..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Próximo passo: python scripts/pipeline_phase_c.py (verificação Lean)"
