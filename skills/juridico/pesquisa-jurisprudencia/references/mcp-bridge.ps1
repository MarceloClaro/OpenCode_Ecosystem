#Requires -Version 5.1

<#
.SYNOPSIS
  Ponte MCP para conectar a CLI jurisprudencias.ps1 ao ecossistema OpenCode.
.DESCRIPTION
  Expoe funcoes da API Jurisprudencias como comandos via stdin/stdout JSON
  no formato MCP (Model Context Protocol).
  Uso: Get-Content .\request.json | .\mcp-bridge.ps1
#>

# carrega CLI
. "$PSScriptRoot\..\scripts\jurisprudencias.ps1" -ErrorAction Stop

function Write-McpResponse {
    param([object] $Data)
    $body = [PSCustomObject]@{ jsonrpc = "2.0"; result = $Data; id = 1 }
    $body | ConvertTo-Json -Depth 10 -Compress
}

function Write-McpError {
    param([string] $Message, [int] $Code = -1)
    $err = [PSCustomObject]@{
        jsonrpc = "2.0"
        error   = [PSCustomObject]@{ code = $Code; message = $Message }
        id      = 1
    }
    $err | ConvertTo-Json -Depth 5 -Compress
}

try {
    $inputJson = Get-Content -Raw -Encoding UTF8 -LiteralPath $env:MCP_REQUEST_PATH
    $req = $inputJson | ConvertFrom-Json

    $method = $req.method
    $params = $req.parameters

    if (-not $method) { throw "Metodo nao especificado" }

    switch ($method) {
        "jur.search" {
            $r = Search-JurDecisions @params
            if (-not $r) { Write-McpResponse @() }
            else { Write-McpResponse @($r) }
        }
        "jur.lookup" {
            $r = Get-JurDecision @params
            if (-not $r) { Write-McpResponse $null }
            else { Write-McpResponse $r }
        }
        "jur.courts" {
            $r = Get-JurCourts
            Write-McpResponse @($r)
        }
        "jur.cache_status" {
            $r = Get-JurCacheStatus *>&1 | Out-String
            Write-McpResponse @{ status = $r.Trim() }
        }
        "jur.cache_clear" {
            Clear-JurCache
            Write-McpResponse @{ cleared = $true }
        }
        "jur.cache_search" {
            $r = Search-JurCache @params
            Write-McpResponse @(if ($r) { $r } else { @() })
        }
        "jur.export" {
            $path = if ($params.OutputPath) { $params.OutputPath } else { ".\jur_offline.html" }
            Export-JurDocs -OutputPath $path
            Write-McpResponse @{ path = $path }
        }
        default {
            Write-McpError "Metodo desconhecido: $method" -Code -32601
        }
    }
} catch {
    Write-McpError $_.Exception.Message -Code -32603
}
