# 💰 Dashboard Baker - Sistema Financeiro Transpontual

## 🚀 Versão 2.0 - Integração PostgreSQL

### ✅ Correções Implementadas

- **🔧 Erro `titlefont` corrigido**: Atualizado para `title` conforme nova API do Plotly
- **🗄️ Nova aba PostgreSQL**: Inserção direta de CTEs no banco de dados
- **📝 Formulário completo**: Todos os campos do CSV disponíveis para inserção
- **🔄 Sincronização total**: Dados integrados entre CSV e banco PostgreSQL

---

## 📋 Estrutura do Sistema

```
Dashboard Baker/
├── 📊 dashboard_baker_web_corrigido.py     # Dashboard principal (CORRIGIDO)
├── 🗄️ popular_banco_postgresql.py          # Popular banco com CSV existente
├── ⚙️ config_banco.py                      # Configurações centralizadas
├── 🚀 setup_dashboard_postgresql.py        # Setup automático Python
├── 🪟 setup_dashboard_postgresql.bat       # Setup automático Windows
├── 📄 .env                                 # Variáveis de ambiente
├── 📦 requirements_postgresql.txt          # Dependências
└── 🎯 iniciar_dashboard_postgresql.bat     # Script de inicialização
```

---

## 🏗️ Arquitetura do Sistema

### 🎯 Dashboard Principal
- **Aba 1: 📊 Dashboard Principal** - Análise de dados CSV (funcionalidade original)
- **Aba 2: 🗄️ Inserção no Banco** - Nova funcionalidade PostgreSQL

### 🗄️ Banco de Dados PostgreSQL

```sql
CREATE TABLE dashboard_baker (
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
    origem_dados VARCHAR(50) DEFAULT 'CSV_LOCAL',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🚀 Instalação e Configuração

### 📋 Pré-requisitos

1. **🐍 Python 3.8+** - [Download Python](https://www.python.org/downloads/)
2. **🐘 PostgreSQL** - [Download PostgreSQL](https://www.postgresql.org/download/)
3. **🌐 Navegador web** - Para acessar o dashboard

### ⚡ Instalação Rápida (Windows)

```batch
# 1. Execute o setup automático
setup_dashboard_postgresql.bat

# 2. Siga as instruções na tela

# 3. Execute o dashboard
iniciar_dashboard_postgresql.bat
```

### 🐧 Instalação Manual (Linux/Mac)

```bash
# 1. Clone/baixe os arquivos

# 2. Instale dependências
pip install -r requirements_postgresql.txt

# 3. Configure PostgreSQL
# Edite as variáveis no arquivo .env

# 4. Execute setup
python setup_dashboard_postgresql.py

# 5. Execute dashboard
streamlit run dashboard_baker_web_corrigido.py
```

---

## 🎯 Como Usar

### 📊 Aba 1: Dashboard Principal

1. **📤 Upload de CSV**: Carregue o arquivo CSV do Baker
2. **📈 Visualize métricas**: Resumo executivo automático
3. **⏱️ Análise temporal**: Variações de tempo entre processos
4. **📋 Relatórios**: Gráficos interativos e tabelas

### 🗄️ Aba 2: Inserção no Banco

1. **📝 Formulário completo**: Todos os campos disponíveis
2. **✅ Validação automática**: Campos obrigatórios verificados
3. **💾 Salvar no PostgreSQL**: Dados persistentes
4. **📊 Visualização**: Tabela com todos os CTEs cadastrados

---

## 📊 Funcionalidades Implementadas

### ✅ Dashboard Original (Mantido)
- 📊 Análise de status das faturas
- 👥 Visão por cliente
- 🚛 Análise por veículos
- ⏱️ **7 variações de tempo implementadas**:
  - 📋 CTE → Inclusão Fatura
  - 📤 CTE → Envio Processo
  - 🔄 Inclusão → Envio Processo
  - 📨 Inclusão → 1º Envio
  - 🚛 RQ/TMC → 1º Envio
  - ✅ 1º Envio → Atesto
  - 🏁 Atesto → Envio Final
- 🔄 Sistema de conciliação de baixas

### 🆕 Novas Funcionalidades PostgreSQL
- 🗄️ **Inserção direta no banco**
- 📝 **Formulário web completo**
- 🔄 **Sincronização automática**
- 📊 **Visualização integrada**
- 🧪 **Teste de conexão**
- 📥 **Export para CSV**
- 🔍 **Filtros avançados**

---

## 🔧 Configuração Avançada

### 📄 Arquivo .env

```env
# Configuração do Banco PostgreSQL
DB_HOST=localhost
DB_NAME=dashboard_baker
DB_USER=postgres
DB_PASSWORD=sua_senha_aqui
DB_PORT=5432

