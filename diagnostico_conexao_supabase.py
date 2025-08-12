#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Diagnóstico e Correção - Dashboard Baker
Conexão Supabase PostgreSQL
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import json

# Cores para output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def carregar_env():
    """Carrega variáveis de ambiente"""
    # Tentar múltiplos caminhos
    env_paths = ['.env', '.env.local', '../.env', '../../.env']
    
    for path in env_paths:
        if os.path.exists(path):
            load_dotenv(path)
            print_success(f"Arquivo .env carregado de: {path}")
            return True
    
    # Se não encontrar, tentar criar
    print_warning("Arquivo .env não encontrado. Criando novo...")
    return False

def verificar_variaveis_ambiente():
    """Verifica se as variáveis de ambiente estão configuradas"""
    print_header("VERIFICANDO VARIÁVEIS DE AMBIENTE")
    
    variaveis_necessarias = {
        'SUPABASE_HOST': 'Host do Supabase',
        'SUPABASE_DB': 'Nome do banco de dados',
        'SUPABASE_USER': 'Usuário do banco',
        'SUPABASE_PASSWORD': 'Senha do banco',
        'SUPABASE_PORT': 'Porta do banco'
    }
    
    variaveis_faltando = []
    variaveis_encontradas = {}
    
    for var, descricao in variaveis_necessarias.items():
        valor = os.getenv(var)
        if valor:
            # Mascarar senha
            if 'PASSWORD' in var:
                valor_exibido = '*' * 8
            else:
                valor_exibido = valor
            print_success(f"{var}: {valor_exibido}")
            variaveis_encontradas[var] = valor
        else:
            print_error(f"{var}: NÃO ENCONTRADA - {descricao}")
            variaveis_faltando.append(var)
    
    return variaveis_encontradas, variaveis_faltando

def testar_conexao_supabase(config):
    """Testa conexão com o Supabase"""
    print_header("TESTANDO CONEXÃO SUPABASE")
    
    try:
        print_info("Tentando conectar ao Supabase...")
        print_info(f"Host: {config.get('host', 'N/A')}")
        print_info(f"Database: {config.get('database', 'N/A')}")
        print_info(f"User: {config.get('user', 'N/A')}")
        print_info(f"Port: {config.get('port', 'N/A')}")
        
        # Configuração de conexão com SSL
        conn_params = {
            'host': config.get('host'),
            'database': config.get('database', 'postgres'),
            'user': config.get('user', 'postgres'),
            'password': config.get('password'),
            'port': int(config.get('port', 5432)),
            'sslmode': 'require',
            'connect_timeout': 10
        }
        
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Teste simples
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print_success(f"Conectado com sucesso!")
        print_info(f"PostgreSQL versão: {version[0][:50]}...")
        
        # Verificar se a tabela existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'dashboard_baker'
            );
        """)
        
        tabela_existe = cursor.fetchone()[0]
        
        if tabela_existe:
            print_success("Tabela 'dashboard_baker' encontrada!")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM dashboard_baker;")
            count = cursor.fetchone()[0]
            print_info(f"Total de registros na tabela: {count}")
        else:
            print_warning("Tabela 'dashboard_baker' não existe")
            return conn, False
        
        cursor.close()
        return conn, True
        
    except psycopg2.OperationalError as e:
        print_error(f"Erro de conexão: {str(e)}")
        print_info("\nPossíveis causas:")
        print_info("1. Credenciais incorretas")
        print_info("2. Firewall/Rede bloqueando conexão")
        print_info("3. Serviço Supabase offline")
        print_info("4. SSL não configurado corretamente")
        return None, False
        
    except Exception as e:
        print_error(f"Erro inesperado: {str(e)}")
        return None, False

def criar_tabela_dashboard(conn):
    """Cria a tabela dashboard_baker se não existir"""
    print_header("CRIANDO ESTRUTURA DO BANCO")
    
    try:
        cursor = conn.cursor()
        
        # Script de criação da tabela
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS dashboard_baker (
            id SERIAL PRIMARY KEY,
            numero_cte INTEGER UNIQUE NOT NULL,
            destinatario_nome VARCHAR(255),
            veiculo_placa VARCHAR(20),
            valor_total DECIMAL(15,2),
            data_emissao DATE,
            numero_fatura VARCHAR(100),
            data_baixa DATE,
            observacao TEXT,
            data_inclusao_fatura DATE,
            data_envio_processo DATE,
            primeiro_envio DATE,
            data_rq_tmc DATE,
            data_atesto DATE,
            envio_final DATE,
            origem_dados VARCHAR(50) DEFAULT 'Sistema',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Criar índices para performance
        CREATE INDEX IF NOT EXISTS idx_numero_cte ON dashboard_baker(numero_cte);
        CREATE INDEX IF NOT EXISTS idx_data_emissao ON dashboard_baker(data_emissao);
        CREATE INDEX IF NOT EXISTS idx_destinatario ON dashboard_baker(destinatario_nome);
        """
        
        cursor.execute(create_table_sql)
        conn.commit()
        
        print_success("Tabela e índices criados com sucesso!")
        
        # Inserir registro de teste
        cursor.execute("""
            INSERT INTO dashboard_baker (
                numero_cte, destinatario_nome, valor_total, 
                data_emissao, origem_dados
            ) VALUES (
                1001, 'Cliente Teste Setup', 1500.00, 
                CURRENT_DATE, 'Diagnóstico'
            )
            ON CONFLICT (numero_cte) DO UPDATE
            SET updated_at = CURRENT_TIMESTAMP;
        """)
        
        conn.commit()
        print_success("Registro de teste inserido!")
        
        cursor.close()
        return True
        
    except Exception as e:
        print_error(f"Erro ao criar tabela: {str(e)}")
        return False

