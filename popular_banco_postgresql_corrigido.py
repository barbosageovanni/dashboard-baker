#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script CORRIGIDO para POPULAR o banco PostgreSQL dashboard_baker
Versão mais flexível que detecta automaticamente a estrutura do CSV
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

def conectar_banco():
    """Conecta ao banco de dados PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Conectado ao banco PostgreSQL")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None

def detectar_coluna_cte(df):
    """Detecta automaticamente a coluna que contém os números CTE"""
    print("🔍 Detectando coluna CTE...")
    
    # Possíveis nomes para coluna CTE
    padroes_cte = [
        r'.*cte.*',
        r'.*número.*',
        r'.*numero.*',
        r'.*conhecimento.*',
        r'.*ct.*'
    ]
    
    colunas_candidatas = []
    
    for coluna in df.columns:
        for padrao in padroes_cte:
            if re.search(padrao, coluna.lower()):
                colunas_candidatas.append(coluna)
                break
    
    print(f"📋 Colunas candidatas para CTE: {colunas_candidatas}")
    
    if not colunas_candidatas:
        print("❌ Nenhuma coluna CTE detectada automaticamente")
        print("📋 Todas as colunas disponíveis:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i:2d}. '{col}'")
        
        while True:
            try:
                escolha = input("\n🔍 Digite o número da coluna que contém os CTEs (ou 'q' para sair): ")
                if escolha.lower() == 'q':
                    return None
                
                escolha = int(escolha) - 1
                if 0 <= escolha < len(df.columns):
                    coluna_cte = df.columns[escolha]
                    print(f"✅ Coluna CTE selecionada: '{coluna_cte}'")
                    return coluna_cte
                else:
                    print("❌ Número inválido")
            except ValueError:
                print("❌ Digite um número válido")
    
    else:
        # Verificar qual coluna tem mais valores numéricos válidos
        melhor_coluna = None
        melhor_score = 0
        
        for coluna in colunas_candidatas:
            valores_validos = 0
            valores_totais = len(df[coluna].dropna())
            
            if valores_totais == 0:
                continue
            
            for valor in df[coluna].dropna().head(50):  # Testar apenas 50 valores
                try:
                    int(valor)
                    valores_validos += 1
                except:
                    pass
            
            score = valores_validos / valores_totais if valores_totais > 0 else 0
            print(f"   📊 '{coluna}': {valores_validos}/{valores_totais} válidos ({score:.1%})")
            
            if score > melhor_score:
                melhor_score = score
                melhor_coluna = coluna
        
        if melhor_coluna and melhor_score > 0.5:
            print(f"✅ Coluna CTE detectada: '{melhor_coluna}' (score: {melhor_score:.1%})")
            return melhor_coluna
        else:
            print("❌ Nenhuma coluna CTE adequada detectada automaticamente")
            return None

def detectar_colunas_principais(df):
    """Detecta automaticamente as principais colunas do CSV"""
    print("🔍 Detectando colunas principais...")
    
    mapeamento = {}
    
    # Padrões para detectar colunas
    padroes = {
        'destinatario': [r'.*destinat.*', r'.*cliente.*', r'.*nome.*'],
        'veiculo': [r'.*veículo.*', r'.*veiculo.*', r'.*placa.*'],
        'valor': [r'.*total.*', r'.*valor.*', r'.*r\$.*'],
        'data_emissao': [r'.*emiss.*', r'.*data.*emiss.*'],
        'fatura': [r'.*fatura.*', r'.*fat.*'],
        'data_baixa': [r'.*baixa.*', r'.*pagamento.*'],
        'observacao': [r'.*observ.*', r'.*obs.*', r'.*nota.*', r'.*coment.*']
    }
    
    for campo, padroes_campo in padroes.items():
        for coluna in df.columns:
            for padrao in padroes_campo:
                if re.search(padrao, coluna.lower()):
                    mapeamento[campo] = coluna
                    print(f"   ✅ {campo}: '{coluna}'")
                    break
            if campo in mapeamento:
                break
        
        if campo not in mapeamento:
            print(f"   ⚠️ {campo}: Não detectado")
    
    return mapeamento

def processar_valor_monetario(valor):
    """Processa valores monetários brasileiros"""
    if pd.isna(valor):
        return 0.0
    
    try:
        # Converter para string e limpar
        valor_str = str(valor).strip()
        
        # Remover símbolos monetários
        valor_str = re.sub(r'[R$\s]', '', valor_str)
        
        # Se contém vírgula e ponto, assumir formato brasileiro
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

def mapear_dados_csv_para_banco_flexivel(df, coluna_cte, mapeamento):
    """Mapeia os dados do CSV para a estrutura do banco de forma flexível"""
    try:
        registros = []
        
        print(f"🔄 Processando {len(df)} registros...")
        
        for index, row in df.iterrows():
            try:
                # Extrair número CTE
                numero_cte_raw = row[coluna_cte]
                
                if pd.isna(numero_cte_raw):
                    print(f"⚠️ Linha {index+1}: CTE vazio")
                    continue
                
                # Tentar converter para int
                try:
                    numero_cte = int(numero_cte_raw)
                    if numero_cte <= 0:
                        print(f"⚠️ Linha {index+1}: CTE inválido: {numero_cte_raw}")
                        continue
                except:
                    print(f"⚠️ Linha {index+1}: CTE não numérico: '{numero_cte_raw}'")
                    continue
                
                # Mapear outros campos
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
                    'origem_dados': 'CSV_FLEXIVEL'
                }
                
                # Mapear campos detectados
                if 'destinatario' in mapeamento:
                    dest = row[mapeamento['destinatario']]
                    registro['destinatario_nome'] = str(dest).strip() if pd.notna(dest) else None
                
                if 'veiculo' in mapeamento:
                    vei = row[mapeamento['veiculo']]
                    registro['veiculo_placa'] = str(vei).strip() if pd.notna(vei) else None
                
                if 'valor' in mapeamento:
                    registro['valor_total'] = processar_valor_monetario(row[mapeamento['valor']])
                
                if 'data_emissao' in mapeamento:
                    registro['data_emissao'] = processar_data_brasileira(row[mapeamento['data_emissao']])
                
                if 'fatura' in mapeamento:
                    fat = row[mapeamento['fatura']]
                    registro['numero_fatura'] = str(fat).strip() if pd.notna(fat) else None
                
                if 'data_baixa' in mapeamento:
                    registro['data_baixa'] = processar_data_brasileira(row[mapeamento['data_baixa']])
                
                if 'observacao' in mapeamento:
                    obs = row[mapeamento['observacao']]
                    registro['observacao'] = str(obs).strip() if pd.notna(obs) else None
                
                # Tentar detectar outras datas automaticamente
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
                
                # Mostrar progresso a cada 50 registros
                if (index + 1) % 50 == 0:
                    print(f"   📊 Processados: {index + 1}/{len(df)}")
                
            except Exception as e:
                print(f"⚠️ Erro na linha {index+1}: {e}")
                continue
        
        print(f"✅ {len(registros)} registros mapeados para inserção")
        return registros
        
    except Exception as e:
        print(f"❌ Erro no mapeamento: {e}")
        return []

def carregar_csv_flexivel():
    """Carrega o arquivo CSV de forma mais flexível"""
    try:
        # Tentar diferentes nomes de arquivo CSV
        possiveis_arquivos = [
            'Status Faturamento   Ctes vs Faturas vs Atestos.csv',
            'Relatório Faturamento Baker em aberto  Ctes vs Faturas vs Atestos.csv',
            'data/Status Faturamento   Ctes vs Faturas vs Atestos.csv',
            'dashboard_data.csv'
        ]
        
        # Também procurar por qualquer arquivo .csv na pasta atual
        arquivos_csv = [f for f in os.listdir('.') if f.endswith('.csv')]
        possiveis_arquivos.extend(arquivos_csv)
        
        df = None
        arquivo_usado = None
        
        for arquivo in possiveis_arquivos:
            if os.path.exists(arquivo):
                try:
                    # Tentar diferentes encodings
                    encodings = ['cp1252', 'utf-8', 'latin1', 'iso-8859-1']
                    
                    for encoding in encodings:
                        try:
                            df = pd.read_csv(arquivo, sep=';', encoding=encoding, on_bad_lines='skip')
                            arquivo_usado = arquivo
                            print(f"✅ CSV carregado: {arquivo} (encoding: {encoding})")
                            break
                        except:
                            continue
                    
                    if df is not None:
                        break
                        
                except Exception as e:
                    print(f"⚠️ Erro ao carregar {arquivo}: {e}")
                    continue
        
        if df is None:
            print("❌ Nenhum arquivo CSV encontrado")
            print("📋 Arquivos procurados:")
            for arquivo in possiveis_arquivos[:4]:  # Mostrar apenas os principais
                print(f"   - {arquivo}")
            return None
        
        print(f"✅ Dados carregados: {len(df)} registros de {arquivo_usado}")
        
        # Limpar nomes das colunas
        df.columns = df.columns.str.strip()
        
        print("✅ Dados processados")
        return df
        
    except Exception as e:
        print(f"❌ Erro ao carregar CSV: {e}")
        return None

def inserir_registros_banco(conn, registros):
    """Insere os registros no banco de dados"""
    try:
        cursor = conn.cursor()
        
        # Query de inserção
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
        
        for i, registro in enumerate(registros, 1):
            try:
                # Preparar parâmetros
                parametros = (
                    registro['numero_cte'],
                    registro['destinatario_nome'],
                    registro['veiculo_placa'],
                    registro['valor_total'],
                    registro['data_emissao'],
                    registro['numero_fatura'],
                    registro['data_baixa'],
                    registro['observacao'],
                    registro['data_inclusao_fatura'],
                    registro['data_envio_processo'],
                    registro['primeiro_envio'],
                    registro['data_rq_tmc'],
                    registro['data_atesto'],
                    registro['envio_final'],
                    registro['origem_dados']
                )
                
                # Verificar se já existe
                cursor.execute("SELECT id FROM dashboard_baker WHERE numero_cte = %s", (registro['numero_cte'],))
                existe = cursor.fetchone()
                
                # Executar inserção/atualização
                cursor.execute(insert_query, parametros)
                
                if existe:
                    atualizados += 1
                    if i % 50 == 0:  # Mostrar progresso menos frequente
                        print(f"🔄 Atualizado {i}/{len(registros)} - CTE {registro['numero_cte']}")
                else:
                    inseridos += 1
                    if i % 50 == 0:
                        print(f"✅ Inserido {i}/{len(registros)} - CTE {registro['numero_cte']}")
                
                # Commit a cada 100 registros
                if i % 100 == 0:
                    conn.commit()
                    print(f"💾 Commit realizado - {i} registros processados")
                
            except Exception as e:
                erros += 1
                print(f"❌ Erro ao inserir CTE {registro.get('numero_cte', 'N/A')}: {e}")
                continue
        
        # Commit final
        conn.commit()
        cursor.close()
        
        print(f"\n📊 RESUMO DA INSERÇÃO:")
        print(f"   ✅ {inseridos} registros inseridos")
        print(f"   🔄 {atualizados} registros atualizados")
        print(f"   ❌ {erros} erros")
        print(f"   📈 Taxa de sucesso: {((inseridos + atualizados)/(len(registros)) * 100):.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na inserção: {e}")
        conn.rollback()
        return False

def main():
    """Função principal"""
    print("🚀 POPULAR BANCO POSTGRESQL - VERSÃO CORRIGIDA")
    print("=" * 60)
    
    # 1. Conectar ao banco
    conn = conectar_banco()
    if not conn:
        return
    
    # 2. Carregar CSV
    print("\n📂 Carregando dados do CSV...")
    df = carregar_csv_flexivel()
    if df is None or df.empty:
        print("❌ Não foi possível carregar dados do CSV")
        conn.close()
        return
    
    # 3. Detectar coluna CTE
    print("\n🔍 Detectando estrutura do CSV...")
    coluna_cte = detectar_coluna_cte(df)
    if not coluna_cte:
        print("❌ Não foi possível identificar a coluna CTE")
        conn.close()
        return
    
    # 4. Detectar outras colunas
    mapeamento = detectar_colunas_principais(df)
    
    # 5. Mapear dados
    print("\n🔄 Mapeando dados para estrutura do banco...")
    registros = mapear_dados_csv_para_banco_flexivel(df, coluna_cte, mapeamento)
    if not registros:
        print("❌ Nenhum registro válido para inserir")
        
        # Mostrar diagnóstico
        print("\n🔍 EXECUTANDO DIAGNÓSTICO...")
        print("💡 Execute: python diagnostico_csv.py para mais detalhes")
        
        conn.close()
        return
    
    # 6. Confirmar inserção
    print(f"\n🎯 Será feita a inserção de {len(registros)} registros no banco PostgreSQL")
    
    confirmacao = input("\n🔄 Deseja continuar com a inserção? (s/N): ")
    
    if confirmacao.lower() not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada pelo usuário")
        conn.close()
        return
    
    # 7. Inserir dados
    print("\n💾 Inserindo dados no banco...")
    if not inserir_registros_banco(conn, registros):
        conn.close()
        return
    
    # 8. Fechar conexão
    conn.close()
    
    print(f"\n✅ PROCESSO CONCLUÍDO COM SUCESSO!")
    print(f"🎯 O banco PostgreSQL foi atualizado")
    print(f"🌐 Execute o dashboard: streamlit run dashboard_baker_web_corrigido.py")
    print("=" * 60)

if __name__ == "__main__":
    main()