@echo off
REM ============================================================
REM  git-salvar.bat - adiciona, commita e envia as mudancas
REM
REM  Uso:
REM    git-salvar.bat                 (pergunta a mensagem)
REM    git-salvar.bat "minha msg"     (usa a mensagem do argumento)
REM ============================================================
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Esta pasta nao e um repositorio git.
    pause
    exit /b 1
)

REM Ha algo para commitar?
git status --porcelain > "%TEMP%\_gitsave.txt"
for %%A in ("%TEMP%\_gitsave.txt") do set "TAM=%%~zA"
del "%TEMP%\_gitsave.txt" >nul 2>&1
if "%TAM%"=="0" (
    echo Nada para salvar: a arvore de trabalho esta limpa.
    pause
    exit /b 0
)

echo.
echo === MUDANCAS QUE SERAO SALVAS ===
git status --short
echo.

REM Mensagem: argumento tem prioridade; senao pergunta
set "MSG=%~1"
if "%MSG%"=="" set /p "MSG=Mensagem do commit: "
if "%MSG%"=="" (
    echo [ERRO] Mensagem vazia. Cancelado.
    pause
    exit /b 1
)

echo.
echo === git add -A ===
git add -A || goto erro

echo.
echo === git commit ===
git commit -m "%MSG%" || goto erro

echo.
for /f "delims=" %%b in ('git branch --show-current') do set "BRANCH=%%b"

REM Se nao houver upstream, configura no primeiro push
git rev-parse --abbrev-ref --symbolic-full-name "@{u}" >nul 2>&1
if errorlevel 1 (
    echo === Primeiro push: definindo upstream origin/%BRANCH% ===
    git push -u origin "%BRANCH%" || goto erro_push
) else (
    echo === git push origin %BRANCH% ===
    git push origin "%BRANCH%" || goto erro_push
)

echo.
echo === CONCLUIDO com sucesso ===
pause
exit /b 0

:erro
echo.
echo [ERRO] Um comando git falhou. Veja a mensagem acima. Nada foi enviado.
pause
exit /b 1

:erro_push
echo.
echo [ERRO] O push falhou. Causas comuns:
echo   - O remoto tem commits que voce nao tem: rode git-sincronizar.bat e tente de novo.
echo   - Sem permissao/credencial: confira o acesso ao GitHub.
pause
exit /b 1
endlocal
