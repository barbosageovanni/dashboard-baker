#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE RÁPIDO: Credenciais Externas Comuns do Railway
Dashboard Baker - Tentativa com hosts externos padrão
"""

import psycopg2

def testar_credenciais_railway():
    """Testa diferentes combinações de hosts externos do Railway"""
    print("🔍 TESTANDO HOSTS EXTERNOS COMUNS DO RAILWAY")
    print("=" * 60)
    
    # Sua senha que sabemos que está correta
    password_correto = "vhTRxeFMipdQFlkQpQRdqvKaAyZDbgCL"
    
    # Hosts externos comuns do Railway
    hosts_externos = [
        "viaduct.proxy.rlwy.net",
        "roundhouse.proxy.rlwy.net", 
        "maglev.proxy.rlwy.net",
        "containers.proxy.rlwy.net"
    ]
    
    # Portas comuns do Railway
    portas_comuns = [18783, 12345, 5432, 54321, 65432]
    
    print(f"🔑 Usando password: {password_correto[:8]}{'*' * (len(password_correto) - 8)}")
    print()
    
    # Testar combinações
    for host in hosts_externos:
        print(f"🌐 Testando host: {host}")
        
        for porta in portas_comuns:
            config_teste = {
                'host': host,
                'database': 'railway',
                'user': 'postgres',
                'password': password_correto,
                'port': porta,
                'sslmode': 'require',
                'connect_timeout': 8
            }
            
            try:
                print(f"   🔌 Porta {porta}...", end="")
                conn = psycopg2.connect(**config_teste)
                
                # Teste rápido
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                conn.close()
                
                print(" ✅ SUCESSO!")
                print()
                print("🎉 CREDENCIAIS CORRETAS ENCONTRADAS:")
                print(f"   Host: {host}")
                print(f"   Port: {porta}")
                print(f"   Database: railway")
                print(f"   User: postgres")
                print(f"   Password: {password_correto}")
                
                return config_teste
                
            except psycopg2.OperationalError as e:
                if "could not translate host name" in str(e):
                    print(" ❌ DNS")
                elif "Connection refused" in str(e):
                    print(" ❌ Recusada")
                elif "authentication failed" in str(e):
                    print(" ❌ Auth")
                elif "timeout" in str(e):
                    print(" ❌ Timeout")
                else:
                    print(" ❌ Erro")
            except Exception as e:
                print(" ❌ Erro")
        
        print()
    
    print("❌ NENHUMA COMBINAÇÃO FUNCIONOU")
    print()
    print("💡 SOLUÇÕES:")
    print("   1. Verifique credenciais no Railway Dashboard")
    print("   2. Confirme que PostgreSQL está ativo")
    print("   3. Use o script interativo: python obter_credenciais_externas.py")
    
    return None

def atualizar_env_rapido(config):
    """Atualiza .env rapidamente com credenciais funcionais"""
    import os
    from datetime import datetime
    
    if os.path.exists('.env'):
        backup = f'.env.backup.rapido.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        os.rename('.env', backup)
        print(f"💾 Backup: {backup}")
    
    conteudo = f'''# RAILWAY EXTERNAS - TESTADAS E FUNCIONANDO
PGHOST={config['host']}
PGDATABASE={config['database']}
PGUSER={config['user']}
PGPASSWORD={config['password']}
PGPORT={config['port']}

# LOCAL
LOCAL_DB_PASSWORD=senha123
'''
    
    with open('.env', 'w') as f:
        f.write(conteudo)
    
    print("✅ .env atualizado!")

def executar_migracao_imediata(config):
    """Executa migração imediatamente com credenciais funcionais"""
    print()
    print("🚀 EXECUTAR MIGRAÇÃO AGORA? (s/n): ", end="")
    resposta = input().lower()
    
    if resposta in ['s', 'sim', 'y', 'yes']:
        print()
        print("⚡ INICIANDO MIGRAÇÃO IMEDIATA...")
        
        try:
            import pandas as pd
            
            # Conectar Railway
            conn_railway = psycopg2.connect(**config)
            print("✅ Conectado ao Railway")
            
            # Conectar local
            conn_local = psycopg2.connect(
                host='localhost',
                database='dashboard_baker', 
                user='postgres',
                password='senha123',
                port=5432
            )
            print("✅ Conectado ao local")
            
            # Criar tabela
            cursor = conn_railway.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dashboard_baker (
                    id SERIAL PRIMARY KEY,
                    numero_cte INTEGER UNIQUE NOT NULL,
                    destinatario_nome VARCHAR(255),
                    valor_total DECIMAL(15,2) DEFAULT 0,
                    data_emissao DATE,
                    origem_dados VARCHAR(50) DEFAULT 'Migração_Imediata'
                )
            """)
            conn_railway.commit()
            print("✅ Tabela criada")
            
            # Migrar dados básicos
            df = pd.read_sql_query(
                "SELECT numero_cte, destinatario_nome, valor_total, data_emissao FROM dashboard_baker LIMIT 100",
                conn_local
            )
            print(f"✅ {len(df)} registros extraídos")
            
            # Inserir
            inseridos = 0
            for _, row in df.iterrows():
                try:
                    cursor.execute("""
                        INSERT INTO dashboard_baker (numero_cte, destinatario_nome, valor_total, data_emissao)
                        VALUES (%s, %s, %s, %s) ON CONFLICT (numero_cte) DO NOTHING
                    """, (row['numero_cte'], row['destinatario_nome'], row['valor_total'], row['data_emissao']))
                    inseridos += 1
                except:
                    pass
            
            conn_railway.commit()
            print(f"✅ {inseridos} registros migrados")
            
            conn_railway.close()
            conn_local.close()
            
            print("🎉 MIGRAÇÃO TESTE CONCLUÍDA!")
            return True
            
        except Exception as e:
            print(f"❌ Erro na migração: {e}")
            return False
    
    return False

def main():
    """Função principal"""
    config_funcionais = testar_credenciais_railway()
    
    if config_funcionais:
        print()
        atualizar_env_rapido(config_funcionais)
        executar_migracao_imediata(config_funcionais)
        
        print()
        print("🎯 PRÓXIMOS PASSOS:")
        print("   1. Migração completa: python migracao_direta.py")
        print("   2. Teste dashboard: python dashboard_baker_web_corrigido.py")
    else:
        print()
        print("🔧 ALTERNATIVE SOLUTION:")
        print("   Execute: python obter_credenciais_externas.py")
        print("   Para teste interativo com suas credenciais")

if __name__ == "__main__":
    main()