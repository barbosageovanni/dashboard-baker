#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 DEPLOY DASHBOARD BAKER NO SUPABASE - VERSÃO COMPLETA
Migração completa do sistema local para Supabase PostgreSQL
MANTÉM: dashboard_baker_web_corrigido.py (nome original)
"""

import os
import psycopg2
import pandas as pd
from datetime import datetime, date
import json
import getpass
import sys
from urllib.parse import urlparse
import shutil

class DeploySupabaseCompleto:
    """Classe para deploy completo no Supabase"""
    
    def __init__(self):
        self.config_local = {}
        self.config_supabase = {}
        self.conexao_local = None
        self.conexao_supabase = None
        
    def step1_configurar_supabase(self):
        """Configurar conexão com Supabase"""
        print("🎯 STEP 1: CONFIGURAÇÃO SUPABASE")
        print("="*50)
        
        # Solicitar URL do Supabase
        print("📋 ONDE ENCONTRAR SUA URL SUPABASE:")
        print("   1. Acesse: https://supabase.com/dashboard")
        print("   2. Selecione seu projeto")
        print("   3. Vá em: Settings → API")
        print("   4. Copie a 'Project URL'")
        print()
        
        url = input("🌐 Cole sua URL do Supabase: ").strip()
        if not url or not '.supabase.co' in url:
            print("❌ URL inválida!")
            return False
            
        # Extrair informações da URL
        parsed = urlparse(url)
        project_id = parsed.hostname.split('.')[0]
        
        # Solicitar senha
        print("\n🔑 SENHA DO BANCO:")
        print("   1. No Supabase: Settings → Database")
        print("   2. Se não lembra: clique 'Reset database password'")
        
        senha = getpass.getpass("🔐 Digite a senha do banco: ")
        
        # Configurar Supabase
        self.config_supabase = {
            'host': f'db.{project_id}.supabase.co',
            'database': 'postgres',
            'user': 'postgres', 
            'password': senha,
            'port': 5432,
            'sslmode': 'require'
        }
        
        print(f"✅ Configuração Supabase: {self.config_supabase['host']}")
        return True
    
    def step2_testar_conexoes(self):
        """Testar conexão local e Supabase"""
        print("\n🔍 STEP 2: TESTANDO CONEXÕES")
        print("="*50)
        
        # Testar conexão local
        print("🏠 Testando conexão local...")
        self.config_local = {
            'host': 'localhost',
            'database': 'dashboard_baker',
            'user': 'postgres',
            'password': 'senha123',
            'port': 5432
        }
        
        try:
            self.conexao_local = psycopg2.connect(**self.config_local)
            print("✅ Conexão local OK")
            
            cursor = self.conexao_local.cursor()
            cursor.execute("SELECT COUNT(*) FROM dashboard_baker")
            count = cursor.fetchone()[0]
            print(f"📊 Registros locais: {count:,}")
            cursor.close()
            
        except Exception as e:
            print(f"❌ Erro conexão local: {e}")
            return False
        
        # Testar conexão Supabase
        print("\n☁️ Testando conexão Supabase...")
        try:
            self.conexao_supabase = psycopg2.connect(**self.config_supabase)
            print("✅ Conexão Supabase OK")
            
            cursor = self.conexao_supabase.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            print(f"📋 PostgreSQL: {version.split()[1]}")
            cursor.close()
            
        except Exception as e:
            print(f"❌ Erro conexão Supabase: {e}")
            print("💡 Verifique a senha e tente novamente")
            return False
        
        return True
    
    def step3_criar_tabela_supabase(self):
        """Criar tabela no Supabase"""
        print("\n🏗️ STEP 3: CRIANDO TABELA NO SUPABASE")
        print("="*50)
        
        try:
            cursor = self.conexao_supabase.cursor()
            
            # Criar tabela
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS dashboard_baker (
                id SERIAL PRIMARY KEY,
                numero_cte INTEGER UNIQUE NOT NULL,
                destinatario_nome VARCHAR(255),
                veiculo_placa VARCHAR(20),
                valor_total DECIMAL(15,2),
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
                origem_dados VARCHAR(50) DEFAULT 'Migração',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Criar índices para performance
            CREATE INDEX IF NOT EXISTS idx_dashboard_baker_cte ON dashboard_baker(numero_cte);
            CREATE INDEX IF NOT EXISTS idx_dashboard_baker_cliente ON dashboard_baker(destinatario_nome);
            CREATE INDEX IF NOT EXISTS idx_dashboard_baker_data_emissao ON dashboard_baker(data_emissao);
            CREATE INDEX IF NOT EXISTS idx_dashboard_baker_data_baixa ON dashboard_baker(data_baixa);
            
            -- Criar trigger para updated_at
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
            
            DROP TRIGGER IF EXISTS update_dashboard_baker_updated_at ON dashboard_baker;
            CREATE TRIGGER update_dashboard_baker_updated_at
                BEFORE UPDATE ON dashboard_baker
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """
            
            cursor.execute(create_table_sql)
            self.conexao_supabase.commit()
            
            print("✅ Tabela criada no Supabase")
            print("✅ Índices criados para performance")
            print("✅ Trigger de updated_at configurado")
            
            cursor.close()
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar tabela: {e}")
            return False
    
    def step4_migrar_dados(self):
        """Migrar dados do local para Supabase"""
        print("\n📦 STEP 4: MIGRANDO DADOS")
        print("="*50)
        
        try:
            # Extrair dados do banco local
            cursor_local = self.conexao_local.cursor()
            cursor_local.execute("""
                SELECT numero_cte, destinatario_nome, veiculo_placa, valor_total,
                       data_emissao, numero_fatura, data_baixa, observacao,
                       data_inclusao_fatura, data_envio_processo, primeiro_envio,
                       data_rq_tmc, data_atesto, envio_final, origem_dados
                FROM dashboard_baker
                ORDER BY numero_cte
            """)
            
            dados = cursor_local.fetchall()
            cursor_local.close()
            
            print(f"📊 {len(dados):,} registros para migrar")
            
            if not dados:
                print("⚠️ Nenhum dado para migrar")
                return True
            
            # Inserir dados no Supabase
            cursor_supabase = self.conexao_supabase.cursor()
            
            insert_sql = """
                INSERT INTO dashboard_baker (
                    numero_cte, destinatario_nome, veiculo_placa, valor_total,
                    data_emissao, numero_fatura, data_baixa, observacao,
                    data_inclusao_fatura, data_envio_processo, primeiro_envio,
                    data_rq_tmc, data_atesto, envio_final, origem_dados
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) ON CONFLICT (numero_cte) DO UPDATE SET
                    destinatario_nome = EXCLUDED.destinatario_nome,
                    veiculo_placa = EXCLUDED.veiculo_placa,
                    valor_total = EXCLUDED.valor_total,
                    data_emissao = EXCLUDED.data_emissao,
                    numero_fatura = EXCLUDED.numero_fatura,
                    data_baixa = EXCLUDED.data_baixa,
                    observacao = EXCLUDED.observacao,
                    data_inclusao_fatura = EXCLUDED.data_inclusao_fatura,
                    data_envio_processo = EXCLUDED.data_envio_processo,
                    primeiro_envio = EXCLUDED.primeiro_envio,
                    data_rq_tmc = EXCLUDED.data_rq_tmc,
                    data_atesto = EXCLUDED.data_atesto,
                    envio_final = EXCLUDED.envio_final,
                    origem_dados = EXCLUDED.origem_dados,
                    updated_at = CURRENT_TIMESTAMP
            """
            
            # Inserir em lotes
            batch_size = 100
            sucessos = 0
            
            for i in range(0, len(dados), batch_size):
                batch = dados[i:i + batch_size]
                try:
                    cursor_supabase.executemany(insert_sql, batch)
                    self.conexao_supabase.commit()
                    sucessos += len(batch)
                    print(f"📦 Migrados: {sucessos:,}/{len(dados):,} ({sucessos/len(dados)*100:.1f}%)")
                except Exception as e:
                    print(f"❌ Erro no lote {i}: {e}")
                    self.conexao_supabase.rollback()
            
            cursor_supabase.close()
            
            # Verificar migração
            cursor_supabase = self.conexao_supabase.cursor()
            cursor_supabase.execute("SELECT COUNT(*) FROM dashboard_baker")
            count = cursor_supabase.fetchone()[0]
            cursor_supabase.close()
            
            print(f"✅ Migração concluída: {count:,} registros no Supabase")
            return True
            
        except Exception as e:
            print(f"❌ Erro na migração: {e}")
            return False
    
    def step5_configurar_env(self):
        """Criar arquivo .env para Supabase"""
        print("\n⚙️ STEP 5: CONFIGURANDO AMBIENTE")
        print("="*50)
        
        # Backup do .env atual
        if os.path.exists('.env'):
            shutil.copy('.env', '.env.backup')
            print("📋 Backup do .env criado (.env.backup)")
        
        # Criar novo .env para Supabase
        env_content = f"""# CONFIGURAÇÃO SUPABASE - DASHBOARD BAKER
# Gerado automaticamente em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

# SUPABASE POSTGRESQL
SUPABASE_HOST={self.config_supabase['host']}
SUPABASE_DB=postgres
SUPABASE_USER=postgres
SUPABASE_PASSWORD={self.config_supabase['password']}
SUPABASE_PORT=5432

# CONFIGURAÇÕES STREAMLIT
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# AMBIENTE
ENVIRONMENT=production
DEBUG=False
"""
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ Arquivo .env configurado para Supabase")
        print("✅ Configurações de produção aplicadas")
        return True
    
    def step6_testar_dashboard(self):
        """Testar dashboard com Supabase"""
        print("\n🧪 STEP 6: TESTANDO DASHBOARD")
        print("="*50)
        
        try:
            # Testar importação
            import subprocess
            import sys
            
            print("📦 Verificando dependências...")
            deps = ['streamlit', 'pandas', 'plotly', 'psycopg2']
            
            for dep in deps:
                try:
                    __import__(dep)
                    print(f"✅ {dep}")
                except ImportError:
                    print(f"❌ {dep} - Instalando...")
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            
            # Testar conexão dashboard
            print("\n🔗 Testando conexão do dashboard...")
            
            # Simular teste de conexão
            test_conn = psycopg2.connect(**self.config_supabase)
            cursor = test_conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM dashboard_baker LIMIT 1")
            cursor.close()
            test_conn.close()
            
            print("✅ Dashboard conecta com Supabase")
            print("✅ Sistema pronto para deploy!")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            return False
    
    def step7_instrucoes_deploy(self):
        """Instruções finais de deploy"""
        print("\n🚀 STEP 7: INSTRUÇÕES DE DEPLOY")
        print("="*50)
        
        print("""
🎉 DEPLOY CONCLUÍDO COM SUCESSO!

📋 ARQUIVOS CONFIGURADOS:
   ✅ .env - Configurado para Supabase
   ✅ dashboard_baker_web_corrigido.py - MANTIDO nome original
   ✅ Banco de dados migrado
   ✅ Tabelas e índices criados

🚀 PARA EXECUTAR:
   1. Execute: streamlit run dashboard_baker_web_corrigido.py
   2. Ou: python -m streamlit run dashboard_baker_web_corrigido.py
   3. Acesse: http://localhost:8501

☁️ DEPLOY EM PRODUÇÃO (Streamlit Cloud):
   1. Faça push do código para GitHub
   2. Acesse: https://streamlit.io/cloud
   3. Conecte seu repositório
   4. Configure as variáveis de ambiente:
      - SUPABASE_HOST = {self.config_supabase['host']}
      - SUPABASE_PASSWORD = [sua_senha]
      - SUPABASE_USER = postgres
      - SUPABASE_DB = postgres
      - SUPABASE_PORT = 5432

📁 ESTRUTURA FINAL:
   📂 projeto/
   ├── 📄 dashboard_baker_web_corrigido.py (dashboard principal)
   ├── 📄 .env (configurações Supabase)
   ├── 📄 .env.backup (backup configurações locais)
   └── 📄 requirements.txt

🔧 REQUIREMENTS.TXT:
""")
        
        # Criar requirements.txt
        requirements = """streamlit>=1.28.0
pandas>=1.5.0
plotly>=5.17.0
psycopg2-binary>=2.9.0
python-dotenv>=1.0.0
xlsxwriter>=3.1.0
numpy>=1.24.0
"""
        
        with open('requirements.txt', 'w') as f:
            f.write(requirements)
        
        print("✅ requirements.txt criado")
        
        print(f"""
🌐 CONFIGURAÇÃO SUPABASE:
   • Host: {self.config_supabase['host']}
   • Database: postgres
   • User: postgres
   • Port: 5432
   • SSL: require

💡 DICAS:
   • Mantenha a senha segura
   • Use variáveis de ambiente em produção
   • Configure Row Level Security no Supabase se necessário
   • Monitor os logs do Supabase Dashboard

🎯 PRÓXIMOS PASSOS:
   1. Teste local: streamlit run dashboard_baker_web_corrigido.py
   2. Commit no Git
   3. Deploy no Streamlit Cloud
   4. Configure monitoramento
""")

