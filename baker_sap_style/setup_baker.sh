#!/bin/bash
# ===================================================
# SETUP AUTOMÁTICO - DASHBOARD BAKER
# Sistema completo de instalação e configuração
# ===================================================

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções auxiliares
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner
echo -e "${BLUE}"
cat << "EOF"
██████╗  █████╗ ██╗  ██╗███████╗██████╗ 
██╔══██╗██╔══██╗██║ ██╔╝██╔════╝██╔══██╗
██████╔╝███████║█████╔╝ █████╗  ██████╔╝
██╔══██╗██╔══██║██╔═██╗ ██╔══╝  ██╔══██╗
██████╔╝██║  ██║██║  ██╗███████╗██║  ██║
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝

DASHBOARD FINANCEIRO - SETUP AUTOMÁTICO
EOF
echo -e "${NC}"

echo "========================================================"
echo "🚀 Iniciando configuração automática do Dashboard Baker"
echo "========================================================"

# Verificar se está rodando como root
if [[ $EUID -eq 0 ]]; then
   log_error "Este script não deve ser executado como root"
   exit 1
fi

# Detectar sistema operacional
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    DISTRO=$(lsb_release -si 2>/dev/null || echo "Unknown")
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
else
    OS="unknown"
fi

log_info "Sistema detectado: $OS"

# Função para instalar Docker
install_docker() {
    log_info "Instalando Docker..."
    
    if [[ "$OS" == "linux" ]]; then
        # Remover versões antigas
        sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
        
        # Atualizar repositórios
        sudo apt-get update
        
        # Instalar dependências
        sudo apt-get install -y \
            apt-transport-https \
            ca-certificates \
            curl \
            gnupg \
            lsb-release
        
        # Adicionar chave GPG oficial do Docker
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        
        # Adicionar repositório
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # Instalar Docker
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
        
        # Adicionar usuário ao grupo docker
        sudo usermod -aG docker $USER
        
    elif [[ "$OS" == "macos" ]]; then
        log_info "Para macOS, baixe Docker Desktop de: https://www.docker.com/products/docker-desktop"
        log_warning "Após instalar, execute novamente este script"
        exit 1
    else
        log_error "Sistema não suportado para instalação automática do Docker"
        log_info "Instale Docker manualmente: https://docs.docker.com/get-docker/"
        exit 1
    fi
}

# Verificar Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_warning "Docker não encontrado"
        read -p "Deseja instalar Docker automaticamente? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_docker
            log_success "Docker instalado! Faça logout/login e execute novamente"
            exit 0
        else
            log_error "Docker é necessário para continuar"
            exit 1
        fi
    else
        log_success "Docker encontrado: $(docker --version)"
    fi
    
    # Verificar se Docker está rodando
    if ! docker info &> /dev/null; then
        log_error "Docker não está rodando"
        log_info "Inicie o Docker e execute novamente"
        exit 1
    fi
    
    # Verificar Docker Compose
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose não encontrado"
        log_info "Instale Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    else
        log_success "Docker Compose encontrado: $(docker compose version)"
    fi
}

# Criar estrutura de diretórios
create_directories() {
    log_info "Criando estrutura de diretórios..."
    
    mkdir -p {credentials,data,exports,backups,logs,uploads,ssl}
    
    log_success "Diretórios criados"
}

