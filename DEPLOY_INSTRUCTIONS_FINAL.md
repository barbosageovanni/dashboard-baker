🚀 DASHBOARD BAKER - DEPLOY INSTRUCTIONS
=====================================

## ✅ STATUS ATUAL
- ✅ **Sistema Funcionando**: Dashboard rodando em http://localhost:8503
- ✅ **Banco Conectado**: Supabase PostgreSQL com 391 registros
- ✅ **Código Atualizado**: Última versão commitada no Git
- ✅ **Sem Erros**: Todas as correções aplicadas

## 🌐 OPÇÕES DE DEPLOY

### 🎯 STREAMLIT CLOUD (RECOMENDADO - GRATUITO)

**Passo 1: Acesse https://share.streamlit.io**
1. Faça login com GitHub
2. Clique em "New app"
3. Selecione "From existing repo"

**Passo 2: Configurar App**
- Repository: `Transpontual/dashboard_financeiro` (ou seu repo)
- Branch: `main`  
- Main file path: `dashboard_baker_web_corrigido.py`

**Passo 3: Advanced Settings > Secrets**
Cole este conteúdo:
```toml
SUPABASE_HOST = "db.lijtncazuwnbydeqtoyz.supabase.co"
SUPABASE_DB = "postgres"
SUPABASE_USER = "postgres"
SUPABASE_PASSWORD = "Mariaana953@7334"
SUPABASE_PORT = "5432"
DATABASE_ENVIRONMENT = "supabase"
```

**Passo 4: Deploy**
- Clique "Deploy!"
- Aguarde 2-3 minutos
- URL será: `https://dashboard-baker-username.streamlit.app`

### 🚂 RAILWAY (ALTERNATIVA)

**Passo 1: Acesse https://railway.app**
1. Login com GitHub
2. "New Project" > "Deploy from GitHub repo"
3. Selecione seu repositório

**Passo 2: Configurar Variáveis**
No painel Railway, adicione:
```
SUPABASE_HOST=db.lijtncazuwnbydeqtoyz.supabase.co
SUPABASE_DB=postgres
SUPABASE_USER=postgres
SUPABASE_PASSWORD=Mariaana953@7334
SUPABASE_PORT=5432
DATABASE_ENVIRONMENT=supabase
```

**Passo 3: Deploy Automático**
- Railway detecta automaticamente Procfile
- Deploy acontece automaticamente
- URL será: `https://nome-projeto.railway.app`

### 🌈 RENDER (ALTERNATIVA)

**Passo 1: Acesse https://render.com**
1. "New" > "Web Service"
2. Connect GitHub repository

**Passo 2: Configurar**
- Name: dashboard-baker
- Environment: Python 3
- Build Command: `pip install -r requirements.txt`
- Start Command: `streamlit run dashboard_baker_web_corrigido.py --server.port=$PORT --server.address=0.0.0.0`

**Passo 3: Environment Variables**
Adicione as mesmas variáveis do Railway

## 📋 CHECKLIST PRÉ-DEPLOY

✅ Código atualizado e sem erros  
✅ requirements.txt presente  
✅ Procfile configurado  
✅ Conexão Supabase testada  
✅ 391 registros na base de dados  
✅ Dashboard funcionando localmente  
✅ Git repository atualizado  

## 🎯 PÓS-DEPLOY

Após o deploy, o sistema terá:
- ✅ **URL pública** funcionando 24/7
- ✅ **Status "Sistema Operacional"** em vez de "Offline"
- ✅ **Todas as funcionalidades** disponíveis online
- ✅ **Cards e relatórios** atualizados em tempo real
- ✅ **Downloads** funcionando
- ✅ **Sistema de alertas** ativo

## 🆘 SUPORTE

Se tiver problemas:
1. Verifique os logs no painel da plataforma
2. Confirme que as variáveis de ambiente estão corretas
3. Teste conexão Supabase
4. Verifique se requirements.txt está completo

**Tempo estimado de deploy: 5-10 minutos**
**Custo: GRATUITO (Streamlit Cloud)**
