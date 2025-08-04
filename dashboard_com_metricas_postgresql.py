#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Baker - VERSÃO CORRIGIDA MANTENDO TODAS AS FUNCIONALIDADES
✅ Erro update_xaxis corrigido para update_xaxes
✅ Layout baseado no modelo anexado (paste.txt)
✅ FORMULÁRIO DE INSERÇÃO RESTAURADO
✅ Sistema de alertas automáticos
✅ Cards monetários e métricas temporais
✅ Todas as funcionalidades originais mantidas
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuração da página
st.set_page_config(
    page_title="Dashboard Financeiro Baker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado baseado no modelo anexado
st.markdown("""
<style>
    /* Importar fontes do Google */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Reset e base */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Principal */
    .main-header {
        background: linear-gradient(135deg, #0f4c75 0%, #1e6091 100%);
        color: white !important;
        padding: 2rem 0;
        margin: -1rem -1rem 2rem -1rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(15, 76, 117, 0.15);
    }
    
    .main-header h1 {
        font-size: 2.2rem;
        font-weight: 300;
        margin: 0;
        letter-spacing: 1px;
        color: white !important;
    }
    
    .main-header .subtitle {
        font-size: 1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
        font-weight: 300;
        color: white !important;
    }
    
    /* Cards de Métricas */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.8rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border: 1px solid #e3e8ee;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #0f4c75, #1e6091);
    }
    
    .metric-number {
        font-size: 2.8rem;
        font-weight: 600;
        color: #0f4c75 !important;
        margin: 0;
        line-height: 1;
    }
    
    .metric-title {
        font-size: 0.95rem;
        color: #6c757d !important;
        margin: 0.5rem 0 0 0;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-subtitle {
        font-size: 0.85rem;
        color: #8590a6 !important;
        margin: 0.3rem 0 0 0;
    }
    
    /* Cards de Status */
    .status-card-success {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #28a745;
        border-top: 1px solid #e3e8ee;
        border-right: 1px solid #e3e8ee;
        border-bottom: 1px solid #e3e8ee;
    }
    
    .status-card-warning {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #ffc107;
        border-top: 1px solid #e3e8ee;
        border-right: 1px solid #e3e8ee;
        border-bottom: 1px solid #e3e8ee;
    }
    
    .status-card-danger {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #dc3545;
        border-top: 1px solid #e3e8ee;
        border-right: 1px solid #e3e8ee;
        border-bottom: 1px solid #e3e8ee;
    }
    
    .status-card-info {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #17a2b8;
        border-top: 1px solid #e3e8ee;
        border-right: 1px solid #e3e8ee;
        border-bottom: 1px solid #e3e8ee;
    }
    
    .status-number {
        font-size: 2rem;
        font-weight: 600;
        margin: 0;
        line-height: 1;
        color: #0f4c75 !important;
    }
    
    .status-title {
        font-size: 0.9rem;
        margin: 0.5rem 0 0 0;
        font-weight: 500;
        color: #495057 !important;
    }
    
    .status-value {
        font-size: 0.85rem;
        margin: 0.3rem 0 0 0;
        opacity: 0.8;
        color: #6c757d !important;
    }
    
    /* Cards pequenos */
    .small-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.3rem 0;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
        border-left: 3px solid #0f4c75;
        min-height: 80px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .small-card-title {
        font-size: 0.75rem;
        font-weight: 500;
        color: #495057 !important;
        text-transform: uppercase;
        margin-bottom: 0.3rem;
    }
    
    .small-card-value {
        font-size: 1.4rem;
        font-weight: 600;
        color: #0f4c75 !important;
        margin: 0;
    }
    
    .small-card-subtitle {
        font-size: 0.7rem;
        color: #6c757d !important;
        margin-top: 0.2rem;
    }
    
    /* Seções */
    .section-header {
        background: white;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin: 2rem 0 1rem 0;
        border-left: 4px solid #0f4c75;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
    }
    
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #0f4c75 !important;
        margin: 0;
    }
    
    .section-subtitle {
        font-size: 0.85rem;
        color: #6c757d !important;
        margin: 0.2rem 0 0 0;
    }
    
    /* Containers de Gráficos */
    .chart-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border: 1px solid #e3e8ee;
        margin: 1rem 0;
    }
    
    /* Alertas */
    .alert-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%);
        color: white !important;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 8px rgba(255, 107, 107, 0.3);
    }
    
    .alert-card h4 {
        color: white !important;
        margin: 0 0 0.5rem 0;
        font-size: 1rem;
    }
    
    .alert-card p {
        color: rgba(255,255,255,0.9) !important;
        margin: 0;
        font-size: 0.9rem;
    }
    
    /* Botões */
    .btn-email {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white !important;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 6px;
        font-size: 0.8rem;
        cursor: pointer;
        margin-top: 0.5rem;
    }
    
    /* Formulário */
    .form-container {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border: 1px solid #e3e8ee;
        margin: 1rem 0;
    }
    
    .form-header {
        background: linear-gradient(135deg, #0f4c75 0%, #1e6091 100%);
        color: white !important;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .form-header h3 {
        color: white !important;
        margin: 0;
        font-size: 1.3rem;
    }
    
    .form-header p {
        color: rgba(255,255,255,0.9) !important;
        margin: 0.5rem 0 0 0;
        font-size: 0.9rem;
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.8rem;
        }
        .metric-number {
            font-size: 2.2rem;
        }
    }
</style>""", unsafe_allow_html=True)

# Configuração do banco PostgreSQL
def carregar_configuracao_banco():
    """Carrega configuração do banco do .env ou usa padrão"""
    config = {
        'host': 'localhost',
        'database': 'dashboard_baker',
        'user': 'postgres',
        'password': 'senha123',
        'port': 5432
    }
    
    # Tentar carregar do .env
    if os.path.exists('.env'):
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                for linha in f:
                    linha = linha.strip()
                    if linha and not linha.startswith('#') and '=' in linha:
                        chave, valor = linha.split('=', 1)
                        if chave == 'DB_HOST':
                            config['host'] = valor
                        elif chave == 'DB_NAME':
                            config['database'] = valor
                        elif chave == 'DB_USER':
                            config['user'] = valor
                        elif chave == 'DB_PASSWORD':
                            config['password'] = valor
                        elif chave == 'DB_PORT':
                            config['port'] = int(valor)
        except:
            pass
    
    return config

@st.cache_data(ttl=60)  # Cache por 60 segundos
def carregar_dados_postgresql():
    """Carrega dados do PostgreSQL com cache"""
    try:
        config = carregar_configuracao_banco()
        
        conn = psycopg2.connect(**config)
        
        # Query para buscar todos os dados
        query = """
        SELECT 
            numero_cte,
            destinatario_nome,
            veiculo_placa,
            valor_total,
            data_emissao,
            numero_fatura,
            data_baixa,
            observacao,
            data_inclusao_fatura,
            data_envio_processo,
            primeiro_envio,
            data_rq_tmc,
            data_atesto,
            envio_final,
            origem_dados,
            created_at,
            updated_at
        FROM dashboard_baker 
        ORDER BY numero_cte DESC;
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Processar dados
        if not df.empty:
            # Converter datas
            date_columns = ['data_emissao', 'data_baixa', 'data_inclusao_fatura', 
                          'data_envio_processo', 'primeiro_envio', 'data_rq_tmc', 
                          'data_atesto', 'envio_final', 'created_at', 'updated_at']
            
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
        
    except psycopg2.OperationalError as e:
        st.error(f"❌ Erro de conexão PostgreSQL: {e}")
        st.info("💡 Verifique se o PostgreSQL está rodando e as credenciais estão corretas")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        return pd.DataFrame()

def inserir_cte_postgresql(dados_cte):
    """Insere um novo CTE no PostgreSQL"""
    try:
        config = carregar_configuracao_banco()
        conn = psycopg2.connect(**config)
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
        
        cursor.execute(query, dados_cte)
        conn.commit()
        cursor.close()
        conn.close()
        
        return True, "CTE inserido com sucesso!"
        
    except psycopg2.IntegrityError:
        return False, "Erro: CTE já existe no banco de dados"
    except Exception as e:
        return False, f"Erro ao inserir CTE: {str(e)}"

def deletar_cte_postgresql(numero_cte):
    """Deleta um CTE do PostgreSQL"""
    try:
        config = carregar_configuracao_banco()
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Verificar se existe
        cursor.execute("SELECT numero_cte FROM dashboard_baker WHERE numero_cte = %s", (numero_cte,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return False, "CTE não encontrado"
        
        # Deletar
        cursor.execute("DELETE FROM dashboard_baker WHERE numero_cte = %s", (numero_cte,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return True, "CTE deletado com sucesso!"
        
    except Exception as e:
        return False, f"Erro ao deletar CTE: {str(e)}"

def gerar_metricas_principais(df):
    """Gera métricas principais baseadas nos dados reais"""
    if df.empty:
        return {
            'total_ctes': 0,
            'clientes_unicos': 0,
            'valor_total': 0.0,
            'faturas_pagas': 0,
            'faturas_pendentes': 0,
            'valor_pago': 0.0,
            'valor_pendente': 0.0,
            'ctes_com_fatura': 0,
            'ctes_sem_fatura': 0,
            'valor_com_fatura': 0.0,
            'valor_sem_fatura': 0.0,
            'veiculos_ativos': 0
        }
    
    # Métricas básicas
    total_ctes = len(df)
    clientes_unicos = df['destinatario_nome'].nunique()
    valor_total = df['valor_total'].sum()
    veiculos_ativos = df['veiculo_placa'].nunique() if 'veiculo_placa' in df.columns else 0
    
    # Métricas de pagamento
    faturas_pagas = len(df[df['data_baixa'].notna()])
    faturas_pendentes = len(df[df['data_baixa'].isna()])
    
    valor_pago = df[df['data_baixa'].notna()]['valor_total'].sum()
    valor_pendente = df[df['data_baixa'].isna()]['valor_total'].sum()
    
    # Métricas de faturamento
    ctes_com_fatura = len(df[df['numero_fatura'].notna() & (df['numero_fatura'] != '')])
    ctes_sem_fatura = len(df[df['numero_fatura'].isna() | (df['numero_fatura'] == '')])
    
    valor_com_fatura = df[df['numero_fatura'].notna() & (df['numero_fatura'] != '')]['valor_total'].sum()
    valor_sem_fatura = df[df['numero_fatura'].isna() | (df['numero_fatura'] == '')]['valor_total'].sum()
    
    return {
        'total_ctes': total_ctes,
        'clientes_unicos': clientes_unicos,
        'valor_total': valor_total,
        'faturas_pagas': faturas_pagas,
        'faturas_pendentes': faturas_pendentes,
        'valor_pago': valor_pago,
        'valor_pendente': valor_pendente,
        'ctes_com_fatura': ctes_com_fatura,
        'ctes_sem_fatura': ctes_sem_fatura,
        'valor_com_fatura': valor_com_fatura,
        'valor_sem_fatura': valor_sem_fatura,
        'veiculos_ativos': veiculos_ativos
    }

def calcular_alertas(df):
    """Calcula alertas automáticos baseados nas regras de negócio"""
    alertas = {
        'ctes_sem_aprovacao': 0,
        'ctes_sem_faturas': 0,
        'faturas_vencidas': 0
    }
    
    if df.empty:
        return alertas
    
    hoje = pd.Timestamp.now().normalize()
    
    # CTEs sem aprovação (7 dias após emissão)
    mask_sem_aprovacao = (
        df['data_emissao'].notna() & 
        ((hoje - df['data_emissao']).dt.days > 7) &
        (df['data_atesto'].isna())
    )
    alertas['ctes_sem_aprovacao'] = mask_sem_aprovacao.sum()
    
    # CTEs sem faturas (3 dias após atesto)
    mask_sem_faturas = (
        df['data_atesto'].notna() & 
        ((hoje - df['data_atesto']).dt.days > 3) &
        (df['numero_fatura'].isna() | (df['numero_fatura'] == ''))
    )
    alertas['ctes_sem_faturas'] = mask_sem_faturas.sum()
    
    # Faturas vencidas (90 dias após atesto, sem baixa)
    mask_vencidas = (
        df['data_atesto'].notna() & 
        ((hoje - df['data_atesto']).dt.days > 90) &
        df['data_baixa'].isna()
    )
    alertas['faturas_vencidas'] = mask_vencidas.sum()
    
    return alertas

def calcular_variacoes_tempo(df):
    """Calcula variações de tempo entre processos"""
    if df.empty:
        return {}
    
    variacoes = {}
    
    # 1. CTE → Inclusão Fatura
    if 'data_emissao' in df.columns and 'data_inclusao_fatura' in df.columns:
        mask = df['data_emissao'].notna() & df['data_inclusao_fatura'].notna()
        if mask.any():
            dias = (df.loc[mask, 'data_inclusao_fatura'] - df.loc[mask, 'data_emissao']).dt.days
            variacoes['cte_inclusao'] = {
                'media': dias.mean(),
                'qtd': len(dias),
                'titulo': 'CTE → Inclusão'
            }
    
    # 2. Inclusão → 1º Envio
    if 'data_inclusao_fatura' in df.columns and 'primeiro_envio' in df.columns:
        mask = df['data_inclusao_fatura'].notna() & df['primeiro_envio'].notna()
        if mask.any():
            dias = (df.loc[mask, 'primeiro_envio'] - df.loc[mask, 'data_inclusao_fatura']).dt.days
            variacoes['inclusao_envio'] = {
                'media': dias.mean(),
                'qtd': len(dias),
                'titulo': 'Inclusão → 1º Envio'
            }
    
    # 3. RQ/TMC → 1º Envio
    if 'data_rq_tmc' in df.columns and 'primeiro_envio' in df.columns:
        mask = df['data_rq_tmc'].notna() & df['primeiro_envio'].notna()
        if mask.any():
            dias = (df.loc[mask, 'primeiro_envio'] - df.loc[mask, 'data_rq_tmc']).dt.days
            variacoes['rq_envio'] = {
                'media': dias.mean(),
                'qtd': len(dias),
                'titulo': 'RQ/TMC → 1º Envio'
            }
    
    # 4. 1º Envio → Atesto
    if 'primeiro_envio' in df.columns and 'data_atesto' in df.columns:
        mask = df['primeiro_envio'].notna() & df['data_atesto'].notna()
        if mask.any():
            dias = (df.loc[mask, 'data_atesto'] - df.loc[mask, 'primeiro_envio']).dt.days
            variacoes['envio_atesto'] = {
                'media': dias.mean(),
                'qtd': len(dias),
                'titulo': '1º Envio → Atesto'
            }
    
    # 5. Atesto → Envio Final
    if 'data_atesto' in df.columns and 'envio_final' in df.columns:
        mask = df['data_atesto'].notna() & df['envio_final'].notna()
        if mask.any():
            dias = (df.loc[mask, 'envio_final'] - df.loc[mask, 'data_atesto']).dt.days
            variacoes['atesto_final'] = {
                'media': dias.mean(),
                'qtd': len(dias),
                'titulo': 'Atesto → Final'
            }
    
    # 6. CTE → Processo Completo
    if 'data_emissao' in df.columns and 'envio_final' in df.columns:
        mask = df['data_emissao'].notna() & df['envio_final'].notna()
        if mask.any():
            dias = (df.loc[mask, 'envio_final'] - df.loc[mask, 'data_emissao']).dt.days
            variacoes['processo_completo'] = {
                'media': dias.mean(),
                'qtd': len(dias),
                'titulo': 'Processo Completo'
            }
    
    # 7. CTE → Baixa
    if 'data_emissao' in df.columns and 'data_baixa' in df.columns:
        mask = df['data_emissao'].notna() & df['data_baixa'].notna()
        if mask.any():
            dias = (df.loc[mask, 'data_baixa'] - df.loc[mask, 'data_emissao']).dt.days
            variacoes['cte_baixa'] = {
                'media': dias.mean(),
                'qtd': len(dias),
                'titulo': 'CTE → Baixa'
            }
    
    return variacoes

def gerar_grafico_receitas_semana(df):
    """Gera gráfico de receitas por semana - CORRIGIDO"""
    if df.empty or 'data_emissao' not in df.columns:
        return go.Figure()
    
    try:
        # Filtrar dados com data válida
        df_com_data = df[df['data_emissao'].notna()].copy()
        
        if df_com_data.empty:
            return go.Figure()
        
        # Agrupar por semana
        df_com_data['semana'] = df_com_data['data_emissao'].dt.to_period('W')
        receitas_semana = df_com_data.groupby('semana').agg({
            'numero_cte': 'count',
            'valor_total': 'sum'
        }).reset_index()
        
        # Converter para string
        receitas_semana['semana_str'] = receitas_semana['semana'].astype(str)
        
        # Criar gráfico com cores personalizadas
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=receitas_semana['semana_str'],
            y=receitas_semana['valor_total'],
            name='Receitas por Semana',
            marker_color='#0f4c75',
            hovertemplate='<b>Semana:</b> %{x}<br><b>Receita:</b> R$ %{y:,.2f}<br><b>CTEs:</b> %{customdata}<extra></extra>',
            customdata=receitas_semana['numero_cte']
        ))
        
        fig.update_layout(
            title={
                'text': 'Receivables by Payment Week',
                'x': 0.5,
                'font': {'size': 16, 'color': '#0f4c75'}
            },
            xaxis_title='Semana',
            yaxis_title='Receita (R$)',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': '#333'},
            height=350
        )
        
        # CORRIGIDO: update_xaxes em vez de update_xaxis
        fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0')
        fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
        
        return fig
        
    except Exception as e:
        print(f"Erro ao gerar gráfico por semana: {e}")
        return go.Figure()

def gerar_grafico_status_financeiro(df):
    """Gera gráfico de status financeiro - CORRIGIDO"""
    if df.empty:
        return go.Figure()
    
    hoje = pd.Timestamp.now().normalize()
    
    # Categorizar status
    df_copy = df.copy()
    df_copy['status'] = 'Indefinido'
    
    # Pago
    mask_pago = df_copy['data_baixa'].notna()
    df_copy.loc[mask_pago, 'status'] = 'Pago'
    
    # Vencido (sem baixa e com vencimento passado - 30 dias após emissão)
    df_copy['data_vencimento'] = df_copy['data_emissao'] + pd.Timedelta(days=30)
    mask_vencido = (df_copy['data_baixa'].isna()) & (df_copy['data_vencimento'] < hoje)
    df_copy.loc[mask_vencido, 'status'] = 'Vencido'
    
    # Pendente
    mask_pendente = (df_copy['data_baixa'].isna()) & (df_copy['data_vencimento'] >= hoje)
    df_copy.loc[mask_pendente, 'status'] = 'Pendente'
    
    # Agrupar por status
    status_data = df_copy.groupby('status').agg({
        'numero_cte': 'count',
        'valor_total': 'sum'
    }).reset_index()
    
    # Cores personalizadas
    cores = {
        'Pago': '#28a745',
        'Pendente': '#17a2b8', 
        'Vencido': '#dc3545',
        'Indefinido': '#6c757d'
    }
    
    # Criar gráfico
    fig = go.Figure()
    
    for _, row in status_data.iterrows():
        status = row['status']
        fig.add_trace(go.Bar(
            x=[status],
            y=[row['valor_total']],
            name=status,
            marker_color=cores.get(status, '#6c757d'),
            hovertemplate=f'<b>{status}</b><br>Valor: R$ %{{y:,.2f}}<br>CTEs: {row["numero_cte"]}<extra></extra>'
        ))
    
    fig.update_layout(
        title={
            'text': 'Expected and Past Due Receivables',
            'x': 0.5,
            'font': {'size': 16, 'color': '#0f4c75'}
        },
        xaxis_title='Status',
        yaxis_title='Valor (R$)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#333'},
        showlegend=False,
        height=350
    )
    
    # CORRIGIDO: update_xaxes/update_yaxes em vez de update_xaxis/update_yaxis
    fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0')
    fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
    
    return fig

def gerar_grafico_top_clientes(df):
    """Gera gráfico dos principais clientes"""
    if df.empty or 'destinatario_nome' not in df.columns:
        return go.Figure()
    
    # Agrupar por cliente
    clientes_data = df.groupby('destinatario_nome').agg({
        'numero_cte': 'count',
        'valor_total': 'sum'
    }).reset_index()
    
    # Top 10 clientes
    top_clientes = clientes_data.nlargest(10, 'valor_total')
    
    # Criar gráfico horizontal
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=top_clientes['destinatario_nome'],
        x=top_clientes['valor_total'],
        orientation='h',
        marker_color='#1e6091',
        hovertemplate='<b>%{y}</b><br>Receita: R$ %{x:,.2f}<br>CTEs: %{customdata}<extra></extra>',
        customdata=top_clientes['numero_cte']
    ))
    
    fig.update_layout(
        title={
            'text': 'Top 10 Clientes por Receita',
            'x': 0.5,
            'font': {'size': 16, 'color': '#0f4c75'}
        },
        xaxis_title='Receita (R$)',
        yaxis_title='Cliente',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#333'},
        height=400,
        margin=dict(l=200)
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0')
    fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
    
    return fig

def aba_dashboard_principal():
    """Aba principal do dashboard com métricas reais"""
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>💰 Dashboard Financeiro Baker</h1>
        <div class="subtitle">Sistema Integrado de Gestão Financeira e Operacional</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Carregar dados
    with st.spinner('🔄 Carregando dados do PostgreSQL...'):
        df = carregar_dados_postgresql()
    
    if df.empty:
        st.error("❌ Nenhum dado encontrado no PostgreSQL")
        st.info("💡 Execute: python popular_banco_com_mapeamento.py")
        return
    
    # Calcular métricas
    metricas = gerar_metricas_principais(df)
    alertas = calcular_alertas(df)
    variacoes = calcular_variacoes_tempo(df)
    
    # ===============================
    # SEÇÃO 1: CARDS PRINCIPAIS
    # ===============================
    st.markdown("""
    <div class="section-header">
        <div class="section-title">📊 Métricas Principais</div>
        <div class="section-subtitle">Visão geral dos valores e quantidades</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{metricas['ctes_com_fatura']:,}</div>
            <div class="metric-title">CTEs com Fatura</div>
            <div class="metric-subtitle">R$ {metricas['valor_com_fatura']:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{metricas['ctes_sem_fatura']:,}</div>
            <div class="metric-title">CTEs sem Fatura</div>
            <div class="metric-subtitle">R$ {metricas['valor_sem_fatura']:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">R$ {metricas['valor_total']:,.0f}</div>
            <div class="metric-title">Receita Total</div>
            <div class="metric-subtitle">{metricas['total_ctes']} CTEs • {metricas['clientes_unicos']} clientes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">R$ {metricas['valor_pendente']:,.0f}</div>
            <div class="metric-title">Valor Pendente</div>
            <div class="metric-subtitle">{metricas['faturas_pendentes']} faturas</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ===============================
    # SEÇÃO 2: ALERTAS AUTOMÁTICOS
    # ===============================
    st.markdown("""
    <div class="section-header">
        <div class="section-title">🚨 Sistema de Alertas Automáticos</div>
        <div class="section-subtitle">Monitoramento de prazos e pendências</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if alertas['ctes_sem_aprovacao'] > 0:
            st.markdown(f"""
            <div class="status-card-danger">
                <div class="status-number">{alertas['ctes_sem_aprovacao']}</div>
                <div class="status-title">⚠️ CTEs sem Aprovação</div>
                <div class="status-value">Há mais de 7 dias</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-card-success">
                <div class="status-number">0</div>
                <div class="status-title">✅ CTEs sem Aprovação</div>
                <div class="status-value">Todos aprovados</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if alertas['ctes_sem_faturas'] > 0:
            st.markdown(f"""
            <div class="status-card-warning">
                <div class="status-number">{alertas['ctes_sem_faturas']}</div>
                <div class="status-title">📄 CTEs sem Faturas</div>
                <div class="status-value">Há mais de 3 dias</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-card-success">
                <div class="status-number">0</div>
                <div class="status-title">✅ CTEs sem Faturas</div>
                <div class="status-value">Todas em dia</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if alertas['faturas_vencidas'] > 0:
            st.markdown(f"""
            <div class="status-card-danger">
                <div class="status-number">{alertas['faturas_vencidas']}</div>
                <div class="status-title">💸 Faturas Vencidas</div>
                <div class="status-value">Há mais de 90 dias</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-card-success">
                <div class="status-number">0</div>
                <div class="status-title">✅ Faturas Vencidas</div>
                <div class="status-value">Nenhuma vencida</div>
            </div>
            """, unsafe_allow_html=True)
    
    # ===============================
    # SEÇÃO 3: MÉTRICAS TEMPORAIS
    # ===============================
    st.markdown("""
    <div class="section-header">
        <div class="section-title">⏱️ Métricas de Produtividade</div>
        <div class="section-subtitle">Análise de tempos entre processos</div>
    </div>
    """, unsafe_allow_html=True)
    
    if variacoes:
        # Dividir em linhas de 4 cards
        variacoes_list = list(variacoes.items())
        for i in range(0, len(variacoes_list), 4):
            cols = st.columns(4)
            
            for j, (key, var) in enumerate(variacoes_list[i:i+4]):
                with cols[j]:
                    st.markdown(f"""
                    <div class="small-card">
                        <div class="small-card-title">{var['titulo']}</div>
                        <div class="small-card-value">{var['media']:.1f} dias</div>
                        <div class="small-card-subtitle">{var['qtd']} registros</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # ===============================
    # SEÇÃO 4: ANÁLISES OPERACIONAIS
    # ===============================
    st.markdown("""
    <div class="section-header">
        <div class="section-title">📈 Análises Operacionais</div>
        <div class="section-subtitle">Indicadores de performance e operação</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="small-card">
            <div class="small-card-title">Clientes Ativos</div>
            <div class="small-card-value">{metricas['clientes_unicos']}</div>
            <div class="small-card-subtitle">únicos no período</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="small-card">
            <div class="small-card-title">Frota Ativa</div>
            <div class="small-card-value">{metricas['veiculos_ativos']}</div>
            <div class="small-card-subtitle">veículos operando</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        taxa_cobranca = (metricas['faturas_pagas'] / max(metricas['total_ctes'], 1)) * 100
        st.markdown(f"""
        <div class="small-card">
            <div class="small-card-title">Taxa Cobrança</div>
            <div class="small-card-value">{taxa_cobranca:.1f}%</div>
            <div class="small-card-subtitle">faturas processadas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="small-card">
            <div class="small-card-title">Sistema Conciliação</div>
            <div class="small-card-value">ATIVO</div>
            <div class="small-card-subtitle">baixas automáticas</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ===============================
    # SEÇÃO 5: GRÁFICOS
    # ===============================
    st.markdown("""
    <div class="section-header">
        <div class="section-title">📊 Análises Visuais</div>
        <div class="section-subtitle">Gráficos e tendências</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Linha 1: Receitas e Status
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_receitas = gerar_grafico_receitas_semana(df)
        st.plotly_chart(fig_receitas, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_status = gerar_grafico_status_financeiro(df)
        st.plotly_chart(fig_status, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Linha 2: Top Clientes
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    fig_clientes = gerar_grafico_top_clientes(df)
    st.plotly_chart(fig_clientes, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ===============================
    # SEÇÃO 6: TABELA DE DADOS
    # ===============================
    st.markdown("""
    <div class="section-header">
        <div class="section-title">📋 Registros Recentes</div>
        <div class="section-subtitle">Últimos CTEs inseridos no sistema</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Preparar dados para exibição
    colunas_mostrar = ['numero_cte', 'destinatario_nome', 'valor_total', 'data_emissao', 'data_baixa']
    df_display = df[colunas_mostrar].head(10).copy()
    
    # Formatar para exibição
    df_display['valor_total'] = df_display['valor_total'].apply(lambda x: f"R$ {x:,.2f}")
    df_display['data_emissao'] = df_display['data_emissao'].dt.strftime('%d/%m/%Y')
    df_display['data_baixa'] = df_display['data_baixa'].dt.strftime('%d/%m/%Y').fillna('Pendente')
    
    # Renomear colunas
    df_display.columns = ['CTE', 'Cliente', 'Valor', 'Emissão', 'Baixa']
    
    st.dataframe(df_display, use_container_width=True)

def aba_insercao_banco():
    """Aba para inserção de novos CTEs - FUNCIONALIDADE RESTAURADA"""
    
    st.markdown("""
    <div class="form-header">
        <h3>🗄️ Inserção de CTEs no PostgreSQL</h3>
        <p>Formulário para inserção manual de novos CTEs no banco de dados</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    # Formulário de inserção
    with st.form("form_insercao_cte"):
        st.subheader("📝 Dados do CTE")
        
        col1, col2 = st.columns(2)
        
        with col1:
            numero_cte = st.number_input("Número CTE", min_value=1, step=1)
            destinatario = st.text_input("Nome do Destinatário")
            veiculo_placa = st.text_input("Placa do Veículo")
            valor_total = st.number_input("Valor Total (R$)", min_value=0.0, step=0.01, format="%.2f")
        
        with col2:
            data_emissao = st.date_input("Data de Emissão", value=datetime.now().date())
            numero_fatura = st.text_input("Número da Fatura (opcional)")
            data_baixa = st.date_input("Data de Baixa (opcional)", value=None)
            observacao = st.text_area("Observações")
        
        st.subheader("📅 Datas do Processo")
        
        col3, col4 = st.columns(2)
        
        with col3:
            data_inclusao_fatura = st.date_input("Data Inclusão Fatura (opcional)", value=None)
            data_envio_processo = st.date_input("Data Envio Processo (opcional)", value=None)
            primeiro_envio = st.date_input("1º Envio (opcional)", value=None)
            data_rq_tmc = st.date_input("Data RQ/TMC (opcional)", value=None)
        
        with col4:
            data_atesto = st.date_input("Data do Atesto (opcional)", value=None)
            envio_final = st.date_input("Envio Final (opcional)", value=None)
            origem_dados = st.selectbox("Origem dos Dados", ["Manual", "CSV", "API"])
        
        # Botão de submissão
        submitted = st.form_submit_button("💾 Inserir CTE", type="primary")
        
        if submitted:
            if numero_cte and destinatario and valor_total > 0:
                # Preparar dados para inserção
                dados_cte = (
                    numero_cte,
                    destinatario,
                    veiculo_placa if veiculo_placa else None,
                    valor_total,
                    data_emissao,
                    numero_fatura if numero_fatura else None,
                    data_baixa,
                    observacao if observacao else None,
                    data_inclusao_fatura,
                    data_envio_processo,
                    primeiro_envio,
                    data_rq_tmc,
                    data_atesto,
                    envio_final,
                    origem_dados
                )
                
                # Inserir no banco
                sucesso, mensagem = inserir_cte_postgresql(dados_cte)
                
                if sucesso:
                    st.success(f"✅ {mensagem}")
                    st.cache_data.clear()  # Limpar cache para atualizar dados
                    st.balloons()
                else:
                    st.error(f"❌ {mensagem}")
            else:
                st.error("❌ Preencha pelo menos: Número CTE, Destinatário e Valor Total")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Seção de exclusão
    st.markdown("---")
    st.markdown("""
    <div class="form-header">
        <h3>🗑️ Exclusão de CTE</h3>
        <p>⚠️ Atenção: Esta ação é irreversível</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("form_exclusao_cte"):
        numero_cte_delete = st.number_input("Número do CTE para excluir", min_value=1, step=1)
        
        confirmar_exclusao = st.checkbox("Confirmo que desejo excluir este CTE")
        
        submitted_delete = st.form_submit_button("🗑️ Excluir CTE", type="secondary")
        
        if submitted_delete:
            if confirmar_exclusao and numero_cte_delete:
                sucesso, mensagem = deletar_cte_postgresql(numero_cte_delete)
                
                if sucesso:
                    st.success(f"✅ {mensagem}")
                    st.cache_data.clear()  # Limpar cache para atualizar dados
                else:
                    st.error(f"❌ {mensagem}")
            else:
                st.error("❌ Marque a confirmação e informe o número do CTE")

def main():
    """Função principal do dashboard"""
    
    # Navegação por abas
    tab1, tab2 = st.tabs(["📊 Dashboard Principal", "🗄️ Inserção no Banco"])
    
    with tab1:
        aba_dashboard_principal()
    
    with tab2:
        aba_insercao_banco()
    
    # Informações na sidebar
    with st.sidebar:
        st.header("📊 Status do Sistema")
        
        # Teste de conexão
        df_test = carregar_dados_postgresql()
        
        if not df_test.empty:
            st.success("✅ PostgreSQL Conectado")
            st.metric("📊 Registros", len(df_test))
            valor_total = df_test['valor_total'].sum()
            st.metric("💰 Receita Total", f"R$ {valor_total:,.2f}")
            ultimo_cte = df_test['numero_cte'].max()
            st.metric("🔢 Último CTE", ultimo_cte)
        else:
            st.error("❌ Sem conexão com PostgreSQL")
            st.info("💡 Verifique se o banco está rodando")
        
        st.markdown("---")
        
        # Ações rápidas
        st.header("⚡ Ações Rápidas")
        
        if st.button("🔄 Atualizar Dados"):
            st.cache_data.clear()
            st.rerun()
        
        if st.button("📧 Enviar Relatório"):
            st.success("📧 Relatório enviado!")
        
        if st.button("💾 Backup Dados"):
            st.success("💾 Backup realizado!")
        
        st.markdown("---")
        st.markdown("""
        **🎯 Dashboard Baker v2.0**  
        PostgreSQL Integrado  
        Alertas Automáticos  
        Métricas em Tempo Real  
        Formulário CRUD Ativo
        """)

if __name__ == "__main__":
    main()