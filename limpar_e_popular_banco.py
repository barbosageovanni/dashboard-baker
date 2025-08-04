#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script CORRIGIDO para popular o banco PostgreSQL - VERSÃO 3.0
✅ CORREÇÃO CRÍTICA: Mapeamento e importação do campo "envio_final"
✅ DEBUGGING AVANÇADO: Rastreamento completo da importação
✅ MAPEAMENTO INTELIGENTE: Detecção automática de colunas com espaços/caracteres especiais
✅ NOVAS FUNCIONALIDADES: Sistema de baixas, variações temporais, alertas automáticos
"""

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import os
import re
import json

# Configuração do banco PostgreSQL  
DB_CONFIG = {
    'host': 'localhost',
    'database': 'dashboard_baker',
    'user': 'postgres',
    'password': 'senha123',
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

def carregar_csv_com_deteccao_avancada():
    """Carrega CSV com detecção avançada de encoding e formato"""
    
    # Buscar arquivo CSV com nomes possíveis
    arquivos_possiveis = [
        "Status Faturamento   Ctes vs Faturas vs Atestos.csv",
        "Status Faturamento Ctes vs Faturas vs Atestos.csv",
        "Status Faturamento.csv",
        "Relatório Faturamento Baker.csv"
    ]
    
    arquivo = None
    for arquivo_teste in arquivos_possiveis:
        if os.path.exists(arquivo_teste):
            arquivo = arquivo_teste
            print(f"🎯 Arquivo encontrado automaticamente: {arquivo}")
            break
    
    if not arquivo:
        # Procurar qualquer CSV
        arquivos_csv = [f for f in os.listdir('.') if f.endswith('.csv')]
        if arquivos_csv:
            print("\n📋 Arquivos CSV encontrados:")
            for i, arq in enumerate(arquivos_csv, 1):
                print(f"   {i}. {arq}")
            
            try:
                escolha = int(input(f"\nEscolha o arquivo (1-{len(arquivos_csv)}): ")) - 1
                if 0 <= escolha < len(arquivos_csv):
                    arquivo = arquivos_csv[escolha]
            except:
                return None, None
        else:
            print("❌ Nenhum arquivo CSV encontrado")
            return None, None
    
    print(f"📂 Carregando: {arquivo}")
    print(f"📁 Tamanho: {os.path.getsize(arquivo) / 1024:.1f} KB")
    
    # CONFIGURAÇÕES AVANÇADAS DE CARREGAMENTO
    configuracoes = [
        {'sep': ';', 'encoding': 'utf-8'},
        {'sep': ';', 'encoding': 'cp1252'},      # Windows-1252 (mais comum)
        {'sep': ';', 'encoding': 'latin1'},       # ISO-8859-1
        {'sep': ';', 'encoding': 'utf-8-sig'},    # UTF-8 with BOM
        {'sep': ',', 'encoding': 'utf-8'},        # CSV inglês
        {'sep': ',', 'encoding': 'cp1252'},
        {'sep': '\t', 'encoding': 'utf-8'},       # TSV
        {'sep': '\t', 'encoding': 'cp1252'},
    ]
    
    df = None
    config_usada = None
    
    for i, config in enumerate(configuracoes, 1):
        try:
            print(f"   🔄 Tentativa {i}: {config}")
            df = pd.read_csv(arquivo, on_bad_lines='skip', **config)
            config_usada = config
            print(f"   ✅ Sucesso com: {config}")
            break
        except Exception as e:
            print(f"   ❌ Falhou: {str(e)[:50]}...")
            continue
    
    if df is None:
        print("❌ Não foi possível carregar o arquivo com nenhuma configuração")
        return None, None
    
    # LIMPEZA AVANÇADA DE COLUNAS
    print(f"\n🧹 Limpando nomes das colunas...")
    print(f"   📋 Colunas originais: {len(df.columns)}")
    
    # Mostrar colunas originais para debug
    print(f"   🔍 Colunas brutas encontradas:")
    for i, col in enumerate(df.columns, 1):
        print(f"      {i:2}. '{col}' (len={len(col)})")
    
    # Limpar colunas com técnica avançada
    colunas_limpas = []
    for col in df.columns:
        # Remover espaços extras, quebras de linha, etc.
        col_limpa = re.sub(r'\s+', ' ', str(col).strip())
        colunas_limpas.append(col_limpa)
    
    df.columns = colunas_limpas
    
    print(f"   ✅ Colunas após limpeza:")
    for i, col in enumerate(df.columns, 1):
        print(f"      {i:2}. '{col}'")
    
    print(f"\n📊 Dataset carregado:")
    print(f"   📈 Registros: {len(df)}")
    print(f"   📋 Colunas: {len(df.columns)}")
    print(f"   💾 Memória: {df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    
    return df, arquivo

def criar_mapeamento_inteligente(df):
    """Cria mapeamento inteligente com foco especial no campo envio_final"""
    
    colunas_disponiveis = df.columns.tolist()
    
    print(f"\n🧠 MAPEAMENTO INTELIGENTE - {len(colunas_disponiveis)} colunas")
    print("=" * 70)
    
    # MAPEAMENTO BASE EXPANDIDO com mais variações
    mapeamento_base = {
        'numero_cte': ['CTE', 'Numero CTE', 'Número CTE', 'NumCTE', 'N CTE', 'Nº CTE'],
        'destinatario_nome': [
            'Remetente - Nome', 'Destinatario', 'Cliente', 'Remetente',
            'Destinatário - Nome', 'Nome Destinatario', 'Nome Cliente',
            'Destinatário', 'Remetente Nome'
        ],
        'veiculo_placa': [
            'Veículo - Placa', 'Veiculo', 'Placa', 'Veiculo - Placa',
            'Placa Veiculo', 'Placa do Veiculo', 'Veículo Placa'
        ],
        'valor_total': [
            'Total', 'Valor', 'Valor Total', 'Valor do CTE', 'Vlr Total',
            ' Total ', 'Total ', ' Total'  # Variações com espaços
        ],
        'data_emissao': [
            'Data emissão Cte', 'Data Emissao', 'Emissao', 'Data CTE',
            'Data de emissão', 'Dt Emissao', 'Data emissao Cte'
        ],
        'data_rq_tmc': [
            'Data RQ/TMC', 'RQ/TMC', 'Data RQ', 'Data TMC',
            'RQ TMC', 'Data RQ-TMC', 'Data RQ TMC'
        ],
        'data_envio_processo': [
            'Data Envio do processo Faturamento', 'Envio Processo',
            'Data Envio Processo', 'Envio do Processo', 'Data Envio Faturamento'
        ],
        'data_inclusao_fatura': [
            'Data INCLUSÃO Fatura Bsoft', 'Inclusão Fatura', 'Inclusao Fatura',
            'Data Inclusao', 'Dt Inclusao Fatura', 'Data INCLUSAO Fatura Bsoft'
        ],
        'primeiro_envio': [
            '1° Envio', '1º Envio', 'Primeiro Envio', '1 Envio',
            'Primeiro envio', '1° envio', '1º envio', '1 envio'
        ],
        'data_atesto': [
            'Data do atesto', 'Atesto', 'Data Atesto', 'Dt Atesto',
            'Data de Atesto', 'Data do Atesto', 'Data atesto'
        ],
        # ⭐ FOCO ESPECIAL NO ENVIO_FINAL - TODAS AS VARIAÇÕES POSSÍVEIS
        'envio_final': [
            'Envio final', 'Envio Final', 'Final', 'Envio final CTE',
            'Data Envio Final', 'Dt Envio Final', 'Envio Final',
            'envio final', 'ENVIO FINAL', 'Envio_Final', 'EnvioFinal',
            ' Envio final', 'Envio final ', ' Envio final ',  # Com espaços
            'Envio\nfinal', 'Envio\r\nfinal',  # Com quebras de linha
        ],
        'numero_fatura': [
            'Faturas', 'Fatura', 'Numero Fatura', 'Nº Fatura',
            'N Fatura', 'Num Fatura', 'Número Fatura'
        ],
        'observacao': [
            'OBSERVAÇÃO', 'Observacao', 'Obs', 'Observacoes',
            'Observações', 'Comentario', 'Comentário', 'OBSERVACAO'
        ]
    }
    
    # ALGORITMO DE MAPEAMENTO INTELIGENTE
    mapeamento_final = {}
    colunas_nao_mapeadas = []
    
    print(f"🔍 Iniciando mapeamento inteligente...")
    
    for campo, possiveis_nomes in mapeamento_base.items():
        encontrado = False
        campo_encontrado = None
        
        # Busca exata primeiro
        for nome_possivel in possiveis_nomes:
            if nome_possivel in colunas_disponiveis:
                mapeamento_final[campo] = nome_possivel
                campo_encontrado = nome_possivel
                encontrado = True
                print(f"   ✅ {campo:20} -> '{nome_possivel}' (busca exata)")
                break
        
        # Se não encontrou, busca aproximada (ignorando espaços e case)
        if not encontrado:
            for coluna_real in colunas_disponiveis:
                coluna_normalizada = re.sub(r'\s+', ' ', coluna_real.lower().strip())
                
                for nome_possivel in possiveis_nomes:
                    nome_normalizado = re.sub(r'\s+', ' ', nome_possivel.lower().strip())
                    
                    # Comparação flexível
                    if (coluna_normalizada == nome_normalizado or
                        nome_normalizado in coluna_normalizada or
                        coluna_normalizada in nome_normalizado):
                        
                        mapeamento_final[campo] = coluna_real
                        campo_encontrado = coluna_real
                        encontrado = True
                        print(f"   ✅ {campo:20} -> '{coluna_real}' (busca aproximada)")
                        break
                
                if encontrado:
                    break
        
        # Se ainda não encontrou
        if not encontrado:
            mapeamento_final[campo] = None
            colunas_nao_mapeadas.append(campo)
            print(f"   ❌ {campo:20} -> NÃO ENCONTRADO")
            
            # Debug especial para envio_final
            if campo == 'envio_final':
                print(f"      🚨 PROBLEMA CRÍTICO: Campo 'envio_final' não mapeado!")
                print(f"      🔍 Procurei por: {possiveis_nomes}")
                print(f"      📋 Colunas disponíveis que contêm 'envio' ou 'final':")
                for col in colunas_disponiveis:
                    if 'envio' in col.lower() or 'final' in col.lower():
                        print(f"         📌 '{col}'")
    
    # VERIFICAÇÃO ESPECIAL PARA ENVIO_FINAL
    if not mapeamento_final.get('envio_final'):
        print(f"\n🚨 BUSCA EMERGENCIAL PARA ENVIO_FINAL:")
        
        # Busca mais agressiva
        candidatos_envio_final = []
        for col in colunas_disponiveis:
            col_lower = col.lower()
            if ('envio' in col_lower and 'final' in col_lower) or 'final' in col_lower:
                candidatos_envio_final.append(col)
        
        if candidatos_envio_final:
            print(f"   🎯 Candidatos encontrados:")
            for i, candidato in enumerate(candidatos_envio_final, 1):
                print(f"      {i}. '{candidato}'")
            
            # Usar o primeiro candidato automaticamente
            mapeamento_final['envio_final'] = candidatos_envio_final[0]
            print(f"   ✅ Usando automaticamente: '{candidatos_envio_final[0]}'")
        else:
            print(f"   ❌ Nenhum candidato encontrado para envio_final")
    
    print(f"\n📊 RESULTADO DO MAPEAMENTO:")
    print(f"   ✅ Campos mapeados: {len([v for v in mapeamento_final.values() if v])}")
    print(f"   ❌ Campos não mapeados: {len(colunas_nao_mapeadas)}")
    
    if colunas_nao_mapeadas:
        print(f"   ⚠️ Não mapeados: {', '.join(colunas_nao_mapeadas)}")
    
    # SALVAR MAPEAMENTO PARA DEBUG
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    arquivo_debug = f'mapeamento_debug_{timestamp}.json'
    
    debug_info = {
        'timestamp': timestamp,
        'arquivo_csv': 'N/A',
        'mapeamento_final': mapeamento_final,
        'colunas_disponiveis': colunas_disponiveis,
        'colunas_nao_mapeadas': colunas_nao_mapeadas
    }
    
    try:
        with open(arquivo_debug, 'w', encoding='utf-8') as f:
            json.dump(debug_info, f, indent=2, default=str)
        print(f"   💾 Debug salvo em: {arquivo_debug}")
    except:
        pass
    
    return mapeamento_final

def processar_valor_monetario_avancado(valor):
    """Processamento avançado de valores monetários brasileiros"""
    if pd.isna(valor) or valor == '' or valor is None:
        return 0.0
    
    try:
        valor_str = str(valor).strip()
        
        if not valor_str or valor_str.lower() in ['nan', 'nat', '', 'none', 'null']:
            return 0.0
        
        # Remover símbolos monetários, espaços e outros caracteres
        valor_str = re.sub(r'[R$\s€\$£¥]', '', valor_str)
        valor_str = re.sub(r'[^\d,.-]', '', valor_str)
        
        if not valor_str:
            return 0.0
        
        # Processar diferentes formatos brasileiros
        if ',' in valor_str and '.' in valor_str:
            # Formato: 1.234.567,89 ou 1,234,567.89
            if valor_str.rfind(',') > valor_str.rfind('.'):
                # Formato brasileiro: 1.234.567,89
                valor_str = valor_str.replace('.', '').replace(',', '.')
            else:
                # Formato americano: 1,234,567.89
                valor_str = valor_str.replace(',', '')
        
        elif ',' in valor_str:
            # Pode ser formato brasileiro (1234,89) ou americano (1,234)
            partes = valor_str.split(',')
            if len(partes) == 2 and len(partes[1]) <= 2:
                # Formato brasileiro: 1234,89
                valor_str = valor_str.replace(',', '.')
            else:
                # Formato americano: 1,234 ou 1,234,567
                valor_str = valor_str.replace(',', '')
        
        return float(valor_str)
        
    except Exception as e:
        print(f"   ⚠️ Erro ao processar valor '{valor}': {e}")
        return 0.0

def processar_data_brasileira_avancada(data_str, debug_campo=None):
    """Processamento avançado de datas brasileiras com debugging detalhado"""
    if pd.isna(data_str) or data_str == '' or data_str is None:
        return None
    
    try:
        data_str = str(data_str).strip()
        
        if not data_str or data_str.lower() in ['nan', 'nat', '', 'none', 'null']:
            return None
        
        # Remover caracteres especiais comuns
        data_str = re.sub(r'[^\w/\-.:, ]', '', data_str)
        data_str = data_str.strip()
        
        if not data_str:
            return None
        
        # FORMATOS DE DATA EXPANDIDOS (ordem de prioridade)
        formatos = [
            # Formatos brasileiros com mês abreviado
            '%d/%b/%y',      # 25/jul/24
            '%d/%b/%Y',      # 25/jul/2024
            '%d %b %y',      # 25 jul 24
            '%d %b %Y',      # 25 jul 2024
            '%d-%b-%y',      # 25-jul-24
            '%d-%b-%Y',      # 25-jul-2024
            '%d.%b.%y',      # 25.jul.24
            '%d.%b.%Y',      # 25.jul.2024
            
            # Formatos numéricos
            '%d/%m/%Y',      # 25/07/2024
            '%d-%m-%Y',      # 25-07-2024
            '%Y-%m-%d',      # 2024-07-25 (ISO)
            '%d/%m/%y',      # 25/07/24
            '%d-%m-%y',      # 25-07-24
            '%d.%m.%Y',      # 25.07.2024
            '%d.%m.%y',      # 25.07.24
            '%d %m %Y',      # 25 07 2024
            '%d %m %y',      # 25 07 24
            
            # Formatos americanos
            '%m/%d/%Y',      # 07/25/2024
            '%m-%d-%Y',      # 07-25-2024
            '%m/%d/%y',      # 07/25/24
            '%m-%d-%y',      # 07-25-24
            
            # Formatos longos
            '%d de %B de %Y', # 25 de julho de 2024
        ]
        
        # Tentar cada formato
        for formato in formatos:
            try:
                data_processada = datetime.strptime(data_str, formato).date()
                
                # Validação básica da data
                if data_processada.year < 2020 or data_processada.year > 2030:
                    continue
                
                if debug_campo:
                    print(f"      🗓️ {debug_campo}: '{data_str}' -> {data_processada} ✅")
                
                return data_processada
                
            except ValueError:
                continue
        
        # Se não conseguiu processar com formatos padrão, tentar limpeza mais agressiva
        # Normalizar meses brasileiros
        meses_br = {
            'jan': 'Jan', 'fev': 'Feb', 'mar': 'Mar', 'abr': 'Apr',
            'mai': 'May', 'jun': 'Jun', 'jul': 'Jul', 'ago': 'Aug',
            'set': 'Sep', 'out': 'Oct', 'nov': 'Nov', 'dez': 'Dec'
        }
        
        data_normalizada = data_str.lower()
        for br_mes, en_mes in meses_br.items():
            if br_mes in data_normalizada:
                data_normalizada = data_normalizada.replace(br_mes, en_mes)
                break
        
        # Tentar novamente com data normalizada
        for formato in formatos[:8]:  # Só os formatos com mês abreviado
            try:
                data_processada = datetime.strptime(data_normalizada, formato).date()
                
                if data_processada.year < 2020 or data_processada.year > 2030:
                    continue
                
                if debug_campo:
                    print(f"      🗓️ {debug_campo}: '{data_str}' -> {data_processada} ✅ (normalizada)")
                
                return data_processada
                
            except ValueError:
                continue
        
        # Se chegou aqui, não conseguiu processar
        if debug_campo:
            print(f"      ❌ {debug_campo}: Falha ao processar '{data_str}'")
        
        return None
        
    except Exception as e:
        if debug_campo:
            print(f"      ❌ {debug_campo}: Erro '{data_str}': {e}")
        return None

def mapear_dados_para_banco_avancado(df, mapeamento):
    """Mapeamento avançado com foco especial no envio_final e debugging detalhado"""
    
    if not mapeamento.get('numero_cte'):
        print("❌ ERRO CRÍTICO: Coluna CTE não identificada no mapeamento!")
        return []
    
    print(f"\n🔄 MAPEAMENTO AVANÇADO - {len(df)} registros")
    print("=" * 70)
    
    # VERIFICAÇÃO PRÉVIA DA COLUNA ENVIO_FINAL
    coluna_envio_final = mapeamento.get('envio_final')
    if coluna_envio_final:
        print(f"🎯 VERIFICAÇÃO PRÉVIA - Campo envio_final mapeado para: '{coluna_envio_final}'")
        
        # Estatísticas da coluna envio_final no CSV
        if coluna_envio_final in df.columns:
            valores_envio_final = df[coluna_envio_final]
            total_valores = len(valores_envio_final)
            valores_nao_nulos = valores_envio_final.notna().sum()
            valores_nao_vazios = (valores_envio_final != '').sum()
            
            print(f"   📊 Total de registros: {total_valores}")
            print(f"   ✅ Valores não nulos: {valores_nao_nulos}")
            print(f"   ✅ Valores não vazios: {valores_nao_vazios}")
            
            # Mostrar alguns exemplos
            exemplos = valores_envio_final.dropna().head(10)
            if len(exemplos) > 0:
                print(f"   🔍 Exemplos de valores encontrados:")
                for i, valor in enumerate(exemplos, 1):
                    print(f"      {i}. '{valor}'")
            else:
                print(f"   ❌ PROBLEMA: Nenhum valor válido encontrado na coluna!")
        else:
            print(f"   ❌ ERRO: Coluna '{coluna_envio_final}' não existe no DataFrame!")
    else:
        print(f"❌ PROBLEMA CRÍTICO: Campo envio_final não foi mapeado!")
    
    print(f"\n🔄 Iniciando processamento dos registros...")
    
    registros = []
    erros_cte = 0
    debug_count = 0
    registros_envio_final_encontrados = 0
    
    for index, row in df.iterrows():
        try:
            # Extrair número CTE com processamento avançado
            numero_cte_raw = row[mapeamento['numero_cte']]
            
            if pd.isna(numero_cte_raw):
                erros_cte += 1
                continue
            
            # Converter para int com limpeza
            try:
                if isinstance(numero_cte_raw, str):
                    numero_cte_str = re.sub(r'[^\d]', '', numero_cte_raw)
                    if not numero_cte_str:
                        erros_cte += 1
                        continue
                    numero_cte = int(numero_cte_str)
                else:
                    numero_cte = int(float(numero_cte_raw))
                
                if numero_cte <= 0:
                    erros_cte += 1
                    continue
                    
            except:
                erros_cte += 1
                continue
            
            # Criar registro base
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
                'origem_dados': 'CSV_CORRIGIDO_V3'
            }
            
            # Debug detalhado para os primeiros registros E para o CTE 306 específico
            mostrar_debug = debug_count < 5 or numero_cte == 306
            if mostrar_debug:
                print(f"\n   🔍 DEBUG CTE {numero_cte}:")
            
            # Mapear todos os campos disponíveis
            for campo, coluna in mapeamento.items():
                if not coluna or coluna not in df.columns:
                    continue
                
                valor = row[coluna]
                
                if campo == 'destinatario_nome':
                    if pd.notna(valor) and str(valor).strip() != '':
                        registro['destinatario_nome'] = str(valor).strip()
                        if mostrar_debug:
                            print(f"      👤 Destinatário: '{registro['destinatario_nome']}'")
                
                elif campo == 'veiculo_placa':
                    if pd.notna(valor) and str(valor).strip() != '':
                        registro['veiculo_placa'] = str(valor).strip()
                        if mostrar_debug:
                            print(f"      🚛 Veículo: '{registro['veiculo_placa']}'")
                
                elif campo == 'valor_total':
                    registro['valor_total'] = processar_valor_monetario_avancado(valor)
                    if mostrar_debug:
                        print(f"      💰 Valor: R$ {registro['valor_total']:.2f} (original: '{valor}')")
                
                elif campo == 'numero_fatura':
                    if pd.notna(valor) and str(valor).strip() != '':
                        registro['numero_fatura'] = str(valor).strip()
                        if mostrar_debug:
                            print(f"      📄 Fatura: '{registro['numero_fatura']}'")
                
                elif campo == 'observacao':
                    if pd.notna(valor) and str(valor).strip() != '':
                        registro['observacao'] = str(valor).strip()[:500]  # Limitar tamanho
                
                # PROCESSAMENTO ESPECIAL PARA ENVIO_FINAL
                elif campo == 'envio_final':
                    debug_campo = 'ENVIO_FINAL' if mostrar_debug else None
                    data_processada = processar_data_brasileira_avancada(valor, debug_campo)
                    registro['envio_final'] = data_processada
                    
                    if data_processada:
                        registros_envio_final_encontrados += 1
                        if mostrar_debug:
                            print(f"      🎯 ENVIO_FINAL: '{valor}' -> {data_processada} ✅✅✅")
                    elif mostrar_debug:
                        print(f"      ⚠️ ENVIO_FINAL: '{valor}' -> FALHA NO PROCESSAMENTO")
                
                # Processar outras datas
                elif campo in ['data_emissao', 'data_rq_tmc', 'data_envio_processo', 
                             'data_inclusao_fatura', 'primeiro_envio', 'data_atesto', 'data_baixa']:
                    
                    debug_campo = campo if mostrar_debug else None
                    data_processada = processar_data_brasileira_avancada(valor, debug_campo)
                    registro[campo] = data_processada
            
            registros.append(registro)
            
            if mostrar_debug:
                debug_count += 1
            
            # Progresso
            if (index + 1) % 50 == 0:
                print(f"   📊 Processados: {index + 1}/{len(df)} (envio_final: {registros_envio_final_encontrados})")
        
        except Exception as e:
            print(f"⚠️ Erro na linha {index+1} (CTE {numero_cte_raw}): {e}")
            continue
    
    print(f"\n✅ RESULTADO DO MAPEAMENTO:")
    print(f"   📈 {len(registros)} registros válidos mapeados")
    print(f"   🎯 {registros_envio_final_encontrados} registros COM envio_final ⭐")
    print(f"   ❌ {erros_cte} registros ignorados por CTE inválido")
    
    # Estatísticas detalhadas
    estatisticas = {
        'com_destinatario': sum(1 for r in registros if r['destinatario_nome']),
        'com_veiculo': sum(1 for r in registros if r['veiculo_placa']),
        'com_emissao': sum(1 for r in registros if r['data_emissao']),
        'com_primeiro_envio': sum(1 for r in registros if r['primeiro_envio']),
        'com_atesto': sum(1 for r in registros if r['data_atesto']),
        'com_envio_final': sum(1 for r in registros if r['envio_final']),  # ⭐ CRÍTICO
        'com_fatura': sum(1 for r in registros if r['numero_fatura']),
        'com_rq_tmc': sum(1 for r in registros if r['data_rq_tmc'])
    }
    
    print(f"\n📊 ESTATÍSTICAS DETALHADAS:")
    for campo, quantidade in estatisticas.items():
        porcentagem = (quantidade / len(registros)) * 100 if len(registros) > 0 else 0
        emoji = "🎯" if campo == 'com_envio_final' else "✅"
        print(f"   {emoji} {campo:20}: {quantidade:4}/{len(registros)} ({porcentagem:5.1f}%)")
    
    # VERIFICAÇÃO FINAL ESPECÍFICA PARA ENVIO_FINAL
    print(f"\n🎯 VERIFICAÇÃO FINAL - ENVIO_FINAL:")
    registros_com_envio_final = [r for r in registros if r['envio_final']]
    
    if registros_com_envio_final:
        print(f"   ✅ {len(registros_com_envio_final)} registros processados com envio_final")
        print(f"   🔍 Primeiros 10 exemplos:")
        for i, r in enumerate(registros_com_envio_final[:10], 1):
            print(f"      {i:2}. CTE {r['numero_cte']:6}: {r['envio_final']}")
        
        # VERIFICAÇÃO ESPECÍFICA DO CTE 306
        cte_306 = next((r for r in registros if r['numero_cte'] == 306), None)
        if cte_306:
            print(f"\n   🎯 VERIFICAÇÃO CTE 306:")
            print(f"      ✅ CTE 306 encontrado nos registros")
            print(f"      🗓️ Envio Final: {cte_306['envio_final']}")
            if cte_306['envio_final']:
                print(f"      🎉 SUCESSO! CTE 306 tem envio_final: {cte_306['envio_final']}")
            else:
                print(f"      ❌ PROBLEMA: CTE 306 não tem envio_final processado")
        else:
            print(f"\n   ⚠️ CTE 306 não foi encontrado nos registros processados")
    else:
        print(f"   ❌ PROBLEMA CRÍTICO: Nenhum registro com envio_final foi processado!")
        print(f"   🔍 Possíveis causas:")
        print(f"      1. Coluna '{coluna_envio_final}' não contém datas válidas")
        print(f"      2. Formato das datas não é reconhecido")
        print(f"      3. Valores estão em branco ou com caracteres especiais")
    
    return registros

def inserir_registros_banco_avancado(conn, registros):
    """Inserção avançada com verificação detalhada do envio_final"""
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
        )
        """
        
        inseridos = 0
        erros = 0
        registros_envio_final = 0
        cte_306_inserido = False
        
        print(f"\n💾 INSERÇÃO AVANÇADA NO BANCO:")
        print("=" * 50)
        
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
                    registro['envio_final'],  # ⭐ CAMPO CRÍTICO
                    registro['origem_dados']
                )
                
                # Executar inserção
                cursor.execute(insert_query, parametros)
                inseridos += 1
                
                # Contar registros com envio_final
                if registro['envio_final']:
                    registros_envio_final += 1
                
                # Verificar especificamente o CTE 306
                if registro['numero_cte'] == 306:
                    cte_306_inserido = True
                    print(f"   🎯 CTE 306 INSERIDO:")
                    print(f"      📅 Envio Final: {registro['envio_final']}")
                    if registro['envio_final']:
                        print(f"      ✅ COM ENVIO_FINAL! Problema resolvido!")
                    else:
                        print(f"      ❌ SEM ENVIO_FINAL - problema persiste")
                
                # Debug dos primeiros registros com envio_final
                if registro['envio_final'] and registros_envio_final <= 5:
                    print(f"   🎯 CTE {registro['numero_cte']}: Envio Final = {registro['envio_final']} ✅")
                
                # Mostrar progresso
                if i % 100 == 0:
                    print(f"   📊 {i}/{len(registros)} (envio_final: {registros_envio_final})")
                
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
        
        print(f"\n📊 RESULTADO DA INSERÇÃO:")
        print(f"   ✅ {inseridos} registros inseridos com sucesso")
        print(f"   🎯 {registros_envio_final} registros COM envio_final ⭐")
        print(f"   ❌ {erros} erros durante a inserção")
        
        if not cte_306_inserido:
            print(f"   ⚠️ CTE 306 não foi inserido (pode não estar no CSV)")
        
        if len(registros) > 0:
            taxa_sucesso = (inseridos / len(registros)) * 100
            taxa_envio_final = (registros_envio_final / inseridos) * 100 if inseridos > 0 else 0
            print(f"   📈 Taxa de sucesso: {taxa_sucesso:.1f}%")
            print(f"   🎯 Taxa envio_final: {taxa_envio_final:.1f}%")
        
        return inseridos > 0, registros_envio_final
        
    except Exception as e:
        print(f"❌ Erro crítico na inserção: {e}")
        conn.rollback()
        return False, 0

