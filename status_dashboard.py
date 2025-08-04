#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Status Rápido - Dashboard Baker PostgreSQL
Verificação rápida do status do sistema (30 segundos)
"""

import os
import sys
import psycopg2
from datetime import datetime

def verificar_status():
    """Verificação rápida do status do sistema"""
    
    print("⚡ STATUS RÁPIDO - DASHBOARD BAKER")
    print("=" * 40)
    print(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    status_geral = True
    problemas = []
    
    # 1. Verificar arquivos principais
    print("📁 ARQUIVOS DO SISTEMA:")
    arquivos_principais = [
        'dashboard_baker_web_corrigido.py',
        'popular_banco_postgresql.py',
        '.env'
    ]
    
    for arquivo in arquivos_principais:
        if os.path.exists(arquivo):
            print(f"   ✅ {arquivo}")
        else:
            print(f"   ❌ {arquivo}")
            problemas.append(f"Arquivo {arquivo} não encontrado")
            status_geral = False
    
    # 2. Verificar dependências básicas
    print("\n📦 DEPENDÊNCIAS:")
    dependencias = ['streamlit', 'pandas', 'plotly', 'psycopg2']
    
    for dep in dependencias:
        try:
            if dep == 'psycopg2':
                import psycopg2
            else:
                __import__(dep)
            print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep}")
            problemas.append(f"Biblioteca {dep} não instalada")
            status_geral = False
    
    # 3. Verificar PostgreSQL
    print("\n🐘 POSTGRESQL:")
    
    # Carregar configuração do .env
    db_config = {
        'host': 'localhost',
        'database': 'dashboard_baker',
        'user': 'postgres',
        'password': 'senha123',
        'port': 5432
    }
    
    if os.path.exists('.env'):
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                for linha in f:
                    linha = linha.strip()
                    if linha and not linha.startswith('#') and '=' in linha:
                        chave, valor = linha.split('=', 1)
                        if chave == 'DB_HOST':
                            db_config['host'] = valor
                        elif chave == 'DB_PASSWORD':
                            db_config['password'] = valor
                        elif chave == 'DB_USER':
                            db_config['user'] = valor
                        elif chave == 'DB_PORT':
                            db_config['port'] = int(valor)
        except:
            pass
    
    try:
        conn = psycopg2.connect(**db_config)
        print(f"   ✅ Conexão: {db_config['host']}:{db_config['port']}")
        
        cursor = conn.cursor()
        
        # Verificar tabela
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_name = 'dashboard_baker'
        """)
        
        if cursor.fetchone():
            print("   ✅ Tabela: dashboard_baker")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM dashboard_baker")
            count = cursor.fetchone()[0]
            print(f"   📊 Registros: {count:,}")
            
            if count == 0:
                problemas.append("Tabela vazia - use popular_banco_postgresql.py")
            
        else:
            print("   ❌ Tabela: dashboard_baker não existe")
            problemas.append("Tabela dashboard_baker não encontrada")
            status_geral = False
        
        cursor.close()
        conn.close()
        
    except psycopg2.OperationalError as e:
        print(f"   ❌ Conexão falhou: {str(e)[:50]}...")
        problemas.append("Não foi possível conectar ao PostgreSQL")
        status_geral = False
    except Exception as e:
        print(f"   ❌ Erro: {str(e)[:50]}...")
        problemas.append(f"Erro PostgreSQL: {str(e)[:50]}")
        status_geral = False
    
    # 4. Status final
    print("\n" + "=" * 40)
    
    if status_geral and len(problemas) == 0:
        print("🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!")
        print("🚀 Pode executar: streamlit run dashboard_baker_web_corrigido.py")
        print("🌐 Acesse em: http://localhost:8501")
        return 0
    
    elif len(problemas) <= 2:
        print("⚠️ SISTEMA COM PEQUENOS PROBLEMAS")
        print("💡 Sistema pode funcionar, mas com limitações")
        
        print("\n🔧 PROBLEMAS ENCONTRADOS:")
        for problema in problemas:
            print(f"   • {problema}")
        
        print("\n💡 SOLUÇÕES RÁPIDAS:")
        if "popular_banco_postgresql.py" in str(problemas):
            print("   1. Execute: python popular_banco_postgresql.py")
        if "PostgreSQL" in str(problemas):
            print("   2. Verifique se PostgreSQL está rodando")
            print("   3. Confira senha no arquivo .env")
        if "Biblioteca" in str(problemas):
            print("   4. Execute: pip install -r requirements_postgresql.txt")
        
        return 1
    
    else:
        print("❌ SISTEMA COM PROBLEMAS SÉRIOS")
        print("🔧 Execute setup completo antes de usar")
        
        print("\n🚨 PROBLEMAS CRÍTICOS:")
        for problema in problemas:
            print(f"   • {problema}")
        
        print("\n🔧 SOLUÇÕES:")
        print("   1. Execute: setup_dashboard_postgresql.bat")
        print("   2. Ou: python setup_dashboard_postgresql.py")
        print("   3. Para testes completos: python teste_sistema_completo.py")
        
        return 2

