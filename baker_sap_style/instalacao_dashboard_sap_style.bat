@echo off
chcp 65001 >nul
cls

echo.
echo ████████████████████████████████████████████████████████████████████████
echo ███         💼 SISTEMA BAKER COMPLETO - INSTALAÇÃO TOTAL              ███
echo ████████████████████████████████████████████████████████████████████████
echo.
echo 🎯 SISTEMA INTEGRADO COMPLETO:
echo    ✅ Dashboard Streamlit com auto-detecção
echo    ✅ API REST FastAPI com banco SQLite
echo    ✅ Integração Google Sheets
echo    ✅ Sistema de baixas em tempo real
echo    ✅ Métricas temporais (7 variações)
echo    ✅ Gráficos responsivos completos
echo    ✅ Sincronização automática
echo.

set /p continue="🚀 Instalar sistema completo? (S/N): "
if /i not "%continue%"=="S" if /i not "%continue%"=="s" goto :end

echo.
echo ========================================================================
echo                        🔍 VERIFICAÇÃO DE SISTEMA
echo ========================================================================
echo.

:: Verificar Python
echo [1/4] 🐍 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado
    echo.
    echo 💡 INSTALANDO PYTHON AUTOMATICAMENTE...
    echo 📥 Baixando Python 3.11.6...
    
    :: Criar pasta temporária
    if not exist "temp_python" mkdir temp_python
    cd temp_python
    
    :: Baixar Python
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe' -OutFile 'python_installer.exe'"
    
    if exist "python_installer.exe" (
        echo 🔧 Instalando Python...
        python_installer.exe /passive InstallAllUsers=1 PrependPath=1 Include_pip=1
        
        echo ⏳ Aguardando instalação...
        timeout /t 15 >nul
        
        cd ..
        rmdir /s /q temp_python
        
        :: Verificar novamente
        python --version >nul 2>&1
        if %errorlevel% neq 0 (
            echo ❌ Falha na instalação automática do Python
            echo 💡 Instale manualmente: https://www.python.org/downloads/
            pause
            exit /b 1
        ) else (
            echo ✅ Python instalado com sucesso!
            python --version
        )
    ) else (
        echo ❌ Não foi possível baixar Python
        echo 💡 Instale manualmente: https://www.python.org/downloads/
        pause
        exit /b 1
    )
) else (
    python --version
    echo ✅ Python OK
)

:: Verificar pip
echo [2/4] 📦 Verificando pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip não encontrado
    echo 🔧 Tentando reparar...
    python -m ensurepip --upgrade
    
    pip --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Falha ao configurar pip
        pause
        exit /b 1
    )
)
echo ✅ pip OK

:: Verificar Git (opcional)
echo [3/4] 🔧 Verificando Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Git não encontrado (opcional)
) else (
    echo ✅ Git OK
)

:: Verificar espaço em disco
echo [4/4] 💾 Verificando espaço em disco...
for /f "tokens=3" %%a in ('dir /-c %cd% 2^>nul ^| find "bytes free"') do set free_space=%%a
echo ✅ Espaço disponível verificado

echo.
echo ========================================================================
echo                      📦 INSTALAÇÃO DE DEPENDÊNCIAS
echo ========================================================================
echo.

echo 🔄 Atualizando pip para versão mais recente...
python -m pip install --upgrade pip

echo.
echo 📚 Instalando bibliotecas principais...

:: Core libraries para Dashboard
echo 📊 Dashboard Streamlit...
pip install --upgrade streamlit plotly pandas numpy

:: Libraries para manipulação de dados
echo 📈 Análise de dados...
pip install --upgrade matplotlib seaborn openpyxl xlsxwriter

:: API e banco de dados
echo 🌐 API e banco...
pip install --upgrade fastapi uvicorn sqlite3

:: Google Sheets integration
echo 🔗 Integração Google...
pip install --upgrade gspread google-auth google-auth-oauthlib google-auth-httplib2

:: Utilities
echo 🔧 Utilitários...
pip install --upgrade python-multipart python-jose[cryptography] passlib[bcrypt]

:: Data validation
echo ✅ Validação...
pip install --upgrade pydantic email-validator

echo.
echo ========================================================================
echo                       📁 ESTRUTURA DO PROJETO
echo ========================================================================
echo.

echo 📁 Criando estrutura de pastas...

:: Pastas principais
if not exist "data" (
    mkdir data
    echo ✅ data\ criada (arquivos CSV)
)

if not exist "exports" (
    mkdir exports
    echo ✅ exports\ criada (relatórios)
)

