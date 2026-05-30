param($Port = 8081)
$Workspace = "C:\Users\marce\.config\opencode"
$LogFile = "C:\Users\marce\.config\opencode\nexus\dashboard\dashboard_watchdog.log"
$PythonCmd = "python"
$ScriptPath = "C:\Users\marce\.config\opencode\nexus\dashboard_server.py"

function Write-Log { param([string]$Msg)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$Timestamp  $Msg" | Out-File -FilePath $LogFile -Append -Encoding UTF8
}

Write-Log "Watchdog wrapper iniciado (PID: $(Get-Process -Id $pid).Id)"

while ($true) {
    Write-Log "Iniciando dashboard server na porta $Port..."
    $proc = Start-Process -FilePath $PythonCmd -ArgumentList ""$ScriptPath" --porta $Port" 
        -WorkingDirectory $Workspace -PassThru -NoNewWindow
    $pid_dashboard = $proc.Id
    Write-Log "Dashboard iniciado (PID: $pid_dashboard)"
    
    # Aguarda termino (nunca deve acontecer se estiver saudavel)
    $proc.WaitForExit()
    $exitCode = $proc.ExitCode
    Write-Log "Dashboard encerrado inesperadamente (exit code: $exitCode). Reiniciando em 10s..."
    
    # Evita restart loop
    Start-Sleep -Seconds 10
}
