<#
.SYNOPSIS
    Registra o Dashboard v2.0 como tarefa agendada do Windows para iniciar automaticamente.
.DESCRIPTION
    Cria uma tarefa agendada que inicia o dashboard server automaticamente:
    - Ao fazer login do usuario
    - Reinicia se falhar (configuracao nativa do Task Scheduler)
    - Executa minimizado sem janelas
.PARAMETER Port
    Porta HTTP (default: 8081)
.PARAMETER Unregister
    Remove a tarefa agendada existente
.EXAMPLE
    .\register_dashboard_task.ps1
    .\register_dashboard_task.ps1 -Port 9090
    .\register_dashboard_task.ps1 -Unregister
#>

param(
    [int]$Port = 8081,
    [switch]$Unregister = $false
)

$TaskName = "OpenCodeDashboard-v2"
$Workspace = Resolve-Path "$PSScriptRoot\..\.."
$ScriptPath = "$Workspace\nexus\scripts\start_dashboard.ps1"
$LogFile = "$Workspace\nexus\dashboard\task_register.log"

function Write-Log {
    param([string]$Msg)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$Timestamp  $Msg" | Out-File -FilePath $LogFile -Append -Encoding UTF8
    Write-Host "$Timestamp  $Msg"
}

# =============================================================================
# VERIFICAR PRIVILEGIOS
# =============================================================================

$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Log "AVISO: Sem privilegios de administrador."
    Write-Log "A tarefa sera registrada apenas para o usuario atual (nao global)."
    Write-Log "Para registro global (todos os usuarios), execute como Administrador."
}

# =============================================================================
# UNREGISTER
# =============================================================================

if ($Unregister) {
    Write-Log "Removendo tarefa '$TaskName'..."
    try {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
        Write-Log "Tarefa removida com sucesso."
    } catch {
        Write-Log "Tarefa nao encontrada ou ja removida."
    }
    return
}

# =============================================================================
# VERIFICAR DEPENDENCIAS
# =============================================================================

if (-not (Test-Path $ScriptPath)) {
    Write-Log "ERRO: Script nao encontrado: $ScriptPath"
    exit 1
}

if (-not (Test-Path "$Workspace\nexus\dashboard_server.py")) {
    Write-Log "ERRO: dashboard_server.py nao encontrado em $Workspace\nexus\"
    exit 1
}

Write-Log "Verificando dependencias..."
$pythonCheck = python -c "import json, http.server" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Log "ERRO: Python nao encontrado ou sem modulos stdlib. Verifique instalacao."
    exit 1
}
Write-Log "Python OK (stdlib http.server disponivel)"

# =============================================================================
# REGISTRAR TAREFA
# =============================================================================

Write-Log "============================================"
Write-Log "Registrando tarefa agendada: $TaskName"
Write-Log "Script: $ScriptPath"
Write-Log "Porta: $Port"
Write-Log "Workspace: $Workspace"
Write-Log "============================================"

# Remove tarefa se ja existir
try {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Log "Tarefa antiga removida."
    Start-Sleep -Seconds 1
} catch {}

# Argumentos do PowerShell que serao executados
$PwshArgs = "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`" -Port $Port -Silent"

# Cria acao: iniciar PowerShell com o script
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -Command `"& { $ScriptPath -Port $Port -Silent -NoWatchdog }`"" -WorkingDirectory $Workspace

# Acao de repeticao: reiniciar a cada hora se falhar
$Repetition = New-ScheduledTaskTrigger -AtStartup -RandomDelay "00:01:00"

# Trigger ao logon do usuario
$TriggerLogon = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

# Trigger tambem ao iniciar o sistema (se admin)
$Triggers = @($TriggerLogon)

# Configuracoes: executar mesmo sem bateria, reiniciar se falhar
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit (New-TimeSpan -Days 365) `
    -Priority 7

# Criar tarefa
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $Triggers `
        -Settings $Settings `
        -RunLevel Limited `
        -Force

    Write-Log "Tarefa registrada com sucesso!"
    Write-Log ""
    Write-Log "O dashboard iniciara automaticamente quando voce fizer login."
    Write-Log "URL: http://localhost:$Port"
    Write-Log ""
    Write-Log "Comandos uteis:"
    Write-Log "  Ver status: Get-ScheduledTask -TaskName '$TaskName' | fl"
    Write-Log "  Iniciar manualmente: Start-ScheduledTask -TaskName '$TaskName'"
    Write-Log "  Parar: Stop-ScheduledTask -TaskName '$TaskName'"
    Write-Log "  Remover: .\register_dashboard_task.ps1 -Unregister"
    Write-Log "  Log: $Workspace\nexus\dashboard\dashboard.log"

} catch {
    Write-Log "ERRO ao registrar tarefa: $_"
    Write-Log ""
    Write-Log "Tente executar como Administrador ou registre manualmente:"
    Write-Log "  schtasks /create /tn '$TaskName' /tr 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`" -Port $Port -Silent' /sc onlogon /rl limited /f"
    exit 1
}

# Testar iniciando imediatamente
Write-Log ""
Write-Log "Iniciando tarefa imediatamente..."
try {
    Start-ScheduledTask -TaskName $TaskName
    Write-Log "Tarefa iniciada. Verifique o log em $Workspace\nexus\dashboard\dashboard.log"
    Write-Log "Acesse: http://localhost:$Port"
} catch {
    Write-Log "AVISO: Nao foi possivel iniciar automaticamente. Inicie manualmente:"
    Write-Log "  Start-ScheduledTask -TaskName '$TaskName'"
}
