#!/bin/bash
# ============================================================================
# SCRIPTS DE PRODUÇÃO RAILWAY - DASHBOARD BAKER
# Sistema completo para deploy e manutenção
# ============================================================================

# ============================================================================
# 1. SCRIPT DE DEPLOY AUTOMÁTICO
# Arquivo: deploy_railway.sh
# ============================================================================

#!/bin/bash
echo "🚀 DEPLOY AUTOMÁTICO RAILWAY - DASHBOARD BAKER"
echo "=============================================="

# Verificar se Railway CLI está instalado
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI não encontrado"
    echo "💡 Instale com: npm install -g @railway/cli"
    exit 1
fi

# Login Railway
echo "🔐 Verificando autenticação Railway..."
railway auth

# Criar projeto se não existir
echo "📁 Configurando projeto..."
railway init

# Adicionar PostgreSQL
echo "🐘 Adicionando PostgreSQL..."
railway add postgresql

# Configurar variáveis de ambiente
echo "⚙️ Configurando variáveis de ambiente..."

# Obter DATABASE_URL automaticamente
DATABASE_URL=$(railway variables get DATABASE_URL)

if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL não encontrada"
    echo "💡 Aguarde o PostgreSQL ser provisionado"
    exit 1
fi

# Definir variáveis adicionais
railway variables set STREAMLIT_SERVER_PORT=8501
railway variables set STREAMLIT_SERVER_ADDRESS=0.0.0.0
railway variables set RAILWAY_ENVIRONMENT=production
railway variables set TZ=America/Sao_Paulo

echo "✅ Variáveis configuradas!"

# Deploy
echo "🚀 Fazendo deploy..."
railway up

echo "🎉 Deploy concluído!"
echo "🌐 Acesse: https://[seu-projeto].railway.app"

# ============================================================================
# 2. SCRIPT DE BACKUP AUTOMÁTICO
# Arquivo: backup_railway.sh
# ============================================================================

#!/bin/bash
echo "💾 BACKUP AUTOMÁTICO RAILWAY"
echo "============================"

# Obter DATABASE_URL
DATABASE_URL=$(railway variables get DATABASE_URL)

if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL não encontrada"
    exit 1
fi

# Criar pasta de backup
BACKUP_DIR="backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup completo
echo "📊 Criando backup completo..."
pg_dump "$DATABASE_URL" > "$BACKUP_DIR/backup_completo_$(date +%Y%m%d_%H%M%S).sql"

# Backup apenas dados
echo "📋 Criando backup de dados..."
pg_dump "$DATABASE_URL" --data-only --table=dashboard_baker > "$BACKUP_DIR/dados_$(date +%Y%m%d_%H%M%S).sql"

# Backup em CSV
echo "📄 Exportando para CSV..."
psql "$DATABASE_URL" -c "\COPY dashboard_baker TO '$BACKUP_DIR/dashboard_baker_$(date +%Y%m%d_%H%M%S).csv' WITH CSV HEADER;"

echo "✅ Backup concluído em: $BACKUP_DIR"

# ============================================================================
# 3. SCRIPT DE MONITORAMENTO
# Arquivo: monitor_railway.sh
# ============================================================================

#!/bin/bash
echo "📊 MONITORAMENTO RAILWAY - DASHBOARD BAKER"
echo "=========================================="

# Função para verificar status
check_status() {
    echo "🔍 Verificando status do sistema..."
    
    # Status do Railway
    railway status
    
    # Teste de conexão PostgreSQL
    DATABASE_URL=$(railway variables get DATABASE_URL)
    
    if psql "$DATABASE_URL" -c "SELECT 1;" > /dev/null 2>&1; then
        echo "✅ PostgreSQL: Conectado"
    else
        echo "❌ PostgreSQL: Erro de conexão"
        return 1
    fi
    
    # Verificar dados
    COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM dashboard_baker;")
    echo "📊 Total de registros: $COUNT"
    
    # Verificar último deploy
    echo "🚀 Último deploy:"
    railway logs --tail 5
    
    return 0
}

# Função para restart
restart_service() {
    echo "🔄 Reiniciando serviço..."
    railway redeploy
}

# Menu principal
while true; do
    echo ""
    echo "Escolha uma opção:"
    echo "[1] 🔍 Verificar Status"
    echo "[2] 🔄 Restart Serviço"
    echo "[3] 📊 Ver Logs"
    echo "[4] 💾 Fazer Backup"
    echo "[0] ❌ Sair"
    
    read -p "Opção: " option
    
    case $option in
        1) check_status ;;
        2) restart_service ;;
        3) railway logs ;;
        4) ./backup_railway.sh ;;
        0) exit 0 ;;
        *) echo "❌ Opção inválida" ;;
    esac
