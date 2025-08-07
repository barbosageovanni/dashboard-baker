
🚀 INSTRUÇÕES DE DEPLOY - DASHBOARD BAKER
===============================================

📍 RAILWAY (RECOMENDADO)
1. Acesse: https://railway.app
2. Connect GitHub → Selecione este repositório
3. Adicione PostgreSQL: Add Service → Database → PostgreSQL
4. Configure variáveis de ambiente no painel Railway:
   - PGHOST: [valor do Railway]
   - PGDATABASE: [valor do Railway] 
   - PGUSER: [valor do Railway]
   - PGPASSWORD: [valor do Railway]
   - PGPORT: 5432
5. Deploy automático será feito

📍 RENDER
1. Acesse: https://render.com
2. Crie PostgreSQL Database primeiro
3. New → Web Service → Connect GitHub
4. Configure variáveis de ambiente no painel Render
5. Build Command: pip install -r requirements.txt
6. Start Command: streamlit run dashboard_baker_web_corrigido.py --server.port=$PORT --server.address=0.0.0.0

📍 HEROKU
1. Instale Heroku CLI
2. heroku create nome-do-app
3. heroku addons:create heroku-postgresql:mini
4. heroku config:set [variáveis de ambiente]
5. git push heroku main

📍 STREAMLIT CLOUD
1. Acesse: https://share.streamlit.io
2. Connect GitHub → Selecione repositório
3. Configure secrets no painel:
   PGHOST = "seu-host"
   PGDATABASE = "seu-database"
   PGUSER = "seu-user"
   PGPASSWORD = "sua-senha"
   PGPORT = "5432"

⚡ COMANDOS ÚTEIS:
- Inicializar banco: python inicializar_banco_deploy.py
- Testar local: streamlit run dashboard_baker_web_corrigido.py
- Ver logs: [comando específico da plataforma]

===============================================