if not exist "backups" (
    mkdir backups
    echo ✅ backups\ criada (backups automáticos)
)

if not exist "logs" (
    mkdir logs
    echo ✅ logs\ criada (logs do sistema)
)

if not exist "credentials" (
    mkdir credentials
    echo ✅ credentials\ criada (credenciais Google)
)

if not exist "database" (
    mkdir database
    echo ✅ database\ criada (banco SQLite)
)

if not exist ".streamlit" (
    mkdir .streamlit
    echo ✅ .streamlit\ criada (configurações)
)

echo.
echo 📄 Criando arquivos de configuração...

:: Requirements.txt completo
(
echo # Dashboard Baker - Sistema Completo
echo # =================================
echo.
echo # Dashboard Web
echo streamlit^>=1.28.0
echo plotly^>=5.17.0
echo pandas^>=1.5.0
echo numpy^>=1.24.0
echo.
echo # Visualização
echo matplotlib^>=3.6.0
echo seaborn^>=0.12.0
echo.
echo # Arquivos
echo openpyxl^>=3.1.0
echo xlsxwriter^>=3.1.0
echo.
echo # API REST
echo fastapi^>=0.104.0
echo uvicorn^>=0.24.0
echo python-multipart^>=0.0.6
echo.
echo # Autenticação e Segurança
echo python-jose[cryptography]^>=3.3.0
echo passlib[bcrypt]^>=1.7.4
echo.
echo # Validação de Dados
echo pydantic^>=2.4.0
echo email-validator^>=2.1.0
echo.
echo # Google Sheets
echo gspread^>=5.12.0
echo google-auth^>=2.23.0
echo google-auth-oauthlib^>=1.1.0
echo google-auth-httplib2^>=0.1.1
echo.
echo # Banco de Dados
echo # SQLite já incluído no Python
echo.
echo # Utilitários
echo requests^>=2.31.0
echo python-dateutil^>=2.8.2
) > requirements.txt
echo ✅ requirements.txt criado

:: Configuração Streamlit
(
echo [theme]
echo primaryColor = "#0f4c75"
echo backgroundColor = "#f8f9fa"
echo secondaryBackgroundColor = "#ffffff"
echo textColor = "#495057"
echo font = "sans serif"
echo.
echo [server]
echo headless = true
echo port = 8501
echo enableCORS = false
echo enableXsrfProtection = false
echo maxUploadSize = 100
echo.
echo [browser]
echo gatherUsageStats = false
echo serverAddress = "localhost"
echo.
echo [runner]
echo magicEnabled = true
echo installTracer = false
echo fixMatplotlib = true
echo.
echo [client]
echo toolbarMode = "minimal"
echo showErrorDetails = true
echo.
echo [global]
echo developmentMode = false
echo suppressDeprecationWarnings = true
) > .streamlit\config.toml
echo ✅ Configuração Streamlit criada

:: Script de inicialização do Dashboard
(
echo @echo off
echo chcp 65001 ^>nul
echo cls
echo.
echo 💼 DASHBOARD BAKER - SISTEMA COMPLETO
echo ====================================
echo.
echo 🚀 Iniciando Dashboard...
echo 🌐 Acesse: http://localhost:8501
echo.
echo ⚠️ IMPORTANTE:
echo    • Mantenha este terminal aberto
echo    • Para parar: Ctrl+C
echo    • API separada em http://localhost:8000
echo.
echo streamlit run dashboard_baker_sap_style.py
echo.
echo pause
) > "iniciar_dashboard.bat"
echo ✅ iniciar_dashboard.bat criado

:: Script de inicialização da API
(
echo @echo off
echo chcp 65001 ^>nul
echo cls
echo.
echo 🌐 API BAKER - SISTEMA REST
echo ============================
echo.
echo 🚀 Iniciando API REST...
echo 📋 Docs: http://localhost:8000/docs
echo 🔧 API: http://localhost:8000
echo.
echo ⚠️ IMPORTANTE:
echo    • Mantenha este terminal aberto
echo    • Para parar: Ctrl+C
echo    • Dashboard em http://localhost:8501
echo.
echo python api_baker.py
echo.
echo pause
) > "iniciar_api.bat"
echo ✅ iniciar_api.bat criado

