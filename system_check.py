#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Verificação Completa - Dashboard Baker v3.0
Testa todas as funcionalidades antes do deploy
"""

import sys
import os
import importlib
from datetime import datetime

def print_header(title):
    """Imprime cabeçalho formatado"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_imports():
    """Testa importação de bibliotecas essenciais"""
    print_header("🔍 TESTE DE IMPORTAÇÕES")
    
    required_packages = [
        'streamlit',
        'pandas', 
        'plotly',
        'psycopg2',
        'numpy',
        'datetime'
    ]
    
    success = True
    for package in required_packages:
        try:
            if package == 'psycopg2':
                import psycopg2
            else:
                importlib.import_module(package)
            print(f"✅ {package}: OK")
        except ImportError as e:
            print(f"❌ {package}: FALHOU - {e}")
            success = False
    
    return success

def test_file_structure():
    """Verifica estrutura de arquivos"""
    print_header("📁 ESTRUTURA DE ARQUIVOS")
    
    required_files = [
        'dashboard_baker_web_corrigido.py',
        'requirements.txt'
    ]
    
    success = True
    for file in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file) / 1024
            print(f"✅ {file}: {size:.1f} KB")
        else:
            print(f"❌ {file}: AUSENTE")
            success = False
    
    return success

def test_database_connection():
    """Testa conexão com PostgreSQL/Supabase"""
    print_header("🐘 TESTE DE CONEXÃO POSTGRESQL")
    
    try:
        import psycopg2
        
        # Configurações de teste (usar variáveis de ambiente)
        config = {
            'host': os.getenv('PGHOST', 'localhost'),
            'database': os.getenv('PGDATABASE', 'postgres'),
            'user': os.getenv('PGUSER', 'postgres'),
            'password': os.getenv('PGPASSWORD', ''),
            'port': int(os.getenv('PGPORT', '5432')),
            'connect_timeout': 10
        }
        
        print(f"🔍 Testando conexão: {config['host']}:{config['port']}")
        
        # Tentar conectar
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Testar tabela dashboard_baker
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_name = 'dashboard_baker'
        """)
        
        if cursor.fetchone():
            print("✅ Tabela 'dashboard_baker' encontrada")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM dashboard_baker")
            count = cursor.fetchone()[0]
            print(f"📊 Registros na tabela: {count:,}")
            
            cursor.close()
            conn.close()
            return True
        else:
            print("❌ Tabela 'dashboard_baker' não encontrada")
            cursor.close()
            conn.close()
            return False
            
    except psycopg2.OperationalError as e:
        print(f"❌ Erro de conexão: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        return False

def test_streamlit_config():
    """Verifica configurações do Streamlit"""
    print_header("🌐 CONFIGURAÇÃO STREAMLIT")
    
    # Verificar se está rodando no Streamlit Cloud
    if 'STREAMLIT' in os.environ:
        print("✅ Ambiente Streamlit detectado")
    else:
        print("⚠️ Rodando localmente")
    
    # Verificar secrets
    secrets_file = ".streamlit/secrets.toml"
    if os.path.exists(secrets_file):
        print("✅ Arquivo secrets.toml encontrado")
    else:
        print("⚠️ Arquivo secrets.toml não encontrado")
    
    return True

def generate_test_report():
    """Gera relatório completo de testes"""
    print_header("📋 RELATÓRIO DE VERIFICAÇÃO")
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"🕐 Data/Hora: {timestamp}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"💻 Sistema: {os.name}")
    
    # Executar todos os testes
    tests = [
        ("Importações", test_imports),
        ("Arquivos", test_file_structure), 
        ("PostgreSQL", test_database_connection),
        ("Streamlit", test_streamlit_config)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results[test_name] = False
    
    # Resumo final
    print_header("🎯 RESUMO FINAL")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
    
    print(f"\n📊 Total: {passed_tests}/{total_tests} testes passaram")
    
    if passed_tests == total_tests:
        print("\n🎉 SISTEMA PRONTO PARA DEPLOY!")
        return True
    else:
        print(f"\n⚠️ {total_tests - passed_tests} problemas encontrados")
        return False

def main():
    """Função principal"""
    print("🚀 Dashboard Baker v3.0 - Verificação de Sistema")
    print("=" * 60)
    
    system_ready = generate_test_report()
    
    if system_ready:
        print("\n✅ Todos os testes passaram!")
        print("🌐 Pronto para: https://dashboard-transpontual.streamlit.app/")
    else:
        print("\n❌ Corrija os problemas antes do deploy")
    
    return 0 if system_ready else 1

if __name__ == "__main__":
    sys.exit(main())