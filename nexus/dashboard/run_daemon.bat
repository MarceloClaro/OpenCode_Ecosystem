@echo off
cd /d "C:\Users\marce\.config\opencode"
echo [%date% %time%] Starting OpenCode Dashboard > "nexus\dashboard\bat_daemon.log"
:loop
python "nexus\dashboard_server.py" --porta 8081 >> "nexus\dashboard\bat_daemon.log" 2>&1
echo [%date% %time%] Dashboard exited with code %errorlevel%. Restarting... >> "nexus\dashboard\bat_daemon.log"
timeout /t 5 /nobreak > nul
goto loop
