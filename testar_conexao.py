#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE RÁPIDO DE CONEXÃO POSTGRESQL - DASHBOARD TRANSPONTUAL
"""

import psycopg2
import os

def testar_conexao():
    """Testa conexão com PostgreSQL Railway"""
    
    print("🧪 TESTANDO CONEXÃO POSTGRESQL RAILWAY")
    print("=" * 45)
    
    # Configuração Railway (usando URL pública)
    config = {
        'host': 'maglev.proxy.rlwy.net',
        'database': 'railway',
        'user': 'postgres', 
        'password': 'tioWAuMkDhjxvJMjqGnXbttoQvwsiVsz',
        'port': 18783,
        'sslmode': 'require'
    }
    
    try:
        print("🔌 Tentando conectar...")
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        print("✅ Conexão estabelecida!")
        
        # Testar consulta
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"📊 PostgreSQL: {version[0][:60]}...")
        
        # Verificar se tabela dashboard_baker existe
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_name = 'dashboard_baker'
        """)
        
        if cursor.fetchone():
            print("✅ Tabela 'dashboard_baker' já existe")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM dashboard_baker")
            count = cursor.fetchone()[0]
            print(f"📊 Registros na tabela: {count}")
            
        else:
            print("⚠️ Tabela 'dashboard_baker' não existe (será criada)")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 CONEXÃO OK! Sistema pronto!")
        return True
        
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

if __name__ == "__main__":
    testar_conexao()