def criar_arquivo_env():
    """Cria arquivo .env com as configurações do Supabase"""
    print_header("CONFIGURANDO ARQUIVO .ENV")
    
    print_info("Por favor, forneça as credenciais do Supabase:")
    print_warning("Você pode encontrar essas informações em: Settings > Database no painel Supabase")
    
    config = {
        'SUPABASE_HOST': input("\n🔹 Host (ex: db.xxxx.supabase.co): ").strip(),
        'SUPABASE_DB': input("🔹 Database [postgres]: ").strip() or 'postgres',
        'SUPABASE_USER': input("🔹 User [postgres]: ").strip() or 'postgres',
        'SUPABASE_PASSWORD': input("🔹 Password: ").strip(),
        'SUPABASE_PORT': input("🔹 Port [5432]: ").strip() or '5432'
    }
    
    # Criar conteúdo do arquivo
    env_content = f"""# Dashboard Baker - Configurações Supabase
# Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

SUPABASE_HOST={config['SUPABASE_HOST']}
SUPABASE_DB={config['SUPABASE_DB']}
SUPABASE_USER={config['SUPABASE_USER']}
SUPABASE_PASSWORD={config['SUPABASE_PASSWORD']}
SUPABASE_PORT={config['SUPABASE_PORT']}

# Para forçar uso do Supabase
DATABASE_ENVIRONMENT=supabase
"""
    
    # Salvar arquivo
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print_success("Arquivo .env criado com sucesso!")
    
    # Também criar na pasta .streamlit se existir
    if os.path.exists('.streamlit'):
        secrets_content = f"""# Configurações Supabase - Dashboard Baker
[supabase]
host = "{config['SUPABASE_HOST']}"
password = "{config['SUPABASE_PASSWORD']}"
user = "{config['SUPABASE_USER']}"
database = "{config['SUPABASE_DB']}"
port = "{config['SUPABASE_PORT']}"

[database]
DB_HOST = "{config['SUPABASE_HOST']}"
DB_PASSWORD = "{config['SUPABASE_PASSWORD']}"
DB_USER = "{config['SUPABASE_USER']}"
DB_NAME = "{config['SUPABASE_DB']}"
DB_PORT = "{config['SUPABASE_PORT']}"
"""
        
        with open('.streamlit/secrets.toml', 'w', encoding='utf-8') as f:
            f.write(secrets_content)
        
        print_success("Arquivo .streamlit/secrets.toml também criado!")
    
    return config

