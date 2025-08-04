#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuração centralizada para o banco PostgreSQL
Dashboard Baker - Sistema Transpontual
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class DatabaseConfig:
    """Configuração do banco de dados"""
    host: str = 'localhost'
    database: str = 'dashboard_baker'
    user: str = 'postgres'
    password: str = 'senha123'  # Altere conforme necessário
    port: int = 5432
    
    def to_dict(self):
        """Converte para dicionário para uso com psycopg2"""
        return {
            'host': self.host,
            'database': self.database,
            'user': self.user,
            'password': self.password,
            'port': self.port
        }
    
    def connection_string(self):
        """Gera string de conexão PostgreSQL"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @classmethod
    def from_env(cls):
        """Carrega configuração de variáveis de ambiente"""
        return cls(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'dashboard_baker'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'senha123'),
            port=int(os.getenv('DB_PORT', 5432))
        )

# Configuração padrão
DEFAULT_CONFIG = DatabaseConfig()

# Configurações alternativas para diferentes ambientes
CONFIGS = {
    'development': DatabaseConfig(
        host='localhost',
        database='dashboard_baker_dev',
        user='postgres',
        password='senha123',
        port=5432
    ),
    
    'production': DatabaseConfig(
        host='localhost',  # Altere para seu servidor de produção
        database='dashboard_baker_prod',
        user='baker_user',
        password='sua_senha_segura_aqui',
        port=5432
    ),
    
    'test': DatabaseConfig(
        host='localhost',
        database='dashboard_baker_test',
        user='postgres',
        password='senha123',
        port=5432
    )
}

def get_config(environment: str = 'development') -> DatabaseConfig:
    """
    Obtém configuração para um ambiente específico
    
    Args:
        environment: Ambiente desejado ('development', 'production', 'test')
    
    Returns:
        DatabaseConfig: Configuração do banco para o ambiente
    """
    if environment in CONFIGS:
        return CONFIGS[environment]
    
    # Se não encontrar, tentar carregar de variáveis de ambiente
    env_config = DatabaseConfig.from_env()
    
    # Se variáveis de ambiente não estiverem definidas, usar padrão
    if env_config.password == 'senha123' and environment != 'development':
        print(f"⚠️ Aviso: Usando configuração padrão para ambiente '{environment}'")
        print("   Considere definir variáveis de ambiente ou configurar CONFIGS")
    
    return env_config

# Configurações específicas do Dashboard Baker
class DashboardConfig:
    """Configurações específicas do dashboard"""
    
    # Tabelas do sistema
    TABELA_PRINCIPAL = 'dashboard_baker'
    
    # Campos obrigatórios
    CAMPOS_OBRIGATORIOS = [
        'numero_cte',
        'destinatario_nome',
        'valor_total',
        'data_emissao'
    ]
    
    # Mapeamento de colunas CSV para banco
    MAPEAMENTO_CSV = {
        'Número Cte': 'numero_cte',
        'Destinatário - Nome': 'destinatario_nome',
        'Veículo - Placa': 'veiculo_placa',
        'Data emissão Cte': 'data_emissao',
        'Fatura': 'numero_fatura',
        'Data baixa': 'data_baixa',
        'OBSERVAÇÃO': 'observacao',
        'Data INCLUSÃO Fatura Bsoft': 'data_inclusao_fatura',
        'Data Envio do processo Faturamento': 'data_envio_processo',
        '1º Envio': 'primeiro_envio',
        'Data RQ/TMC': 'data_rq_tmc',
        'Data do atesto': 'data_atesto',
        'Envio final': 'envio_final'
    }
    
    # Formatos de data suportados
    FORMATOS_DATA = [
        '%d/%b/%y',  # 25/jul/24
        '%d/%m/%Y',  # 25/07/2024
        '%Y-%m-%d',  # 2024-07-25
        '%d-%m-%Y'   # 25-07-2024
    ]
    
    # Encodings para CSV
    ENCODINGS_CSV = ['cp1252', 'utf-8', 'latin1', 'iso-8859-1']
    
    # Separadores de CSV
    SEPARADORES_CSV = [';', ',', '\t']

if __name__ == "__main__":
    # Teste das configurações
    print("🧪 TESTE DAS CONFIGURAÇÕES")
    print("=" * 40)
    
    # Testar configuração padrão
    config_dev = get_config('development')
    print(f"🔧 Desenvolvimento:")
    print(f"   Host: {config_dev.host}")
    print(f"   Database: {config_dev.database}")
    print(f"   User: {config_dev.user}")
    print(f"   Connection String: {config_dev.connection_string()}")
    
    print()
    
    # Testar configuração de produção
    config_prod = get_config('production')
    print(f"🚀 Produção:")
    print(f"   Host: {config_prod.host}")
    print(f"   Database: {config_prod.database}")
    print(f"   User: {config_prod.user}")
    
    print()
    
    # Testar configuração de variáveis de ambiente
    print("🌍 Variáveis de Ambiente:")
    env_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_PORT']
    for var in env_vars:
        value = os.getenv(var, 'NÃO DEFINIDA')
        print(f"   {var}: {value}")
    
    print()
    
    # Testar configurações do dashboard
    print("📊 Configurações do Dashboard:")
    print(f"   Tabela principal: {DashboardConfig.TABELA_PRINCIPAL}")
    print(f"   Campos obrigatórios: {len(DashboardConfig.CAMPOS_OBRIGATORIOS)}")
    print(f"   Mapeamento CSV: {len(DashboardConfig.MAPEAMENTO_CSV)} campos")
    print(f"   Formatos de data: {len(DashboardConfig.FORMATOS_DATA)}")
    print(f"   Encodings suportados: {len(DashboardConfig.ENCODINGS_CSV)}")