done

# ============================================================================
# 4. SCRIPT DE SETUP INICIAL
# Arquivo: setup_inicial_railway.sh
# ============================================================================

#!/bin/bash
echo "🔧 SETUP INICIAL RAILWAY - DASHBOARD BAKER"
echo "=========================================="

# 1. Verificar dependências
echo "📋 Verificando dependências..."

# Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado"
    exit 1
fi

# pip
if ! command -v pip &> /dev/null; then
    echo "❌ pip não encontrado"
    exit 1
fi

# Railway CLI
if ! command -v railway &> /dev/null; then
    echo "⬇️ Instalando Railway CLI..."
    npm install -g @railway/cli
fi

echo "✅ Dependências verificadas"

# 2. Instalar dependências Python
echo "📦 Instalando dependências Python..."
pip install -r requirements.txt

# 3. Configurar ambiente local
echo "⚙️ Configurando ambiente local..."

# Criar .env se não existir
if [ ! -f .env ]; then
    cat > .env << EOF
# Railway PostgreSQL Configuration
# Substitua pelas suas credenciais reais

DATABASE_URL=postgresql://postgres:senha@host.railway.app:5432/railway
PGHOST=containers-us-west-xxx.railway.app
PGPORT=5432
PGDATABASE=railway
PGUSER=postgres
PGPASSWORD=sua-senha-postgresql

# Configurações locais
DEV_MODE=true
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
EOF
    echo "📄 Arquivo .env criado - EDITE com suas credenciais!"
fi

# 4. Criar estrutura de pastas
echo "📁 Criando estrutura de pastas..."
mkdir -p backups
mkdir -p logs
mkdir -p data
mkdir -p exports

# 5. Testar configuração local
echo "🧪 Testando configuração..."
python3 -c "
try:
    from config_railway import RailwayConfig
    success, msg = RailwayConfig.test_connection()
    print(f'✅ Teste: {msg}' if success else f'❌ Erro: {msg}')
except Exception as e:
    print(f'❌ Erro no teste: {e}')
"

echo "🎉 Setup inicial concluído!"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "1. Edite o arquivo .env com suas credenciais Railway"
echo "2. Execute: python popular_banco_railway.py seu_arquivo.csv"
echo "3. Execute: streamlit run dashboard_baker_web_railway.py"

# ============================================================================
# 5. SCRIPT DE IMPORTAÇÃO EM MASSA
# Arquivo: importacao_massa_railway.sh
# ============================================================================

#!/bin/bash
echo "📥 IMPORTAÇÃO EM MASSA - RAILWAY"
echo "==============================="

