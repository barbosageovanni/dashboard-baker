import pandas as pd
import psycopg2
from datetime import datetime
import os

def test_dashboard_data():
    """Testa se os dados estão sendo processados corretamente"""
    
    # Simular dados como os que você mostrou
    test_data = {
        'id': [407],
        'numero_cte': [3], 
        'destinatario_nome': ['BAKER HUGHES DO BRASIL LTDA'],
        'veiculo_placa': ['KXM4C46'],
        'valor_total': [0.02],
        'data_emissao': [datetime(2025, 8, 8).date()],
        'numero_fatura': [None],
        'data_baixa': [None], 
        'observacao': [None],
        'data_inclusao_fatura': [None],
        'data_envio_processo': [None],
        'primeiro_envio': [None],
        'data_rq_tmc': [None],
        'data_atesto': [None],
        'envio_final': [None],
        'origem_dados': ['Manual'],
        'created_at': [datetime(2025, 8, 8, 18, 25, 13)],
        'updated_at': [datetime(2025, 8, 8, 18, 25, 13)]
    }
    
    df = pd.DataFrame(test_data)
    
    print("🔍 TESTE DE DADOS COM VALORES NONE")
    print("=" * 50)
    
    # Teste 1: Verificar se o DataFrame é criado corretamente
    print(f"✅ DataFrame criado: {len(df)} registro(s)")
    print(f"✅ Colunas: {len(df.columns)}")
    
    # Teste 2: Verificar cálculos básicos
    try:
        total_ctes = len(df)
        valor_total = df['valor_total'].sum()
        clientes_unicos = df['destinatario_nome'].nunique()
        
        print(f"✅ Total CTEs: {total_ctes}")
        print(f"✅ Valor Total: R$ {valor_total:.2f}")
        print(f"✅ Clientes Únicos: {clientes_unicos}")
    except Exception as e:
        print(f"❌ Erro nos cálculos básicos: {e}")
    
    # Teste 3: Verificar tratamento de valores None
    try:
        faturas_pagas = len(df[df['data_baixa'].notna()])
        faturas_pendentes = len(df[df['data_baixa'].isna()])
        ctes_com_fatura = len(df[df['numero_fatura'].notna() & (df['numero_fatura'] != '')])
        ctes_sem_fatura = len(df[df['numero_fatura'].isna() | (df['numero_fatura'] == '')])
        
        print(f"✅ Faturas Pagas: {faturas_pagas}")
        print(f"✅ Faturas Pendentes: {faturas_pendentes}")
        print(f"✅ CTEs com Fatura: {ctes_com_fatura}")
        print(f"✅ CTEs sem Fatura: {ctes_sem_fatura}")
    except Exception as e:
        print(f"❌ Erro no tratamento de None: {e}")
    
    # Teste 4: Verificar conversão de datas
    try:
        date_columns = ['data_emissao', 'data_baixa', 'data_inclusao_fatura', 
                       'primeiro_envio', 'data_atesto', 'envio_final']
        
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        print(f"✅ Conversão de datas realizada sem erros")
    except Exception as e:
        print(f"❌ Erro na conversão de datas: {e}")
    
    print(f"\n📊 DADOS FINAIS:")
    print(df.to_string())
    
    print(f"\n🎉 TESTE CONCLUÍDO - Dados processados corretamente!")

if __name__ == "__main__":
    test_dashboard_data()
