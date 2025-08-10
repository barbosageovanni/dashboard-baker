# Dashboard Baker - Deploy Configuration

## Status da Conexão
✅ **Supabase PostgreSQL**: Conectado e funcionando
✅ **Tabela dashboard_baker**: 391 registros
✅ **Código**: Sem erros de sintaxe

## Configuração para Deploy

### 🚀 Streamlit Cloud (RECOMENDADO - GRATUITO)

**Passo 1: Preparar repositório Git**
```bash
git add .
git commit -m "Deploy: Dashboard Baker v3.1 - Sistema completo"
git push origin main
```

**Passo 2: Streamlit Cloud**
1. Acesse: https://share.streamlit.io
2. "New app" → "From existing repo"
3. Conecte seu GitHub
4. Selecione repositório
5. Main file: `dashboard_baker_web_corrigido.py`

**Passo 3: Configurar Secrets**
No painel do Streamlit Cloud, adicione em "Advanced settings" → "Secrets":

```toml
[database]
SUPABASE_HOST = "db.lijtncazuwnbydeqtoyz.supabase.co"
SUPABASE_DB = "postgres"
SUPABASE_USER = "postgres"
SUPABASE_PASSWORD = "Mariaana953@7334"
SUPABASE_PORT = "5432"
DATABASE_ENVIRONMENT = "supabase"

[server]
STREAMLIT_SERVER_PORT = "8501"
STREAMLIT_SERVER_ADDRESS = "0.0.0.0"
```

### 🌐 Outras Opções

#### Railway
- Conecta GitHub automaticamente
- PostgreSQL integrado
- Mais recursos
- Pago após trial

#### Render
- Deploy gratuito limitado
- PostgreSQL gratuito por 90 dias
- Boa performance

#### Heroku
- Não tem plano gratuito mais
- PostgreSQL pago

## Arquivos de Deploy Prontos
✅ `requirements.txt` - Dependências
✅ `Procfile` - Comando de start
✅ `.env` - Configuração local
✅ `dashboard_baker_web_corrigido.py` - Aplicação principal

## URLs após Deploy
- Streamlit Cloud: `https://nome-app-usuario.streamlit.app`
- Railway: `https://nome-app.railway.app`
- Render: `https://nome-app.onrender.com`
