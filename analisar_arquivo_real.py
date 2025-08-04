#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise do arquivo CSV real - Status Faturamento Ctes vs Faturas vs Atestos.csv
Mostra exatamente as colunas e permite mapeamento correto
"""

import pandas as pd
import os

def analisar_arquivo_real():
    """Analisa o arquivo CSV real e mostra estrutura exata"""
    
    print("🔍 ANÁLISE DO ARQUIVO REAL")
    print("=" * 50)
    
    # Nome exato do arquivo
    arquivo = "Status Faturamento   Ctes vs Faturas vs Atestos.csv"
    
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        print("\n📋 Arquivos CSV na pasta atual:")
        arquivos_csv = [f for f in os.listdir('.') if f.endswith('.csv')]
        for i, arq in enumerate(arquivos_csv, 1):
            print(f"   {i}. {arq}")
        
        if arquivos_csv:
            try:
                escolha = int(input(f"\nEscolha o arquivo (1-{len(arquivos_csv)}): ")) - 1
                if 0 <= escolha < len(arquivos_csv):
                    arquivo = arquivos_csv[escolha]
                    print(f"✅ Arquivo selecionado: {arquivo}")
                else:
                    print("❌ Escolha inválida")
                    return None
            except:
                print("❌ Entrada inválida")
                return None
        else:
            print("❌ Nenhum arquivo CSV encontrado")
            return None
    
    # Carregar arquivo
    print(f"\n📂 Carregando: {arquivo}")
    
    df = None
    encoding_usado = None
    
    # Tentar diferentes encodings
    encodings = ['utf-8', 'cp1252', 'latin1', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            df = pd.read_csv(arquivo, sep=';', encoding=encoding, on_bad_lines='skip')
            encoding_usado = encoding
            print(f"✅ Carregado com encoding: {encoding}")
            break
        except Exception as e:
            print(f"⚠️ Falha com {encoding}: {str(e)[:50]}")
    
    if df is None:
        print("❌ Não foi possível carregar o arquivo com nenhum encoding")
        return None
    
    print(f"📊 Total de registros: {len(df)}")
    print(f"📋 Total de colunas: {len(df.columns)}")
    
    # Mostrar TODAS as colunas com detalhes
    print("\n" + "="*80)
    print("📋 COLUNAS ENCONTRADAS NO ARQUIVO:")
    print("="*80)
    
    for i, coluna in enumerate(df.columns, 1):
        # Mostrar informações detalhadas da coluna
        valores_nao_vazios = df[coluna].notna().sum()
        valores_vazios = len(df) - valores_nao_vazios
        tipo_dados = df[coluna].dtype
        
        print(f"\n{i:2d}. COLUNA: '{coluna}'")
        print(f"    📊 Tipo: {tipo_dados}")
        print(f"    ✅ Não vazios: {valores_nao_vazios:3d} ({valores_nao_vazios/len(df)*100:.1f}%)")
        print(f"    ⚪ Vazios: {valores_vazios:3d} ({valores_vazios/len(df)*100:.1f}%)")
        
        # Mostrar amostra dos valores
        valores_amostra = df[coluna].dropna().head(3)
        if len(valores_amostra) > 0:
            print(f"    🔍 Amostra:")
            for j, valor in enumerate(valores_amostra, 1):
                valor_str = str(valor)[:50] + "..." if len(str(valor)) > 50 else str(valor)
                print(f"         {j}. '{valor_str}'")
        else:
            print(f"    ⚠️ Todos os valores estão vazios")
    
    print("\n" + "="*80)
    
    # Identificar candidatos para cada campo importante
    print("🎯 IDENTIFICAÇÃO AUTOMÁTICA DE CAMPOS:")
    print("="*50)
    
    campos_identificados = {}
    
    # 1. Campo CTE/Número
    print("\n🔍 CANDIDATOS PARA NÚMERO CTE:")
    candidatos_cte = []
    for coluna in df.columns:
        col_lower = coluna.lower()
        if any(palavra in col_lower for palavra in ['cte', 'número', 'numero', 'conhecimento']):
            valores_numericos = 0
            valores_totais = df[coluna].notna().sum()
            
            if valores_totais > 0:
                for valor in df[coluna].dropna().head(10):
                    try:
                        int(valor)
                        valores_numericos += 1
                    except:
                        pass
                
                score = valores_numericos / min(10, valores_totais) * 100
                candidatos_cte.append((coluna, score, valores_totais))
                print(f"   📊 '{coluna}': {valores_numericos}/{min(10, valores_totais)} numéricos ({score:.1f}%)")
    
    if candidatos_cte:
        melhor_cte = max(candidatos_cte, key=lambda x: x[1])
        campos_identificados['numero_cte'] = melhor_cte[0]
        print(f"   ✅ MELHOR: '{melhor_cte[0]}'")
    else:
        print("   ❌ Nenhum candidato encontrado")
    
    # 2. Campo Destinatário/Cliente
    print("\n🔍 CANDIDATOS PARA DESTINATÁRIO:")
    for coluna in df.columns:
        col_lower = coluna.lower()
        if any(palavra in col_lower for palavra in ['destinat', 'cliente', 'nome']):
            valores_texto = df[coluna].notna().sum()
            print(f"   📊 '{coluna}': {valores_texto} valores")
            if 'destinat' in col_lower:
                campos_identificados['destinatario'] = coluna
                print(f"   ✅ SELECIONADO: '{coluna}'")
    
    # 3. Campo Valor/Total
    print("\n🔍 CANDIDATOS PARA VALOR:")
    for coluna in df.columns:
        col_lower = coluna.lower()
        if any(palavra in col_lower for palavra in ['total', 'valor', 'r$']):
            valores_monetarios = 0
            valores_totais = df[coluna].notna().sum()
            
            if valores_totais > 0:
                for valor in df[coluna].dropna().head(5):
                    valor_str = str(valor)
                    if any(char in valor_str for char in ['R$', ',', '.']):
                        valores_monetarios += 1
                
                print(f"   📊 '{coluna}': {valores_monetarios}/{min(5, valores_totais)} parecem monetários")
                if 'total' in col_lower or valores_monetarios > 0:
                    campos_identificados['valor'] = coluna
                    print(f"   ✅ SELECIONADO: '{coluna}'")
    
    # 4. Campos de Data
    print("\n🔍 CANDIDATOS PARA DATAS:")
    for coluna in df.columns:
        col_lower = coluna.lower()
        if 'data' in col_lower or any(palavra in col_lower for palavra in ['emiss', 'baixa', 'envio', 'atesto']):
            valores_data = df[coluna].notna().sum()
            print(f"   📊 '{coluna}': {valores_data} valores")
            
            # Mapear datas específicas
            if 'emiss' in col_lower:
                campos_identificados['data_emissao'] = coluna
            elif 'baixa' in col_lower:
                campos_identificados['data_baixa'] = coluna
            elif 'inclusão' in col_lower and 'fatura' in col_lower:
                campos_identificados['data_inclusao_fatura'] = coluna
            elif 'envio' in col_lower and 'processo' in col_lower:
                campos_identificados['data_envio_processo'] = coluna
            elif '1º' in coluna and 'envio' in col_lower:
                campos_identificados['primeiro_envio'] = coluna
            elif 'rq' in col_lower or 'tmc' in col_lower:
                campos_identificados['data_rq_tmc'] = coluna
            elif 'atesto' in col_lower:
                campos_identificados['data_atesto'] = coluna
            elif 'final' in col_lower and 'envio' in col_lower:
                campos_identificados['envio_final'] = coluna
    
    # 5. Outros campos
    print("\n🔍 OUTROS CAMPOS:")
    for coluna in df.columns:
        col_lower = coluna.lower()
        if 'fatura' in col_lower and 'data' not in col_lower:
            campos_identificados['numero_fatura'] = coluna
            print(f"   📊 Fatura: '{coluna}'")
        elif 'veículo' in col_lower or 'veiculo' in col_lower or 'placa' in col_lower:
            campos_identificados['veiculo'] = coluna
            print(f"   📊 Veículo: '{coluna}'")
        elif 'observ' in col_lower or 'obs' in col_lower:
            campos_identificados['observacao'] = coluna
            print(f"   📊 Observação: '{coluna}'")
    
    print("\n" + "="*80)
    print("✅ MAPEAMENTO FINAL IDENTIFICADO:")
    print("="*80)
    
    for campo, coluna in campos_identificados.items():
        print(f"   {campo:20} -> '{coluna}'")
    
    # Salvar mapeamento em arquivo
    with open('mapeamento_colunas.txt', 'w', encoding='utf-8') as f:
        f.write("# MAPEAMENTO DE COLUNAS IDENTIFICADO AUTOMATICAMENTE\n")
        f.write(f"# Arquivo: {arquivo}\n")
        f.write(f"# Encoding: {encoding_usado}\n")
        f.write(f"# Data: {pd.Timestamp.now()}\n\n")
        
        f.write("MAPEAMENTO = {\n")
        for campo, coluna in campos_identificados.items():
            f.write(f"    '{campo}': '{coluna}',\n")
        f.write("}\n\n")
        
        f.write("TODAS_AS_COLUNAS = [\n")
        for coluna in df.columns:
            f.write(f"    '{coluna}',\n")
        f.write("]\n")
    
    print(f"\n💾 Mapeamento salvo em: mapeamento_colunas.txt")
    
    # Mostrar amostra dos dados
    print("\n" + "="*80)
    print("📊 AMOSTRA DOS DADOS (3 primeiras linhas):")
    print("="*80)
    
    if 'numero_cte' in campos_identificados:
        colunas_mostrar = [
            campos_identificados.get('numero_cte'),
            campos_identificados.get('destinatario', 'N/A'),
            campos_identificados.get('valor', 'N/A'),
            campos_identificados.get('data_emissao', 'N/A')
        ]
        colunas_mostrar = [col for col in colunas_mostrar if col != 'N/A' and col in df.columns]
        
        if colunas_mostrar:
            amostra = df[colunas_mostrar].head(3)
            for i, (index, row) in enumerate(amostra.iterrows(), 1):
                print(f"\n📋 REGISTRO {i}:")
                for col in colunas_mostrar:
                    valor = row[col]
                    if pd.isna(valor):
                        valor_str = "VAZIO"
                    else:
                        valor_str = f"'{valor}'"
                    print(f"   {col}: {valor_str}")
    
    print("\n" + "="*80)
    
    return df, campos_identificados, arquivo, encoding_usado

if __name__ == "__main__":
    resultado = analisar_arquivo_real()
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Verifique o mapeamento acima")
    print("2. Se estiver correto, execute: python popular_banco_com_mapeamento.py")
    print("3. Se precisar ajustar, edite o arquivo mapeamento_colunas.txt")
    print("4. Para diagnóstico detalhado: python diagnostico_csv.py")