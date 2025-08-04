#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico do CSV - Dashboard Baker
Identifica problemas no mapeamento dos dados
"""

import pandas as pd
import os

def diagnosticar_csv():
    """Diagnostica o arquivo CSV para identificar problemas de mapeamento"""
    
    print("🔍 DIAGNÓSTICO DO CSV - DASHBOARD BAKER")
    print("=" * 50)
    
    # Tentar encontrar o arquivo CSV
    possiveis_arquivos = [
        'Status Faturamento   Ctes vs Faturas vs Atestos.csv',
        'Relatório Faturamento Baker em aberto  Ctes vs Faturas vs Atestos.csv',
        'data/Status Faturamento   Ctes vs Faturas vs Atestos.csv'
    ]
    
    arquivo_encontrado = None
    df = None
    
    for arquivo in possiveis_arquivos:
        if os.path.exists(arquivo):
            try:
                # Tentar diferentes encodings
                encodings = ['cp1252', 'utf-8', 'latin1']
                
                for encoding in encodings:
                    try:
                        df = pd.read_csv(arquivo, sep=';', encoding=encoding, on_bad_lines='skip')
                        arquivo_encontrado = arquivo
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
        print("❌ Nenhum arquivo CSV encontrado ou carregável")
        return
    
    print(f"📊 Total de registros: {len(df)}")
    print()
    
    # 1. ANÁLISE DAS COLUNAS
    print("📋 COLUNAS ENCONTRADAS NO CSV:")
    print("-" * 40)
    
    for i, coluna in enumerate(df.columns, 1):
        print(f"{i:2d}. '{coluna}' (tipo: {df[coluna].dtype})")
    
    print()
    
    # 2. VERIFICAR COLUNAS ESPERADAS
    print("🎯 VERIFICAÇÃO DE COLUNAS ESPERADAS:")
    print("-" * 40)
    
    colunas_esperadas = {
        'Número Cte': ['Número Cte', 'CTE', 'Numero Cte', 'NumCte'],
        'Destinatário - Nome': ['Destinatário - Nome', 'Destinatario - Nome', 'Cliente', 'Destinatario'],
        'Valor': [' Total ', 'Total', 'Valor Total', 'Valor'],
        'Data emissão': ['Data emissão Cte', 'Data Emissao Cte', 'Data Emissao', 'Emissao']
    }
    
    colunas_encontradas = {}
    
    for campo_esperado, variacoes in colunas_esperadas.items():
        encontrada = False
        for variacao in variacoes:
            if variacao in df.columns:
                print(f"✅ {campo_esperado}: '{variacao}' encontrada")
                colunas_encontradas[campo_esperado] = variacao
                encontrada = True
                break
        
        if not encontrada:
            print(f"❌ {campo_esperado}: Não encontrada")
            # Mostrar colunas similares
            similares = [col for col in df.columns if any(palavra.lower() in col.lower() for palavra in campo_esperado.split())]
            if similares:
                print(f"   💡 Similares: {similares}")
    
    print()
    
    # 3. ANÁLISE ESPECÍFICA DA COLUNA CTE
    print("🔍 ANÁLISE DA COLUNA CTE:")
    print("-" * 30)
    
    coluna_cte = None
    for col in df.columns:
        if 'cte' in col.lower() or 'número' in col.lower():
            coluna_cte = col
            break
    
    if coluna_cte:
        print(f"📌 Coluna identificada: '{coluna_cte}'")
        
        # Verificar valores
        valores_cte = df[coluna_cte].dropna()
        print(f"📊 Valores não vazios: {len(valores_cte)}/{len(df)}")
        
        if len(valores_cte) > 0:
            print(f"📋 Primeiros 10 valores:")
            for i, valor in enumerate(valores_cte.head(10), 1):
                print(f"   {i:2d}. '{valor}' (tipo: {type(valor).__name__})")
            
            # Tentar converter para int
            print(f"\n🧪 Teste de conversão para inteiro:")
            conversoes_ok = 0
            conversoes_erro = 0
            
            for valor in valores_cte.head(20):
                try:
                    int_val = int(valor)
                    conversoes_ok += 1
                except:
                    conversoes_erro += 1
                    print(f"   ❌ Não pode converter: '{valor}'")
            
            print(f"   ✅ Conversões OK: {conversoes_ok}")
            print(f"   ❌ Conversões com erro: {conversoes_erro}")
        
        else:
            print("❌ Todos os valores estão vazios!")
    
    else:
        print("❌ Nenhuma coluna CTE identificada!")
        print("💡 Colunas que contêm números:")
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64'] or any(char.isdigit() for char in str(df[col].iloc[0]) if pd.notna(df[col].iloc[0])):
                print(f"   • '{col}': {df[col].dtype}")
    
    print()
    
    # 4. AMOSTRA DOS DADOS
    print("📊 AMOSTRA DOS DADOS (Primeiras 3 linhas):")
    print("-" * 45)
    
    # Mostrar apenas colunas principais
    colunas_importantes = []
    for col in df.columns:
        if any(palavra in col.lower() for palavra in ['cte', 'número', 'destinat', 'total', 'valor', 'emiss']):
            colunas_importantes.append(col)
    
    if colunas_importantes:
        amostra = df[colunas_importantes].head(3)
        for i, (index, row) in enumerate(amostra.iterrows(), 1):
            print(f"\n🔸 Linha {i}:")
            for col in colunas_importantes:
                valor = row[col]
                if pd.isna(valor):
                    valor_str = "VAZIO"
                else:
                    valor_str = f"'{valor}'"
                print(f"   {col}: {valor_str}")
    
    print()
    
    # 5. DIAGNÓSTICO E SOLUÇÕES
    print("🎯 DIAGNÓSTICO E SOLUÇÕES:")
    print("-" * 35)
    
    if coluna_cte is None:
        print("❌ PROBLEMA PRINCIPAL: Coluna CTE não identificada")
        print("💡 SOLUÇÕES:")
        print("   1. Verifique se existe uma coluna com números de CTE")
        print("   2. Renomeie a coluna para 'Número Cte'")
        print("   3. Ou informe qual coluna contém os números CTE")
        
    elif len(df[coluna_cte].dropna()) == 0:
        print("❌ PROBLEMA PRINCIPAL: Coluna CTE está vazia")
        print("💡 SOLUÇÕES:")
        print("   1. Verifique se os dados foram exportados corretamente")
        print("   2. Confirme se a coluna correta foi identificada")
        
    elif conversoes_erro > conversoes_ok:
        print("❌ PROBLEMA PRINCIPAL: Valores CTE não são números válidos")
        print("💡 SOLUÇÕES:")
        print("   1. Verifique o formato dos números CTE")
        print("   2. Remova caracteres especiais dos números")
        print("   3. Confirme se são números inteiros")
        
    else:
        print("✅ ESTRUTURA BÁSICA PARECE OK")
        print("💡 O problema pode ser na lógica de mapeamento")
    
    # 6. GERAR SCRIPT DE CORREÇÃO
    print("\n🔧 GERANDO SCRIPT DE CORREÇÃO...")
    
    if coluna_cte and len(df[coluna_cte].dropna()) > 0:
        script_correcao = f"""
