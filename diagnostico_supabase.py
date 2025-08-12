#!/usr/bin/env python3
"""
Script de Diagnóstico - Conexão Supabase
Identifica problemas específicos de conexão
"""

import os
import psycopg2
from psycopg2 import OperationalError, DatabaseError

def testar_conexao_detalhada():
    """Testa conexão com detalhes completos de erro"""
    
    print("🔍 DIAGNÓSTICO DE CONEXÃO SUPABASE")
    print("="*50)
    
    # Configurações esperadas
    configs = {
        'DB_HOST': os.getenv('DB_HOST'),
        'DB_DATABASE': os.getenv('DB_DATABASE'), 
        'DB_USER': os.getenv('DB_USER'),
        'DB_PASSWORD': os.getenv('DB_PASSWORD'),
        'DB_PORT': os.getenv('DB_PORT'),
        'SUPABASE_HOST': os.getenv('SUPABASE_HOST'),
        'SUPABASE_DB': os.getenv('SUPABASE_DB'),
        'SUPABASE_USER': os.getenv('SUPABASE_USER'),
        'SUPABASE_PASSWORD': os.getenv('SUPABASE_PASSWORD'),
        'SUPABASE_PORT': os.getenv('SUPABASE_PORT'),
        'DATABASE_ENVIRONMENT': os.getenv('DATABASE_ENVIRONMENT')
    }
    
    print("📋 VARIÁVEIS DE AMBIENTE:")
    for key, value in configs.items():
        if value:
            if 'PASSWORD' in key:
                print(f"✅ {key}: {'*' * len(value)}")
            else:
                print(f"✅ {key}: {value}")
        else:
            print(f"❌ {key}: NÃO DEFINIDA")
    
    print("\n" + "="*50)
    
    # Configuração de conexão
    config = {
        'host': configs['SUPABASE_HOST'] or configs['DB_HOST'],
        'database': configs['SUPABASE_DB'] or configs['DB_DATABASE'],
        'user': configs['SUPABASE_USER'] or configs['DB_USER'], 
        'password': configs['SUPABASE_PASSWORD'] or configs['DB_PASSWORD'],
        'port': int(configs['SUPABASE_PORT'] or configs['DB_PORT'] or '5432'),
        'sslmode': 'require',
        'connect_timeout': 30
    }
    
    print("🔧 CONFIGURAÇÃO DE CONEXÃO:")
    for key, value in config.items():
        if key == 'password':
            print(f"✅ {key}: {'*' * len(str(value))}")
        else:
            print(f"✅ {key}: {value}")
    
    print("\n" + "="*50)
    print("🔌 TESTANDO CONEXÃO...")
    
    try:
        # Teste de conexão detalhado
        print("1️⃣ Tentando conectar...")
        conn = psycopg2.connect(**config)
        print("✅ Conexão estabelecida!")
        
        print("2️⃣ Testando cursor...")
        cursor = conn.cursor()
        print("✅ Cursor criado!")
        
        print("3️⃣ Executando query de teste...")
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        print(f"✅ Query executada! Resultado: {result}")
        
        print("4️⃣ Verificando permissões...")
        cursor.execute("SELECT current_user, current_database(), version()")
        user_info = cursor.fetchone()
        print(f"✅ Usuário: {user_info[0]}")
        print(f"✅ Database: {user_info[1]}")
        print(f"✅ Versão PostgreSQL: {user_info[2][:50]}...")
        
        print("5️⃣ Testando acesso a tabelas...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            LIMIT 5
        """)
        tables = cursor.fetchall()
        print(f"✅ Tabelas encontradas: {len(tables)}")
        for table in tables[:3]:
            print(f"   📋 {table[0]}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 CONEXÃO TOTALMENTE FUNCIONAL!")
        return True
        
    except OperationalError as e:
        print(f"\n❌ ERRO OPERACIONAL:")
        print(f"   Código: {e.pgcode}")
        print(f"   Mensagem: {e.pgerror}")
        print(f"   Detalhes: {str(e)}")
        
        if "authentication failed" in str(e).lower():
            print("\n🔍 DIAGNÓSTICO: Problema de autenticação")
            print("   ➡️ Verifique usuário e senha")
            print("   ➡️ Confirme se o usuário tem acesso ao banco")
        elif "connection refused" in str(e).lower():
            print("\n🔍 DIAGNÓSTICO: Conexão recusada")
            print("   ➡️ Verifique host e porta")
            print("   ➡️ Confirme se o servidor está online")
        elif "timeout" in str(e).lower():
            print("\n🔍 DIAGNÓSTICO: Timeout de conexão")
            print("   ➡️ Problema de rede ou firewall")
        
        return False
        
    except DatabaseError as e:
        print(f"\n❌ ERRO DE BANCO:")
        print(f"   Código: {e.pgcode}")
        print(f"   Mensagem: {e.pgerror}")
        print(f"   Detalhes: {str(e)}")
        return False
        
    except Exception as e:
        print(f"\n❌ ERRO GERAL:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
        return False

if __name__ == "__main__":
    testar_conexao_detalhada()