# Configurações do Streamlit
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
```

### 🏢 Configurações por Ambiente

```python
# config_banco.py
CONFIGS = {
    'development': DatabaseConfig(
        host='localhost',
        database='dashboard_baker_dev',
        user='postgres',
        password='senha123'
    ),
    
    'production': DatabaseConfig(
        host='seu_servidor_producao',
        database='dashboard_baker_prod',
        user='baker_user',
        password='senha_segura'
    )
}
```

---

## 🗄️ Migrando Dados Existentes

### 📥 Popular Banco com CSV Existente

```bash
# Execute o script de população
python popular_banco_postgresql.py
```

**O script irá:**
1. 🔍 Detectar arquivos CSV automaticamente
2. 🔄 Mapear campos para estrutura do banco
3. 💾 Inserir dados com verificação de duplicatas
4. 📊 Fornecer relatório de inserção

### 📋 Arquivos CSV Suportados
- `Status Faturamento   Ctes vs Faturas vs Atestos.csv`
- `Relatório Faturamento Baker em aberto  Ctes vs Faturas vs Atestos.csv`
- Qualquer CSV com estrutura similar

---

## 🎨 Interface do Sistema

### 🖥️ Dashboard Principal
```
💰 Dashboard Financeiro Baker
├── 📊 Resumo Executivo
│   ├── Total de Registros: 1,234
│   ├── Valor Total: R$ 2,456,789.00
│   ├── Com Fatura: 892
│   └── Sem Documentos: 45
├── ⏱️ Análise de Produtividade
│   ├── 📋 CTE → Inclusão Fatura: 3.2 dias
│   ├── 🚛 RQ/TMC → 1º Envio: 5.1 dias
│   └── ✅ 1º Envio → Atesto: 7.8 dias
└── 📈 Gráficos Interativos
```

### 🗄️ Aba de Inserção
```
🗄️ Inserção de CTEs no Banco PostgreSQL
├── 📝 Formulário de Inserção
│   ├── 📋 Campos Obrigatórios
│   ├── 🚛 Campos Complementares
│   ├── 📅 Datas do Processo
│   └── 💰 Controle de Baixa
├── 📊 CTEs Cadastrados
│   ├── 🔍 Filtros de Visualização
│   ├── 📋 Tabela Interativa
│   └── 📥 Download CSV
└── 🧪 Teste de Conexão PostgreSQL
```

---

## 🐛 Solução de Problemas

### ❌ Erro "titlefont" Corrigido

**Problema anterior:**
```python
# ERRO - API antiga do Plotly
fig.update_layout(
    xaxis={'titlefont': {'size': 14}}  # ❌ Descontinuado
)
```

**Solução implementada:**
```python
# ✅ API atual do Plotly
fig.update_layout(
    xaxis={'title': {'font': {'size': 14}}}  # ✅ Correto
)
```

### 🐘 Problemas de Conexão PostgreSQL

1. **Verificar serviço PostgreSQL**:
   ```bash
   # Windows
   services.msc → PostgreSQL

   # Linux
   sudo systemctl status postgresql
   ```

2. **Testar conexão manualmente**:
   ```bash
   psql -h localhost -U postgres -d dashboard_baker
   ```

3. **Configurar pg_hba.conf** se necessário

### 📦 Problemas de Dependências

```bash
# Reinstalar dependências
pip install --force-reinstall -r requirements_postgresql.txt