def verificar_resultado_final_detalhado(conn):
    """Verificação final detalhada com foco no envio_final"""
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print(f"\n🎯 VERIFICAÇÃO FINAL DETALHADA:")
        print("=" * 60)
        
        # Estatísticas gerais
        cursor.execute("SELECT COUNT(*) FROM dashboard_baker")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM dashboard_baker WHERE envio_final IS NOT NULL")
        com_envio_final = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM dashboard_baker WHERE data_emissao IS NOT NULL")
        com_emissao = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM dashboard_baker WHERE primeiro_envio IS NOT NULL")
        com_primeiro_envio = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM dashboard_baker WHERE data_atesto IS NOT NULL")
        com_atesto = cursor.fetchone()[0]
        
        print(f"📊 ESTATÍSTICAS GERAIS:")
        print(f"   📈 Total de registros: {total}")
        print(f"   📅 Com data emissão: {com_emissao} ({com_emissao/total*100:.1f}%)")
        print(f"   📤 Com 1º envio: {com_primeiro_envio} ({com_primeiro_envio/total*100:.1f}%)")
        print(f"   ✅ Com atesto: {com_atesto} ({com_atesto/total*100:.1f}%)")
        print(f"   🎯 Com envio final: {com_envio_final} ({com_envio_final/total*100:.1f}%) ⭐")
        
        # Verificar especificamente registros com envio_final
        if com_envio_final > 0:
            print(f"\n🎯 ANÁLISE DOS REGISTROS COM ENVIO_FINAL:")
            
            cursor.execute("""
                SELECT numero_cte, destinatario_nome, envio_final,
                       data_emissao, data_atesto, primeiro_envio
                FROM dashboard_baker 
                WHERE envio_final IS NOT NULL 
                ORDER BY numero_cte 
                LIMIT 15
            """)
            
            exemplos = cursor.fetchall()
            print(f"   📋 Primeiros {len(exemplos)} registros com envio_final:")
            print(f"       {'CTE':>6} {'Envio Final':>12} {'Cliente':>20}")
            print(f"       {'-'*6} {'-'*12} {'-'*20}")
            
            for ex in exemplos:
                cliente = (ex['destinatario_nome'] or 'N/A')[:18]
                print(f"       {ex['numero_cte']:>6} {ex['envio_final']} {cliente:>20}")
            
            # VERIFICAÇÃO ESPECÍFICA DO CTE 306
            print(f"\n🔍 VERIFICAÇÃO ESPECÍFICA - CTE 306:")
            cursor.execute("""
                SELECT numero_cte, destinatario_nome, envio_final, 
                       data_emissao, primeiro_envio, data_atesto,
                       created_at, origem_dados
                FROM dashboard_baker 
                WHERE numero_cte = 306
            """)
            
            cte_306 = cursor.fetchone()
            if cte_306:
                print(f"   ✅ CTE 306 encontrado no banco!")
                print(f"   📊 Dados do CTE 306:")
                print(f"      🔢 Número: {cte_306['numero_cte']}")
                print(f"      👤 Cliente: {cte_306['destinatario_nome'] or 'N/A'}")
                print(f"      📅 Data Emissão: {cte_306['data_emissao'] or 'N/A'}")
                print(f"      📤 1º Envio: {cte_306['primeiro_envio'] or 'N/A'}")
                print(f"      ✅ Atesto: {cte_306['data_atesto'] or 'N/A'}")
                print(f"      🎯 Envio Final: {cte_306['envio_final'] or 'N/A'}")
                print(f"      📝 Origem: {cte_306['origem_dados'] or 'N/A'}")
                print(f"      🕐 Inserido: {cte_306['created_at']}")
                
                if cte_306['envio_final']:
                    print(f"   🎉 SUCESSO TOTAL! CTE 306 foi importado COM envio_final!")
                    print(f"   ✅ Problema do usuário foi RESOLVIDO!")
                else:
                    print(f"   ❌ PROBLEMA AINDA EXISTE: CTE 306 sem envio_final no banco")
            else:
                print(f"   ❌ CTE 306 NÃO ENCONTRADO no banco")
                print(f"   💡 Possível causa: CTE 306 não existe no CSV ou foi filtrado")
                
                # Verificar CTEs próximos
                cursor.execute("""
                    SELECT numero_cte, envio_final 
                    FROM dashboard_baker 
                    WHERE numero_cte BETWEEN 300 AND 310
                    ORDER BY numero_cte
                """)
                proximos = cursor.fetchall()
                if proximos:
                    print(f"   🔍 CTEs próximos encontrados:")
                    for p in proximos:
                        status = "✅" if p['envio_final'] else "❌"
                        print(f"      {status} CTE {p['numero_cte']}: {p['envio_final'] or 'sem envio_final'}")
        
        else:
            print(f"\n❌ PROBLEMA CRÍTICO CONFIRMADO:")
            print(f"   🚨 Nenhum registro com envio_final foi inserido no banco!")
            print(f"   🔍 Possíveis causas:")
            print(f"      1. Mapeamento incorreto da coluna")
            print(f"      2. Formato de data não reconhecido")
            print(f"      3. Dados corrompidos ou em formato inesperado")
            print(f"      4. Erro na lógica de processamento")
        
        # Verificar integridade geral dos dados
        print(f"\n🔍 VERIFICAÇÃO DE INTEGRIDADE:")
        
        # Registros com diferentes combinações de campos
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(data_emissao) as com_emissao,
                COUNT(primeiro_envio) as com_primeiro_envio,
                COUNT(data_atesto) as com_atesto,
                COUNT(envio_final) as com_envio_final,
                COUNT(numero_fatura) as com_fatura
            FROM dashboard_baker
        """)
        
        integridade = cursor.fetchone()
        print(f"   📊 Campo por campo:")
        print(f"      📅 Data Emissão: {integridade['com_emissao']}/{integridade['total']}")
        print(f"      📤 1º Envio: {integridade['com_primeiro_envio']}/{integridade['total']}")
        print(f"      ✅ Atesto: {integridade['com_atesto']}/{integridade['total']}")
        print(f"      🎯 Envio Final: {integridade['com_envio_final']}/{integridade['total']} ⭐")
        print(f"      📄 Fatura: {integridade['com_fatura']}/{integridade['total']}")
        
        cursor.close()
        
        return com_envio_final > 0
        
    except Exception as e:
        print(f"❌ Erro na verificação final: {e}")
        return False

def limpar_banco_com_confirmacao(conn):
    """Limpa todos os dados da tabela dashboard_baker com confirmação detalhada"""
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM dashboard_baker")
        total_antes = cursor.fetchone()[0]
        
        print(f"\n🗑️ LIMPEZA DO BANCO DE DADOS")  
        print("=" * 50)
        print(f"📊 Registros atuais no banco: {total_antes}")
        
        if total_antes == 0:
            print("✅ Banco já está vazio, prosseguindo...")
            cursor.close()
            return True
        
        # Mostrar resumo dos dados atuais
        cursor.execute("""
            SELECT origem_dados, COUNT(*) as qtd
            FROM dashboard_baker 
            GROUP BY origem_dados
            ORDER BY qtd DESC
        """)
        
        origens = cursor.fetchall()
        if origens:
            print(f"📋 Dados por origem:")
            for origem in origens:
                origem_nome = origem[0] or 'N/A'
                print(f"   📁 {origem_nome}: {origem[1]} registros")
        
        print(f"\n⚠️ ATENÇÃO: Esta operação irá:")
        print(f"   🗑️ Apagar TODOS os {total_antes} registros")
        print(f"   🔄 Resetar a sequência de IDs")
        print(f"   🧹 Limpar completamente a tabela")
        print(f"\n💾 DADOS NÃO SERÃO PERDIDOS se você tiver:")
        print(f"   📄 Arquivo CSV original")
        print(f"   💾 Backup do banco de dados")
        
        confirmacao = input(f"\n🔄 CONFIRMA a limpeza completa? Digite 'LIMPAR' para confirmar: ")
        
        if confirmacao != 'LIMPAR':
            print("❌ Limpeza cancelada pelo usuário")
            cursor.close()
            return False
        
        print("🗑️ Executando limpeza completa...")
        cursor.execute("TRUNCATE TABLE dashboard_baker RESTART IDENTITY CASCADE")
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM dashboard_baker")
        total_depois = cursor.fetchone()[0]
        
        cursor.close()
        
        if total_depois == 0:
            print("✅ Tabela limpa com sucesso!")
            print("🎯 Banco pronto para receber novos dados")
            return True
        else:
            print(f"❌ Erro: ainda há {total_depois} registros")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao limpar banco: {e}")
        return False

def main():
    """Função principal com processamento avançado"""
    
    print("🚀 POPULAR BANCO POSTGRESQL - VERSÃO 3.0 AVANÇADA")
    print("=" * 80)
    print("🎯 FOCO CRÍTICO: Resolução completa do problema 'envio_final'")
    print("✅ Mapeamento inteligente com debugging avançado")
    print("✅ Processamento robusto de datas brasileiras")
    print("✅ Verificação detalhada de cada etapa")
    print("=" * 80)
    
    # 1. Conectar ao banco
    print(f"\n[1/8] 🔌 CONECTANDO AO BANCO...")
    conn = conectar_banco()
    if not conn:
        print("❌ Falha na conexão. Verifique o PostgreSQL e as credenciais.")
        return
    
    # 2. Limpar banco atual
    print(f"\n[2/8] 🗑️ LIMPANDO BANCO ATUAL...")
    if not limpar_banco_com_confirmacao(conn):
        print("❌ Operação cancelada na limpeza do banco")
        conn.close()
        return
    
    # 3. Carregar CSV com detecção avançada
    print(f"\n[3/8] 📂 CARREGANDO CSV COM DETECÇÃO AVANÇADA...")
    df, arquivo = carregar_csv_com_deteccao_avancada()
    if df is None:
        print("❌ Falha no carregamento do CSV")
        conn.close()
        return
    
    # 4. Criar mapeamento inteligente
    print(f"\n[4/8] 🧠 CRIANDO MAPEAMENTO INTELIGENTE...")
    mapeamento = criar_mapeamento_inteligente(df)
    
    if not mapeamento or not mapeamento.get('numero_cte'):
        print("❌ Falha no mapeamento - campo CTE não identificado")
        conn.close()
        return
    
    # Verificação crítica do envio_final
    if not mapeamento.get('envio_final'):
        print("🚨 ALERTA CRÍTICO: Campo 'envio_final' não foi mapeado!")
        print("   Este é exatamente o problema reportado pelo usuário.")
        
        continuar = input("   Continuar mesmo assim para debug? (s/N): ")
        if continuar.lower() not in ['s', 'sim']:
            conn.close()
            return
    
    # 5. Mapear dados com processamento avançado
    print(f"\n[5/8] 🔄 MAPEANDO DADOS COM PROCESSAMENTO AVANÇADO...")
    registros = mapear_dados_para_banco_avancado(df, mapeamento)
    
    if not registros:
        print("❌ Nenhum registro válido foi processado")
        conn.close()
        return
    
    # 6. Confirmação final antes da inserção
    print(f"\n[6/8] 🎯 CONFIRMAÇÃO FINAL...")
    registros_com_envio_final = sum(1 for r in registros if r['envio_final'])
    
    print(f"📊 RESUMO PRÉ-INSERÇÃO:")
    print(f"   📈 {len(registros)} registros processados")
    print(f"   🎯 {registros_com_envio_final} com envio_final")
    print(f"   📁 Arquivo: {arquivo}")
    print(f"   🗄️ Destino: {DB_CONFIG['database']}")
    
    if registros_com_envio_final == 0:
        print(f"\n⚠️ ATENÇÃO: Nenhum registro com envio_final será inserido!")
        print(f"   Isso significa que o problema do usuário NÃO será resolvido.")
        
        continuar = input(f"   Continuar para análise de debugging? (s/N): ")
        if continuar.lower() not in ['s', 'sim']:
            conn.close()
            return
    
    confirmacao = input(f"\n🔄 Continuar com a inserção? (s/N): ")
    
    if confirmacao.lower() not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada pelo usuário")
        conn.close()
        return
    
    # 7. Inserir dados com verificação avançada
    print(f"\n[7/8] 💾 INSERINDO DADOS COM VERIFICAÇÃO AVANÇADA...")
    sucesso, qtd_envio_final = inserir_registros_banco_avancado(conn, registros)
    
    # 8. Verificação final detalhada
    print(f"\n[8/8] 🔍 VERIFICAÇÃO FINAL DETALHADA...")
    if sucesso:
        tem_envio_final = verificar_resultado_final_detalhado(conn)
        
        print(f"\n" + "=" * 80)
        print(f"📊 RESULTADO FINAL:")
        print(f"   ✅ Inserção: {'SUCESSO' if sucesso else 'FALHA'}")
        print(f"   🎯 Registros com envio_final: {qtd_envio_final}")
        print(f"   📈 Taxa de importação: {(qtd_envio_final/len(registros)*100) if registros else 0:.1f}%")
        
        if tem_envio_final and qtd_envio_final > 0:
            print(f"   🎉 PROBLEMA DO USUÁRIO: RESOLVIDO! ✅")
            print(f"   🗄️ Campo 'envio_final' está sendo importado corretamente")
        else:
            print(f"   ❌ PROBLEMA DO USUÁRIO: AINDA EXISTE")
            print(f"   🔍 Necessária investigação adicional")
        
        print(f"\n🌐 PRÓXIMO PASSO:")
        print(f"   Execute o dashboard: streamlit run dashboard_baker_web_corrigido.py")
        print(f"   Verifique na aba 'CTEs Pendentes' se os dados aparecem corretamente")
        
    else:
        print(f"\n❌ FALHA NA INSERÇÃO")
        print(f"   Verifique os logs de erro acima")
        print(f"   Possível problema de conectividade ou permissões")
    
    conn.close()
    print(f"\n" + "=" * 80)
    print(f"🏁 PROCESSO CONCLUÍDO")
    
    # Salvar log de execução
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = f'execucao_importacao_{timestamp}.txt'
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Log de Execução - {timestamp}\n")
            f.write(f"Arquivo CSV: {arquivo}\n")
            f.write(f"Registros processados: {len(registros) if registros else 0}\n")
            f.write(f"Registros com envio_final: {qtd_envio_final}\n")
            f.write(f"Sucesso: {sucesso}\n")
            f.write(f"Mapeamento utilizado:\n")
            for campo, coluna in mapeamento.items():
                f.write(f"  {campo}: {coluna}\n")
        
        print(f"📝 Log salvo em: {log_file}")
        
    except:
        pass

if __name__ == "__main__":
    main()