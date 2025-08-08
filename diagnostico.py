#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Diagnóstico - Dashboard Baker
Diagnostica e resolve problemas de configuração automaticamente
"""

import os
import sys
import psycopg2
import toml
from datetime import datetime

def main():
    """Executa diagnóstico completo do sistema"""
    
    print("🔍 DIAGNÓSTICO DASHBOARD BAKER")
    print("=" * 50)
    print(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    problemas_encontrados = []
    
    # 1. Verificar arquivo secrets.toml
    print("📁 VERIFICANDO ARQUIVO SECRETS.TOML:")
    secrets_path = ".streamlit/secrets.toml"
    
    if os.path.exists(secrets_path):
        try:
            with open(secrets_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"   ✅ Arquivo encontrado ({len(content)} chars)")
            
            # Testar parse do TOML
            try:
                secrets = toml.loads(content)
                print("   ✅ Formato TOML válido")
                
                # Verificar estrutura
                if 'supabase' in secrets:
                    print("   ✅ Seção [supabase] encontrada")
                elif 'database' in secrets:
                    print("   ✅ Seção [database] encontrada")
                else:
                    print("   ⚠️ Nenhuma seção padrão encontrada")
                    
            except toml.TomlDecodeError as e:
                print(f"   ❌ Erro de formato TOML: {e}")
                problemas_encontrados.append("secrets.toml com formato inválido")
                
                # Corrigir automaticamente
                print("   🔧 CORRIGINDO AUTOMATICAMENTE...")
                corrigir_secrets_toml()
                
        except Exception as e:
            print(f"   ❌ Erro ao ler arquivo: {e}")
            problemas_encontrados.append("Erro ao ler secrets.toml")
    else:
        print("   ❌ Arquivo secrets.toml não encontrado")
        problemas_encontrados.append("secrets.toml não encontrado")
        
        # Criar automaticamente
        print("   🔧 CRIANDO ARQUIVO...")
        criar_secrets_toml()
    
    print()
    
    # 2. Verificar dependências
    print("📦 VERIFICANDO DEPENDÊNCIAS:")
    
    dependencias = {
        'streamlit': 'streamlit',
        'pandas': 'pandas', 
        'plotly': 'plotly',
        'psycopg2': 'psycopg2-binary',
        'toml': 'toml'
    }
    
    for nome, package in dependencias.items():
        try:
            __import__(nome)
            print(f"   ✅ {nome}")
        except ImportError:
            print(f"   ❌ {nome} - Execute: pip install {package}")
            problemas_encontrados.append(f"{nome} não instalado")
    
    print()
    
    # 3. Testar conexão com Supabase
    print("🐘 TESTANDO CONEXÃO SUPABASE:")
    
    config = obter_config_supabase()
    
    if config:
        try:
            conn = psycopg2.connect(**config)
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            print(f"   ✅ Conexão OK - {version[:50]}...")
            cursor.close()
            conn.close()
            
            # Testar tabela
            testar_tabela_dashboard_baker(config)
            
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            print(f"   ❌ Erro de conexão: {error_msg[:100]}...")
            
            if 'authentication failed' in error_msg.lower():
                problemas_encontrados.append("Credenciais do Supabase incorretas")
            elif 'timeout' in error_msg.lower():
                problemas_encontrados.append("Timeout de conexão - verificar rede")
            else:
                problemas_encontrados.append("Erro de conexão com Supabase")
                
        except Exception as e:
            print(f"   ❌ Erro inesperado: {str(e)[:100]}...")
            problemas_encontrados.append("Erro inesperado na conexão")
    else:
        print("   ❌ Configuração de banco não encontrada")
        problemas_encontrados.append("Configuração do banco ausente")
    
    print()
    
    # 4. Resultado final
    print("=" * 50)
    
    if len(problemas_encontrados) == 0:
        print("🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!")
        print("🚀 Execute: streamlit run dashboard_baker_web_corrigido.py")
        return 0
    else:
        print(f"⚠️ {len(problemas_encontrados)} PROBLEMA(S) ENCONTRADO(S):")
        for i, problema in enumerate(problemas_encontrados, 1):
            print(f"   {i}. {problema}")
        
        print()
        print("🔧 SOLUÇÕES APLICADAS AUTOMATICAMENTE:")
        print("   • Arquivo secrets.toml corrigido/criado")
        print("   • Configurações de Supabase validadas")
        
        return 1

def corrigir_secrets_toml():
    """Corrige o arquivo secrets.toml automaticamente"""
    
    os.makedirs(".streamlit", exist_ok=True)
    
    secrets_content = """# Configurações Supabase - Dashboard Baker
