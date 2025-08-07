@echo off
chcp 65001 >nul
cls

echo.
echo 🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀
echo                    🚀 DEPLOY DASHBOARD BAKER SUPABASE 🚀
echo 🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀
echo.
echo 🎯 DEPLOY AUTOMATIZADO EM 5 MINUTOS
echo 📁 MANTÉM: dashboard_baker_web_corrigido.py
echo ☁️ DESTINO: Supabase PostgreSQL
echo.

set "deploy_sucesso=0"

echo 📋 OPÇÕES DE DEPLOY:
echo.
echo [1] 🚀 Deploy Completo (Migrar dados locais → Supabase)
echo [2] 📊 Popular apenas dados CSV → Supabase  
echo [3] ⚙️ Configurar apenas .env para Supabase
echo [4] 🧪 Testar conexão Supabase existente
echo [5] 📄 Ver status atual do sistema
echo [0] ❌ Sair
echo.

set /p opcao="Escolha uma opção (0-5): "

if "%opcao%"=="1" goto :deploy_completo
if "%opcao%"=="2" goto :popular_csv
if "%opcao%"=="3" goto :configurar_env
if "%opcao%"=="4" goto :testar_conexao
if "%opcao%"=="5" goto :ver_status
if "%opcao%"=="0" goto :end
goto :menu_invalido

:deploy_completo
echo.
echo 🚀 EXECUTANDO DEPLOY COMPLETO...
echo ====================================
echo.
echo ⚠️  ESTE PROCESSO IRÁ:
echo    • Conectar ao Supabase
echo    • Criar/atualizar tabela dashboard_baker
echo    • Migrar todos os dados locais
echo    • Configurar arquivo .env
echo    • Testar funcionamento
echo.

set /p continuar="Continuar? (S/N): "
if /i not "%continuar%"=="S" if /i not "%continuar%"=="s" goto :menu_principal

echo.
echo 🔄 Executando deploy completo...
python deploy_supabase_completo.py

if %errorlevel% equ 0 (
    set "deploy_sucesso=1"
    echo ✅ DEPLOY COMPLETO REALIZADO!
) else (
    echo ❌ Erro no deploy completo
)
goto :resultado_final

:popular_csv
echo.
echo 📊 POPULANDO COM DADOS CSV...
echo =============================
echo.
echo 💡 ESTE PROCESSO IRÁ:
echo    • Buscar arquivos CSV na pasta
echo    • Processar e converter dados
echo    • Inserir/atualizar no Supabase
echo    • Manter dados existentes
echo.

set /p continuar="Continuar? (S/N): "
if /i not "%continuar%"=="S" if /i not "%continuar%"=="s" goto :menu_principal

echo.
echo 🔄 Populando dados CSV...
python popular_supabase_csv.py

if %errorlevel% equ 0 (
    set "deploy_sucesso=1"
    echo ✅ DADOS CSV CARREGADOS!
) else (
    echo ❌ Erro ao carregar CSV
)
goto :resultado_final

:configurar_env
echo.
echo ⚙️ CONFIGURANDO AMBIENTE SUPABASE...
echo ===================================
echo.
echo 📋 Precisarei das seguintes informações:
echo    • URL do projeto Supabase
echo    • Senha do banco de dados
echo.

set /p url_supabase="🌐 URL do Supabase (https://xyz.supabase.co): "
set /p senha_banco="🔑 Senha do banco: "

if "%url_supabase%"=="" goto :erro_configuracao
if "%senha_banco%"=="" goto :erro_configuracao

:: Extrair project_id da URL
for /f "tokens=3 delims=/." %%a in ("%url_supabase%") do set project_id=%%a

:: Criar arquivo .env
(
echo # CONFIGURAÇÃO SUPABASE - DASHBOARD BAKER
echo # Configurado em %date% %time%
echo.
echo SUPABASE_HOST=db.%project_id%.supabase.co
echo SUPABASE_DB=postgres  
echo SUPABASE_USER=postgres
echo SUPABASE_PASSWORD=%senha_banco%
echo SUPABASE_PORT=5432
echo.
echo # AMBIENTE
echo ENVIRONMENT=production
) > .env

echo ✅ Arquivo .env configurado!
echo 🔗 Host: db.%project_id%.supabase.co
set "deploy_sucesso=1"
goto :resultado_final

:erro_configuracao
echo ❌ Informações incompletas para configuração
goto :menu_principal

:testar_conexao
echo.
echo 🧪 TESTANDO CONEXÃO SUPABASE...
echo ===============================
echo.

if not exist ".env" (
    echo ❌ Arquivo .env não encontrado
    echo 💡 Execute primeiro: Opção 3 (Configurar .env)
    pause
    goto :menu_principal
)

echo 🔍 Testando conexão com configurações do .env...
python -c "
import os, psycopg2
from dotenv import load_dotenv

