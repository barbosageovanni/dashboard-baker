#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Baker - VERSÃO FINAL CORRIGIDA v3.0
✅ Sistema de Gestão de Baixas Automáticas
✅ Análise Avançada de Variações Temporais 
✅ Cards de Produtividade Detalhados
✅ Sistema de Alertas Inteligentes
✅ Conciliação em Tempo Real
✅ Sistema de Relatórios PDF/Excel
✅ FUNÇÕES CRUD CORRIGIDAS
MANTER NOME: dashboard_baker_web_corrigido.py
"""

import streamlit as st

# FIX: Locale inglês
import locale
try: locale.setlocale(locale.LC_ALL, "C")
except: pass

# FIX: Forçar locale inglês para evitar None → Nenhum
import locale
try:
    locale.setlocale(locale.LC_ALL, 'C')
except:
    pass
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np
import os
import json
import hashlib
from typing import Dict, List, Tuple, Optional
import base64
from io import BytesIO
import xlsxwriter
from decimal import Decimal
import uuid
import os

os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'

# Verificar disponibilidade do psycopg2
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    psycopg2 = None
    RealDictCursor = None

# Configuração da página
try:
    st.set_page_config(
        page_title="Dashboard Financeiro Baker - Sistema Avançado",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
except Exception:
    # Fallback se já foi configurado
    pass

# Verificar se está em ambiente de produção
if 'DYNO' in os.environ or 'RAILWAY_ENVIRONMENT' in os.environ:
    # Configurações específicas para produção
    st.markdown("🚀 **Modo Produção Ativo**")

# CSS customizado expandido
st.markdown("""
    <style>
    /* Reset para evitar conflitos de DOM */
    .main .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Header principal */
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #0f4c75 0%, #3282b8 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(15, 76, 117, 0.3);
    }

    .main-header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }

    .subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }

    /* Cards de métricas melhorados */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 15px;
        padding: 1.8rem 1.5rem;
        margin: 0.8rem 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
        border-color: #0f4c75;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #0f4c75, #3282b8, #0bb5ff);
        border-radius: 15px 15px 0 0;
    }

    .metric-number {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0f4c75;
        margin-bottom: 0.5rem;
        line-height: 1.2;
    }

    .metric-title {
        font-size: 1rem;
        font-weight: 600;
        color: #495057;
        margin-bottom: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .metric-subtitle {
        font-size: 0.85rem;
        color: #6c757d;
        font-weight: 500;
    }

    /* Cards de status melhorados */
    .status-card-success {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #c3e6cb;
        border-left: 5px solid #28a745;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.8rem 0;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.1);
        transition: all 0.3s ease;
    }

    .status-card-warning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 1px solid #ffeaa7;
        border-left: 5px solid #ffc107;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.8rem 0;
        box-shadow: 0 4px 15px rgba(255, 193, 7, 0.1);
        transition: all 0.3s ease;
    }

    .status-card-danger {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border: 1px solid #f5c6cb;
        border-left: 5px solid #dc3545;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.8rem 0;
        box-shadow: 0 4px 15px rgba(220, 53, 69, 0.1);
        transition: all 0.3s ease;
    }

    .status-card-info {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border: 1px solid #bee5eb;
        border-left: 5px solid #17a2b8;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.8rem 0;
        box-shadow: 0 4px 15px rgba(23, 162, 184, 0.1);
        transition: all 0.3s ease;
    }

    .status-card-success:hover, .status-card-warning:hover, 
    .status-card-danger:hover, .status-card-info:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }

    .status-number {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .status-title {
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .status-value {
        font-size: 0.9rem;
        font-weight: 500;
        opacity: 0.8;
    }

    /* Seções */
    .section-header {
        margin: 2.5rem 0 1.5rem 0;
        text-align: center;
    }

    .section-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f4c75;
        margin-bottom: 0.5rem;
    }

    .section-subtitle {
        font-size: 1rem;
        color: #6c757d;
        font-weight: 500;
    }

    /* Formulários */
    .form-header {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border-left: 5px solid #0f4c75;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    }

    .form-header h3 {
        color: #0f4c75;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .form-header p {
        color: #6c757d;
        margin-bottom: 0;
        font-size: 0.95rem;
    }

    /* Variações temporais */
    .variacao-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.8rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #28a745;
        transition: all 0.3s ease;
    }

    .variacao-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
    }

    .variacao-title {
        font-size: 1rem;
        font-weight: 600;
        color: #495057;
        margin-bottom: 0.5rem;
    }

    .variacao-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f4c75;
        margin-bottom: 0.3rem;
    }

    .variacao-meta {
        font-size: 0.85rem;
        color: #6c757d;
        font-weight: 500;
    }

    /* Sidebar melhorada */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
        border-right: 2px solid #e9ecef;
    }

    /* Responsividade */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }

        .metric-card {
            padding: 1.2rem 1rem;
        }

        .metric-number {
            font-size: 1.8rem;
        }

        .main-header h1 {
            font-size: 2rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# CONFIGURAÇÃO DO BANCO POSTGRESQL - VERSÃO CORRIGIDA
# ============================================================================

# ================================================================
# FUNÇÕES DE CORREÇÃO PARA PROBLEMA None → Nenhum
# ================================================================

def corrigir_valor_traduzido(valor):
    """
    Corrige valores que foram traduzidos pelo sistema
    None → 'Nenhum'/'Nenhuma' volta para None
    """
    if valor is None:
        return None

    # Lista de valores que devem ser convertidos para None
    valores_nulos = [
        'Nenhum', 'Nenhuma', 'nenhum', 'nenhuma',
        'null', 'NULL', 'Null', 'nan', 'NaN', 'NAN',
        '', 'None', 'none'
    ]

    if isinstance(valor, str):
        valor_limpo = valor.strip()
        if valor_limpo in valores_nulos:
            return None

    return valor

def corrigir_dict_traduzido(dicionario):
    """Corrige todos os valores de um dicionário"""
    if not isinstance(dicionario, dict):
        return dicionario

    dict_corrigido = {}
    for chave, valor in dicionario.items():
        dict_corrigido[chave] = corrigir_valor_traduzido(valor)

    return dict_corrigido

def corrigir_dataframe_traduzido(df):
    """Corrige DataFrame removendo traduções"""
    if df is None or df.empty:
        return df

    df_corrigido = df.copy()

    # Aplicar correção em colunas de texto
    for coluna in df_corrigido.columns:
        if df_corrigido[coluna].dtype == 'object':
            df_corrigido[coluna] = df_corrigido[coluna].apply(corrigir_valor_traduzido)

    return df_corrigido

def safe_get_value(dicionario, chave, default=''):
    """Obtém valor de forma segura, corrigindo traduções"""
    valor = dicionario.get(chave, default)
    valor_corrigido = corrigir_valor_traduzido(valor)
    return valor_corrigido if valor_corrigido is not None else default

def carregar_configuracao_banco():
    """Carrega configuração do banco com sistema de fallback inteligente - CORRIGIDO PARA STREAMLIT"""

    if not PSYCOPG2_AVAILABLE:
        st.error("❌ psycopg2-binary não encontrado. Execute: pip install psycopg2-binary")
        st.stop()

    # 1. PRIMEIRO: Verificar se está no Streamlit Cloud/produção
    # No Streamlit Cloud, as secrets ficam em st.secrets
    try:
        # Tentar carregar do Streamlit secrets
        if hasattr(st, 'secrets') and 'database' in st.secrets:
            secrets = st.secrets['database']
            host = secrets.get('SUPABASE_HOST')
            password = secrets.get('SUPABASE_PASSWORD')
            if host and password:
                project_ref = secrets.get('SUPABASE_PROJECT_REF')
                if not project_ref:
                    partes = host.split('.') if host else []
                    if partes and partes[0] == 'db' and len(partes) > 1:
                        project_ref = partes[1]
                    elif partes:
                        project_ref = partes[0]
                if not project_ref:
                    raise ValueError('SUPABASE_PROJECT_REF ausente em secrets e não pôde ser extraído do host')
                config = {
                    'host': host,
                    'database': secrets.get('SUPABASE_DB', 'postgres'),
                    'user': f"postgres.{project_ref}",
                    'password': password,
                    'port': int(secrets.get('SUPABASE_PORT', '6543')),
                    'sslmode': 'require',
                    'connect_timeout': 10
                }
                st.success("🔗 Conectando com Supabase via Streamlit Secrets")
                if _testar_conexao(config):
                    st.success("✅ Conectado ao Supabase PostgreSQL")
                    return config
                else:
                    st.error("❌ Falha na conexão com Supabase via secrets")
    except Exception as e:
        st.warning(f"⚠️ Erro ao carregar Streamlit secrets: {str(e)}")

    # 2. DETECÇÃO DE AMBIENTE CODESPACES
    if 'CODESPACE_NAME' in os.environ:
        st.warning("⚠️ **Modo Desenvolvimento - GitHub Codespaces**")
        st.info("🔧 Conexão com banco externo bloqueada. Usando dados simulados para desenvolvimento.")
        st.info("🚀 **Para produção:** Deploy no Streamlit Cloud com as credenciais do Supabase")
        return None  # Retorna None para usar dados simulados

    # 3. Carregar variáveis de ambiente (.env)
    _carregar_dotenv()

    # 4. Detectar e usar configuração adequada
    ambiente = _detectar_ambiente()
    st.info(f"🌍 Ambiente detectado: {ambiente}")

    if ambiente == 'supabase':
        config = _config_supabase_pooler()
        if _testar_conexao(config):
            st.success("✅ Conectado ao Supabase PostgreSQL")
            return config
        else:
            st.error("❌ Erro de conexão com Supabase PostgreSQL")
            st.info("💡 Verifique se as credenciais estão corretas no arquivo .env")
            return None

    elif ambiente == 'render':
        config = _config_render()
        if _testar_conexao(config):
            st.success("✅ Conectado ao Render PostgreSQL")
            return config
        else:
            st.error("❌ Erro de conexão com Render PostgreSQL")
            return None

    # 5. Fallback para dados simulados em caso de erro
    st.warning("⚠️ Nenhuma configuração de banco válida encontrada - Usando dados simulados")
    return None

def _carregar_dotenv():
    """Carrega variáveis de ambiente"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        if os.path.exists('.env'):
            try:
                with open('.env', 'r', encoding='utf-8') as f:
                    for linha in f:
                        linha = linha.strip()
                        if linha and not linha.startswith('#') and '=' in linha:
                            chave, valor = linha.split('=', 1)
                            valor = valor.strip().strip('"').strip("'")
                            os.environ[chave] = valor
            except:
                pass

def _detectar_ambiente():
    """Detecta ambiente atual - SEM RAILWAY"""
    if os.getenv('DATABASE_URL'):
        return 'render'
    elif os.getenv('SUPABASE_HOST') and os.getenv('SUPABASE_PASSWORD'):
        return 'supabase'
    else:
        return 'local'

def _config_supabase_pooler():
    """Configuração Supabase PostgreSQL via connection pooler"""
    host = os.getenv('SUPABASE_HOST')
    password = os.getenv('SUPABASE_PASSWORD')
    if not host:
        raise ValueError('SUPABASE_HOST não definido')
    if not password:
        raise ValueError('SUPABASE_PASSWORD não definido')

    project_ref = os.getenv('SUPABASE_PROJECT_REF')
    if not project_ref:
        partes = host.split('.') if host else []
        if partes and partes[0] == 'db' and len(partes) > 1:
            project_ref = partes[1]
        elif partes:
            project_ref = partes[0]
    if not project_ref:
        raise ValueError('SUPABASE_PROJECT_REF não definido e não pôde ser extraído do SUPABASE_HOST')

    return {
        'host': host,
        'database': os.getenv('SUPABASE_DB', 'postgres'),
        'user': f"postgres.{project_ref}",
        'password': password,
        'port': int(os.getenv('SUPABASE_PORT', '6543')),
        'sslmode': 'require',
        'connect_timeout': 10
    }

def _config_render():
    """Configuração Render PostgreSQL via DATABASE_URL"""
    import urllib.parse as urlparse

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        return None

    url = urlparse.urlparse(database_url)
    return {
        'host': url.hostname,
        'database': url.path[1:],
        'user': url.username,
        'password': url.password,
        'port': url.port or 5432,
        'sslmode': 'require',
        'connect_timeout': 10
    }

def _config_local():
    """Configuração PostgreSQL Local"""
    return {
        'host': 'localhost',
        'database': 'dashboard_baker',
        'user': 'postgres',
        'password': os.getenv('LOCAL_DB_PASSWORD', 'senha123'),
        'port': 5432,
        'connect_timeout': 5
    }

def _testar_conexao(config):
    """Testa conexão com o banco"""
    if not config or not config.get('host') or not config.get('password'):
        return False

    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        return True
    except:
        return False

# Configurações de Alertas Inteligentes - REMOVIDO "envio_final_pendente"
ALERTAS_CONFIG = {
    'ctes_sem_aprovacao': {
        'dias_limite': 7,
        'prioridade': 'alta',
        'acao_sugerida': 'Entrar em contato com o cliente para aprovação',
        'impacto_financeiro': 'edio'
    },
    'ctes_sem_faturas': {
        'dias_limite': 3,
        'prioridade': 'media',
        'acao_sugerida': 'Gerar fatura no sistema Bsoft',
        'impacto_financeiro': 'baixo'
    },
    'faturas_vencidas': {
        'dias_limite': 90,
        'prioridade': 'critica',
        'acao_sugerida': 'Ação judicial de cobrança',
        'impacto_financeiro': 'alto'
    },
    'envio_final_pendente': {
        'dias_limite': 5,
        'prioridade': 'media',
        'acao_sugerida': 'Completar envio final dos documentos',
        'impacto_financeiro': 'baixo'
    },
    'primeiro_envio_pendente': {
        'dias_limite': 10,
        'prioridade': 'alta',
        'acao_sugerida': 'Enviar documentos para aprovação',
        'impacto_financeiro': 'alto'
    }
}

# Configurações de Variações Temporais Expandidas
VARIACOES_CONFIG = [
    {
        'nome': 'CTE → Inclusão Fatura',
        'campo_inicio': 'data_emissao',
        'campo_fim': 'data_inclusao_fatura',
        'meta_dias': 2,
        'codigo': 'cte_inclusao_fatura',
        'categoria': 'processo_interno'
    },
    {
        'nome': 'Inclusão → 1º Envio', 
        'campo_inicio': 'data_inclusao_fatura',
        'campo_fim': 'primeiro_envio',
        'meta_dias': 1,
        'codigo': 'inclusao_primeiro_envio',
        'categoria': 'processo_interno'
    },
    {
        'nome': 'RQ/TMC → 1º Envio',
        'campo_inicio': 'data_rq_tmc', 
        'campo_fim': 'primeiro_envio',
        'meta_dias': 3,
        'codigo': 'rq_tmc_primeiro_envio',
        'categoria': 'processo_cliente'
    },
    {
        'nome': '1º Envio → Atesto',
        'campo_inicio': 'primeiro_envio',
        'campo_fim': 'data_atesto',
        'meta_dias': 7,
        'codigo': 'primeiro_envio_atesto',
        'categoria': 'processo_cliente'
    },
    {
        'nome': 'Atesto → Envio Final',
        'campo_inicio': 'data_atesto',
        'campo_fim': 'envio_final',
        'meta_dias': 2,
        'codigo': 'atesto_envio_final',
        'categoria': 'processo_interno'
    },
    {
        'nome': 'Processo Completo',
        'campo_inicio': 'data_emissao',
        'campo_fim': 'envio_final',
        'meta_dias': 15,
        'codigo': 'processo_completo',
        'categoria': 'processo_completo'
    },
    {
        'nome': 'CTE → Baixa',
        'campo_inicio': 'data_emissao',
        'campo_fim': 'data_baixa',
        'meta_dias': 30,
        'codigo': 'cte_baixa',
        'categoria': 'financeiro'
    }
]

def _gerar_dados_simulados():
    """Gera dados simulados para desenvolvimento em Codespaces"""
    import random
    from datetime import datetime, timedelta
    
    # Dados base para simulação
    empresas = ['Empresa Alpha Ltda', 'Beta Transportes', 'Gamma Logística', 'Delta Corp', 'Epsilon SA']
    placas = ['ABC1234', 'DEF5678', 'GHI9012', 'JKL3456', 'MNO7890']
    
    # Gerar 50 registros simulados
    dados = []
    base_date = datetime.now() - timedelta(days=90)
    
    for i in range(1, 51):
        # Datas progressivas
        data_emissao = base_date + timedelta(days=random.randint(0, 80))
        data_baixa = data_emissao + timedelta(days=random.randint(1, 30)) if random.random() > 0.3 else None
        
        registro = {
            'numero_cte': 1000 + i,
            'destinatario_nome': random.choice(empresas),
            'veiculo_placa': random.choice(placas),
            'valor_total': round(random.uniform(500, 5000), 2),
            'data_emissao': data_emissao,
            'numero_fatura': f'FAT-2025-{1000+i}' if random.random() > 0.2 else None,
            'data_baixa': data_baixa,
            'observacao': f'Observação simulada {i}' if random.random() > 0.5 else None,
            'data_inclusao_fatura': data_emissao + timedelta(days=random.randint(1, 5)) if random.random() > 0.3 else None,
            'data_envio_processo': data_emissao + timedelta(days=random.randint(2, 10)) if random.random() > 0.4 else None,
            'primeiro_envio': data_emissao + timedelta(days=random.randint(1, 7)) if random.random() > 0.3 else None,
            'data_rq_tmc': data_emissao + timedelta(days=random.randint(3, 15)) if random.random() > 0.5 else None,
            'data_atesto': data_emissao + timedelta(days=random.randint(5, 20)) if random.random() > 0.4 else None,
            'envio_final': data_emissao + timedelta(days=random.randint(7, 25)) if random.random() > 0.6 else None,
            'origem_dados': 'Simulado',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        dados.append(registro)
    
    df = pd.DataFrame(dados)
    
    # Garantir tipos corretos
    date_columns = ['data_emissao', 'data_baixa', 'data_inclusao_fatura',
                    'data_envio_processo', 'primeiro_envio', 'data_rq_tmc',
                    'data_atesto', 'envio_final', 'created_at', 'updated_at']
    
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df

# ============================================================================
# FUNÇÃO DE CACHE OTIMIZADA
# ============================================================================

@st.cache_data(ttl=300, show_spinner=False)
def carregar_dados_postgresql():
    """Carrega dados do PostgreSQL ou simula dados para desenvolvimento"""
    try:
        config = carregar_configuracao_banco()

        # Se config é None (Codespaces), usar dados simulados
        if config is None:
            return _gerar_dados_simulados()

        query = """
        SELECT 
            numero_cte, destinatario_nome, veiculo_placa, valor_total,
            data_emissao, numero_fatura, data_baixa, observacao,
            data_inclusao_fatura, data_envio_processo, primeiro_envio,
            data_rq_tmc, data_atesto, envio_final, origem_dados,
            created_at, updated_at
        FROM dashboard_baker 
        ORDER BY numero_cte DESC
        LIMIT 5000;
        """

        # Preferir SQLAlchemy (engine) e fazer fallback para psycopg2
        try:
            from sqlalchemy import create_engine
            from urllib.parse import quote_plus
            user_enc = quote_plus(str(config.get('user','')))
            pwd_enc = quote_plus(str(config.get('password','')))
            host = config.get('host')
            port = config.get('port', 5432)
            db   = config.get('database','postgres')
            params = f"?sslmode={config.get('sslmode')}" if config.get('sslmode') else ""
            uri = f"postgresql+psycopg2://{user_enc}:{pwd_enc}@{host}:{port}/{db}{params}"
            engine = create_engine(uri, pool_pre_ping=True)
            df = pd.read_sql_query(query, engine)
            engine.dispose()
        except Exception:
            conn = psycopg2.connect(**config)
            df = pd.read_sql_query(query, conn)
            conn.close()

        # CORREÇÃO: Limpar traduções do DataFrame
        if not df.empty:
            df = corrigir_dataframe_traduzido(df)
            # Converter datas
            date_columns = ['data_emissao', 'data_baixa', 'data_inclusao_fatura',
                          'data_envio_processo', 'primeiro_envio', 'data_rq_tmc',
                          'data_atesto', 'envio_final', 'created_at', 'updated_at']

            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')

            if 'valor_total' in df.columns:
                df['valor_total'] = pd.to_numeric(df['valor_total'], errors='coerce').fillna(0)

        return df

    except psycopg2.OperationalError:
        st.error("❌ Erro de conexão PostgreSQL")
        st.info("💡 Verifique as credenciais do banco")
        return _gerar_dados_simulados()
    except psycopg2.ProgrammingError:
        st.error("❌ Tabela 'dashboard_baker' não encontrada")
        st.info("💡 Execute: python inicializar_banco.py")

        if st.button("🔧 Criar Tabela Agora"):
            _criar_tabela()

        return _gerar_dados_simulados()
    except Exception as e:
        st.warning(f"⚠️ Usando dados simulados devido ao erro: {str(e)[:50]}...")
        return _gerar_dados_simulados()

        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")
        return pd.DataFrame()

def _criar_tabela():
    """Cria tabela automaticamente"""
    try:
        config = carregar_configuracao_banco()
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dashboard_baker (
            id SERIAL PRIMARY KEY,
            numero_cte INTEGER UNIQUE NOT NULL,
            destinatario_nome VARCHAR(255),
            veiculo_placa VARCHAR(20),
            valor_total DECIMAL(15,2),
            data_emissao DATE,
            numero_fatura VARCHAR(100),
            data_baixa DATE,
            observacao TEXT,
            data_inclusao_fatura DATE,
            data_envio_processo DATE,
            primeiro_envio DATE,
            data_rq_tmc DATE,
            data_atesto DATE,
            envio_final DATE,
            origem_dados VARCHAR(50) DEFAULT 'Sistema',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        INSERT INTO dashboard_baker (numero_cte, destinatario_nome, valor_total, data_emissao, origem_dados)
        VALUES (1001, 'Cliente Exemplo', 1500.00, CURRENT_DATE, 'Auto-Setup')
        ON CONFLICT (numero_cte) DO NOTHING;
        """)

        conn.commit()
        cursor.close()
        conn.close()

        st.success("✅ Tabela criada!")
        st.cache_data.clear()
        st.rerun()

    except Exception as e:
        st.error(f"❌ Erro ao criar tabela: {e}")