# Criar arquivos de configuração
create_config_files() {
    log_info "Criando arquivos de configuração..."
    
    # requirements.txt
    cat << EOF > requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
streamlit==1.28.1
pandas==2.1.3
plotly==5.17.0
gspread==5.12.0
google-auth==2.23.4
google-auth-oauthlib==1.1.0
psycopg2-binary==2.9.9
reportlab==4.0.7
celery==5.3.4
redis==5.0.1
python-multipart==0.0.6
pydantic==2.5.0
email-validator==2.1.0
openpyxl==3.1.2
xlsxwriter==3.1.9
aiofiles==23.2.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
jinja2==3.1.2
EOF

    # nginx.conf
    cat << 'EOF' > nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }
    
    upstream dashboard {
        server dashboard:8501;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=dashboard:10m rate=5r/s;
    
    server {
        listen 80;
        server_name localhost;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl;
        server_name localhost;
        
        # SSL Configuration (self-signed for development)
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        
        # API Routes
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Dashboard Routes
        location / {
            limit_req zone=dashboard burst=10 nodelay;
            proxy_pass http://dashboard;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support for Streamlit
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
        
        # Health check endpoint
        location /health {
            proxy_pass http://api/health;
            access_log off;
        }
    }
}
EOF

    # init_db.sql
    cat << 'EOF' > init_db.sql
-- Inicialização do banco Dashboard Baker
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabela principal dos CTEs
CREATE TABLE IF NOT EXISTS dashboard_baker (
    id SERIAL PRIMARY KEY,
    numero_cte VARCHAR(50) UNIQUE NOT NULL,
    destinatario_nome VARCHAR(255),
    veiculo_placa VARCHAR(20),
    valor_total DECIMAL(15,2) DEFAULT 0.00,
    data_emissao DATE,
    data_inclusao_fatura DATE,
    data_envio_processo DATE,
    primeiro_envio DATE,
    data_rq_tmc DATE,
    data_atesto DATE,
    envio_final DATE,
    numero_fatura VARCHAR(100),
    data_baixa DATE,
    observacao TEXT,
    status_processamento VARCHAR(50) DEFAULT 'ATIVO',
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    origem_dados VARCHAR(50) DEFAULT 'GOOGLE_SHEETS',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uuid UUID DEFAULT uuid_generate_v4()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_numero_cte ON dashboard_baker(numero_cte);
CREATE INDEX IF NOT EXISTS idx_data_emissao ON dashboard_baker(data_emissao);
CREATE INDEX IF NOT EXISTS idx_status ON dashboard_baker(status_processamento);
CREATE INDEX IF NOT EXISTS idx_data_baixa ON dashboard_baker(data_baixa);
CREATE INDEX IF NOT EXISTS idx_destinatario ON dashboard_baker(destinatario_nome);
CREATE INDEX IF NOT EXISTS idx_veiculo ON dashboard_baker(veiculo_placa);

-- Tabela de logs de ações
CREATE TABLE IF NOT EXISTS baker_logs (
    id SERIAL PRIMARY KEY,
    acao VARCHAR(100) NOT NULL,
    usuario VARCHAR(100),
    detalhes JSONB,
    ip_address INET,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de configurações
CREATE TABLE IF NOT EXISTS baker_config (
    id SERIAL PRIMARY KEY,
    chave VARCHAR(100) UNIQUE NOT NULL,
    valor TEXT,
    descricao VARCHAR(255),
    tipo VARCHAR(50) DEFAULT 'string',
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserir configurações padrão
INSERT INTO baker_config (chave, valor, descricao, tipo) VALUES
('sistema_version', '1.0.0', 'Versão do sistema', 'string'),
('alertas_enabled', 'true', 'Alertas automáticos habilitados', 'boolean'),
('sync_interval', '240', 'Intervalo de sincronização em minutos', 'integer'),
('backup_retention', '30', 'Dias para retenção de backup', 'integer')
ON CONFLICT (chave) DO NOTHING;

-- Função para atualizar timestamp
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $
BEGIN
    NEW.data_atualizacao = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$ LANGUAGE plpgsql;

-- Trigger para atualizar timestamp automaticamente
DROP TRIGGER IF EXISTS trigger_update_timestamp ON dashboard_baker;
CREATE TRIGGER trigger_update_timestamp
    BEFORE UPDATE ON dashboard_baker
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- View para métricas rápidas
CREATE OR REPLACE VIEW baker_metricas AS
SELECT 
    COUNT(*) as total_registros,
    SUM(valor_total) as valor_total,
    COUNT(*) FILTER (WHERE data_baixa IS NOT NULL) as faturas_pagas,
    COUNT(*) FILTER (WHERE data_baixa IS NULL) as faturas_abertas,
    COUNT(*) FILTER (WHERE numero_fatura IS NOT NULL AND numero_fatura != '') as com_fatura,
    COUNT(*) FILTER (WHERE numero_fatura IS NULL OR numero_fatura = '') as sem_fatura,
    COUNT(DISTINCT destinatario_nome) as total_clientes,
    COUNT(DISTINCT veiculo_placa) as total_veiculos,
    AVG(valor_total) as valor_medio,
    MAX(data_atualizacao) as ultima_atualizacao
FROM dashboard_baker 
WHERE status_processamento = 'ATIVO';
EOF

    # backup_script.sh
    cat << 'EOF' > backup_script.sh
#!/bin/bash
# Script de backup automático

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="dashboard_baker"
DB_USER="dashboard_user"
DB_HOST="postgres"

# Criar backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > "$BACKUP_DIR/backup_$DATE.sql"

# Comprimir backup
gzip "$BACKUP_DIR/backup_$DATE.sql"

# Manter apenas últimos 7 backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup criado: backup_$DATE.sql.gz"
EOF
    chmod +x backup_script.sh

    # worker_tasks.py
    cat << 'EOF' > worker_tasks.py
#!/usr/bin/env python3
"""
Worker para tarefas em background do Dashboard Baker
"""

from celery import Celery
import os
import sys
import argparse
from datetime import datetime
import logging

# Configurar Celery
celery_app = Celery(
    'baker_worker',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery_app.task
def executar_sincronizacao():
    """Tarefa de sincronização periódica"""
    try:
        from google_sheets_conciliacao import SistemaConciliacaoCompleto
        
        sistema = SistemaConciliacaoCompleto()
        
        # Configurar PostgreSQL
        config_postgres = {
            'host': 'postgres',
            'database': 'dashboard_baker',
            'user': 'dashboard_user',
            'password': 'baker_postgres_2025',
            'port': 5432
        }
        
        if sistema.configurar_postgresql(config_postgres):
            logger.info("Sincronização periódica iniciada")
            # Aqui você adicionaria a lógica de sincronização
            return {"status": "success", "timestamp": datetime.now().isoformat()}
        
    except Exception as e:
        logger.error(f"Erro na sincronização periódica: {str(e)}")
        return {"status": "error", "error": str(e)}

@celery_app.task
def executar_alertas():
    """Tarefa de alertas automáticos"""
    try:
        from google_sheets_conciliacao import SistemaConciliacaoCompleto
        
        sistema = SistemaConciliacaoCompleto()
        
        # Configurar PostgreSQL
        config_postgres = {
            'host': 'postgres',
            'database': 'dashboard_baker',
            'user': 'dashboard_user',
            'password': 'baker_postgres_2025',
            'port': 5432
        }
        
        if sistema.configurar_postgresql(config_postgres):
            success = sistema.executar_alertas_automaticos()
            logger.info(f"Alertas executados: {success}")
            return {"status": "success" if success else "partial", "timestamp": datetime.now().isoformat()}
        
    except Exception as e:
        logger.error(f"Erro nos alertas automáticos: {str(e)}")
        return {"status": "error", "error": str(e)}

@celery_app.task
def limpar_logs_antigos():
    """Limpa logs antigos"""
    try:
        import glob
        import time
        
        # Remover logs com mais de 30 dias
        log_files = glob.glob("/app/logs/*.log")
        cutoff_time = time.time() - (30 * 24 * 60 * 60)  # 30 dias
        
        removed_count = 0
        for log_file in log_files:
            if os.path.getmtime(log_file) < cutoff_time:
                os.remove(log_file)
                removed_count += 1
        
        logger.info(f"Removidos {removed_count} arquivos de log antigos")
        return {"status": "success", "removed_files": removed_count}
        
    except Exception as e:
        logger.error(f"Erro ao limpar logs: {str(e)}")
        return {"status": "error", "error": str(e)}

# Configurar tarefas periódicas
celery_app.conf.beat_schedule = {
    'sincronizacao-periodica': {
        'task': 'worker_tasks.executar_sincronizacao',
        'schedule': 240.0,  # A cada 4 horas
    },
    'alertas-diarios': {
        'task': 'worker_tasks.executar_alertas',
        'schedule': 28800.0,  # A cada 8 horas
    },
    'limpeza-logs': {
        'task': 'worker_tasks.limpar_logs_antigos',
        'schedule': 86400.0,  # Diário
    },
}

celery_app.conf.timezone = 'America/Sao_Paulo'

# Execução direta para tarefas pontuais
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Baker Worker Tasks')
    parser.add_argument('--task', choices=['sync', 'alertas', 'limpeza'], required=True)
    
    args = parser.parse_args()
    
    if args.task == 'sync':
        result = executar_sincronizacao.delay()
        print(f"Sincronização iniciada: {result.id}")
    elif args.task == 'alertas':
        result = executar_alertas.delay()
        print(f"Alertas iniciados: {result.id}")
    elif args.task == 'limpeza':
        result = limpar_logs_antigos.delay()
        print(f"Limpeza iniciada: {result.id}")
EOF

    log_success "Arquivos de configuração criados"
}

# Gerar certificados SSL auto-assinados
generate_ssl_certs() {
    log_info "Gerando certificados SSL auto-assinados..."
    
    if [[ ! -f ssl/cert.pem ]]; then
        openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes -subj "/C=BR/ST=SP/L=SaoPaulo/O=Baker/CN=localhost"
        log_success "Certificados SSL gerados"
    else
        log_info "Certificados SSL já existem"
    fi
}

# Configurar credenciais Google
setup_google_credentials() {
    log_info "Configuração das credenciais Google Sheets..."
    
    if [[ ! -f credentials/google_credentials.json ]]; then
        log_warning "Credenciais Google não encontradas"
        echo
        echo "Para configurar Google Sheets:"
        echo "1. Acesse: https://console.cloud.google.com/"
        echo "2. Crie um projeto ou use existente"
        echo "3. Ative Google Sheets API e Google Drive API"
        echo "4. Crie credenciais (Service Account ou OAuth2)"
        echo "5. Baixe o arquivo JSON"
        echo "6. Coloque em: credentials/google_credentials.json"
        echo
        read -p "Pressione Enter para continuar..."
    else
        log_success "Credenciais Google encontradas"
    fi
}

# Verificar portas disponíveis
check_ports() {
    log_info "Verificando portas disponíveis..."
    
    ports=(80 443 5432 6379 8000 8501)
    
    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            log_warning "Porta $port está em uso"
            if [[ $port -eq 80 || $port -eq 443 ]]; then
                log_info "Você pode precisar parar outros serviços web"
            fi
        else
            log_success "Porta $port disponível"
        fi
    done
}

# Baixar imagens Docker
pull_docker_images() {
    log_info "Baixando imagens Docker base..."
    
    docker pull postgres:15-alpine
    docker pull redis:7-alpine
    docker pull nginx:alpine
    docker pull python:3.11-slim
    
    log_success "Imagens base baixadas"
}

# Função principal de instalação
main_install() {
    log_info "Iniciando instalação completa do Dashboard Baker"
    
    # Verificações iniciais
    check_docker
    check_ports
    
    # Criar estrutura
    create_directories
    create_config_files
    generate_ssl_certs
    setup_google_credentials
    
    # Preparar Docker
    pull_docker_images
    
    # Build e start dos containers
    log_info "Construindo e iniciando containers..."
    docker compose build --parallel
    docker compose up -d
    
    # Aguardar serviços ficarem prontos
    log_info "Aguardando serviços ficarem prontos..."
    sleep 30
    
    # Verificar saúde dos serviços
    log_info "Verificando saúde dos serviços..."
    
    # Testar API
    if curl -f http://localhost:8000/health &>/dev/null; then
        log_success "API está respondendo"
    else
        log_warning "API pode não estar pronta ainda"
    fi
    
    # Testar Dashboard
    if curl -f http://localhost:8501/_stcore/health &>/dev/null; then
        log_success "Dashboard está respondendo"
    else
        log_warning "Dashboard pode não estar pronto ainda"
    fi
    
    # Mostrar informações finais
    echo
    echo "========================================================"
    log_success "INSTALAÇÃO CONCLUÍDA!"
    echo "========================================================"
    echo
    echo "🌐 Serviços disponíveis:"
    echo "   • Dashboard: https://localhost (ou http://localhost:8501)"
    echo "   • API REST: https://localhost/api (ou http://localhost:8000)"
    echo "   • Documentação API: http://localhost:8000/docs"
    echo "   • PostgreSQL: localhost:5432"
    echo "   • Redis: localhost:6379"
    echo
    echo "🔑 Credenciais padrão:"
    echo "   • API Key: baker_2025_secure_key"
    echo "   • PostgreSQL: dashboard_user / baker_postgres_2025"
    echo
    echo "📁 Diretórios importantes:"
    echo "   • credentials/ - Credenciais Google Sheets"
    echo "   • data/ - Arquivos CSV"
    echo "   • exports/ - Relatórios gerados"
    echo "   • backups/ - Backups automáticos"
    echo "   • logs/ - Logs do sistema"
    echo
    echo "🚀 Próximos passos:"
    echo "   1. Configure credenciais Google em credentials/google_credentials.json"
    echo "   2. Acesse https://localhost para usar o dashboard"
    echo "   3. Configure alertas por email na interface"
    echo "   4. Carregue seus dados CSV"
    echo
    echo "📖 Comandos úteis:"
    echo "   • Ver logs: docker compose logs -f"
    echo "   • Parar: docker compose down"
    echo "   • Reiniciar: docker compose restart"
    echo "   • Backup manual: docker compose exec postgres pg_dump -U dashboard_user dashboard_baker > backup.sql"
    echo
}

# Menu interativo
show_menu() {
    echo
    echo "========================================================"
    echo "🛠️  MENU DE INSTALAÇÃO - DASHBOARD BAKER"
    echo "========================================================"
    echo
    echo "1) 🚀 Instalação completa (recomendado)"
    echo "2) 🔧 Apenas verificar dependências"
    echo "3) 📁 Criar apenas estrutura de arquivos"
    echo "4) 🐳 Apenas build dos containers Docker"
    echo "5) 📊 Verificar status dos serviços"
    echo "6) 🔄 Reiniciar serviços"
    echo "7) 🛑 Parar todos os serviços"
    echo "8) 📋 Mostrar logs"
    echo "9) 🧹 Limpeza completa (CUIDADO!)"
    echo "0) ❌ Sair"
    echo
    read -p "Escolha uma opção (0-9): " choice
    
    case $choice in
        1)
            main_install
            ;;
        2)
            check_docker
            check_ports
            ;;
        3)
            create_directories
            create_config_files
            ;;
        4)
            docker compose build --parallel
            ;;
        5)
            docker compose ps
            echo
            curl -f http://localhost:8000/health 2>/dev/null && echo "✅ API OK" || echo "❌ API indisponível"
            curl -f http://localhost:8501/_stcore/health 2>/dev/null && echo "✅ Dashboard OK" || echo "❌ Dashboard indisponível"
            ;;
        6)
            docker compose restart
            log_success "Serviços reiniciados"
            ;;
        7)
            docker compose down
            log_success "Serviços parados"
            ;;
        8)
            docker compose logs -f
            ;;
        9)
            read -p "⚠️  Isso removerá TODOS os dados. Confirma? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                docker compose down -v
                docker system prune -f
                sudo rm -rf data/* exports/* backups/* logs/*
                log_success "Limpeza completa realizada"
            fi
            ;;
        0)
            log_info "Saindo..."
            exit 0
            ;;
        *)
            log_error "Opção inválida"
            ;;
    esac
}

# Verificar argumentos de linha de comando
if [[ $# -eq 0 ]]; then
    # Modo interativo
    while true; do
        show_menu
        echo
        read -p "Pressione Enter para voltar ao menu..."
    done
else
    # Modo não interativo
    case "$1" in
        "install")
            main_install
            ;;
        "check")
            check_docker
            check_ports
            ;;
        "build")
            docker compose build --parallel
            ;;
        "start")
            docker compose up -d
            ;;
        "stop")
            docker compose down
            ;;
        "logs")
            docker compose logs -f
            ;;
        "status")
            docker compose ps
            ;;
        *)
            echo "Uso: $0 [install|check|build|start|stop|logs|status]"
            echo "Ou execute sem argumentos para menu interativo"
            exit 1
            ;;
    esac
fi