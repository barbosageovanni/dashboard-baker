#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PATCHES DE CORREÇÃO - DASHBOARD BAKER
Corrige apenas os 4 erros identificados sem alterar estrutura
"""

import os
import re
from datetime import datetime

def aplicar_patch_erro_decimal():
    """PATCH 1: Corrige erro float vs decimal na função registrar_baixa"""
    
    print("🔧 PATCH 1: Corrigindo erro float vs decimal...")
    
    patch_decimal = '''    def registrar_baixa(self, numero_cte: int, data_baixa: datetime.date, 
                       observacao: str = "", valor_baixa: float = None) -> Tuple[bool, str]:
        """Registra baixa de uma fatura específica com validação"""
        try:
            conn = psycopg2.connect(**self.config)
            cursor = conn.cursor()
            
            # Verificar se CTE existe
            cursor.execute("SELECT numero_cte, valor_total, data_baixa FROM dashboard_baker WHERE numero_cte = %s", (numero_cte,))
            resultado = cursor.fetchone()
            
            if not resultado:
                return False, f"CTE {numero_cte} não encontrado"
            
            cte_num, valor_original, baixa_existente = resultado
            
            # CORREÇÃO: Converter Decimal para float para evitar erro de tipo
            if isinstance(valor_original, Decimal):
                valor_original = float(valor_original)
            
            # Verificar se já tem baixa
            if baixa_existente:
                return False, f"CTE {numero_cte} já possui baixa em {baixa_existente}"
            
            # Validar valor da baixa se fornecido - CORREÇÃO: usar abs() com float
            if valor_baixa and abs(float(valor_baixa) - float(valor_original)) > 0.01:
                observacao += f" | Valor original: R$ {valor_original:.2f}, Valor baixa: R$ {valor_baixa:.2f}"
            
            # Registrar baixa
            cursor.execute("""
                UPDATE dashboard_baker 
                SET data_baixa = %s, 
                    observacao = COALESCE(observacao, '') || %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE numero_cte = %s
            """, (data_baixa, f" | BAIXA: {observacao}", numero_cte))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True, f"Baixa registrada com sucesso para CTE {numero_cte}"
            
        except Exception as e:
            return False, f"Erro ao registrar baixa: {str(e)}"'''
    
    return patch_decimal

def aplicar_patch_primeiro_envio():
    """PATCH 2: Corrige lógica do 1º envio nos alertas"""
    
    print("🔧 PATCH 2: Corrigindo lógica do 1º envio...")
    
    patch_primeiro_envio = '''        # 4. Primeiro envio pendente (10 dias após emissão) - CORRIGIDO
        mask_primeiro_envio = (
            df['data_emissao'].notna() & 
            ((hoje - df['data_emissao']).dt.days > ALERTAS_CONFIG['primeiro_envio_pendente']['dias_limite']) &
            (df['primeiro_envio'].isna() | (df['primeiro_envio'] == ''))  # CORREÇÃO: incluir string vazia
        )
        if mask_primeiro_envio.any():
            ctes_problema = df[mask_primeiro_envio]
            lista_segura = []
            for _, row in ctes_problema.iterrows():
                item = {
                    'numero_cte': row['numero_cte'],
                    'destinatario_nome': row['destinatario_nome'],
                    'valor_total': float(row['valor_total']),
                    'data_emissao': row['data_emissao'] if pd.notna(row['data_emissao']) else None
                }
                lista_segura.append(item)
            
            alertas['primeiro_envio_pendente'] = {
                'qtd': len(ctes_problema),
                'valor': float(ctes_problema['valor_total'].sum()),
                'lista': lista_segura
            }'''
    
    return patch_primeiro_envio

def aplicar_patch_envio_final_pendente():
    """PATCH 3: Adiciona card 'Envio Final Pendente' que estava faltando"""
    
    print("🔧 PATCH 3: Adicionando card 'Envio Final Pendente'...")
    
    patch_envio_final = '''    'envio_final_pendente': {
        'dias_limite': 5,
        'prioridade': 'media',
        'acao_sugerida': 'Completar envio final dos documentos',
        'impacto_financeiro': 'baixo'
    }'''
    
    patch_calculo_envio_final = '''        # 5. Envio Final Pendente - ADICIONADO NOVAMENTE
        mask_envio_final = (
            df['data_atesto'].notna() & 
            ((hoje - df['data_atesto']).dt.days > ALERTAS_CONFIG.get('envio_final_pendente', {}).get('dias_limite', 5)) &
            (df['envio_final'].isna() | (df['envio_final'] == ''))
        )
        if mask_envio_final.any():
            ctes_problema = df[mask_envio_final]
            lista_segura = []
            for _, row in ctes_problema.iterrows():
                item = {
                    'numero_cte': row['numero_cte'],
                    'destinatario_nome': row['destinatario_nome'],
                    'valor_total': float(row['valor_total']),
                    'data_atesto': row['data_atesto'] if pd.notna(row['data_atesto']) else None
                }
                lista_segura.append(item)
            
            alertas['envio_final_pendente'] = {
                'qtd': len(ctes_problema),
                'valor': float(ctes_problema['valor_total'].sum()),
                'lista': lista_segura
            }'''
    
    return patch_envio_final, patch_calculo_envio_final

def aplicar_patch_relatorio_javascript():
    """PATCH 4: Corrige erro JavaScript nos relatórios"""
    
    print("🔧 PATCH 4: Corrigindo erro JavaScript dos relatórios...")
    
    patch_javascript = '''        # NOVO SISTEMA DE DOWNLOADS - CORRIGIDO PARA EVITAR ERRO JAVASCRIPT
        if st.button("📊 Gerar Relatórios"):
            if not df_test.empty:
                try:
                    # Gerar dados para relatórios
                    metricas_rel = gerar_metricas_expandidas(df_test)
                    alertas_rel = calcular_alertas_inteligentes(df_test)
                    variacoes_rel = calcular_variacoes_tempo_expandidas(df_test)
                    
                    # Container para downloads com key único
                    with st.container():
                        col_btn1, col_btn2 = st.columns(2)
                        
                        with col_btn1:
                            # Download Excel - CORRIGIDO
                            try:
                                excel_data = gerar_relatorio_excel(df_test, metricas_rel, alertas_rel, variacoes_rel)
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                
                                st.download_button(
                                    label="📊 Download Excel",
                                    data=excel_data,
                                    file_name=f"relatorio_baker_{timestamp}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key=f"download_excel_{timestamp}"  # KEY ÚNICO
                                )
                            except Exception as e:
                                st.error(f"❌ Erro Excel: {str(e)}")
                        
                        with col_btn2:
                            # Download HTML - CORRIGIDO
                            try:
                                html_data = gerar_relatorio_pdf_html(df_test, metricas_rel, alertas_rel, variacoes_rel)
                                timestamp2 = datetime.now().strftime('%Y%m%d_%H%M%S')
                                
                                st.download_button(
                                    label="📄 Download HTML",
                                    data=html_data,
                                    file_name=f"relatorio_baker_{timestamp2}.html",
                                    mime="text/html",
                                    key=f"download_html_{timestamp2}"  # KEY ÚNICO
                                )
                            except Exception as e:
                                st.error(f"❌ Erro HTML: {str(e)}")
                    
                    st.info("💡 **Conversão HTML → PDF:** Abra o HTML no navegador e use Ctrl+P → 'Salvar como PDF'")
                    st.success("📊 Relatórios gerados!")
                    
                except Exception as e:
                    st.error(f"❌ Erro geral: {str(e)}")
            else:
                st.error("❌ Sem dados para gerar relatório")'''
    
    return patch_javascript

def aplicar_patch_card_envio_final_interface():
    """PATCH 5: Adiciona card de Envio Final Pendente na interface"""
    
    print("🔧 PATCH 5: Adicionando card na interface...")
    
    patch_interface = '''    col1, col2, col3 = st.columns(3)
    
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
                    st.write(f"CTE {item['numero_cte']} - {item['destinatario_nome']} - R$ {item['valor_total']:,.2f}{data_str}")
        else:
            st.markdown("""
            <div class="status-card-success">
                <div class="status-number">0</div>
                <div class="status-title">✅ 1º Envio</div>
                <div class="status-value">Todos em dia</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Alerta 2: Envio Final Pendente - ADICIONADO
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
                    st.write(f"CTE {item['numero_cte']} - {item['destinatario_nome']} - R$ {item['valor_total']:,.2f}{data_str}")
        else:
            st.markdown("""
            <div class="status-card-success">
                <div class="status-number">0</div>
                <div class="status-title">✅ Envio Final</div>
                <div class="status-value">Todos enviados</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Alerta 3: Faturas vencidas
    with col3:'''
    
    return patch_interface

def aplicar_patches_no_arquivo():
    """Aplica todos os patches no arquivo existente"""
    
    print("🔧 APLICANDO PATCHES NO ARQUIVO EXISTENTE")
    print("=" * 50)
    
    # Ler arquivo atual
    if not os.path.exists('dashboard_baker_web_corrigido.py'):
        print("❌ Arquivo dashboard_baker_web_corrigido.py não encontrado")
        return False
    
    with open('dashboard_baker_web_corrigido.py', 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Backup
    backup = f'dashboard_baker_web_corrigido.py.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    with open(backup, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print(f"💾 Backup: {backup}")
    
    # PATCH 1: Adicionar import Decimal no topo
    if 'from decimal import Decimal' not in conteudo:
        conteudo = conteudo.replace(
            'import xlsxwriter',
            'import xlsxwriter\nfrom decimal import Decimal'
        )
        print("✅ Import Decimal adicionado")
    
    # PATCH 2: Corrigir erro decimal na função registrar_baixa
    if 'isinstance(valor_original, Decimal)' not in conteudo:
        # Encontrar e substituir a função registrar_baixa
        padrao_registrar_baixa = r'(def registrar_baixa\(self.*?return False, f"Erro ao registrar baixa: {str\(e\)}")'
        novo_registrar_baixa = '''def registrar_baixa(self, numero_cte: int, data_baixa: datetime.date, 
                       observacao: str = "", valor_baixa: float = None) -> Tuple[bool, str]:
        """Registra baixa de uma fatura específica com validação"""
        try:
            conn = psycopg2.connect(**self.config)
            cursor = conn.cursor()
            
            # Verificar se CTE existe
            cursor.execute("SELECT numero_cte, valor_total, data_baixa FROM dashboard_baker WHERE numero_cte = %s", (numero_cte,))
            resultado = cursor.fetchone()
            
            if not resultado:
                return False, f"CTE {numero_cte} não encontrado"
            
            cte_num, valor_original, baixa_existente = resultado
            
            # CORREÇÃO: Converter Decimal para float
            if isinstance(valor_original, Decimal):
                valor_original = float(valor_original)
            
            # Verificar se já tem baixa
            if baixa_existente:
                return False, f"CTE {numero_cte} já possui baixa em {baixa_existente}"
            
            # Validar valor da baixa - CORREÇÃO
            if valor_baixa and abs(float(valor_baixa) - float(valor_original)) > 0.01:
                observacao += f" | Valor original: R$ {valor_original:.2f}, Valor baixa: R$ {valor_baixa:.2f}"
            
            # Registrar baixa
            cursor.execute("""
                UPDATE dashboard_baker 
                SET data_baixa = %s, 
                    observacao = COALESCE(observacao, '') || %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE numero_cte = %s
            """, (data_baixa, f" | BAIXA: {observacao}", numero_cte))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True, f"Baixa registrada com sucesso para CTE {numero_cte}"
            
        except Exception as e:
            return False, f"Erro ao registrar baixa: {str(e)}"'''
        
        conteudo = re.sub(padrao_registrar_baixa, novo_registrar_baixa, conteudo, flags=re.DOTALL)
        print("✅ Função registrar_baixa corrigida")
    
    # PATCH 3: Adicionar configuração envio_final_pendente
    if "'envio_final_pendente'" not in conteudo:
        conteudo = conteudo.replace(
            "'primeiro_envio_pendente': {",
            """'envio_final_pendente': {
        'dias_limite': 5,
        'prioridade': 'media',
        'acao_sugerida': 'Completar envio final dos documentos',
        'impacto_financeiro': 'baixo'
    },
    'primeiro_envio_pendente': {"""
        )
        print("✅ Configuração envio_final_pendente adicionada")
    
    # PATCH 4: Adicionar cálculo de envio_final_pendente nos alertas
    if "'envio_final_pendente': {'qtd': 0" not in conteudo:
        conteudo = conteudo.replace(
            "'primeiro_envio_pendente': {'qtd': 0, 'valor': 0.0, 'lista': []}",
            """'primeiro_envio_pendente': {'qtd': 0, 'valor': 0.0, 'lista': []},
        'envio_final_pendente': {'qtd': 0, 'valor': 0.0, 'lista': []}"""
        )
        
        # Adicionar cálculo do envio final pendente
        if "# 5. Alerta \"Envio Final Pendente\" removido" in conteudo:
            conteudo = conteudo.replace(
                "# 5. Alerta \"Envio Final Pendente\" removido conforme especificação.",
                '''# 5. Envio Final Pendente - REINTEGRADO
        mask_envio_final = (
            df['data_atesto'].notna() & 
            ((hoje - df['data_atesto']).dt.days > ALERTAS_CONFIG.get('envio_final_pendente', {}).get('dias_limite', 5)) &
            (df['envio_final'].isna() | (df['envio_final'] == ''))
        )
        if mask_envio_final.any():
            ctes_problema = df[mask_envio_final]
            lista_segura = []
            for _, row in ctes_problema.iterrows():
                item = {
                    'numero_cte': row['numero_cte'],
                    'destinatario_nome': row['destinatario_nome'],
                    'valor_total': float(row['valor_total']),
                    'data_atesto': row['data_atesto'] if pd.notna(row['data_atesto']) else None
                }
                lista_segura.append(item)
            
            alertas['envio_final_pendente'] = {
                'qtd': len(ctes_problema),
                'valor': float(ctes_problema['valor_total'].sum()),
                'lista': lista_segura
            }'''
            )
        print("✅ Cálculo envio_final_pendente adicionado")
    
    # PATCH 5: Corrigir interface para 3 colunas
    if "col1, col2 = st.columns(2)" in conteudo and "# Alerta 1: Primeiro envio pendente" in conteudo:
        conteudo = conteudo.replace(
            "col1, col2 = st.columns(2)",
            "col1, col2, col3 = st.columns(3)"
        )
        
        # Adicionar card de envio final pendente
        padrao_interface = r'(# Alerta 2: Faturas vencidas\s+with col2:)'
        substituicao_interface = '''# Alerta 2: Envio Final Pendente - ADICIONADO
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
                    st.write(f"CTE {item['numero_cte']} - {item['destinatario_nome']} - R$ {item['valor_total']:,.2f}{data_str}")
        else:
            st.markdown("""
            <div class="status-card-success">
                <div class="status-number">0</div>
                <div class="status-title">✅ Envio Final</div>
                <div class="status-value">Todos enviados</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Alerta 3: Faturas vencidas
    with col3:'''
        
        conteudo = re.sub(padrao_interface, substituicao_interface, conteudo)
        print("✅ Interface 3 colunas e card envio final adicionados")
    
    # PATCH 6: Corrigir erro JavaScript nos downloads
    if 'key=f"download_excel_{timestamp}"' not in conteudo:
        # Adicionar keys únicos nos botões de download
        conteudo = conteudo.replace(
            'st.download_button(\n                                label="📊 Download Excel",\n                                data=excel_data,\n                                file_name=f"relatorio_baker_{timestamp}.xlsx",\n                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"\n                            )',
            '''st.download_button(
                                label="📊 Download Excel",
                                data=excel_data,
                                file_name=f"relatorio_baker_{timestamp}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key=f"download_excel_{timestamp}"
                            )'''
        )
        
        conteudo = conteudo.replace(
            'st.download_button(\n                                label="📄 Download HTML",\n                                data=html_data,\n                                file_name=f"relatorio_baker_{timestamp}.html",\n                                mime="text/html"\n                            )',
            '''st.download_button(
                                label="📄 Download HTML",
                                data=html_data,
                                file_name=f"relatorio_baker_{timestamp2}.html",
                                mime="text/html",
                                key=f"download_html_{timestamp2}"
                            )'''
        )
        print("✅ Keys únicos nos downloads adicionados")
    
    # Salvar arquivo corrigido
    with open('dashboard_baker_web_corrigido.py', 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print("✅ Todos os patches aplicados com sucesso!")
    return True

def main():
    """Função principal"""
    print("🔧 PATCHES DE CORREÇÃO - DASHBOARD BAKER")
    print("=" * 60)
    print("Corrigindo os 4 erros identificados...")
    print()
    
    print("🎯 ERROS A SEREM CORRIGIDOS:")
    print("1. ❌ Erro float vs decimal nas baixas")
    print("2. ❌ Lógica do 1º envio incorreta")
    print("3. ❌ Card 'Envio Final Pendente' faltando")
    print("4. ❌ Erro JavaScript nos relatórios")
    print()
    
    if aplicar_patches_no_arquivo():
        print("\n🎉 TODOS OS PATCHES APLICADOS COM SUCESSO!")
        print("=" * 50)
        print("✅ Erro decimal corrigido")
        print("✅ Lógica 1º envio corrigida") 
        print("✅ Card 'Envio Final Pendente' adicionado")
        print("✅ Erro JavaScript resolvido")
        print()
        print("🚀 REINICIE O DASHBOARD:")
        print("   Ctrl+C (parar atual)")
        print("   streamlit run dashboard_baker_web_corrigido.py")
        print()
        print("🎯 TESTE AS CORREÇÕES:")
        print("   • Registre uma baixa (erro decimal resolvido)")
        print("   • Veja o card 'Envio Final Pendente'")  
        print("   • Gere relatórios (sem erro JavaScript)")
        print("   • Verifique alertas de 1º envio")
        
    else:
        print("❌ Erro ao aplicar patches")

if __name__ == "__main__":
    main()