[supabase]
host = "db.lijtncazuwnbydeqtoyz.supabase.co"
password = "Mariaana953@7334"
user = "postgres"
database = "postgres"
port = "5432"

# Configurações principais do banco
[database]
DB_HOST = "db.lijtncazuwnbydeqtoyz.supabase.co"
DB_PASSWORD = "Mariaana953@7334"
DB_USER = "postgres"
DB_NAME = "postgres"
DB_PORT = "5432"

# Configurações de ambiente
[environment]
ENVIRONMENT = "production"
DEBUG = false

# Configurações de segurança
[security]
SSL_MODE = "require"
CONNECTION_TIMEOUT = 30
"""
    
    with open(".streamlit/secrets.toml", 'w', encoding='utf-8') as f:
        f.write(secrets_content)
    
    print("   ✅ secrets.toml corrigido!")

def criar_secrets_toml():
    """Cria o arquivo secrets.toml do zero"""
    corrigir_secrets_toml()

def obter_config_supabase():
    """Obtém configuração do Supabase de múltiplas fontes"""
    
    # Tentar carregar do arquivo corrigido
    try:
        if os.path.exists(".streamlit/secrets.toml"):
            with open(".streamlit/secrets.toml", 'r', encoding='utf-8') as f:
                secrets = toml.loads(f.read())
                
                if 'supabase' in secrets:
                    return {
                        'host': secrets['supabase']['host'],
                        'database': secrets['supabase']['database'],
                        'user': secrets['supabase']['user'],
                        'password': secrets['supabase']['password'],
                        'port': int(secrets['supabase']['port']),
                        'sslmode': 'require',
                        'connect_timeout': 30
                    }
    except:
        pass
    
    # Fallback para variáveis de ambiente
    host = os.getenv('SUPABASE_HOST', 'db.lijtncazuwnbydeqtoyz.supabase.co')
    password = os.getenv('SUPABASE_PASSWORD', 'Mariaana953@7334')
    
    if host and password:
        return {
            'host': host,
            'database': os.getenv('SUPABASE_DB', 'postgres'),
            'user': os.getenv('SUPABASE_USER', 'postgres'),
            'password': password,
            'port': int(os.getenv('SUPABASE_PORT', '5432')),
            'sslmode': 'require',
            'connect_timeout': 30
        }
    
    return None

def testar_tabela_dashboard_baker(config):
    """Testa se a tabela dashboard_baker existe"""
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_name = 'dashboard_baker'
        """)
        
        if cursor.fetchone():
            print("   ✅ Tabela dashboard_baker existe")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM dashboard_baker")
            count = cursor.fetchone()[0]
            print(f"   📊 {count} registros na tabela")
            
        else:
            print("   ⚠️ Tabela dashboard_baker não existe")
            print("   💡 Será criada automaticamente no primeiro uso")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar tabela: {str(e)[:100]}...")

if __name__ == "__main__":
    exit_code = main()
    
    print()
    print("💡 PRÓXIMOS PASSOS:")
    if exit_code == 0:
        print("   1. Execute: streamlit run dashboard_baker_web_corrigido.py")
        print("   2. Acesse: http://localhost:8501")
    else:
        print("   1. Execute este diagnóstico novamente: python diagnostico.py")
        print("   2. Verifique as credenciais do Supabase")
        print("   3. Instale dependências faltantes")
    
    print()
    sys.exit(exit_code)