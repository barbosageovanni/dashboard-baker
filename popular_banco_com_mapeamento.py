#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para POPULAR o banco PostgreSQL usando mapeamento correto das colunas
Baseado na análise real do arquivo CSV
"""

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import os
import re

# Configuração do banco PostgreSQL  
DB_CONFIG = {
    'host': 'localhost',
    'database': 'dashboard_baker',
    'user': 'postgres',
    'password': 'senha123',  # Altere conforme sua configuração
    'port': 5432
}

def carregar_configuracao_env():
    """Carrega configuração do arquivo .env se existir"""
    if os.path.exists('.env'):
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                for linha in f:
                    linha = linha.strip()
                    if linha and not linha.startswith('#') and '=' in linha:
                        chave, valor = linha.split('=', 1)
                        if chave == 'DB_HOST':
                            DB_CONFIG['host'] = valor
                        elif chave == 'DB_NAME':
                            DB_CONFIG['database'] = valor
                        elif chave == 'DB_USER':
                            DB_CONFIG['user'] = valor
                        elif chave == 'DB_PASSWORD':
                            DB_CONFIG['password'] = valor
                        elif chave == 'DB_PORT':
                            DB_CONFIG['port'] = int(valor)
        except:
            pass

def conectar_banco():
    """Conecta ao banco de dados PostgreSQL"""
    try:
        carregar_configuracao_env()
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Conectado ao banco PostgreSQL")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None

def carregar_mapeamento():
    """Carrega o mapeamento de colunas identificado"""
    
    # Verificar se existe arquivo de mapeamento
    if os.path.exists('mapeamento_colunas.txt'):
        try:
            with open('mapeamento_colunas.txt', 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Extrair mapeamento do arquivo
            if 'MAPEAMENTO = {' in conteudo:
                inicio = conteudo.find('MAPEAMENTO = {')
                fim = conteudo.find('}', inicio) + 1
                mapeamento_str = conteudo[inicio:fim]
                
                # Parse básico do mapeamento
                mapeamento = {}
                linhas = mapeamento_str.split('\n')
                for linha in linhas:
                    if ':' in linha and "'" in linha:
                        try:
                            partes = linha.split(':')
                            chave = partes[0].strip().replace("'", "").replace("MAPEAMENTO = {", "").strip()
                            valor = partes[1].strip().replace("'", "").replace(",", "").strip()
                            if chave and valor:
                                mapeamento[chave] = valor
                        except:
                            continue
                
                print("✅ Mapeamento carregado do arquivo")
                return mapeamento
        except Exception as e:
            print(f"⚠️ Erro ao carregar mapeamento: {e}")
    
    # Mapeamento padrão se não encontrar arquivo
    print("⚠️ Usando mapeamento padrão - Execute analisar_arquivo_real.py primeiro")
    return {}

def carregar_csv_com_mapeamento():
    """Carrega o arquivo CSV usando o mapeamento correto"""
    
    arquivo = "Status Faturamento   Ctes vs Faturas vs Atestos.csv"
    
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        
        # Procurar por outros arquivos CSV
        arquivos_csv = [f for f in os.listdir('.') if f.endswith('.csv')]
        if arquivos_csv:
            print("\n📋 Arquivos CSV encontrados:")
            for i, arq in enumerate(arquivos_csv, 1):
                print(f"   {i}. {arq}")
            
            try:
                escolha = int(input(f"\nEscolha o arquivo (1-{len(arquivos_csv)}): ")) - 1
                if 0 <= escolha < len(arquivos_csv):
                    arquivo = arquivos_csv[escolha]
                else:
                    return None, None
            except:
                return None, None
        else:
            return None, None
    
    print(f"📂 Carregando: {arquivo}")
    
    # Tentar diferentes encodings
    encodings = ['utf-8', 'cp1252', 'latin1', 'iso-8859-1']
    
    df = None
    for encoding in encodings:
        try:
            df = pd.read_csv(arquivo, sep=';', encoding=encoding, on_bad_lines='skip')
            print(f"✅ Carregado com encoding: {encoding}")
            break
        except Exception as e:
            continue
    
    if df is None:
        print("❌ Não foi possível carregar o arquivo")
        return None, None
    
    # Limpar nomes das colunas
    df.columns = df.columns.str.strip()
    
    print(f"📊 Total de registros: {len(df)}")
    print(f"📋 Total de colunas: {len(df.columns)}")
    
    return df, arquivo

def identificar_colunas_automaticamente(df):
    """Identifica colunas automaticamente se não houver mapeamento"""
    
    print("🔍 Identificando colunas automaticamente...")
    
    mapeamento = {}
    
    # Identificar coluna CTE
    for coluna in df.columns:
        col_lower = coluna.lower()
        if any(palavra in col_lower for palavra in ['cte', 'número', 'numero', 'conhecimento']):
            # Verificar se tem valores numéricos
            valores_numericos = 0
            valores_totais = df[coluna].notna().sum()
            
            if valores_totais > 0:
                for valor in df[coluna].dropna().head(10):
                    try:
                        int(valor)
                        valores_numericos += 1
                    except:
                        pass
                
                if valores_numericos > valores_totais * 0.8:  # 80% dos valores são números
                    mapeamento['numero_cte'] = coluna
                    print(f"   ✅ CTE: '{coluna}'")
                    break
    
    # Identificar outras colunas importantes
    for coluna in df.columns:
        col_lower = coluna.lower()
        
        if 'destinat' in col_lower and 'destinatario' not in mapeamento:
            mapeamento['destinatario'] = coluna
            print(f"   ✅ Destinatário: '{coluna}'")
        
        elif 'total' in col_lower and 'valor' not in mapeamento:
            mapeamento['valor'] = coluna
            print(f"   ✅ Valor: '{coluna}'")
        
        elif 'emiss' in col_lower and 'data_emissao' not in mapeamento:
            mapeamento['data_emissao'] = coluna
            print(f"   ✅ Data Emissão: '{coluna}'")
        
        elif 'fatura' in col_lower and 'data' not in col_lower and 'numero_fatura' not in mapeamento:
            mapeamento['numero_fatura'] = coluna
            print(f"   ✅ Fatura: '{coluna}'")
        
        elif 'baixa' in col_lower and 'data_baixa' not in mapeamento:
            mapeamento['data_baixa'] = coluna
            print(f"   ✅ Data Baixa: '{coluna}'")
        
        elif ('veículo' in col_lower or 'veiculo' in col_lower or 'placa' in col_lower) and 'veiculo' not in mapeamento:
            mapeamento['veiculo'] = coluna
            print(f"   ✅ Veículo: '{coluna}'")
        
        elif ('observ' in col_lower or 'obs' in col_lower) and 'observacao' not in mapeamento:
            mapeamento['observacao'] = coluna
            print(f"   ✅ Observação: '{coluna}'")
    
    return mapeamento

def processar_valor_monetario(valor):
    """Processa valores monetários brasileiros"""
    if pd.isna(valor):
        return 0.0
    
    try:
        valor_str = str(valor).strip()
        
        # Remover símbolos monetários
        valor_str = re.sub(r'[R$\s]', '', valor_str)
        
        # Processar formato brasileiro
        if ',' in valor_str and '.' in valor_str:
            # Formato: 1.234.567,89
            valor_str = valor_str.replace('.', '').replace(',', '.')
        elif ',' in valor_str:
            # Formato: 1234,89
            valor_str = valor_str.replace(',', '.')
        
        return float(valor_str)
    except:
        return 0.0

def processar_data_brasileira(data_str):
    """Processa datas no formato brasileiro"""
    if pd.isna(data_str):
        return None
    
    try:
        data_str = str(data_str).strip()
        
        if not data_str or data_str.lower() in ['nan', 'nat', '']:
            return None
        
        # Formatos possíveis
        formatos = [
            '%d/%b/%y',    # 25/jul/24
            '%d/%m/%Y',    # 25/07/2024
            '%d-%m-%Y',    # 25-07-2024
            '%Y-%m-%d',    # 2024-07-25
            '%d/%m/%y'     # 25/07/24
        ]
        
        for formato in formatos:
            try:
                return datetime.strptime(data_str, formato).date()
            except:
                continue
        
        return None
    except:
        return None

def mapear_dados_para_banco(df, mapeamento):
    """Mapeia os dados do CSV para a estrutura do banco"""
    
    if not mapeamento.get('numero_cte'):
        print("❌ Coluna CTE não identificada no mapeamento!")
        return []
    
    print(f"🔄 Mapeando dados usando as colunas identificadas...")
    print(f"📋 Mapeamento usado:")
    for campo, coluna in mapeamento.items():
        print(f"   {campo:20} -> '{coluna}'")
    
    registros = []
    erros_cte = 0
    
    for index, row in df.iterrows():
        try:
            # Extrair número CTE
            numero_cte_raw = row[mapeamento['numero_cte']]
            
            if pd.isna(numero_cte_raw):
                erros_cte += 1
                continue
            
            # Converter para int
            try:
                numero_cte = int(numero_cte_raw)
                if numero_cte <= 0:
                    erros_cte += 1
                    continue
            except:
                erros_cte += 1
                continue
            
            # Criar registro
            registro = {
                'numero_cte': numero_cte,
                'destinatario_nome': None,
                'veiculo_placa': None,
                'valor_total': 0.0,
                'data_emissao': None,
                'numero_fatura': None,
                'data_baixa': None,
                'observacao': None,
                'data_inclusao_fatura': None,
                'data_envio_processo': None,
                'primeiro_envio': None,
                'data_rq_tmc': None,
                'data_atesto': None,
                'envio_final': None,
                'origem_dados': 'CSV_MAPEADO'
            }
            
            # Mapear campos disponíveis
            if 'destinatario' in mapeamento and mapeamento['destinatario'] in row:
                dest = row[mapeamento['destinatario']]
                registro['destinatario_nome'] = str(dest).strip() if pd.notna(dest) else None
            
            if 'veiculo' in mapeamento and mapeamento['veiculo'] in row:
                vei = row[mapeamento['veiculo']]
                registro['veiculo_placa'] = str(vei).strip() if pd.notna(vei) else None
            
            if 'valor' in mapeamento and mapeamento['valor'] in row:
                registro['valor_total'] = processar_valor_monetario(row[mapeamento['valor']])
            
            if 'data_emissao' in mapeamento and mapeamento['data_emissao'] in row:
                registro['data_emissao'] = processar_data_brasileira(row[mapeamento['data_emissao']])
            
            if 'numero_fatura' in mapeamento and mapeamento['numero_fatura'] in row:
                fat = row[mapeamento['numero_fatura']]
                registro['numero_fatura'] = str(fat).strip() if pd.notna(fat) else None
            
            if 'data_baixa' in mapeamento and mapeamento['data_baixa'] in row:
                registro['data_baixa'] = processar_data_brasileira(row[mapeamento['data_baixa']])
            
            if 'observacao' in mapeamento and mapeamento['observacao'] in row:
                obs = row[mapeamento['observacao']]
                registro['observacao'] = str(obs).strip() if pd.notna(obs) else None
            
            # Tentar mapear outras datas automaticamente
            for col in df.columns:
                col_lower = col.lower()
                if 'inclusão' in col_lower and 'fatura' in col_lower:
                    registro['data_inclusao_fatura'] = processar_data_brasileira(row[col])
                elif 'envio' in col_lower and 'processo' in col_lower:
                    registro['data_envio_processo'] = processar_data_brasileira(row[col])
                elif '1º' in col and 'envio' in col_lower:
                    registro['primeiro_envio'] = processar_data_brasileira(row[col])
                elif 'rq' in col_lower or 'tmc' in col_lower:
                    registro['data_rq_tmc'] = processar_data_brasileira(row[col])
                elif 'atesto' in col_lower:
                    registro['data_atesto'] = processar_data_brasileira(row[col])
                elif 'envio' in col_lower and 'final' in col_lower:
                    registro['envio_final'] = processar_data_brasileira(row[col])
            
            registros.append(registro)
            
            # Progresso
            if (index + 1) % 50 == 0:
                print(f"   📊 Processados: {index + 1}/{len(df)}")
        
        except Exception as e:
            print(f"⚠️ Erro na linha {index+1}: {e}")
            continue
    
    print(f"✅ {len(registros)} registros válidos mapeados")
    if erros_cte > 0:
        print(f"⚠️ {erros_cte} registros ignorados por CTE inválido")
    
    return registros

def inserir_registros_banco(conn, registros):
    """Insere os registros no banco de dados"""
    try:
        cursor = conn.cursor()
        
        # Query de inserção/atualização
        insert_query = """
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
            observacao = COALESCE(EXCLUDED.observacao, dashboard_baker.observacao),
            data_inclusao_fatura = COALESCE(EXCLUDED.data_inclusao_fatura, dashboard_baker.data_inclusao_fatura),
            data_envio_processo = COALESCE(EXCLUDED.data_envio_processo, dashboard_baker.data_envio_processo),
            primeiro_envio = COALESCE(EXCLUDED.primeiro_envio, dashboard_baker.primeiro_envio),
            data_rq_tmc = COALESCE(EXCLUDED.data_rq_tmc, dashboard_baker.data_rq_tmc),
            data_atesto = COALESCE(EXCLUDED.data_atesto, dashboard_baker.data_atesto),
            envio_final = COALESCE(EXCLUDED.envio_final, dashboard_baker.envio_final),
            updated_at = CURRENT_TIMESTAMP;
        """
        
        inseridos = 0
        atualizados = 0
        erros = 0
        
        print("💾 Inserindo registros no banco...")
        
        for i, registro in enumerate(registros, 1):
            try:
                # Preparar parâmetros
                parametros = tuple(registro[campo] for campo in [
                    'numero_cte', 'destinatario_nome', 'veiculo_placa', 'valor_total',
                    'data_emissao', 'numero_fatura', 'data_baixa', 'observacao',
                    'data_inclusao_fatura', 'data_envio_processo', 'primeiro_envio',
                    'data_rq_tmc', 'data_atesto', 'envio_final', 'origem_dados'
                ])
                
                # Verificar se já existe
                cursor.execute("SELECT id FROM dashboard_baker WHERE numero_cte = %s", (registro['numero_cte'],))
                existe = cursor.fetchone()
                
                # Executar inserção/atualização
                cursor.execute(insert_query, parametros)
                
                if existe:
                    atualizados += 1
                else:
                    inseridos += 1
                
                # Mostrar progresso
                if i % 50 == 0:
                    print(f"   📊 {i}/{len(registros)} - CTE {registro['numero_cte']}")
                
                # Commit a cada 100 registros
                if i % 100 == 0:
                    conn.commit()
            
            except Exception as e:
                erros += 1
                print(f"❌ Erro CTE {registro.get('numero_cte', 'N/A')}: {e}")
                continue
        
        # Commit final
        conn.commit()
        cursor.close()
        
        print(f"\n📊 RESULTADO FINAL:")
        print(f"   ✅ {inseridos} registros inseridos")
        print(f"   🔄 {atualizados} registros atualizados")
        print(f"   ❌ {erros} erros")
        
        total_processados = inseridos + atualizados
        if len(registros) > 0:
            taxa_sucesso = (total_processados / len(registros)) * 100
            print(f"   📈 Taxa de sucesso: {taxa_sucesso:.1f}%")
        
        return total_processados > 0
        
    except Exception as e:
        print(f"❌ Erro na inserção: {e}")
        conn.rollback()
        return False

def main():
    """Função principal"""
    
    print("🚀 POPULAR BANCO - VERSÃO COM MAPEAMENTO CORRETO")
    print("=" * 60)
    
    # 1. Conectar ao banco
    conn = conectar_banco()
    if not conn:
        return
    
    # 2. Carregar CSV
    df, arquivo = carregar_csv_com_mapeamento()
    if df is None:
        print("❌ Não foi possível carregar o CSV")
        conn.close()
        return
    
    # 3. Carregar ou identificar mapeamento
    mapeamento = carregar_mapeamento()
    
    if not mapeamento or 'numero_cte' not in mapeamento:
        print("⚠️ Mapeamento não encontrado, identificando automaticamente...")
        mapeamento = identificar_colunas_automaticamente(df)
    
    if not mapeamento.get('numero_cte'):
        print("❌ Não foi possível identificar a coluna CTE")
        print("💡 Execute primeiro: python analisar_arquivo_real.py")
        conn.close()
        return
    
    # 4. Mapear dados
    registros = mapear_dados_para_banco(df, mapeamento)
    
    if not registros:
        print("❌ Nenhum registro válido para inserir")
        print("💡 Verifique se a coluna CTE contém números válidos")
        conn.close()
        return
    
    # 5. Confirmar inserção
    print(f"\n🎯 Pronto para inserir {len(registros)} registros no banco")
    print(f"📋 Arquivo: {arquivo}")
    print(f"🗄️ Banco: {DB_CONFIG['database']}")
    
    confirmacao = input("\n🔄 Continuar com a inserção? (s/N): ")
    
    if confirmacao.lower() not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada")
        conn.close()
        return
    
    # 6. Inserir dados
    sucesso = inserir_registros_banco(conn, registros)
    
    # 7. Verificação final
    if sucesso:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM dashboard_baker")
        total_banco = cursor.fetchone()[0]
        cursor.close()
        
        print(f"\n✅ SUCESSO!")
        print(f"🗄️ Total de registros no banco: {total_banco:,}")
        print(f"🌐 Execute o dashboard: streamlit run dashboard_baker_web_corrigido.py")
    else:
        print(f"\n❌ Falha na inserção")
        print(f"💡 Verifique os erros acima e tente novamente")
    
    conn.close()
    print("=" * 60)

if __name__ == "__main__":
    main()