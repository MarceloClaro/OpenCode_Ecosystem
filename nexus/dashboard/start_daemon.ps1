# OpenCode Dashboard Daemon
$ErrorActionPreference = "Stop"
$Workspace = "C:\Users\marce\.config\opencode"
$ScriptPath = "$Workspace\nexus\dashboard_server.py"
$LogFile = "$logDir\daemon.log"
$Port = 8081

function Write-Log { param([string]$Msg)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$Timestamp  $Msg" | Out-File -FilePath $LogFile -Append -Encoding UTF8
}

Write-Log "=== OpenCode Dashboard Daemon v1.0 ==="
Write-Log "Porta: $Port | Workspace: $Workspace"
Set-Location -Path $Workspace

while ($true) {
    try {
        Write-Log "Iniciando dashboard server..."
        $proc = Start-Process -FilePath python -ArgumentList ""$ScriptPath" --porta $Port" -NoNewWindow -PassThru -RedirectStandardOutput "C:\Users\marce\.config\opencode\nexus\dashboard\stdout.log" -RedirectStandardError "C:\Users\marce\.config\opencode\nexus\dashboard\stderr.log"
        Write-Log "Dashboard iniciado (PID: $($proc.Id))"
        $proc.WaitForExit()
        $exitCode = $proc.ExitCode
        Write-Log "Dashboard encerrado (exit code: $exitCode). Reiniciando em 5s..."
    } catch {
        Write-Log "ERRO: "
        Write-Log "Reiniciando em 10s..."
    }
    Start-Sleep -Seconds 5
}