:: Script de inicialização completa
(
echo @echo off
echo chcp 65001 ^>nul
echo cls
echo.
echo 🚀 SISTEMA BAKER COMPLETO
echo =========================
echo.
echo ⚡ Iniciando todos os serviços...
echo.
echo 📊 Dashboard: http://localhost:8501
echo 🌐 API: http://localhost:8000
echo 📋 Docs: http://localhost:8000/docs
echo.
echo 🔄 Iniciando API em segundo plano...
echo start /min "API Baker" cmd /c "python api_baker.py"
echo.
echo ⏳ Aguardando API inicializar...
echo timeout /t 5 /nobreak ^>nul
echo.
echo 🔄 Iniciando Dashboard...
echo streamlit run dashboard_baker_sap_style.py
echo.
echo pause
) > "iniciar_sistema_completo.bat"
echo ✅ iniciar_sistema_completo.bat criado

:: Script de diagnóstico
(
echo @echo off
echo chcp 65001 ^>nul
echo cls
echo.
echo 🔍 DIAGNÓSTICO SISTEMA BAKER
echo ============================
echo.
echo [1/6] 🐍 Python...
echo python --version
echo.
echo [2/6] 📦 Principais bibliotecas...
echo python -c "import streamlit, fastapi, pandas, plotly; print('✅ Todas OK')"
echo.
echo [3/6] 🌐 Teste API...
echo python -c "import requests; print('✅ Requests OK')"
echo.
echo [4/6] 🔗 Google Sheets...
echo python -c "import gspread; print('✅ Google Sheets OK')" 2^>nul ^|^| echo "⚠️ Google Sheets não instalado"
echo.
echo [5/6] 📁 Estrutura...
echo if exist dashboard_baker_sap_style.py echo ✅ Dashboard
echo if exist api_baker.py echo ✅ API
echo if exist data echo ✅ Pasta data
echo if exist credentials echo ✅ Pasta credentials
echo.
echo [6/6] 🎯 Status geral...
echo echo ✅ Sistema pronto para uso!
echo.
echo pause
) > "diagnostico_sistema.bat"
echo ✅ diagnostico_sistema.bat criado

echo.
echo ========================================================================
echo                        🧪 TESTE DAS INSTALAÇÕES
echo ========================================================================
echo.

echo 🔍 Testando importações principais...

python -c "
try:
    import streamlit as st
    import fastapi
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    import openpyxl
    import sqlite3
    import uvicorn
    import pydantic
    print('✅ TODAS AS BIBLIOTECAS PRINCIPAIS: OK')
except ImportError as e:
    print(f'❌ ERRO DE IMPORTAÇÃO: {e}')
    exit(1)
"

if %errorlevel% neq 0 (
    echo ❌ Problemas nas importações
    echo 🔧 Tentando reinstalar dependências...
    pip install --force-reinstall -r requirements.txt
    
    echo 🧪 Testando novamente...
    python -c "import streamlit, fastapi, pandas, plotly; print('✅ Bibliotecas corrigidas!')"
    if %errorlevel% neq 0 (
        echo ❌ Persistem problemas - verifique manualmente
        pause
        exit /b 1
    )
) else (
    echo ✅ Todas as bibliotecas funcionando!
)

echo.
echo 🧪 Testando Google Sheets (opcional)...
python -c "
try:
    import gspread
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import Flow
    from google.oauth2.credentials import Credentials
    from google.oauth2.service_account import Credentials as ServiceAccountCredentials
    print('✅ Google Sheets: OK')
except ImportError as e:
    print('⚠️ Google Sheets: Dependências ausentes (instalando...)')
    exit(1)
" 2>nul

if %errorlevel% neq 0 (
    echo 🔧 Instalando dependências Google Sheets...
    pip install gspread google-auth google-auth-oauthlib google-auth-httplib2
    echo ✅ Google Sheets instalado
) else (
    echo ✅ Google Sheets OK
)

echo.
echo ========================================================================
echo                    📊 CRIAÇÃO DE DADOS DE EXEMPLO
echo ========================================================================
echo.

echo 📊 Criando dados de exemplo para teste...

python -c "
import pandas as pd
import random
from datetime import datetime, timedelta

print('🔄 Gerando dados de exemplo...')

# Criar dados realistas
dados = []
clientes = ['Empresa A Ltda', 'Transportes B', 'Logística C', 'Comércio D S/A', 'Indústria E']
veiculos = ['ABC-1234', 'DEF-5678', 'GHI-9012', 'JKL-3456', 'MNO-7890']