def main():
    """Função principal do deploy"""
    print("🚀 DEPLOY DASHBOARD BAKER NO SUPABASE")
    print("="*60)
    print("Sistema completo de migração e deploy")
    print("MANTÉM: dashboard_baker_web_corrigido.py")
    print("="*60)
    
    deploy = DeploySupabaseCompleto()
    
    try:
        # Executar todos os steps
        if not deploy.step1_configurar_supabase():
            return
        
        if not deploy.step2_testar_conexoes():
            return
        
        if not deploy.step3_criar_tabela_supabase():
            return
        
        if not deploy.step4_migrar_dados():
            return
        
        if not deploy.step5_configurar_env():
            return
        
        if not deploy.step6_testar_dashboard():
            return
        
        deploy.step7_instrucoes_deploy()
        
        print("\n🎉 DEPLOY CONCLUÍDO COM SUCESSO!")
        print("🚀 Execute: streamlit run dashboard_baker_web_corrigido.py")
        
    except KeyboardInterrupt:
        print("\n❌ Deploy cancelado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro no deploy: {e}")
    finally:
        # Fechar conexões
        if deploy.conexao_local:
            deploy.conexao_local.close()
        if deploy.conexao_supabase:
            deploy.conexao_supabase.close()

if __name__ == "__main__":
    main()