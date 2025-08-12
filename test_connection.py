#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Conexão - Dashboard Baker
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

def carregar_env():
    """Carrega variáveis de ambiente do arquivo .env"""
    env_path = '.env'
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                if linha and not linha.startswith('#') and '=' in linha:
                    chave, valor = linha.split('=', 1)
                    os.environ[chave.strip()] = valor.strip()

def _detectar_ambiente():
    """Detecta ambiente atual"""
    if os.getenv('SUPABASE_HOST') and os.getenv('SUPABASE_PASSWORD'):
        return 'supabase'
    elif os.getenv('DATABASE_URL'):
        return 'render'
    else:
        return 'local'

def _config_supabase():
    """Configuração Supabase PostgreSQL"""
    return {
        'host': os.getenv('SUPABASE_HOST'),
        'database': os.getenv('SUPABASE_DB', 'postgres'),
        'user': os.getenv('SUPABASE_USER', 'postgres'),
        'password': os.getenv('SUPABASE_PASSWORD'),
        'port': int(os.getenv('SUPABASE_PORT', '5432')),
        'sslmode': 'require',
        'connect_timeout': 10
    }

def _config_local():
    """Configuração PostgreSQL Local"""
    return {
        'host': 'localhost',
        'database': 'dashboard_baker',
        'user': 'postgres',
        'password': os.getenv('LOCAL_DB_PASSWORD', 'senha123'),
        'port': 5432,
        'connect_timeout': 5
    }

def _testar_conexao(config):
    """Testa conexão com o banco"""
    if not config or not config.get('host') or not config.get('password'):
        return False
    
    try:
        print(f"🔗 Tentando conectar em: {config['host']}:{config['port']}")
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def main():
    print("🧪 TESTE DE CONEXÃO - DASHBOARD BAKER")
    print("=" * 50)
    
    # Carregar variáveis de ambiente
    carregar_env()
    
    # Detectar ambiente
    ambiente = _detectar_ambiente()
    print(f"🌍 Ambiente detectado: {ambiente}")
    
    if ambiente == 'supabase':
        config = _config_supabase()
        print(f"🗄️  Configuração Supabase: {config['host']}")
        
        if _testar_conexao(config):
            print("✅ CONEXÃO SUPABASE OK!")
            
            # Testar tabela
            try:
                conn = psycopg2.connect(**config)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM dashboard_baker")
                count = cursor.fetchone()[0]
                print(f"📊 Registros na tabela: {count}")
                cursor.close()
                conn.close()
                print("✅ TABELA OK!")
            except Exception as e:
                print(f"❌ Problema na tabela: {e}")
        else:
            print("❌ FALHA NA CONEXÃO SUPABASE")
    
    elif ambiente == 'local':
        config = _config_local()
        print(f"🗄️  Configuração Local: {config['host']}")
        
        if _testar_conexao(config):
            print("✅ CONEXÃO LOCAL OK!")
        else:
            print("❌ FALHA NA CONEXÃO LOCAL")
    
    print("\n🎯 RESULTADO DO TESTE:")
    if ambiente == 'supabase':
        print("   • Configuração Supabase carregada")
        print("   • Use este ambiente para deploy")
    else:
        print("   • Verificar configuração .env")
        print("   • Configurar Supabase para deploy")

if __name__ == "__main__":
    main()
