#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Baker - VERSÃO COMPLETA FINAL CORRIGIDA
✅ Análise de Produtividade (Variações de Tempo)
✅ Sistema de Conciliação Real
✅ Nova Aba para Inserção no PostgreSQL
✅ Correção do erro titlefont -> title
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import json
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuração da página
st.set_page_config(
    page_title="Dashboard Financeiro Baker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-card {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid;
        color: #000000;
        font-weight: 500;
    }
    .status-success { 
        border-color: #28a745; 
        background-color: #d4edda; 
        color: #155724;
    }
    .status-warning { 
        border-color: #ffc107; 
        background-color: #fff3cd; 
        color: #856404;
    }
    .status-danger { 
        border-color: #dc3545; 
        background-color: #f8d7da; 
        color: #721c24;
    }
    .status-info { 
        border-color: #17a2b8; 
        background-color: #d1ecf1; 
        color: #0c5460;
    }
    .valor-detalhado {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
    }
    .valor-item {
        color: #495057;
        font-weight: 500;
        margin: 0.3rem 0;
    }
    .conciliacao-destaque {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .api-info {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .database-section {
        background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Configuração do banco PostgreSQL
DB_CONFIG = {
    'host': 'localhost',
    'database': 'dashboard_baker',
    'user': 'postgres',
    'password': 'senha123',
    'port': 5432
}

def conectar_banco():
    """Conecta ao banco PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Erro ao conectar ao banco: {e}")
        return None

def carregar_dados_csv(arquivo):
    """Carrega e processa dados do CSV"""
    try:
        encodings = ['cp1252', 'utf-8', 'latin1']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(arquivo, sep=';', encoding=encoding, on_bad_lines='skip')
                break
            except:
                continue
        
        # Processar valores monetários
        if ' Total ' in df.columns:
            df['Valor_Numerico'] = (
                df[' Total '].astype(str)
                .str.replace('R$', '', regex=False)
                .str.replace('.', '', regex=False)
                .str.replace(',', '.', regex=False)
                .str.strip()
                .astype(float)
            )
        
        return df
    
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {str(e)}")
        return None

def processar_status_faturas(df):
    """Processa status das faturas"""
    com_fatura = df[df['Fatura'].notna() & (df['Fatura'] != '')]
    sem_fatura = df[df['Fatura'].isna() | (df['Fatura'] == '')]
    com_baixa = df[df['Data baixa'].notna() & (df['Data baixa'] != '')]
    sem_baixa = df[df['Data baixa'].isna() | (df['Data baixa'] == '')]
    
    valor_com_fatura = com_fatura['Valor_Numerico'].sum() if len(com_fatura) > 0 else 0
    valor_sem_fatura = sem_fatura['Valor_Numerico'].sum() if len(sem_fatura) > 0 else 0
    valor_com_baixa = com_baixa['Valor_Numerico'].sum() if len(com_baixa) > 0 else 0
    valor_sem_baixa = sem_baixa['Valor_Numerico'].sum() if len(sem_baixa) > 0 else 0
    
    return {
        'total': len(df),
        'com_fatura': len(com_fatura),
        'sem_fatura': len(sem_fatura),
        'com_baixa': len(com_baixa),
        'sem_baixa': len(sem_baixa),
        'valor_total': df['Valor_Numerico'].sum(),
        'valor_com_fatura': valor_com_fatura,
        'valor_sem_fatura': valor_sem_fatura,
        'valor_com_baixa': valor_com_baixa,
        'valor_sem_baixa': valor_sem_baixa
    }

def processar_variacoes_tempo(df):
    """Calcula TODAS as variações de tempo para análise de produtividade"""
    variacoes = {}
    
    # Converter colunas de data para datetime
    colunas_data = {
        'Data emissão Cte': 'data_emissao_cte',
        'Data INCLUSÃO Fatura Bsoft': 'data_inclusao_fatura',
        'Data Envio do processo Faturamento': 'data_envio_processo',
        '1º Envio': 'primeiro_envio',
        'Data RQ/TMC': 'data_rq_tmc',
        'Data do atesto': 'data_atesto',
        'Envio final': 'envio_final'
    }
    
    # Processar datas
    df_temp = df.copy()
    for col_original, col_nova in colunas_data.items():
        if col_original in df_temp.columns:
            df_temp[col_nova] = pd.to_datetime(df_temp[col_original], format='%d/%b/%y', errors='coerce')
    
    # 1. CTE vs Inclusão Fatura
    if 'data_emissao_cte' in df_temp.columns and 'data_inclusao_fatura' in df_temp.columns:
        mask = df_temp['data_emissao_cte'].notna() & df_temp['data_inclusao_fatura'].notna()
        if mask.any():
            dias = (df_temp.loc[mask, 'data_inclusao_fatura'] - df_temp.loc[mask, 'data_emissao_cte']).dt.days
            variacoes['cte_vs_inclusao_fatura'] = {
                'dados': dias,
                'media': dias.mean(),
                'mediana': dias.median(),
                'min': dias.min(),
                'max': dias.max(),
                'qtd_registros': len(dias),
                'titulo': 'CTE → Inclusão Fatura'
            }
    
    # 2. CTE vs Envio Processo
    if 'data_emissao_cte' in df_temp.columns and 'data_envio_processo' in df_temp.columns:
        mask = df_temp['data_emissao_cte'].notna() & df_temp['data_envio_processo'].notna()
        if mask.any():
            dias = (df_temp.loc[mask, 'data_envio_processo'] - df_temp.loc[mask, 'data_emissao_cte']).dt.days
            variacoes['cte_vs_envio_processo'] = {
                'dados': dias,
                'media': dias.mean(),
                'mediana': dias.median(),
                'min': dias.min(),
                'max': dias.max(),
                'qtd_registros': len(dias),
                'titulo': 'CTE → Envio Processo'
            }
    
    # 3. Inclusão Fatura vs Envio Processo
    if 'data_inclusao_fatura' in df_temp.columns and 'data_envio_processo' in df_temp.columns:
        mask = df_temp['data_inclusao_fatura'].notna() & df_temp['data_envio_processo'].notna()
        if mask.any():
            dias = (df_temp.loc[mask, 'data_envio_processo'] - df_temp.loc[mask, 'data_inclusao_fatura']).dt.days
            variacoes['inclusao_vs_envio_processo'] = {
                'dados': dias,
                'media': dias.mean(),
                'mediana': dias.median(),
                'min': dias.min(),
                'max': dias.max(),
                'qtd_registros': len(dias),
                'titulo': 'Inclusão Fatura → Envio Processo'
            }
    
    # 4. Inclusão Fatura vs 1º Envio
    if 'data_inclusao_fatura' in df_temp.columns and 'primeiro_envio' in df_temp.columns:
        mask = df_temp['data_inclusao_fatura'].notna() & df_temp['primeiro_envio'].notna()
        if mask.any():
            dias = (df_temp.loc[mask, 'primeiro_envio'] - df_temp.loc[mask, 'data_inclusao_fatura']).dt.days
            variacoes['inclusao_vs_primeiro_envio'] = {
                'dados': dias,
                'media': dias.mean(),
                'mediana': dias.median(),
                'min': dias.min(),
                'max': dias.max(),
                'qtd_registros': len(dias),
                'titulo': 'Inclusão Fatura → 1º Envio'
            }
    
    # 5. RQ/TMC vs 1º Envio
    if 'data_rq_tmc' in df_temp.columns and 'primeiro_envio' in df_temp.columns:
        mask = df_temp['data_rq_tmc'].notna() & df_temp['primeiro_envio'].notna()
        if mask.any():
            dias = (df_temp.loc[mask, 'primeiro_envio'] - df_temp.loc[mask, 'data_rq_tmc']).dt.days
            variacoes['rq_tmc_vs_primeiro_envio'] = {
                'dados': dias,
                'media': dias.mean(),
                'mediana': dias.median(),
                'min': dias.min(),
                'max': dias.max(),
                'qtd_registros': len(dias),
                'titulo': 'RQ/TMC → 1º Envio'
            }
    
    # 6. 1º Envio vs Atesto
    if 'primeiro_envio' in df_temp.columns and 'data_atesto' in df_temp.columns:
        mask = df_temp['primeiro_envio'].notna() & df_temp['data_atesto'].notna()
        if mask.any():
            dias = (df_temp.loc[mask, 'data_atesto'] - df_temp.loc[mask, 'primeiro_envio']).dt.days
            variacoes['primeiro_envio_vs_atesto'] = {
                'dados': dias,
                'media': dias.mean(),
                'mediana': dias.median(),
                'min': dias.min(),
                'max': dias.max(),
                'qtd_registros': len(dias),
                'titulo': '1º Envio → Atesto'
            }
    
    # 7. Atesto vs Envio Final
    if 'data_atesto' in df_temp.columns and 'envio_final' in df_temp.columns:
        mask = df_temp['data_atesto'].notna() & df_temp['envio_final'].notna()
        if mask.any():
            dias = (df_temp.loc[mask, 'envio_final'] - df_temp.loc[mask, 'data_atesto']).dt.days
            variacoes['atesto_vs_envio_final'] = {
                'dados': dias,
                'media': dias.mean(),
                'mediana': dias.median(),
                'min': dias.min(),
                'max': dias.max(),
                'qtd_registros': len(dias),
                'titulo': 'Atesto → Envio Final'
            }
    
    return variacoes

def gerar_graficos_principais_corrigidos(df, status):
    """Gera gráficos principais com correção do erro titlefont"""
    
    # 1. Gráfico de Status das Faturas
    fig_status = go.Figure(data=[
        go.Pie(
            labels=['Com Baixa', 'Sem Baixa', 'Sem Fatura'],
            values=[status['com_baixa'], status['sem_baixa'], status['sem_fatura']],
            hole=0.3,
            marker_colors=['#28a745', '#ffc107', '#dc3545']
        )
    ])
    
    # CORREÇÃO: Usar title ao invés de titlefont
    fig_status.update_layout(
        title={
            'text': "Distribuição Financeira por Status",
            'x': 0.5,
            'font': {'size': 16, 'color': '#1f77b4'}
        },
        showlegend=True,
        height=400
    )
    
    # 2. Análise por Cliente (se existir)
    fig_cliente = None
    if 'Destinatário - Nome' in df.columns:
        cliente_analise = (
            df.groupby('Destinatário - Nome')
            .agg({'Valor_Numerico': 'sum'})
            .sort_values('Valor_Numerico', ascending=False)
            .head(10)
        )
        
        fig_cliente = px.bar(
            x=cliente_analise.index,
            y=cliente_analise['Valor_Numerico'],
            title="Top 10 Clientes por Receita"
        )
        
        # CORREÇÃO: Usar title ao invés de titlefont
        fig_cliente.update_layout(
            xaxis={'title': {'text': 'Cliente', 'font': {'size': 12}}},
            yaxis={'title': {'text': 'Valor (R$)', 'font': {'size': 12}}},
            title={'x': 0.5, 'font': {'size': 16, 'color': '#1f77b4'}}
        )
    
    return fig_status, fig_cliente

def inserir_cte_banco(dados_cte):
    """Insere um novo CTE no banco PostgreSQL"""
    try:
        conn = conectar_banco()
        if not conn:
            return False, "Erro de conexão com o banco"
        
        cursor = conn.cursor()
        
        # Query de inserção
        query = """
        INSERT INTO dashboard_baker (
            numero_cte, destinatario_nome, veiculo_placa, valor_total,
            data_emissao, numero_fatura, data_baixa, observacao,
            data_inclusao_fatura, data_envio_processo, primeiro_envio,
            data_rq_tmc, data_atesto, envio_final, origem_dados
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        parametros = (
            dados_cte['numero_cte'],
            dados_cte['destinatario_nome'],
            dados_cte['veiculo_placa'],
            dados_cte['valor_total'],
            dados_cte['data_emissao'],
            dados_cte['numero_fatura'],
            dados_cte['data_baixa'],
            dados_cte['observacao'],
            dados_cte['data_inclusao_fatura'],
            dados_cte['data_envio_processo'],
            dados_cte['primeiro_envio'],
            dados_cte['data_rq_tmc'],
            dados_cte['data_atesto'],
            dados_cte['envio_final'],
            'FORMULARIO_WEB'
        )
        
        cursor.execute(query, parametros)
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return True, "CTE inserido com sucesso!"
        
    except psycopg2.IntegrityError as e:
        if "duplicate key" in str(e):
            return False, f"CTE {dados_cte['numero_cte']} já existe no banco"
        return False, f"Erro de integridade: {e}"
    except Exception as e:
        return False, f"Erro ao inserir CTE: {e}"

def carregar_ctes_banco():
    """Carrega CTEs do banco PostgreSQL"""
    try:
        conn = conectar_banco()
        if not conn:
            return pd.DataFrame()
        
        query = """
        SELECT * FROM dashboard_baker 
        ORDER BY created_at DESC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao carregar dados do banco: {e}")
        return pd.DataFrame()

def aba_dashboard_principal():
    """Aba principal do dashboard (original)"""
    st.header("📊 Dashboard Principal - Análise de Dados CSV")
    
    # Upload de arquivo
    arquivo_csv = st.file_uploader(
        "Carregar arquivo CSV",
        type=['csv'],
        help="Selecione o arquivo de relatório do Baker"
    )
    
    if arquivo_csv is not None:
        df = carregar_dados_csv(arquivo_csv)
        if df is not None:
            st.success(f"✅ Arquivo carregado: {len(df)} registros")
            
            # Processar dados
            status = processar_status_faturas(df)
            variacoes = processar_variacoes_tempo(df)
            
            # Métricas principais
            st.subheader("📊 Resumo Executivo")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total de Registros", f"{status['total']:,}")
            
            with col2:
                st.metric("Valor Total", f"R$ {status['valor_total']:,.2f}")
            
            with col3:
                st.metric("Com Fatura", f"{status['com_fatura']:,}")
            
            with col4:
                st.metric("Sem Documentos", f"{status['sem_fatura']:,}")
            
            # Gráficos corrigidos
            st.subheader("📈 Visualizações")
            
            fig_status, fig_cliente = gerar_graficos_principais_corrigidos(df, status)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(fig_status, use_container_width=True)
            
            with col2:
                if fig_cliente:
                    st.plotly_chart(fig_cliente, use_container_width=True)
                else:
                    st.info("Dados de cliente não disponíveis")
            
            # Análise de variações de tempo
            if variacoes:
                st.subheader("⏱️ Análise de Produtividade - Variações de Tempo")
                
                for key, var in variacoes.items():
                    if 'media' in var:
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric(
                                f"{var['titulo']} - Média",
                                f"{var['media']:.1f} dias"
                            )
                        
                        with col2:
                            st.metric(
                                f"{var['titulo']} - Mediana", 
                                f"{var['mediana']:.1f} dias"
                            )
                        
                        with col3:
                            st.metric(
                                f"{var['titulo']} - Registros",
                                f"{var['qtd_registros']}"
                            )

def aba_insercao_banco():
    """Nova aba para inserção de CTEs no banco PostgreSQL"""
    st.header("🗄️ Inserção de CTEs no Banco PostgreSQL")
    
    st.markdown("""
    <div class="database-section">
        <h3>💾 FORMULÁRIO DE INSERÇÃO DE CTES</h3>
        <p>✅ Inserção direta no banco PostgreSQL</p>
        <p>🔗 Dados integrados com o dashboard principal</p>
        <p>📊 Controle completo de todos os campos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Teste de conexão
    with st.expander("🔧 Teste de Conexão com Banco", expanded=False):
        if st.button("Testar Conexão PostgreSQL"):
            conn = conectar_banco()
            if conn:
                st.success("✅ Conexão com PostgreSQL estabelecida!")
                
                # Verificar estrutura da tabela
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = 'dashboard_baker'
                        ORDER BY ordinal_position;
                    """)
                    colunas = cursor.fetchall()
                    
                    if colunas:
                        st.write("📋 Estrutura da Tabela:")
                        for coluna, tipo in colunas:
                            st.write(f"  • {coluna}: {tipo}")
                    else:
                        st.warning("⚠️ Tabela 'dashboard_baker' não encontrada")
                    
                    cursor.close()
                    conn.close()
                    
                except Exception as e:
                    st.error(f"Erro ao verificar tabela: {e}")
            else:
                st.error("❌ Falha na conexão com PostgreSQL")
    
    # Formulário de inserção
    st.subheader("📝 Formulário de Inserção de Novo CTE")
    
    with st.form("inserir_cte_form"):
        col1, col2 = st.columns(2)
        
        # Campos obrigatórios
        with col1:
            st.write("**📋 Campos Obrigatórios:**")
            numero_cte = st.number_input(
                "Número CTE", 
                min_value=1, 
                step=1,
                help="Número único do Conhecimento de Transporte"
            )
            
            destinatario_nome = st.text_input(
                "Nome do Destinatário",
                help="Nome completo do cliente destinatário"
            )
            
            valor_total = st.number_input(
                "Valor Total (R$)",
                min_value=0.0,
                format="%.2f",
                help="Valor total do frete em reais"
            )
            
            data_emissao = st.date_input(
                "Data de Emissão",
                value=datetime.now().date(),
                help="Data de emissão do CTE"
            )
        
        with col2:
            st.write("**🚛 Campos Complementares:**")
            veiculo_placa = st.text_input(
                "Placa do Veículo",
                help="Placa do veículo utilizado no transporte"
            )
            
            numero_fatura = st.text_input(
                "Número da Fatura",
                help="Número da fatura gerada (opcional)"
            )
            
            observacao = st.text_area(
                "Observações",
                help="Observações gerais sobre o CTE"
            )
        
        # Campos de datas (opcionais)
        st.write("**📅 Datas do Processo (Opcionais):**")
        
        col3, col4, col5 = st.columns(3)
        
        with col3:
            data_inclusao_fatura = st.date_input(
                "Data Inclusão Fatura",
                value=None,
                help="Data de inclusão da fatura no sistema"
            )
            
            data_envio_processo = st.date_input(
                "Data Envio Processo",
                value=None,
                help="Data de envio do processo de faturamento"
            )
        
        with col4:
            primeiro_envio = st.date_input(
                "1º Envio",
                value=None,
                help="Data do primeiro envio da documentação"
            )
            
            data_rq_tmc = st.date_input(
                "Data RQ/TMC",
                value=None,
                help="Data do RQ/TMC"
            )
        
        with col5:
            data_atesto = st.date_input(
                "Data do Atesto",
                value=None,
                help="Data do atesto da documentação"
            )
            
            envio_final = st.date_input(
                "Envio Final",
                value=None,
                help="Data do envio final"
            )
        
        # Campo de baixa
        st.write("**💰 Controle de Baixa:**")
        data_baixa = st.date_input(
            "Data da Baixa",
            value=None,
            help="Data da baixa/pagamento (deixe vazio se não foi pago)"
        )
        
        # Botão de submissão
        submitted = st.form_submit_button("🚀 Inserir CTE no Banco", type="primary")
        
        if submitted:
            # Validações
            if not numero_cte:
                st.error("❌ Número CTE é obrigatório!")
            elif not destinatario_nome.strip():
                st.error("❌ Nome do destinatário é obrigatório!")
            elif valor_total <= 0:
                st.error("❌ Valor total deve ser maior que zero!")
            else:
                # Preparar dados
                dados_cte = {
                    'numero_cte': int(numero_cte),
                    'destinatario_nome': destinatario_nome.strip(),
                    'veiculo_placa': veiculo_placa.strip() if veiculo_placa else None,
                    'valor_total': float(valor_total),
                    'data_emissao': data_emissao,
                    'numero_fatura': numero_fatura.strip() if numero_fatura else None,
                    'data_baixa': data_baixa,
                    'observacao': observacao.strip() if observacao else None,
                    'data_inclusao_fatura': data_inclusao_fatura,
                    'data_envio_processo': data_envio_processo,
                    'primeiro_envio': primeiro_envio,
                    'data_rq_tmc': data_rq_tmc,
                    'data_atesto': data_atesto,
                    'envio_final': envio_final
                }
                
                # Inserir no banco
                sucesso, mensagem = inserir_cte_banco(dados_cte)
                
                if sucesso:
                    st.success(f"✅ {mensagem}")
                    st.balloons()
                    
                    # Mostrar resumo
                    with st.expander("📋 Resumo do CTE Inserido", expanded=True):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**CTE Número:** {numero_cte}")
                            st.write(f"**Cliente:** {destinatario_nome}")
                            st.write(f"**Valor:** R$ {valor_total:,.2f}")
                            st.write(f"**Data Emissão:** {data_emissao.strftime('%d/%m/%Y')}")
                        
                        with col2:
                            if veiculo_placa:
                                st.write(f"**Veículo:** {veiculo_placa}")
                            if numero_fatura:
                                st.write(f"**Fatura:** {numero_fatura}")
                            if data_baixa:
                                st.write(f"**Data Baixa:** {data_baixa.strftime('%d/%m/%Y')}")
                                st.write("**Status:** 💚 Pago")
                            else:
                                st.write("**Status:** 🟡 Em Aberto")
                else:
                    st.error(f"❌ {mensagem}")
    
    # Visualização dos dados do banco
    st.subheader("📊 CTEs Cadastrados no Banco")
    
    # Carregar dados do banco
    df_banco = carregar_ctes_banco()
    
    if not df_banco.empty:
        # Estatísticas rápidas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total CTEs", len(df_banco))
        
        with col2:
            valor_total_banco = df_banco['valor_total'].sum()
            st.metric("Valor Total", f"R$ {valor_total_banco:,.2f}")
        
        with col3:
            ctes_pagos = len(df_banco[df_banco['data_baixa'].notna()])
            st.metric("CTEs Pagos", ctes_pagos)
        
        with col4:
            ctes_abertos = len(df_banco[df_banco['data_baixa'].isna()])
            st.metric("CTEs em Aberto", ctes_abertos)
        
        # Filtros
        with st.expander("🔍 Filtros de Visualização", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                filtro_status = st.selectbox(
                    "Status",
                    ["Todos", "Pagos", "Em Aberto"]
                )
            
            with col2:
                filtro_origem = st.selectbox(
                    "Origem dos Dados",
                    ["Todos"] + list(df_banco['origem_dados'].unique())
                )
        
        # Aplicar filtros
        df_filtrado = df_banco.copy()
        
        if filtro_status == "Pagos":
            df_filtrado = df_filtrado[df_filtrado['data_baixa'].notna()]
        elif filtro_status == "Em Aberto":
            df_filtrado = df_filtrado[df_filtrado['data_baixa'].isna()]
        
        if filtro_origem != "Todos":
            df_filtrado = df_filtrado[df_filtrado['origem_dados'] == filtro_origem]
        
        # Mostrar tabela
        st.dataframe(
            df_filtrado[[
                'numero_cte', 'destinatario_nome', 'valor_total', 
                'data_emissao', 'data_baixa', 'origem_dados', 'created_at'
            ]],
            use_container_width=True
        )
        
        # Opção de download
        if st.button("📥 Baixar Dados do Banco (CSV)"):
            csv_banco = df_banco.to_csv(index=False, sep=';', encoding='utf-8')
            st.download_button(
                label="💾 Download CSV",
                data=csv_banco,
                file_name=f"ctes_banco_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    else:
        st.info("📝 Nenhum CTE cadastrado no banco ainda. Use o formulário acima para inserir o primeiro registro.")

def main():
    """Função principal com navegação por abas"""
    
    # Cabeçalho principal
    st.markdown('<h1 class="main-header">💰 Dashboard Financeiro Baker</h1>', 
                unsafe_allow_html=True)
    
    # Navegação por abas
    tab1, tab2 = st.tabs(["📊 Dashboard Principal", "🗄️ Inserção no Banco"])
    
    with tab1:
        aba_dashboard_principal()
    
    with tab2:
        aba_insercao_banco()
    
    # Rodapé
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        💰 Dashboard Financeiro Baker v2.0 | 
        ✅ Análise CSV + 🗄️ Integração PostgreSQL
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()