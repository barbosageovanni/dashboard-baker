-- ============================================================================
-- QUERIES ÚTEIS - DASHBOARD BAKER
-- Sistema de Gestão Financeira com PostgreSQL/Supabase
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. ESTRUTURA E MANUTENÇÃO
-- ----------------------------------------------------------------------------

-- Criar tabela principal (se não existir)
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

-- Criar índices para performance
CREATE INDEX IF NOT EXISTS idx_numero_cte ON dashboard_baker(numero_cte);
CREATE INDEX IF NOT EXISTS idx_data_emissao ON dashboard_baker(data_emissao);
CREATE INDEX IF NOT EXISTS idx_destinatario ON dashboard_baker(destinatario_nome);
CREATE INDEX IF NOT EXISTS idx_data_baixa ON dashboard_baker(data_baixa);
CREATE INDEX IF NOT EXISTS idx_valor_total ON dashboard_baker(valor_total);

-- Trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_dashboard_baker_updated_at 
BEFORE UPDATE ON dashboard_baker 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ----------------------------------------------------------------------------
-- 2. CONSULTAS DE STATUS E MÉTRICAS
-- ----------------------------------------------------------------------------

-- Resumo geral do sistema
SELECT 
    COUNT(*) as total_registros,
    COUNT(DISTINCT destinatario_nome) as clientes_unicos,
    COUNT(DISTINCT veiculo_placa) as veiculos_ativos,
    SUM(valor_total) as valor_total,
    AVG(valor_total) as ticket_medio,
    COUNT(CASE WHEN numero_fatura IS NOT NULL THEN 1 END) as com_fatura,
    COUNT(CASE WHEN numero_fatura IS NULL THEN 1 END) as sem_fatura,
    COUNT(CASE WHEN data_baixa IS NOT NULL THEN 1 END) as faturas_pagas,
    COUNT(CASE WHEN data_baixa IS NULL THEN 1 END) as faturas_pendentes
FROM dashboard_baker;

-- Análise de valores por status
SELECT 
    'Com Fatura' as categoria,
    COUNT(*) as quantidade,
    SUM(valor_total) as valor_total
FROM dashboard_baker
WHERE numero_fatura IS NOT NULL
UNION ALL
SELECT 
    'Sem Fatura' as categoria,
    COUNT(*) as quantidade,
    SUM(valor_total) as valor_total
FROM dashboard_baker
WHERE numero_fatura IS NULL
UNION ALL
SELECT 
    'Pagas' as categoria,
    COUNT(*) as quantidade,
    SUM(valor_total) as valor_total
FROM dashboard_baker
WHERE data_baixa IS NOT NULL
UNION ALL
SELECT 
    'Pendentes' as categoria,
    COUNT(*) as quantidade,
    SUM(valor_total) as valor_total
FROM dashboard_baker
WHERE data_baixa IS NULL;

-- ----------------------------------------------------------------------------
-- 3. ANÁLISE DE VARIAÇÕES TEMPORAIS
-- ----------------------------------------------------------------------------

-- Variação: Data Emissão CTE → Inclusão Fatura
SELECT 
    AVG(data_inclusao_fatura - data_emissao) as media_dias,
    MIN(data_inclusao_fatura - data_emissao) as min_dias,
    MAX(data_inclusao_fatura - data_emissao) as max_dias,
    COUNT(*) as registros
FROM dashboard_baker
WHERE data_emissao IS NOT NULL 
  AND data_inclusao_fatura IS NOT NULL;

-- Variação: RQ/TMC → 1º Envio
SELECT 
    AVG(primeiro_envio - data_rq_tmc) as media_dias,
    MIN(primeiro_envio - data_rq_tmc) as min_dias,
    MAX(primeiro_envio - data_rq_tmc) as max_dias,
    COUNT(*) as registros
FROM dashboard_baker
WHERE data_rq_tmc IS NOT NULL 
  AND primeiro_envio IS NOT NULL;

-- Variação: 1º Envio → Atesto
SELECT 
    AVG(data_atesto - primeiro_envio) as media_dias,
    MIN(data_atesto - primeiro_envio) as min_dias,
    MAX(data_atesto - primeiro_envio) as max_dias,
    COUNT(*) as registros
FROM dashboard_baker
WHERE primeiro_envio IS NOT NULL 
  AND data_atesto IS NOT NULL;

-- Variação: Atesto → Envio Final
SELECT 
    AVG(envio_final - data_atesto) as media_dias,
    MIN(envio_final - data_atesto) as min_dias,
    MAX(envio_final - data_atesto) as max_dias,
    COUNT(*) as registros
FROM dashboard_baker
WHERE data_atesto IS NOT NULL 
  AND envio_final IS NOT NULL;

-- ----------------------------------------------------------------------------
-- 4. ANÁLISE POR CLIENTE
-- ----------------------------------------------------------------------------

-- Top 10 clientes por valor
SELECT 
    destinatario_nome,
    COUNT(*) as qtd_ctes,
    SUM(valor_total) as valor_total,
    AVG(valor_total) as ticket_medio,
    COUNT(DISTINCT veiculo_placa) as veiculos_utilizados,
    MIN(data_emissao) as primeira_operacao,
    MAX(data_emissao) as ultima_operacao