for i in range(100):
    dados.append({
        'Numero_CTE': 40000 + i,
        'Destinatario_Nome': random.choice(clientes),
        'Veiculo_Placa': random.choice(veiculos),
        'Valor_Total': random.randint(800, 15000),
        'Data_Emissao_CTE': (datetime.now() - timedelta(days=random.randint(1, 300))).strftime('%d/%b/%y'),
        'Numero_Fatura': f'FAT{5000 + i}' if random.random() > 0.15 else '',
        'Data_Baixa': (datetime.now() - timedelta(days=random.randint(1, 100))).strftime('%d/%m/%Y') if random.random() > 0.35 else '',
        'Observacoes': f'Operação {i} - Baker' if random.random() > 0.5 else '',
        'Status_Processo': 'Finalizado' if random.random() > 0.25 else 'Em andamento',
        'Data_RQ_TMC': (datetime.now() - timedelta(days=random.randint(1, 250))).strftime('%d/%b/%y'),
        'Primeiro_Envio': (datetime.now() - timedelta(days=random.randint(1, 200))).strftime('%d/%b/%y'),
        'Data_Atesto': (datetime.now() - timedelta(days=random.randint(1, 150))).strftime('%d/%b/%y') if random.random() > 0.3 else ''
    })

df = pd.DataFrame(dados)
df.to_csv('data/exemplo_completo_baker.csv', sep=';', index=False, encoding='cp1252')
print(f'✅ Arquivo criado: data/exemplo_completo_baker.csv')
print(f'📊 {len(df)} registros com todas as variações de tempo')
print(f'💰 Valor total: R$ {df[\"Valor_Total\"].sum():,.2f}')
print('📋 Colunas:', ', '.join(df.columns.tolist()))
"

if %errorlevel% equ 0 (
    echo ✅ Dados de exemplo criados com sucesso!
) else (
    echo ⚠️ Problemas ao criar dados de exemplo
)

echo.
echo ========================================================================
echo                       📋 CONFIGURAÇÃO GOOGLE SHEETS
echo ========================================================================
echo.

echo 📋 Preparando configuração Google Sheets...

:: Criar arquivo de instruções
(
echo # CONFIGURAÇÃO GOOGLE SHEETS - DASHBOARD BAKER
echo ============================================
echo.
echo ## PASSO 1: Criar Projeto Google Cloud
echo 1. Acesse: https://console.cloud.google.com/
echo 2. Crie novo projeto: "Dashboard Baker"
echo 3. Anote o ID do projeto
echo.
echo ## PASSO 2: Ativar APIs
echo 1. Vá em "APIs e Serviços" ^> "Biblioteca"
echo 2. Ative as APIs:
echo    - Google Sheets API
echo    - Google Drive API
echo.
echo ## PASSO 3: Criar Credenciais
echo ### Para Desenvolvimento ^(OAuth 2.0^):
echo 1. Vá em "Credenciais" ^> "Criar Credenciais"
echo 2. Escolha "ID do cliente OAuth 2.0"
echo 3. Tipo: "Aplicativo para computador"
echo 4. Nome: "Dashboard Baker Desktop"
echo 5. Baixe o arquivo JSON
echo 6. Renomeie para: oauth_credentials.json
echo 7. Coloque na pasta: credentials/
echo.
echo ### Para Produção ^(Service Account^):
echo 1. Vá em "Credenciais" ^> "Criar Credenciais"
echo 2. Escolha "Conta de serviço"
echo 3. Nome: "baker-service-account"
echo 4. Conceda papel: "Editor"
echo 5. Baixe a chave JSON
echo 6. Renomeie para: service_account.json
echo 7. Coloque na pasta: credentials/
echo.
echo ## PASSO 4: Configurar Planilha
echo 1. Crie uma planilha no Google Sheets
echo 2. Compartilhe com o email da service account
echo 3. Copie a URL da planilha
echo 4. Use no dashboard
echo.
echo ## PASSO 5: Testar
echo 1. Execute: diagnostico_sistema.bat
echo 2. Teste a conexão no dashboard
echo 3. Verifique sincronização
echo.
echo DICAS:
echo - Use OAuth para desenvolvimento
echo - Use Service Account para produção
echo - Mantenha credenciais seguras
echo - Faça backup das configurações
) > "credentials\CONFIGURACAO_GOOGLE_SHEETS.md"
echo ✅ Guia de configuração Google Sheets criado

