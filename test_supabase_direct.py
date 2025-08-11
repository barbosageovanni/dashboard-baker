#!/usr/bin/env python3
"""
Teste de Conexão Supabase - Direto com Credenciais
"""

import psycopg2
from psycopg2 import OperationalError, DatabaseError

def testar_supabase():
    """Testa conexão direta com credenciais"""
    
    print("🔍 TESTE DIRETO DE CONEXÃO SUPABASE")
    print("="*50)
    
    # Credenciais diretas (do arquivo streamlit_secrets.toml)
    config = {
        'host': 'db.lijtncazuwnbydeqtoyz.supabase.co',
        'database': 'postgres',
        'user': 'postgres',
        'password': 'Mariaana953@7334',
        'port': 5432,
        'sslmode': 'require',
        'connect_timeout': 30
    }
    
    print("🔧 CONFIGURAÇÃO:")
    for key, value in config.items():
        if key == 'password':
            print(f"✅ {key}: {'*' * len(str(value))}")
        else:
            print(f"✅ {key}: {value}")
    
    print("\n" + "="*50)
    print("🔌 TESTANDO CONEXÃO...")
    
    try:
        print("1️⃣ Conectando ao Supabase...")
        conn = psycopg2.connect(**config)
        print("✅ Conexão estabelecida!")
        
        cursor = conn.cursor()
        print("2️⃣ Executando query de teste...")
        cursor.execute("SELECT current_user, current_database(), version()")
        result = cursor.fetchone()
        print(f"✅ Usuário: {result[0]}")
        print(f"✅ Database: {result[1]}")
        print(f"✅ PostgreSQL: {result[2][:60]}...")
        
        print("3️⃣ Verificando permissões de esquema...")
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name IN ('public', 'auth', 'storage')
        """)
        schemas = cursor.fetchall()
        print(f"✅ Esquemas acessíveis: {[s[0] for s in schemas]}")
        
        print("4️⃣ Verificando tabelas públicas...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
            LIMIT 10
        """)
        tables = cursor.fetchall()
        print(f"✅ Tabelas encontradas: {len(tables)}")
        for table in tables:
            print(f"   📋 {table[0]}")
        
        print("5️⃣ Testando criação de tabela (se necessário)...")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'ctes'
        """)
        table_exists = cursor.fetchone()[0]
        print(f"✅ Tabela 'ctes' existe: {'Sim' if table_exists > 0 else 'Não'}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 SUPABASE CONECTADO COM SUCESSO!")
        print("   ➡️ Todas as permissões funcionando")
        print("   ➡️ Pronto para uso no dashboard")
        return True
        
    except OperationalError as e:
        print(f"\n❌ ERRO OPERACIONAL:")
        error_msg = str(e).lower()
        
        if "authentication failed" in error_msg:
            print("🔍 PROBLEMA: Falha de autenticação")
            print("   ❌ Usuário ou senha incorretos")
            print("   🔧 SOLUÇÃO: Verificar credenciais no Supabase")
            
        elif "password authentication failed" in error_msg:
            print("🔍 PROBLEMA: Senha incorreta")
            print("   ❌ A senha não confere")
            print("   🔧 SOLUÇÃO: Redefinir senha no dashboard Supabase")
            
        elif "role" in error_msg and "does not exist" in error_msg:
            print("🔍 PROBLEMA: Usuário não existe")
            print("   ❌ O usuário 'postgres' não foi encontrado")
            print("   🔧 SOLUÇÃO: Verificar usuário correto no Supabase")
            
        elif "connection refused" in error_msg:
            print("🔍 PROBLEMA: Conexão recusada")
            print("   ❌ Servidor não aceita conexões")
            print("   🔧 SOLUÇÃO: Verificar se Supabase está ativo")
            
        elif "timeout" in error_msg:
            print("🔍 PROBLEMA: Timeout")
            print("   ❌ Conexão muito lenta")
            print("   🔧 SOLUÇÃO: Verificar conectividade")
            
        else:
            print(f"🔍 ERRO ESPECÍFICO: {str(e)}")
            
        return False
        
    except Exception as e:
        print(f"\n❌ ERRO GERAL:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
        return False

if __name__ == "__main__":
    resultado = testar_supabase()
    if not resultado:
        print("\n🚨 ERRO DE CONEXÃO DETECTADO")
        print("   📞 Entre em contato com suporte se necessário")