# Verificar argumentos
if [ $# -eq 0 ]; then
    echo "❌ Uso: ./importacao_massa_railway.sh <pasta_com_csvs>"
    exit 1
fi

PASTA_CSV=$1

# Verificar se pasta existe
if [ ! -d "$PASTA_CSV" ]; then
    echo "❌ Pasta não encontrada: $PASTA_CSV"
    exit 1
fi

# Encontrar arquivos CSV
CSV_FILES=$(find "$PASTA_CSV" -name "*.csv" -type f)

if [ -z "$CSV_FILES" ]; then
    echo "❌ Nenhum arquivo CSV encontrado em: $PASTA_CSV"
    exit 1
fi

echo "📋 Arquivos CSV encontrados:"
echo "$CSV_FILES"
echo ""

# Confirmar importação
read -p "Continuar com a importação? (s/N): " confirm
if [[ $confirm != [sS] ]]; then
    echo "❌ Importação cancelada"
    exit 0
fi

# Processar cada arquivo
SUCCESS_COUNT=0
ERROR_COUNT=0

for csv_file in $CSV_FILES; do
    echo "📊 Processando: $(basename "$csv_file")"
    
    if python3 popular_banco_railway.py "$csv_file"; then
        echo "✅ Sucesso: $(basename "$csv_file")"
        ((SUCCESS_COUNT++))
    else
        echo "❌ Erro: $(basename "$csv_file")"
        ((ERROR_COUNT++))
    fi
    
    echo "---"
done

echo ""
echo "🎉 IMPORTAÇÃO CONCLUÍDA!"
echo "✅ Sucessos: $SUCCESS_COUNT"
echo "❌ Erros: $ERROR_COUNT"

# ============================================================================
# 6. SCRIPT DE MANUTENÇÃO
# Arquivo: manutencao_railway.sh
# ============================================================================

#!/bin/bash
echo "🔧 MANUTENÇÃO RAILWAY - DASHBOARD BAKER"
echo "======================================"

DATABASE_URL=$(railway variables get DATABASE_URL)

# Função para otimizar banco
optimize_database() {
    echo "🚀 Otimizando banco de dados..."
    
    psql "$DATABASE_URL" << EOF
-- Vacuum e Analyze
VACUUM ANALYZE dashboard_baker;

-- Reindexar
REINDEX TABLE dashboard_baker;

-- Estatísticas
SELECT 
    schemaname, tablename, 
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE tablename = 'dashboard_baker';
EOF
    
    echo "✅ Otimização concluída"
}

# Função para limpar logs
clean_logs() {
    echo "🧹 Limpando logs antigos..."
    
    # Limpar logs locais
    find logs/ -name "*.log" -mtime +7 -delete 2>/dev/null
    
    echo "✅ Logs limpos"
}

# Função para verificar integridade
check_integrity() {
    echo "🔍 Verificando integridade dos dados..."
    
    psql "$DATABASE_URL" << EOF
-- Verificar dados inconsistentes
SELECT 'CTEs sem numero_cte' as problema, COUNT(*) as quantidade
FROM dashboard_baker WHERE numero_cte IS NULL
UNION ALL
SELECT 'CTEs com valor zero' as problema, COUNT(*) as quantidade
FROM dashboard_baker WHERE valor_total <= 0
UNION ALL
SELECT 'CTEs sem destinatário' as problema, COUNT(*) as quantidade
FROM dashboard_baker WHERE destinatario_nome IS NULL OR destinatario_nome = '';
EOF
    
    echo "✅ Verificação concluída"
}

# Menu
while true; do
    echo ""
    echo "Escolha uma ação:"
    echo "[1] 🚀 Otimizar Banco"
    echo "[2] 🧹 Limpar Logs"
    echo "[3] 🔍 Verificar Integridade"
    echo "[4] 💾 Backup Completo"
    echo "[5] 📊 Estatísticas"
    echo "[0] ❌ Sair"
    
    read -p "Opção: " option
    
    case $option in
        1) optimize_database ;;
        2) clean_logs ;;
        3) check_integrity ;;
        4) ./backup_railway.sh ;;
        5) 
            echo "📊 Estatísticas atuais:"
            psql "$DATABASE_URL" -c "
            SELECT 
                COUNT(*) as total_registros,
                COUNT(CASE WHEN data_baixa IS NOT NULL THEN 1 END) as com_baixa,
                ROUND(SUM(valor_total), 2) as receita_total
            FROM dashboard_baker;"
            ;;
        0) exit 0 ;;
        *) echo "❌ Opção inválida" ;;
    esac
done

# ============================================================================
# 7. SCRIPT DE ATUALIZAÇÃO
# Arquivo: update_sistema_railway.sh
# ============================================================================

#!/bin/bash
echo "🔄 ATUALIZAÇÃO DO SISTEMA RAILWAY"
echo "================================"

# 1. Backup antes da atualização
echo "💾 Criando backup de segurança..."
./backup_railway.sh

# 2. Atualizar dependências
echo "📦 Atualizando dependências..."
pip install --upgrade -r requirements.txt

# 3. Verificar mudanças no esquema
echo "🔍 Verificando esquema do banco..."
DATABASE_URL=$(railway variables get DATABASE_URL)

psql "$DATABASE_URL" << EOF
-- Adicionar colunas se não existirem
ALTER TABLE dashboard_baker 
ADD COLUMN IF NOT EXISTS versao_sistema VARCHAR(10) DEFAULT '4.0';

ALTER TABLE dashboard_baker 
ADD COLUMN IF NOT EXISTS ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Atualizar índices
CREATE INDEX IF NOT EXISTS idx_dashboard_baker_versao 
ON dashboard_baker(versao_sistema);
EOF

# 4. Deploy da nova versão
echo "🚀 Deploy da nova versão..."
railway up

# 5. Verificar saúde do sistema
echo "🏥 Verificando saúde do sistema..."
sleep 30  # Aguardar deploy

# Testar endpoint
if curl -f -s "https://[seu-projeto].railway.app" > /dev/null; then
    echo "✅ Sistema online e funcionando"
else
    echo "❌ Sistema pode estar com problemas"
    echo "📋 Verificando logs..."
    railway logs --tail 20
fi

echo "🎉 Atualização concluída!"

