@echo off
chcp 65001 >nul
cls

echo.
echo 🚀 DASHBOARD FINANCEIRO BAKER v3.0
echo ================================
echo.
echo 🔄 Iniciando sistema...
echo.

REM Verificar se arquivo existe
if not exist "dashboard_baker_web_corrigido.py" (
    echo ❌ Arquivo dashboard_baker_web_corrigido.py não encontrado!
    echo.
    echo 💡 Certifique-se que este arquivo .bat está na mesma pasta do dashboard
    pause
    exit /b 1
)

echo ✅ Arquivo dashboard encontrado
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não está instalado ou não está no PATH
    echo.
    echo 💡 Instale Python em: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python disponível
echo.

REM Verificar Streamlit
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Streamlit não está instalado
    echo.
    echo 🔧 Instalando Streamlit...
    pip install streamlit
    
    if %errorlevel% neq 0 (
        echo ❌ Falha na instalação do Streamlit
        pause
        exit /b 1
    )
)

echo ✅ Streamlit disponível
echo.

REM Executar dashboard
echo 🌐 Iniciando Dashboard Baker...
echo.
echo ⚠️  IMPORTANTE:
echo    • Mantenha este terminal aberto
echo    • Dashboard abrirá no navegador
echo    • Para parar: Pressione Ctrl+C
echo.
echo 🌐 Acesse: http://localhost:8501
echo.

streamlit run dashboard_baker_web_corrigido.py

echo.
echo 👋 Dashboard encerrado.
pause
