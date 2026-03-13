@echo off
setlocal

REM =====================================================
REM Script de build portátil - Separador de Certificados
REM =====================================================

REM Vai para a raiz do projeto, mesmo executando de dentro da pasta scripts
cd /d "%~dp0.."

echo.
echo ==========================================
echo  GERANDO VERSAO PORTATIL DO PROJETO
echo ==========================================
echo.

REM Verifica se o Python existe
where python >nul 2>nul
if errorlevel 1 (
    echo [ERRO] Python nao foi encontrado no PATH.
    echo Instale o Python na maquina de desenvolvimento e tente novamente.
    pause
    exit /b 1
)

REM Cria ambiente virtual local, se ainda nao existir
if not exist ".venv_portatil" (
    echo [INFO] Criando ambiente virtual .venv_portatil...
    python -m venv .venv_portatil
    if errorlevel 1 (
        echo [ERRO] Nao foi possivel criar o ambiente virtual.
        pause
        exit /b 1
    )
)

REM Ativa o ambiente virtual
call ".venv_portatil\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERRO] Nao foi possivel ativar o ambiente virtual.
    pause
    exit /b 1
)

REM Atualiza ferramentas basicas
echo [INFO] Atualizando pip, setuptools e wheel...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo [ERRO] Falha ao atualizar ferramentas basicas.
    pause
    exit /b 1
)

REM Instala dependencias do projeto
echo [INFO] Instalando dependencias do projeto...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar requirements.txt
    pause
    exit /b 1
)

REM Instala PyInstaller
echo [INFO] Instalando PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo [ERRO] Falha ao instalar PyInstaller.
    pause
    exit /b 1
)

REM Limpa builds anteriores
if exist "build" (
    echo [INFO] Removendo pasta build anterior...
    rmdir /s /q build
)

if exist "dist" (
    echo [INFO] Removendo pasta dist anterior...
    rmdir /s /q dist
)

REM Verifica se o arquivo spec existe
if not exist "separador_certificados.spec" (
    echo [ERRO] Arquivo separador_certificados.spec nao encontrado na raiz do projeto.
    pause
    exit /b 1
)

REM Gera a versao portátil
echo [INFO] Gerando executavel com PyInstaller...
pyinstaller --clean separador_certificados.spec
if errorlevel 1 (
    echo [ERRO] O build falhou.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo  BUILD CONCLUIDO COM SUCESSO
echo ==========================================
echo.
echo Saida esperada:
echo dist\SeparadorCertificados\SeparadorCertificados.exe
echo.

if exist "dist\SeparadorCertificados\SeparadorCertificados.exe" (
    echo [OK] Executavel gerado com sucesso.
) else (
    echo [AVISO] O build terminou, mas o .exe nao foi encontrado no caminho esperado.
)

pause
endlocal