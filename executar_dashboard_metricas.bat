@echo off
chcp 65001 >nul
cls

echo.
echo 📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊
echo                📊 DASHBOARD BAKER COM MÉTRICAS 📊
echo 📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊
echo.
echo 🎯 Dashboard corrigido que conecta com PostgreSQL
echo 📈 Gera métricas reais baseadas nos dados do banco
echo 💼 Cards estilo profissional como mostrado na tela
echo.

:: Verificar se arquivo existe
if exist "dashboard_com_metricas_postgresql.py" (
    echo ✅ Arquivo dashboard encontrado!
) else (
    echo ❌ Arquivo dashboard_com_metricas_postgresql.py não encontrado!
    echo 💡 Certifique-se que está na pasta correta
    pause
    exit /b 1
)

echo 🔍 Verificando PostgreSQL...

:: Testar conexão PostgreSQL
python -c "import psycopg2; conn = psycopg2.connect(host='localhost', user='postgres', password='senha123', database='dashboard_baker'); print('✅ PostgreSQL OK'); conn.close()" >nul 2>&1

if %errorlevel% equ 0 (
    echo ✅ Conexão PostgreSQL confirmada
) else (
    echo ❌ Problema com PostgreSQL
    echo.
    echo 🔧 POSSÍVEIS SOLUÇÕES:
    echo    1. Verifique se PostgreSQL está rodando
    echo    2. Confirme a senha no arquivo .env
    echo    3. Execute: python status_dashboard.py
    echo.
    
    set /p continuar="Continuar mesmo assim? (S/N): "
    if /i not "%continuar%"=="S" if /i not "%continuar%"=="s" exit /b 1
)

echo.
echo 🚀 INICIANDO DASHBOARD COM MÉTRICAS...
echo.
echo 🌐 O dashboard será aberto em: http://localhost:8501
echo.
echo 📊 FUNCIONALIDADES DISPONÍVEIS:
echo    ✅ Cards com métricas reais do PostgreSQL
echo    ✅ Gráficos de receitas por semana
echo    ✅ Status de recebimento (Pago/Pendente/Vencido)
echo    ✅ Top 10 clientes por valor
echo    ✅ Análise de produtividade (variações de tempo)
echo    ✅ Tabela com registros recentes
echo.
echo ⚠️  IMPORTANTE: Mantenha este terminal aberto!
echo    Para parar o dashboard: Pressione Ctrl+C
echo.

echo Pressione qualquer tecla para iniciar...
pause >nul

:: Executar dashboard
streamlit run dashboard_com_metricas_postgresql.py

echo.
echo ✅ Dashboard encerrado.
echo 💡 Para executar novamente: executar_dashboard_metricas.bat
echo.
pause