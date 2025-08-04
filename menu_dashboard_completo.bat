@echo off
chcp 65001 >nul
cls

:inicio
echo.
echo 🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀
echo                🚀 DASHBOARD BAKER - MENU COMPLETO 🚀
echo 🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀
echo.
echo 🎯 Sistema completo funcionando:
echo    ✅ PostgreSQL populado com dados
echo    ✅ Dashboard com métricas reais
echo    ✅ Cards e gráficos profissionais
echo.

:menu
echo 📋 OPÇÕES DISPONÍVEIS:
echo.
echo [1] 📊 Verificar Métricas (testar dados do banco)
echo [2] 🚀 Executar Dashboard com Métricas
echo [3] 🔍 Analisar CSV Original
echo [4] 💾 Popular/Atualizar Banco
echo [5] 🧪 Testes Completos do Sistema
echo [6] 📊 Status Rápido
echo [7] 📚 Mostrar Comandos Úteis
echo [0] ❌ Sair
echo.

set /p opcao="🎯 Escolha uma opção (0-7): "

if "%opcao%"=="1" goto :verificar_metricas
if "%opcao%"=="2" goto :executar_dashboard
if "%opcao%"=="3" goto :analisar_csv
if "%opcao%"=="4" goto :popular_banco
if "%opcao%"=="5" goto :testes_completos
if "%opcao%"=="6" goto :status_rapido
if "%opcao%"=="7" goto :comandos_uteis
if "%opcao%"=="0" goto :sair

echo ❌ Opção inválida!
timeout /t 2 >nul
goto :menu

:verificar_metricas
echo.
echo 📊 VERIFICANDO MÉTRICAS DO BANCO...
echo ===================================
echo.
python verificar_metricas.py
echo.
pause
goto :menu

:executar_dashboard
echo.
echo 🚀 EXECUTANDO DASHBOARD COM MÉTRICAS...
echo =======================================
echo.
if exist "dashboard_com_metricas_postgresql.py" (
    echo ✅ Arquivo encontrado, iniciando...
    echo.
    call executar_dashboard_metricas.bat
) else (
    echo ❌ Arquivo dashboard não encontrado!
    echo 💡 Certifique-se que dashboard_com_metricas_postgresql.py está na pasta
    pause
)
goto :menu

:analisar_csv
echo.
echo 🔍 ANALISANDO ARQUIVO CSV ORIGINAL...
echo ====================================
echo.
python analisar_arquivo_real.py
echo.
pause
goto :menu

:popular_banco
echo.
echo 💾 POPULANDO/ATUALIZANDO BANCO...
echo =================================
echo.
echo [1] 🚀 Usar versão com mapeamento (recomendado)
echo [2] 🔄 Processo completo (diagnóstico + população)
echo [3] 📋 Versão original corrigida
echo.
set /p sub_opcao="Escolha (1-3): "

if "%sub_opcao%"=="1" (
    python popular_banco_com_mapeamento.py
) else if "%sub_opcao%"=="2" (
    call solucao_completa_csv.bat
) else if "%sub_opcao%"=="3" (
    python popular_banco_postgresql_corrigido.py
) else (
    echo ❌ Opção inválida
)
echo.
pause
goto :menu

:testes_completos
echo.
echo 🧪 EXECUTANDO TESTES COMPLETOS...
echo =================================
echo.
python teste_sistema_completo.py
echo.
pause
goto :menu

:status_rapido
echo.
echo 📊 STATUS RÁPIDO DO SISTEMA...
echo ==============================
echo.
call status_dashboard.bat
goto :menu

:comandos_uteis
echo.
echo 📚 COMANDOS ÚTEIS DO SISTEMA
echo ============================
echo.
echo 🚀 EXECUTAR DASHBOARD:
echo    streamlit run dashboard_com_metricas_postgresql.py
echo    executar_dashboard_metricas.bat
echo.
echo 🔍 ANÁLISE E POPULAÇÃO:
echo    python analisar_arquivo_real.py
echo    python popular_banco_com_mapeamento.py
echo    solucao_completa_csv.bat
echo.
echo 🧪 DIAGNÓSTICO:
echo    python verificar_metricas.py
echo    python teste_sistema_completo.py
echo    status_dashboard.bat
echo.
echo 📊 STATUS E VERIFICAÇÃO:
echo    python status_dashboard.py
echo    python diagnostico_csv.py
echo.
echo 🌐 URLs IMPORTANTES:
echo    Dashboard: http://localhost:8501
echo    PostgreSQL: localhost:5432
echo.
echo 📁 ARQUIVOS IMPORTANTES:
echo    dashboard_com_metricas_postgresql.py (dashboard principal)
echo    popular_banco_com_mapeamento.py (população do banco)
echo    .env (configurações do banco)
echo    mapeamento_colunas.txt (mapeamento CSV)
echo.
pause
goto :menu

:sair
echo.
echo 👋 SAINDO DO SISTEMA...
echo.
echo 🎯 RESUMO DO QUE ESTÁ FUNCIONANDO:
echo    ✅ PostgreSQL com dados populados
echo    ✅ Dashboard com métricas reais
echo    ✅ Cards e gráficos profissionais
echo    ✅ Sistema de análise de CSV
echo    ✅ Scripts de manutenção
echo.
echo 🚀 PARA USAR O DASHBOARD:
echo    1. Execute: executar_dashboard_metricas.bat
echo    2. Acesse: http://localhost:8501
echo    3. Veja os cards com suas métricas reais
echo    4. Explore os gráficos interativos
echo.
echo 💡 PARA VOLTAR AO MENU:
echo    Execute: menu_dashboard_completo.bat
echo.

echo Pressione qualquer tecla para sair...
pause >nul