FROM dashboard_baker
GROUP BY destinatario_nome
ORDER BY valor_total DESC
LIMIT 10;

-- Análise de inadimplência por cliente
SELECT 
    destinatario_nome,
    COUNT(CASE WHEN data_baixa IS NULL THEN 1 END) as faturas_pendentes,
    SUM(CASE WHEN data_baixa IS NULL THEN valor_total ELSE 0 END) as valor_pendente,
    COUNT(CASE WHEN data_baixa IS NOT NULL THEN 1 END) as faturas_pagas,
    SUM(CASE WHEN data_baixa IS NOT NULL THEN valor_total ELSE 0 END) as valor_pago,
    ROUND(
        COUNT(CASE WHEN data_baixa IS NULL THEN 1 END)::numeric / 
        NULLIF(COUNT(*), 0) * 100, 2
    ) as taxa_inadimplencia
FROM dashboard_baker
GROUP BY destinatario_nome
HAVING COUNT(CASE WHEN data_baixa IS NULL THEN 1 END) > 0
ORDER BY valor_pendente DESC;

-- ----------------------------------------------------------------------------
-- 5. ANÁLISE POR VEÍCULO
-- ----------------------------------------------------------------------------

-- Performance por veículo
SELECT 
    veiculo_placa,
    COUNT(*) as viagens,
    SUM(valor_total) as receita_total,
    AVG(valor_total) as receita_media,
    COUNT(DISTINCT destinatario_nome) as clientes_atendidos,
    MIN(data_emissao) as primeira_viagem,
    MAX(data_emissao) as ultima_viagem
FROM dashboard_baker
WHERE veiculo_placa IS NOT NULL
GROUP BY veiculo_placa
ORDER BY receita_total DESC;

-- ----------------------------------------------------------------------------
-- 6. ANÁLISE TEMPORAL
-- ----------------------------------------------------------------------------

-- Receita mensal
SELECT 
    TO_CHAR(data_emissao, 'YYYY-MM') as mes_ano,
    COUNT(*) as qtd_ctes,
    SUM(valor_total) as receita_mensal,
    AVG(valor_total) as ticket_medio
FROM dashboard_baker
WHERE data_emissao IS NOT NULL
GROUP BY TO_CHAR(data_emissao, 'YYYY-MM')
ORDER BY mes_ano DESC;

-- Evolução diária (últimos 30 dias)
SELECT 
    data_emissao,
    COUNT(*) as ctes_dia,
    SUM(valor_total) as receita_dia
FROM dashboard_baker
WHERE data_emissao >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY data_emissao
ORDER BY data_emissao DESC;

-- ----------------------------------------------------------------------------
-- 7. ALERTAS E PENDÊNCIAS
-- ----------------------------------------------------------------------------

-- CTEs sem primeiro envio (há mais de 10 dias)
SELECT 
    numero_cte,
    destinatario_nome,
    valor_total,
    data_emissao,
    CURRENT_DATE - data_emissao as dias_pendente
FROM dashboard_baker
WHERE primeiro_envio IS NULL 
  AND data_emissao <= CURRENT_DATE - INTERVAL '10 days'
ORDER BY dias_pendente DESC;

-- Faturas vencidas (90+ dias sem baixa após atesto)
SELECT 
    numero_cte,
    destinatario_nome,
    numero_fatura,
    valor_total,
    data_atesto,
    CURRENT_DATE - data_atesto as dias_vencido
FROM dashboard_baker
WHERE data_baixa IS NULL 
  AND data_atesto IS NOT NULL
  AND data_atesto <= CURRENT_DATE - INTERVAL '90 days'
ORDER BY dias_vencido DESC;

-- CTEs sem fatura (após atesto)
SELECT 
    numero_cte,
    destinatario_nome,
    valor_total,
    data_atesto,
    CURRENT_DATE - data_atesto as dias_sem_fatura
FROM dashboard_baker
WHERE numero_fatura IS NULL 
  AND data_atesto IS NOT NULL
ORDER BY dias_sem_fatura DESC;

-- Processos incompletos
SELECT 
    numero_cte,
    destinatario_nome,
    valor_total,
    CASE 
        WHEN data_emissao IS NULL THEN 'Sem data emissão'
        WHEN primeiro_envio IS NULL THEN 'Sem 1º envio'
        WHEN data_atesto IS NULL THEN 'Sem atesto'
        WHEN envio_final IS NULL THEN 'Sem envio final'
        ELSE 'Completo'
    END as status_processo
FROM dashboard_baker
WHERE data_emissao IS NULL 
   OR primeiro_envio IS NULL 
   OR data_atesto IS NULL 
   OR envio_final IS NULL
ORDER BY numero_cte DESC;

-- ----------------------------------------------------------------------------
-- 8. OPERAÇÕES DE MANUTENÇÃO
-- ----------------------------------------------------------------------------

