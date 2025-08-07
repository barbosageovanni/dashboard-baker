#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 POPULAR SUPABASE COM DADOS DO CSV
Script para carregar/atualizar dados do CSV no Supabase
"""

import pandas as pd
import psycopg2
from datetime import datetime
import os
import glob

class PopularSupabaseCSV:
    """Classe para popular Supabase com dados do CSV"""
    
    def __init__(self):
        self.config_supabase = None
        self.conexao = None
        
    def carregar_configuracao(self):
        """Carrega configuração do Supabase do .env"""
        if not os.path.exists('.env'):
            print("❌ Arquivo .env não encontrado")
            print("💡 Execute primeiro: python deploy_supabase_completo.py")
            return False
        
        # Carregar do .env
        config = {}
        with open('.env', 'r') as f:
            for linha in f:
                if '=' in linha and not linha.startswith('#'):
                    chave, valor = linha.strip().split('=', 1)
                    config[chave] = valor
        
        # Configurar conexão
        self.config_supabase = {
            'host': config.get('SUPABASE_HOST'),
            'database': config.get('SUPABASE_DB', 'postgres'),
            'user': config.get('SUPABASE_USER', 'postgres'),
            'password': config.get('SUPABASE_PASSWORD'),
            'port': int(config.get('SUPABASE_PORT', '5432')),
            'sslmode': 'require'
        }
        
        if not all([self.config_supabase['host'], self.config_supabase['password']]):
            print("❌ Configuração incompleta no .env")
            return False
        
        print(f"✅ Configuração carregada: {self.config_supabase['host']}")
        return True
    
    def conectar(self):
        """Conecta com Supabase"""
        try:
            self.conexao = psycopg2.connect(**self.config_supabase)
            print("✅ Conectado ao Supabase")
            return True
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return False
    
    def encontrar_arquivo_csv(self):
        """Encontra arquivo CSV na pasta"""
        # Padrões de busca
        padroes = [
            '*baker*.csv',
            '*faturamento*.csv', 
            '*relatorio*.csv',
            '*.csv'
        ]
        
        arquivos_encontrados = []
        for padrao in padroes:
            arquivos = glob.glob(padrao)
            arquivos_encontrados.extend(arquivos)
        
        # Remover duplicatas e ordenar por data de modificação
        arquivos_unicos = list(set(arquivos_encontrados))
        arquivos_unicos.sort(key=os.path.getmtime, reverse=True)
        
        if not arquivos_unicos:
            print("❌ Nenhum arquivo CSV encontrado")
            return None
        
        print("📁 Arquivos CSV encontrados:")
        for i, arquivo in enumerate(arquivos_unicos):
            tamanho = os.path.getsize(arquivo) / 1024
            mod_time = datetime.fromtimestamp(os.path.getmtime(arquivo))
            print(f"   [{i+1}] {arquivo} ({tamanho:.1f} KB, {mod_time.strftime('%d/%m/%Y %H:%M')})")
        
        # Selecionar arquivo
        if len(arquivos_unicos) == 1:
            return arquivos_unicos[0]
        
        try:
            escolha = int(input(f"\nEscolha um arquivo (1-{len(arquivos_unicos)}): ")) - 1
            return arquivos_unicos[escolha]
        except (ValueError, IndexError):
            print("❌ Seleção inválida")
            return None
    
    def processar_csv(self, arquivo_csv):
        """Processa arquivo CSV e converte para formato do banco"""
        print(f"📊 Processando: {arquivo_csv}")
        
        try:
            # Tentar diferentes encodings
            encodings = ['cp1252', 'utf-8', 'iso-8859-1', 'latin1']
            separadores = [';', ',', '\t']
            
            df = None
            for encoding in encodings:
                for sep in separadores:
                    try:
                        df_test = pd.read_csv(arquivo_csv, sep=sep, encoding=encoding)
                        if len(df_test.columns) > 5:  # CSV válido tem várias colunas
                            df = df_test
                            print(f"✅ CSV carregado: {encoding}, separador '{sep}'")
                            break
                    except:
                        continue
                if df is not None:
                    break
            
            if df is None:
                print("❌ Não foi possível ler o CSV")
                return None
            
            print(f"📋 {len(df)} registros encontrados, {len(df.columns)} colunas")
            
            # Mapear colunas do CSV para o banco
            mapeamento_colunas = {
                # Possíveis nomes no CSV : nome no banco
                'Número Cte': 'numero_cte',
                'Numero Cte': 'numero_cte', 
                'Destinatário - Nome': 'destinatario_nome',
                'Destinatario Nome': 'destinatario_nome',
                'Cliente': 'destinatario_nome',
                'Veículo - Placa': 'veiculo_placa',
                'Veiculo Placa': 'veiculo_placa',
                'Placa': 'veiculo_placa',
                ' Total ': 'valor_total',
                'Valor Total': 'valor_total',
                'Total': 'valor_total',
                'Data emissão Cte': 'data_emissao',
                'Data emissao Cte': 'data_emissao',
                'Data Emissao': 'data_emissao',
                'Fatura': 'numero_fatura',
                'Numero Fatura': 'numero_fatura',
                'Data baixa': 'data_baixa',
                'Data Baixa': 'data_baixa',
                'OBSERVAÇÃO': 'observacao',
                'Observacao': 'observacao',
                'Observacoes': 'observacao',
                'Data INCLUSÃO Fatura Bsoft': 'data_inclusao_fatura',
                'Data inclusao Fatura': 'data_inclusao_fatura',
                'Data Envio do processo Faturamento': 'data_envio_processo',
                '1º Envio': 'primeiro_envio',
                'Primeiro Envio': 'primeiro_envio',
                'Data RQ/TMC': 'data_rq_tmc',
                'Data do atesto': 'data_atesto',
                'Data Atesto': 'data_atesto',
                'Envio final': 'envio_final',
                'Envio Final': 'envio_final'
            }
            
            # Limpar nomes das colunas
            df.columns = df.columns.str.strip()
            
            # Renomear colunas
            for col_csv, col_banco in mapeamento_colunas.items():
                if col_csv in df.columns:
                    df = df.rename(columns={col_csv: col_banco})
            
            # Verificar colunas obrigatórias
            if 'numero_cte' not in df.columns:
                print("❌ Coluna 'numero_cte' não encontrada")
                print("📋 Colunas disponíveis:", list(df.columns))
                return None
            
            # Processar valores monetários
            if 'valor_total' in df.columns:
                df['valor_total'] = (
                    df['valor_total']
                    .astype(str)
                    .str.replace('R$', '', regex=False)
                    .str.replace('.', '', regex=False)
                    .str.replace(',', '.', regex=False)
                    .str.strip()
                )
                df['valor_total'] = pd.to_numeric(df['valor_total'], errors='coerce')
            
            # Processar datas
            colunas_data = ['data_emissao', 'data_baixa', 'data_inclusao_fatura',
                           'data_envio_processo', 'primeiro_envio', 'data_rq_tmc',
                           'data_atesto', 'envio_final']
            
            for col in colunas_data:
                if col in df.columns:
                    # Tentar diferentes formatos de data
                    df[col] = pd.to_datetime(df[col], format='%d/%b/%y', errors='coerce')
                    if df[col].isna().all():
                        df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce')
                    if df[col].isna().all():
                        df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Adicionar coluna origem_dados
            df['origem_dados'] = 'CSV_Import'
            
            print(f"✅ CSV processado: {len(df)} registros válidos")
            return df
            
        except Exception as e:
            print(f"❌ Erro ao processar CSV: {e}")
            return None
    
    def inserir_dados(self, df):
        """Insere dados no Supabase"""
        if df is None or df.empty:
            print("❌ Nenhum dado para inserir")
            return False
        
        print(f"💾 Inserindo {len(df)} registros no Supabase...")
        
        try:
            cursor = self.conexao.cursor()
            
            # Preparar SQL de inserção
            colunas_banco = ['numero_cte', 'destinatario_nome', 'veiculo_placa', 'valor_total',
                           'data_emissao', 'numero_fatura', 'data_baixa', 'observacao',
                           'data_inclusao_fatura', 'data_envio_processo', 'primeiro_envio',
                           'data_rq_tmc', 'data_atesto', 'envio_final', 'origem_dados']
            
            # Garantir que todas as colunas existem no DataFrame
            for col in colunas_banco:
                if col not in df.columns:
                    df[col] = None
            
            # SQL com UPSERT (INSERT ... ON CONFLICT)
            placeholders = ', '.join(['%s'] * len(colunas_banco))
            update_set = ', '.join([f"{col} = EXCLUDED.{col}" for col in colunas_banco if col != 'numero_cte'])
            
            insert_sql = f"""
                INSERT INTO dashboard_baker ({', '.join(colunas_banco)})
                VALUES ({placeholders})
                ON CONFLICT (numero_cte) DO UPDATE SET
                {update_set},
                updated_at = CURRENT_TIMESTAMP
            """
            
            # Preparar dados
            dados_para_inserir = []
            sucessos = 0
            erros = 0
            
            for _, row in df.iterrows():
                try:
                    # Converter None para NULL e tratar tipos
                    valores = []
                    for col in colunas_banco:
                        valor = row[col]
                        if pd.isna(valor):
                            valores.append(None)
                        elif col == 'valor_total' and valor is not None:
                            valores.append(float(valor))
                        elif col == 'numero_cte' and valor is not None:
                            valores.append(int(valor))
                        else:
                            valores.append(valor)
                    
                    dados_para_inserir.append(tuple(valores))
                    sucessos += 1
                    
                except Exception as e:
                    print(f"⚠️ Erro na linha {row.name}: {e}")
                    erros += 1
            
            # Inserir em lotes
            batch_size = 100
            total_inserido = 0
            
            for i in range(0, len(dados_para_inserir), batch_size):
                batch = dados_para_inserir[i:i + batch_size]
                try:
                    cursor.executemany(insert_sql, batch)
                    self.conexao.commit()
                    total_inserido += len(batch)
                    print(f"📦 Progresso: {total_inserido}/{len(dados_para_inserir)} ({total_inserido/len(dados_para_inserir)*100:.1f}%)")
                except Exception as e:
                    print(f"❌ Erro no lote {i//batch_size + 1}: {e}")
                    self.conexao.rollback()
            
            cursor.close()
            
            # Verificar resultado final
            cursor = self.conexao.cursor()
            cursor.execute("SELECT COUNT(*) FROM dashboard_baker")
            total_final = cursor.fetchone()[0]
            cursor.close()
            
            print(f"✅ Inserção concluída!")
            print(f"📊 Total no banco: {total_final:,} registros")
            print(f"📦 Processados: {sucessos} sucessos, {erros} erros")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na inserção: {e}")
            return False
    
    def executar(self):
        """Executa o processo completo"""
        print("📊 POPULAR SUPABASE COM DADOS CSV")
        print("="*50)
        
        # Carregar configuração
        if not self.carregar_configuracao():
            return False
        
        # Conectar
        if not self.conectar():
            return False
        
        # Encontrar CSV
        arquivo_csv = self.encontrar_arquivo_csv()
        if not arquivo_csv:
            return False
        
        # Processar CSV
        df = self.processar_csv(arquivo_csv)
        if df is None:
            return False
        
        # Inserir dados
        return self.inserir_dados(df)

def main():
    """Função principal"""
    try:
        popular = PopularSupabaseCSV()
        sucesso = popular.executar()
        
        if sucesso:
            print("\n🎉 DADOS CARREGADOS COM SUCESSO!")
            print("🚀 Execute o dashboard: streamlit run dashboard_baker_web_corrigido.py")
        else:
            print("\n❌ Falha no carregamento dos dados")
            
    except KeyboardInterrupt:
        print("\n❌ Operação cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")

if __name__ == "__main__":
    main()