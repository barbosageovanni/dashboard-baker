@echo off
chcp 65001 >nul
cls

echo.
echo ████████████████████████████████████████████████████████████████████████
echo ███        💼 TESTE DASHBOARD BAKER - ESTILO SAP TAULIA               ███
echo ████████████████████████████████████████████████████████████████████████
echo.
echo 🎯 Script de teste e demonstração do dashboard profissional
echo.

:: Verificar se todos os arquivos estão presentes
echo ========================================================================
echo                       🔍 VERIFICAÇÃO DE ARQUIVOS
echo ========================================================================
echo.

set arquivos_ok=1

echo [1/4] 📄 Verificando arquivo principal...
if exist "dashboard_baker_sap_style.py" (
    echo ✅ dashboard_baker_sap_style.py encontrado
) else (
    echo ❌ dashboard_baker_sap_style.py NÃO encontrado
    set arquivos_ok=0
)

echo [2/4] ⚙️ Verificando configuração Streamlit...
if exist ".streamlit\config.toml" (
    echo ✅ .streamlit\config.toml encontrado
) else (
    echo ⚠️ .streamlit\config.toml não encontrado - criando...
    if not exist ".streamlit" mkdir .streamlit
    
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
    echo.
    echo [browser]
    echo gatherUsageStats = false
    ) > .streamlit\config.toml
    
    echo ✅ Configuração criada automaticamente
)

echo [3/4] 📋 Verificando requirements.txt...
if exist "requirements.txt" (
    echo ✅ requirements.txt encontrado
) else (
    echo ⚠️ requirements.txt não encontrado - criando...
    (
    echo pandas^>=1.5.0
    echo streamlit^>=1.28.0
    echo plotly^>=5.17.0
    echo openpyxl^>=3.1.0
    ) > requirements.txt
    echo ✅ requirements.txt criado
)

echo [4/4] 📁 Verificando estrutura de pastas...
if not exist "data" mkdir data && echo ✅ data\ criada
if not exist "exports" mkdir exports && echo ✅ exports\ criada
if not exist "backups" mkdir backups && echo ✅ backups\ criada

echo.
if %arquivos_ok%==0 (
    echo ❌ ERRO: Arquivos essenciais não encontrados
    echo 💡 Certifique-se de ter o arquivo dashboard_baker_sap_style.py
    pause
    exit /b 1
)

:: Verificar dependências
echo ========================================================================
echo                      📦 VERIFICAÇÃO DE DEPENDÊNCIAS  
echo ========================================================================
echo.

echo 🐍 Testando Python...
python --version 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado - execute instalacao_completa.bat primeiro
    pause
    exit /b 1
) else (
    echo ✅ Python OK
)

echo.
echo 📚 Testando bibliotecas principais...

python -c "
try:
    import pandas as pd
    print('✅ pandas:', pd.__version__)
except ImportError:
    print('❌ pandas não encontrado')
    exit(1)

try:
    import streamlit as st
    print('✅ streamlit:', st.__version__)
except ImportError:
    print('❌ streamlit não encontrado')
    exit(1)
    
try:
    import plotly
    print('✅ plotly:', plotly.__version__)
except ImportError:
    print('❌ plotly não encontrado')
    exit(1)
    
try:
    import openpyxl
    print('✅ openpyxl: OK')
except ImportError:
    print('❌ openpyxl não encontrado')
    exit(1)
    
print('🎉 Todas as dependências OK!')
"

if %errorlevel% neq 0 (
    echo.
    echo ⚠️ Dependências não encontradas - instalando...
    pip install pandas streamlit plotly openpyxl
    
    echo 🔄 Testando novamente...
    python -c "import pandas, streamlit, plotly, openpyxl; print('✅ Dependências instaladas com sucesso!')"
    
    if %errorlevel% neq 0 (
        echo ❌ Falha na instalação - execute instalacao_completa.bat
        pause
        exit /b 1
    )
)

:: Verificar se porta está livre
echo.
echo ========================================================================
echo                        🌐 VERIFICAÇÃO DE REDE
echo ========================================================================
echo.

echo 🔍 Verificando porta 8501...
netstat -an | find ":8501" >nul
if %errorlevel% equ 0 (
    echo ⚠️ Porta 8501 está em uso
    echo 🛑 Tentando finalizar processos Streamlit...
    
    taskkill /f /im streamlit.exe >nul 2>&1
    taskkill /f /im python.exe /fi "WINDOWTITLE eq *streamlit*" >nul 2>&1
    
    timeout /t 3 >nul
    
    netstat -an | find ":8501" >nul
    if %errorlevel% equ 0 (
        echo ⚠️ Usando porta alternativa 8502
        set PORT=8502
    ) else (
        echo ✅ Porta 8501 liberada
        set PORT=8501
    )
) else (
    echo ✅ Porta 8501 disponível
    set PORT=8501
)

