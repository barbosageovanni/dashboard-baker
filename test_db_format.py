#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Compatibilidade - Formatos DB_ e SUPABASE_
"""

import os

# Simular variáveis DB_ (formato Streamlit Cloud)
os.environ['DB_HOST'] = 'db.lijtncazuwnbydeqtoyz.supabase.co'
os.environ['DB_DATABASE'] = 'postgres'
os.environ['DB_USER'] = 'postgres'
os.environ['DB_PASSWORD'] = 'Mariaana953@7334'
os.environ['DB_PORT'] = '5432'
os.environ['DATABASE_ENVIRONMENT'] = 'supabase'

def _detectar_ambiente():
    """Detecta ambiente atual"""
    if os.getenv('PGHOST') and os.getenv('PGDATABASE'):
        return 'railway'
    elif os.getenv('DATABASE_URL'):
        return 'render'
    elif (os.getenv('SUPABASE_HOST') and os.getenv('SUPABASE_PASSWORD')) or (os.getenv('DB_HOST') and os.getenv('DB_PASSWORD')):
        return 'supabase'
    else:
        return 'local'

def _config_supabase():
    """Configuração Supabase PostgreSQL - Compatível com múltiplos formatos"""
    return {
        'host': os.getenv('SUPABASE_HOST') or os.getenv('DB_HOST'),
        'database': os.getenv('SUPABASE_DB') or os.getenv('DB_DATABASE', 'postgres'),
        'user': os.getenv('SUPABASE_USER') or os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('SUPABASE_PASSWORD') or os.getenv('DB_PASSWORD'),
        'port': int(os.getenv('SUPABASE_PORT') or os.getenv('DB_PORT', '5432')),
        'sslmode': 'require',
        'connect_timeout': 10
    }

def main():
    print("🧪 TESTE DE COMPATIBILIDADE - FORMATOS DB_")
    print("=" * 50)
    
    # Testar detecção de ambiente
    ambiente = _detectar_ambiente()
    print(f"🌍 Ambiente detectado: {ambiente}")
    
    # Testar configuração
    if ambiente == 'supabase':
        config = _config_supabase()
        print(f"🗄️  Configuração gerada:")
        for key, value in config.items():
            if key == 'password':
                print(f"   {key}: ***{value[-4:] if value else 'None'}")
            else:
                print(f"   {key}: {value}")
        
        # Verificar se todos os campos estão preenchidos
        campos_obrigatorios = ['host', 'database', 'user', 'password', 'port']
        campos_ok = all(config.get(campo) for campo in campos_obrigatorios)
        
        if campos_ok:
            print("✅ CONFIGURAÇÃO VÁLIDA - Todos os campos preenchidos")
        else:
            print("❌ CONFIGURAÇÃO INVÁLIDA - Campos em falta")
            for campo in campos_obrigatorios:
                if not config.get(campo):
                    print(f"   ❌ {campo}: não encontrado")
    
    print("\n🎯 VARIÁVEIS TESTADAS:")
    print("   DB_HOST =", os.getenv('DB_HOST'))
    print("   DB_DATABASE =", os.getenv('DB_DATABASE'))
    print("   DB_USER =", os.getenv('DB_USER'))
    print("   DB_PASSWORD = ***" + (os.getenv('DB_PASSWORD', '')[-4:] if os.getenv('DB_PASSWORD') else ''))
    print("   DB_PORT =", os.getenv('DB_PORT'))

if __name__ == "__main__":
    main()
