@echo off
echo CORRIGINDO ERRO HTML - Dashboard Baker v3.0
echo ============================================

echo Executando fix_html_error.py...
python fix_html_error.py

echo.
echo Fazendo git push...
git add .
git commit -m "Fix HTML error - Clean version v3"
git push origin main

echo.
echo ============================================
echo PRONTO! Aguarde 2-3 minutos para atualizar
echo ============================================
echo.
echo URL: https://dashboard-transpontual.streamlit.app/
echo.
pause