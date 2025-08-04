# dashboard_STABLE.py - Versão Estável sem Erros DOM

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import logging
import io
import numpy as np
from typing import Dict, Any, Optional, List, Tuple

# Importações do sistema
from config import config
from data_manager import MultiDataManager
from metrics import (
    FinancialMetrics, calculate_aging_analysis, calculate_monthly_evolution,
    calculate_customer_performance, calculate_tempo_medio_recebimento,
    calculate_total_open_value, format_currency, format_percentage, format_number,
    calculate_valor_sem_faturas  # CORREÇÃO: Importa a função correta do metrics.py
)
from visualization import (
    create_status_distribution_chart, create_monthly_revenue_chart,
    create_aging_analysis_chart, create_top_customers_chart,
    create_payment_forecast_chart, create_filial_comparison_chart,
    create_kpi_card, create_summary_table, create_trend_indicator,
    create_gauge_chart, COLORS
)

# Novos imports para funcionalidades integradas
from auth import check_authentication, login_form, create_user_sidebar, admin_user_management
from vehicle_metrics import VehicleMetrics, create_vehicle_performance_chart, create_vehicle_utilization_chart, create_vehicle_trends_chart
from excel_exporter import ExcelExporter, create_download_link, export_filtered_data

# Configuração da página
st.set_page_config(
    page_title='Transpontual - Dashboard Financeiro',
    page_icon='🚚',
    layout='wide',
    initial_sidebar_state='expanded'
)

# CSS simplificado para evitar conflitos DOM
st.markdown("""
<style>
    .main { 
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
        color: white; 
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1a1f3a 0%, #2d3561 100%);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #4fc3f7;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    .metric-value { 
        font-size: 28px; 
        font-weight: bold; 
        color: #4fc3f7; 
        margin: 10px 0;
    }
    
    .metric-label { 
        font-size: 14px; 
        color: #b0bec5; 
        text-transform: uppercase;
    }
    
    .stats-container {
        background: rgba(26, 31, 58, 0.3);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border: 1px solid rgba(79, 195, 247, 0.2);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1f3a;
        border-radius: 8px;
        color: white;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4fc3f7;
    }
</style>
""", unsafe_allow_html=True)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicialização do session state
if 'dashboard_initialized' not in st.session_state:
    st.session_state.dashboard_initialized = True
    st.session_state.selected_filial = 'consolidated'
    st.session_state.notifications = []
    st.session_state.last_refresh = None

def add_notification(message: str, type: str = "info"):
    """Adiciona notificação ao sistema."""
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []
    
    st.session_state.notifications.append({
        'message': message,
        'type': type,
        'timestamp': datetime.now()
    })
    
    # Manter apenas as 5 mais recentes
    st.session_state.notifications = st.session_state.notifications[-5:]

@st.cache_data(ttl=300, show_spinner=False)
def load_data_cached(filial_key='consolidated'):
    """Carrega dados com cache otimizado por filial."""
    try:
        data_manager = MultiDataManager(config, use_cache=True)
        
        if filial_key == 'consolidated':
            df, warnings = data_manager.load_consolidated_data()
        else:
            df, warnings = data_manager.load_filial_data(filial_key)
        
        if df is not None and not df.empty:
            logger.info(f"✅ {len(df)} registros carregados para {filial_key}")
            return df, warnings
        else:
            return None, warnings
            
    except Exception as e:
        logger.error(f"Erro ao carregar dados: {e}")
        return None, [str(e)]

def calculate_variation(current, previous):
    """Calcula variação percentual."""
    if previous == 0:
        return 0, "neutral"
    
    variation = ((current - previous) / previous) * 100
    delta_type = "positive" if variation >= 0 else "negative"
    return variation, delta_type

