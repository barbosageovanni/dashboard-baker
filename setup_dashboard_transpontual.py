#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SETUP ESPECÍFICO - DASHBOARD TRANSPONTUAL
Projeto: https://railway.com/project/5ae0dce9-c7cb-45fe-8d75-7f44aecf6523
"""

import os
import subprocess
import sys
from datetime import datetime

def executar_comando(comando, descricao):
    """Executa comando e mostra resultado"""
    print(f"🔄 {descricao}...")
    try:
        result = subprocess.run(comando, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {descricao} - Sucesso")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()[:200]}")
            return True, result.stdout
        else:
            print(f"❌ {descricao} - Erro")
            print(f"   Erro: {result.stderr.strip()[:200]}")
            return False, result.stderr
    except Exception as e:
        print(f"❌ {descricao} - Exceção: {str(e)}")
        return False, str(e)

def verificar_projeto_railway():
    """Verifica se estamos no projeto correto"""
    print("🔍 Verificando projeto Railway...")
    
    sucesso, output = executar_comando("railway status", "Verificação do projeto")
    if sucesso:
        if "Dashboard Transpontual" in output or "5ae0dce9-c7cb-45fe-8d75-7f44aecf6523" in output:
            print("✅ Projeto correto: Dashboard Transpontual")
            return True
        else:
            print("⚠️ Projeto pode estar diferente")
            print("💡 Execute: railway link")
            print("💡 E selecione: Dashboard Transpontual")
            return False
    else:
        print("❌ Não foi possível verificar projeto")
        return False

def verificar_postgresql():
    """Verifica se PostgreSQL está disponível"""
    print("🐘 Verificando PostgreSQL...")
    
    sucesso, output = executar_comando("railway variables", "Verificação de variáveis")
    if sucesso:
        if "DATABASE_URL" in output or "PGHOST" in output:
            print("✅ PostgreSQL configurado!")
            return True
        else:
            print("❌ PostgreSQL não encontrado")
            return False
    else:
        print("❌ Não foi possível verificar variáveis")
        return False

def tentar_adicionar_postgresql():
    """Tenta adicionar PostgreSQL usando diferentes métodos"""
    print("🔧 Tentando adicionar PostgreSQL...")
    
    # Lista de comandos para tentar
    comandos = [
        ("railway service create", "Service Create"),
        ("railway template deploy postgres", "Template PostgreSQL"),
        ("railway add database", "Add Database"),
        ("railway database add postgresql", "Database Add PostgreSQL")
    ]
    
    for comando, descricao in comandos:
        print(f"\n🧪 Tentando: {descricao}")
        sucesso, output = executar_comando(comando, descricao)
        if sucesso:
            print(f"✅ {descricao} funcionou!")
            # Aguardar um pouco para provisionar
            print("⏳ Aguardando provisionamento (30 segundos)...")
            import time
            time.sleep(30)
            return True
    
    print("\n❌ Nenhum comando CLI funcionou")
    print("💡 USE O MÉTODO MANUAL:")
    print("   1. Abra: https://railway.com/project/5ae0dce9-c7cb-45fe-8d75-7f44aecf6523")
    print("   2. Clique em '+ New Service'")
    print("   3. Selecione 'Database' → 'PostgreSQL'")
    print("   4. Aguarde 2-3 minutos")
    print("   5. Execute este script novamente")
    
    input("⏸️  Pressione Enter após adicionar PostgreSQL via web...")
    return verificar_postgresql()

def criar_arquivo_env():
    """Cria arquivo .env com configurações"""
    print("📄 Criando arquivo .env...")
    
    # Obter variáveis do Railway
    sucesso, output = executar_comando("railway variables", "Obtenção de variáveis")
    
    if not sucesso:
        print("❌ Não foi possível obter variáveis")
        return False
    
    # Extrair DATABASE_URL
    database_url = ""
    for linha in output.split('\n'):
        if 'DATABASE_URL' in linha:
            try:
                database_url = linha.split('=', 1)[1].strip()
                break
            except:
                continue
    
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return False
    
    # Criar conteúdo do .env
    env_content = f"""# Dashboard Transpontual - Railway Configuration
# Gerado automaticamente em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

# PostgreSQL Principal
DATABASE_URL={database_url}

# Configurações Streamlit
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Ambiente
RAILWAY_ENVIRONMENT=production
RAILWAY_PROJECT_ID=5ae0dce9-c7cb-45fe-8d75-7f44aecf6523

# Auto-gerado pelo setup
SETUP_VERSION=1.0
SETUP_DATE={datetime.now().isoformat()}
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ Arquivo .env criado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar .env: {e}")
        return False

def testar_conexao_postgresql():
    """Testa conexão com PostgreSQL"""
    print("🧪 Testando conexão PostgreSQL...")
    
    try:
        import psycopg2
        import urllib.parse as urlparse
        
        # Obter DATABASE_URL
        sucesso, output = executar_comando("railway variables get DATABASE_URL", "Obter DATABASE_URL")
        if not sucesso:
            print("❌ Não foi possível obter DATABASE_URL")
            return False
        
        database_url = output.strip()
        if not database_url:
            print("❌ DATABASE_URL vazia")
            return False
        
        # Parse da URL
        url = urlparse.urlparse(database_url)
        config = {
            'host': url.hostname,
            'database': url.path[1:],
            'user': url.username,
            'password': url.password,
            'port': url.port or 5432,
            'sslmode': 'require'
        }
        
        # Testar conexão
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print(f"✅ Conexão PostgreSQL OK!")
        print(f"   Versão: {version[0][:50]}...")
        
        cursor.close()
        conn.close()
        return True
        
    except ImportError:
        print("⚠️ psycopg2 não instalado")
        print("🔧 Instalando psycopg2-binary...")
        sucesso, output = executar_comando("pip install psycopg2-binary", "Instalação psycopg2")
        if sucesso:
            print("✅ psycopg2-binary instalado!")
            return testar_conexao_postgresql()  # Tentar novamente
        else:
            print("❌ Falha na instalação do psycopg2-binary")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {str(e)[:100]}...")
        return False

def main():
    """Função principal do setup"""
    print("=" * 60)
    print("🚀 SETUP DASHBOARD TRANSPONTUAL - RAILWAY")
    print("   Projeto: 5ae0dce9-c7cb-45fe-8d75-7f44aecf6523")
    print("=" * 60)
    print()
    
    # 1. Verificar projeto
    if not verificar_projeto_railway():
        print("\n💡 Execute: railway link")
        print("   E selecione: Dashboard Transpontual")
        return False
    
    # 2. Verificar/Adicionar PostgreSQL
    if not verificar_postgresql():
        if not tentar_adicionar_postgresql():
            return False
    
    # 3. Criar .env
    if not criar_arquivo_env():
        return False
    
    # 4. Testar conexão
    if not testar_conexao_postgresql():
        return False
    
    print("\n" + "=" * 60)
    print("🎉 SETUP CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    print()
    print("✅ Próximos passos:")
    print("   1. Popular banco: python popular_banco_railway.py seu_arquivo.csv")
    print("   2. Fazer deploy: railway up")
    print("   3. Acessar: https://[sua-url].railway.app")
    print()
    
    return True

if __name__ == "__main__":
    if not main():
        print("\n❌ Setup falhou. Verifique os erros acima.")
        sys.exit(1)
    else:
        print("🚀 Sistema pronto para usar!")
        sys.exit(0)