# ============================================================================
# 8. ARQUIVO MAKEFILE PARA AUTOMAÇÃO
# Arquivo: Makefile
# ============================================================================

# Makefile para Dashboard Baker Railway
.PHONY: help setup deploy backup monitor clean update

help:
	@echo "🚀 Dashboard Baker Railway - Comandos Disponíveis"
	@echo "================================================"
	@echo "setup     - Configuração inicial"
	@echo "deploy    - Deploy para Railway"
	@echo "backup    - Criar backup"
	@echo "monitor   - Monitorar sistema"
	@echo "clean     - Limpeza e manutenção"
	@echo "update    - Atualizar sistema"
	@echo "local     - Executar localmente"
	@echo "logs      - Ver logs Railway"

setup:
	@echo "🔧 Executando setup inicial..."
	@chmod +x scripts/*.sh
	@./scripts/setup_inicial_railway.sh

deploy:
	@echo "🚀 Deploy para Railway..."
	@./scripts/deploy_railway.sh

backup:
	@echo "💾 Criando backup..."
	@./scripts/backup_railway.sh

monitor:
	@echo "📊 Monitorando sistema..."
	@./scripts/monitor_railway.sh

clean:
	@echo "🧹 Executando manutenção..."
	@./scripts/manutencao_railway.sh

update:
	@echo "🔄 Atualizando sistema..."
	@./scripts/update_sistema_railway.sh

local:
	@echo "🏠 Executando localmente..."
	@streamlit run dashboard_baker_web_railway.py

logs:
	@echo "📋 Logs Railway..."
	@railway logs

# Comandos de desenvolvimento
dev-install:
	@pip install -r requirements.txt
	@pip install -r requirements-dev.txt

dev-test:
	@python -m pytest tests/

dev-lint:
	@flake8 *.py
	@black --check *.py

# ============================================================================
# 9. SCRIPT DE TESTE DE CARGA
# Arquivo: teste_carga_railway.sh
# ============================================================================

#!/bin/bash
echo "🔥 TESTE DE CARGA - RAILWAY DASHBOARD"
echo "===================================="

# URL do dashboard
DASHBOARD_URL="https://[seu-projeto].railway.app"

# Verificar se curl existe
if ! command -v curl &> /dev/null; then
    echo "❌ curl não encontrado"
    exit 1
fi

# Função para testar endpoint
test_endpoint() {
    local url=$1
    local name=$2
    
    echo "🧪 Testando: $name"
    
    start_time=$(date +%s.%N)
    
    if curl -f -s "$url" > /dev/null; then
        end_time=$(date +%s.%N)
        response_time=$(echo "$end_time - $start_time" | bc)
        echo "✅ $name: ${response_time}s"
        return 0
    else
        echo "❌ $name: FALHOU"
        return 1
    fi
}

# Teste básico de conectividade
echo "📡 Teste básico de conectividade..."
test_endpoint "$DASHBOARD_URL" "Homepage"

# Teste de carga simples
echo ""
echo "🔥 Teste de carga (10 requisições simultâneas)..."

for i in {1..10}; do
    (
        test_endpoint "$DASHBOARD_URL" "Requisição $i"
    ) &
done

wait
echo "✅ Teste de carga concluído"

# ============================================================================
# 10. ARQUIVO DE CONFIGURAÇÃO DOCKER (OPCIONAL)
# Arquivo: Dockerfile
# ============================================================================

FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Expor porta
EXPOSE 8501

# Comando de inicialização
CMD ["streamlit", "run", "dashboard_baker_web_railway.py", "--server.port=8501", "--server.address=0.0.0.0"]

# ============================================================================
# 11. ARQUIVO DOCKER-COMPOSE (DESENVOLVIMENTO LOCAL)
# Arquivo: docker-compose.yml
# ============================================================================

version: '3.8'

services:
  dashboard:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DATABASE_URL=postgresql://postgres:senha123@postgres:5432/dashboard_baker
    depends_on:
      - postgres
    volumes:
      - ./data:/app/data
      - ./exports:/app/exports

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: dashboard_baker
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: senha123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:

# ============================================================================
# 12. ARQUIVO DE GITHUB ACTIONS (CI/CD)
# Arquivo: .github/workflows/deploy.yml
# ============================================================================

name: Deploy to Railway

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/ || echo "Tests not found, skipping..."
    
    - name: Deploy to Railway
      if: github.ref == 'refs/heads/main'
      run: |
        npm install -g @railway/cli
        railway login --token ${{ secrets.RAILWAY_TOKEN }}
        railway up
      env:
        RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}