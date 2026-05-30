@echo off
cd /d "C:\Users\marce\.config\opencode"
echo [%date% %time%] Iniciando OpenCode Dashboard > "C:\Users\marce\.config\opencode\nexus\dashboard\dashboard_task.log"
python "C:\Users\marce\.config\opencode\nexus\dashboard_server.py" --porta %1 >> "C:\Users\marce\.config\opencode\nexus\dashboard\dashboard_task.log" 2>&1
if errorlevel 1 (
    echo [%date% %time%] Dashboard falhou (code %errorlevel%) >> "C:\Users\marce\.config\opencode\nexus\dashboard\dashboard_task.log"
    timeout /t 30 /nobreak > nul
    exit %errorlevel%
)
