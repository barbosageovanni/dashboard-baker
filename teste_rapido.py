#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Rápido de Conexão - Dashboard Baker
Execute este script para verificar rapidamente o status do sistema
"""

import os
import sys
from datetime import datetime

print("""
╔══════════════════════════════════════════════════════════════╗
║          TESTE RÁPIDO - DASHBOARD BAKER v3.0                ║
╚══════════════════════════════════════════════════════════════╝
""")

# 1. Verificar Python
print("1️⃣ Verificando Python...")
print(f"   ✅ Python {sys.version.split()[0]}")

# 2. Verificar bibliotecas
print("\n2️⃣ Verificando bibliotecas...")
bibliotecas = {
    'pandas': 'Manipulação de dados',
    'psycopg2': 'Conexão PostgreSQL',
    'streamlit': 'Interface web',
    'plotly': 'Gráficos',
    'xlsxwriter': 'Exportação Excel'
}

faltando = []
for lib, descricao in bibliotecas.items():
    try:
        __import__(lib)
        print(f"   ✅ {lib}: {descricao}")
    except ImportError:
        print(f"   ❌ {lib}: {descricao} - NÃO INSTALADO")
        faltando.append(lib)

if faltando:
    print(f"\n⚠️ Instale as bibliotecas faltando:")
    print(f"   pip install {' '.join(faltando)}")

# 3. Verificar arquivo .env
print("\n3️⃣ Verificando configuração...")
if os.path.exists('.env'):
    print("   ✅ Arquivo .env encontrado")
    
    # Verificar variáveis
    from dotenv import load_dotenv
    load_dotenv()
    
    variaveis = ['SUPABASE_HOST', 'SUPABASE_PASSWORD']
    config_ok = True
    
    for var in variaveis:
        if os.getenv(var):
            if 'PASSWORD' in var:
                print(f"   ✅ {var}: ********")
            else:
                print(f"   ✅ {var}: {os.getenv(var)[:20]}...")
        else:
            print(f"   ❌ {var}: NÃO CONFIGURADA")
            config_ok = False
else:
    print("   ❌ Arquivo .env NÃO encontrado")
    config_ok = False

# 4. Testar conexão se configurado
if config_ok and 'psycopg2' not in faltando:
    print("\n4️⃣ Testando conexão com Supabase...")
    
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host=os.getenv('SUPABASE_HOST'),
            database=os.getenv('SUPABASE_DB', 'postgres'),
            user=os.getenv('SUPABASE_USER', 'postgres'),
            password=os.getenv('SUPABASE_PASSWORD'),
            port=int(os.getenv('SUPABASE_PORT', '5432')),
            sslmode='require',
            connect_timeout=5
        )
        
        cursor = conn.cursor()
        
        # Verificar tabela
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'dashboard_baker'
            );
        """)
        
        tabela_existe = cursor.fetchone()[0]
        
        if tabela_existe:
            cursor.execute("SELECT COUNT(*) FROM dashboard_baker;")
            count = cursor.fetchone()[0]
            print(f"   ✅ Conectado ao Supabase")
            print(f"   ✅ Tabela dashboard_baker: {count} registros")
            
            # Estatísticas rápidas
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN data_baixa IS NOT NULL THEN 1 END) as com_baixa,
                    COUNT(CASE WHEN numero_fatura IS NOT NULL THEN 1 END) as com_fatura,
                    COALESCE(SUM(valor_total), 0) as valor_total
                FROM dashboard_baker;
            """)
            
            com_baixa, com_fatura, valor_total = cursor.fetchone()
            
            print(f"\n   📊 Estatísticas:")
            print(f"      • Faturas pagas: {com_baixa}")
            print(f"      • Com número fatura: {com_fatura}")
            print(f"      • Valor total: R$ {valor_total:,.2f}")
        else:
            print(f"   ⚠️ Conectado, mas tabela não existe")
            print(f"   💡 Execute: python diagnostico_conexao_supabase.py")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Erro de conexão: {str(e)[:100]}...")
        print(f"\n   💡 Execute: python diagnostico_conexao_supabase.py")

# 5. Status final
print("\n" + "="*60)
print("📋 RESUMO DO STATUS")
print("="*60)

if not faltando and config_ok:
    print("✅ Sistema pronto para uso!")
    print("\n🚀 Para iniciar o dashboard:")
    print("   streamlit run dashboard_baker_web_corrigido.py")
else:
    print("⚠️ Sistema precisa de configuração")
    print("\n🔧 Para corrigir:")
    print("   1. Execute: executar_diagnostico.bat")
    print("   2. Ou: python diagnostico_conexao_supabase.py")

print("\n" + "="*60)
print(f"Teste executado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("="*60)