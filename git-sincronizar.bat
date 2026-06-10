@echo off
REM ============================================================
REM  git-sincronizar.bat - traz as mudancas do remoto (pull --rebase)
REM
REM  Usa rebase para manter o historico linear. Se houver mudancas
REM  locais nao salvas, ele para e avisa (rode git-salvar.bat antes).
REM ============================================================
setlocal
chcp 65001 >nul
cd /d "%~dp0"

git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Esta pasta nao e um repositorio git.
    pause
    exit /b 1
)

for /f "delims=" %%b in ('git branch --show-current') do set "BRANCH=%%b"

REM Bloqueia se houver mudancas pendentes (evita conflito no meio do rebase)
git diff --quiet && git diff --cached --quiet
if errorlevel 1 (
    echo [ATENCAO] Voce tem mudancas locais nao salvas:
    echo.
    git status --short
    echo.
    echo Salve-as antes ^(git-salvar.bat^) ou guarde com 'git stash'.
    pause
    exit /b 1
)

echo === Buscando do remoto ===
git fetch origin || goto erro

git rev-parse --abbrev-ref --symbolic-full-name "@{u}" >nul 2>&1
if errorlevel 1 (
    echo [INFO] A branch %BRANCH% nao tem upstream. Nada a sincronizar.
    pause
    exit /b 0
)

echo.
echo === git pull --rebase origin %BRANCH% ===
git pull --rebase origin "%BRANCH%"
if errorlevel 1 (
    echo.
    echo [ERRO] O rebase encontrou conflitos ou falhou.
    echo   - Resolva os arquivos em conflito, depois: git rebase --continue
    echo   - Ou desfaca tudo com: git rebase --abort
    pause
    exit /b 1
)

echo.
echo === Sincronizado. Estado atual ===
git status --short --branch
echo.
pause
exit /b 0

:erro
echo.
echo [ERRO] Falha ao buscar do remoto. Confira a conexao/credencial.
pause
exit /b 1
endlocal
