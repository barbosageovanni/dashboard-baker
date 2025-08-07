#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALTERNATIVA: SUPABASE POSTGRESQL (GRATUITO)
Dashboard Baker - Setup Rápido e Confiável
"""

import psycopg2
import pandas as pd
from datetime import datetime
import os

def explicar_supabase():
    """Explica vantagens do Supabase"""
    print("🌟 SUPABASE: ALTERNATIVA SUPERIOR AO RAILWAY")
    print("=" * 60)
    print()
    print("✅ VANTAGENS DO SUPABASE:")
    print("   🆓 Completamente GRATUITO (500MB)")
    print("   🚀 Setup em 2 minutos")
    print("   🔒 Credenciais claras e confiáveis")
    print("   📊 Dashboard visual integrado")
    print("   🔄 API REST automática")
    print("   💾 Backup automático")
    print("   🌐 CDN global")
    print()
    print("❌ PROBLEMAS DO RAILWAY RESOLVIDOS:")
    print("   • Sem confusão host interno vs externo")
    print("   • Credenciais claras e documentadas")
    print("   • Interface mais amigável")
    print("   • Suporte melhor")
    print()

def criar_projeto_supabase():
    """Instrui como criar projeto Supabase"""
    print("🎯 COMO CRIAR PROJETO SUPABASE:")
    print("=" * 40)
    print()
    print("1️⃣ Acesse: https://app.supabase.com")
    print("   • Faça login com GitHub, Google ou email")
    print()
    print("2️⃣ Clique em 'New Project'")
    print()
    print("3️⃣ Preencha:")
    print("   • Name: Dashboard-Baker")
    print("   • Database Password: (crie uma senha forte)")
    print("   • Region: South America (São Paulo)")
    print()
    print("4️⃣ Clique 'Create new project'")
    print("   • Aguarde ~2 minutos para provisionar")
    print()
    print("5️⃣ Vá em Settings → Database")
    print("   • Copie as credenciais de 'Connection info'")
    print()

def input_credenciais_supabase():
    """Solicita credenciais do Supabase"""
    print("📝 DIGITE AS CREDENCIAIS DO SUPABASE:")
    print("=" * 40)
    print()
    print("No Supabase: Settings → Database → Connection info")
    print()
    
    host = input("🌐 Host (ex: db.abc123.supabase.co): ").strip()
    database = input("📊 Database (padrão: postgres): ").strip() or "postgres"
    user = input("👤 User (padrão: postgres): ").strip() or "postgres"
    password = input("🔑 Password: ").strip()
    port = input("🔢 Port (padrão: 5432): ").strip() or "5432"
    
    if not host or not password:
        print("❌ Host e password são obrigatórios!")
        return None
    
    try:
        port = int(port)
    except ValueError:
        print("❌ Porta inválida!")
        return None
    
    return {
        'host': host,
        'database': database,
        'user': user,
        'password': password,
        'port': port
    }

def testar_conexao_supabase(credenciais):
    """Testa conexão com Supabase"""
    print()
    print("🔌 TESTANDO CONEXÃO SUPABASE...")
    
    try:
        config = credenciais.copy()
        config.update({
            'sslmode': 'require',
            'connect_timeout': 10
        })
        
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Testes
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"   ✅ PostgreSQL: {version[:50]}...")
        
        cursor.execute("SELECT current_database(), current_user")
        db, user = cursor.fetchone()
        print(f"   ✅ Database: {db}")
        print(f"   ✅ User: {user}")
        
        # Teste de permissões
        cursor.execute("CREATE TABLE IF NOT EXISTS teste_supabase (id SERIAL, data TIMESTAMP DEFAULT NOW())")
        cursor.execute("INSERT INTO teste_supabase DEFAULT VALUES")
        cursor.execute("SELECT COUNT(*) FROM teste_supabase")
        count = cursor.fetchone()[0]
        cursor.execute("DROP TABLE teste_supabase")
        
        print(f"   ✅ Teste de escrita: {count} registros")
        
        cursor.close()
        conn.close()
        
        print("   🎉 SUPABASE FUNCIONANDO PERFEITAMENTE!")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def criar_tabela_dashboard_supabase(credenciais):
    """Cria tabela do dashboard no Supabase"""
    print()
    print("🏗️ CRIANDO TABELA DASHBOARD NO SUPABASE...")
    
    try:
        config = credenciais.copy()
        config.update({'sslmode': 'require', 'connect_timeout': 15})
        
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # SQL completo para criar tabela
        create_sql = """
        -- Remover tabela se existir
        DROP TABLE IF EXISTS dashboard_baker CASCADE;
        
        -- Criar tabela principal
        CREATE TABLE dashboard_baker (
            id BIGSERIAL PRIMARY KEY,
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
            origem_dados VARCHAR(50) DEFAULT 'Migração_Supabase',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Índices para performance
        CREATE INDEX idx_dashboard_baker_numero_cte ON dashboard_baker(numero_cte);
        CREATE INDEX idx_dashboard_baker_destinatario ON dashboard_baker(destinatario_nome);
        CREATE INDEX idx_dashboard_baker_data_emissao ON dashboard_baker(data_emissao);
        CREATE INDEX idx_dashboard_baker_data_baixa ON dashboard_baker(data_baixa);
        CREATE INDEX idx_dashboard_baker_created_at ON dashboard_baker(created_at);
        
        -- Trigger para updated_at
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        
        CREATE TRIGGER update_dashboard_baker_updated_at
            BEFORE UPDATE ON dashboard_baker
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        
        -- Políticas RLS (Row Level Security) - opcional
        ALTER TABLE dashboard_baker ENABLE ROW LEVEL SECURITY;
        
        -- Política para permitir todas as operações (para desenvolvimento)
        CREATE POLICY "Allow all operations" ON dashboard_baker
            FOR ALL USING (true) WITH CHECK (true);
        """
        
        cursor.execute(create_sql)
        conn.commit()
        cursor.close()
        conn.close()
        
        print("   ✅ Tabela criada com sucesso!")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao criar tabela: {e}")
        return False

def migrar_dados_para_supabase(credenciais):
    """Migra dados do local para Supabase"""
    print()
    print("📥 MIGRANDO DADOS PARA SUPABASE...")
    
    try:
        # Conectar Supabase
        config_supabase = credenciais.copy()
        config_supabase.update({'sslmode': 'require', 'connect_timeout': 15})
        conn_supabase = psycopg2.connect(**config_supabase)
        print("   ✅ Conectado ao Supabase")
        
        # Conectar local
        conn_local = psycopg2.connect(
            host='localhost',
            database='dashboard_baker',
            user='postgres',
            password='senha123',
            port=5432
        )
        print("   ✅ Conectado ao banco local")
        
        # Extrair dados
        df = pd.read_sql_query("""
            SELECT numero_cte, destinatario_nome, veiculo_placa, valor_total,
                   data_emissao, numero_fatura, data_baixa, observacao,
                   data_inclusao_fatura, data_envio_processo, primeiro_envio,
                   data_rq_tmc, data_atesto, envio_final
            FROM dashboard_baker 
            ORDER BY numero_cte
        """, conn_local)
        
        print(f"   📤 {len(df)} registros extraídos do local")
        
        # Inserir no Supabase
        cursor_supabase = conn_supabase.cursor()
        inseridos = 0
        
        for index, row in df.iterrows():
            try:
                cursor_supabase.execute("""
                    INSERT INTO dashboard_baker (
                        numero_cte, destinatario_nome, veiculo_placa, valor_total,
                        data_emissao, numero_fatura, data_baixa, observacao,
                        data_inclusao_fatura, data_envio_processo, primeiro_envio,
                        data_rq_tmc, data_atesto, envio_final
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, tuple(row))
                inseridos += 1
                
                # Progress
                if inseridos % 100 == 0:
                    conn_supabase.commit()
                    print(f"      💾 {inseridos} registros processados...")
                    
            except Exception as e:
                if "duplicate key" not in str(e):
                    print(f"      ⚠️ Erro CTE {row.get('numero_cte', 'N/A')}: {str(e)[:40]}")
        
        # Commit final
        conn_supabase.commit()
        
        # Verificar
        cursor_supabase.execute("SELECT COUNT(*) FROM dashboard_baker")
        total_supabase = cursor_supabase.fetchone()[0]
        
        cursor_supabase.execute("SELECT SUM(valor_total) FROM dashboard_baker")
        valor_total = cursor_supabase.fetchone()[0] or 0
        
        conn_supabase.close()
        conn_local.close()
        
        print(f"   ✅ {inseridos} registros inseridos")
        print(f"   📊 Total no Supabase: {total_supabase}")
        print(f"   💰 Valor total: R$ {valor_total:,.2f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro na migração: {e}")
        return False

def criar_env_supabase(credenciais):
    """Cria .env com credenciais Supabase"""
    if os.path.exists('.env'):
        backup = f'.env.backup.supabase.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        os.rename('.env', backup)
        print(f"💾 Backup criado: {backup}")
    
    conteudo = f'''# ========================================
# SUPABASE POSTGRESQL - CREDENCIAIS FUNCIONAIS
# Migração concluída em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
# ========================================

# SUPABASE (Produção)
SUPABASE_HOST={credenciais['host']}
SUPABASE_DB={credenciais['database']}
SUPABASE_USER={credenciais['user']}
SUPABASE_PASSWORD={credenciais['password']}
SUPABASE_PORT={credenciais['port']}

# ALTERNATIVA (para compatibilidade com scripts existentes)
PGHOST={credenciais['host']}
PGDATABASE={credenciais['database']}
PGUSER={credenciais['user']}
PGPASSWORD={credenciais['password']}
PGPORT={credenciais['port']}

# LOCAL
LOCAL_DB_PASSWORD=senha123

# CONFIGURAÇÕES
DEBUG=True
ENVIRONMENT=production
DATABASE_PROVIDER=supabase
'''
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print("✅ .env atualizado com credenciais Supabase!")

def main():
    """Função principal"""
    print("🌟 SETUP SUPABASE: ALTERNATIVA SUPERIOR")
    print("=" * 50)
    print()
    
    # Explicar vantagens
    explicar_supabase()
    
    # Instruções de criação
    criar_projeto_supabase()
    
    print()
    print("▶️  Pressione Enter quando tiver criado o projeto Supabase...")
    input()
    
    # Solicitar credenciais
    credenciais = input_credenciais_supabase()
    if not credenciais:
        return False
    
    # Testar conexão
    if not testar_conexao_supabase(credenciais):
        print("❌ Falha na conexão com Supabase")
        return False
    
    # Criar tabela
    if not criar_tabela_dashboard_supabase(credenciais):
        print("❌ Falha ao criar tabela")
        return False
    
    # Migrar dados
    if not migrar_dados_para_supabase(credenciais):
        print("❌ Falha na migração")
        return False
    
    # Atualizar .env
    criar_env_supabase(credenciais)
    
    print()
    print("🎉 MIGRAÇÃO SUPABASE CONCLUÍDA COM SUCESSO!")
    print("=" * 50)
    print("✅ VANTAGENS OBTIDAS:")
    print("   🆓 Banco gratuito e confiável")
    print("   🚀 Performance superior")
    print("   📊 Dashboard visual no Supabase")
    print("   🔄 API REST automática criada")
    print("   💾 Backups automáticos")
    print()
    print("🎯 PRÓXIMOS PASSOS:")
    print("   1. Teste: python dashboard_baker_web_corrigido.py")
    print("   2. Acesse o Supabase Dashboard para ver os dados")
    print("   3. Deploy da aplicação")
    print("   4. Configure domínio personalizado")
    print()
    print(f"🌐 Supabase Dashboard: https://app.supabase.com/project/{credenciais['host'].split('.')[1]}")
    
    return True

if __name__ == "__main__":
    main()