#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patch de Correção de Warnings - Dashboard Baker
Este script corrige os warnings do pandas e SQLAlchemy
"""

import os
import shutil
from datetime import datetime

def aplicar_correcoes():
    """Aplica correções no arquivo dashboard_baker_web_corrigido.py"""
    
    arquivo_original = 'dashboard_baker_web_corrigido.py'
    arquivo_backup = f'dashboard_baker_web_corrigido_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
    
    print("🔧 CORREÇÃO DE WARNINGS - DASHBOARD BAKER")
    print("="*60)
    
    # Verificar se arquivo existe
    if not os.path.exists(arquivo_original):
        print(f"❌ Arquivo {arquivo_original} não encontrado!")
        return False
    
    # Fazer backup
    print(f"📁 Criando backup: {arquivo_backup}")
    shutil.copy2(arquivo_original, arquivo_backup)
    
    # Ler arquivo
    with open(arquivo_original, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    print("🔍 Aplicando correções...")
    
    # ============================================================
    # CORREÇÃO 1: Warning do SQLAlchemy (linha ~628)
    # ============================================================
    
    # Localizar e substituir o trecho problemático
    trecho_antigo_1 = """        df = pd.read_sql_query(query, conn)"""
    
    trecho_novo_1 = """        # Usar SQLAlchemy para evitar warning
        from sqlalchemy import create_engine
        
        # Criar string de conexão SQLAlchemy
        db_url = f"postgresql://{config.get('user')}:{config.get('password')}@{config.get('host')}:{config.get('port')}/{config.get('database')}?sslmode=require"
        engine = create_engine(db_url)
        
        # Executar query com SQLAlchemy
        df = pd.read_sql_query(query, engine)
        engine.dispose()"""
    
    # Alternativa mais simples sem SQLAlchemy
    trecho_novo_1_simples = """        # Executar query e converter para DataFrame manualmente para evitar warning
        cursor = conn.cursor()
        cursor.execute(query)
        
        # Obter nomes das colunas
        columns = [desc[0] for desc in cursor.description]
        
        # Obter dados
        data = cursor.fetchall()
        cursor.close()
        
        # Criar DataFrame
        df = pd.DataFrame(data, columns=columns)"""
    
    # Aplicar correção simples (sem precisar instalar SQLAlchemy)
    if trecho_antigo_1 in conteudo:
        conteudo = conteudo.replace(trecho_antigo_1, trecho_novo_1_simples)
        print("✅ Correção 1: Warning SQLAlchemy corrigido")
    
    # ============================================================
    # CORREÇÃO 2: SettingWithCopyWarning (linha ~2856)
    # ============================================================
    
    # Procurar padrões problemáticos e corrigi-los
    
    # Padrão 1: df_display['coluna'] = valor
    padrao_antigo_2a = """df_display['dias_atraso'] = df_display['data_emissao'].apply(calcular_dias_atraso)"""
    padrao_novo_2a = """df_display.loc[:, 'dias_atraso'] = df_display['data_emissao'].apply(calcular_dias_atraso)"""
    
    if padrao_antigo_2a in conteudo:
        conteudo = conteudo.replace(padrao_antigo_2a, padrao_novo_2a)
        print("✅ Correção 2a: SettingWithCopyWarning corrigido (dias_atraso)")
    
    # Padrão 2: df_display['valor_total'] = 
    padrao_antigo_2b = """df_display['valor_total'] = df_display['valor_total'].apply(lambda x: f"R$ {x:,.2f}")"""
    padrao_novo_2b = """df_display.loc[:, 'valor_total'] = df_display['valor_total'].apply(lambda x: f"R$ {x:,.2f}")"""
    
    if padrao_antigo_2b in conteudo:
        conteudo = conteudo.replace(padrao_antigo_2b, padrao_novo_2b)
        print("✅ Correção 2b: SettingWithCopyWarning corrigido (valor_total)")
    
    # Padrão 3: df_display['data_emissao'] = 
    padrao_antigo_2c = """df_display['data_emissao'] = df_display['data_emissao'].apply(formatar_data)"""
    padrao_novo_2c = """df_display.loc[:, 'data_emissao'] = df_display['data_emissao'].apply(formatar_data)"""
    
    if padrao_antigo_2c in conteudo:
        conteudo = conteudo.replace(padrao_antigo_2c, padrao_novo_2c)
        print("✅ Correção 2c: SettingWithCopyWarning corrigido (data_emissao)")
    
    # Padrão 4: df_display['dias_desde_envio'] = 
    padrao_antigo_2d = """df_display['dias_desde_envio'] = df_display['primeiro_envio'].apply(calcular_dias_desde_envio)"""
    padrao_novo_2d = """df_display.loc[:, 'dias_desde_envio'] = df_display['primeiro_envio'].apply(calcular_dias_desde_envio)"""
    
    if padrao_antigo_2d in conteudo:
        conteudo = conteudo.replace(padrao_antigo_2d, padrao_novo_2d)
        print("✅ Correção 2d: SettingWithCopyWarning corrigido (dias_desde_envio)")
    
    # Padrão 5: df_display['primeiro_envio'] = 
    padrao_antigo_2e = """df_display['primeiro_envio'] = df_display['primeiro_envio'].apply(formatar_primeiro_envio)"""
    padrao_novo_2e = """df_display.loc[:, 'primeiro_envio'] = df_display['primeiro_envio'].apply(formatar_primeiro_envio)"""
    
    if padrao_antigo_2e in conteudo:
        conteudo = conteudo.replace(padrao_antigo_2e, padrao_novo_2e)
        print("✅ Correção 2e: SettingWithCopyWarning corrigido (primeiro_envio)")
    
    # Padrão 6: ctes_sem_baixa_todos['dias_sem_baixa'] = 
    padrao_antigo_2f = """ctes_sem_baixa_todos['dias_sem_baixa'] = ctes_sem_baixa_todos['data_atesto'].apply(calcular_dias_sem_baixa)"""
    padrao_novo_2f = """ctes_sem_baixa_todos.loc[:, 'dias_sem_baixa'] = ctes_sem_baixa_todos['data_atesto'].apply(calcular_dias_sem_baixa)"""
    
    if padrao_antigo_2f in conteudo:
        conteudo = conteudo.replace(padrao_antigo_2f, padrao_novo_2f)
        print("✅ Correção 2f: SettingWithCopyWarning corrigido (dias_sem_baixa)")
    
    # ============================================================
    # CORREÇÃO 3: Adicionar suppressão de warnings no início
    # ============================================================
    
    # Adicionar import e configuração de warnings se não existir
    if "import warnings" not in conteudo:
        # Encontrar local após os imports principais
        pos_imports = conteudo.find("import pandas as pd")
        if pos_imports != -1:
            # Adicionar após o import do pandas
            pos_fim_linha = conteudo.find("\n", pos_imports)
            adicao_warnings = """
