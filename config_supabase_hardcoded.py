#!/usr/bin/env python3
"""
Configuração HARDCODED para Supabase - EMERGÊNCIA
Use este arquivo caso os secrets não funcionem
"""

def get_supabase_config():
    """Retorna configuração hardcoded do Supabase"""
    return {
        'host': 'db.lijtncazuwnbydeqtoyz.supabase.co',
        'database': 'postgres',
        'user': 'postgres',
        'password': 'Mariaana953@7334',
        'port': 5432,
        'sslmode': 'require',
        'connect_timeout': 30
    }

# Configuração para importação
SUPABASE_CONFIG = get_supabase_config()