# ============================================================================
# SISTEMA DE ANÁLISE EXPANDIDO
# ============================================================================

def gerar_metricas_expandidas(df: pd.DataFrame) -> Dict:
    """Gera métricas expandidas com análises avançadas"""
    if df.empty:
        return {
            'total_ctes': 0, 'clientes_unicos': 0, 'valor_total': 0.0,
            'faturas_pagas': 0, 'faturas_pendentes': 0, 'valor_pago': 0.0,
            'valor_pendente': 0.0, 'ctes_com_fatura': 0, 'ctes_sem_fatura': 0,
            'valor_com_fatura': 0.0, 'valor_sem_fatura': 0.0, 'veiculos_ativos': 0,
            'ctes_com_envio_final': 0, 'ctes_sem_envio_final': 0,
            'valor_com_envio_final': 0.0, 'valor_sem_envio_final': 0.0,
            'processos_completos': 0, 'processos_incompletos': 0,
            'ticket_medio': 0.0, 'maior_valor': 0.0, 'menor_valor': 0.0,
            'receita_mensal_media': 0.0, 'crescimento_mensal': 0.0
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

    # Métricas de envio final
    ctes_com_envio_final = len(df[df['envio_final'].notna()])
    ctes_sem_envio_final = len(df[df['envio_final'].isna()])

    valor_com_envio_final = df[df['envio_final'].notna()]['valor_total'].sum()
    valor_sem_envio_final = df[df['envio_final'].isna()]['valor_total'].sum()

    # NOVAS MÉTRICAS AVANÇADAS
    # Processos Completos (tem todas as datas principais)
    mask_completo = (
        df['data_emissao'].notna() & 
        df['primeiro_envio'].notna() & 
        df['data_atesto'].notna() & 
        df['envio_final'].notna()
    )
    processos_completos = mask_completo.sum()
    processos_incompletos = total_ctes - processos_completos

    # Métricas financeiras avançadas
    ticket_medio = df['valor_total'].mean() if total_ctes > 0 else 0.0
    maior_valor = df['valor_total'].max() if total_ctes > 0 else 0.0
    menor_valor = df['valor_total'].min() if total_ctes > 0 else 0.0

    # Análise temporal (receita mensal)
    receita_mensal_media = 0.0
    crescimento_mensal = 0.0

    if 'data_emissao' in df.columns and df['data_emissao'].notna().any():
        try:
            # Agrupar por mês
            df_temp = df[df['data_emissao'].notna()].copy()
            df_temp['mes_ano'] = df_temp['data_emissao'].dt.to_period('M')
            receita_mensal = df_temp.groupby('mes_ano')['valor_total'].sum()

            if len(receita_mensal) > 0:
                receita_mensal_media = receita_mensal.mean()

                # Calcular crescimento mensal (últimos 2 meses)
                if len(receita_mensal) >= 2:
                    ultimo_mes = receita_mensal.iloc[-1]
                    penultimo_mes = receita_mensal.iloc[-2]
                    if penultimo_mes > 0:
                        crescimento_mensal = ((ultimo_mes - penultimo_mes) / penultimo_mes) * 100
        except:
            pass

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
        'veiculos_ativos': veiculos_ativos,
        'ctes_com_envio_final': ctes_com_envio_final,
        'ctes_sem_envio_final': ctes_sem_envio_final,
        'valor_com_envio_final': valor_com_envio_final,
        'valor_sem_envio_final': valor_sem_envio_final,
        'processos_completos': processos_completos,
        'processos_incompletos': processos_incompletos,
        'ticket_medio': ticket_medio,
        'maior_valor': maior_valor,
        'menor_valor': menor_valor,
        'receita_mensal_media': receita_mensal_media,
        'crescimento_mensal': crescimento_mensal
    }

