@echo off
echo ========================================
echo  DASHBOARD FINANCEIRO BAKER - EXECUTAR
echo ========================================
echo.
echo 🚀 Iniciando dashboard na porta 8515...
echo.
echo 💡 O dashboard será aberto automaticamente no navegador
echo 🌐 URL: http://localhost:8515
echo.
echo 🔄 Para parar o dashboard, pressione Ctrl+C
echo.
pause
echo.
echo ⏳ Carregando dashboard...
streamlit run dashboard_baker_web_corrigido.py --server.port 8515
echo.
echo 🛑 Dashboard finalizado
pause
