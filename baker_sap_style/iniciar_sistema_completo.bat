@echo off
chcp 65001 >nul
cls

🚀 SISTEMA BAKER COMPLETO
=========================

⚡ Iniciando todos os serviços...

📊 Dashboard: http://localhost:8501
🌐 API: http://localhost:8000
📋 Docs: http://localhost:8000/docs

🔄 Iniciando API em segundo plano...
start /min "API Baker" cmd /c "python api_baker.py"

⏳ Aguardando API inicializar...
timeout /t 5 /nobreak >nul

🔄 Iniciando Dashboard...
streamlit run dashboard_baker_sap_style.py

pause
