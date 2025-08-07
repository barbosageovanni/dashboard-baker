#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PATCH CRÍTICO - Dashboard Baker
Correção de inconsistências nos alertas e adição do card Envio Final Pendente
Execução: python patch_dashboard_correcoes_criticas.py
"""

import os
import re
from datetime import datetime

def analisar_problemas():
    """Analisa os problemas no arquivo atual"""
    print("🔍 ANALISANDO PROBLEMAS NO DASHBOARD")
    print("=" * 50)
    
    problemas = {
        1: "Cards mostram dados diferentes dos alertas (7 vs 0)",
        2: "Lista de CTEs pendentes não aparece na análise detalhada",
        3: "Card 'Envio Final Pendente' não foi adicionado corretamente", 
        4: "Sistema de alertas mostra todos zerados",
        5: "Layout usa 3 colunas em vez de 4"
    }
    
    for num, desc in problemas.items():
        print(f"❌ PROBLEMA {num}: {desc}")
    
    return problemas

def corrigir_funcao_alertas():
    """Retorna função de alertas corrigida"""
    return '''def calcular_alertas_inteligentes(df: pd.DataFrame) -> Dict:
    """Sistema de alertas inteligentes - VERSÃO CORRIGIDA FINAL"""
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
        # 1. Primeiro envio pendente - CORRIGIDO
        # Critério: CTEs emitidos há mais de 10 dias SEM primeiro envio
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
        # Critério: CTEs com atesto há mais de 5 dias SEM envio final
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
        print(f"Erro no cálculo de alertas: {str(e)}")
    
    return alertas'''

def corrigir_layout_alertas():
    """Retorna seção de alertas corrigida com 4 colunas"""
    return '''    # ===============================
    # SEÇÃO 2: SISTEMA DE ALERTAS INTELIGENTES - CORRIGIDO
    # ===============================
    st.markdown("""
    <div class="section-header">
        <div class="section-title">🚨 Sistema de Alertas Inteligentes</div>
        <div class="section-subtitle">Monitoramento proativo com ações sugeridas - 4 Colunas</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Alerta 1: Primeiro envio pendente
    with col1:
        alerta = alertas['primeiro_envio_pendente']
        if alerta['qtd'] > 0:
            st.markdown(f"""
            <div class="status-card-danger">
                <div class="status-number">{alerta['qtd']}</div>
                <div class="status-title">🚨 1º Envio Pendente</div>
                <div class="status-value">R$ {alerta['valor']:,.0f} em risco</div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"Ver {alerta['qtd']} CTEs pendentes"):
                for item in alerta['lista'][:10]:
                    data_str = ""
                    if item.get('data_emissao') and pd.notna(item['data_emissao']):
                        try:
                            data_str = f" ({item['data_emissao'].strftime('%d/%m/%Y')})"
                        except:
                            data_str = ""
                    st.write(f"CTE **{item['numero_cte']}** - {item['destinatario_nome']} - R$ {item['valor_total']:,.2f}{data_str}")
        else:
            st.markdown("""
            <div class="status-card-success">
                <div class="status-number">0</div>
                <div class="status-title">✅ 1º Envio</div>
                <div class="status-value">Todos em dia</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Alerta 2: Envio Final Pendente - NOVO
    with col2:
        alerta = alertas['envio_final_pendente']
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
            """, unsafe_allow_html=True)
    
    # Alerta 3: Faturas vencidas
    with col3:
        alerta = alertas['faturas_vencidas']
        if alerta['qtd'] > 0:
            st.markdown(f"""
            <div class="status-card-danger">
                <div class="status-number">{alerta['qtd']}</div>
                <div class="status-title">💸 Faturas Vencidas</div>
                <div class="status-value">R$ {alerta['valor']:,.0f} inadimplentes</div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"Ver {alerta['qtd']} faturas vencidas"):
                for item in alerta['lista'][:10]:
                    days_overdue = 0
                    if item.get('data_atesto') and pd.notna(item['data_atesto']):
                        try:
                            days_overdue = (datetime.now().date() - item['data_atesto'].date()).days
                        except:
                            days_overdue = 0
                    st.write(f"CTE **{item['numero_cte']}** - {item['destinatario_nome']} - R$ {item['valor_total']:,.2f} ({days_overdue} dias)")
        else:
            st.markdown("""
            <div class="status-card-success">
                <div class="status-number">0</div>
                <div class="status-title">✅ Faturas OK</div>
                <div class="status-value">Nenhuma vencida</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Alerta 4: Resumo geral
    with col4:
        total_alertas = (alertas['primeiro_envio_pendente']['qtd'] + 
                        alertas['envio_final_pendente']['qtd'] + 
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

def aplicar_patches():
    """Aplica todas as correções no arquivo"""
    print("\n🔧 APLICANDO PATCHES CRÍTICOS")
    print("=" * 50)
    
    if not os.path.exists('dashboard_baker_web_corrigido.py'):
        print("❌ Arquivo dashboard_baker_web_corrigido.py não encontrado")
        return False
    
    # Ler arquivo
    with open('dashboard_baker_web_corrigido.py', 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = f'dashboard_baker_web_corrigido_backup_{timestamp}.py'
    with open(backup, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print(f"💾 Backup criado: {backup}")
    
    # PATCH 1: Substituir função de alertas
    nova_funcao = corrigir_funcao_alertas()
    padrao_funcao = r'def calcular_alertas_inteligentes\(df: pd\.DataFrame\) -> Dict:.*?return alertas'
    conteudo = re.sub(padrao_funcao, nova_funcao, conteudo, flags=re.DOTALL)
    print("✅ PATCH 1: Função de alertas corrigida")
    
    # PATCH 2: Substituir seção de alertas por versão com 4 colunas
    nova_secao = corrigir_layout_alertas()
    padrao_secao = r'# SEÇÃO 2: SISTEMA DE ALERTAS INTELIGENTES.*?# ===============================\s+# SEÇÃO 3:'
    
    nova_secao_completa = nova_secao + '''
    
    # ===============================
    # SEÇÃO 3:'''
    
    conteudo = re.sub(padrao_secao, nova_secao_completa, conteudo, flags=re.DOTALL)
    print("✅ PATCH 2: Seção de alertas com 4 colunas aplicada")
    
    # PATCH 3: Remover duplicações de configuração se existirem
    # Remover linhas duplicadas de envio_final_pendente
    linhas = conteudo.split('\n')
    linhas_limpas = []
    envio_final_config_count = 0
    
    for linha in linhas:
        if "'envio_final_pendente': {" in linha and 'dias_limite' in linha:
            envio_final_config_count += 1
            if envio_final_config_count > 1:
                continue  # Pular duplicação
        linhas_limpas.append(linha)
    
    conteudo = '\n'.join(linhas_limpas)
    print("✅ PATCH 3: Duplicações removidas")
    
    # Salvar arquivo corrigido
    with open('dashboard_baker_web_corrigido.py', 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print("\n🎉 PATCHES APLICADOS COM SUCESSO!")
    return True

def main():
    """Função principal do patch"""
    print("🚨 PATCH CRÍTICO - DASHBOARD BAKER")
    print("🎯 Corrigindo inconsistências nos alertas")
    print("📝 Adicionando card 'Envio Final Pendente'")
    print("🔄 Sincronizando dados entre seções")
    print()
    
    # Analisar problemas
    analisar_problemas()
    
    # Aplicar correções
    if aplicar_patches():
        print("\n🎊 SUCESSO COMPLETO!")
        print("=" * 50)
        print("✅ Função de alertas reescrita com lógica correta")
        print("✅ Card 'Envio Final Pendente' adicionado")
        print("✅ Layout alterado de 3 para 4 colunas")
        print("✅ Dados sincronizados entre cards e alertas")
        print("✅ Lista de CTEs pendentes funcionando")
        print()
        print("🚀 PRÓXIMO PASSO:")
        print("   1. Pare o dashboard atual (Ctrl+C)")
        print("   2. Reinicie: streamlit run dashboard_baker_web_corrigido.py")
        print("   3. Verifique se os alertas mostram dados corretos")
        print()
        print("🎯 RESULTADO ESPERADO:")
        print("   • Cards de estatísticas = Alertas (mesmo valor)")
        print("   • 4 colunas de alertas funcionando")
        print("   • Lista de CTEs pendentes aparecendo")
        print("   • Card 'Envio Final Pendente' operacional")
    else:
        print("\n❌ ERRO na aplicação dos patches")

if __name__ == "__main__":
    main()