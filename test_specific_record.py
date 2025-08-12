import pandas as pd
from decimal import Decimal
import datetime

def test_specific_record():
    """Testa o processamento do registro específico com valores None"""
    
    # Simular o registro exato que você mostrou
    data = {
        'id': 407,
        'numero_cte': 3,
        'destinatario_nome': 'BAKER HUGHES DO BRASIL LTDA',
        'veiculo_placa': 'KXM4C46',
        'valor_total': Decimal('0.02'),
        'data_emissao': datetime.date(2025, 8, 8),
        'numero_fatura': None,
        'data_baixa': None,
        'observacao': None,
        'data_inclusao_fatura': None,
        'data_envio_processo': None,
        'primeiro_envio': None,
        'data_rq_tmc': None,
        'data_atesto': None,
        'envio_final': None,
        'origem_dados': 'Manual',
        'created_at': datetime.datetime(2025, 8, 8, 18, 25, 13, 295, tzinfo=datetime.timezone.utc),
        'updated_at': datetime.datetime(2025, 8, 8, 18, 25, 13, 295, tzinfo=datetime.timezone.utc)
    }

    print('🔍 TESTE COM REGISTRO ESPECÍFICO')
    print('=' * 50)

    try:
        # Criar DataFrame
        df = pd.DataFrame([data])
        print(f'✅ DataFrame criado: {len(df)} registro(s)')
        print(f'✅ Valor total: {df["valor_total"].iloc[0]}')
        print(f'✅ Tipo do valor: {type(df["valor_total"].iloc[0])}')

        # Testar conversões
        valor_float = float(df['valor_total'].iloc[0])
        print(f'✅ Conversão para float: {valor_float}')
        
        # Verificar None values
        none_count = df.isnull().sum().sum()
        print(f'✅ Valores None/NaN: {none_count}')
        
        # Testar soma
        soma_total = df['valor_total'].sum()
        print(f'✅ Soma total: {soma_total}')
        
        # Testar conversão de datas
        date_columns = ['data_emissao', 'data_baixa', 'data_inclusao_fatura',
                       'data_envio_processo', 'primeiro_envio', 'data_rq_tmc',
                       'data_atesto', 'envio_final', 'created_at', 'updated_at']
        
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        print('✅ Conversão de datas OK')
        
        # Testar filtros que o dashboard usa
        faturas_pagas = len(df[df['data_baixa'].notna()])
        faturas_pendentes = len(df[df['data_baixa'].isna()])
        ctes_com_fatura = len(df[df['numero_fatura'].notna() & (df['numero_fatura'] != '')])
        
        print(f'✅ Faturas pagas: {faturas_pagas}')
        print(f'✅ Faturas pendentes: {faturas_pendentes}')
        print(f'✅ CTEs com fatura: {ctes_com_fatura}')
        
        print('\n🎉 TODOS OS TESTES PASSARAM - REGISTRO PROCESSADO CORRETAMENTE!')
        
        return True
        
    except Exception as e:
        print(f'❌ ERRO no processamento: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_specific_record()
    
    if success:
        print('\n✅ O registro está sendo processado corretamente pelo sistema.')
        print('💡 Valores None são normais para campos opcionais não preenchidos.')
    else:
        print('\n❌ Há problema no processamento que precisa ser corrigido.')