def mostrar_comandos_uteis():
    """Mostra comandos úteis do sistema"""
    print("\n📋 COMANDOS ÚTEIS:")
    print("-" * 20)
    print("🚀 Iniciar dashboard:")
    print("   streamlit run dashboard_baker_web_corrigido.py")
    print()
    print("📥 Popular banco com CSV:")
    print("   python popular_banco_postgresql.py")
    print()
    print("🧪 Testes completos:")
    print("   python teste_sistema_completo.py")
    print()
    print("⚙️ Setup completo:")
    print("   python setup_dashboard_postgresql.py")
    print()
    print("📊 Status detalhado:")
    print("   python status_dashboard.py --detalhado")

def status_detalhado():
    """Status mais detalhado do sistema"""
    print("🔍 STATUS DETALHADO - DASHBOARD BAKER")
    print("=" * 45)
    
    # Informações do sistema
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"💻 Sistema: {os.name}")
    print(f"📁 Diretório: {os.getcwd()}")
    print()
    
    # Tamanho dos arquivos
    print("📊 TAMANHO DOS ARQUIVOS:")
    arquivos_verificar = [
        'dashboard_baker_web_corrigido.py',
        'popular_banco_postgresql.py',
        'setup_dashboard_postgresql.py',
        'teste_sistema_completo.py'
    ]
    
    for arquivo in arquivos_verificar:
        if os.path.exists(arquivo):
            tamanho = os.path.getsize(arquivo)
            tamanho_kb = tamanho / 1024
            print(f"   📄 {arquivo}: {tamanho_kb:.1f} KB")
        else:
            print(f"   ❌ {arquivo}: Não encontrado")
    
    print()
    
    # Verificar portas em uso
    print("🌐 VERIFICAÇÃO DE PORTAS:")
    try:
        import socket
        
        portas_testar = [8501, 8502, 5432]
        for porta in portas_testar:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            resultado = sock.connect_ex(('localhost', porta))
            sock.close()
            
            if resultado == 0:
                print(f"   🟡 Porta {porta}: Em uso")
            else:
                print(f"   ✅ Porta {porta}: Livre")
                
    except Exception as e:
        print(f"   ❌ Erro ao verificar portas: {e}")
    
    print()
    
    # Status normal
    return verificar_status()

def main():
    """Função principal"""
    
    # Verificar argumentos
    if len(sys.argv) > 1 and sys.argv[1] == '--detalhado':
        exit_code = status_detalhado()
    elif len(sys.argv) > 1 and sys.argv[1] == '--comandos':
        mostrar_comandos_uteis()
        exit_code = 0
    else:
        exit_code = verificar_status()
        
        # Mostrar comandos úteis se houver problemas
        if exit_code > 0:
            mostrar_comandos_uteis()
    
    print()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()