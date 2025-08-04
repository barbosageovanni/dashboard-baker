@echo off
chcp 65001 >nul
cls

title Dashboard Baker - Status

echo.
echo ⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡
echo                    ⚡ STATUS DASHBOARD BAKER ⚡
echo ⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡
echo.
echo 🚀 Verificação rápida do sistema (30 segundos)
echo 🕐 %date% %time%
echo.

set status_ok=1
set problemas=0

echo 📁 VERIFICANDO ARQUIVOS...
echo.

:: Verificar arquivos principais
if exist "dashboard_baker_web_corrigido.py" (
    echo    ✅ dashboard_baker_web_corrigido.py
) else (
    echo    ❌ dashboard_baker_web_corrigido.py
    set status_ok=0
    set /a problemas+=1
)

if exist "popular_banco_postgresql.py" (
    echo    ✅ popular_banco_postgresql.py
) else (
    echo    ❌ popular_banco_postgresql.py
    set status_ok=0
    set /a problemas+=1
)

if exist ".env" (
    echo    ✅ .env
) else (
    echo    ❌ .env
    set /a problemas+=1
)

if exist "requirements_postgresql.txt" (
    echo    ✅ requirements_postgresql.txt
) else (
    echo    ⚠️ requirements_postgresql.txt
)

echo.
echo 🐍 VERIFICANDO PYTHON...
echo.

python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ Python disponível
    python --version | findstr /C:"Python"
) else (
    echo    ❌ Python não encontrado
    set status_ok=0
    set /a problemas+=1
)

echo.
echo 📦 VERIFICANDO DEPENDÊNCIAS...
echo.

:: Testar importações principais
python -c "import streamlit" >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ streamlit
) else (
    echo    ❌ streamlit
    set status_ok=0
    set /a problemas+=1
)

python -c "import pandas" >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ pandas
) else (
    echo    ❌ pandas
    set status_ok=0
    set /a problemas+=1
)

python -c "import plotly" >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ plotly
) else (
    echo    ❌ plotly
    set status_ok=0
    set /a problemas+=1
)

python -c "import psycopg2" >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ psycopg2
    set tem_psycopg2=1
) else (
    echo    ❌ psycopg2
    set status_ok=0
    set tem_psycopg2=0
    set /a problemas+=1
)

echo.
echo 🐘 VERIFICANDO POSTGRESQL...
echo.

if %tem_psycopg2% equ 1 (
    :: Testar conexão PostgreSQL
    python -c "import psycopg2; conn = psycopg2.connect(host='localhost', user='postgres', password='senha123'); print('✅ Conexão OK'); conn.close()" >nul 2>&1
    if %errorlevel% equ 0 (
        echo    ✅ Conexão PostgreSQL OK
        
        :: Testar banco dashboard_baker
        python -c "import psycopg2; conn = psycopg2.connect(host='localhost', user='postgres', password='senha123', database='dashboard_baker'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM dashboard_baker'); count = cursor.fetchone()[0]; print(f'✅ Registros: {count}'); conn.close()" 2>nul
        if %errorlevel% equ 0 (
            echo    ✅ Banco dashboard_baker OK
        ) else (
            echo    ⚠️ Banco dashboard_baker - problemas
            set /a problemas+=1
        )
    ) else (
        echo    ❌ Conexão PostgreSQL falhou
        set status_ok=0
        set /a problemas+=1
    )
) else (
    echo    ❌ psycopg2 não disponível
)

echo.
echo 🌐 VERIFICANDO PORTAS...
echo.

:: Verificar porta 8501 (Streamlit)
netstat -an | find ":8501" >nul
if %errorlevel% equ 0 (
    echo    🟡 Porta 8501: Em uso (Streamlit pode estar rodando)
) else (
    echo    ✅ Porta 8501: Livre
)

:: Verificar porta 5432 (PostgreSQL)
netstat -an | find ":5432" >nul
if %errorlevel% equ 0 (
    echo    ✅ Porta 5432: PostgreSQL ativo
) else (
    echo    ⚠️ Porta 5432: PostgreSQL pode não estar rodando
)

