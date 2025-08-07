#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORREÇÃO DE CONFIGURAÇÃO POSTGRESQL RAILWAY
Detecta e corrige problemas de conexão com Railway PostgreSQL
"""

import os
import sys
import subprocess
import json

def verificar_railway_cli():
    """Verifica se Railway CLI está instalado e funcionando"""
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Railway CLI: {result.stdout.strip()}")
            return True
        else:
            print("❌ Railway CLI não está funcionando")
            return False
    except FileNotFoundError:
        print("❌ Railway CLI não encontrado")
        print("💡 Instale com: npm install -g @railway/cli")
        return False

def obter_variaveis_railway():
    """Obtém todas as variáveis de ambiente do Railway"""
    try:
        result = subprocess.run(['railway', 'variables'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Variáveis do Railway obtidas")
            return result.stdout
        else:
            print(f"❌ Erro ao obter variáveis: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def obter_database_url():
    """Obtém DATABASE_URL do Railway"""
    try:
        result = subprocess.run(['railway', 'variables', 'get', 'DATABASE_URL'], 
                              capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            database_url = result.stdout.strip()
            print(f"✅ DATABASE_URL encontrada")
            return database_url
        else:
            print("❌ DATABASE_URL não encontrada")
            return None
    except Exception as e:
        print(f"❌ Erro ao obter DATABASE_URL: {e}")
        return None

def parsear_database_url(database_url):
    """Parse da DATABASE_URL para extrair componentes"""
    try:
        import urllib.parse as urlparse
        url = urlparse.urlparse(database_url)
        
        config = {
            'host': url.hostname,
            'database': url.path[1:],  # Remove primeira barra
            'user': url.username,
            'password': url.password,
            'port': url.port or 5432
        }
        
        print("✅ DATABASE_URL parseada:")
        print(f"   Host: {config['host']}")
        print(f"   Database: {config['database']}")
        print(f"   User: {config['user']}")
        print(f"   Port: {config['port']}")
        
        return config
    except Exception as e:
        print(f"❌ Erro ao parsear DATABASE_URL: {e}")
        return None

def configurar_variaveis_individuais(config):
    """Configura variáveis individuais no Railway"""
    try:
        variaveis = {
            'PGHOST': config['host'],
            'PGDATABASE': config['database'],
            'PGUSER': config['user'],
            'PGPASSWORD': config['password'],
            'PGPORT': str(config['port'])
        }
        
        for var, valor in variaveis.items():
            result = subprocess.run([
                'railway', 'variables', 'set', f'{var}={valor}'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {var} configurada")
            else:
                print(f"❌ Erro ao configurar {var}: {result.stderr}")
                
    except Exception as e:
        print(f"❌ Erro ao configurar variáveis: {e}")

def criar_arquivo_env_local(config):
    """Cria arquivo .env local para desenvolvimento"""
    try:
        env_content = f"""# Railway PostgreSQL Configuration
DATABASE_URL=postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}
PGHOST={config['host']}
PGPORT={config['port']}
PGDATABASE={config['database']}
PGUSER={config['user']}
PGPASSWORD={config['password']}

# Configurações Streamlit
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Ambiente
RAILWAY_ENVIRONMENT=production
"""
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ Arquivo .env criado para desenvolvimento local")
        
    except Exception as e:
        print(f"❌ Erro ao criar .env: {e}")

def testar_conexao_postgresql(config):
    """Testa conexão com PostgreSQL"""
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host=config['host'],
            database=config['database'],
            user=config['user'],
            password=config['password'],
            port=config['port'],
            sslmode='require'
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print(f"✅ Conexão PostgreSQL OK: {version[0][:50]}...")
        
        cursor.close()
        conn.close()
        return True
        
    except ImportError:
        print("❌ psycopg2 não instalado")
        print("💡 Instale com: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def main():
    """Função principal de correção"""
    print("🔧 CORREÇÃO POSTGRESQL RAILWAY")
    print("=" * 40)
    
    # 1. Verificar Railway CLI
    if not verificar_railway_cli():
        return False
    
    # 2. Obter DATABASE_URL
    database_url = obter_database_url()
    if not database_url:
        print("❌ Não foi possível obter DATABASE_URL")
        print("💡 Certifique-se que PostgreSQL foi adicionado ao projeto")
        return False
    
    # 3. Parsear DATABASE_URL
    config = parsear_database_url(database_url)
    if not config:
        return False
    
    # 4. Configurar variáveis individuais
    print("\n🔧 Configurando variáveis individuais...")
    configurar_variaveis_individuais(config)
    
    # 5. Criar .env local
    print("\n📄 Criando arquivo .env local...")
    criar_arquivo_env_local(config)
    
    # 6. Testar conexão
    print("\n🧪 Testando conexão...")
    if testar_conexao_postgresql(config):
        print("\n🎉 CONFIGURAÇÃO CORRIGIDA COM SUCESSO!")
        print("💡 Agora você pode fazer o deploy com: railway up")
        return True
    else:
        print("\n❌ Ainda há problemas de conexão")
        return False

if __name__ == "__main__":
    main()