# Atualizar pip
python -m pip install --upgrade pip
```

---

## 📈 Métricas e Indicadores

### 💰 Indicadores Financeiros
- **Valor Total**: Soma de todos os CTEs
- **Taxa de Cobrança**: % de faturas pagas
- **Taxa de Inadimplência**: % de faturas vencidas
- **Receita por Cliente**: Análise de performance

### ⏱️ Indicadores de Produtividade
- **Tempo Médio por Processo**: 7 variações calculadas
- **Gargalos Identificados**: Processos mais lentos
- **Eficiência Operacional**: Métricas de tempo

### 📊 Indicadores Operacionais
- **CTEs Processados**: Volume total
- **Veículos Ativos**: Frota em operação
- **Clientes Ativos**: Base de clientes

---

## 🔮 Roadmap Futuro

### 🎯 Próximas Funcionalidades
- 📱 **App Mobile**: Interface responsiva
- 🤖 **IA Preditiva**: Previsão de inadimplência
- 🔔 **Alertas Automáticos**: Notificações em tempo real
- 📊 **Relatórios Agendados**: Geração automática
- 🔗 **Integração ERP**: Conexão com sistemas empresariais
- 🌐 **API REST**: Endpoints para integração

### 🏗️ Melhorias Técnicas
- 🚀 **Performance**: Otimização de consultas
- 🔒 **Segurança**: Autenticação e autorização
- 📊 **Analytics**: Dashboard executivo avançado
- 🎨 **UX/UI**: Interface mais intuitiva

---

## 🤝 Suporte e Contribuição

### 📞 Suporte Técnico
- 📧 **Email**: suporte@transpontual.com.br
- 📱 **WhatsApp**: (XX) XXXXX-XXXX
- 🌐 **Portal**: https://suporte.transpontual.com.br

### 🔧 Desenvolvimento
- 💻 **Linguagem**: Python 3.8+
- 🌐 **Framework**: Streamlit
- 🗄️ **Banco**: PostgreSQL
- 📊 **Visualização**: Plotly
- 📋 **Dados**: Pandas

### 📝 Logs e Debugging
```python
# Habilitar logs detalhados
import logging
logging.basicConfig(level=logging.DEBUG)

# Verificar conexão
python -c "from config_banco import get_config; print(get_config())"
```

---

## ⚖️ Licença e Uso

### 📋 Termos de Uso
- ✅ **Uso Interno**: Liberado para Transpontual
- ✅ **Modificações**: Permitidas para melhorias
- ❌ **Redistribuição**: Não permitida sem autorização
- 🔒 **Dados**: Confidenciais da empresa

### 🛡️ Segurança
- 🔐 **Senhas**: Sempre use senhas seguras
- 🌐 **Rede**: Execute apenas em redes confiáveis
- 💾 **Backup**: Faça backup regular dos dados
- 🔄 **Updates**: Mantenha sistema atualizado

---

## 📊 Changelog

### 🆕 Versão 2.0 (Atual)
- ✅ **CORREÇÃO**: Erro `titlefont` → `title` no Plotly
- 🆕 **NOVA ABA**: Inserção PostgreSQL
- 🗄️ **BANCO**: Integração completa PostgreSQL
- 📝 **FORMULÁRIO**: Interface web para CTEs
- 🔧 **SETUP**: Scripts automáticos de instalação
- 📋 **DOCS**: Documentação completa

### 📊 Versão 1.0 (Anterior)
- 📊 Dashboard básico com CSV
- ⏱️ Análise de variações de tempo
- 🔄 Sistema de conciliação
- 📈 Gráficos interativos

---

*💰 Dashboard Baker - Sistema Financeiro Transpontual*  
*🏢 Desenvolvido para otimizar processos financeiros e logísticos*  
*⚡ Versão 2.0 - PostgreSQL Integration*