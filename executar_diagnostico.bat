@echo off
chcp 65001 >nul
cls

echo.
echo ========================================================================
echo           🔧 DASHBOARD BAKER - SISTEMA DE DIAGNÓSTICO
echo ========================================================================
echo.
echo Este script irá diagnosticar e corrigir problemas de conexão
echo com o banco de dados PostgreSQL do Supabase.
echo.
echo ⚠️ IMPORTANTE: Tenha em mãos suas credenciais do Supabase
echo.

pause

echo.
echo ========================================================================
echo                      ETAPA 1: DIAGNÓSTICO DE CONEXÃO
echo ========================================================================
echo.

python diagnostico_conexao_supabase.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Erro ao executar diagnóstico!
    echo.
    echo Verifique se o Python está instalado:
    python --version
    echo.
    echo Se o Python não estiver instalado, baixe em:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo                      ETAPA 2: IMPORTAÇÃO DE DADOS
echo ========================================================================
echo.
echo Deseja importar dados agora?
echo.

set /p importar="Importar dados? (S/N): "

if /i "%importar%"=="S" (
    echo.
    python importar_dados_planilha.py
    
    if %errorlevel% neq 0 (
        echo.
        echo ❌ Erro na importação!
        pause
        exit /b 1
    )
)

echo.
echo ========================================================================
echo                      ETAPA 3: INICIAR DASHBOARD
echo ========================================================================
echo.
echo Deseja iniciar o Dashboard agora?
echo.

set /p iniciar="Iniciar Dashboard? (S/N): "

if /i "%iniciar%"=="S" (
    echo.
    echo 🚀 Iniciando Dashboard Baker...
    echo.
    echo O dashboard será aberto no navegador em alguns segundos...
    echo Para parar, pressione CTRL+C nesta janela.
    echo.
    streamlit run dashboard_baker_web_corrigido.py
)

echo.
echo ========================================================================
echo                           ✅ PROCESSO CONCLUÍDO
echo ========================================================================
echo.
echo Dashboard Baker está configurado e pronto para uso!
echo.
echo Para executar manualmente:
echo   - Diagnóstico: python diagnostico_conexao_supabase.py
echo   - Importação: python importar_dados_planilha.py
echo   - Dashboard: streamlit run dashboard_baker_web_corrigido.py
echo.

pause