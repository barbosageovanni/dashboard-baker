#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONFIGURADOR SUPABASE DASHBOARD BAKER
Configura variáveis de ambiente para Supabase PostgreSQL
"""

import os
import psycopg2
from datetime import datetime

def configurar_supabase_environment():
    """Configura variáveis de ambiente para Supabase"""
    print("🌟 CONFIGURANDO SUPABASE PARA DASHBOARD BAKER")
    print("=" * 50)
    
    # Credenciais padrão baseadas na configuração do usuário
    supabase_config = {
        'SUPABASE_HOST': 'db.lijtncazuwnbydeqtoyz.supabase.co',
        'SUPABASE_DB': 'postgres',
        'SUPABASE_USER': 'postgres',
        'SUPABASE_PORT': '5432'
    }
    
    print("📋 CREDENCIAIS SUPABASE DETECTADAS:")
    for key, value in supabase_config.items():
        print(f"   {key}: {value}")
    
    # Solicitar senha
    print("\n🔑 DIGITE A SENHA DO BANCO SUPABASE:")
    senha = input("Password: ").strip()
    
    if not senha:
        print("❌ Senha é obrigatória!")
        return False
    
    supabase_config['SUPABASE_PASSWORD'] = senha
    
    # Testar conexão
    print("\n🔌 TESTANDO CONEXÃO...")
    
    try:
        test_config = {
            'host': supabase_config['SUPABASE_HOST'],
            'database': supabase_config['SUPABASE_DB'],
            'user': supabase_config['SUPABASE_USER'],
            'password': supabase_config['SUPABASE_PASSWORD'],
            'port': int(supabase_config['SUPABASE_PORT']),
            'sslmode': 'require',
            'connect_timeout': 15
        }
        
        conn = psycopg2.connect(**test_config)
        cursor = conn.cursor()
        
        # Verificar tabela
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name = 'dashboard_baker'
        """)
        table_exists = cursor.fetchone()[0] > 0
        
        if table_exists:
            cursor.execute("SELECT COUNT(*) FROM dashboard_baker")
            total_registros = cursor.fetchone()[0]
            print(f"✅ Conexão OK! Encontrados {total_registros} registros na tabela")
        else:
            print("⚠️  Conexão OK, mas tabela 'dashboard_baker' não encontrada")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False
    
    # Definir variáveis de ambiente
    print("\n🔧 CONFIGURANDO VARIÁVEIS DE AMBIENTE...")
    
    for key, value in supabase_config.items():
        os.environ[key] = value
        print(f"✅ {key} configurado")
    
    # Criar arquivo .env para persistência
    env_content = f"""# CONFIGURAÇÃO SUPABASE - DASHBOARD BAKER
# Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

SUPABASE_HOST={supabase_config['SUPABASE_HOST']}
SUPABASE_DB={supabase_config['SUPABASE_DB']}
SUPABASE_USER={supabase_config['SUPABASE_USER']}
SUPABASE_PASSWORD={supabase_config['SUPABASE_PASSWORD']}
SUPABASE_PORT={supabase_config['SUPABASE_PORT']}

# Para forçar uso do Supabase
DATABASE_ENVIRONMENT=supabase
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ Arquivo .env criado com credenciais")
    except Exception as e:
        print(f"⚠️  Não foi possível criar .env: {e}")
    
    print("\n🎉 CONFIGURAÇÃO SUPABASE CONCLUÍDA!")
    print("✅ Dashboard Baker agora está configurado para usar Supabase")
    print("✅ Execute: streamlit run dashboard_baker_web_corrigido.py")
    
    return True

def verificar_configuracao_atual():
    """Verifica se já existe configuração do Supabase"""
    print("🔍 VERIFICANDO CONFIGURAÇÃO ATUAL...")
    
    vars_necessarias = ['SUPABASE_HOST', 'SUPABASE_PASSWORD']
    configurado = all(os.getenv(var) for var in vars_necessarias)
    
    if configurado:
        print("✅ Configuração Supabase já existe")
        for var in ['SUPABASE_HOST', 'SUPABASE_DB', 'SUPABASE_USER', 'SUPABASE_PORT']:
            valor = os.getenv(var, 'não definido')
            if var == 'SUPABASE_PASSWORD':
                valor = '*' * len(os.getenv(var, ''))
            print(f"   {var}: {valor}")
        return True
    else:
        print("❌ Configuração Supabase não encontrada")
        return False

if __name__ == "__main__":
    print("🚀 CONFIGURADOR SUPABASE DASHBOARD BAKER")
    print("=" * 50)
    
    if not verificar_configuracao_atual():
        if configurar_supabase_environment():
            print("\n✅ Configuração concluída com sucesso!")
        else:
            print("\n❌ Falha na configuração")
    else:
        resposta = input("\n🔄 Reconfigurar? (s/n): ").lower()
        if resposta == 's':
            configurar_supabase_environment()
        else:
            print("✅ Mantendo configuração atual")
    
    input("\n📱 Pressione Enter para continuar...")
