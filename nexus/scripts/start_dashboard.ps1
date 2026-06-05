<#
.SYNOPSIS
    Inicia o Dashboard v2.0 do ecossistema OpenCode com watchdog.
.DESCRIPTION
    Script de inicializacao do Dashboard v2.0 com Chart.js.
    - Inicia o servidor HTTP na porta 8081
    - Watchdog integrado: reinicia automaticamente se cair
    - Gera log em nexus/dashboard/dashboard.log
    - Modo silencioso (minimizado) via -Silent
.PARAMETER Port
    Porta HTTP (default: 8081)
.PARAMETER Silent
    Inicia sem abrir janela do PowerShell
.PARAMETER NoWatchdog
    Executa sem watchdog (unica instancia)
.EXAMPLE
    .\start_dashboard.ps1
    .\start_dashboard.ps1 -Port 9090 -Silent
#>

param(
    [int]$Port = 8081,
    [switch]$Silent = $false,
    [switch]$NoWatchdog = $false
)

$Workspace = Resolve-Path "$PSScriptRoot\..\.."
$PythonCmd = "python"
$ScriptPath = "$Workspace\nexus\dashboard_server.py"
$LogDir = "$Workspace\nexus\dashboard"
$LogFile = "$LogDir\dashboard.log"
$PidFile = "$LogDir\dashboard.pid"

# Garante diretorio de log
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }

function Write-Log {
    param([string]$Msg)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$Timestamp  $Msg" | Out-File -FilePath $LogFile -Append -Encoding UTF8
    if (-not $Silent) { Write-Host "$Timestamp  $Msg" }
}

function Test-Dashboard {
    <#
    .SYNOPSIS
        Verifica se o dashboard esta respondendo via HTTP.
    #>
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$Port/api/dados" -Method GET -TimeoutSec 3 -UseBasicParsing
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

function Start-DashboardInstance {
    <#
    .SYNOPSIS
        Inicia uma instancia do dashboard server.
    #>
    $oldPid = $null
    if (Test-Path $PidFile) {
        $oldPid = Get-Content $PidFile -Raw -ErrorAction SilentlyContinue
        if ($oldPid) {
            $oldPid = $oldPid.Trim()
            $proc = Get-Process -Id $oldPid -ErrorAction SilentlyContinue
            if ($proc -and $proc.ProcessName -match "python") {
                Write-Log "Dashboard ja esta rodando (PID: $oldPid). Reiniciando..."
                Stop-Process -Id $oldPid -Force -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 2
            }
        }
    }

    Write-Log "Iniciando Dashboard v2.0 em http://localhost:$Port"

    if ($Silent) {
        # Inicia minimizado sem janela
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = "python"
        $psi.Arguments = "`"$ScriptPath`" --porta $Port"
        $psi.WorkingDirectory = $Workspace
        $psi.UseShellExecute = $false
        $psi.CreateNoWindow = $true
        $psi.RedirectStandardOutput = $true
        $psi.RedirectStandardError = $true
        $proc = [System.Diagnostics.Process]::Start($psi)
        $procId = $proc.Id

        # Log rotativo (ultimas 500 linhas)
        $output = $proc.StandardOutput.ReadToEnd()
        $err = $proc.StandardError.ReadToEnd()
    } else {
        # Inicia com janela (processo filho)
        $proc = Start-Process -FilePath $PythonCmd -ArgumentList "`"$ScriptPath`" --porta $Port" `
            -WorkingDirectory $Workspace -PassThru -NoNewWindow:$false
        $procId = $proc.Id
    }

    # Salva PID
    $procId | Out-File -FilePath $PidFile -Force -Encoding UTF8
    Write-Log "Dashboard iniciado (PID: $procId)"

    # Aguarda inicializacao
    $tentativas = 0
    do {
        Start-Sleep -Seconds 1
        $tentativas++
        if (Test-Dashboard) {
            Write-Log "Dashboard respondendo em http://localhost:$Port (apos ${tentativas}s)"
            return $true
        }
    } while ($tentativas -lt 15)

    if (-not (Test-Dashboard)) {
        Write-Log "AVISO: Dashboard nao respondeu apos 15s. Verifique $LogFile"
        return $false
    }
    return $true
}

# =============================================================================
# MAIN
# =============================================================================

Write-Log "========================================"
Write-Log "Dashboard v2.0 - Inicializacao"
Write-Log "Porta: $Port | Watchdog: $(-not $NoWatchdog)"
Write-Log "Log: $LogFile"
Write-Log "========================================"

if (-not (Test-Path $ScriptPath)) {
    Write-Log "ERRO: Script nao encontrado em $ScriptPath"
    exit 1
}

# Primeira inicializacao
$ok = Start-DashboardInstance
if (-not $ok) {
    Write-Log "ERRO: Falha na inicializacao do dashboard"
    if (-not $NoWatchdog) {
        Write-Log "Watchdog tentara reiniciar em 30s..."
    }
}

# Watchdog
if (-not $NoWatchdog) {
    Write-Log "Watchdog ativo - monitorando a cada 30s"
    while ($true) {
        Start-Sleep -Seconds 30
        if (-not (Test-Dashboard)) {
            Write-Log "WATCHDOG: Dashboard sem resposta. Reiniciando..."
            Start-DashboardInstance
        } else {
            # Log de heartbeat a cada 5 minutos
            $now = Get-Date
            if ($now.Minute % 5 -eq 0 -and $now.Second -lt 10) {
                Write-Log "[heartbeat] Dashboard OK em http://localhost:$Port"
            }
        }
    }
}

Write-Log "Script finalizado (modo sem watchdog)"