# SCRIPT DE CORREÇÃO PERSONALIZADO
# Baseado na análise do seu CSV

def mapear_dados_csv_para_banco_corrigido(df):
    registros = []
    
    for index, row in df.iterrows():
        try:
            # COLUNA CTE IDENTIFICADA: '{coluna_cte}'
            numero_cte = row['{coluna_cte}']
            
            if pd.isna(numero_cte):
                continue
                
            # Tentar converter para int
            try:
                numero_cte = int(numero_cte)
            except:
                print(f"⚠️ Linha {{index+1}}: CTE '{{numero_cte}}' não é número válido")
                continue
            
            # Mapear outros campos
            registro = {{
                'numero_cte': numero_cte,
                'destinatario_nome': row.get('{colunas_encontradas.get("Destinatário - Nome", "CAMPO_NAO_ENCONTRADO")}', '').strip() if pd.notna(row.get('{colunas_encontradas.get("Destinatário - Nome", "CAMPO_NAO_ENCONTRADO")}')) else None,
                'valor_total': 0.0,  # Processar separadamente
                'origem_dados': 'CSV_CORRIGIDO'
            }}
            
            registros.append(registro)
            
        except Exception as e:
            print(f"⚠️ Erro na linha {{index+1}}: {{e}}")
            continue
    
    return registros
"""
        
        with open('correcao_mapeamento.py', 'w', encoding='utf-8') as f:
            f.write(script_correcao)
        
        print("✅ Script salvo em: correcao_mapeamento.py")
    
    print()
    print("=" * 50)
    print("🎯 Execute este diagnóstico e verifique as soluções propostas")
    print("📧 Se precisar de ajuda, compartilhe o resultado deste diagnóstico")

if __name__ == "__main__":
    diagnosticar_csv()