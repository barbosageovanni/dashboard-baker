#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Avançado de Variações Temporais - Dashboard Baker
Análise completa de produtividade e performance temporal
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

class AnaliseVariacoesTempo:
    """
    Sistema completo de análise de variações temporais
    Calcula e atualiza automaticamente as colunas de diferenças
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.variacoes_config = self._get_config_variacoes()
        self.metas_produtividade = self._get_metas_produtividade()
    
    def _get_config_variacoes(self) -> List[Dict]:
        """Configuração completa das variações temporais"""
        return [
            {
                'nome': 'CTE → Inclusão Fatura',
                'campo_inicio': 'data_emissao',
                'campo_fim': 'data_inclusao_fatura',
                'coluna_resultado': 'dias_cte_inclusao_fatura',
                'meta_dias': 2,
                'codigo': 'cte_inclusao_fatura',
                'categoria': 'processo_interno',
                'descricao': 'Tempo para incluir fatura após emissão do CTE',
                'impacto': 'Processo interno - Agilidade do faturamento'
            },
            {
                'nome': 'CTE → Envio Processo',
                'campo_inicio': 'data_emissao',
                'campo_fim': 'data_envio_processo',
                'coluna_resultado': 'dias_cte_envio_processo',
                'meta_dias': 3,
                'codigo': 'cte_envio_processo',
                'categoria': 'processo_interno',
                'descricao': 'Tempo para enviar processo após emissão',
                'impacto': 'Processo interno - Eficiência operacional'
            },
            {
                'nome': 'Inclusão → Envio Processo',
                'campo_inicio': 'data_inclusao_fatura',
                'campo_fim': 'data_envio_processo',
                'coluna_resultado': 'dias_inclusao_envio_processo',
                'meta_dias': 1,
                'codigo': 'inclusao_envio_processo',
                'categoria': 'processo_interno',
                'descricao': 'Tempo entre inclusão da fatura e envio',
                'impacto': 'Processo interno - Fluxo de trabalho'
            },
            {
                'nome': 'Inclusão → 1º Envio',
                'campo_inicio': 'data_inclusao_fatura',
                'campo_fim': 'primeiro_envio',
                'coluna_resultado': 'dias_inclusao_primeiro_envio',
                'meta_dias': 1,
                'codigo': 'inclusao_primeiro_envio',
                'categoria': 'processo_interno',
                'descricao': 'Tempo para primeiro envio após inclusão',
                'impacto': 'Processo interno - Velocidade de resposta'
            },
            {
                'nome': 'RQ/TMC → 1º Envio',
                'campo_inicio': 'data_rq_tmc',
                'campo_fim': 'primeiro_envio',
                'coluna_resultado': 'Dias Data RQ/TMC vs  1º Envio',  # Coluna existente
                'meta_dias': 3,
                'codigo': 'rq_tmc_primeiro_envio',
                'categoria': 'processo_cliente',
                'descricao': 'Tempo entre RQ/TMC e primeiro envio',
                'impacto': 'Processo com cliente - Tempo de resposta'
            },
            {
                'nome': '1º Envio → Atesto',
                'campo_inicio': 'primeiro_envio',
                'campo_fim': 'data_atesto',
                'coluna_resultado': 'Dias do 1º Envio vs Atesto',  # Coluna existente
                'meta_dias': 7,
                'codigo': 'primeiro_envio_atesto',
                'categoria': 'processo_cliente',
                'descricao': 'Tempo para cliente atestar documentos',
                'impacto': 'Processo com cliente - Dependente do cliente'
            },
            {
                'nome': 'Atesto → Envio Final',
                'campo_inicio': 'data_atesto',
                'campo_fim': 'envio_final',
                'coluna_resultado': 'Dias do Envio Final vs Atesto',  # Coluna existente
                'meta_dias': 2,
                'codigo': 'atesto_envio_final',
                'categoria': 'processo_interno',
                'descricao': 'Tempo para envio final após atesto',
                'impacto': 'Processo interno - Finalização'
            },
            {
                'nome': 'Processo Completo (CTE → Envio Final)',
                'campo_inicio': 'data_emissao',
                'campo_fim': 'envio_final',
                'coluna_resultado': 'dias_processo_completo',
                'meta_dias': 15,
                'codigo': 'processo_completo',
                'categoria': 'processo_completo',
                'descricao': 'Tempo total do processo de emissão até envio final',
                'impacto': 'Performance geral - KPI principal'
            },
            {
                'nome': 'CTE → Baixa',
                'campo_inicio': 'data_emissao',
                'campo_fim': 'data_baixa',
                'coluna_resultado': 'dias_cte_baixa',
                'meta_dias': 30,
                'codigo': 'cte_baixa',
                'categoria': 'financeiro',
                'descricao': 'Tempo total para recebimento',
                'impacto': 'Financeiro - Ciclo de caixa'
            },
            {
                'nome': 'Atesto → Baixa',
                'campo_inicio': 'data_atesto',
                'campo_fim': 'data_baixa',
                'coluna_resultado': 'dias_atesto_baixa',
                'meta_dias': 20,
                'codigo': 'atesto_baixa',
                'categoria': 'financeiro',
                'descricao': 'Tempo para pagamento após atesto',
                'impacto': 'Financeiro - Prazo de pagamento'
            }
        ]
    
    def _get_metas_produtividade(self) -> Dict:
        """Define metas de produtividade por categoria"""
        return {
            'processo_interno': {
                'excelente': 0.8,  # 80% dentro da meta
                'bom': 0.6,        # 60% dentro da meta
                'atencao': 0.4,    # 40% dentro da meta
                'critico': 0.2     # 20% dentro da meta
            },
            'processo_cliente': {
                'excelente': 0.7,  # Mais flexível para processos com cliente
                'bom': 0.5,
                'atencao': 0.3,
                'critico': 0.1
            },
            'processo_completo': {
                'excelente': 0.75,
                'bom': 0.55,
                'atencao': 0.35,
                'critico': 0.15
            },
            'financeiro': {
                'excelente': 0.7,
                'bom': 0.5,
                'atencao': 0.3,
                'critico': 0.1
            }
        }
    
    def calcular_todas_variacoes(self) -> pd.DataFrame:
        """Calcula todas as variações e atualiza o DataFrame"""
        
        print("🔄 Iniciando cálculo de variações temporais...")
        
        for config in self.variacoes_config:
            campo_inicio = config['campo_inicio']
            campo_fim = config['campo_fim']
            coluna_resultado = config['coluna_resultado']
            
            if campo_inicio in self.df.columns and campo_fim in self.df.columns:
                # Calcular diferença em dias
                mask = self.df[campo_inicio].notna() & self.df[campo_fim].notna()
                
                if mask.any():
                    dias = (self.df.loc[mask, campo_fim] - self.df.loc[mask, campo_inicio]).dt.days
                    
                    # Filtrar dias válidos (não negativos)
                    dias_validos = dias[dias >= 0]
                    
                    # Atualizar coluna no DataFrame
                    self.df.loc[mask, coluna_resultado] = dias
                    
                    print(f"✅ {config['nome']}: {len(dias_validos)} registros calculados")
                else:
                    print(f"⚠️ {config['nome']}: Sem dados válidos")
            else:
                print(f"❌ {config['nome']}: Colunas não encontradas")
        
        return self.df
    
    def gerar_relatorio_variacoes(self) -> Dict:
        """Gera relatório completo das variações"""
        
        relatorio = {
            'resumo_geral': {},
            'por_categoria': {},
            'detalhamento': {},
            'alertas': [],
            'recomendacoes': []
        }
        
        total_processos = 0
        processos_dentro_meta = 0
        
        for config in self.variacoes_config:
            campo_inicio = config['campo_inicio']
            campo_fim = config['campo_fim']
            coluna_resultado = config['coluna_resultado']
            meta_dias = config['meta_dias']
            categoria = config['categoria']
            codigo = config['codigo']
            
            if coluna_resultado in self.df.columns:
                # Dados válidos
                dados_validos = self.df[self.df[coluna_resultado].notna()][coluna_resultado]
                
                if len(dados_validos) > 0:
                    # Estatísticas básicas
                    media = dados_validos.mean()
                    mediana = dados_validos.median()
                    desvio_padrao = dados_validos.std()
                    percentil_90 = dados_validos.quantile(0.9)
                    minimo = dados_validos.min()
                    maximo = dados_validos.max()
                    
                    # Performance vs meta
                    dentro_meta = len(dados_validos[dados_validos <= meta_dias])
                    taxa_conformidade = dentro_meta / len(dados_validos)
                    
                    # Classificar performance
                    meta_categoria = self.metas_produtividade.get(categoria, self.metas_produtividade['processo_interno'])
                    
                    if taxa_conformidade >= meta_categoria['excelente']:
                        performance = 'excelente'
                        cor = '#28a745'
                    elif taxa_conformidade >= meta_categoria['bom']:
                        performance = 'bom'
                        cor = '#17a2b8'
                    elif taxa_conformidade >= meta_categoria['atencao']:
                        performance = 'atencao'
                        cor = '#ffc107'
                    else:
                        performance = 'critico'
                        cor = '#dc3545'
                    
                    # Detalhamento
                    detalhes = {
                        'nome': config['nome'],
                        'categoria': categoria,
                        'quantidade': len(dados_validos),
                        'media': round(media, 1),
                        'mediana': round(mediana, 1),
                        'desvio_padrao': round(desvio_padrao, 1),
                        'percentil_90': round(percentil_90, 1),
                        'minimo': int(minimo),
                        'maximo': int(maximo),
                        'meta_dias': meta_dias,
                        'dentro_meta': dentro_meta,
                        'taxa_conformidade': round(taxa_conformidade * 100, 1),
                        'performance': performance,
                        'cor': cor,
                        'desvio_meta': round(((media - meta_dias) / meta_dias * 100), 1) if meta_dias > 0 else 0,
                        'descricao': config['descricao'],
                        'impacto': config['impacto']
                    }
                    
                    relatorio['detalhamento'][codigo] = detalhes
                    
                    # Acumular para resumo geral
                    total_processos += len(dados_validos)
                    processos_dentro_meta += dentro_meta
                    
                    # Acumular por categoria
                    if categoria not in relatorio['por_categoria']:
                        relatorio['por_categoria'][categoria] = {
                            'processos': 0,
                            'dentro_meta': 0,
                            'variacoes': []
                        }
                    
                    relatorio['por_categoria'][categoria]['processos'] += len(dados_validos)
                    relatorio['por_categoria'][categoria]['dentro_meta'] += dentro_meta
                    relatorio['por_categoria'][categoria]['variacoes'].append(detalhes)
                    
                    # Gerar alertas se performance crítica
                    if performance == 'critico':
                        relatorio['alertas'].append({
                            'tipo': 'performance_critica',
                            'processo': config['nome'],
                            'taxa_conformidade': taxa_conformidade,
                            'media_dias': media,
                            'meta_dias': meta_dias
                        })
                    
                    # Gerar recomendações
                    if media > meta_dias * 1.5:
                        relatorio['recomendacoes'].append({
                            'processo': config['nome'],
                            'recomendacao': f"Processo com média de {media:.1f} dias (meta: {meta_dias}). Revisar fluxo de trabalho.",
                            'prioridade': 'alta' if performance == 'critico' else 'media'
                        })
        
        # Resumo geral
        relatorio['resumo_geral'] = {
            'total_processos': total_processos,
            'processos_dentro_meta': processos_dentro_meta,
            'taxa_geral_conformidade': round((processos_dentro_meta / total_processos * 100), 1) if total_processos > 0 else 0,
            'categorias_analisadas': len(relatorio['por_categoria']),
            'variacoes_calculadas': len(relatorio['detalhamento'])
        }
        
        return relatorio
    
    def gerar_graficos_variacoes(self, relatorio: Dict) -> go.Figure:
        """Gera gráficos completos das variações"""
        
        # Dados para gráficos
        nomes = []
        medias = []
        metas = []
        performances = []
        categorias = []
        taxa_conformidade = []
        
        for codigo, dados in relatorio['detalhamento'].items():
            nomes.append(dados['nome'])
            medias.append(dados['media'])
            metas.append(dados['meta_dias'])
            performances.append(dados['performance'])
            categorias.append(dados['categoria'])
            taxa_conformidade.append(dados['taxa_conformidade'])
        
        # Cores por performance
        cores_performance = {
            'excelente': '#28a745',
            'bom': '#17a2b8',
            'atencao': '#ffc107',
            'critico': '#dc3545'
        }
        
        cores = [cores_performance.get(perf, '#6c757d') for perf in performances]
        
        # Criar subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Média vs Meta (dias)',
                'Taxa de Conformidade (%)',
                'Distribuição por Performance',
                'Performance por Categoria'
            ),
            specs=[
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "pie"}, {"type": "bar"}]
            ]
        )
        
        # Gráfico 1: Média vs Meta
        fig.add_trace(
            go.Bar(
                x=nomes,
                y=medias,
                name='Média Atual',
                marker_color=cores,
                text=[f'{media:.1f}d' for media in medias],
                textposition='auto',
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Linha de meta
        fig.add_trace(
            go.Scatter(
                x=nomes,
                y=metas,
                mode='markers+lines',
                name='Meta',
                line=dict(color='red', dash='dash', width=2),
                marker=dict(color='red', size=8),
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Gráfico 2: Taxa de Conformidade
        fig.add_trace(
            go.Bar(
                x=nomes,
                y=taxa_conformidade,
                name='Taxa de Conformidade',
                marker_color=cores,
                text=[f'{taxa:.1f}%' for taxa in taxa_conformidade],
                textposition='auto',
                showlegend=False
            ),
            row=1, col=2
        )
        
        # Gráfico 3: Distribuição por Performance
        performance_counts = {}
        for perf in performances:
            performance_counts[perf] = performance_counts.get(perf, 0) + 1
        
        fig.add_trace(
            go.Pie(
                labels=list(performance_counts.keys()),
                values=list(performance_counts.values()),
                marker_colors=[cores_performance.get(perf, '#6c757d') for perf in performance_counts.keys()],
                name="Performance",
                showlegend=False
            ),
            row=2, col=1
        )
        
        # Gráfico 4: Performance por Categoria
        categoria_performance = {}
        for cat, perf in zip(categorias, performances):
            if cat not in categoria_performance:
                categoria_performance[cat] = {'excelente': 0, 'bom': 0, 'atencao': 0, 'critico': 0}
            categoria_performance[cat][perf] += 1
        
        categorias_unicas = list(categoria_performance.keys())
        for performance_tipo in ['excelente', 'bom', 'atencao', 'critico']:
            valores = [categoria_performance[cat].get(performance_tipo, 0) for cat in categorias_unicas]
            fig.add_trace(
                go.Bar(
                    x=categorias_unicas,
                    y=valores,
                    name=performance_tipo.title(),
                    marker_color=cores_performance[performance_tipo]
                ),
                row=2, col=2
            )
        
        # Layout
        fig.update_layout(
            height=800,
            title_text="Análise Completa de Variações Temporais",
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Atualizar eixos
        fig.update_xaxes(title_text="Processos", row=1, col=1, tickangle=45)
        fig.update_yaxes(title_text="Dias", row=1, col=1)
        
        fig.update_xaxes(title_text="Processos", row=1, col=2, tickangle=45)
        fig.update_yaxes(title_text="Taxa (%)", row=1, col=2)
        
        fig.update_xaxes(title_text="Categorias", row=2, col=2)
        fig.update_yaxes(title_text="Quantidade", row=2, col=2)
        
        return fig
    
    def gerar_dashboard_produtividade(self) -> Dict:
        """Gera dashboard específico de produtividade"""
        
        relatorio = self.gerar_relatorio_variacoes()
        
        # KPIs de produtividade
        kpis = {
            'eficiencia_geral': relatorio['resumo_geral']['taxa_geral_conformidade'],
            'processos_criticos': len([d for d in relatorio['detalhamento'].values() if d['performance'] == 'critico']),
            'processos_excelentes': len([d for d in relatorio['detalhamento'].values() if d['performance'] == 'excelente']),
            'media_desvio_meta': np.mean([d['desvio_meta'] for d in relatorio['detalhamento'].values()]),
        }
        
        # Ranking de processos (melhor para pior)
        ranking = sorted(
            relatorio['detalhamento'].values(),
            key=lambda x: x['taxa_conformidade'],
            reverse=True
        )
        
        # Processos que mais impactam o resultado
        impacto_alto = [
            d for d in relatorio['detalhamento'].values()
            if d['categoria'] in ['processo_completo', 'financeiro'] and d['performance'] in ['critico', 'atencao']
        ]
        
        return {
            'kpis': kpis,
            'ranking': ranking,
            'impacto_alto': impacto_alto,
            'relatorio_completo': relatorio
        }
    
    def exportar_analise_completa(self) -> Tuple[pd.DataFrame, Dict]:
        """Exporta análise completa para arquivo"""
        
        # Calcular variações
        df_atualizado = self.calcular_todas_variacoes()
        
        # Gerar relatório
        relatorio = self.gerar_relatorio_variacoes()
        
        # Adicionar colunas de classificação ao DataFrame
        for config in self.variacoes_config:
            coluna_resultado = config['coluna_resultado']
            meta_dias = config['meta_dias']
            
            if coluna_resultado in df_atualizado.columns:
                # Coluna de conformidade
                coluna_conformidade = f'{coluna_resultado}_conformidade'
                df_atualizado[coluna_conformidade] = df_atualizado[coluna_resultado].apply(
                    lambda x: 'Dentro da Meta' if pd.notna(x) and x <= meta_dias else 'Fora da Meta' if pd.notna(x) else 'Sem Dados'
                )
                
                # Coluna de performance
                coluna_performance = f'{coluna_resultado}_performance'
                categoria = config['categoria']
                meta_categoria = self.metas_produtividade.get(categoria, self.metas_produtividade['processo_interno'])
                
                def classificar_performance(dias):
                    if pd.isna(dias):
                        return 'Sem Dados'
                    if dias <= meta_dias:
                        return 'Excelente'
                    elif dias <= meta_dias * 1.5:
                        return 'Bom'
                    elif dias <= meta_dias * 2:
                        return 'Atenção'
                    else:
                        return 'Crítico'
                
                df_atualizado[coluna_performance] = df_atualizado[coluna_resultado].apply(classificar_performance)
        
        return df_atualizado, relatorio

def exibir_dashboard_variacoes_streamlit(df: pd.DataFrame):
    """Exibe dashboard de variações no Streamlit"""
    
    st.markdown("""
    <div class="section-header">
        <div class="section-title">⏱️ Análise Avançada de Variações Temporais</div>
        <div class="section-subtitle">Sistema de produtividade e performance com metas</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar análise
    analise = AnaliseVariacoesTempo(df)
    
    # Gerar dashboard de produtividade
    with st.spinner('📊 Calculando variações temporais...'):
        dashboard = analise.gerar_dashboard_produtividade()
    
    # KPIs principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        eficiencia = dashboard['kpis']['eficiencia_geral']
        cor = '#28a745' if eficiencia >= 70 else '#ffc107' if eficiencia >= 50 else '#dc3545'
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: {cor};">
            <div class="metric-number">{eficiencia:.1f}%</div>
            <div class="metric-title">Eficiência Geral</div>
            <div class="metric-subtitle">Processos dentro da meta</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        criticos = dashboard['kpis']['processos_criticos']
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #dc3545;">
            <div class="metric-number">{criticos}</div>
            <div class="metric-title">Processos Críticos</div>
            <div class="metric-subtitle">Precisam de atenção imediata</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        excelentes = dashboard['kpis']['processos_excelentes']
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #28a745;">
            <div class="metric-number">{excelentes}</div>
            <div class="metric-title">Processos Excelentes</div>
            <div class="metric-subtitle">Performance superior</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        desvio = dashboard['kpis']['media_desvio_meta']
        cor_desvio = '#28a745' if desvio <= 10 else '#ffc107' if desvio <= 30 else '#dc3545'
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: {cor_desvio};">
            <div class="metric-number">{desvio:+.1f}%</div>
            <div class="metric-title">Desvio Médio da Meta</div>
            <div class="metric-subtitle">Variação vs meta estabelecida</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Gráficos
    st.subheader("📈 Análise Visual Completa")
    fig = analise.gerar_graficos_variacoes(dashboard['relatorio_completo'])
    st.plotly_chart(fig, use_container_width=True)
    
    # Ranking de processos
    st.subheader("🏆 Ranking de Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🟢 Melhores Performances**")
        for i, processo in enumerate(dashboard['ranking'][:5], 1):
            emoji = '🥇' if i == 1 else '🥈' if i == 2 else '🥉' if i == 3 else '🏅'
            st.write(f"{emoji} {processo['nome']}: {processo['taxa_conformidade']:.1f}%")
    
    with col2:
        st.markdown("**🔴 Performances Críticas**")
        criticos = [p for p in dashboard['ranking'] if p['performance'] == 'critico']
        for processo in criticos:
            st.write(f"⚠️ {processo['nome']}: {processo['taxa_conformidade']:.1f}%")
    
    # Alertas e recomendações
    if dashboard['relatorio_completo']['alertas']:
        st.subheader("🚨 Alertas Críticos")
        for alerta in dashboard['relatorio_completo']['alertas']:
            st.error(f"**{alerta['processo']}**: Taxa de conformidade {alerta['taxa_conformidade']*100:.1f}% (Média: {alerta['media_dias']:.1f} dias vs Meta: {alerta['meta_dias']} dias)")
    
    if dashboard['relatorio_completo']['recomendacoes']:
        st.subheader("💡 Recomendações")
        for rec in dashboard['relatorio_completo']['recomendacoes']:
            icon = "🔴" if rec['prioridade'] == 'alta' else "🟡"
            st.warning(f"{icon} **{rec['processo']}**: {rec['recomendacao']}")
    
    # Download da análise
    st.subheader("📥 Download da Análise")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Gerar Relatório Completo"):
            df_analise, relatorio_completo = analise.exportar_analise_completa()
            
            # Criar CSV
            csv_data = df_analise.to_csv(index=False, sep=';', encoding='utf-8')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            st.download_button(
                label="📄 Download CSV com Análise",
                data=csv_data,
                file_name=f"analise_variacoes_temporais_{timestamp}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📈 Exportar Gráficos"):
            st.info("💡 Use o botão de download no canto superior direito do gráfico")
    
    return dashboard

# Exemplo de uso
if __name__ == "__main__":
    # Dados de exemplo
    sample_data = {
        'numero_cte': [1001, 1002, 1003],
        'data_emissao': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'data_inclusao_fatura': ['2024-01-03', '2024-01-04', '2024-01-05'],
        'primeiro_envio': ['2024-01-04', '2024-01-05', '2024-01-06'],
        'data_atesto': ['2024-01-10', '2024-01-12', '2024-01-14'],
        'envio_final': ['2024-01-12', '2024-01-14', '2024-01-16'],
        'data_baixa': ['2024-01-20', None, '2024-01-25']
    }
    
    df = pd.DataFrame(sample_data)
    
    # Converter datas
    date_cols = ['data_emissao', 'data_inclusao_fatura', 'primeiro_envio', 'data_atesto', 'envio_final', 'data_baixa']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col])
    
    # Executar análise
    analise = AnaliseVariacoesTempo(df)
    df_resultado, relatorio = analise.exportar_analise_completa()
    
    print("✅ Análise de variações temporais concluída!")
    print(f"📊 Relatório gerado com {len(relatorio['detalhamento'])} variações calculadas")