-- Registrar baixa de fatura
UPDATE dashboard_baker 
SET 
    data_baixa = CURRENT_DATE,
    observacao = COALESCE(observacao, '') || ' | Baixa manual em ' || CURRENT_DATE,
    updated_at = CURRENT_TIMESTAMP
WHERE numero_cte = 12345;  -- Substituir pelo número do CTE

-- Atualizar múltiplas baixas
UPDATE dashboard_baker 
SET 
    data_baixa = CURRENT_DATE,
    updated_at = CURRENT_TIMESTAMP
WHERE numero_cte IN (12345, 12346, 12347);  -- Lista de CTEs

-- Limpar duplicatas (mantendo mais recente)
DELETE FROM dashboard_baker a
USING dashboard_baker b
WHERE a.id < b.id 
  AND a.numero_cte = b.numero_cte;

-- ----------------------------------------------------------------------------
-- 9. RELATÓRIOS EXECUTIVOS
-- ----------------------------------------------------------------------------

-- Dashboard executivo completo
WITH metricas AS (
    SELECT 
        COUNT(*) as total_ctes,
        COUNT(DISTINCT destinatario_nome) as clientes,
        SUM(valor_total) as receita_total,
        AVG(valor_total) as ticket_medio,
        COUNT(CASE WHEN data_baixa IS NOT NULL THEN 1 END) as ctes_pagos,
        SUM(CASE WHEN data_baixa IS NOT NULL THEN valor_total END) as valor_pago,
        COUNT(CASE WHEN data_baixa IS NULL THEN 1 END) as ctes_pendentes,
        SUM(CASE WHEN data_baixa IS NULL THEN valor_total END) as valor_pendente
    FROM dashboard_baker
),
processos_completos AS (
    SELECT COUNT(*) as completos
    FROM dashboard_baker
    WHERE data_emissao IS NOT NULL 
      AND primeiro_envio IS NOT NULL 
      AND data_atesto IS NOT NULL 
      AND envio_final IS NOT NULL
)
SELECT 
    m.*,
    p.completos as processos_completos,
    ROUND(p.completos::numeric / NULLIF(m.total_ctes, 0) * 100, 2) as taxa_conclusao
FROM metricas m, processos_completos p;

-- ----------------------------------------------------------------------------
-- 10. VIEWS ÚTEIS
-- ----------------------------------------------------------------------------

-- View de CTEs pendentes
CREATE OR REPLACE VIEW v_ctes_pendentes AS
SELECT 
    numero_cte,
    destinatario_nome,
    veiculo_placa,
    valor_total,
    data_emissao,
    numero_fatura,
    CURRENT_DATE - data_emissao as dias_em_aberto,
    CASE 
        WHEN primeiro_envio IS NULL THEN '1º Envio Pendente'
        WHEN data_atesto IS NULL THEN 'Aguardando Atesto'
        WHEN numero_fatura IS NULL THEN 'Sem Fatura'
        WHEN data_baixa IS NULL THEN 'Aguardando Pagamento'
        ELSE 'OK'
    END as status_atual
FROM dashboard_baker
WHERE data_baixa IS NULL
ORDER BY dias_em_aberto DESC;

-- View de performance mensal
CREATE OR REPLACE VIEW v_performance_mensal AS
SELECT 
    TO_CHAR(data_emissao, 'YYYY-MM') as mes,
    COUNT(*) as ctes,
    SUM(valor_total) as receita,
    AVG(valor_total) as ticket_medio,
    COUNT(CASE WHEN data_baixa IS NOT NULL THEN 1 END) as ctes_pagos,
    SUM(CASE WHEN data_baixa IS NOT NULL THEN valor_total END) as receita_realizada,
    ROUND(
        COUNT(CASE WHEN data_baixa IS NOT NULL THEN 1 END)::numeric / 
        NULLIF(COUNT(*), 0) * 100, 2
    ) as taxa_pagamento
FROM dashboard_baker
WHERE data_emissao IS NOT NULL
GROUP BY TO_CHAR(data_emissao, 'YYYY-MM')
ORDER BY mes DESC;

-- ----------------------------------------------------------------------------
-- 11. FUNÇÕES ÚTEIS
-- ----------------------------------------------------------------------------

-- Função para calcular dias úteis entre datas
CREATE OR REPLACE FUNCTION dias_uteis(data_inicial DATE, data_final DATE)
RETURNS INTEGER AS $
DECLARE
    dias INTEGER := 0;
    data_atual DATE := data_inicial;
BEGIN
    WHILE data_atual <= data_final LOOP
        IF EXTRACT(DOW FROM data_atual) NOT IN (0, 6) THEN
            dias := dias + 1;
        END IF;
        data_atual := data_atual + INTERVAL '1 day';
    END LOOP;
    RETURN dias;
END;
$ LANGUAGE plpgsql;

-- Usar função de dias úteis nas análises
SELECT 
    numero_cte,
    dias_uteis(data_emissao, COALESCE(data_baixa, CURRENT_DATE)) as dias_uteis_processo
FROM dashboard_baker
LIMIT 10;