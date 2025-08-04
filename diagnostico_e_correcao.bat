@echo off
chcp 65001 >nul
cls

echo.
echo 🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍
echo                    🔍 DIAGNÓSTICO E CORREÇÃO CSV 🔍
echo 🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍
echo.
echo 🎯 Este script vai identificar por que não há registros válidos
echo    e executar a versão corrigida do populador do banco
echo.

:menu
echo 📋 OPÇÕES:
echo.
echo [1] 🔍 Executar Diagnóstico do CSV
echo [2] 🚀 Popular Banco (Versão Corrigida)
echo [3] 🔍+🚀 Diagnóstico + Popular Banco
echo [4] 📊 Ver Status do Sistema
echo [0] ❌ Sair
echo.

set /p opcao="Escolha uma opção (0-4): "

if "%opcao%"=="1" goto :diagnostico
if "%opcao%"=="2" goto :popular_corrigido
if "%opcao%"=="3" goto :diagnostico_e_popular
if "%opcao%"=="4" goto :status
if "%opcao%"=="0" goto :end
goto :menu

:diagnostico
echo.
echo 🔍 EXECUTANDO DIAGNÓSTICO DO CSV...
echo ===================================
echo.
python diagnostico_csv.py
echo.
echo ✅ Diagnóstico concluído!
echo 💡 Analise o resultado acima para identificar o problema
echo.
pause
goto :menu

:popular_corrigido
echo.
echo 🚀 EXECUTANDO POPULAR BANCO CORRIGIDO...
echo ========================================
echo.
python popular_banco_postgresql_corrigido.py
echo.
pause
goto :menu

:diagnostico_e_popular
echo.
echo 🔍 FASE 1: DIAGNÓSTICO
echo ======================
echo.
python diagnostico_csv.py
echo.
echo 🔍 Diagnóstico concluído! Pressione qualquer tecla para continuar...
pause >nul
echo.
echo 🚀 FASE 2: POPULAR BANCO CORRIGIDO
echo ===================================
echo.
python popular_banco_postgresql_corrigido.py
echo.
pause
goto :menu

:status
echo.
echo 📊 VERIFICANDO STATUS DO SISTEMA...
echo ===================================
echo.
python status_dashboard.py
echo.
pause
goto :menu

:end
echo.
echo 👋 Saindo...
echo.
pause