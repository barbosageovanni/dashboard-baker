#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inicializador de Banco para Deploy - Dashboard Baker
Cria tabela e estrutura necessária automaticamente
"""

import psycopg2
import os
from datetime import datetime

def carregar_config_deploy():
    """Carrega configuração para deploy"""
    # Tentar Railway primeiro
    if os.getenv('PGHOST'):
        return {
            'host': os.getenv('PGHOST'),
            'database': os.getenv('PGDATABASE'), 
            'user': os.getenv('PGUSER'),
            'password': os.getenv('PGPASSWORD'),
            'port': int(os.getenv('PGPORT', '5432')),
            'sslmode': 'require'
        }
    
    # Tentar Supabase
    elif os.getenv('SUPABASE_HOST'):
        return {
            'host': os.getenv('SUPABASE_HOST'),
            'database': os.getenv('SUPABASE_DB', 'postgres'),
            'user': os.getenv('SUPABASE_USER', 'postgres'), 
            'password': os.getenv('SUPABASE_PASSWORD'),
            'port': int(os.getenv('SUPABASE_PORT', '5432')),
            'sslmode': 'require'
        }
    
    # Local fallback
    else:
        return {
            'host': 'localhost',
            'database': 'dashboard_baker',
            'user': 'postgres',
            'password': os.getenv('LOCAL_DB_PASSWORD', 'senha123'),
            'port': 5432
        }

def criar_tabela_dashboard_baker(cursor):
    """Cria a tabela principal do dashboard"""
    sql_create_table = """
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
        origem_dados VARCHAR(50) DEFAULT 'Sistema',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Índices para performance
    CREATE INDEX IF NOT EXISTS idx_dashboard_baker_numero_cte ON dashboard_baker(numero_cte);
    CREATE INDEX IF NOT EXISTS idx_dashboard_baker_destinatario ON dashboard_baker(destinatario_nome);
    CREATE INDEX IF NOT EXISTS idx_dashboard_baker_data_emissao ON dashboard_baker(data_emissao);
    CREATE INDEX IF NOT EXISTS idx_dashboard_baker_data_baixa ON dashboard_baker(data_baixa);
    
    -- Trigger para updated_at
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
    
    cursor.execute(sql_create_table)
    print("✅ Tabela dashboard_baker criada/verificada com sucesso")

def inserir_dados_exemplo(cursor):
    """Insere alguns dados de exemplo se a tabela estiver vazia"""
    # Verificar se já tem dados
    cursor.execute("SELECT COUNT(*) FROM dashboard_baker")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("📝 Inserindo dados de exemplo...")
        
        dados_exemplo = [
            (22001, 'EMPRESA TESTE LTDA', 'ABC1234', 1500.00, '2024-01-15', 'FAT001', None, 'Dados de exemplo', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-15', '2024-01-20', None, 'Sistema'),
            (22002, 'CLIENTE DEMO S/A', 'DEF5678', 2300.50, '2024-01-20', 'FAT002', '2024-02-15', 'Exemplo concluído', '2024-01-21', '2024-01-22', '2024-01-23', '2024-01-20', '2024-01-25', '2024-01-26', 'Sistema'),
            (22003, 'TRANSPORTES EXEMPLO', 'GHI9012', 1800.75, '2024-01-25', None, None, 'Processo em andamento', None, None, None, '2024-01-25', None, None, 'Sistema')
        ]
        
        sql_insert = """
        INSERT INTO dashboard_baker (
            numero_cte, destinatario_nome, veiculo_placa, valor_total, data_emissao, 
            numero_fatura, data_baixa, observacao, data_inclusao_fatura, data_envio_processo,
            primeiro_envio, data_rq_tmc, data_atesto, envio_final, origem_dados
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        for dados in dados_exemplo:
            cursor.execute(sql_insert, dados)
        
        print(f"✅ {len(dados_exemplo)} registros de exemplo inseridos")
    else:
        print(f"ℹ️ Tabela já contém {count} registros")

def main():
    """Função principal de inicialização"""
    print("🚀 Inicializando banco de dados para deploy...")
    print(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    try:
        # Carregar configuração
        config = carregar_config_deploy()
        print(f"🔗 Conectando em: {config['host']}:{config['port']}")
        
        # Conectar ao banco
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Criar estrutura
        criar_tabela_dashboard_baker(cursor)
        
        # Inserir dados de exemplo se necessário
        inserir_dados_exemplo(cursor)
        
        # Confirmar alterações
        conn.commit()
        
        # Verificar resultado final
        cursor.execute("SELECT COUNT(*) FROM dashboard_baker")
        total_registros = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print()
        print("=" * 50)
        print("✅ INICIALIZAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"📊 Total de registros: {total_registros}")
        print("🚀 Dashboard pronto para usar!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na inicialização: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)