def importar_dados_teste(conn):
    """Importa alguns dados de teste"""
    print_header("IMPORTANDO DADOS DE TESTE")
    
    try:
        cursor = conn.cursor()
        
        # Dados de exemplo baseados na planilha
        dados_teste = [
            (20949, 'BAKER HUGHES DO BRASIL LTDA', 'KDI7099', 614.27, '2024-06-03'),
            (840, 'BAKER HUGHES DO BRASIL LTDA', 'KAD7265', 553.30, '2024-05-17'),
            (21106, 'BAKER HUGHES DO BRASIL LTDA', 'KDI7099', 606.63, '2025-05-12'),
            (933, 'BAKER HUGHES DO BRASIL LTDA', 'KYE922', 623.45, '2025-05-16'),
            (934, 'BAKER HUGHES DO BRASIL LTDA', 'GQG4826', 767.36, '2025-05-25')
        ]
        
        for cte, destinatario, placa, valor, data in dados_teste:
            cursor.execute("""
                INSERT INTO dashboard_baker (
                    numero_cte, destinatario_nome, veiculo_placa,
                    valor_total, data_emissao, origem_dados
                ) VALUES (%s, %s, %s, %s, %s, 'Teste')
                ON CONFLICT (numero_cte) DO UPDATE
                SET valor_total = EXCLUDED.valor_total,
                    updated_at = CURRENT_TIMESTAMP;
            """, (cte, destinatario, placa, valor, data))
        
        conn.commit()
        print_success(f"{len(dados_teste)} registros de teste importados!")
        
        cursor.close()
        return True
        
    except Exception as e:
        print_error(f"Erro ao importar dados: {str(e)}")
        return False

def main():
    """Função principal do diagnóstico"""
    print_header("DIAGNÓSTICO DASHBOARD BAKER")
    print_info("Sistema de Diagnóstico e Correção v1.0")
    print_info(f"Executando em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # 1. Carregar variáveis de ambiente
    env_carregado = carregar_env()
    
    # 2. Verificar variáveis
    variaveis, faltando = verificar_variaveis_ambiente()
    
    # 3. Se faltar variáveis, criar .env
    if faltando:
        print_warning(f"\n{len(faltando)} variáveis faltando!")
        resposta = input("\nDeseja configurar agora? (s/n): ").lower()
        
        if resposta == 's':
            config = criar_arquivo_env()
            # Recarregar
            load_dotenv('.env')
            variaveis, faltando = verificar_variaveis_ambiente()
        else:
            print_error("Configuração cancelada. Execute novamente quando tiver as credenciais.")
            return
    
    # 4. Testar conexão
    config_supabase = {
        'host': variaveis.get('SUPABASE_HOST'),
        'database': variaveis.get('SUPABASE_DB', 'postgres'),
        'user': variaveis.get('SUPABASE_USER', 'postgres'),
        'password': variaveis.get('SUPABASE_PASSWORD'),
        'port': variaveis.get('SUPABASE_PORT', '5432')
    }
    
    conn, tabela_existe = testar_conexao_supabase(config_supabase)
    
    if conn:
        # 5. Criar tabela se necessário
        if not tabela_existe:
            resposta = input("\nDeseja criar a tabela agora? (s/n): ").lower()
            if resposta == 's':
                if criar_tabela_dashboard(conn):
                    # Importar dados de teste
                    resposta = input("\nDeseja importar dados de teste? (s/n): ").lower()
                    if resposta == 's':
                        importar_dados_teste(conn)
        
        conn.close()
        
        print_header("DIAGNÓSTICO CONCLUÍDO")
        print_success("Sistema configurado e pronto para uso!")
        print_info("\nPróximos passos:")
        print_info("1. Execute: streamlit run dashboard_baker_web_corrigido.py")
        print_info("2. O dashboard deve conectar automaticamente")
        print_info("3. Importe seus dados do CSV quando necessário")
        
    else:
        print_header("DIAGNÓSTICO CONCLUÍDO COM ERROS")
        print_error("Não foi possível estabelecer conexão com o banco.")
        print_info("\nVerifique:")
        print_info("1. Se as credenciais estão corretas")
        print_info("2. Se o Supabase está ativo")
        print_info("3. Se não há bloqueio de firewall")
        print_info("4. Execute novamente após corrigir os problemas")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Diagnóstico interrompido pelo usuário.")
    except Exception as e:
        print_error(f"\nErro crítico: {str(e)}")
        import traceback
        traceback.print_exc()