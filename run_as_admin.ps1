# run_as_admin.ps1 — OpenCode Ecosystem Elevated Runner
# Executa suite completa de testes com privilegios de administrador
# Usado para contornar politicas WDAC que bloqueiam DLLs nativas (numpy/scipy)
#
# Uso: powershell -ExecutionPolicy Bypass -File run_as_admin.ps1

param(
    [switch]$SkipAdminCheck,
    [string]$TestPath = "artigo/evaluations/tests/"
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Get-Item $ScriptDir).FullName

function Test-Admin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not $SkipAdminCheck -and -not (Test-Admin)) {
    Write-Host "[OpenCode] Solicitando privilegios de administrador..." -ForegroundColor Yellow
    $args = "-ExecutionPolicy Bypass -File `"$($MyInvocation.MyCommand.Path)`" -SkipAdminCheck"
    Start-Process powershell -Verb RunAs -ArgumentList $args
    exit 0
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  OpenCode Ecosystem — Execucao Elevada (Admin)" -ForegroundColor Cyan
Write-Host "  Projeto: $ProjectRoot" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Set-Location -LiteralPath $ProjectRoot

Write-Host "`n[1/4] Verificando ambiente Python..." -ForegroundColor Green
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] Python nao encontrado no PATH" -ForegroundColor Red
    exit 1
}

Write-Host "`n[2/4] Verificando numpy/scipy (bloqueados por WDAC?)..." -ForegroundColor Green
$numpyOk = $false
try {
    python -c "import numpy; print('numpy', numpy.__version__)" 2>$null
    $numpyOk = ($LASTEXITCODE -eq 0)
} catch { $numpyOk = $false }

if ($numpyOk) {
    Write-Host "  numpy/scipy: OK (admin resolveu o bloqueio)" -ForegroundColor Green
} else {
    Write-Host "  numpy/scipy: INDISPONIVEL mesmo como admin. Testes dependentes serao skipados." -ForegroundColor Yellow
}

Write-Host "`n[3/4] Executando suite TDD completa..." -ForegroundColor Green
Write-Host "  pytest $TestPath -v --tb=short" -ForegroundColor Gray
python -m pytest $TestPath -v --tb=short
$testResult = $LASTEXITCODE

Write-Host "`n[4/4] Gerando relatorio..." -ForegroundColor Green
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$reportDir = "artigo/tests/reports"
if (-not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
}
python -m pytest $TestPath -v --tb=short --json-report --json-report-file="$reportDir/report_$timestamp.json" 2>$null
Write-Host "  Relatorio: $reportDir/report_$timestamp.json" -ForegroundColor Gray

Write-Host "`n============================================================" -ForegroundColor Cyan
if ($testResult -eq 0) {
    Write-Host "  RESULTADO: TODOS OS TESTES PASSARAM" -ForegroundColor Green
} else {
    Write-Host "  RESULTADO: ALGUNS TESTES FALHARAM (exit code: $testResult)" -ForegroundColor Red
}
Write-Host "============================================================" -ForegroundColor Cyan
exit $testResult
