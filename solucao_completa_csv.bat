@echo off
chcp 65001 >nul
cls

echo.
echo 🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯
echo                    🎯 SOLUÇÃO COMPLETA CSV 🎯
echo 🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯
echo.
echo 📋 Este script resolve o problema "0 registros válidos" de forma definitiva
echo 🔍 Analisa seu arquivo CSV real e mapeia as colunas corretamente
echo 💾 Popula o banco PostgreSQL com os dados corretos
echo.

echo 📂 ARQUIVO ESPERADO: "Status Faturamento   Ctes vs Faturas vs Atestos.csv"
echo.

:: Verificar se arquivo existe
if exist "Status Faturamento   Ctes vs Faturas vs Atestos.csv" (
    echo ✅ Arquivo CSV encontrado!
) else (
    echo ❌ Arquivo CSV não encontrado!
    echo.
    echo 📋 Arquivos CSV na pasta atual:
    dir /b *.csv 2>nul
    
    echo.
    echo 💡 SOLUÇÕES:
    echo    1. Certifique-se que o arquivo está nesta pasta
    echo    2. Verifique se o nome está exato (com espaços)
    echo    3. O script pode trabalhar com outros arquivos CSV também
    echo.
    
    set /p continuar="Continuar mesmo assim? (S/N): "
    if /i not "%continuar%"=="S" if /i not "%continuar%"=="s" goto :end
)

echo.
echo 🎯 PROCESSO EM 3 ETAPAS:
echo    1️⃣ Analisar arquivo CSV real
echo    2️⃣ Mapear colunas automaticamente  
echo    3️⃣ Popular banco com dados corretos
echo.

set /p continuar="Iniciar processo? (S/N): "
if /i not "%continuar%"=="S" if /i not "%continuar%"=="s" goto :end

echo.
echo ========================================================================
echo                    1️⃣ ANÁLISE DO ARQUIVO CSV REAL
echo ========================================================================
echo.

echo 🔍 Executando análise detalhada do arquivo...
echo.

python analisar_arquivo_real.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ ERRO na análise do arquivo!
    echo 💡 Possíveis problemas:
    echo    - Arquivo CSV corrompido
    echo    - Encoding não suportado
    echo    - Estrutura inesperada
    echo.
    pause
    goto :end
)

echo.
echo ✅ ANÁLISE CONCLUÍDA!
echo 📄 Arquivo mapeamento_colunas.txt criado
echo.

echo Pressione qualquer tecla para continuar para a etapa 2...
pause >nul

echo.
echo ========================================================================
echo                    2️⃣ VERIFICAÇÃO DO MAPEAMENTO
echo ========================================================================
echo.

if exist "mapeamento_colunas.txt" (
    echo ✅ Arquivo de mapeamento encontrado!
    echo.
    echo 📋 MAPEAMENTO IDENTIFICADO:
    echo.
    findstr /C:":" mapeamento_colunas.txt | findstr /V "#" | findstr /V "MAPEAMENTO" | findstr /V "TODAS_AS_COLUNAS"
    echo.
) else (
    echo ❌ Arquivo de mapeamento não foi criado!
    echo 💡 Volte à etapa 1 e verifique se houve erros
    pause
    goto :end
)

echo 🔍 VERIFICAÇÃO DO MAPEAMENTO:
echo.
echo ⚠️  IMPORTANTE: Verifique se o mapeamento acima está correto
echo    • numero_cte deve apontar para a coluna com números CTE
echo    • destinatario deve apontar para nomes de clientes  
echo    • valor deve apontar para valores monetários
echo.

set /p mapeamento_ok="O mapeamento está correto? (S/N): "

if /i not "%mapeamento_ok%"=="S" if /i not "%mapeamento_ok%"=="s" (
    echo.
    echo 📝 Para corrigir o mapeamento:
    echo    1. Abra o arquivo: mapeamento_colunas.txt
    echo    2. Edite as linhas do MAPEAMENTO = { ... }
    echo    3. Salve o arquivo
    echo    4. Execute novamente este script
    echo.
    
    set /p abrir_arquivo="Abrir arquivo para edição? (S/N): "
    if /i "%abrir_arquivo%"=="S" if /i "%abrir_arquivo%"=="s" (
        notepad mapeamento_colunas.txt
    )
    
    echo Após corrigir, execute novamente este script
    pause
    goto :end
)

echo.
echo ✅ Mapeamento confirmado! Continuando...
echo.

echo Pressione qualquer tecla para continuar para a etapa 3...
pause >nul

echo.
echo ========================================================================
echo                    3️⃣ POPULANDO BANCO POSTGRESQL
echo ========================================================================
echo.

echo 💾 Executando inserção no banco com mapeamento correto...
echo.

python popular_banco_com_mapeamento.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ SUCESSO TOTAL!
    echo 🎉 Banco populado com dados do CSV
    echo.
    echo 📊 PRÓXIMOS PASSOS:
    echo    1. Execute: streamlit run dashboard_baker_web_corrigido.py
    echo    2. Acesse: http://localhost:8501
    echo    3. Use as duas abas do dashboard
    echo.
    
    set /p iniciar_dashboard="Iniciar dashboard agora? (S/N): "
    if /i "%iniciar_dashboard%"=="S" if /i "%iniciar_dashboard%"=="s" (
        echo.
        echo 🚀 Iniciando Dashboard Baker...
        echo 🌐 Acesse: http://localhost:8501
        echo.
        streamlit run dashboard_baker_web_corrigido.py
    )
    
) else (
    echo.
    echo ❌ ERRO na inserção no banco!
    echo.
    echo 🔧 POSSÍVEIS SOLUÇÕES:
    echo    1. Verifique se PostgreSQL está rodando
    echo    2. Confirme credenciais no arquivo .env
    echo    3. Execute: python status_dashboard.py
    echo    4. Verifique se o mapeamento está correto
    echo.
    
    echo 💡 DIAGNÓSTICOS DISPONÍVEIS:
    echo    • python teste_sistema_completo.py
    echo    • python status_dashboard.py
    echo    • status_dashboard.bat
    echo.
)

echo.
echo ========================================================================
echo                         📊 RESUMO FINAL
echo ========================================================================
echo.

echo 🎯 PROCESSO EXECUTADO:
echo    ✅ 1️⃣ Análise do CSV real
echo    ✅ 2️⃣ Mapeamento de colunas
if %errorlevel% equ 0 (
    echo    ✅ 3️⃣ População do banco
    echo.
    echo 🎉 TUDO FUNCIONANDO!
    echo 📊 Dashboard pronto para uso
) else (
    echo    ❌ 3️⃣ População do banco (com erros)
    echo.
    echo ⚠️ PARCIALMENTE FUNCIONANDO
    echo 🔧 Verifique erros da etapa 3
)

echo.
echo 📁 ARQUIVOS CRIADOS:
echo    • mapeamento_colunas.txt (mapeamento das colunas)
if %errorlevel% equ 0 (
    echo    • Dados inseridos no PostgreSQL
)

echo.
echo 🚀 COMANDOS ÚTEIS:
echo    • Iniciar dashboard: streamlit run dashboard_baker_web_corrigido.py
echo    • Verificar status: status_dashboard.bat
echo    • Testes completos: python teste_sistema_completo.py
echo    • Repetir processo: solucao_completa_csv.bat
echo.

:end
echo ========================================================================
echo 👋 Processo concluído!
echo.
echo 💡 Para executar novamente: solucao_completa_csv.bat
echo 📧 Para suporte: compartilhe o arquivo mapeamento_colunas.txt
echo.
pause