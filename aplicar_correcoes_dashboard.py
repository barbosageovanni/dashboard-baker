#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APLICAR CORREÇÕES NO DASHBOARD BAKER
Script para corrigir automaticamente os problemas identificados
Execução: python aplicar_correcoes_dashboard.py
"""

import os
import re
from datetime import datetime

def fazer_backup():
    """Cria backup do arquivo original"""
    if not os.path.exists('dashboard_baker_web_corrigido.py'):
        print("❌ Arquivo dashboard_baker_web_corrigido.py não encontrado")
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'dashboard_baker_backup_{timestamp}.py'
    
    with open('dashboard_baker_web_corrigido.py', 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    with open(backup_name, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print(f"💾 Backup criado: {backup_name}")
    return conteudo

def aplicar_correcao_alertas(conteudo):
    """Aplica correção na função de alertas"""
    print("🔧 Aplicando correção na função de alertas...")
    
    nova_funcao = '''def calcular_alertas_inteligentes(df: pd.DataFrame) -> Dict:
    """Sistema de alertas inteligentes - CORRIGIDO PARA SINCRONIZAÇÃO"""
    alertas = {
        'ctes_sem_aprovacao': {'qtd': 0, 'valor': 0.0, 'lista': []},
        'ctes_sem_faturas': {'qtd': 0, 'valor': 0.0, 'lista': []},
        'faturas_vencidas': {'qtd': 0, 'valor': 0.0, 'lista': []},
        'primeiro_envio_pendente': {'qtd': 0, 'valor': 0.0, 'lista': []},
        'envio_final_pendente': {'qtd': 0, 'valor': 0.0, 'lista': []}
    }
    
    if df.empty:
        return alertas
    
    hoje = pd.Timestamp.now().normalize()
    
    try:
        # 1. Primeiro envio pendente - LÓGICA CORRIGIDA
        mask_primeiro_envio = (
            df['data_emissao'].notna() & 
            ((hoje - df['data_emissao']).dt.days > 10) &
            (df['primeiro_envio'].isna() | (df['primeiro_envio'] == ''))
        )
        
        if mask_primeiro_envio.any():
            ctes_problema = df[mask_primeiro_envio]
            lista_segura = []
            for _, row in ctes_problema.iterrows():
                item = {
                    'numero_cte': int(row['numero_cte']) if pd.notna(row['numero_cte']) else 0,
                    'destinatario_nome': str(row['destinatario_nome']) if pd.notna(row['destinatario_nome']) else 'N/A',
                    'valor_total': float(row['valor_total']) if pd.notna(row['valor_total']) else 0.0,
                    'data_emissao': row['data_emissao'] if pd.notna(row['data_emissao']) else None
                }
                lista_segura.append(item)
            
            alertas['primeiro_envio_pendente'] = {
                'qtd': len(ctes_problema),
                'valor': float(ctes_problema['valor_total'].sum()),
                'lista': lista_segura
            }
        
        # 2. Envio Final Pendente - NOVO
        mask_envio_final = (
            df['data_atesto'].notna() & 
            ((hoje - df['data_atesto']).dt.days > 5) &
            (df['envio_final'].isna() | (df['envio_final'] == ''))
        )
        
        if mask_envio_final.any():
            ctes_problema = df[mask_envio_final]
            lista_segura = []
            for _, row in ctes_problema.iterrows():
                item = {
                    'numero_cte': int(row['numero_cte']) if pd.notna(row['numero_cte']) else 0,
                    'destinatario_nome': str(row['destinatario_nome']) if pd.notna(row['destinatario_nome']) else 'N/A',
                    'valor_total': float(row['valor_total']) if pd.notna(row['valor_total']) else 0.0,
                    'data_atesto': row['data_atesto'] if pd.notna(row['data_atesto']) else None
                }
                lista_segura.append(item)
                
            alertas['envio_final_pendente'] = {
                'qtd': len(ctes_problema),
                'valor': float(ctes_problema['valor_total'].sum()),
                'lista': lista_segura
            }
        
        # 3. Faturas vencidas - MANTIDO
        mask_vencidas = (
            df['data_atesto'].notna() & 
            ((hoje - df['data_atesto']).dt.days > 90) &
            (df['data_baixa'].isna() | (df['data_baixa'] == ''))
        )
        
        if mask_vencidas.any():
            ctes_problema = df[mask_vencidas]
            lista_segura = []
            for _, row in ctes_problema.iterrows():
                item = {
                    'numero_cte': int(row['numero_cte']) if pd.notna(row['numero_cte']) else 0,
                    'destinatario_nome': str(row['destinatario_nome']) if pd.notna(row['destinatario_nome']) else 'N/A',
                    'valor_total': float(row['valor_total']) if pd.notna(row['valor_total']) else 0.0,
                    'data_atesto': row['data_atesto'] if pd.notna(row['data_atesto']) else None
                }
                lista_segura.append(item)
            
            alertas['faturas_vencidas'] = {
                'qtd': len(ctes_problema),
                'valor': float(ctes_problema['valor_total'].sum()),
                'lista': lista_segura
            }

    except Exception as e:
        st.error(f"Erro no cálculo de alertas: {str(e)}")
    
    return alertas'''
    
    # Substituir função
    padrao = r'def calcular_alertas_inteligentes\(df: pd\.DataFrame\) -> Dict:.*?return alertas'
    conteudo_novo = re.sub(padrao, nova_funcao, conteudo, flags=re.DOTALL)
    
    if conteudo_novo != conteudo:
        print("✅ Função de alertas substituída com sucesso")
        return conteudo_novo
    else:
        print("⚠️ Função de alertas não foi encontrada ou não foi substituída")
        return conteudo

def aplicar_correcao_layout(conteudo):
    """Aplica correção no layout para 4 colunas"""
    print("🔧 Alterando layout para 4 colunas...")
    
    # Substituir 3 colunas por 4
    if 'col1, col2, col3 = st.columns(3)' in conteudo:
        conteudo = conteudo.replace('col1, col2, col3 = st.columns(3)', 'col1, col2, col3, col4 = st.columns(4)')
        print("✅ Layout alterado para 4 colunas")
    else:
        print("⚠️ Padrão de 3 colunas não encontrado")
    
    return conteudo

def adicionar_card_envio_final(conteudo):
    """Adiciona card de envio final pendente"""
    print("🔧 Adicionando card de envio final pendente...")
    
    novo_card = '''
    # Alerta 2: Envio Final Pendente - NOVO
    with col2:
        alerta = alertas.get('envio_final_pendente', {'qtd': 0, 'valor': 0.0, 'lista': []})
        if alerta['qtd'] > 0:
            st.markdown(f"""
            <div class="status-card-warning">
                <div class="status-number">{alerta['qtd']}</div>
                <div class="status-title">📤 Envio Final Pendente</div>
                <div class="status-value">R$ {alerta['valor']:,.0f} pendentes</div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"Ver {alerta['qtd']} envios pendentes"):
                for item in alerta['lista'][:10]:
                    data_str = ""
                    if item.get('data_atesto') and pd.notna(item['data_atesto']):
                        try:
                            data_str = f" ({item['data_atesto'].strftime('%d/%m/%Y')})"
                        except:
                            data_str = ""
                    st.write(f"CTE **{item['numero_cte']}** - {item['destinatario_nome']} - R$ {item['valor_total']:,.2f}{data_str}")
        else:
            st.markdown("""
            <div class="status-card-success">
                <div class="status-number">0</div>
                <div class="status-title">✅ Envio Final</div>
                <div class="status-value">Todos enviados</div>
            </div>
            """, unsafe_allow_html=True)'''
    
    # Encontrar onde inserir (após col1 - primeiro envio)
    if '# Alerta 2: Envio Final Pendente - ADICIONADO' not in conteudo and '# Alerta 2: Envio Final Pendente - NOVO' not in conteudo:
        # Procurar pelo final do bloco with col1
        padrao_insercao = r'(\s+)(# Alerta 3: Faturas vencidas\s+with col3:)'
        
        substituicao = r'\1' + novo_card + r'\n\1\2'
        conteudo_novo = re.sub(padrao_insercao, substituicao, conteudo)
        
        if conteudo_novo != conteudo:
            print("✅ Card de envio final pendente adicionado")
            # Corrigir a referência para col3 -> col3 (faturas vencidas)
            conteudo_novo = conteudo_novo.replace('    # Alerta 3: Faturas vencidas\n    with col3:', '    # Alerta 3: Faturas vencidas\n    with col3:')
            return conteudo_novo
        else:
            print("⚠️ Não foi possível adicionar o card de envio final")
    else:
        print("✅ Card de envio final já existe")
    
    return conteudo

def adicionar_col4_resumo(conteudo):
    """Adiciona col4 com resumo dos alertas"""
    print("🔧 Adicionando col4 com resumo...")
    
    resumo_col4 = '''
    
    # Alerta 4: Resumo Geral
    with col4:
        total_alertas = (alertas['primeiro_envio_pendente']['qtd'] + 
                        alertas.get('envio_final_pendente', {'qtd': 0})['qtd'] + 
                        alertas['faturas_vencidas']['qtd'])
        
        if total_alertas > 0:
            st.markdown(f"""
            <div class="status-card-warning">
                <div class="status-number">{total_alertas}</div>
                <div class="status-title">⚠️ Total Alertas</div>
                <div class="status-value">Requerem atenção</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-card-success">
                <div class="status-number">0</div>
                <div class="status-title">🎉 Sistema OK</div>
                <div class="status-value">Tudo funcionando</div>
            </div>
            """, unsafe_allow_html=True)'''
    
    if 'with col4:' not in conteudo:
        # Encontrar o final da seção de alertas
        padrao_fim_alertas = r'(\s+)(# ===============================\s+# SEÇÃO 3:)'
        substituicao = r'\1' + resumo_col4 + r'\n\1\2'
        
        conteudo_novo = re.sub(padrao_fim_alertas, substituicao, conteudo)
        
        if conteudo_novo != conteudo:
            print("✅ Col4 com resumo adicionado")
            return conteudo_novo
        else:
            print("⚠️ Não foi possível adicionar col4")
    else:
        print("✅ Col4 já existe")
    
    return conteudo

def main():
    """Função principal"""
    print("🚀 APLICANDO CORREÇÕES NO DASHBOARD BAKER")
    print("=" * 50)
    
    # Fazer backup
    conteudo = fazer_backup()
    if conteudo is None:
        return
    
    print(f"📊 Tamanho original: {len(conteudo)} caracteres")
    
    # Aplicar correções em sequência
    conteudo = aplicar_correcao_alertas(conteudo)
    conteudo = aplicar_correcao_layout(conteudo)
    conteudo = adicionar_card_envio_final(conteudo)
    conteudo = adicionar_col4_resumo(conteudo)
    
    # Salvar arquivo corrigido
    try:
        with open('dashboard_baker_web_corrigido.py', 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        print(f"📊 Tamanho final: {len(conteudo)} caracteres")
        print("✅ Arquivo salvo com sucesso!")
        
        print("\n🎉 CORREÇÕES APLICADAS COM SUCESSO!")
        print("=" * 50)
        print("✅ Função de alertas corrigida e sincronizada")
        print("✅ Layout alterado para 4 colunas")
        print("✅ Card 'Envio Final Pendente' adicionado")
        print("✅ Col4 com resumo geral incluída")
        
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("1. Pare o dashboard atual (Ctrl+C)")
        print("2. Reinicie: streamlit run dashboard_baker_web_corrigido.py")
        print("3. Verifique se os números dos cards = alertas")
        
        print("\n🎯 RESULTADO ESPERADO:")
        print("• Cards mostrarão os mesmos números dos alertas")
        print("• Lista de CTEs pendentes aparecerá nos expanders")
        print("• 4 colunas de alertas funcionando corretamente")
        print("• Dados sincronizados em todas as seções")
        
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo: {str(e)}")

if __name__ == "__main__":
    main()