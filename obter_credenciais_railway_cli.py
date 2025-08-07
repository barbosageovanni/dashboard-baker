#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OBTER CREDENCIAIS RAILWAY VIA CLI
Dashboard Baker - Automático e Confiável
"""

import subprocess
import psycopg2
import os
import re
from datetime import datetime

def obter_variaveis_railway():
    """Obtém variáveis do projeto Railway via CLI"""
    print("🚂 OBTENDO CREDENCIAIS VIA RAILWAY CLI...")
    print("=" * 50)
    
    try:
        # Verificar se está logado
        result = subprocess.run(['railway', 'whoami'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print("❌ Não está logado no Railway CLI")
            print("💡 Execute: railway login")
            return None
        
        print(f"✅ Logado como: {result.stdout.strip()}")
        
        # Obter variáveis do projeto
        print("📊 Obtendo variáveis do projeto...")
        result = subprocess.run(['railway', 'variables'], 
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode != 0:
            print(f"❌ Erro ao obter variáveis: {result.stderr}")
            return None
        
        print("✅ Variáveis obtidas!")
        
        # Parsear variáveis
        variables_output = result.stdout
        print("\n📋 VARIÁVEIS DO RAILWAY:")
        print("-" * 30)
        print(variables_output)
        print("-" * 30)
        
        # Extrair credenciais específicas
        credenciais = {}
        
        for line in variables_output.split('\n'):
            line = line.strip()
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Mapear variáveis Railway para credenciais PostgreSQL
                if key == 'PGHOST':
                    credenciais['host'] = value
                elif key == 'PGPORT':
                    credenciais['port'] = int(value)
                elif key == 'PGDATABASE':
                    credenciais['database'] = value
                elif key == 'PGUSER':
                    credenciais['user'] = value
                elif key == 'PGPASSWORD':
                    credenciais['password'] = value
                elif key == 'POSTGRES_PASSWORD':
                    credenciais['password'] = value
                elif key == 'RAILWAY_TCP_PROXY_DOMAIN':
                    credenciais['host'] = value
                elif key == 'RAILWAY_TCP_PROXY_PORT':
                    credenciais['port'] = int(value)
                elif key == 'DATABASE_URL':
                    # Parse DATABASE_URL se disponível
                    credenciais_url = parse_database_url(value)
                    if credenciais_url:
                        credenciais.update(credenciais_url)
        
        return credenciais
        
    except subprocess.TimeoutExpired:
        print("❌ Timeout ao executar Railway CLI")
        return None
    except FileNotFoundError:
        print("❌ Railway CLI não encontrado no PATH")
        print("💡 Instale: npm install -g @railway/cli")
        return None
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return None

def parse_database_url(database_url):
    """Parse DATABASE_URL para extrair credenciais"""
    try:
        import urllib.parse as urlparse
        parsed = urlparse.urlparse(database_url)
        
        return {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'database': parsed.path[1:] if parsed.path.startswith('/') else parsed.path,
            'user': parsed.username,
            'password': parsed.password
        }
    except:
        return None

def obter_credenciais_via_service():
    """Tenta obter credenciais via railway service"""
    print("\n🔄 TENTANDO MÉTODO ALTERNATIVO...")
    
    try:
        # Listar serviços
        result = subprocess.run(['railway', 'service', 'list'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("📋 Serviços disponíveis:")
            print(result.stdout)
            
            # Procurar por PostgreSQL
            lines = result.stdout.split('\n')
            postgres_service = None
            
            for line in lines:
                if 'postgres' in line.lower() or 'postgresql' in line.lower():
                    postgres_service = line.strip()
                    break
            
            if postgres_service:
                print(f"✅ Serviço PostgreSQL encontrado: {postgres_service}")
                
                # Tentar obter variáveis específicas do serviço
                service_id = postgres_service.split()[0] if postgres_service.split() else None
                
                if service_id:
                    result = subprocess.run(['railway', 'variables', '--service', service_id], 
                                          capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        print("📊 Variáveis do serviço PostgreSQL:")
                        print(result.stdout)
                        return parse_variables_output(result.stdout)
        
        return None
        
    except Exception as e:
        print(f"❌ Erro no método alternativo: {e}")
        return None

def parse_variables_output(output):
    """Parse output das variáveis para extrair credenciais"""
    credenciais = {}
    
    for line in output.split('\n'):
        line = line.strip()
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            if key in ['PGHOST', 'POSTGRES_HOST']:
                credenciais['host'] = value
            elif key in ['PGPORT', 'POSTGRES_PORT']:
                credenciais['port'] = int(value)
            elif key in ['PGDATABASE', 'POSTGRES_DB']:
                credenciais['database'] = value
            elif key in ['PGUSER', 'POSTGRES_USER']:
                credenciais['user'] = value
            elif key in ['PGPASSWORD', 'POSTGRES_PASSWORD']:
                credenciais['password'] = value
    
    return credenciais if len(credenciais) >= 4 else None

def montar_credenciais_completas(credenciais_parciais):
    """Monta credenciais completas com valores padrão"""
    credenciais = {
        'host': credenciais_parciais.get('host', ''),
        'port': credenciais_parciais.get('port', 5432),
        'database': credenciais_parciais.get('database', 'railway'),
        'user': credenciais_parciais.get('user', 'postgres'),
        'password': credenciais_parciais.get('password', '')
    }
    
    # Se não temos host, tentar construir
    if not credenciais['host']:
        # Hosts comuns Railway
        hosts_railway = [
            "viaduct.proxy.rlwy.net",
            "roundhouse.proxy.rlwy.net", 
            "maglev.proxy.rlwy.net"
        ]
        
        # Testar cada host com a senha obtida
        if credenciais['password']:
            for host in hosts_railway:
                test_cred = credenciais.copy()
                test_cred['host'] = host
                
                if testar_conexao_rapida(test_cred):
                    credenciais['host'] = host
                    break
    
    return credenciais

def testar_conexao_rapida(credenciais):
    """Teste rápido de conexão"""
    try:
        config = credenciais.copy()
        config.update({
            'sslmode': 'require',
            'connect_timeout': 5
        })
        
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        return True
    except:
        return False

def testar_credenciais_obtidas(credenciais):
    """Testa as credenciais obtidas do Railway"""
    print("\n🔌 TESTANDO CREDENCIAIS OBTIDAS...")
    print("=" * 40)
    
    print("📋 Credenciais extraídas:")
    for key, value in credenciais.items():
        if key == 'password':
            print(f"   {key}: {'*' * len(str(value))}")
        else:
            print(f"   {key}: {value}")
    
    # Verificar se temos credenciais mínimas
    required_fields = ['host', 'password']
    missing_fields = [field for field in required_fields if not credenciais.get(field)]
    
    if missing_fields:
        print(f"❌ Campos obrigatórios ausentes: {missing_fields}")
        return False
    
    try:
        config = credenciais.copy()
        config.update({
            'sslmode': 'require',
            'connect_timeout': 15,
            'application_name': 'Dashboard_Baker_Railway_CLI'
        })
        
        print("\n🔌 Conectando...", end="")
        conn = psycopg2.connect(**config)
        print(" ✅ Conectado!")
        
        cursor = conn.cursor()
        
        # Teste 1: Versão
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL: {version[:50]}...")
        
        # Teste 2: Database e User
        cursor.execute("SELECT current_database(), current_user")
        db, user = cursor.fetchone()
        print(f"✅ Database: {db}")
        print(f"✅ User: {user}")
        
        # Teste 3: Permissões
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
        table_count = cursor.fetchone()[0]
        print(f"✅ Tabelas disponíveis: {table_count}")
        
        # Teste 4: Escrita
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teste_railway_cli (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT NOW(),
                source VARCHAR(50) DEFAULT 'Railway_CLI_Test'
            )
        """)
        
        cursor.execute("INSERT INTO teste_railway_cli (source) VALUES ('Dashboard_Baker_Migration')")
        cursor.execute("SELECT COUNT(*) FROM teste_railway_cli")
        test_count = cursor.fetchone()[0]
        cursor.execute("DROP TABLE teste_railway_cli")
        
        print(f"✅ Teste de escrita: {test_count} registros")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 CREDENCIAIS RAILWAY CLI FUNCIONAIS!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro na conexão: {e}")
        return False