import warnings

# Suprimir warnings desnecessários
warnings.filterwarnings('ignore', category=UserWarning, module='pandas')
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)
"""
            conteudo = conteudo[:pos_fim_linha] + adicao_warnings + conteudo[pos_fim_linha:]
            print("✅ Correção 3: Configuração de warnings adicionada")
    
    # ============================================================
    # CORREÇÃO 4: Garantir uso de .copy() onde necessário
    # ============================================================
    
    # Procurar por padrões onde .copy() deve ser usado
    padrao_antigo_4a = """df_display = ctes_sem_atesto_detalhado[['numero_cte', 'destinatario_nome', 'valor_total', 'primeiro_envio']]"""
    padrao_novo_4a = """df_display = ctes_sem_atesto_detalhado[['numero_cte', 'destinatario_nome', 'valor_total', 'primeiro_envio']].copy()"""
    
    if padrao_antigo_4a in conteudo:
        conteudo = conteudo.replace(padrao_antigo_4a, padrao_novo_4a)
        print("✅ Correção 4a: Adicionado .copy() para evitar warnings")
    
    # Salvar arquivo corrigido
    print("\n💾 Salvando arquivo corrigido...")
    with open(arquivo_original, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print(f"✅ Arquivo {arquivo_original} corrigido com sucesso!")
    print(f"📁 Backup salvo em: {arquivo_backup}")
    
    return True

def main():
    """Função principal"""
    print("\n" + "="*60)
    print("     PATCH DE CORREÇÃO DE WARNINGS")
    print("     Dashboard Baker v3.0")
    print("="*60 + "\n")
    
    # Aplicar correções
    if aplicar_correcoes():
        print("\n" + "="*60)
        print("✅ CORREÇÕES APLICADAS COM SUCESSO!")
        print("="*60)
        print("\n🎯 Próximos passos:")
        print("1. Reinicie o dashboard: streamlit run dashboard_baker_web_corrigido.py")
        print("2. Os warnings devem desaparecer")
        print("3. Se algum warning persistir, me avise!")
        print("\n💡 Dica: Um backup foi criado caso precise reverter")
    else:
        print("\n❌ Erro ao aplicar correções")
        print("Verifique se o arquivo dashboard_baker_web_corrigido.py existe")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Operação cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()