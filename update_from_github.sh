#!/bin/bash
# Atualizar Codespace com a versão mais recente do GitHub
# Execute: bash update_from_github.sh

echo "🔄 ATUALIZANDO CODESPACE COM GITHUB"
echo "==================================="
echo "🕐 $(date '+%d/%m/%Y %H:%M:%S')"
echo ""

echo "📍 Codespace: $CODESPACE_NAME"
echo "🎯 Objetivo: Sincronizar com a versão mais recente do GitHub"
echo ""

# 1. Verificar repositório atual
echo "📊 [1/7] Verificando repositório atual..."
REPO_URL=$(git config --get remote.origin.url)
REPO_NAME=$(echo $REPO_URL | sed 's/.*github.com[:/]//; s/.git$//')
echo "   📂 Repositório: $REPO_NAME"
echo "   🔗 URL: $REPO_URL"
echo ""

# 2. Ver commits locais vs remotos
echo "📈 [2/7] Comparando versões..."
echo "   🏠 Último commit local:"
git log --oneline -1 2>/dev/null || echo "      ❌ Erro ao ler commits locais"

echo ""
echo "   🌐 Buscando commits remotos..."
git fetch origin >/dev/null 2>&1

echo "   ☁️ Último commit no GitHub:"
git log origin/main --oneline -1 2>/dev/null || echo "      ❌ Erro ao ler commits remotos"

echo ""

# 3. Verificar se há mudanças locais não commitadas
echo "🔍 [3/7] Verificando mudanças locais..."
if git status --porcelain | grep -q .; then
    echo "   ⚠️ ATENÇÃO: Você tem mudanças locais não salvas:"
    git status --porcelain | head -5
    echo ""
    
    read -p "   ❓ Deseja salvar essas mudanças antes de atualizar? (s/N): " save_changes
    if [[ $save_changes =~ ^[Ss]$ ]]; then
        echo "   💾 Salvando mudanças locais..."
        git add .
        git commit -m "Backup automático antes de atualizar do GitHub - $(date '+%Y%m%d_%H%M%S')"
        echo "   ✅ Mudanças salvas em commit local"
    else
        echo "   ⚠️ Mudanças locais serão descartadas!"
        read -p "   ❓ Confirma? Isso vai PERDER suas mudanças locais (s/N): " confirm_discard
        if [[ $confirm_discard =~ ^[Ss]$ ]]; then
            echo "   🗑️ Descartando mudanças locais..."
            git reset --hard HEAD
            git clean -fd
            echo "   ✅ Mudanças locais descartadas"
        else
            echo "   ❌ Operação cancelada. Resolva as mudanças locais primeiro."
            exit 1
        fi
    fi
else
    echo "   ✅ Nenhuma mudança local pendente"
fi

echo ""

# 4. Fazer backup do estado atual
echo "💾 [4/7] Fazendo backup do estado atual..."
BACKUP_DIR="backup_$(date '+%Y%m%d_%H%M%S')"
mkdir -p $BACKUP_DIR

# Backup de arquivos importantes
IMPORTANT_FILES=(
    "dashboard_baker_web_corrigido.py"
    ".streamlit/secrets.toml"
    "requirements.txt"
    "*.py"
)

for pattern in "${IMPORTANT_FILES[@]}"; do
    if ls $pattern 2>/dev/null; then
        cp $pattern $BACKUP_DIR/ 2>/dev/null || true
    fi
done

echo "   ✅ Backup criado em: $BACKUP_DIR"
echo ""

# 5. Atualizar do GitHub
echo "⬇️ [5/7] Baixando versão mais recente do GitHub..."

# Método 1: Pull normal
if git pull origin main; then
    echo "   ✅ Atualização bem-sucedida via pull"
elif git pull origin master; then
    echo "   ✅ Atualização bem-sucedida via pull (branch master)"
else
    echo "   ⚠️ Pull falhou, tentando reset forçado..."
    
    # Método 2: Reset forçado
    git fetch origin
    if git reset --hard origin/main; then
        echo "   ✅ Atualização forçada bem-sucedida (main)"
    elif git reset --hard origin/master; then
        echo "   ✅ Atualização forçada bem-sucedida (master)"
    else
        echo "   ❌ Falha na atualização"
        echo "   💡 Tente manualmente: git fetch && git reset --hard origin/main"
        exit 1
    fi
fi

echo ""

# 6. Verificar arquivos atualizados
echo "📋 [6/7] Verificando arquivos atualizados..."
echo ""

# Lista de arquivos importantes para verificar
IMPORTANT_FILES=(
    "dashboard_baker_web_corrigido.py"
    "requirements.txt"
    ".streamlit/secrets.toml"
    "README.md"
)

echo "   📄 Status dos arquivos principais:"
for file in "${IMPORTANT_FILES[@]}"; do
    if [ -f "$file" ]; then
        SIZE=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "?")
        MOD_TIME=$(stat -f%Sm "$file" 2>/dev/null || stat -c%y "$file" 2>/dev/null || echo "?")
        echo "      ✅ $file (${SIZE} bytes, mod: ${MOD_TIME})"
    else
        echo "      ❌ $file (não encontrado)"
    fi
done

echo ""

# 7. Verificar se há novos arquivos importantes
echo "🔍 Novos arquivos Python:"
find . -name "*.py" -newer $BACKUP_DIR 2>/dev/null | head -5 | while read file; do
    echo "      🆕 $file"
done

echo ""

# 8. Status final
echo "✅ [7/7] Atualização concluída!"
echo ""

echo "📊 RESUMO DA ATUALIZAÇÃO:"
echo "   📂 Repositório: $REPO_NAME"
echo "   💾 Backup: $BACKUP_DIR"
echo "   🔄 Status: Codespace atualizado com GitHub"
echo ""

echo "🎯 PRÓXIMOS PASSOS:"
echo ""
echo "   1️⃣ Verificar se tem o arquivo principal:"
echo "      ls -la dashboard_baker_web_corrigido.py"
echo ""
echo "   2️⃣ Instalar dependências:"
echo "      pip install -r requirements.txt"
echo ""
echo "   3️⃣ Configurar secrets se necessário:"
echo "      cat .streamlit/secrets.toml"
echo ""
echo "   4️⃣ Executar o dashboard:"
echo "      streamlit run dashboard_baker_web_corrigido.py"
echo ""

echo "💡 COMANDOS RÁPIDOS:"
echo ""
echo "# Ver diferenças com backup"
echo "diff dashboard_baker_web_corrigido.py $BACKUP_DIR/dashboard_baker_web_corrigido.py"
echo ""
echo "# Verificar última modificação"
echo "git log --oneline -5"
echo ""
echo "# Status atual"
echo "git status"
echo ""

echo "🎉 CODESPACE SINCRONIZADO COM GITHUB!"
echo "📍 Agora você tem a versão mais recente do seu repositório"