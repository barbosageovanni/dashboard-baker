# Configuração de fallback - PostgreSQL Local
# Use este arquivo se Supabase não funcionar

import os

def get_database_config():
    """Retorna configuração do banco local"""
    
    # Primeiro, tenta Supabase se credenciais disponíveis
    supabase_password = os.getenv('SUPABASE_PASSWORD')
    
    if supabase_password:
        supabase_config = {
            'host': 'db.lijtncazuwnbydeqtoyz.supabase.co',
            'database': 'postgres',
            'user': 'postgres',
            'password': supabase_password,
            'port': 5432,
            'sslmode': 'require',
            'connect_timeout': 10
        }
        
        # Testar conexão Supabase
        try:
            import psycopg2
            conn = psycopg2.connect(**supabase_config)
            conn.close()
            print("✅ Usando Supabase PostgreSQL")
            return supabase_config
        except:
            print("⚠️ Supabase falhou, usando PostgreSQL local")
    
    # Fallback para PostgreSQL local
    local_config = {
        'host': 'localhost',
        'database': 'dashboard_baker',
        'user': 'postgres',
        'password': 'senha123',
        'port': 5432
    }
    
    print("✅ Usando PostgreSQL local")
    return local_config
