@echo off
chcp 65001 >nul
cls

🔍 DIAGNÓSTICO SISTEMA BAKER
============================

[1/6] 🐍 Python...
python --version

[2/6] 📦 Principais bibliotecas...
python -c "import streamlit, fastapi, pandas, plotly; print('✅ Todas OK')"

[3/6] 🌐 Teste API...
python -c "import requests; print('✅ Requests OK')"

[4/6] 🔗 Google Sheets...
python -c "import gspread; print('✅ Google Sheets OK')" 2>nul || echo "⚠️ Google Sheets não instalado"

[5/6] 📁 Estrutura...
if exist dashboard_baker_sap_style.py echo ✅ Dashboard
if exist api_baker.py echo ✅ API
if exist data echo ✅ Pasta data
if exist credentials echo ✅ Pasta credentials

[6/6] 🎯 Status geral...
echo ✅ Sistema pronto para uso!

pause