def calculate_enhanced_metrics(df):
    """Calcula métricas melhoradas."""
    if df is None or df.empty:
        return {}
    
    hoje = datetime.now()
    mes_atual = hoje.replace(day=1)
    mes_anterior = (mes_atual - timedelta(days=1)).replace(day=1)
    
    # Converte datas
    df['Emissão'] = pd.to_datetime(df['Emissão'], errors='coerce')
    
    # Filtra dados por mês
    df_mes_atual = df[df['Emissão'].dt.to_period('M') == pd.Period(mes_atual, 'M')]
    df_mes_anterior = df[df['Emissão'].dt.to_period('M') == pd.Period(mes_anterior, 'M')]
    
    # Métricas básicas totais
    total_revenue = df['Valor Total do Título'].sum()
    total_invoices = len(df)
    
    # Status
    df_paid = df[df['Status'] == 'Paga'] if 'Status' in df.columns else pd.DataFrame()
    df_open = df[df['Status'] == 'Em Aberto'] if 'Status' in df.columns else pd.DataFrame()
    df_overdue = df[df['Status'] == 'Vencida'] if 'Status' in df.columns else pd.DataFrame()
    
    paid_amount = df_paid['Valor Total do Título'].sum()
    open_amount = df_open['Valor Total do Título'].sum()
    overdue_amount = df_overdue['Valor Total do Título'].sum()
    
    # CORREÇÃO: Usa a função correta do metrics.py
    valores_sem_faturas = calculate_valor_sem_faturas(df)
    
    # Valor total em aberto = valores em aberto + vencidos + sem faturas
    valor_total_aberto = open_amount + overdue_amount + valores_sem_faturas
    
    # Métricas mensais
    receita_mes_atual = df_mes_atual['Valor Total do Título'].sum()
    receita_mes_anterior = df_mes_anterior['Valor Total do Título'].sum()
    
    # Variações
    var_receita, var_receita_type = calculate_variation(receita_mes_atual, receita_mes_anterior)
    
    # Participação do mês
    participacao_mes = (receita_mes_atual / total_revenue * 100) if total_revenue > 0 else 0
    
    # Taxas
    conversion_rate = (paid_amount / total_revenue * 100) if total_revenue > 0 else 0
    default_rate = (overdue_amount / total_revenue * 100) if total_revenue > 0 else 0
    open_rate = (valor_total_aberto / total_revenue * 100) if total_revenue > 0 else 0
    
    return {
        'receita_total': total_revenue,
        'valor_pago': paid_amount,
        'valor_aberto': open_amount,
        'valor_vencido': overdue_amount,
        'valores_sem_faturas': valores_sem_faturas,
        'valor_total_aberto': valor_total_aberto,
        'numero_faturas': total_invoices,
        'ticket_medio': total_revenue / total_invoices if total_invoices > 0 else 0,
        'receita_mes_atual': receita_mes_atual,
        'receita_mes_anterior': receita_mes_anterior,
        'variacao_receita': var_receita,
        'variacao_receita_type': var_receita_type,
        'participacao_mes': participacao_mes,
        'taxa_conversao': conversion_rate,
        'taxa_inadimplencia': default_rate,
        'taxa_aberto': open_rate,
        'faturas_pagas': len(df_paid),
        'faturas_abertas': len(df_open),
        'faturas_vencidas': len(df_overdue)
    }

def create_metric_card_safe(title: str, value: str, help_text: str = "", delta: str = "", delta_color: str = "normal"):
    """Cria card de métrica usando componentes nativos do Streamlit."""
    
    # Usar st.metric nativo ao invés de HTML customizado
    if delta and delta != "":
        if delta_color == "positive":
            delta_value = delta
        elif delta_color == "negative":
            delta_value = f"-{delta}" if not delta.startswith('-') else delta
        else:
            delta_value = delta
    else:
        delta_value = None
    
    st.metric(
        label=title,
        value=value,
        delta=delta_value,
        help=help_text if help_text else None
    )

