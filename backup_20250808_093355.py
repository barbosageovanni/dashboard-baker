#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Baker v3.0 - VERSÃO LIMPA (Sem HTML customizado)
Sistema de Gestão Financeira com PostgreSQL
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np
import os
from io import BytesIO
import xlsxwriter

# Verificar psycopg2
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    st.error("❌ psycopg2-binary não instalado. Execute: pip install psycopg2-binary")

# Configuração da página (sem CSS customizado)
st.set_page_config(
    page_title="Dashboard Baker v3.0",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CONFIGURAÇÃO DO BANCO
# ============================================================================

@st.cache_resource
def conectar_banco():
    """Conecta ao PostgreSQL"""
    if not PSYCOPG2_AVAILABLE:
        return None
    
    try:
        # Tentar secrets do Streamlit primeiro
        if hasattr(st, 'secrets') and 'PGHOST' in st.secrets:
            config = {
                'host': st.secrets['PGHOST'],
                'database': st.secrets.get('PGDATABASE', 'postgres'),
                'user': st.secrets.get('PGUSER', 'postgres'),
                'password': st.secrets['PGPASSWORD'],
                'port': int(st.secrets.get('PGPORT', '5432'))
            }
        else:
            # Configuração padrão
            config = {
                'host': os.getenv('PGHOST', 'db.lijtncazuwnbydeqtoyz.supabase.co'),
                'database': os.getenv('PGDATABASE', 'postgres'),
                'user': os.getenv('PGUSER', 'postgres'),
                'password': os.getenv('PGPASSWORD', 'SEQAg17334'),
                'port': int(os.getenv('PGPORT', '5432'))
            }
        
        conn = psycopg2.connect(**config)
        return conn
    except Exception as e:
        st.error(f"❌ Erro ao conectar: {e}")
        return None

@st.cache_data(ttl=300)
def carregar_dados():
    """Carrega dados do PostgreSQL"""
    conn = conectar_banco()
    if not conn:
        return pd.DataFrame()
    
    try:
        query = """
        SELECT numero_cte, destinatario_nome, veiculo_placa, valor_total,
               data_emissao, numero_fatura, data_baixa, observacao,
               primeiro_envio, data_atesto, envio_final
        FROM dashboard_baker 
        ORDER BY numero_cte DESC
        LIMIT 1000
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Converter colunas
        date_cols = ['data_emissao', 'data_baixa', 'primeiro_envio', 'data_atesto', 'envio_final']
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        if 'valor_total' in df.columns:
            df['valor_total'] = pd.to_numeric(df['valor_total'], errors='coerce').fillna(0)
        
        return df
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        return pd.DataFrame()

# ============================================================================
# INTERFACE PRINCIPAL (SEM HTML CUSTOMIZADO)
# ============================================================================

def main():
    """Interface principal simplificada"""
    
    # Título principal (sem HTML)
    st.title("💰 Dashboard Financeiro Baker v3.0")
    st.subheader("Sistema de Gestão Financeira Integrada")
    
    # Carregar dados
    with st.spinner("🔄 Carregando dados..."):
        df = carregar_dados()
    
    if df.empty:
        st.error("❌ Nenhum dado encontrado no banco de dados")
        st.info("💡 Verifique a conexão com o PostgreSQL")
        
        # Mostrar status da conexão
        conn = conectar_banco()
        if conn:
            st.success("✅ Conexão com banco OK")
            conn.close()
        else:
            st.error("❌ Não foi possível conectar ao banco")
            
            # Mostrar configuração esperada
            st.subheader("⚙️ Configuração Esperada:")
            st.code("""
PGHOST = "db.lijtncazuwnbydeqtoyz.supabase.co"
PGDATABASE = "postgres"
PGUSER = "postgres"
PGPASSWORD = "SEQAg17334"
PGPORT = "5432"
            """)
        return
    
    # Métricas principais (sem HTML customizado)
    st.header("📊 Métricas Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_ctes = len(df)
        st.metric("Total CTEs", f"{total_ctes:,}")
    
    with col2:
        valor_total = df['valor_total'].sum()
        st.metric("Receita Total", f"R$ {valor_total:,.2f}")
    
    with col3:
        clientes_unicos = df['destinatario_nome'].nunique()
        st.metric("Clientes", clientes_unicos)
    
    with col4:
        faturas_pagas = len(df[df['data_baixa'].notna()])
        st.metric("Faturas Pagas", faturas_pagas)
    
    # Separador
    st.markdown("---")
    
    # Gráficos (sem HTML customizado)
    st.header("📈 Análises")
    
    tab1, tab2, tab3 = st.tabs(["📊 Receita", "👥 Clientes", "📅 Temporal"])
    
    with tab1:
        # Gráfico de status
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Status das Faturas")
            
            status_counts = pd.Series({
                'Pagas': len(df[df['data_baixa'].notna()]),
                'Pendentes': len(df[df['data_baixa'].isna()])
            })
            
            fig_pie = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Distribuição de Status"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.subheader("Valores por Status")
            
            valores_status = pd.Series({
                'Valor Pago': df[df['data_baixa'].notna()]['valor_total'].sum(),
                'Valor Pendente': df[df['data_baixa'].isna()]['valor_total'].sum()
            })
            
            fig_bar = px.bar(
                x=valores_status.index,
                y=valores_status.values,
                title="Valores Financeiros"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab2:
        st.subheader("Top 10 Clientes")
        
        if 'destinatario_nome' in df.columns:
            top_clientes = df.groupby('destinatario_nome')['valor_total'].sum().nlargest(10)
            
            fig_clientes = px.bar(
                x=top_clientes.values,
                y=top_clientes.index,
                orientation='h',
                title="Maiores Clientes por Receita"
            )
            st.plotly_chart(fig_clientes, use_container_width=True)
    
    with tab3:
        st.subheader("Evolução Temporal")
        
        if 'data_emissao' in df.columns:
            df_temp = df[df['data_emissao'].notna()].copy()
            df_temp['mes'] = df_temp['data_emissao'].dt.to_period('M')
            receita_mensal = df_temp.groupby('mes')['valor_total'].sum()
            
            fig_temporal = px.line(
                x=receita_mensal.index.astype(str),
                y=receita_mensal.values,
                title="Receita Mensal"
            )
            st.plotly_chart(fig_temporal, use_container_width=True)
    
    # Tabela de dados
    st.markdown("---")
    st.header("📋 Dados Detalhados")
    
    # Filtros simples
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtro_cliente = st.selectbox(
            "Filtrar por Cliente:",
            ["Todos"] + sorted(df['destinatario_nome'].dropna().unique().tolist())
        )
    
    with col2:
        filtro_status = st.selectbox(
            "Filtrar por Status:",
            ["Todos", "Pagos", "Pendentes"]
        )
    
    with col3:
        num_registros = st.number_input(
            "Número de registros:",
            min_value=10,
            max_value=1000,
            value=100,
            step=10
        )
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if filtro_cliente != "Todos":
        df_filtrado = df_filtrado[df_filtrado['destinatario_nome'] == filtro_cliente]
    
    if filtro_status == "Pagos":
        df_filtrado = df_filtrado[df_filtrado['data_baixa'].notna()]
    elif filtro_status == "Pendentes":
        df_filtrado = df_filtrado[df_filtrado['data_baixa'].isna()]
    
    # Mostrar tabela
    st.dataframe(df_filtrado.head(num_registros), use_container_width=True)
    
    # Download
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"dashboard_baker_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    # Rodapé
    st.markdown("---")
    st.caption("Dashboard Baker v3.0 - Sistema de Gestão Financeira © 2025")

# Sidebar
with st.sidebar:
    st.header("⚙️ Sistema")
    
    if st.button("🔄 Atualizar Dados"):
        st.cache_data.clear()
        st.rerun()
    
    st.header("📊 Status")
    
    # Verificar conexão
    conn = conectar_banco()
    if conn:
        st.success("✅ Banco Conectado")
        conn.close()
    else:
        st.error("❌ Banco Desconectado")
    
    st.caption("Versão 3.0 - Limpa")

if __name__ == "__main__":
    main()