:: Criar dados de exemplo se necessário
echo.
echo ========================================================================
echo                        📊 DADOS DE DEMONSTRAÇÃO
echo ========================================================================
echo.

if not exist "data\exemplo_dashboard.csv" (
    echo 📝 Criando arquivo de exemplo para demonstração...
    
    python -c "
import pandas as pd
import random
from datetime import datetime, timedelta

# Criar dados de exemplo
dados = []
for i in range(100):
    dados.append({
        'Número Cte': 20000 + i,
        'Destinatário - Nome': f'Cliente {chr(65 + (i %% 26))}',
        'Veículo - Placa': f'ABC-{1000 + (i %% 50)}',
        ' Total ': f'R$ {random.randint(500, 5000)},00',
        'Data emissão Cte': (datetime.now() - timedelta(days=random.randint(1, 90))).strftime('%d/%b/%y'),
        'Fatura': f'FAT{1000 + i}' if random.random() > 0.2 else '',
        'Data baixa': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%d/%m/%Y') if random.random() > 0.3 else '',
        'OBSERVAÇÃO': ''
    })

df = pd.DataFrame(dados)
df.to_csv('data/exemplo_dashboard.csv', sep=';', index=False, encoding='cp1252')
print('✅ Arquivo de exemplo criado: data/exemplo_dashboard.csv')
"
    
    if %errorlevel% equ 0 (
        echo ✅ Dados de exemplo criados com sucesso
    ) else (
        echo ⚠️ Não foi possível criar dados de exemplo
    )
) else (
    echo ✅ Arquivo de exemplo já existe
)

:: Iniciar dashboard
echo.
echo ████████████████████████████████████████████████████████████████████████
echo ███                    🚀 INICIANDO DASHBOARD                         ███
echo ████████████████████████████████████████████████████████████████████████
echo.
echo 💼 Dashboard Baker - Estilo SAP Taulia Profissional
echo ═══════════════════════════════════════════════════
echo.
echo ✅ VERIFICAÇÕES CONCLUÍDAS:
echo    📄 Arquivo principal: dashboard_baker_sap_style.py
echo    ⚙️ Configuração: .streamlit\config.toml  
echo    📦 Dependências: pandas, streamlit, plotly
echo    🌐 Porta: %PORT%
echo    📊 Dados: Arquivo de exemplo disponível
echo.
echo 🎯 CARACTERÍSTICAS DO DASHBOARD:
echo    • Design profissional estilo SAP Taulia
echo    • Cards de métricas elegantes
echo    • Gráficos interativos modernos
echo    • Paleta de cores corporativa
echo    • Layout responsivo
echo.
echo 🌐 ACESSO:
echo    URL: http://localhost:%PORT%
echo.
echo ⚠️ IMPORTANTE:
echo    • Mantenha este terminal ABERTO durante o uso
echo    • Para parar: Pressione Ctrl+C
echo    • Se não abrir automaticamente, use a URL acima
echo.
echo 🔄 Iniciando em 3 segundos...
timeout /t 3 /nobreak >nul

:: Verificar novamente se a porta mudou
if "%PORT%"=="8502" (
    echo 🚀 Iniciando na porta alternativa 8502...
    streamlit run dashboard_baker_sap_style.py --server.port 8502
) else (
    echo 🚀 Iniciando na porta padrão 8501...
    streamlit run dashboard_baker_sap_style.py
)

:: Pós-execução
echo.
echo ========================================================================
echo                          👋 DASHBOARD ENCERRADO
echo ========================================================================
echo.
echo 💡 FEEDBACK:
echo    • O dashboard funcionou conforme esperado?
echo    • O design está similar ao SAP Taulia?
echo    • Todas as funcionalidades estão operacionais?
echo.
echo 🔧 TROUBLESHOOTING:
echo    • Erro de importação: Execute instalacao_completa.bat
echo    • Porta ocupada: Use fix_streamlit_rapido.bat  
echo    • Arquivo não encontrado: Verifique os nomes dos arquivos
echo.
echo 📁 ARQUIVOS IMPORTANTES:
echo    📄 dashboard_baker_sap_style.py (arquivo principal)
echo    ⚙️ .streamlit\config.toml (configurações)
echo    📊 data\exemplo_dashboard.csv (dados de teste)
echo.
echo ✅ Para usar novamente: Execute este script ou use
echo    streamlit run dashboard_baker_sap_style.py
echo.
pause