def create_kpi_summary(metrics: Dict[str, Any]) -> None:
    """Cria resumo KPI usando componentes nativos."""
    
    st.markdown("## 📊 **Visão Geral Executiva**")
    
    # Primeira linha - Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        receita_total = metrics.get('receita_total', 0)
        create_metric_card_safe(
            "💰 RECEITA TOTAL",
            format_currency(receita_total),
            "Soma de todos os valores faturados no período de análise"
        )
    
    with col2:
        receita_mes_atual = metrics.get('receita_mes_atual', 0)
        variacao_receita = metrics.get('variacao_receita', 0)
        variacao_tipo = metrics.get('variacao_receita_type', 'neutral')
        delta_text = f"{variacao_receita:+.1f}%" if variacao_receita != 0 else ""
        
        create_metric_card_safe(
            "📈 RECEITA MÊS ATUAL",
            format_currency(receita_mes_atual),
            "Receita faturada no mês corrente",
            delta_text,
            variacao_tipo
        )
    
    with col3:
        receita_mes_anterior = metrics.get('receita_mes_anterior', 0)
        create_metric_card_safe(
            "📊 RECEITA MÊS ANTERIOR",
            format_currency(receita_mes_anterior),
            "Receita faturada no mês anterior"
        )
    
    with col4:
        participacao_mes = metrics.get('participacao_mes', 0)
        create_metric_card_safe(
            "📋 PARTICIPAÇÃO DO MÊS",
            format_percentage(participacao_mes),
            "Percentual que o mês atual representa do total faturado"
        )
    
    # Segunda linha - Valores em aberto
    st.markdown("### 📊 Composição dos Valores em Aberto")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        valor_aberto = metrics.get('valor_aberto', 0)
        create_metric_card_safe(
            "⏳ VALOR EM ABERTO",
            format_currency(valor_aberto),
            "Faturas aguardando pagamento dentro do prazo"
        )
    
    with col2:
        valor_vencido = metrics.get('valor_vencido', 0)
        create_metric_card_safe(
            "⚠️ VALOR VENCIDO",
            format_currency(valor_vencido),
            "Faturas que passaram do prazo de vencimento"
        )
    
    with col3:
        valores_sem_faturas = metrics.get('valores_sem_faturas', 0)
        create_metric_card_safe(
            "📄 VALORES SEM FATURAS",
            format_currency(valores_sem_faturas),
            "Valores sem documento mas com CTE/OC"
        )
    
    with col4:
        valor_total_aberto = metrics.get('valor_total_aberto', 0)
        receita_total = metrics.get('receita_total', 0)
        taxa_aberto = (valor_total_aberto / receita_total * 100) if receita_total > 0 else 0
        delta_text = f"{taxa_aberto:.1f}% do total"
        
        create_metric_card_safe(
            "💰 VALOR TOTAL EM ABERTO",
            format_currency(valor_total_aberto),
            "Soma: aberto + vencido + sem faturas",
            delta_text
        )
    
    # Terceira linha - Métricas operacionais
    st.markdown("### 🎯 Indicadores de Performance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        taxa_conversao = metrics.get('taxa_conversao', 0)
        delta_type = "positive" if taxa_conversao >= 70 else "negative"
        
        create_metric_card_safe(
            "🎯 TAXA DE CONVERSÃO",
            f"{taxa_conversao:.1f}%",
            "Percentual do faturado que foi efetivamente pago",
            "Meta: 80%",
            delta_type
        )
    
    with col2:
        ticket_medio = metrics.get('ticket_medio', 0)
        create_metric_card_safe(
            "💼 TICKET MÉDIO",
            format_currency(ticket_medio),
            "Valor médio por fatura no período"
        )
    
    with col3:
        faturas_vencidas = metrics.get('faturas_vencidas', 0)
        valor_vencido = metrics.get('valor_vencido', 0)
        
        create_metric_card_safe(
            "⚠️ FATURAS VENCIDAS",
            f"{faturas_vencidas:,}",
            f"Total vencido: {format_currency(valor_vencido)}"
        )
    
    with col4:
        tempo_medio = calculate_tempo_medio_recebimento(st.session_state.get('current_df', pd.DataFrame()))
        delta_type = "positive" if tempo_medio <= 30 else "negative"
        
        create_metric_card_safe(
            "⏱️ TEMPO MÉDIO COBRANÇA",
            f"{tempo_medio:.0f} dias",
            "Tempo médio entre emissão e recebimento",
            "Meta: 30 dias",
            delta_type
        )

def create_advanced_filters():
    """Cria sistema de filtros avançados na sidebar."""
    
    with st.sidebar:
        st.markdown("# 🔧 **Filtros Avançados**")
        
        # Seleção de filial
        filial_options = {
            'consolidated': '🏢 Consolidado',
            'matriz': '🏛️ Matriz Transpontual', 
            'rj': '🌆 Filial RJ'
        }
        
        # Key única para evitar conflitos
        selected_filial = st.selectbox(
            '🏢 Visão',
            options=list(filial_options.keys()),
            format_func=lambda x: filial_options[x],
            index=0,
            key='filial_selectbox'
        )
        
        # Detecta mudança de filial de forma segura
        if 'current_filial' not in st.session_state:
            st.session_state.current_filial = selected_filial
        
        if st.session_state.current_filial != selected_filial:
            st.cache_data.clear()
            st.session_state.current_filial = selected_filial
            add_notification(f"Filial alterada para: {filial_options[selected_filial]}", "success")
            st.rerun()
        
        st.markdown("---")
        
        # Filtros de período
        st.markdown("### 📅 **Período**")
        
        periodo_options = {
            'all': 'Todos os dados',
            'ytd': 'Acumulado no ano',
            'last_12m': 'Últimos 12 meses',
            'last_6m': 'Últimos 6 meses',
            'last_3m': 'Últimos 3 meses',
            'current_month': 'Mês atual'
        }
        
        periodo = st.selectbox(
            'Período', 
            list(periodo_options.keys()), 
            format_func=lambda x: periodo_options[x],
            key='periodo_selectbox'
        )
        
        # Filtros de status
        st.markdown("### 📊 **Status**")
        status_options = ['Paga', 'Em Aberto', 'Vencida', 'Valores sem Faturas']
        selected_status = st.multiselect(
            'Status das faturas',
            status_options,
            default=['Paga', 'Em Aberto', 'Vencida'],
            key='status_multiselect'
        )
        
        # Filtros de valor
        st.markdown("### 💰 **Valores**")
        valor_min = st.number_input(
            "Valor mínimo (R$)", 
            min_value=0.0, 
            value=0.0, 
            step=100.0,
            key='valor_min_input'
        )
        valor_max = st.number_input(
            "Valor máximo (R$)", 
            min_value=0.0, 
            value=0.0, 
            step=1000.0,
            key='valor_max_input'
        )
        
        # Filtros de veículos (NOVO)
        st.markdown("### 🚛 **Veículos**")
        
        # Carrega dados para popular filtros de veículos
        if 'current_df' in st.session_state and st.session_state.current_df is not None:
            current_df = st.session_state.current_df
            if 'Veículo - Placa' in current_df.columns:
                unique_vehicles = sorted(current_df['Veículo - Placa'].dropna().unique())
                if len(unique_vehicles) > 0:
                    selected_vehicles = st.multiselect(
                        'Veículos específicos',
                        unique_vehicles,
                        key='vehicles_multiselect',
                        help="Deixe vazio para incluir todos os veículos"
                    )
                else:
                    selected_vehicles = []
            else:
                selected_vehicles = []
        else:
            selected_vehicles = []
        
        # Filtros de clientes (NOVO)
        st.markdown("### 👥 **Clientes**")
        
        if 'current_df' in st.session_state and st.session_state.current_df is not None:
            current_df = st.session_state.current_df
            if 'Cliente - Nome' in current_df.columns:
                unique_clients = sorted(current_df['Cliente - Nome'].dropna().unique())
                if len(unique_clients) > 0:
                    # Dropdown para filtro rápido de top clientes
                    client_filter_type = st.selectbox(
                        'Filtro de clientes',
                        ['Todos', 'Top 10', 'Top 20', 'Personalizado'],
                        key='client_filter_type'
                    )
                    
                    if client_filter_type == 'Personalizado':
                        selected_clients = st.multiselect(
                            'Clientes específicos',
                            unique_clients,
                            key='clients_multiselect'
                        )
                    else:
                        selected_clients = []
                else:
                    client_filter_type = 'Todos'
                    selected_clients = []
            else:
                client_filter_type = 'Todos'
                selected_clients = []
        else:
            client_filter_type = 'Todos'
            selected_clients = []
        
        # Botões de ação
        st.markdown("---")
        st.markdown("### ⚡ **Ações**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Atualizar", use_container_width=True, key='btn_atualizar'):
                st.cache_data.clear()
                add_notification("Dados atualizados", "success")
                st.rerun()
        
        with col2:
            if st.button("🗑️ Limpar", use_container_width=True, key='btn_limpar'):
                st.rerun()
        
        # Retorna filtros e filial selecionada
        filters = {
            'periodo': periodo,
            'status': selected_status,
            'valor_min': valor_min,
            'valor_max': valor_max,
            'vehicles': selected_vehicles,
            'client_filter_type': client_filter_type,
            'clients': selected_clients
        }
        
        return filters, selected_filial

def apply_filters(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """Aplica filtros ao DataFrame."""
    if df is None or df.empty:
        return df
    
    filtered_df = df.copy()
    
    # Filtro de período
    if filters.get('periodo') != 'all' and 'Emissão' in filtered_df.columns:
        hoje = datetime.now()
        
        if filters['periodo'] == 'ytd':
            start_date = datetime(hoje.year, 1, 1)
            filtered_df = filtered_df[filtered_df['Emissão'] >= start_date]
        elif filters['periodo'] == 'last_12m':
            start_date = hoje - timedelta(days=365)
            filtered_df = filtered_df[filtered_df['Emissão'] >= start_date]
        elif filters['periodo'] == 'last_6m':
            start_date = hoje - timedelta(days=180)
            filtered_df = filtered_df[filtered_df['Emissão'] >= start_date]
        elif filters['periodo'] == 'last_3m':
            start_date = hoje - timedelta(days=90)
            filtered_df = filtered_df[filtered_df['Emissão'] >= start_date]
        elif filters['periodo'] == 'current_month':
            start_date = hoje.replace(day=1)
            filtered_df = filtered_df[filtered_df['Emissão'] >= start_date]
    
    # CORREÇÃO: Filtro de status usando a lógica correta do metrics.py
    if filters.get('status') and 'Status' in filtered_df.columns:
        selected_status = filters['status']
        
        if 'Valores sem Faturas' in selected_status:
            normal_status = [s for s in selected_status if s != 'Valores sem Faturas']
            
            # Filtra registros com status normal
            if normal_status:
                df_status_normal = filtered_df[filtered_df['Status'].isin(normal_status)]
            else:
                df_status_normal = pd.DataFrame()
            
            # CORREÇÃO: Usa a mesma lógica do metrics.py para identificar valores sem faturas
            if 'Documento' in filtered_df.columns:
                mask_sem_documento = (
                    filtered_df['Documento'].isna() | 
                    (filtered_df['Documento'].astype(str).str.strip() == '') |
                    (filtered_df['Documento'].astype(str).str.upper().isin(['NAN', 'NULL', '', 'NONE']))
                )
                
                # CORREÇÃO: Verifica se tem CTE/OC (lógica do metrics.py)
                if 'cte_oc_numero' in filtered_df.columns:
                    mask_com_cte = filtered_df['cte_oc_numero'].notna() & (filtered_df['cte_oc_numero'].astype(str).str.strip() != '')
                    df_sem_faturas = filtered_df[mask_sem_documento & mask_com_cte]
                else:
                    df_sem_faturas = filtered_df[mask_sem_documento]
            else:
                df_sem_faturas = pd.DataFrame()
            
            # Combina os DataFrames
            if not df_status_normal.empty and not df_sem_faturas.empty:
                filtered_df = pd.concat([df_status_normal, df_sem_faturas], ignore_index=True).drop_duplicates()
            elif not df_status_normal.empty:
                filtered_df = df_status_normal
            elif not df_sem_faturas.empty:
                filtered_df = df_sem_faturas
            else:
                filtered_df = pd.DataFrame()
        else:
            # Filtro normal por status
            filtered_df = filtered_df[filtered_df['Status'].isin(selected_status)]
    
    # Filtro de valores
    if 'Valor Total do Título' in filtered_df.columns:
        if filters.get('valor_min', 0) > 0:
            filtered_df = filtered_df[filtered_df['Valor Total do Título'] >= filters['valor_min']]
        if filters.get('valor_max', 0) > 0:
            filtered_df = filtered_df[filtered_df['Valor Total do Título'] <= filters['valor_max']]
    
    # Filtro de veículos (NOVO)
    if filters.get('vehicles') and 'Veículo - Placa' in filtered_df.columns:
        selected_vehicles = filters['vehicles']
        if selected_vehicles:  # Se tem veículos selecionados
            filtered_df = filtered_df[filtered_df['Veículo - Placa'].isin(selected_vehicles)]
    
    # Filtro de clientes (NOVO)
    if 'Cliente - Nome' in filtered_df.columns:
        client_filter_type = filters.get('client_filter_type', 'Todos')
        
        if client_filter_type == 'Top 10':
            # Pega os top 10 clientes por receita
            top_clients = filtered_df.groupby('Cliente - Nome')['Valor Total do Título'].sum().nlargest(10).index
            filtered_df = filtered_df[filtered_df['Cliente - Nome'].isin(top_clients)]
        
        elif client_filter_type == 'Top 20':
            # Pega os top 20 clientes por receita
            top_clients = filtered_df.groupby('Cliente - Nome')['Valor Total do Título'].sum().nlargest(20).index
            filtered_df = filtered_df[filtered_df['Cliente - Nome'].isin(top_clients)]
        
        elif client_filter_type == 'Personalizado' and filters.get('clients'):
            # Filtra clientes específicos selecionados
            selected_clients = filters['clients']
            if selected_clients:
                filtered_df = filtered_df[filtered_df['Cliente - Nome'].isin(selected_clients)]
    
    return filtered_df

def render_notifications():
    """Renderiza notificações do sistema de forma segura."""
    if 'notifications' in st.session_state and st.session_state.notifications:
        notifications = st.session_state.notifications[-2:]  # Apenas 2 mais recentes
        
        for i, notif in enumerate(notifications):
            timestamp = notif['timestamp'].strftime("%H:%M:%S")
            
            if notif['type'] == 'success':
                st.success(f"✅ {timestamp} - {notif['message']}")
            elif notif['type'] == 'warning':
                st.warning(f"⚠️ {timestamp} - {notif['message']}")
            elif notif['type'] == 'error':
                st.error(f"❌ {timestamp} - {notif['message']}")

def create_aging_analysis_chart_safe(aging_data) -> go.Figure:
    """Cria gráfico de análise de aging de forma segura."""
    
    try:
        if aging_data is None:
            fig = go.Figure()
            fig.add_annotation(
                text="Sem faturas vencidas",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font=dict(size=16, color='white')
            )
            return fig
        
        if isinstance(aging_data, pd.DataFrame):
            if aging_data.empty:
                fig = go.Figure()
                fig.add_annotation(
                    text="Sem dados de aging disponíveis",
                    xref="paper", yref="paper", x=0.5, y=0.5,
                    showarrow=False, font=dict(size=16, color='white')
                )
                return fig
            
            x_data = aging_data.get('Faixa_Atraso', aging_data.iloc[:, 0])
            y_data = aging_data.get('Valor_Total', aging_data.iloc[:, 1])
        else:
            if not aging_data:
                fig = go.Figure()
                fig.add_annotation(
                    text="Sem faturas vencidas",
                    xref="paper", yref="paper", x=0.5, y=0.5,
                    showarrow=False, font=dict(size=16, color='white')
                )
                return fig
            
            x_data = list(aging_data.keys())
            y_data = list(aging_data.values())
        
        # Cores para diferentes faixas de aging
        colors = ['#4caf50', '#2196f3', '#ff9800', '#ff7043', '#f44336']
        colors = colors[:len(x_data)]
        
        fig = go.Figure(data=[
            go.Bar(
                x=x_data,
                y=y_data,
                marker=dict(color=colors),
                text=[f'R$ {val:,.0f}' for val in y_data],
                textposition='auto',
                textfont=dict(color='white', size=12),
                hovertemplate='<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title='Análise de Aging - Faturas Vencidas',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(
                showgrid=True,
                gridwidth=0.5,
                gridcolor='#2d3561',
                color='#b0bec5',
                title='Faixa de Atraso'
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=0.5,
                gridcolor='#2d3561',
                color='#b0bec5',
                title='Valor (R$)'
            ),
            xaxis_tickangle=-45
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Erro ao criar gráfico de aging: {e}")
        fig = go.Figure()
        fig.add_annotation(
            text="Erro ao carregar dados de aging",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=16, color='white')
        )
        return fig

def render_financial_overview_tab(df: pd.DataFrame, metrics: Dict[str, Any]):
    """Renderiza aba de visão geral financeira de forma segura."""
    
    st.markdown("## 💰 **Análise Financeira Detalhada**")
    
    # Gráficos principais
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        try:
            fig_status = create_status_distribution_chart(df)
            st.plotly_chart(fig_status, use_container_width=True, key='chart_status')
        except Exception as e:
            st.error(f"Erro ao carregar gráfico de status: {e}")
    
    with chart_col2:
        try:
            fig_monthly = create_monthly_revenue_chart(df)
            st.plotly_chart(fig_monthly, use_container_width=True, key='chart_monthly')
        except Exception as e:
            st.error(f"Erro ao carregar gráfico mensal: {e}")
    
    # Análise de aging
    st.markdown("### 📊 **Análise de Aging**")
    
    try:
        aging_data = calculate_aging_analysis(df)
        
        has_aging_data = False
        if aging_data is not None:
            if isinstance(aging_data, pd.DataFrame):
                has_aging_data = not aging_data.empty
            elif isinstance(aging_data, dict):
                has_aging_data = bool(aging_data)
            else:
                has_aging_data = bool(aging_data)
        
        if has_aging_data:
            chart_col1, chart_col2 = st.columns([2, 1])
            
            with chart_col1:
                fig_aging = create_aging_analysis_chart_safe(aging_data)
                st.plotly_chart(fig_aging, use_container_width=True, key='chart_aging')
            
            with chart_col2:
                st.markdown("**📈 Estatísticas de Aging**")
                
                if isinstance(aging_data, pd.DataFrame) and not aging_data.empty:
                    total_vencido = aging_data['Valor_Total'].sum() if 'Valor_Total' in aging_data.columns else 0
                    st.metric("Total Vencido", format_currency(total_vencido))
                    
                    if total_vencido > 0:
                        max_idx = aging_data['Valor_Total'].idxmax() if 'Valor_Total' in aging_data.columns else 0
                        max_faixa = aging_data.loc[max_idx]
                        st.metric("Maior Concentração", str(max_faixa.get('Faixa_Atraso', 'N/A')))
                        st.metric("Valor", format_currency(max_faixa.get('Valor_Total', 0)))
                
                elif isinstance(aging_data, dict):
                    total_vencido = sum(aging_data.values())
                    st.metric("Total Vencido", format_currency(total_vencido))
                    
                    if total_vencido > 0:
                        max_faixa = max(aging_data, key=aging_data.get)
                        st.metric("Maior Concentração", max_faixa)
                        st.metric("Valor", format_currency(aging_data[max_faixa]))
        else:
            st.info("📊 Nenhuma fatura vencida para análise de aging")
            
    except Exception as e:
        st.error(f"❌ Erro ao calcular aging: {str(e)}")
        logger.error(f"Erro na análise de aging: {e}")

def render_customer_analysis_tab(df: pd.DataFrame):
    """Renderiza aba de análise de clientes de forma segura."""
    
    st.markdown("## 👥 **Análise de Clientes**")
    
    try:
        if 'Cliente - Nome' not in df.columns or df.empty:
            st.warning("Dados de clientes não disponíveis")
            return
        
        customer_data = calculate_customer_performance(df)
        
        if customer_data.empty:
            st.warning("Nenhum dado de cliente encontrado")
            return
        
        # Métricas de clientes usando componentes nativos
        col1, col2, col3, col4 = st.columns(4)
        
        total_clientes = len(customer_data)
        receita_media_cliente = customer_data['faturamento'].mean()
        top_cliente_receita = customer_data.iloc[0]['faturamento'] if not customer_data.empty else 0
        concentracao_top10 = customer_data.head(10)['faturamento'].sum() / customer_data['faturamento'].sum() * 100
        
        with col1:
            st.metric("👥 Total Clientes", f"{total_clientes:,}", 
                     help="Número total de clientes ativos")
        
        with col2:
            st.metric("💼 Receita Média/Cliente", format_currency(receita_media_cliente),
                     help="Receita média por cliente no período")
        
        with col3:
            st.metric("🏆 Top Cliente", format_currency(top_cliente_receita),
                     help="Receita do maior cliente")
        
        with col4:
            delta_type = "normal" if concentracao_top10 <= 50 else "inverse"
            st.metric("⚖️ Concentração Top 10", f"{concentracao_top10:.1f}%",
                     help="Concentração de receita nos 10 maiores clientes")
        
        # Gráfico de top clientes
        try:
            fig_top_customers = create_top_customers_chart(customer_data, 15)
            st.plotly_chart(fig_top_customers, use_container_width=True, key='chart_customers')
        except Exception as e:
            st.error(f"Erro ao carregar gráfico de clientes: {e}")
    
    except Exception as e:
        st.error(f"Erro na análise de clientes: {e}")
        logger.error(f"Erro na análise de clientes: {e}")

def render_vehicle_analysis_tab(df: pd.DataFrame):
    """Renderiza aba de análise de veículos de forma segura."""
    
    st.markdown("## 🚛 **Análise de Veículos**")
    
    try:
        if 'Veículo - Placa' not in df.columns or df.empty:
            st.warning("Dados de veículos não disponíveis")
            return
        
        vm = VehicleMetrics(df)
        vehicle_data = vm.calculate_vehicle_performance()
        utilization_data = vm.calculate_vehicle_utilization()
        
        if vehicle_data.empty:
            st.warning("Nenhum dado de veículo encontrado")
            return
        
        # Métricas de frota usando componentes nativos
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🚛 Total Veículos", utilization_data.get('total_vehicles', 0),
                     help="Número total de veículos na frota")
        
        with col2:
            active_vehicles = utilization_data.get('active_vehicles', 0)
            utilization_rate = utilization_data.get('utilization_rate', 0)
            st.metric("✅ Veículos Ativos", f"{active_vehicles}",
                     delta=f"{utilization_rate:.1f}% utilização",
                     help="Veículos com receita no período")
        
        with col3:
            high_perf = utilization_data.get('high_performance_vehicles', 0)
            st.metric("🏆 Alta Performance", f"{high_perf}",
                     help="Veículos no top 20% de performance")
        
        with col4:
            avg_revenue = utilization_data.get('avg_revenue_per_vehicle', 0)
            st.metric("💰 Receita Média/Veículo", format_currency(avg_revenue),
                     help="Receita média por veículo")
        
        # Gráficos de veículos
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            try:
                fig_vehicles = create_vehicle_performance_chart(vehicle_data, 15)
                st.plotly_chart(fig_vehicles, use_container_width=True, key='chart_vehicles')
            except Exception as e:
                st.error(f"Erro ao carregar gráfico de performance: {e}")
        
        with chart_col2:
            try:
                fig_utilization = create_vehicle_utilization_chart(utilization_data)
                st.plotly_chart(fig_utilization, use_container_width=True, key='chart_utilization')
            except Exception as e:
                st.error(f"Erro ao carregar gráfico de utilização: {e}")
        
        # Tendências mensais (se disponível)
        st.markdown("### 📈 **Tendências Mensais dos Top Veículos**")
        try:
            trends_data = vm.calculate_monthly_vehicle_trends()
            if not trends_data.empty:
                top_vehicles = vehicle_data.head(5)['Veículo - Placa'].tolist()
                fig_trends = create_vehicle_trends_chart(trends_data, top_vehicles)
                st.plotly_chart(fig_trends, use_container_width=True, key='chart_vehicle_trends')
            else:
                st.info("Dados de tendências não disponíveis")
        except Exception as e:
            st.error(f"Erro ao carregar tendências: {e}")
    
    except Exception as e:
        st.error(f"Erro na análise de veículos: {e}")
        logger.error(f"Erro na análise de veículos: {e}")

def render_export_tab(df: pd.DataFrame, metrics: Dict[str, Any]):
    """Renderiza aba de exportação melhorada."""
    
    st.markdown("## 📥 **Exportação Avançada**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 **Relatório Completo**")
        st.markdown("Gera relatório Excel com múltiplas abas e formatação profissional")
        
        if st.button("📄 Gerar Relatório Excel", use_container_width=True, key='btn_relatorio_completo'):
            try:
                with st.spinner('🔄 Gerando relatório...'):
                    exporter = ExcelExporter()
                    excel_data = exporter.create_financial_report(df, metrics)
                    
                    filename = f"relatorio_transpontual_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    download_link = create_download_link(excel_data, filename, "📥 Download Relatório Excel")
                    st.markdown(download_link, unsafe_allow_html=True)
                    st.success("✅ Relatório gerado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao gerar relatório: {e}")
    
    with col2:
        st.markdown("### 📋 **Dados Filtrados**")
        st.markdown("Exporta apenas os dados atualmente visíveis com filtros aplicados")
        
        export_format = st.selectbox("Formato de Exportação", ["Excel", "CSV"], key='export_format_select')
        
        if st.button("📤 Exportar Dados Filtrados", use_container_width=True, key='btn_dados_filtrados'):
            try:
                with st.spinner(f'🔄 Gerando {export_format}...'):
                    if export_format == "Excel":
                        data = export_filtered_data(df, "excel")
                        filename = f"dados_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    else:
                        data = export_filtered_data(df, "csv")
                        filename = f"dados_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                        mime_type = "text/csv"
                    
                    download_link = create_download_link(data, filename, f"📥 Download {export_format}")
                    st.markdown(download_link, unsafe_allow_html=True)
                    st.success(f"✅ {export_format} gerado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao exportar: {e}")
    
    # Estatísticas do dataset atual
    st.markdown("---")
    st.markdown("### 📊 **Informações do Dataset Atual**")
    
    info_col1, info_col2, info_col3, info_col4 = st.columns(4)
    
    with info_col1:
        st.metric("📋 Total Registros", f"{len(df):,}")
    
    with info_col2:
        if 'Cliente - Nome' in df.columns:
            unique_clients = df['Cliente - Nome'].nunique()
            st.metric("👥 Clientes Únicos", f"{unique_clients:,}")
    
    with info_col3:
        if 'Veículo - Placa' in df.columns:
            unique_vehicles = df['Veículo - Placa'].nunique()
            st.metric("🚛 Veículos Únicos", f"{unique_vehicles:,}")
    
    with info_col4:
        period_info = "N/A"
        if 'Emissão' in df.columns and not df.empty:
            min_date = df['Emissão'].min()
            max_date = df['Emissão'].max()
            if pd.notna(min_date) and pd.notna(max_date):
                period_days = (max_date - min_date).days
                period_info = f"{period_days} dias"
        st.metric("📅 Período", period_info)

def main():
    """Função principal do dashboard."""
    
    # Verificação de autenticação
    if not check_authentication():
        login_form()
        return
    
    # Header principal
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #4fc3f7; font-size: 3rem; margin: 0;">
            🚚 Transpontual Dashboard
        </h1>
        <p style="color: #b0bec5; font-size: 1.2rem; margin: 0.5rem 0 0 0;">
            Sistema Integrado de Análise Financeira
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar com filtros e informações do usuário
    try:
        create_user_sidebar()
        filters, selected_filial = create_advanced_filters()
    except Exception as e:
        st.error(f"Erro ao criar filtros: {e}")
        st.stop()
    
    # Carregamento de dados por filial
    try:
        with st.spinner('🔄 Carregando dados...'):
            df, warnings = load_data_cached(selected_filial)
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        st.stop()
    
    # Renderiza notificações
    render_notifications()
    
    if df is None or df.empty:
        st.error("❌ Nenhum dado disponível para análise")
        st.stop()
    
    # Aplica filtros
    try:
        filtered_df = apply_filters(df, filters)
        st.session_state.current_df = filtered_df
    except Exception as e:
        st.error(f"Erro ao aplicar filtros: {e}")
        filtered_df = df
        st.session_state.current_df = df
    
    if filtered_df.empty:
        st.warning("⚠️ Nenhum dado encontrado com os filtros aplicados")
        st.stop()
    
    # Calcula métricas
    try:
        metrics = calculate_enhanced_metrics(filtered_df)
    except Exception as e:
        st.error(f"Erro ao calcular métricas: {e}")
        metrics = {}
    
    # Informações do dataset
    dataset_info_col1, dataset_info_col2, dataset_info_col3 = st.columns(3)
    
    with dataset_info_col1:
        st.info(f"📊 **{len(filtered_df):,}** registros carregados")
    
    with dataset_info_col2:
        filial_names = {
            'consolidated': 'Consolidado',
            'matriz': 'Matriz',
            'rj': 'Filial RJ'
        }
        st.info(f"🏢 **{filial_names.get(selected_filial, selected_filial)}**")
    
    with dataset_info_col3:
        st.info(f"🔄 **{datetime.now().strftime('%H:%M:%S')}**")
    
    # KPI Summary no topo
    try:
        create_kpi_summary(metrics)
    except Exception as e:
        st.error(f"Erro ao criar KPIs: {e}")
    
    # Separador visual
    st.markdown("---")
    
    # Sistema de abas principal - ATUALIZADO
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "💰 **Visão Financeira**",
        "👥 **Análise de Clientes**", 
        "🚛 **Análise de Veículos**",
        "🔬 **Analytics Avançados**",
        "📥 **Exportação**",
        "👤 **Usuários**"
    ])
    
    with tab1:
        try:
            render_financial_overview_tab(filtered_df, metrics)
        except Exception as e:
            st.error(f"Erro na aba financeira: {e}")
    
    with tab2:
        try:
            render_customer_analysis_tab(filtered_df)
        except Exception as e:
            st.error(f"Erro na aba de clientes: {e}")
    
    with tab3:
        try:
            render_vehicle_analysis_tab(filtered_df)
        except Exception as e:
            st.error(f"Erro na aba de veículos: {e}")
    
    with tab4:
        st.markdown("## 🔬 **Analytics Avançados**")
        st.info("Análise de tendências e sazonalidade - Em implementação")
    
    with tab5:
        try:
            render_export_tab(filtered_df, metrics)
        except Exception as e:
            st.error(f"Erro na aba de exportação: {e}")
    
    with tab6:
        try:
            admin_user_management()
        except Exception as e:
            st.error(f"Erro no gerenciamento de usuários: {e}")
    
    # Footer
    st.markdown("---")
    footer_col1, footer_col2, footer_col3 = st.columns(3)
    
    with footer_col1:
        st.markdown("**🚚 Transpontual Dashboard v2.0**")
    
    with footer_col2:
        st.markdown(f"**📊 {len(filtered_df):,} registros**")
    
    with footer_col3:
        st.markdown(f"**⏰ {datetime.now().strftime('%H:%M:%S')}**")

if __name__ == "__main__":
    main()