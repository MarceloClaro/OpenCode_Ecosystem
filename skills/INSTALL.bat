@echo off
REM ====================================================
REM  my-crazy-skills — Instalação completa para OpenCode
REM  Execute este script para clonar todas as skills
REM ====================================================

set "SKILLS_DIR=%USERPROFILE%\.config\opencode\skills"
set "CACHE_DIR=%USERPROFILE%\.cache\my-crazy-skills"

echo ╔════════════════════════════════════════════╗
echo ║   my-crazy-skills - Instalador OpenCode   ║
echo ╚════════════════════════════════════════════╝
echo.

REM Clone do repo principal se não existir
if not exist "%CACHE_DIR%" (
    echo Clonando my-crazy-skills...
    git clone --recurse-submodules https://github.com/rahul123gautam/my-crazy-skills.git "%CACHE_DIR%"
) else (
    echo Atualizando my-crazy-skills...
    cd /d "%CACHE_DIR%"
    git pull
    git submodule update --init --recursive
)

echo.
echo Skills baixadas em: %CACHE_DIR%
echo Skills já instaladas manualmente em: %SKILLS_DIR%
echo.
echo Para usar, reinicie o OpenCode.
echo O plugin Superpowers foi adicionado ao opencode.json.
echo.
echo Skills instaladas manualmente (prontas para uso):
echo   - Superpowers (10 skills: brainstorming, writing-plans, executing-plans,
echo     test-driven-development, subagent-driven-development, etc.)
echo   - Anthropic Example Skills
echo   - UI UX Pro Max
echo   - UI Skills (Design Engineer)
echo.
echo Skills restantes disponíveis via submodules em:
echo   %CACHE_DIR%\skills\

pause
