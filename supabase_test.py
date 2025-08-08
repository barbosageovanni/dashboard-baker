#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Específico de Conexão Supabase
Valida configurações e conectividade
"""

import os
import sys
import psycopg2
from datetime import datetime

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def load_env_file():
    """Carrega arquivo .env se existir"""
    if os.path.exists('.env'):
        print("✅ Arquivo .env encontrado")
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")
        return True
    else:
        print("❌ Arquivo .env não encontrado")
        return False

def test_supabase_connection():
    """Testa conexão específica com Supabase"""
    print_header("🧪 TESTE DE CONEXÃO SUPABASE")
    
    # Carregar variáveis de ambiente
    load_env_file()
    
    # Configurações Supabase
    configs = {
        'host': os.getenv('PGHOST') or os.getenv('SUPABASE_HOST'),
        'database': os.getenv('PGDATABASE', 'postgres'),
        'user': os.getenv('PGUSER', 'postgres'),
        'password': os.getenv('PGPASSWORD') or os.getenv('SUPABASE_PASSWORD'),
        'port': int(os.getenv('PGPORT', '5432')),
        'sslmode': 'require',  # Obrigatório para Supabase
        'connect_timeout': 10
    }
    
    print("🔍 CONFIGURAÇÕES DETECTADAS:")
    print(f"   Host: {configs['host']}")
    print(f"   Database: {configs['database']}")
    print(f"   User: {configs['user']}")
    print(f"   Password: {'***' + configs['password'][-4:] if configs['password'] else 'AUSENTE'}")
    print(f"   Port: {configs['port']}")
    print(f"   SSL: {configs['sslmode']}")
    
    # Validar configurações obrigatórias
    missing_configs = []
    if not configs['host']:
        missing_configs.append('PGHOST/SUPABASE_HOST')
    if not configs['password']:
        missing_configs.append('PGPASSWORD/SUPABASE_PASSWORD')
    
    if missing_configs:
        print(f"\n❌ CONFIGURAÇÕES AUSENTES: {', '.join(missing_configs)}")
        print("\n💡 COMO CORRIGIR:")
        print("1. Acesse: https://app.supabase.com/")
        print("2. Selecione seu projeto")
        print("3. Settings > Database > Connection Info")
        print("4. Copie as credenciais para o arquivo .env")
        return False
    
    # Testar conexão
    print(f"\n🔄 Testando conexão com {configs['host']}...")
    
    try:
        # Conectar ao Supabase
        conn = psycopg2.connect(**configs)
        cursor = conn.cursor()
        
        print("✅ Conexão estabelecida com sucesso!")
        
        # Testar query básica
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL Version: {version[:50]}...")
        
        # Verificar tabela dashboard_baker
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_name = 'dashboard_baker'
        """)
        
        if cursor.fetchone():
            print("✅ Tabela 'dashboard_baker' encontrada")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM dashboard_baker")
            count = cursor.fetchone()[0]
            print(f"✅ Registros na tabela: {count:,}")
            
            if count > 0:
                # Testar uma query mais complexa
                cursor.execute("""
                    SELECT numero_cte, destinatario_nome, valor_total 
                    FROM dashboard_baker 
                    LIMIT 3
                """)
                
                print("✅ Dados de amostra:")
                for row in cursor.fetchall():
                    print(f"   CTE {row[0]}: {row[1]} - R$ {row[2]:,.2f}")
            
        else:
            print("⚠️ Tabela 'dashboard_baker' não encontrada")
            print("💡 Execute: python create_table.py")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        print(f"❌ Erro de conexão: {error_msg}")
        
        # Diagnóstico específico
        if "no password supplied" in error_msg:
            print("💡 Problema: Senha não configurada no .env")
        elif "authentication failed" in error_msg:
            print("💡 Problema: Senha incorreta")
        elif "timeout" in error_msg:
            print("💡 Problema: Timeout de conexão (firewall/rede)")
        elif "could not translate host name" in error_msg:
            print("💡 Problema: Host inválido ou incorreto")
        
        return False
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def create_env_template():
    """Cria template .env para Supabase"""
    print_header("📝 CRIANDO TEMPLATE .ENV")
    
    template = """# Dashboard Baker - Configuração Supabase
# ==========================================
# 
# 🔧 SUBSTITUA pelos dados do seu Supabase:
# 1. Acesse: https://app.supabase.com/
# 2. Selecione seu projeto
# 3. Settings > Database > Connection Info
# 4. Copie as informações abaixo:

PGHOST=db.xxxxx.supabase.co
PGDATABASE=postgres
PGUSER=postgres
PGPASSWORD=sua-senha-aqui
PGPORT=5432

# Configurações adicionais
SUPABASE_HOST=db.xxxxx.supabase.co
SUPABASE_DB=postgres
SUPABASE_USER=postgres
SUPABASE_PASSWORD=sua-senha-aqui
SUPABASE_PORT=5432

# Configurações da aplicação
APP_NAME=Dashboard Financeiro Baker
APP_VERSION=3.0
DEBUG_MODE=false
"""
    
    try:
        if not os.path.exists('.env'):
            with open('.env', 'w', encoding='utf-8') as f:
                f.write(template)
            print("✅ Arquivo .env criado com template")
            print("💡 Edite o arquivo .env com suas credenciais Supabase")
        else:
            print("ℹ️ Arquivo .env já existe")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar .env: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE ESPECÍFICO SUPABASE")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Se .env não existe, criar template
    if not os.path.exists('.env'):
        create_env_template()
        print("\n⚠️ Configure o arquivo .env antes de continuar")
        return 1
    
    # Testar conexão
    success = test_supabase_connection()
    
    print_header("🎯 RESULTADO FINAL")
    
    if success:
        print("🎉 SUPABASE CONECTADO COM SUCESSO!")
        print("✅ Todas as configurações estão corretas")
        print("🚀 Sistema pronto para deploy no Streamlit Cloud")
        return 0
    else:
        print("❌ PROBLEMAS DE CONEXÃO ENCONTRADOS")
        print("🔧 Corrija as configurações e teste novamente")
        print("💡 Execute: python supabase_test.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())