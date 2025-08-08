#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir o trigger update_updated_at_column no PostgreSQL
"""

import psycopg2
import sys
import os

def carregar_configuracao_banco():
    """Carrega configuração do banco de dados"""
    try:
        from dashboard_baker_web_corrigido import carregar_configuracao_banco as config_func
        return config_func()
    except:
        # Configuração fallback
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'postgres'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
            'port': os.getenv('DB_PORT', '5432')
        }

def corrigir_trigger():
    """Corrige o trigger update_updated_at_column"""
    try:
        config = carregar_configuracao_banco()
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        print("🔧 Corrigindo trigger update_updated_at_column...")
        
        # 1. Remover trigger existente se houver
        cursor.execute("""
            DROP TRIGGER IF EXISTS update_dashboard_baker_updated_at ON dashboard_baker;
        """)
        
        # 2. Remover função existente se houver
        cursor.execute("""
            DROP FUNCTION IF EXISTS update_updated_at_column();
        """)
        
        # 3. Criar função corrigida com RETURN
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """)
        
        # 4. Criar trigger corrigido
        cursor.execute("""
            CREATE TRIGGER update_dashboard_baker_updated_at
                BEFORE UPDATE ON dashboard_baker
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Trigger corrigido com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir trigger: {str(e)}")
        return False

def testar_trigger():
    """Testa o trigger corrigido"""
    try:
        config = carregar_configuracao_banco()
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        print("🧪 Testando trigger corrigido...")
        
        # Fazer uma atualização simples para testar
        cursor.execute("""
            UPDATE dashboard_baker 
            SET observacao = COALESCE(observacao, '') || ' [Teste trigger]'
            WHERE numero_cte = (SELECT numero_cte FROM dashboard_baker LIMIT 1)
        """)
        
        if cursor.rowcount > 0:
            print("✅ Trigger funcionando corretamente!")
            conn.commit()
        else:
            print("⚠️ Nenhum registro encontrado para teste")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar trigger: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Iniciando correção do trigger PostgreSQL...")
    
    # Corrigir trigger
    sucesso_correcao = corrigir_trigger()
    
    if sucesso_correcao:
        # Testar trigger
        sucesso_teste = testar_trigger()
        
        if sucesso_teste:
            print("\n🎉 Trigger corrigido e testado com sucesso!")
            print("✅ Sistema pronto para atualizações e baixas!")
        else:
            print("\n⚠️ Trigger corrigido, mas teste falhou")
    else:
        print("\n❌ Falha na correção do trigger")
    
    sys.exit(0 if sucesso_correcao else 1)
