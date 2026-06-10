@echo off
REM ============================================================
REM  git-status.bat - mostra o estado do repositorio
REM ============================================================
setlocal
chcp 65001 >nul
cd /d "%~dp0"

REM Confere se estamos dentro de um repositorio git
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Esta pasta nao e um repositorio git.
    pause
    exit /b 1
)

for /f "delims=" %%b in ('git branch --show-current') do set "BRANCH=%%b"

echo.
echo === BRANCH: %BRANCH% ===
echo.
echo === MUDANCAS LOCAIS ===
git status --short
if errorlevel 1 goto fim
git diff --quiet && git diff --cached --quiet && echo   (nenhuma mudanca pendente)

echo.
echo === RELACAO COM O REMOTO ===
git fetch --quiet 2>nul
for /f %%a in ('git rev-list --count "@{u}..HEAD" 2^>nul') do set "AHEAD=%%a"
for /f %%a in ('git rev-list --count "HEAD..@{u}" 2^>nul') do set "BEHIND=%%a"
if not defined AHEAD (
    echo   Sem upstream configurado para esta branch.
) else (
    echo   Commits a enviar ^(ahead^):  %AHEAD%
    echo   Commits a receber ^(behind^): %BEHIND%
)

echo.
echo === ULTIMOS 10 COMMITS ===
git --no-pager log --oneline -10

:fim
echo.
pause
endlocal
