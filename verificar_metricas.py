#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificação das métricas do dashboard
Testa se os dados estão corretos no PostgreSQL
"""

import psycopg2
import pandas as pd
import os
from datetime import datetime

def carregar_configuracao_banco():
    """Carrega configuração do banco"""
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

def verificar_metricas():
    """Verifica e mostra as métricas que serão exibidas no dashboard"""
    
    print("🔍 VERIFICAÇÃO DAS MÉTRICAS DO DASHBOARD")
    print("=" * 50)
    
    try:
        # Conectar ao banco
        config = carregar_configuracao_banco()
        print(f"🔗 Conectando a: {config['host']}:{config['port']}/{config['database']}")
        
        conn = psycopg2.connect(**config)
        print("✅ Conexão PostgreSQL estabelecida")
        
        # Carregar dados
        query = """
        SELECT 
            numero_cte,
            destinatario_nome,
            valor_total,
            data_emissao,
            data_baixa,
            origem_dados
        FROM dashboard_baker 
        ORDER BY numero_cte DESC;
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            print("❌ NENHUM DADO ENCONTRADO NO BANCO!")
            print("💡 Execute: python popular_banco_com_mapeamento.py")
            return
        
        print(f"📊 Total de registros: {len(df)}")
        print()
        
        # Métricas principais
        print("📈 MÉTRICAS PRINCIPAIS:")
        print("-" * 30)
        
        # 1. Total de CTEs
        total_ctes = len(df)
        print(f"🔢 Total de CTEs: {total_ctes:,}")
        
        # 2. Clientes únicos
        clientes_unicos = df['destinatario_nome'].nunique()
        print(f"👥 Clientes únicos: {clientes_unicos:,}")
        
        # 3. Valor total
        valor_total = df['valor_total'].sum()
        print(f"💰 Valor total: R$ {valor_total:,.2f}")
        
        # 4. Faturas pagas vs pendentes
        faturas_pagas = len(df[df['data_baixa'].notna()])
        faturas_pendentes = len(df[df['data_baixa'].isna()])
        
        print(f"✅ Faturas pagas: {faturas_pagas:,}")
        print(f"⏳ Faturas pendentes: {faturas_pendentes:,}")
        
        # 5. Valores pagos vs pendentes
        valor_pago = df[df['data_baixa'].notna()]['valor_total'].sum()
        valor_pendente = df[df['data_baixa'].isna()]['valor_total'].sum()
        
        print(f"💚 Valor pago: R$ {valor_pago:,.2f}")
        print(f"🟡 Valor pendente: R$ {valor_pendente:,.2f}")
        
        print()
        
        # Top 5 clientes
        print("🏆 TOP 5 CLIENTES POR VALOR:")
        print("-" * 35)
        
        top_clientes = df.groupby('destinatario_nome')['valor_total'].sum().nlargest(5)
        
        for i, (cliente, valor) in enumerate(top_clientes.items(), 1):
            cliente_resumido = cliente[:30] + "..." if len(cliente) > 30 else cliente
            print(f"{i:2d}. {cliente_resumido}: R$ {valor:,.2f}")
        
        print()
        
        # Amostra dos dados
        print("📋 AMOSTRA DOS DADOS (5 mais recentes):")
        print("-" * 45)
        
        amostra = df.head(5)
        
        for i, (_, row) in enumerate(amostra.iterrows(), 1):
            cte = row['numero_cte']
            cliente = row['destinatario_nome'][:25] + "..." if len(str(row['destinatario_nome'])) > 25 else row['destinatario_nome']
            valor = row['valor_total']
            status = "💚 Pago" if pd.notna(row['data_baixa']) else "🟡 Pendente"
            
            print(f"{i}. CTE {cte}: {cliente}")
            print(f"   Valor: R$ {valor:,.2f} | Status: {status}")
        
        print()
        
        # Status geral
        print("🎯 STATUS PARA O DASHBOARD:")
        print("-" * 35)
        
        if total_ctes > 0:
            print("✅ Dados suficientes para gerar métricas")
            print("✅ Cards de resumo executivo serão exibidos")
            
            if clientes_unicos > 1:
                print("✅ Gráfico de top clientes será gerado")
            else:
                print("⚠️ Apenas 1 cliente - gráfico será simples")
            
            if df['data_emissao'].notna().sum() > 0:
                print("✅ Gráfico de receitas por semana será gerado")
            else:
                print("⚠️ Sem datas de emissão - gráfico temporal limitado")
            
            taxa_pagamento = (faturas_pagas / total_ctes) * 100
            print(f"📊 Taxa de pagamento: {taxa_pagamento:.1f}%")
            
            if taxa_pagamento > 50:
                print("✅ Boa taxa de pagamento para análises")
            else:
                print("⚠️ Taxa de pagamento baixa")
        
        else:
            print("❌ Dados insuficientes para dashboard")
        
        print()
        print("🚀 COMANDO PARA EXECUTAR DASHBOARD:")
        print("   executar_dashboard_metricas.bat")
        print("   OU")
        print("   streamlit run dashboard_com_metricas_postgresql.py")
        
    except psycopg2.Error as e:
        print(f"❌ Erro PostgreSQL: {e}")
        print("💡 Verifique se o PostgreSQL está rodando")
        print("💡 Confirme as credenciais no arquivo .env")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    verificar_metricas()