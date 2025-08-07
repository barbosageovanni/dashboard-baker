#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATUALIZADOR DE CREDENCIAIS RAILWAY
Dashboard Baker - Correção Automática
"""

import os
from datetime import datetime

def atualizar_arquivo_env():
    """Atualiza o arquivo .env com as credenciais corretas do Railway"""
    print("🔧 ATUALIZANDO CREDENCIAIS DO RAILWAY...")
    print("=" * 50)
    
    # Credenciais corretas conforme print do usuário
    credenciais_corretas = {
        'PGHOST': 'postgres.railway.internal',
        'PGDATABASE': 'railway',
        'PGUSER': 'postgres',
        'PGPASSWORD': 'vhTRxeFMipdQFlkQpQRdqvKaAyZDbgCL',
        'PGPORT': '5432'
    }
    
    # Criar backup do .env atual se existir
    if os.path.exists('.env'):
        backup_name = f'.env.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        os.rename('.env', backup_name)
        print(f"💾 Backup criado: {backup_name}")
    
    # Criar novo arquivo .env
    conteudo_env = f'''# ========================================
# CONFIGURAÇÕES POSTGRESQL - Dashboard Baker
# ATUALIZADO: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
# ========================================

# LOCAL DATABASE (Desenvolvimento)
LOCAL_DB_PASSWORD=senha123

# RAILWAY (Produção) - CREDENCIAIS ATUALIZADAS
PGHOST={credenciais_corretas['PGHOST']}
PGDATABASE={credenciais_corretas['PGDATABASE']}
PGUSER={credenciais_corretas['PGUSER']}
PGPASSWORD={credenciais_corretas['PGPASSWORD']}
PGPORT={credenciais_corretas['PGPORT']}

# CONFIGURAÇÕES OPCIONAIS
DEBUG=True
ENVIRONMENT=production

# ========================================
# HISTÓRICO DE ATUALIZAÇÕES:
# ========================================
# - {datetime.now().strftime("%d/%m/%Y %H:%M")}: Credenciais Railway atualizadas
# - Host corrigido: postgres-6klk.railway.internal → postgres.railway.internal
# - Password atualizada para versão atual
'''
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(conteudo_env)
    
    print("✅ Arquivo .env atualizado com credenciais corretas!")
    print()
    print("📋 CREDENCIAIS APLICADAS:")
    for key, value in credenciais_corretas.items():
        if key == 'PGPASSWORD':
            masked_password = value[:8] + '*' * (len(value) - 8)
            print(f"   {key}: {masked_password}")
        else:
            print(f"   {key}: {value}")
    
    return True

def verificar_credenciais_railway():
    """Verifica se as credenciais foram aplicadas corretamente"""
    print()
    print("🔍 VERIFICANDO APLICAÇÃO DAS CREDENCIAIS...")
    
    # Recarregar variáveis de ambiente
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)  # Force reload
    except ImportError:
        # Recarregar manualmente
        if os.path.exists('.env'):
            with open('.env', 'r', encoding='utf-8') as f:
                for linha in f:
                    linha = linha.strip()
                    if linha and not linha.startswith('#') and '=' in linha:
                        chave, valor = linha.split('=', 1)
                        valor = valor.strip().strip('"').strip("'")
                        os.environ[chave] = valor
    
    # Verificar se as credenciais corretas foram carregadas
    credenciais_atuais = {
        'PGHOST': os.getenv('PGHOST'),
        'PGDATABASE': os.getenv('PGDATABASE'),
        'PGUSER': os.getenv('PGUSER'),
        'PGPASSWORD': os.getenv('PGPASSWORD'),
        'PGPORT': os.getenv('PGPORT')
    }
    
    print("📊 CREDENCIAIS CARREGADAS:")
    corretas = 0
    total = 0
    
    esperadas = {
        'PGHOST': 'postgres.railway.internal',
        'PGDATABASE': 'railway',
        'PGUSER': 'postgres',
        'PGPASSWORD': 'vhTRxeFMipdQFlkQpQRdqvKaAyZDbgCL',
        'PGPORT': '5432'
    }
    
    for key, valor_atual in credenciais_atuais.items():
        valor_esperado = esperadas[key]
        total += 1
        
        if valor_atual == valor_esperado:
            status = "✅"
            corretas += 1
        else:
            status = "❌"
        
        if key == 'PGPASSWORD':
            valor_mostrar = valor_atual[:8] + '*' * (len(valor_atual) - 8) if valor_atual else 'NÃO DEFINIDO'
        else:
            valor_mostrar = valor_atual or 'NÃO DEFINIDO'
        
        print(f"   {status} {key}: {valor_mostrar}")
    
    if corretas == total:
        print()
        print("🎉 TODAS AS CREDENCIAIS ESTÃO CORRETAS!")
        return True
    else:
        print()
        print(f"⚠️ {total - corretas} credenciais incorretas de {total}")
        return False

def testar_conexao_railway():
    """Testa conexão com as novas credenciais"""
    print()
    print("🔌 TESTANDO CONEXÃO COM RAILWAY...")
    
    try:
        import psycopg2
        
        config = {
            'host': os.getenv('PGHOST'),
            'database': os.getenv('PGDATABASE'),
            'user': os.getenv('PGUSER'),
            'password': os.getenv('PGPASSWORD'),
            'port': int(os.getenv('PGPORT', '5432')),
            'sslmode': 'require',
            'connect_timeout': 15
        }
        
        print("   Conectando...")
        conn = psycopg2.connect(**config)
        
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        
        cursor.execute("SELECT current_database(), current_user")
        db, user = cursor.fetchone()
        
        print(f"   ✅ Conexão bem-sucedida!")
        print(f"   ✅ Database: {db}")
        print(f"   ✅ User: {user}")
        print(f"   ✅ PostgreSQL: {version[:50]}...")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro na conexão: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 CORRETOR DE CREDENCIAIS RAILWAY")
    print("=" * 50)
    print("📝 Este script irá:")
    print("   1. Fazer backup do .env atual")
    print("   2. Atualizar com credenciais corretas")
    print("   3. Verificar se foram aplicadas")
    print("   4. Testar conexão com Railway")
    print()
    
    # 1. Atualizar arquivo .env
    if not atualizar_arquivo_env():
        print("❌ Erro ao atualizar .env")
        return False
    
    # 2. Verificar credenciais
    if not verificar_credenciais_railway():
        print("❌ Erro na verificação das credenciais")
        return False
    
    # 3. Testar conexão
    if not testar_conexao_railway():
        print("❌ Erro na conexão com Railway")
        print()
        print("💡 POSSÍVEIS CAUSAS:")
        print("   1. Credenciais ainda estão incorretas")
        print("   2. Serviço Railway está inativo")
        print("   3. Problemas de rede/firewall")
        return False
    
    print()
    print("🎉 CREDENCIAIS ATUALIZADAS E TESTADAS COM SUCESSO!")
    print("=" * 50)
    print("✅ PRÓXIMOS PASSOS:")
    print("   1. Execute: python migrar_local_para_railway_corrigido.py")
    print("   2. Teste: python dashboard_baker_web_corrigido.py")
    print("   3. Deploy: railway up")
    print()
    
    return True

if __name__ == "__main__":
    main()