def criar_env_railway_cli(credenciais):
    """Cria .env com credenciais obtidas via Railway CLI"""
    if os.path.exists('.env'):
        backup = f'.env.backup.railway_cli.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        os.rename('.env', backup)
        print(f"💾 Backup criado: {backup}")
    
    conteudo = f'''# ========================================
# RAILWAY POSTGRESQL - VIA CLI
# Obtidas automaticamente em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
# ========================================

# RAILWAY (Produção) - CREDENCIAIS VIA CLI
PGHOST={credenciais['host']}
PGDATABASE={credenciais['database']}
PGUSER={credenciais['user']}
PGPASSWORD={credenciais['password']}
PGPORT={credenciais['port']}

# LOCAL DATABASE (Desenvolvimento)
LOCAL_DB_PASSWORD=senha123

# CONFIGURAÇÕES
DEBUG=True
ENVIRONMENT=production
RAILWAY_CLI_VALIDATED=true

# ========================================
# VALIDAÇÃO CLI:
# ========================================
# ✅ Obtidas via Railway CLI
# ✅ Testadas e funcionais
# ✅ Prontas para migração
'''
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print("✅ .env atualizado com credenciais Railway CLI!")

def executar_migracao_imediata(credenciais):
    """Executa migração imediata com credenciais Railway CLI"""
    print("\n🚀 EXECUTAR MIGRAÇÃO AGORA? (s/n): ", end="")
    resposta = input().lower()
    
    if resposta not in ['s', 'sim', 'y', 'yes']:
        return False
    
    print("\n⚡ INICIANDO MIGRAÇÃO VIA RAILWAY CLI...")
    
    try:
        import pandas as pd
        
        # Conectar Railway
        config_railway = credenciais.copy()
        config_railway.update({
            'sslmode': 'require',
            'connect_timeout': 15
        })
        
        conn_railway = psycopg2.connect(**config_railway)
        print("   ✅ Conectado ao Railway")
        
        # Conectar local
        conn_local = psycopg2.connect(
            host='localhost',
            database='dashboard_baker',
            user='postgres',
            password='senha123',
            port=5432
        )
        print("   ✅ Conectado ao banco local")
        
        # Criar tabela
        cursor = conn_railway.cursor()
        cursor.execute("""
            DROP TABLE IF EXISTS dashboard_baker;
            CREATE TABLE dashboard_baker (
                id SERIAL PRIMARY KEY,
                numero_cte INTEGER UNIQUE NOT NULL,
                destinatario_nome VARCHAR(255),
                veiculo_placa VARCHAR(20),
                valor_total DECIMAL(15,2) DEFAULT 0,
                data_emissao DATE,
                numero_fatura VARCHAR(100),
                data_baixa DATE,
                observacao TEXT,
                data_inclusao_fatura DATE,
                data_envio_processo DATE,
                primeiro_envio DATE,
                data_rq_tmc DATE,
                data_atesto DATE,
                envio_final DATE,
                origem_dados VARCHAR(50) DEFAULT 'Railway_CLI_Migration',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn_railway.commit()
        print("   ✅ Tabela criada")
        
        # Migrar dados
        df = pd.read_sql_query("""
            SELECT numero_cte, destinatario_nome, veiculo_placa, valor_total,
                   data_emissao, numero_fatura, data_baixa, observacao,
                   data_inclusao_fatura, data_envio_processo, primeiro_envio,
                   data_rq_tmc, data_atesto, envio_final
            FROM dashboard_baker 
            ORDER BY numero_cte
        """, conn_local)
        
        print(f"   📤 {len(df)} registros extraídos")
        
        # Inserir
        inseridos = 0
        for _, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO dashboard_baker (
                        numero_cte, destinatario_nome, veiculo_placa, valor_total,
                        data_emissao, numero_fatura, data_baixa, observacao,
                        data_inclusao_fatura, data_envio_processo, primeiro_envio,
                        data_rq_tmc, data_atesto, envio_final
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, tuple(row))
                inseridos += 1
                
                if inseridos % 100 == 0:
                    conn_railway.commit()
                    print(f"      💾 {inseridos} registros processados...")
            except:
                pass
        
        conn_railway.commit()
        
        # Verificar
        cursor.execute("SELECT COUNT(*) FROM dashboard_baker")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(valor_total) FROM dashboard_baker")
        valor_total = cursor.fetchone()[0] or 0
        
        conn_railway.close()
        conn_local.close()
        
        print(f"   ✅ {inseridos} registros migrados")
        print(f"   📊 Total no Railway: {total}")
        print(f"   💰 Valor total: R$ {valor_total:,.2f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro na migração: {e}")
        return False

def main():
    """Função principal"""
    print("🚂 OBTER CREDENCIAIS VIA RAILWAY CLI")
    print("=" * 50)
    print()
    
    # Método 1: Variáveis gerais
    credenciais = obter_variaveis_railway()
    
    # Método 2: Se não funcionou, tentar via service
    if not credenciais or len(credenciais) < 4:
        print("\n🔄 Tentando método alternativo...")
        credenciais_alt = obter_credenciais_via_service()
        if credenciais_alt:
            credenciais = credenciais_alt
    
    # Completar credenciais se necessário
    if credenciais:
        credenciais = montar_credenciais_completas(credenciais)
    
    if not credenciais or not credenciais.get('password'):
        print("\n❌ NÃO FOI POSSÍVEL OBTER CREDENCIAIS VIA CLI")
        print("💡 ALTERNATIVAS:")
        print("   1. Verifique se está no projeto correto: railway status")
        print("   2. Tente: railway variables --help")
        print("   3. Use: python obter_credenciais_railway_manual.py")
        print("   4. Ou migre para Supabase: python alternativa_supabase.py")
        return False
    
    # Testar credenciais
    if not testar_credenciais_obtidas(credenciais):
        print("\n❌ CREDENCIAIS OBTIDAS NÃO FUNCIONARAM")
        return False
    
    # Salvar no .env
    criar_env_railway_cli(credenciais)
    
    # Migração opcional
    executar_migracao_imediata(credenciais)
    
    print("\n🎉 SUCESSO COMPLETO VIA RAILWAY CLI!")
    print("=" * 40)
    print("✅ PRÓXIMOS PASSOS:")
    print("   1. Migração completa: python migracao_direta.py")
    print("   2. Teste dashboard: python dashboard_baker_web_corrigido.py")
    print("   3. Deploy: railway up")
    
    return True

if __name__ == "__main__":
    main()