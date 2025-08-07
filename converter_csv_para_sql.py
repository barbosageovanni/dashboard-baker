#!/usr/bin/env python3
"""
Converter CSV para comandos SQL - Dashboard Baker
"""
import pandas as pd
import os

def converter_csv_para_sql():
    """Converte CSV em comandos SQL para copiar/colar no Supabase"""
    
    # Procurar arquivo CSV
    arquivos_csv = [f for f in os.listdir('.') if f.endswith('.csv')]
    
    if not arquivos_csv:
        print("❌ Nenhum arquivo CSV encontrado")
        return
    
    arquivo_csv = arquivos_csv[0]
    print(f"📊 Processando: {arquivo_csv}")
    
    try:
        # Carregar CSV com encoding correto
        df = pd.read_csv(arquivo_csv, sep=';', encoding='cp1252', on_bad_lines='skip')
        print(f"✅ {len(df)} registros carregados")
        
        # Processar primeiros 10 registros (teste)
        comandos_sql = []
        comandos_sql.append("-- Limpar tabela existente")
        comandos_sql.append("DELETE FROM dashboard_baker;")
        comandos_sql.append("")
        comandos_sql.append("-- Inserir dados do CSV")
        
        processados = 0
        for idx, row in df.head(10).iterrows():  # Apenas 10 para teste
            try:
                # Processar CTE
                cte_str = str(row.get('CTE', ''))
                if not cte_str or cte_str == 'nan':
                    continue
                    
                numero_cte = int(float(cte_str))
                
                # Processar valor
                valor_str = str(row.get(' Total ', '0'))
                valor_total = 0
                try:
                    valor_total = float(valor_str.replace('R$', '').replace('.', '').replace(',', '.').strip())
                except:
                    valor_total = 0
                
                # Processar nomes (remover caracteres especiais)
                remetente = str(row.get('ï»¿Remetente - Nome', '')).strip()
                veiculo = str(row.get('Veí­culo - Placa', '')).strip()
                
                # Gerar comando SQL
                sql = f"""INSERT INTO dashboard_baker (numero_cte, destinatario_nome, veiculo_placa, valor_total, origem_dados) 
VALUES ({numero_cte}, '{remetente[:100]}', '{veiculo[:20]}', {valor_total}, 'CSV_Transpontual');"""
                
                comandos_sql.append(sql)
                processados += 1
                
            except Exception as e:
                print(f"⚠️ Erro linha {idx}: {e}")
                continue
        
        # Salvar arquivo SQL
        with open('inserir_dados.sql', 'w', encoding='utf-8') as f:
            f.write('\n'.join(comandos_sql))
        
        print(f"✅ {processados} comandos SQL gerados!")
        print(f"📁 Arquivo salvo: inserir_dados.sql")
        print()
        print("🔥 PRÓXIMO PASSO:")
        print("1. Abra o arquivo 'inserir_dados.sql'")
        print("2. Copie todo o conteúdo")
        print("3. Cole no SQL Editor do Supabase")
        print("4. Clique RUN")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    converter_csv_para_sql()