echo.
echo ========================================================================

:: Resultado final
if %status_ok% equ 1 if %problemas% leq 1 (
    echo 🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!
    echo.
    echo 🚀 Para iniciar o dashboard:
    echo    iniciar_dashboard_postgresql.bat
    echo    OU
    echo    streamlit run dashboard_baker_web_corrigido.py
    echo.
    echo 🌐 Acesse em: http://localhost:8501
    echo.
    
) else if %problemas% leq 3 (
    echo ⚠️ SISTEMA COM PEQUENOS PROBLEMAS
    echo.
    echo 💡 O sistema pode funcionar, mas com limitações
    echo 🔧 Problemas encontrados: %problemas%
    echo.
    echo 🛠️ SOLUÇÕES RÁPIDAS:
    echo    1. Para popular banco: python popular_banco_postgresql.py
    echo    2. Para instalar dependências: pip install -r requirements_postgresql.txt
    echo    3. Para setup completo: setup_dashboard_postgresql.bat
    echo.
    
) else (
    echo ❌ SISTEMA COM PROBLEMAS SÉRIOS
    echo.
    echo 🚨 Muitos problemas encontrados: %problemas%
    echo 🔧 Execute setup completo antes de usar
    echo.
    echo 🛠️ SOLUÇÕES:
    echo    1. Execute: setup_dashboard_postgresql.bat
    echo    2. Ou: python setup_dashboard_postgresql.py
    echo    3. Para testes detalhados: python teste_sistema_completo.py
    echo.
)

echo ========================================================================
echo.
echo 📋 COMANDOS ÚTEIS DISPONÍVEIS:
echo.
echo 🚀 Iniciar:           iniciar_dashboard_postgresql.bat
echo 📥 Popular banco:     python popular_banco_postgresql.py  
echo 🧪 Testes completos: python teste_sistema_completo.py
echo ⚙️ Setup completo:    setup_dashboard_postgresql.bat
echo 📊 Status detalhado:  python status_dashboard.py --detalhado
echo.

:: Menu de ações rápidas
echo 🎯 AÇÕES RÁPIDAS:
echo.
echo [1] 🚀 Iniciar Dashboard
echo [2] 📥 Popular Banco com CSV
echo [3] 🧪 Executar Testes Completos
echo [4] ⚙️ Setup Completo
echo [5] 📊 Status Detalhado
echo [0] ❌ Sair
echo.

set /p acao="Escolha uma ação (0-5): "

if "%acao%"=="1" goto :iniciar_dashboard
if "%acao%"=="2" goto :popular_banco
if "%acao%"=="3" goto :executar_testes
if "%acao%"=="4" goto :setup_completo
if "%acao%"=="5" goto :status_detalhado
if "%acao%"=="0" goto :sair

goto :menu_invalido

:iniciar_dashboard
echo.
echo 🚀 Iniciando Dashboard Baker...
if exist "iniciar_dashboard_postgresql.bat" (
    call iniciar_dashboard_postgresql.bat
) else (
    echo streamlit run dashboard_baker_web_corrigido.py
    streamlit run dashboard_baker_web_corrigido.py
)
goto :end

:popular_banco
echo.
echo 📥 Executando população do banco...
python popular_banco_postgresql.py
pause
goto :end

:executar_testes
echo.
echo 🧪 Executando testes completos...
python teste_sistema_completo.py
pause
goto :end

:setup_completo
echo.
echo ⚙️ Executando setup completo...
if exist "setup_dashboard_postgresql.bat" (
    call setup_dashboard_postgresql.bat
) else (
    python setup_dashboard_postgresql.py
)
goto :end

:status_detalhado
echo.
echo 📊 Status detalhado...
python status_dashboard.py --detalhado
pause
goto :end

:menu_invalido
echo.
echo ❌ Opção inválida!
timeout /t 2 >nul
goto :end

:sair
echo.
echo 👋 Saindo...
goto :end

:end
echo.
echo 💡 Para verificar status novamente: status_dashboard.bat
echo.
pause