:: Criar arquivo de exemplo de credenciais
(
echo {
echo   "exemplo_oauth": {
echo     "installed": {
echo       "client_id": "SEU_CLIENT_ID.apps.googleusercontent.com",
echo       "project_id": "seu-projeto-baker",
echo       "auth_uri": "https://accounts.google.com/o/oauth2/auth",
echo       "token_uri": "https://oauth2.googleapis.com/token",
echo       "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
echo       "client_secret": "SUA_CLIENT_SECRET",
echo       "redirect_uris": ["http://localhost"]
echo     }
echo   },
echo   "exemplo_service_account": {
echo     "type": "service_account",
echo     "project_id": "seu-projeto-baker",
echo     "private_key_id": "key_id",
echo     "private_key": "-----BEGIN PRIVATE KEY-----\nSUA_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",
echo     "client_email": "baker-service@seu-projeto.iam.gserviceaccount.com",
echo     "client_id": "123456789",
echo     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
echo     "token_uri": "https://oauth2.googleapis.com/token",
echo     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
echo     "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/baker-service%40seu-projeto.iam.gserviceaccount.com"
echo   }
echo }
) > "credentials\exemplo_credenciais.json"
echo ✅ Exemplo de credenciais criado

echo.
echo ████████████████████████████████████████████████████████████████████████
echo ███                  ✅ INSTALAÇÃO CONCLUÍDA!                         ███
echo ████████████████████████████████████████████████████████████████████████
echo.
echo 🎉 SISTEMA BAKER COMPLETO INSTALADO COM SUCESSO!
echo.
echo 📊 COMPONENTES INSTALADOS:
echo    ✅ Dashboard Streamlit adaptativo
echo    ✅ API REST FastAPI completa
echo    ✅ Integração Google Sheets
echo    ✅ Sistema de baixas automatizado
echo    ✅ 7 variações de tempo para produtividade
echo    ✅ Gráficos responsivos e interativos
echo    ✅ Banco SQLite para API
echo    ✅ Autenticação e segurança
echo    ✅ Sincronização em tempo real
echo.
echo 🚀 COMO USAR:
echo.
echo    1️⃣ DASHBOARD ISOLADO:
echo       👉 Execute: iniciar_dashboard.bat
echo       🌐 Acesse: http://localhost:8501
echo.
echo    2️⃣ API ISOLADA:
echo       👉 Execute: iniciar_api.bat  
echo       🌐 Acesse: http://localhost:8000
echo       📋 Docs: http://localhost:8000/docs
echo.
echo    3️⃣ SISTEMA COMPLETO:
echo       👉 Execute: iniciar_sistema_completo.bat
echo       📊 Dashboard + API funcionando juntos
echo.
echo 🔧 CONFIGURAÇÃO GOOGLE SHEETS:
echo    📋 Leia: credentials\CONFIGURACAO_GOOGLE_SHEETS.md
echo    🔑 Use: credentials\exemplo_credenciais.json como base
echo.
echo 📁 ESTRUTURA CRIADA:
echo    📂 %cd%
echo    ├── 📁 data\              (seus arquivos CSV)
echo    ├── 📁 exports\           (relatórios gerados)
echo    ├── 📁 backups\           (backups automáticos)
echo    ├── 📁 logs\              (logs do sistema)
echo    ├── 📁 credentials\       (credenciais Google)
echo    ├── 📁 database\          (banco SQLite API)
echo    ├── 📁 .streamlit\        (configurações)
echo    ├── 📄 dashboard_baker_sap_style.py
echo    ├── 📄 api_baker.py
echo    ├── 📄 requirements.txt
echo    └── 📄 iniciar_sistema_completo.bat
echo.
echo 🧪 TESTE RÁPIDO:
echo    👉 Execute: diagnostico_sistema.bat
echo    👉 Use arquivo: data\exemplo_completo_baker.csv
echo.
echo 💡 PRÓXIMOS PASSOS:
echo    1. Configure Google Sheets (se necessário)
echo    2. Execute o sistema completo
echo    3. Carregue seus dados CSV
echo    4. Explore todas as funcionalidades
echo    5. Configure sincronização automática
echo.
echo 🎯 FUNCIONALIDADES PRINCIPAIS:
echo    ✅ Auto-detecção de estrutura CSV
echo    ✅ Dashboard responsivo estilo SAP
echo    ✅ Sistema de baixas em tempo real
echo    ✅ API REST para integrações
echo    ✅ Métricas financeiras detalhadas
echo    ✅ 7 variações de tempo produtividade
echo    ✅ Gráficos interativos Plotly
echo    ✅ Sincronização Google Sheets
echo    ✅ Backup automático
echo    ✅ Logs e monitoramento
echo.

:end
echo.
echo 🎊 Instalação finalizada!
echo 💡 Execute: iniciar_sistema_completo.bat para começar
echo.
pause