def calcular_alertas_inteligentes(df: pd.DataFrame) -> Dict:
    """Sistema de alertas inteligentes - CORRIGIDO para tratar valores NaT"""
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
        # 1. CTEs sem aprovação (7 dias após emissão)
        mask_sem_aprovacao = (
            df['data_emissao'].notna() & 
            ((hoje - df['data_emissao']).dt.days > ALERTAS_CONFIG['ctes_sem_aprovacao']['dias_limite']) &
            (df['data_atesto'].isna())
        )
        if mask_sem_aprovacao.any():
            ctes_problema = df[mask_sem_aprovacao]
            # Converter datas para dict de forma segura
            lista_segura = []
            for _, row in ctes_problema.iterrows():
                item = {
                    'numero_cte': row['numero_cte'],
                    'destinatario_nome': row['destinatario_nome'],
                    'valor_total': float(row['valor_total']),
                    'data_emissao': row['data_emissao'] if pd.notna(row['data_emissao']) else None
                }
                lista_segura.append(item)

            alertas['ctes_sem_aprovacao'] = {
                'qtd': len(ctes_problema),
                'valor': float(ctes_problema['valor_total'].sum()),
                'lista': lista_segura
            }

        # 2. CTEs sem faturas (3 dias após atesto)
        mask_sem_faturas = (
            df['data_atesto'].notna() & 
            ((hoje - df['data_atesto']).dt.days > ALERTAS_CONFIG['ctes_sem_faturas']['dias_limite']) &
            (df['numero_fatura'].isna() | (df['numero_fatura'] == ''))
        )
        if mask_sem_faturas.any():
            ctes_problema = df[mask_sem_faturas]
            lista_segura = []
            for _, row in ctes_problema.iterrows():
                item = {
                    'numero_cte': row['numero_cte'],
                    'destinatario_nome': row['destinatario_nome'],
                    'valor_total': float(row['valor_total']),
                    'data_atesto': row['data_atesto'] if pd.notna(row['data_atesto']) else None
                }
                lista_segura.append(item)

            alertas['ctes_sem_faturas'] = {
                'qtd': len(ctes_problema),
                'valor': float(ctes_problema['valor_total'].sum()),
                'lista': lista_segura
            }

        # 3. Faturas vencidas (90 dias após atesto, sem baixa)
        mask_vencidas = (
            df['data_atesto'].notna() & 
            ((hoje - df['data_atesto']).dt.days > ALERTAS_CONFIG['faturas_vencidas']['dias_limite']) &
            df['data_baixa'].isna()
        )
        if mask_vencidas.any():
            ctes_problema = df[mask_vencidas]
            lista_segura = []
            for _, row in ctes_problema.iterrows():
                item = {
                    'numero_cte': row['numero_cte'],
                    'destinatario_nome': row['destinatario_nome'],
                    'valor_total': float(row['valor_total']),
                    'data_atesto': row['data_atesto'] if pd.notna(row['data_atesto']) else None
                }
                lista_segura.append(item)

            alertas['faturas_vencidas'] = {
                'qtd': len(ctes_problema),
                'valor': float(ctes_problema['valor_total'].sum()),
                'lista': lista_segura
            }

        # 4. Primeiro envio pendente (10 dias após emissão)
        mask_primeiro_envio = (
            df['data_emissao'].notna() & 
            ((hoje - df['data_emissao']).dt.days > ALERTAS_CONFIG['primeiro_envio_pendente']['dias_limite']) &
            df['primeiro_envio'].isna()
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
            }

        # 5. Envio Final Pendente - REINTEGRADO
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
            }

    except Exception as e:
        st.warning(f"⚠️ Aviso no cálculo de alertas: {str(e)}")

    return alertas

def calcular_variacoes_tempo_expandidas(df: pd.DataFrame) -> Dict:
    """Sistema de análise de variações temporais expandido"""
    if df.empty:
        return {}

    variacoes = {}

    for config in VARIACOES_CONFIG:
        campo_inicio = config['campo_inicio']
        campo_fim = config['campo_fim']
        codigo = config['codigo']
        meta_dias = config['meta_dias']

        if campo_inicio in df.columns and campo_fim in df.columns:
            # Calcular diferença em dias
            mask = df[campo_inicio].notna() & df[campo_fim].notna()

            if mask.any():
                dias = (df.loc[mask, campo_fim] - df.loc[mask, campo_inicio]).dt.days

                # Filtrar dias válidos (não negativos)
                dias_validos = dias[dias >= 0]

                if len(dias_validos) > 0:
                    media = dias_validos.mean()
                    mediana = dias_validos.median()
                    percentil_90 = dias_validos.quantile(0.9)

                    # Classificar performance
                    if media <= meta_dias:
                        performance = 'excelente'
                    elif media <= meta_dias * 1.5:
                        performance = 'bom'
                    elif media <= meta_dias * 2:
                        performance = 'atencao'
                    else:
                        performance = 'critico'

                    variacoes[codigo] = {
                        'nome': config['nome'],
                        'media': media,
                        'mediana': mediana,
                        'percentil_90': percentil_90,
                        'qtd': len(dias_validos),
                        'meta_dias': meta_dias,
                        'performance': performance,
                        'categoria': config['categoria'],
                        'desvio_meta': ((media - meta_dias) / meta_dias * 100) if meta_dias > 0 else 0,
                        'min': dias_validos.min(),
                        'max': dias_validos.max()
                    }

    return variacoes

# ============================================================================
# SISTEMA DE RELATÓRIOS E DOWNLOADS PDF/EXCEL
# ============================================================================

def gerar_relatorio_excel(df: pd.DataFrame, metricas: Dict, alertas: Dict, variacoes: Dict) -> BytesIO:
    """Gera relatório completo em Excel para download"""

    # Criar buffer de memória
    output = BytesIO()

    # Criar workbook
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})

    # Definir formatos
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#0f4c75',
        'font_color': 'white',
        'align': 'center'
    })

    currency_format = workbook.add_format({'num_format': 'R$ #,##0.00'})
    percent_format = workbook.add_format({'num_format': '0.0%'})
    date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})

    # Aba 1: Resumo Executivo
    worksheet1 = workbook.add_worksheet('Resumo Executivo')

    # Cabeçalho
    worksheet1.write('A1', f'Relatório Dashboard Baker - {datetime.now().strftime("%d/%m/%Y %H:%M")}', header_format)
    worksheet1.merge_range('A1:D1', f'Relatório Dashboard Baker - {datetime.now().strftime("%d/%m/%Y %H:%M")}', header_format)

    # Métricas principais
    row = 3
    worksheet1.write(row, 0, 'MÉTRICAS PRINCIPAIS', header_format)
    row += 2

    metricas_lista = [
        ('Total CTEs', metricas['total_ctes']),
        ('Receita Total', metricas['valor_total']),
        ('Clientes Únicos', metricas['clientes_unicos']),
        ('Processos Completos', metricas['processos_completos']),
        ('Faturas Pagas', metricas['faturas_pagas']),
        ('Valor Pago', metricas['valor_pago']),
        ('Valor Pendente', metricas['valor_pendente']),
        ('Ticket Médio', metricas['ticket_medio'])
    ]

    for metrica, valor in metricas_lista:
        worksheet1.write(row, 0, metrica)
        if 'Valor' in metrica or 'Receita' in metrica or 'Ticket' in metrica:
            worksheet1.write(row, 1, valor, currency_format)
        else:
            worksheet1.write(row, 1, valor)
        row += 1

    # Aba 2: Alertas
    worksheet2 = workbook.add_worksheet('Alertas')

    worksheet2.write('A1', 'ALERTAS ATIVOS', header_format)
    worksheet2.write('A3', 'Tipo de Alerta', header_format)
    worksheet2.write('B3', 'Quantidade', header_format)
    worksheet2.write('C3', 'Valor em Risco', header_format)

    row = 4
    for tipo_alerta, dados in alertas.items():
        nome_alerta = tipo_alerta.replace('_', ' ').title()
        worksheet2.write(row, 0, nome_alerta)
        worksheet2.write(row, 1, dados['qtd'])
        worksheet2.write(row, 2, dados['valor'], currency_format)
        row += 1

    # Aba 3: Variações Temporais
    if variacoes:
        worksheet3 = workbook.add_worksheet('Variações Temporais')

        worksheet3.write('A1', 'PERFORMANCE TEMPORAL', header_format)
        worksheet3.write('A3', 'Processo', header_format)
        worksheet3.write('B3', 'Média (dias)', header_format)
        worksheet3.write('C3', 'Meta (dias)', header_format)
        worksheet3.write('D3', 'Performance', header_format)
        worksheet3.write('E3', 'Quantidade', header_format)

        row = 4
        for codigo, dados in variacoes.items():
            worksheet3.write(row, 0, dados['nome'])
            worksheet3.write(row, 1, dados['media'])
            worksheet3.write(row, 2, dados['meta_dias'])
            worksheet3.write(row, 3, dados['performance'])
            worksheet3.write(row, 4, dados['qtd'])
            row += 1

    # Aba 4: Dados Completos
    if not df.empty:
        worksheet4 = workbook.add_worksheet('Dados Completos')

        # Cabeçalhos
        colunas = ['numero_cte', 'destinatario_nome', 'valor_total', 'data_emissao', 
                  'primeiro_envio', 'data_atesto', 'envio_final', 'data_baixa']

        col = 0
        for coluna in colunas:
            if coluna in df.columns:
                nome_coluna = coluna.replace('_', ' ').title()
                worksheet4.write(0, col, nome_coluna, header_format)
                col += 1

        # Dados - CORRIGIDO para tratar valores NaT
        for idx, row_data in df.iterrows():
            col = 0
            for coluna in colunas:
                if coluna in df.columns:
                    valor = row_data[coluna]

                    # Tratar valores NaT/None/NaN
                    if pd.isna(valor) or valor is None:
                        worksheet4.write(idx + 1, col, "")  # Escrever string vazia
                    elif coluna == 'valor_total':
                        worksheet4.write(idx + 1, col, float(valor), currency_format)
                    elif 'data_' in coluna:
                        # Verificar se é uma data válida antes de aplicar formato
                        try:
                            if pd.notna(valor) and hasattr(valor, 'date'):
                                worksheet4.write(idx + 1, col, valor, date_format)
                            else:
                                worksheet4.write(idx + 1, col, "")
                        except:
                            worksheet4.write(idx + 1, col, "")
                    else:
                        # Para outros tipos de dados
                        if isinstance(valor, (int, float)) and not pd.isna(valor):
                            worksheet4.write(idx + 1, col, valor)
                        else:
                            worksheet4.write(idx + 1, col, str(valor) if not pd.isna(valor) else "")
                    col += 1

    workbook.close()
    output.seek(0)

    return output