load_dotenv()
config = {
    'host': os.getenv('SUPABASE_HOST'),
    'database': 'postgres',  
    'user': 'postgres',
    'password': os.getenv('SUPABASE_PASSWORD'),
    'port': 5432,
    'sslmode': 'require'
}

try:
    conn = psycopg2.connect(**config)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM dashboard_baker')
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    print(f'✅ Conexão OK! {count:,} registros na tabela dashboard_baker')
except Exception as e:
    print(f'❌ Erro de conexão: {e}')
    exit(1)
"

if %errorlevel% equ 0 (
    echo ✅ CONEXÃO FUNCIONANDO!
    set "deploy_sucesso=1"
) else (
    echo ❌ FALHA NA CONEXÃO
)
goto :resultado_final

:ver_status
echo.
echo 📄 STATUS ATUAL DO SISTEMA
echo ==========================
echo.

echo 📁 ARQUIVOS:
if exist "dashboard_baker_web_corrigido.py" (
    echo    ✅ dashboard_baker_web_corrigido.py
) else (
    echo    ❌ dashboard_baker_web_corrigido.py
)

if exist ".env" (
    echo    ✅ .env
    echo       📋 Configuração encontrada
) else (
    echo    ❌ .env (não configurado)
)

if exist "requirements.txt" (
    echo    ✅ requirements.txt
) else (
    echo    ⚠️ requirements.txt (será criado no deploy)
)

echo.
echo 🐍 PYTHON:
python --version 2>nul
if %errorlevel% equ 0 (
    echo    ✅ Python disponível
) else (
    echo    ❌ Python não encontrado
)

echo.
echo 📦 DEPENDÊNCIAS:
python -c "
deps = ['streamlit', 'pandas', 'plotly', 'psycopg2']
for dep in deps:
    try:
        __import__(dep)
        print(f'    ✅ {dep}')
    except ImportError:
        print(f'    ❌ {dep}')
" 2>nul

echo.
echo 🔗 CONEXÃO SUPABASE:
if exist ".env" (
    python -c "
import os
from dotenv import load_dotenv
load_dotenv()
host = os.getenv('SUPABASE_HOST')
if host:
    print(f'    🌐 Host: {host}')
    print('    💡 Execute: Opção 4 (Testar conexão)')
else:
    print('    ❌ Configuração Supabase não encontrada')
" 2>nul
) else (
    echo    ❌ Arquivo .env não existe
    echo    💡 Execute: Opção 3 (Configurar .env)
)

goto :menu_principal

:resultado_final
echo.
echo ========================================================================
if "%deploy_sucesso%"=="1" (
    echo                        🎉 OPERAÇÃO REALIZADA COM SUCESSO!
    echo ========================================================================
    echo.
    echo 🚀 PARA EXECUTAR O DASHBOARD:
    echo    python -m streamlit run dashboard_baker_web_corrigido.py
    echo    OU
    echo    streamlit run dashboard_baker_web_corrigido.py
    echo.
    echo 🌐 DEPOIS DE EXECUTAR, ACESSE:
    echo    http://localhost:8501
    echo.
    echo 💡 DEPLOY EM PRODUÇÃO:
    echo    1. Faça push para GitHub
    echo    2. Use Streamlit Cloud (https://streamlit.io/cloud)
    echo    3. Configure as variáveis de ambiente do .env
    echo.
    
) else (
    echo                         ❌ OPERAÇÃO COM PROBLEMAS
    echo ========================================================================
    echo.
    echo 🔧 SOLUÇÕES:
    echo    • Verifique sua conexão com internet
    echo    • Confirme as credenciais do Supabase
    echo    • Tente executar novamente
    echo    • Use: Opção 5 (Ver status) para diagnóstico
    echo.
)

:menu_principal
echo.
set /p voltar="Voltar ao menu principal? (S/N): "
if /i "%voltar%"=="S" if /i "%voltar%"=="s" (
    cls
    goto :inicio
)
goto :end

:menu_invalido
echo ❌ Opção inválida!
timeout /t 2 >nul
goto :menu_principal

:inicio
echo.
echo 📋 OPÇÕES DE DEPLOY:
echo.
echo [1] 🚀 Deploy Completo (Migrar dados locais → Supabase)
echo [2] 📊 Popular apenas dados CSV → Supabase  
echo [3] ⚙️ Configurar apenas .env para Supabase
echo [4] 🧪 Testar conexão Supabase existente
echo [5] 📄 Ver status atual do sistema
echo [0] ❌ Sair
echo.

set /p opcao="Escolha uma opção (0-5): "

if "%opcao%"=="1" goto :deploy_completo
if "%opcao%"=="2" goto :popular_csv
if "%opcao%"=="3" goto :configurar_env
if "%opcao%"=="4" goto :testar_conexao
if "%opcao%"=="5" goto :ver_status
if "%opcao%"=="0" goto :end
goto :menu_invalido

:end
echo.
echo 👋 Deploy finalizado!
echo 💡 Execute: streamlit run dashboard_baker_web_corrigido.py
pause