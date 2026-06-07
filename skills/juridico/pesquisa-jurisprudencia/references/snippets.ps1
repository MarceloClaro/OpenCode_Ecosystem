#Requires -Version 5.1

<#
.SYNOPSIS
  Snippets reutilizaveis para a CLI Jurisprudencias.ai
.DESCRIPTION
  Colecao de trechos prontos para uso em scripts e pipelines.
  Cada snippet eh auto-contido e pode ser copiado para o terminal ou script.
#>

# Requires: scripts/jurisprudencias.ps1
# Setup:
#   . .\scripts\jurisprudencias.ps1
#   $env:JURISPRUDENCIAS_API_TOKEN = 'jur_seu_token_aqui'

# ---------------------------------------------------------------
# Snippet 1: Busca basica com filtro de tribunal e exportacao
# ---------------------------------------------------------------
<#
Parametros:
  $query    - termo de busca (obrigatorio)
  $court    - tribunal (STJ, STF, TJSP, etc.)
  $pages    - numero de paginas (padrao 1, max 5)
  $out      - caminho do arquivo de saida CSV
#>
function Invoke-JurSearchAndExport {
    param(
        [Parameter(Mandatory)] [string]$Query,
        [string]$Court = "STJ",
        [int]$Pages = 1,
        [string]$OutFile = "resultados.csv"
    )
    $all = @()
    for ($p = 1; $p -le $Pages; $p++) {
        $r = Search-JurDecision -Query $Query -Court $Court -Page $p -PageSize 20
        if (-not $r.results) { break }
        $all += $r.results
        Write-Host "Pagina $p/$Pages: $($r.results.Count) resultados"
    }
    $all | Export-Csv -Path $OutFile -NoTypeInformation -Encoding UTF8
    Write-Host "Exportados $($all.Count) resultados para $OutFile"
}

# ---------------------------------------------------------------
# Snippet 2: Resolver processo e gerar relatorio
# ---------------------------------------------------------------
<#
Uso:
  Show-JurCaseBrief -ProcessNumber "0700834-24.2022.8.02.0001"
#>
function Show-JurCaseBrief {
    param([Parameter(Mandatory)] [string]$ProcessNumber)
    $r = Resolve-JurProcess -ProcessNumber $ProcessNumber
    if (-not $r) { Write-Warning "Processo nao encontrado"; return }
    Write-Host "`n=== RELATORIO DO PROCESSO ===" -ForegroundColor Cyan
    Write-Host "Numero: $($r.numero)" -ForegroundColor Yellow
    Write-Host "Classe: $($r.classe_judicial)" -ForegroundColor Yellow
    Write-Host "Assunto: $($r.assunto)" -ForegroundColor Yellow
    Write-Host "Orgao Julgador: $($r.orgao_julgador)" -ForegroundColor Yellow
    Write-Host "Relator: $($r.relator)" -ForegroundColor Yellow
    Write-Host "Data Julgamento: $($r.data_julgamento)" -ForegroundColor Yellow
    Write-Host "Data Publicacao: $($r.data_publicacao)" -ForegroundColor Yellow
    if ($r.ementa) {
        Write-Host "`nEMENTA:" -ForegroundColor Green
        Write-Host $r.ementa
    }
    if ($r.acordao_url) {
        Write-Host "`nAcordao: $($r.acordao_url)" -ForegroundColor Blue
    }
    Write-Host "`n===========================" -ForegroundColor Cyan
}

# ---------------------------------------------------------------
# Snippet 3: Busca multiplos tribunais em paralelo
# ---------------------------------------------------------------
<#
Uso:
  $resultados = Invoke-JurMultiCourtSearch -Query "dano moral" -Courts @("STJ","TJSP","TJPR")
#>
function Invoke-JurMultiCourtSearch {
    param(
        [Parameter(Mandatory)] [string]$Query,
        [string[]]$Courts = @("STJ","STF","TJSP"),
        [int]$PageSize = 10
    )
    $jobs = @()
    foreach ($c in $Courts) {
        $jobs += Start-Job -ScriptBlock {
            param($q, $co, $ps)
            . $using:PSScriptRoot\..\scripts\jurisprudencias.ps1
            Search-JurDecision -Query $q -Court $co -PageSize $ps
        } -ArgumentList $Query, $c, $PageSize
    }
    $all = @()
    foreach ($j in $jobs) {
        $r = Receive-Job -Job $j -Wait
        if ($r.results) { $all += $r.results }
        Remove-Job -Job $j
    }
    return $all
}

# ---------------------------------------------------------------
# Snippet 4: Cache management helpers
# ---------------------------------------------------------------
<#
Uso:
  Show-JurCacheStatus    # mostra tamanho e contagem do cache
  Clear-JurCache         # limpa todo cache
#>
function Show-JurCacheStatus {
    $dir = if ($env:JURISPRUDENCIAS_CACHE_DIR) { $env:JURISPRUDENCIAS_CACHE_DIR } else { "$env:USERPROFILE\.jurisprudencias\cache" }
    if (-not (Test-Path $dir)) { Write-Host "Cache vazio"; return }
    $files = Get-ChildItem -Path $dir -Filter "*.json"
    $total = ($files | Measure-Object Length -Sum).Sum
    Write-Host "Arquivos em cache: $($files.Count)" -ForegroundColor Cyan
    Write-Host "Tamanho total: $('{0:N2}' -f ($total/1KB)) KB" -ForegroundColor Cyan
}

function Clear-JurCache {
    $dir = if ($env:JURISPRUDENCIAS_CACHE_DIR) { $env:JURISPRUDENCIAS_CACHE_DIR } else { "$env:USERPROFILE\.jurisprudencias\cache" }
    if (Test-Path $dir) {
        Remove-Item -Path "$dir\*.json" -Force
        Write-Host "Cache limpo" -ForegroundColor Green
    }
}

# ---------------------------------------------------------------
# Snippet 5: Pipeline integracao com pecas juridicas
# ---------------------------------------------------------------
<#
Uso:
  $ementa = Get-JurEmentaForPeca -Query "honorarios sucumbenciais" -Court "STJ"
  # Use $ementa na sua peca juridica
#>
function Get-JurEmentaForPeca {
    param(
        [Parameter(Mandatory)] [string]$Query,
        [string]$Court = "STJ",
        [int]$MaxPages = 2
    )
    $ementas = @()
    for ($p = 1; $p -le $MaxPages; $p++) {
        $r = Search-JurDecision -Query $Query -Court $Court -Page $p -PageSize 5
        if (-not $r.results) { break }
        foreach ($item in $r.results) {
            if ($item.ementa) {
                $ementas += [PSCustomObject]@{
                    Ementa    = $item.ementa
                    Tribunal  = $item.tribunal
                    Numero    = $item.numero_processo
                    Relator   = $item.relator
                    Data      = $item.data_julgamento
                }
            }
        }
    }
    return $ementas
}