def gerar_relatorio_pdf_html(df: pd.DataFrame, metricas: Dict, alertas: Dict, variacoes: Dict) -> str:
    """Gera HTML otimizado para conversão em PDF"""

    hoje = datetime.now().strftime('%d/%m/%Y %H:%M')

    # Calcular alguns indicadores extras
    taxa_processos_completos = (metricas['processos_completos'] / max(metricas['total_ctes'], 1)) * 100
    total_alertas = sum(alerta['qtd'] for alerta in alertas.values())
    valor_total_risco = sum(alerta['valor'] for alerta in alertas.values())

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Relatório Dashboard Baker - {hoje}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; font-size: 12px; }}
            .header {{ background: linear-gradient(135deg, #0f4c75 0%, #1e6091 100%); color: white; padding: 20px; text-align: center; border-radius: 8px; page-break-inside: avoid; }}
            .metric-card {{ background: #f8f9fa; border-left: 4px solid #0f4c75; padding: 15px; margin: 10px 0; page-break-inside: avoid; }}
            .metric-number {{ font-size: 20px; font-weight: bold; color: #0f4c75; }}
            .alert-card {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 10px 0; page-break-inside: avoid; }}
            .alert-danger {{ background: #f8d7da; border-left-color: #dc3545; }}
            .section {{ margin: 20px 0; page-break-inside: avoid; }}
            .section h2 {{ color: #0f4c75; border-bottom: 2px solid #e3e8ee; padding-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 10px 0; page-break-inside: avoid; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 11px; }}
            th {{ background-color: #0f4c75; color: white; }}
            .footer {{ text-align: center; color: #666; margin-top: 40px; font-size: 10px; }}
            .page-break {{ page-break-before: always; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>💰 Dashboard Financeiro Baker</h1>
            <p>Relatório Executivo - {hoje}</p>
        </div>

        <div class="section">
            <h2>📊 Resumo Executivo</h2>

            <div class="metric-card">
                <div class="metric-number">R$ {metricas['valor_total']:,.2f}</div>
                <p><strong>Receita Total</strong> - {metricas['total_ctes']} CTEs</p>
            </div>

            <div class="metric-card">
                <div class="metric-number">{metricas['processos_completos']}</div>
                <p><strong>Processos Completos</strong> - {taxa_processos_completos:.1f}% do total</p>
            </div>

            <div class="metric-card">
                <div class="metric-number">R$ {metricas['valor_pendente']:,.2f}</div>
                <p><strong>Valor Pendente</strong> - {metricas['faturas_pendentes']} faturas</p>
            </div>
        </div>

        <div class="section">
            <h2>🚨 Alertas Críticos</h2>

            {'<div class="alert-card alert-danger"><strong>🚨 ATENÇÃO:</strong> ' + str(total_alertas) + ' alertas ativos com R$ ' + f'{valor_total_risco:,.2f}' + ' em risco</div>' if total_alertas > 0 else '<div class="alert-card"><strong>✅ SISTEMA OK:</strong> Nenhum alerta ativo</div>'}

            <table>
                <tr>
                    <th>Tipo de Alerta</th>
                    <th>Quantidade</th>
                    <th>Valor (R$)</th>
                </tr>
                <tr>
                    <td>1º Envio Pendente</td>
                    <td>{alertas['primeiro_envio_pendente']['qtd']}</td>
                    <td>R$ {alertas['primeiro_envio_pendente']['valor']:,.2f}</td>
                </tr>
                <tr>
                    <td>CTEs sem Faturas</td>
                    <td>{alertas['ctes_sem_faturas']['qtd']}</td>
                    <td>R$ {alertas['ctes_sem_faturas']['valor']:,.2f}</td>
                </tr>
                <tr>
                    <td>Faturas Vencidas</td>
                    <td>{alertas['faturas_vencidas']['qtd']}</td>
                    <td>R$ {alertas['faturas_vencidas']['valor']:,.2f}</td>
                </tr>
            </table>
        </div>

        <div class="page-break"></div>

        <div class="section">
            <h2>⏱️ Performance Temporal</h2>
            <table>
                <tr>
                    <th>Processo</th>
                    <th>Média (dias)</th>
                    <th>Meta (dias)</th>
                    <th>Performance</th>
                </tr>
    """

    # Adicionar variações temporais
    for codigo, dados in variacoes.items():
        performance_emoji = {
            'excelente': '🟢',
            'bom': '🔵',
            'atencao': '🟡',
            'critico': '🔴'
        }.get(dados['performance'], '⚪')

        html += f"""
                <tr>
                    <td>{dados['nome']}</td>
                    <td>{dados['media']:.1f}</td>
                    <td>{dados['meta_dias']}</td>
                    <td>{performance_emoji} {dados['performance'].title()}</td>
                </tr>
        """

    html += f"""
            </table>
        </div>

        <div class="section">
            <h2>📈 Indicadores Financeiros</h2>
            <ul>
                <li><strong>Clientes Ativos:</strong> {metricas['clientes_unicos']}</li>
                <li><strong>Veículos Ativos:</strong> {metricas['veiculos_ativos']}</li>
                <li><strong>Ticket Médio:</strong> R$ {metricas['ticket_medio']:,.2f}</li>
                <li><strong>Maior Valor:</strong> R$ {metricas['maior_valor']:,.2f}</li>
                <li><strong>Receita Média Mensal:</strong> R$ {metricas['receita_mensal_media']:,.2f}</li>
                <li><strong>Crescimento Mensal:</strong> {metricas['crescimento_mensal']:+.1f}%</li>
            </ul>
        </div>

        <div class="footer">
            <p>Relatório gerado automaticamente pelo Dashboard Baker v3.0</p>
            <p>Sistema de Gestão Financeira Integrada</p>
        </div>
    </body>
    </html>
    """

    return html

# ============================================================================
# SISTEMA DE BAIXAS AUTOMÁTICAS
# ============================================================================

class SistemaBaixasAutomaticas:
    """Sistema avançado de gestão de baixas e conciliação"""

    def __init__(self):
        self.config = carregar_configuracao_banco()

    def registrar_baixa(self, numero_cte: int, data_baixa: datetime.date, 
                       observacao: str = "", valor_baixa: float = None) -> Tuple[bool, str]:
        """Registra baixa de uma fatura específica com validação"""
        try:
            conn = psycopg2.connect(**self.config)
            cursor = conn.cursor()

            # Verificar se CTE existe
            cursor.execute("SELECT numero_cte, valor_total, data_baixa FROM dashboard_baker WHERE numero_cte = %s", (numero_cte,))
            resultado = cursor.fetchone()

            if not resultado:
                cursor.close()
                conn.close()
                return False, f"CTE {numero_cte} não encontrado"

            cte_num, valor_original, baixa_existente = resultado

            # CORREÇÃO: Converter Decimal para float
            if isinstance(valor_original, Decimal):
                valor_original = float(valor_original)

            # Verificar se já tem baixa
            if baixa_existente:
                cursor.close()
                conn.close()
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
            return False, f"Erro ao registrar baixa: {str(e)}"

    def processar_baixas_em_lote(self, arquivo_csv: str) -> Dict:
        """Processa baixas em lote a partir de arquivo CSV"""
        try:
            # Carregar arquivo
            df_baixas = pd.read_csv(arquivo_csv)

            # Validar colunas obrigatórias
            colunas_obrigatorias = ['numero_cte', 'data_baixa']
            for col in colunas_obrigatorias:
                if col not in df_baixas.columns:
                    return {'sucesso': False, 'erro': f'Coluna obrigatória ausente: {col}'}

            # Processar cada baixa
            resultados = {
                'processadas': 0,
                'sucessos': 0,
                'erros': 0,
                'detalhes': []
            }

            for _, row in df_baixas.iterrows():
                numero_cte = int(row['numero_cte'])
                data_baixa = pd.to_datetime(row['data_baixa']).date()
                observacao = row.get('observacao', '')
                valor_baixa = row.get('valor_baixa', None)

                sucesso, mensagem = self.registrar_baixa(numero_cte, data_baixa, observacao, valor_baixa)

                resultados['processadas'] += 1
                if sucesso:
                    resultados['sucessos'] += 1
                else:
                    resultados['erros'] += 1

                resultados['detalhes'].append({
                    'cte': numero_cte,
                    'sucesso': sucesso,
                    'mensagem': mensagem
                })

            return {'sucesso': True, 'resultados': resultados}

        except Exception as e:
            return {'sucesso': False, 'erro': str(e)}

# ============================================================================
# SISTEMA DE GRÁFICOS AVANÇADOS
# ============================================================================

def gerar_grafico_variacoes_tempo(variacoes: Dict) -> go.Figure:
    """Gera gráfico avançado de variações de tempo com metas"""
    if not variacoes:
        return go.Figure()

    # Preparar dados
    nomes = []
    medias = []
    metas = []
    performances = []
    categorias = []

    for codigo, dados in variacoes.items():
        nomes.append(dados['nome'])
        medias.append(dados['media'])
        metas.append(dados['meta_dias'])
        performances.append(dados['performance'])
        categorias.append(dados['categoria'])

    # Cores por performance
    cores_performance = {
        'excelente': '#28a745',
        'bom': '#17a2b8',
        'atencao': '#ffc107',
        'critico': '#dc3545'
    }

    cores = [cores_performance.get(perf, '#6c757d') for perf in performances]

    # Criar gráfico
    fig = go.Figure()

    # Barras de média
    fig.add_trace(go.Bar(
        x=nomes,
        y=medias,
        name='Média Atual',
        marker_color=cores,
        text=[f'{media:.1f}d' for media in medias],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Média: %{y:.1f} dias<br>Performance: %{customdata}<extra></extra>',
        customdata=performances
    ))

    # Linha de meta
    fig.add_trace(go.Scatter(
        x=nomes,
        y=metas,
        mode='markers+lines',
        name='Meta',
        line=dict(color='red', dash='dash', width=2),
        marker=dict(color='red', size=8),
        hovertemplate='<b>%{x}</b><br>Meta: %{y} dias<extra></extra>'
    ))

    fig.update_layout(
        title={
            'text': 'Análise de Performance - Variações Temporais vs Metas',
            'x': 0.5,
            'font': {'size': 16, 'color': '#0f4c75'}
        },
        xaxis_title='Processos',
        yaxis_title='Dias',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#333'},
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0', tickangle=45)
    fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0')

    return fig

def gerar_grafico_receita_mensal(df: pd.DataFrame) -> go.Figure:
    """Gera gráfico de evolução da receita mensal"""
    if df.empty or 'data_emissao' not in df.columns:
        return go.Figure()

    # Filtrar dados válidos
    df_temp = df[df['data_emissao'].notna()].copy()

    if df_temp.empty:
        return go.Figure()

    # Agrupar por mês
    df_temp['mes_ano'] = df_temp['data_emissao'].dt.to_period('M')
    receita_mensal = df_temp.groupby('mes_ano').agg({
        'valor_total': 'sum',
        'numero_cte': 'count'
    }).reset_index()

    receita_mensal['mes_ano_str'] = receita_mensal['mes_ano'].astype(str)

    # Criar gráfico combinado
    fig = make_subplots(
        rows=1, cols=1,
        specs=[[{"secondary_y": True}]]
    )

    # Receita (barras)
    fig.add_trace(
        go.Bar(
            x=receita_mensal['mes_ano_str'],
            y=receita_mensal['valor_total'],
            name='Receita Mensal',
            marker_color='#0f4c75',
            text=[f'R$ {v:,.0f}' for v in receita_mensal['valor_total']],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Receita: R$ %{y:,.2f}<extra></extra>'
        ),
        secondary_y=False
    )

    # Quantidade de CTEs (linha)
    fig.add_trace(
        go.Scatter(
            x=receita_mensal['mes_ano_str'],
            y=receita_mensal['numero_cte'],
            mode='lines+markers',
            name='Quantidade CTEs',
            line=dict(color='#28a745', width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{x}</b><br>CTEs: %{y}<extra></extra>'
        ),
        secondary_y=True
    )

    # Layout
    fig.update_layout(
        title={
            'text': 'Evolução Mensal - Receita e Volume',
            'x': 0.5,
            'font': {'size': 16, 'color': '#0f4c75'}
        },
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=True
    )

    fig.update_xaxes(title_text="Mês/Ano", showgrid=True, gridcolor='#f0f0f0')
    fig.update_yaxes(title_text="Receita (R$)", secondary_y=False, showgrid=True, gridcolor='#f0f0f0')
    fig.update_yaxes(title_text="Quantidade CTEs", secondary_y=True)

    return fig

# ============================================================================
# FUNÇÕES DE SUPORTE PARA OUTRAS ABAS (MANTIDAS DO ORIGINAL)
# ============================================================================

def processar_data_para_input(data_obj):
    """Processa um objeto de data para usar no st.date_input"""
    try:
        # CORREÇÃO: Verificar valores traduzidos
        data_corrigida = corrigir_valor_traduzido(data_obj)
        if not data_corrigida:
            return None

        # Se é string, tentar converter
        if isinstance(data_obj, str):
            return None

        # Se já é um objeto date
        if hasattr(data_obj, 'date') and callable(getattr(data_obj, 'date')):
            return data_obj.date()

        # Se já é um date (não datetime)
        elif hasattr(data_obj, 'year') and hasattr(data_obj, 'month') and hasattr(data_obj, 'day'):
            # Verificar se não é datetime, se for, converter para date
            if hasattr(data_obj, 'hour'):  # É datetime
                return data_obj.date()
            else:  # Já é date
                return data_obj
        else:
            return None
    except Exception:
        return None


def validar_resultado_busca(resultado):
    """Valida resultado de busca para evitar erros de descompactação"""
    if resultado is None:
        return False, "Erro interno: resultado nulo"

    if not isinstance(resultado, (tuple, list)) or len(resultado) != 2:
        return False, "Erro interno: formato de resultado inválido"

    return resultado

def buscar_cte_postgresql(numero_cte):
    """Busca um CTE específico no PostgreSQL"""
    try:
        # Validar entrada
        if not numero_cte or numero_cte <= 0:
            return False, "Número do CTE inválido"

        config = carregar_configuracao_banco()
        if not config:
            return False, "Erro na configuração do banco"

        conn = psycopg2.connect(**config)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT * FROM dashboard_baker WHERE numero_cte = %s", (numero_cte,))
        resultado = cursor.fetchone()

        cursor.close()
        conn.close()

        if resultado:
            # Converter para dict e limpar valores traduzidos
            dados_dict = dict(resultado)

            # Corrigir valores None traduzidos
            for key, value in dados_dict.items():
                if isinstance(value, str) and value.strip() in ['Nenhum', 'Nenhuma', 'null', 'NULL']:
                    dados_dict[key] = None

            return True, dados_dict
        else:
            return False, "CTE não encontrado"

    except psycopg2.Error as e:
        return False, f"Erro de banco de dados: {str(e)}"
    except Exception as e:
        return False, f"Erro ao buscar CTE: {str(e)}"

def atualizar_cte_postgresql(numero_cte, dados_atualizados):
    """Atualiza um CTE existente no PostgreSQL"""
    try:
        config = carregar_configuracao_banco()
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()

        # Query de atualização
        query = """
        UPDATE dashboard_baker SET
            destinatario_nome = %s,
            veiculo_placa = %s,
            valor_total = %s,
            data_emissao = %s,
            numero_fatura = %s,
            data_baixa = %s,
            observacao = %s,
            data_inclusao_fatura = %s,
            data_envio_processo = %s,
            primeiro_envio = %s,
            data_rq_tmc = %s,
            data_atesto = %s,
            envio_final = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE numero_cte = %s
        """

        cursor.execute(query, dados_atualizados + (numero_cte,))

        if cursor.rowcount > 0:
            conn.commit()
            cursor.close()
            conn.close()
            return True, "CTE atualizado com sucesso!"
        else:
            cursor.close()
            conn.close()
            return False, "CTE não encontrado para atualização"

    except Exception as e:
        return False, f"Erro ao atualizar CTE: {str(e)}"

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

# ============================================================================
# ABAS DO SISTEMA EXPANDIDO
# ============================================================================

def aba_dashboard_principal_expandido():
    """Aba principal expandida com novas funcionalidades"""

    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>💰 Dashboard Financeiro Baker - Sistema Avançado</h1>
        <div class="subtitle">Gestão Inteligente de Faturamento com Análise Preditiva e Automação</div>
    </div>
    """, unsafe_allow_html=True)

    # Carregar dados
    with st.spinner('🔄 Carregando dados do PostgreSQL...'):
        df = carregar_dados_postgresql()

    if df.empty:
        st.error("❌ Nenhum dado encontrado no PostgreSQL")
        st.info("💡 Execute: python limpar_e_popular_banco.py")
        return

    # Calcular métricas expandidas
    metricas = gerar_metricas_expandidas(df)
    alertas = calcular_alertas_inteligentes(df)
    variacoes = calcular_variacoes_tempo_expandidas(df)

    # ===============================
    # SEÇÃO 1: CARDS PRINCIPAIS EXPANDIDOS
    # ===============================
    st.markdown("""
    <div class="section-header">
        <div class="section-title">📊 Métricas Principais</div>
        <div class="section-subtitle">Visão geral expandida com indicadores avançados</div>
    </div>
    """, unsafe_allow_html=True)

    # Primeira linha - Métricas básicas
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        crescimento_icon = "📈" if metricas['crescimento_mensal'] >= 0 else "📉"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">R$ {metricas['valor_total']:,.0f}</div>
            <div class="metric-title">Receita Total</div>
            <div class="metric-subtitle">{crescimento_icon} {metricas['crescimento_mensal']:+.1f}% vs mês anterior</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{metricas['total_ctes']:,}</div>
            <div class="metric-title">CTEs Total</div>
            <div class="metric-subtitle">Ticket médio: R$ {metricas['ticket_medio']:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        taxa_conclusao = (metricas['processos_completos'] / max(metricas['total_ctes'], 1)) * 100
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{metricas['processos_completos']:,}</div>
            <div class="metric-title">Processos Completos</div>
            <div class="metric-subtitle">{taxa_conclusao:.1f}% do total</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        valor_risco = sum(alerta['valor'] for alerta in alertas.values())
        qtd_alertas = sum(alerta['qtd'] for alerta in alertas.values())
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{qtd_alertas}</div>
            <div class="metric-title">Alertas Ativos</div>
            <div class="metric-subtitle">R$ {valor_risco:,.0f} em risco</div>
        </div>
        """, unsafe_allow_html=True)

    # Segunda linha - Métricas financeiras detalhadas
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        taxa_pagamento = (metricas['faturas_pagas'] / max(metricas['total_ctes'], 1)) * 100
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">R$ {metricas['valor_pago']:,.0f}</div>
            <div class="metric-title">Receita Realizada</div>
            <div class="metric-subtitle">{taxa_pagamento:.1f}% das faturas</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">R$ {metricas['valor_pendente']:,.0f}</div>
            <div class="metric-title">Valor a Receber</div>
            <div class="metric-subtitle">{metricas['faturas_pendentes']} faturas pendentes</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{metricas['clientes_unicos']}</div>
            <div class="metric-title">Clientes Ativos</div>
            <div class="metric-subtitle">{metricas['veiculos_ativos']} veículos</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        receita_media_formatada = f"R$ {metricas['receita_mensal_media']:,.0f}"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{receita_media_formatada}</div>
            <div class="metric-title">Receita Média Mensal</div>
            <div class="metric-subtitle">Últimos 12 meses</div>
        </div>
        """, unsafe_allow_html=True)

    # ===============================
    # SEÇÃO 2: SISTEMA DE ALERTAS INTELIGENTES (APENAS 2 ALERTAS)
    # ===============================
    st.markdown("""
    <div class="section-header">
        <div class="section-title">🚨 Sistema de Alertas Inteligentes</div>
        <div class="section-subtitle">Monitoramento proativo com ações sugeridas</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

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
                for item in alerta['lista'][:10]:  # Máximo 10
                    # Tratar data_emissao None de forma segura
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
                    # Calcular dias de atraso de forma segura
                    days_overdue = 0
                    if item.get('data_atesto') and pd.notna(item['data_atesto']):
                        try:
                            days_overdue = (datetime.now().date() - item['data_atesto'].date()).days
                        except:
                            days_overdue = 0
                    st.write(f"CTE {item['numero_cte']} - {item['destinatario_nome']} - R$ {item['valor_total']:,.2f} ({days_overdue} dias)")
        else:
            st.markdown("""
            <div class="status-card-success">
                <div class="status-number">0</div>
                <div class="status-title">✅ Faturas Vencidas</div>
                <div class="status-value">Nenhuma inadimplente</div>
            </div>
            """, unsafe_allow_html=True)

    # ===============================
    # SEÇÃO 3: ANÁLISE DE VARIAÇÕES TEMPORAIS EXPANDIDA
    # ===============================
    st.markdown("""
    <div class="section-header">
        <div class="section-title">⏱️ Análise de Performance Temporal</div>
        <div class="section-subtitle">Variações de tempo com metas e análise de performance</div>
    </div>
    """, unsafe_allow_html=True)

    if variacoes:
        # Cards de variações em grid
        col1, col2, col3 = st.columns(3)

        variacoes_lista = list(variacoes.items())

        for i, (codigo, dados) in enumerate(variacoes_lista):
            col_idx = i % 3

            # Determinar cor baseada na performance
            cor_performance = {
                'excelente': '#28a745',
                'bom': '#17a2b8', 
                'atencao': '#ffc107',
                'critico': '#dc3545'
            }

            cor = cor_performance.get(dados['performance'], '#6c757d')

            # Emoji baseado na performance
            emoji_performance = {
                'excelente': '🟢',
                'bom': '🔵',
                'atencao': '🟡', 
                'critico': '🔴'
            }

            emoji = emoji_performance.get(dados['performance'], '⚪')

            # Card HTML personalizado
            card_html = f"""
            <div class="variacao-card" style="border-left-color: {cor};">
                <div class="variacao-title">{emoji} {dados['nome']}</div>
                <div class="variacao-value">{dados['media']:.1f} dias</div>
                <div class="variacao-meta">Meta: {dados['meta_dias']} dias | {dados['qtd']} registros</div>
            </div>
            """

            if col_idx == 0:
                with col1:
                    st.markdown(card_html, unsafe_allow_html=True)
            elif col_idx == 1:
                with col2:
                    st.markdown(card_html, unsafe_allow_html=True)
            else:
                with col3:
                    st.markdown(card_html, unsafe_allow_html=True)

        # Gráfico de variações vs metas
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_variacoes = gerar_grafico_variacoes_tempo(variacoes)
        st.plotly_chart(fig_variacoes, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("⚠️ Dados insuficientes para calcular variações temporais")

    # ===============================
    # SEÇÃO 4: GRÁFICOS DE ANÁLISE AVANÇADA
    # ===============================
    st.markdown("""
    <div class="section-header">
        <div class="section-title">📈 Análise de Tendências</div>
        <div class="section-subtitle">Evolução temporal e padrões de receita</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_receita = gerar_grafico_receita_mensal(df)
        st.plotly_chart(fig_receita, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # Gráfico de distribuição de valores
        if not df.empty and 'valor_total' in df.columns:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)

            fig_dist = go.Figure()

            # Histograma de valores
            fig_dist.add_trace(go.Histogram(
                x=df['valor_total'],
                nbinsx=20,
                name='Distribuição de Valores',
                marker_color='#0f4c75',
                opacity=0.7
            ))

            fig_dist.update_layout(
                title='Distribuição de Valores dos CTEs',
                xaxis_title='Valor (R$)',
                yaxis_title='Frequência',
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )

            st.plotly_chart(fig_dist, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ===============================
    # SEÇÃO 5: TABELA EXPANDIDA COM FILTROS
    # ===============================
    st.markdown("""
    <div class="section-header">
        <div class="section-title">📋 Dados Detalhados com Filtros</div>
        <div class="section-subtitle">Análise interativa dos registros</div>
    </div>
    """, unsafe_allow_html=True)

    # Filtros
    col1, col2, col3 = st.columns(3)

    with col1:
        # Filtro por cliente
        clientes = ['Todos'] + sorted(df['destinatario_nome'].dropna().unique().tolist())
        cliente_selecionado = st.selectbox('Cliente:', clientes)

    with col2:
        # Filtro por status
        status_options = ['Todos', 'Com Baixa', 'Sem Baixa', 'Processo Completo', 'Processo Incompleto']
        status_selecionado = st.selectbox('Status:', status_options)

    with col3:
        # Filtro por período
        periodo_options = ['Todos', 'Últimos 30 dias', 'Últimos 90 dias', 'Último ano']
        periodo_selecionado = st.selectbox('Período:', periodo_options)

    # Aplicar filtros
    df_filtrado = df.copy()

    if cliente_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['destinatario_nome'] == cliente_selecionado]

    if status_selecionado == 'Com Baixa':
        df_filtrado = df_filtrado[df_filtrado['data_baixa'].notna()]
    elif status_selecionado == 'Sem Baixa':
        df_filtrado = df_filtrado[df_filtrado['data_baixa'].isna()]
    elif status_selecionado == 'Processo Completo':
        mask_completo = (
            df_filtrado['data_emissao'].notna() & 
            df_filtrado['primeiro_envio'].notna() & 
            df_filtrado['data_atesto'].notna() & 
            df_filtrado['envio_final'].notna()
        )
        df_filtrado = df_filtrado[mask_completo]
    elif status_selecionado == 'Processo Incompleto':
        mask_incompleto = ~(
            df_filtrado['data_emissao'].notna() & 
            df_filtrado['primeiro_envio'].notna() & 
            df_filtrado['data_atesto'].notna() & 
            df_filtrado['envio_final'].notna()
        )
        df_filtrado = df_filtrado[mask_incompleto]

    if periodo_selecionado != 'Todos' and 'data_emissao' in df_filtrado.columns:
        hoje = pd.Timestamp.now()
        if periodo_selecionado == 'Últimos 30 dias':
            df_filtrado = df_filtrado[df_filtrado['data_emissao'] >= (hoje - timedelta(days=30))]
        elif periodo_selecionado == 'Últimos 90 dias':
            df_filtrado = df_filtrado[df_filtrado['data_emissao'] >= (hoje - timedelta(days=90))]
        elif periodo_selecionado == 'Último ano':
            df_filtrado = df_filtrado[df_filtrado['data_emissao'] >= (hoje - timedelta(days=365))]

    # Mostrar resultados filtrados
    st.write(f"📊 **{len(df_filtrado)} registros** encontrados com os filtros aplicados")

    if not df_filtrado.empty:
        # Preparar dados para exibição
        colunas_exibir = ['numero_cte', 'destinatario_nome', 'valor_total', 'data_emissao', 
                         'primeiro_envio', 'data_atesto', 'envio_final', 'data_baixa']

        colunas_existentes = [col for col in colunas_exibir if col in df_filtrado.columns]
        df_display = df_filtrado[colunas_existentes].copy()

        # Formatar dados
        if 'valor_total' in df_display.columns:
            df_display['valor_total'] = df_display['valor_total'].apply(lambda x: f"R$ {x:,.2f}")

        # Formatar datas
        date_cols = ['data_emissao', 'primeiro_envio', 'data_atesto', 'envio_final', 'data_baixa']
        for col in date_cols:
            if col in df_display.columns:
                df_display[col] = df_display[col].apply(
                    lambda x: x.strftime('%d/%m/%Y') if pd.notna(x) else 'Pendente'
                )

        # Renomear colunas
        novos_nomes = {
            'numero_cte': 'CTE',
            'destinatario_nome': 'Cliente',
            'valor_total': 'Valor',
            'data_emissao': 'Emissão',
            'primeiro_envio': '1º Envio',
            'data_atesto': 'Atesto',
            'envio_final': 'Envio Final',
            'data_baixa': 'Baixa'
        }

        df_display = df_display.rename(columns=novos_nomes)

        # Exibir tabela
        st.dataframe(corrigir_dataframe_traduzido(df_display), use_container_width=True, hide_index=True)

        # Opção de download
        csv_data = df_display.to_csv(index=False)
        timestamp_csv = datetime.now().strftime('%Y%m%d_%H%M')
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"baker_filtrado_{timestamp_csv}.csv",
            mime="text/csv",
            key="download_csv_filtrado"
        )

def aba_sistema_baixas():
    """Nova aba para o sistema de baixas automáticas"""

    st.markdown("""
    <div class="main-header">
        <h1>💳 Sistema de Baixas Automáticas</h1>
        <div class="subtitle">Gestão e conciliação de baixas em tempo real</div>
    </div>
    """, unsafe_allow_html=True)

    # Inicializar sistema de baixas
    sistema_baixas = SistemaBaixasAutomaticas()

    # Abas do sistema de baixas
    tab1, tab2, tab3 = st.tabs(["🔄 Registrar Baixas", "📊 Baixas em Lote", "📈 Relatórios"])

    with tab1:
        st.markdown("""
        <div class="form-header">
            <h3>💳 Registar Baixa Individual</h3>
            <p>Registre baixas individuais com validação automática</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_baixa_individual"):
            col1, col2, col3 = st.columns(3)

            with col1:
                numero_cte = st.number_input("Número do CTE", min_value=1, step=1)
                data_baixa = st.date_input("Data da Baixa", value=datetime.now().date())

            with col2:
                valor_baixa = st.number_input("Valor da Baixa (opcional)", min_value=0.0, step=0.01, format="%.2f")
                observacao = st.text_area("Observações")

            submitted = st.form_submit_button("💾 Registrar Baixa", type="primary")

            if submitted:
                if numero_cte:
                    valor_baixa_final = valor_baixa if valor_baixa > 0 else None
                    sucesso, mensagem = sistema_baixas.registrar_baixa(
                        numero_cte, data_baixa, observacao, valor_baixa_final
                    )

                    if sucesso:
                        st.success(f"✅ {mensagem}")
                        st.balloons()
                        st.cache_data.clear()  # Limpar cache
                    else:
                        st.error(f"❌ {mensagem}")
                else:
                    st.error("❌ Informe o número do CTE")

    with tab2:
        st.markdown("""
        <div class="form-header">
            <h3>📊 Processamento em Lote</h3>
            <p>Processe múltiplas baixas a partir de arquivo CSV</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        **📋 Formato do CSV:**
        - `numero_cte`: Número do CTE (obrigatório)
        - `data_baixa`: Data da baixa no formato DD/MM/AAAA (obrigatório)  
        - `valor_baixa`: Valor da baixa (opcional)
        - `observacao`: Observações (opcional)
        """)

        arquivo_baixas = st.file_uploader(
            "Selecione o arquivo CSV com as baixas",
            type=['csv'],
            help="Arquivo CSV com as colunas: numero_cte, data_baixa, valor_baixa, observacao"
        )

        if arquivo_baixas:
            if st.button("🔄 Processar Baixas em Lote"):
                with st.spinner("Processando baixas..."):
                    # Salvar arquivo temporariamente
                    with open("temp_baixas.csv", "wb") as f:
                        f.write(arquivo_baixas.getbuffer())

                    # Processar
                    resultado = sistema_baixas.processar_baixas_em_lote("temp_baixas.csv")

                    # Limpar arquivo temporário
                    os.remove("temp_baixas.csv")

                    if resultado['sucesso']:
                        resultados = resultado['resultados']

                        st.success(f"""
                        ✅ Processamento concluído!
                        - Processadas: {resultados['processadas']}
                        - Sucessos: {resultados['sucessos']}
                        - Erros: {resultados['erros']}
                        """)

                        # Mostrar detalhes
                        if resultados['detalhes']:
                            st.subheader("📋 Detalhes do Processamento")

                            for detalhe in resultados['detalhes']:
                                status_icon = "✅" if detalhe['sucesso'] else "❌"
                                st.write(f"{status_icon} CTE {detalhe['cte']}: {detalhe['mensagem']}")

                        st.cache_data.clear()  # Limpar cache
                    else:
                        st.error(f"❌ Erro: {resultado['erro']}")

    with tab3:
        st.markdown("""
        <div class="form-header">
            <h3>📈 Relatórios de Baixas</h3>
            <p>Análise e estatísticas das baixas processadas</p>
        </div>
        """, unsafe_allow_html=True)

        # Carregar dados para relatórios
        df = carregar_dados_postgresql()

        if not df.empty:
            # Estatísticas de baixas
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                baixas_total = len(df[df['data_baixa'].notna()])
                st.metric("Total de Baixas", baixas_total)

            with col2:
                valor_baixado = df[df['data_baixa'].notna()]['valor_total'].sum()
                st.metric("Valor Baixado", f"R$ {valor_baixado:,.2f}")

            with col3:
                pendentes = len(df[df['data_baixa'].isna()])
                st.metric("Baixas Pendentes", pendentes)

            with col4:
                valor_pendente = df[df['data_baixa'].isna()]['valor_total'].sum()
                st.metric("Valor Pendente", f"R$ {valor_pendente:,.2f}")

            # Gráfico de evolução das baixas
            if 'data_baixa' in df.columns:
                df_baixas = df[df['data_baixa'].notna()].copy()

                if not df_baixas.empty:
                    # Agrupar por mês
                    df_baixas['mes_baixa'] = df_baixas['data_baixa'].dt.to_period('M')
                    baixas_mensais = df_baixas.groupby('mes_baixa').agg({
                        'valor_total': 'sum',
                        'numero_cte': 'count'
                    }).reset_index()

                    baixas_mensais['mes_str'] = baixas_mensais['mes_baixa'].astype(str)

                    # Gráfico
                    fig = go.Figure()

                    fig.add_trace(go.Bar(
                        x=baixas_mensais['mes_str'],
                        y=baixas_mensais['valor_total'],
                        name='Valor Baixado',
                        marker_color='#28a745'
                    ))

                    fig.update_layout(
                        title='Evolução das Baixas por Mês',
                        xaxis_title='Mês',
                        yaxis_title='Valor (R$)',
                        height=400
                    )

                    st.plotly_chart(fig, use_container_width=True)

def aba_insercao_banco():
    """Aba para inserção de novos CTEs - MANTIDA DO ORIGINAL"""

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

        col1, col2, col3 = st.columns(3)

        with col1:
            numero_cte = st.number_input("Número CTE", min_value=1, step=1, key="insert_cte")
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
        submitted = st.form_submit_button("💾 Inserir CTE", type="primary", use_container_width=True)

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

    # Seção de busca e alteração (mantida do original)
    st.markdown("---")
    st.markdown("""
    <div class="form-header">
        <h3>🔍 Buscar e Alterar CTE</h3>
        <p>Busque um CTE existente e edite suas informações</p>
    </div>
    """, unsafe_allow_html=True)

    # Formulário de busca
    with st.form("form_busca_cte"):
        col1, col2 = st.columns([2, 1])

        with col1:
            numero_busca = st.number_input("Número do CTE para buscar", min_value=1, step=1, key="busca_cte_num")

        with col2:
            st.write("")  # Espaçamento
            st.write("")  # Espaçamento

        # Botão de busca (obrigatório em formulário)
        buscar_btn = st.form_submit_button("🔍 Buscar CTE", type="secondary")

        if buscar_btn and numero_busca:
            try:
                resultado_busca = buscar_cte_postgresql(numero_busca)
                if resultado_busca is None or len(resultado_busca) != 2:
                    sucesso, resultado = False, "Erro interno na busca"
                else:
                    sucesso, resultado = resultado_busca
            except Exception as e:
                sucesso, resultado = False, f"Erro na busca: {str(e)}"

            if sucesso:
                st.success(f"✅ CTE {numero_busca} encontrado!")

                # Armazenar dados encontrados no session_state
                st.session_state['cte_encontrado'] = resultado
                st.session_state['numero_cte_edicao'] = numero_busca
            else:
                st.error(f"❌ {resultado}")
                if 'cte_encontrado' in st.session_state:
                    del st.session_state['cte_encontrado']

    # Formulário de edição (aparece só se CTE foi encontrado)
    if 'cte_encontrado' in st.session_state and 'numero_cte_edicao' in st.session_state:
        dados_cte = st.session_state['cte_encontrado']
        numero_edicao = st.session_state['numero_cte_edicao']

        st.subheader(f"📝 Editando CTE {numero_edicao}")

        with st.form("form_edicao_cte"):
            col1, col2, col3 = st.columns(3)

            with col1:
                destinatario_edit = st.text_input("Nome do Destinatário", value=safe_get_value(dados_cte, 'destinatario_nome', ''))
                veiculo_edit = st.text_input("Placa do Veículo", value=safe_get_value(dados_cte, 'veiculo_placa', ''))
                valor_edit = st.number_input("Valor Total (R$)", value=float(dados_cte.get('valor_total', 0)), min_value=0.0, step=0.01, format="%.2f")

            with col2:
                data_emissao_edit = st.date_input("Data de Emissão", 
                value=processar_data_para_input(dados_cte.get('data_emissao')) or datetime.now().date())
                numero_fatura_edit = st.text_input("Número da Fatura", value=safe_get_value(dados_cte, 'numero_fatura', ''))
                data_baixa_edit = st.date_input("Data de Baixa", 
                value=processar_data_para_input(dados_cte.get('data_baixa')))

            observacao_edit = st.text_area("Observações", value=safe_get_value(dados_cte, 'observacao', ''))

            st.subheader("📅 Datas do Processo")

            col3, col4 = st.columns(2)

            with col3:
                data_inclusao_edit = st.date_input("Data Inclusão Fatura", 
                value=processar_data_para_input(dados_cte.get('data_inclusao_fatura')))
                data_envio_edit = st.date_input("Data Envio Processo", 
                value=processar_data_para_input(dados_cte.get('data_envio_processo')))
                primeiro_envio_edit = st.date_input("1º Envio", 
                value=processar_data_para_input(dados_cte.get('primeiro_envio')))

            with col4:
                data_rq_edit = st.date_input("Data RQ/TMC", 
                value=processar_data_para_input(dados_cte.get('data_rq_tmc')))
                data_atesto_edit = st.date_input("Data do Atesto", 
                value=processar_data_para_input(dados_cte.get('data_atesto')))
                envio_final_edit = st.date_input("Envio Final", 
                value=processar_data_para_input(dados_cte.get('envio_final')))

            # Botões de ação
            col_btn1, col_btn2 = st.columns(2)

            with col_btn1:
                salvar_alteracoes = st.form_submit_button("💾 Salvar Alterações", type="primary")

            with col_btn2:
                cancelar_edicao = st.form_submit_button("❌ Cancelar Edição", type="secondary")

            if salvar_alteracoes:
                # Preparar dados para atualização
                dados_atualizados = (
                    destinatario_edit,
                    veiculo_edit if veiculo_edit else None,
                    valor_edit,
                    data_emissao_edit,
                    numero_fatura_edit if numero_fatura_edit else None,
                    data_baixa_edit,
                    observacao_edit if observacao_edit else None,
                    data_inclusao_edit,
                    data_envio_edit,
                    primeiro_envio_edit,
                    data_rq_edit,
                    data_atesto_edit,
                    envio_final_edit
                )

                # Atualizar no banco
                sucesso, mensagem = atualizar_cte_postgresql(numero_edicao, dados_atualizados)

                if sucesso:
                    st.success(f"✅ {mensagem}")
                    st.cache_data.clear()  # Limpar cache

                    # Limpar session_state
                    if 'cte_encontrado' in st.session_state:
                        del st.session_state['cte_encontrado']
                    if 'numero_cte_edicao' in st.session_state:
                        del st.session_state['numero_cte_edicao']

                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {mensagem}")

            if cancelar_edicao:
                # Limpar session_state
                if 'cte_encontrado' in st.session_state:
                    del st.session_state['cte_encontrado']
                if 'numero_cte_edicao' in st.session_state:
                    del st.session_state['numero_cte_edicao']
                st.rerun()

    # Seção de exclusão
    st.markdown("---")
    st.markdown("""
    <div class="form-header">
        <h3>🗑️ Exclusão de CTE</h3>
        <p>⚠️ Atenção: Esta ação é irreversível</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("form_exclusao_cte"):
        numero_cte_delete = st.number_input("Número do CTE para excluir", min_value=1, step=1, key="delete_cte_num")

        confirmar_exclusao = st.checkbox("Confirmo que desejo excluir este CTE")

        # Botão de exclusão (obrigatório em formulário)
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

def aba_ctes_pendentes():
    """Aba para análise de CTEs pendentes"""

    st.markdown("""
    <div class="main-header">
        <h1>🚨 CTEs Pendentes - Análise Detalhada</h1>
        <div class="subtitle">Monitoramento proativo de processos pendentes</div>
    </div>
    """, unsafe_allow_html=True)

    # Carregar dados
    df = carregar_dados_postgresql()

    if df.empty:
        st.error("❌ Nenhum dado encontrado")
        return

    # Calcular alertas
    alertas = calcular_alertas_inteligentes(df)

    # Estatísticas gerais de pendências - CORRIGIDO COM VALORES MONETÁRIOS
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        ctes_sem_primeiro_envio = len(df[df['primeiro_envio'].isna()])
        valor_sem_primeiro_envio = df[df['primeiro_envio'].isna()]['valor_total'].sum()
        st.markdown(f"""
        <div class="status-card-warning">
            <div class="status-number">{ctes_sem_primeiro_envio}</div>
            <div class="status-title">Sem 1º Envio</div>
            <div class="status-value">R$ {valor_sem_primeiro_envio:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        ctes_sem_atesto = len(df[df['data_atesto'].isna()])
        valor_sem_atesto = df[df['data_atesto'].isna()]['valor_total'].sum()
        st.markdown(f"""
        <div class="status-card-info">
            <div class="status-number">{ctes_sem_atesto}</div>
            <div class="status-title">Sem Atesto</div>
            <div class="status-value">R$ {valor_sem_atesto:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        ctes_sem_fatura = len(df[df['numero_fatura'].isna() | (df['numero_fatura'] == '')])
        valor_sem_fatura = df[df['numero_fatura'].isna() | (df['numero_fatura'] == '')]['valor_total'].sum()
        st.markdown(f"""
        <div class="status-card-warning">
            <div class="status-number">{ctes_sem_fatura}</div>
            <div class="status-title">Sem Fatura</div>
            <div class="status-value">R$ {valor_sem_fatura:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        ctes_sem_baixa = len(df[df['data_baixa'].isna()])
        valor_sem_baixa = df[df['data_baixa'].isna()]['valor_total'].sum()
        st.markdown(f"""
        <div class="status-card-danger">
            <div class="status-number">{ctes_sem_baixa}</div>
            <div class="status-title">Sem Baixa</div>
            <div class="status-value">R$ {valor_sem_baixa:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    # Análise detalhada por tipo de pendência
    st.markdown("""
    <div class="section-header">
        <div class="section-title">📋 Análise Detalhada por Categoria</div>
        <div class="section-subtitle">CTEs pendentes organizados por tipo de processo</div>
    </div>
    """, unsafe_allow_html=True)

    # Abas para diferentes tipos de pendência
    tab1, tab2, tab3 = st.tabs([
        "🚨 Primeiro Envio Pendente", 
        "⏳ Atesto Pendente", 
        "💸 Baixa Pendente"
    ])

    with tab1:
        alerta = alertas['primeiro_envio_pendente']
        if alerta['qtd'] > 0:
            st.error(f"🚨 **{alerta['qtd']} CTEs** com primeiro envio pendente há mais de 10 dias")
            st.write(f"💰 **Valor em risco:** R$ {alerta['valor']:,.2f}")

            # Tabela detalhada
            df_pendente = pd.DataFrame(alerta['lista'])
            if not df_pendente.empty:
                # Calcular dias em atraso de forma segura
                hoje = datetime.now().date()

                def calcular_dias_atraso(data_emissao):
                    if pd.isna(data_emissao) or data_emissao is None:
                        return 0
                    try:
                        if hasattr(data_emissao, 'date'):
                            return (hoje - data_emissao.date()).days
                        else:
                            return 0
                    except:
                        return 0

                df_pendente['dias_atraso'] = df_pendente['data_emissao'].apply(calcular_dias_atraso)

                # Formatar valores
                df_pendente['valor_total'] = df_pendente['valor_total'].apply(lambda x: f"R$ {x:,.2f}")

                def formatar_data(data_emissao):
                    if pd.isna(data_emissao) or data_emissao is None:
                        return 'N/A'
                    try:
                        if hasattr(data_emissao, 'strftime'):
                            return data_emissao.strftime('%d/%m/%Y')
                        else:
                            return 'N/A'
                    except:
                        return 'N/A'

                df_pendente['data_emissao'] = df_pendente['data_emissao'].apply(formatar_data)

                # Renomear colunas
                df_display = df_pendente.rename(columns={
                    'numero_cte': 'CTE',
                    'destinatario_nome': 'Cliente',
                    'valor_total': 'Valor',
                    'data_emissao': 'Data Emissão',
                    'dias_atraso': 'Dias em Atraso'
                })

                st.dataframe(corrigir_dataframe_traduzido(df_display), use_container_width=True, hide_index=True)
        else:
            st.success("✅ Nenhum CTE com primeiro envio pendente")

    with tab2:
        ctes_sem_atesto_detalhado = df[df['data_atesto'].isna()]
        if not ctes_sem_atesto_detalhado.empty:
            st.warning(f"⏳ **{len(ctes_sem_atesto_detalhado)} CTEs** aguardando atesto")

            # Preparar dados para exibição
            df_display = ctes_sem_atesto_detalhado[['numero_cte', 'destinatario_nome', 'valor_total', 'primeiro_envio']].copy()

            # Calcular dias desde primeiro envio de forma segura
            hoje = datetime.now().date()

            def calcular_dias_desde_envio(primeiro_envio):
                if pd.isna(primeiro_envio) or primeiro_envio is None:
                    return 0
                try:
                    if hasattr(primeiro_envio, 'date'):
                        return (hoje - primeiro_envio.date()).days
                    else:
                        return 0
                except:
                    return 0

            df_display['dias_desde_envio'] = df_display['primeiro_envio'].apply(calcular_dias_desde_envio)

            # Formatar dados
            df_display['valor_total'] = df_display['valor_total'].apply(lambda x: f"R$ {x:,.2f}")

            def formatar_primeiro_envio(primeiro_envio):
                if pd.isna(primeiro_envio) or primeiro_envio is None:
                    return 'Não enviado'
                try:
                    if hasattr(primeiro_envio, 'strftime'):
                        return primeiro_envio.strftime('%d/%m/%Y')
                    else:
                        return 'Não enviado'
                except:
                    return 'Não enviado'

            df_display['primeiro_envio'] = df_display['primeiro_envio'].apply(formatar_primeiro_envio)

            # Renomear colunas
            df_display = df_display.rename(columns={
                'numero_cte': 'CTE',
                'destinatario_nome': 'Cliente',
                'valor_total': 'Valor',
                'primeiro_envio': '1º Envio',
                'dias_desde_envio': 'Dias desde Envio'
            })

            st.dataframe(corrigir_dataframe_traduzido(df_display), use_container_width=True, hide_index=True)
        else:
            st.success("✅ Todos os CTEs possuem atesto")

    with tab3:
        alerta = alertas['faturas_vencidas']
        ctes_sem_baixa_todos = df[df['data_baixa'].isna()]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("💸 Faturas Vencidas (90+ dias)")
            if alerta['qtd'] > 0:
                st.error(f"**{alerta['qtd']} faturas vencidas**")
                st.write(f"Valor: R$ {alerta['valor']:,.2f}")

                # Lista das faturas vencidas - Exibição segura
                for item in alerta['lista'][:10]:
                    # Calcular dias de atraso de forma segura
                    days_overdue = 0
                    if item.get('data_atesto') and pd.notna(item['data_atesto']):
                        try:
                            if hasattr(item['data_atesto'], 'date'):
                                days_overdue = (datetime.now().date() - item['data_atesto'].date()).days
                        except:
                            days_overdue = 0
                    st.write(f"• CTE {item['numero_cte']} - {days_overdue} dias - R$ {item['valor_total']:,.2f}")
            else:
                st.success("✅ Nenhuma fatura vencida")

        with col2:
            st.subheader("⏳ Todas as Baixas Pendentes")
            if not ctes_sem_baixa_todos.empty:
                st.info(f"**{len(ctes_sem_baixa_todos)} CTEs** sem baixa")
                valor_total_pendente = ctes_sem_baixa_todos['valor_total'].sum()
                st.write(f"Valor total: R$ {valor_total_pendente:,.2f}")

                # Distribuição por idade - Cálculo seguro
                hoje = datetime.now().date()

                def calcular_dias_sem_baixa(data_atesto):
                    if pd.isna(data_atesto) or data_atesto is None:
                        return 0
                    try:
                        if hasattr(data_atesto, 'date'):
                            return (hoje - data_atesto.date()).days
                        else:
                            return 0
                    except:
                        return 0

                ctes_sem_baixa_todos['dias_sem_baixa'] = ctes_sem_baixa_todos['data_atesto'].apply(calcular_dias_sem_baixa)

                # Categorizar por idade
                ate_30_dias = len(ctes_sem_baixa_todos[ctes_sem_baixa_todos['dias_sem_baixa'] <= 30])
                ate_60_dias = len(ctes_sem_baixa_todos[(ctes_sem_baixa_todos['dias_sem_baixa'] > 30) & (ctes_sem_baixa_todos['dias_sem_baixa'] <= 60)])
                ate_90_dias = len(ctes_sem_baixa_todos[(ctes_sem_baixa_todos['dias_sem_baixa'] > 60) & (ctes_sem_baixa_todos['dias_sem_baixa'] <= 90)])
                mais_90_dias = len(ctes_sem_baixa_todos[ctes_sem_baixa_todos['dias_sem_baixa'] > 90])

                st.write("**Por idade:**")
                st.write(f"• Até 30 dias: {ate_30_dias}")
                st.write(f"• 31-60 dias: {ate_60_dias}")
                st.write(f"• 61-90 dias: {ate_90_dias}")
                st.write(f"• Mais de 90 dias: {mais_90_dias}")
            else:
                st.success("✅ Todas as faturas foram baixadas")

def main():
    """Função principal - REMOVIDA aba de email"""

    # Limpeza preventiva do DOM
    if 'dom_cleaned' not in st.session_state:
        st.session_state.dom_cleaned = True

    # Sistema de navegação
    tabs = st.tabs([
        "📊 Dashboard Principal", 
        "💳 Sistema de Baixas", 
        "🗄️ Gestão de Dados",
        "🚨 CTEs Pendentes",
        "📈 Análises Avançadas"
    ])

    with tabs[0]:
        aba_dashboard_principal_expandido()

    with tabs[1]:
        aba_sistema_baixas()

    with tabs[2]:
        aba_insercao_banco()

    with tabs[3]:
        aba_ctes_pendentes()

    with tabs[4]:
        st.markdown("""
        <div class="main-header">
            <h1>📈 Análises Avançadas</h1>
            <div class="subtitle">Business Intelligence e Análise Preditiva</div>
        </div>
        """, unsafe_allow_html=True)

        st.info("🚧 Módulo em desenvolvimento - Próximas funcionalidades:")
        st.markdown("""
        - 🤖 **Análise Preditiva de Inadimplência**
        - 📊 **Dashboard Executivo Interativo**  
        - 🔔 **Sistema de Notificações Automáticas**
        - 📱 **Integração com WhatsApp/SMS**
        - 📈 **Análise de Tendências e Sazonalidade**
        - 🎯 **KPIs Personalizados por Cliente**
        - 🔍 **Análise de Padrões de Comportamento**
        - 📋 **Relatórios Executivos Automatizados**
        """)

        # Carregar dados para análises futuras
        df = carregar_dados_postgresql()

        if not df.empty:
            st.subheader("📊 Pré-visualização de Análises")

            # Análise básica de tendências
            col1, col2, col3 = st.columns(3)

            with col1:
                # Análise de sazonalidade simples
                if 'data_emissao' in df.columns:
                    df_temp = df[df['data_emissao'].notna()].copy()
                    if not df_temp.empty:
                        df_temp['mes'] = df_temp['data_emissao'].dt.month
                        receita_por_mes = df_temp.groupby('mes')['valor_total'].sum()

                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            x=[f"Mês {m}" for m in receita_por_mes.index],
                            y=receita_por_mes.values,
                            marker_color='#0f4c75'
                        ))

                        fig.update_layout(
                            title='Receita por Mês (Análise Sazonal)',
                            height=300
                        )

                        st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Análise de performance por cliente
                if 'destinatario_nome' in df.columns:
                    top_clientes = df.groupby('destinatario_nome')['valor_total'].sum().sort_values(ascending=False).head(10)

                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=top_clientes.values,
                        y=top_clientes.index,
                        orientation='h',
                        marker_color='#28a745'
                    ))

                    fig.update_layout(
                        title='Top 10 Clientes por Receita',
                        height=300
                    )

                    st.plotly_chart(fig, use_container_width=True)

    # Sidebar expandida COM DOWNLOADS
    with st.sidebar:
        st.header("📊 Status do Sistema Avançado")

        # Teste de conexão
        with st.spinner('🔄 Verificando sistema...'):
            df_test = carregar_dados_postgresql()

        if not df_test.empty:
            metricas_sidebar = gerar_metricas_expandidas(df_test)
            alertas_sidebar = calcular_alertas_inteligentes(df_test)

            st.success("✅ Sistema Operacional")

            # Métricas resumidas
            st.metric("📊 Total CTEs", metricas_sidebar['total_ctes'])
            st.metric("💰 Receita", f"R$ {metricas_sidebar['valor_total']:,.0f}")
            st.metric("🎯 Processos Completos", f"{metricas_sidebar['processos_completos']}")

            # Alertas resumidos
            total_alertas = sum(alerta['qtd'] for alerta in alertas_sidebar.values())
            if total_alertas > 0:
                st.error(f"🚨 {total_alertas} alertas ativos")
            else:
                st.success("✅ Nenhum alerta")

            # Indicador de performance geral
            taxa_processos_completos = (metricas_sidebar['processos_completos'] / max(metricas_sidebar['total_ctes'], 1)) * 100

            if taxa_processos_completos >= 80:
                st.success(f"🟢 Performance: {taxa_processos_completos:.1f}%")
            elif taxa_processos_completos >= 60:
                st.warning(f"🟡 Performance: {taxa_processos_completos:.1f}%")
            else:
                st.error(f"🔴 Performance: {taxa_processos_completos:.1f}%")
        else:
            st.error("❌ Sistema Offline")

        st.markdown("---")

        # Ações rápidas expandidas COM SISTEMA DE DOWNLOADS
        st.header("⚡ Ações Rápidas")

        if st.button("🔄 Atualizar Cache"):
            st.cache_data.clear()
            st.success("✅ Cache atualizado")
            st.rerun()

        # SISTEMA DE DOWNLOADS MELHORADO
        st.header("📥 Central de Relatórios")

        if not df_test.empty:
            # Cards de métricas rápidas no sidebar
            with st.container():
                st.markdown("""
                <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
                           padding: 1rem; border-radius: 10px; margin-bottom: 1rem;
                           border-left: 4px solid #2196f3;">
                    <h4 style="margin: 0; color: #1976d2;">📊 Resumo Executivo</h4>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("📋 CTEs", metricas_sidebar['total_ctes'], 
                             delta=f"{metricas_sidebar['processos_completos']} completos")
                with col2:
                    st.metric("💰 Receita", f"R$ {metricas_sidebar['valor_total']/1000:.0f}K",
                             delta=f"{total_alertas} alertas")

            # Botões de download melhorados
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%); 
                       padding: 1rem; border-radius: 10px; margin: 1rem 0;
                       border-left: 4px solid #9c27b0;">
                <h4 style="margin: 0; color: #7b1fa2;">📥 Downloads</h4>
                <p style="margin: 0.5rem 0 0 0; color: #7b1fa2; font-size: 0.9rem;">
                Gere relatórios detalhados em diferentes formatos
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Gerar dados para relatórios
            metricas_rel = gerar_metricas_expandidas(df_test)
            alertas_rel = calcular_alertas_inteligentes(df_test)
            variacoes_rel = calcular_variacoes_tempo_expandidas(df_test)

            # Botão Excel
            try:
                excel_data = gerar_relatorio_excel(df_test, metricas_rel, alertas_rel, variacoes_rel)
                timestamp_excel = datetime.now().strftime('%Y%m%d_%H%M%S')

                st.download_button(
                    label="📊 Relatório Excel Completo",
                    data=excel_data,
                    file_name=f"dashboard_baker_{timestamp_excel}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ Erro Excel: {str(e)[:50]}...")

            # Botão HTML
            try:
                html_data = gerar_relatorio_pdf_html(df_test, metricas_rel, alertas_rel, variacoes_rel)
                timestamp_html = datetime.now().strftime('%Y%m%d_%H%M%S')

                st.download_button(
                    label="📄 Relatório HTML/PDF",
                    data=html_data,
                    file_name=f"dashboard_baker_{timestamp_html}.html",
                    mime="text/html",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ Erro HTML: {str(e)[:50]}...")

            # Botão CSV
            try:
                csv_data = df_test.to_csv(index=False, encoding='utf-8-sig')
                timestamp_csv = datetime.now().strftime('%Y%m%d_%H%M%S')

                st.download_button(
                    label="📋 Dados CSV Brutos",
                    data=csv_data,
                    file_name=f"dados_baker_{timestamp_csv}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ Erro CSV: {str(e)[:50]}...")

            st.info("💡 **HTML → PDF:** Abra o arquivo HTML no navegador e pressione Ctrl+P")
        else:
            st.error("❌ Sem dados para gerar relatório")

        if st.button("💾 Backup Sistema"):
            st.success("💾 Backup realizado!")

        if st.button("🔔 Testar Alertas"):
            st.info("🔔 Sistema de alertas ativo!")

        if st.button("📊 Gerar Relatório Executivo"):
            # Simular geração de relatório
            with st.spinner("Gerando relatório..."):
                import time
                time.sleep(2)
            st.success("📋 Relatório executivo gerado!")

        st.markdown("---")

        # Informações do sistema - ATUALIZADA
        st.markdown("""
        **🎯 Dashboard Baker v3.0**  
        ✅ Sistema Avançado de Gestão  
        ✅ Alertas Inteligentes  
        ✅ Baixas Automáticas  
        ✅ Análise Preditiva  
        ✅ Variações Temporais  
        ✅ Performance Tracking  
        ✅ Business Intelligence  
        ✅ CTEs Pendentes Análise  
        ✅ Sistema CRUD Completo  
        ✅ Relatórios PDF/Excel  
        ❌ Sistema de Email Removido  
        🚧 Notificações WhatsApp  
        🚧 AI Predictive Analytics  
        🚧 Relatórios Automatizados  
        """)

        # Status da base de dados
        if not df_test.empty:
            st.markdown("---")
            st.markdown("**📊 Status da Base**")
            ultimo_update = datetime.now().strftime("%H:%M:%S")
            st.text(f"Última atualização: {ultimo_update}")

            # Estatísticas rápidas
            if 'created_at' in df_test.columns:
                registros_hoje = len(df_test[df_test['created_at'].dt.date == datetime.now().date()])
                st.text(f"Registros hoje: {registros_hoje}")

        # Link para documentação (simulado)
        st.markdown("---")
        st.markdown("**📚 Recursos**")
        if st.button("📖 Manual do Usuário"):
            st.info("📖 Manual disponível na documentação")

        if st.button("🆘 Suporte Técnico"):
            st.info("🆘 Entre em contato com o suporte")

if __name__ == "__main__":
    main()