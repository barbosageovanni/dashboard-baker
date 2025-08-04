#!/usr/bin/env python3
"""
Popular banco Supabase com dados do CSV
"""
import pandas as pd
import psycopg2
from datetime import datetime
import os

# SUAS CREDENCIAIS DO SUPABASE
SUPABASE_CONFIG = {
    'host': 'db.lijtncazuwnbydeqtoyz.supabase.co',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'Ariam953#',
    'port': 5432,
    'sslmode': 'require'
}

def popular_banco_supabase():
    """Popular banco Supabase com dados do CSV"""
    
    # Procurar arquivo CSV
    arquivos_csv = [f for f in os.listdir('.') if f.endswith('.csv')]
    
    if not arquivos_csv:
        print("❌ Nenhum arquivo CSV encontrado na pasta")
        return False
    
    print(f"📁 Arquivos CSV encontrados: {arquivos_csv}")
    arquivo_csv = arquivos_csv[0]  # Usar primeiro CSV encontrado
    
    try:
        # Carregar CSV
        print(f"📊 Carregando {arquivo_csv}...")
        df = pd.read_csv(arquivo_csv, sep=';', encoding='cp1252', on_bad_lines='skip')
        
        print(f"✅ CSV carregado: {len(df)} registros")
        print(f"📋 Colunas encontradas: {list(df.columns)}")
        
        # Conectar ao Supabase
        print("🔌 Conectando ao Supabase...")
        conn = psycopg2.connect(**SUPABASE_CONFIG)
        cursor = conn.cursor()
        
        # Limpar tabela existente
        cursor.execute("DELETE FROM dashboard_baker")
        print("🗑️ Tabela limpa")
        
        # Processar e inserir dados
        inseridos = 0
        erros = 0
        
        for idx, row in df.iterrows():
            try:
                # Extrair dados do CSV
                numero_cte = int(row.get('Número Cte', 0)) if pd.notna(row.get('Número Cte')) else 0
                if numero_cte == 0:
                    continue
                
                # Processar valor total
                valor_str = str(row.get(' Total ', '0'))
                valor_total = 0
                try:
                    valor_total = float(valor_str.replace('R$', '').replace('.', '').replace(',', '.').strip())
                except:
                    valor_total = 0
                
                # Preparar dados
                dados = (
                    numero_cte,
                    str(row.get('Destinatário - Nome', '')).strip() if pd.notna(row.get('Destinatário - Nome')) else '',
                    str(row.get('Veículo - Placa', '')).strip() if pd.notna(row.get('Veículo - Placa')) else '',
                    valor_total,
                    pd.to_datetime(row.get('Data emissão Cte'), format='%d/%b/%y', errors='coerce'),
                    str(row.get('Fatura', '')).strip() if pd.notna(row.get('Fatura')) else '',
                    pd.to_datetime(row.get('Data baixa'), format='%d/%b/%y', errors='coerce'),
                    str(row.get('OBSERVAÇÃO', '')).strip() if pd.notna(row.get('OBSERVAÇÃO')) else '',
                    pd.to_datetime(row.get('Data INCLUSÃO Fatura Bsoft'), format='%d/%b/%y', errors='coerce'),
                    pd.to_datetime(row.get('Data Envio do processo Faturamento'), format='%d/%b/%y', errors='coerce'),
                    pd.to_datetime(row.get('1º Envio'), format='%d/%b/%y', errors='coerce'),
                    pd.to_datetime(row.get('Data RQ/TMC'), format='%d/%b/%y', errors='coerce'),
                    pd.to_datetime(row.get('Data do atesto'), format='%d/%b/%y', errors='coerce'),
                    pd.to_datetime(row.get('Envio final'), format='%d/%b/%y', errors='coerce'),
                    'CSV_Supabase'
                )
                
                cursor.execute("""
                    INSERT INTO dashboard_baker (
                        numero_cte, destinatario_nome, veiculo_placa, valor_total,
                        data_emissao, numero_fatura, data_baixa, observacao,
                        data_inclusao_fatura, data_envio_processo, primeiro_envio,
                        data_rq_tmc, data_atesto, envio_final, origem_dados
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (numero_cte) DO NOTHING
                """, dados)
                
                inseridos += 1
                
                if inseridos % 100 == 0:
                    print(f"📊 Processados: {inseridos}")
                
            except Exception as e:
                erros += 1
                if erros <= 5:  # Mostrar só os primeiros 5 erros
                    print(f"⚠️ Erro na linha {idx}: {e}")
                continue
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ {inseridos} registros inseridos no Supabase!")
        print(f"⚠️ {erros} erros ignorados")
        return True
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

if __name__ == "__main__":
    popular_banco_supabase()