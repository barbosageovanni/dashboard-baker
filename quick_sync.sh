#!/bin/bash
# Sincronização RÁPIDA - GitHub → Codespace
# Execute: bash quick_sync.sh

echo "⚡ SINCRONIZAÇÃO RÁPIDA - GITHUB → CODESPACE"
echo "============================================"
echo ""

# Verificar se está no codespace
if [ -z "$CODESPACE_NAME" ]; then
    echo "❌ Este script é para GitHub Codespaces"
    exit 1
fi

echo "🎯 Atualizando com a versão mais recente do GitHub..."
echo ""

# 1. Fazer backup rápido (se houver mudanças)
if git status --porcelain | grep -q .; then
    echo "💾 Fazendo backup das mudanças locais..."
    git stash push -m "backup-antes-sync-$(date +%s)"
    echo "   ✅ Backup salvo no stash"
fi

# 2. Atualizar do GitHub
echo "⬇️ Baixando última versão..."
git fetch origin
git reset --hard origin/main 2>/dev/null || git reset --hard origin/master

echo "   ✅ Código atualizado!"
echo ""

# 3. Verificar arquivos principais
echo "📋 Verificando arquivos principais..."
if [ -f "dashboard_baker_web_corrigido.py" ]; then
    SIZE=$(stat -c%s "dashboard_baker_web_corrigido.py" 2>/dev/null || echo "?")
    echo "   ✅ dashboard_baker_web_corrigido.py ($SIZE bytes)"
else
    echo "   ❌ dashboard_baker_web_corrigido.py não encontrado"
fi

if [ -f "requirements.txt" ]; then
    echo "   ✅ requirements.txt"
else
    echo "   ❌ requirements.txt não encontrado"
fi

echo ""

# 4. Instalar dependências automaticamente
echo "📦 Instalando dependências..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    echo "   ✅ Dependências instaladas"
else
    echo "   🔧 Instalando dependências básicas..."
    pip install streamlit pandas plotly psycopg2-binary --quiet
    echo "   ✅ Dependências básicas instaladas"
fi

echo ""

# 5. Verificar configuração
echo "⚙️ Verificando configuração..."
if [ -f ".streamlit/secrets.toml" ]; then
    echo "   ✅ Arquivo secrets.toml encontrado"
else
    echo "   ⚠️ Criando secrets.toml básico..."
    mkdir -p .streamlit
    cat > .streamlit/secrets.toml << 'EOF'
[supabase]
host = "db.lijtncazuwnbydeqtoyz.supabase.co"
password = "Mariaana953@7334"
user = "postgres"
database = "postgres"
port = "5432"
EOF
    echo "   ✅ secrets.toml criado"
fi

echo ""

# 6. Status final e comando para executar
echo "🎉 SINCRONIZAÇÃO CONCLUÍDA!"
echo ""
echo "📊 STATUS:"
echo "   📂 Codespace atualizado com GitHub"
echo "   📦 Dependências instaladas"
echo "   ⚙️ Configuração verificada"
echo ""

echo "🚀 EXECUTAR AGORA:"
echo ""
echo "   streamlit run dashboard_baker_web_corrigido.py"
echo ""

echo "🌐 Depois acesse:"
echo "   http://localhost:8501"
echo ""

# 7. Executar automaticamente se solicitado
read -p "❓ Deseja executar o dashboard agora? (s/N): " auto_run
if [[ $auto_run =~ ^[Ss]$ ]]; then
    echo ""
    echo "🚀 Iniciando dashboard..."
    sleep 2
    streamlit run dashboard_baker_web_corrigido.py
fi