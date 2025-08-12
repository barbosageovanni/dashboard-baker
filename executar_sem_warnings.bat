@echo off
chcp 65001 >nul
cls

echo ========================================================================
echo           DASHBOARD BAKER - EXECUÇÃO SEM WARNINGS
echo ========================================================================
echo.

echo Escolha uma opção:
echo.
echo 1. Executar dashboard SEM warnings (temporário)
echo 2. CORRIGIR warnings permanentemente
echo 3. Executar dashboard normal
echo.

set /p opcao="Digite sua escolha (1-3): "

if "%opcao%"=="1" (
    echo.
    echo 🚀 Iniciando dashboard sem warnings...
    echo.
    python -W ignore -c "import warnings; warnings.filterwarnings('ignore')" && streamlit run dashboard_baker_web_corrigido.py
    
) else if "%opcao%"=="2" (
    echo.
    echo 🔧 Aplicando correções permanentes...
    echo.
    python corrigir_warnings_dashboard.py
    
    if %errorlevel% equ 0 (
        echo.
        echo ✅ Correções aplicadas!
        echo.
        set /p reiniciar="Deseja iniciar o dashboard agora? (S/N): "
        if /i "%reiniciar%"=="S" (
            echo.
            echo 🚀 Iniciando dashboard corrigido...
            streamlit run dashboard_baker_web_corrigido.py
        )
    )
    
) else if "%opcao%"=="3" (
    echo.
    echo 🚀 Iniciando dashboard normal...
    streamlit run dashboard_baker_web_corrigido.py
    
) else (
    echo.
    echo ❌ Opção inválida!
)

echo.
pause