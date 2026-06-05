<#
.SYNOPSIS
    Instala o Dashboard do ecossistema OpenCode como tarefa agendada do Windows.
.DESCRIPTION
    Cria uma tarefa no Windows Task Scheduler para iniciar o dashboard
    automaticamente no login do usuario e reiniciar se cair.
    Usa schtasks para compatibilidade com Windows 10/11.
.PARAMETER Port
    Porta HTTP (default: 8081)
.PARAMETER Remove
    Remove a tarefa agendada existente
.EXAMPLE
    .\install_dashboard_task.ps1
    .\install_dashboard_task.ps1 -Port 9090
    .\install_dashboard_task.ps1 -Remove
#>

param(
    [int]$Port = 8081,
    [switch]$Remove = $false
)

$TaskName = "OpenCodeDashboard"
$Workspace = Resolve-Path "$PSScriptRoot\..\.."
$PythonCmd = "python"
$ScriptPath = "$Workspace\nexus\dashboard_server.py"
$LogDir = "$Workspace\nexus\dashboard"
$LogFile = "$LogDir\dashboard_task.log"

# Garante diretorio de log
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }

function Write-Log {
    param([string]$Msg)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$Timestamp  $Msg" | Out-File -FilePath $LogFile -Append -Encoding UTF8
    Write-Host "$Timestamp  $Msg"
}

# === REMOVE ===
if ($Remove) {
    Write-Log "Removendo tarefa '$TaskName'..."
    schtasks /DELETE /TN $TaskName /F 2>&1 | Out-Null
    Write-Log "Tarefa removida."
    exit 0
}

# === VERIFICA SCRIPTS ===
if (-not (Test-Path $ScriptPath)) {
    Write-Log "ERRO: Script nao encontrado em $ScriptPath"
    exit 1
}

# === CRIA WRAPPER .BAT ===
$BatPath = "$LogDir\run_dashboard.bat"
@"
@echo off
cd /d "$Workspace"
echo [%date% %time%] Iniciando OpenCode Dashboard > "$LogFile"
python "$ScriptPath" --porta %1 >> "$LogFile" 2>&1
if errorlevel 1 (
    echo [%date% %time%] Dashboard falhou (code %errorlevel%) >> "$LogFile"
    timeout /t 30 /nobreak > nul
    exit %errorlevel%
)
"@ | Out-File -FilePath $BatPath -Encoding ASCII -Force

# === CRIA POWERSHELL WRAPPER (para restart automatico) ===
$PsWrapperPath = "$LogDir\watchdog_wrapper.ps1"
@"
param(`$Port = $Port)
`$Workspace = "$Workspace"
`$LogFile = "$LogDir\dashboard_watchdog.log"
`$PythonCmd = "python"
`$ScriptPath = "$Workspace\nexus\dashboard_server.py"

function Write-Log { param([string]`$Msg)
    `$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "`$Timestamp  `$Msg" | Out-File -FilePath `$LogFile -Append -Encoding UTF8
}

Write-Log "Watchdog wrapper iniciado (PID: `$(Get-Process -Id `$pid).Id)"

while (`$true) {
    Write-Log "Iniciando dashboard server na porta `$Port..."
    `$proc = Start-Process -FilePath `$PythonCmd -ArgumentList "`"`$ScriptPath`" --porta `$Port" `
        -WorkingDirectory `$Workspace -PassThru -NoNewWindow
    `$pid_dashboard = `$proc.Id
    Write-Log "Dashboard iniciado (PID: `$pid_dashboard)"
    
    # Aguarda termino (nunca deve acontecer se estiver saudavel)
    `$proc.WaitForExit()
    `$exitCode = `$proc.ExitCode
    Write-Log "Dashboard encerrado inesperadamente (exit code: `$exitCode). Reiniciando em 10s..."
    
    # Evita restart loop
    Start-Sleep -Seconds 10
}
"@ | Out-File -FilePath $PsWrapperPath -Encoding UTF8 -Force

# === CRIA TAREFA AGENDADA ===
Write-Log "Criando tarefa agendada '$TaskName'..."

# Remove tarefa existente se houver
schtasks /DELETE /TN $TaskName /F 2>&1 | Out-Null

# Cria a tarefa para iniciar no login do usuario
$cmd = "powershell.exe"
$args = "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$PsWrapperPath`" -Port $Port"

$result = schtasks /CREATE /TN $TaskName /TR "$cmd $args" /SC ONLOGON /DELAY 0001:00 /RL HIGHEST /F 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Log "Tarefa '$TaskName' criada com sucesso!"
    Write-Log "Inicia automaticamente no proximo login."
    Write-Log ""
    Write-Log "Comandos uteis:"
    Write-Log "  Iniciar agora: schtasks /RUN /TN $TaskName"
    Write-Log "  Parar:         schtasks /END /TN $TaskName"
    Write-Log "  Status:        schtasks /QUERY /TN $TaskName /V"
    Write-Log "  Logs:          $LogFile"
    Write-Log "  Remover:       .\install_dashboard_task.ps1 -Remove"
    
    # Pergunta se quer iniciar agora
    Write-Host ""
    $res = Read-Host "Iniciar dashboard agora? (S/N)"
    if ($res -eq "S" -or $res -eq "s") {
        schtasks /RUN /TN $TaskName | Out-Null
        Write-Log "Tarefa iniciada. Verifique em http://localhost:$Port"
    }
} else {
    Write-Log "ERRO ao criar tarefa: $result"
    exit 1
}
