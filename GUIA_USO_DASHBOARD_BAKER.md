# 🚀 Guia Prático - Dashboard Baker PostgreSQL

## ⚡ Início Rápido (5 minutos)

### 1️⃣ Instalação Automática (Windows)
```batch
# Execute o setup automático
setup_dashboard_postgresql.bat
```

### 2️⃣ Configuração Rápida
- **Host**: localhost (padrão)
- **Porta**: 5432 (padrão PostgreSQL)
- **Usuário**: postgres (padrão)
- **Senha**: [Digite sua senha do PostgreSQL]

### 3️⃣ Executar Dashboard
```batch
# Execute o dashboard
iniciar_dashboard_postgresql.bat

# Ou manualmente
streamlit run dashboard_baker_web_corrigido.py
```

### 4️⃣ Acessar Sistema
🌐 **URL**: http://localhost:8501

---

## 📊 Como Usar as Funcionalidades

### 🗂️ Aba 1: Dashboard Principal (CSV)

#### 📤 Upload de Arquivo CSV
1. Clique em **"Carregar arquivo CSV"**
2. Selecione seu arquivo do Baker
3. Sistema processará automaticamente

#### 📈 Visualizar Métricas
- **Resumo Executivo**: Valores totais, quantidade de registros
- **Gráficos Interativos**: Status das faturas, clientes
- **Variações de Tempo**: 7 métricas de produtividade

#### ⏱️ Análise de Produtividade
```
📋 CTE → Inclusão Fatura: X.X dias (média)
📤 CTE → Envio Processo: X.X dias (média)
🔄 Inclusão → Envio Processo: X.X dias (média)
📨 Inclusão → 1º Envio: X.X dias (média)
🚛 RQ/TMC → 1º Envio: X.X dias (média)
✅ 1º Envio → Atesto: X.X dias (média)
🏁 Atesto → Envio Final: X.X dias (média)
```

### 🗄️ Aba 2: Inserção no Banco PostgreSQL

#### 📝 Formulário de Inserção

**Campos Obrigatórios:**
- **Número CTE**: Identificador único
- **Nome do Destinatário**: Cliente
- **Valor Total**: Valor em reais
- **Data de Emissão**: Data do CTE

**Campos Opcionais:**
- **Placa do Veículo**: Identificação do veículo
- **Número da Fatura**: Se já foi faturado
- **Observações**: Notas adicionais
- **Datas do Processo**: Todas as etapas do workflow
- **Data da Baixa**: Se já foi pago

#### 💾 Inserir Novo CTE

1. **Preencha o formulário**
2. **Clique em "🚀 Inserir CTE no Banco"**
3. **Sistema validará dados**
4. **Confirmação de sucesso**

#### 📊 Visualizar CTEs Cadastrados

- **Métricas rápidas**: Total, valor, pagos, em aberto
- **Filtros**: Status (Todos/Pagos/Em Aberto)
- **Tabela interativa**: Todos os CTEs
- **Download CSV**: Exportar dados

---

## 🔧 Tarefas Comuns

### 📥 Popular Banco com CSV Existente

```python
# Execute o script de população
python popular_banco_postgresql.py
```

**O que acontece:**
1. 🔍 Detecta arquivos CSV automaticamente
2. 🔄 Mapeia campos para estrutura do banco
3. 💾 Insere dados (evita duplicatas)
4. 📊 Mostra relatório de inserção

### 🧪 Testar Sistema

```python
# Execute testes completos
python teste_sistema_completo.py
```

**Testes realizados:**
- ✅ Python e dependências
- ✅ Arquivos do sistema
- ✅ Conexão PostgreSQL
- ✅ Funcionalidades do dashboard
- ✅ Inserção e consulta de dados

### 🔄 Atualizar Configurações

**Edite o arquivo `.env`:**
```env
DB_HOST=localhost
DB_NAME=dashboard_baker
DB_USER=postgres
DB_PASSWORD=sua_nova_senha
DB_PORT=5432
```

---

## 💡 Exemplos Práticos

### 🎯 Exemplo 1: Inserir CTE via Formulário

```
1. Acesse: http://localhost:8501
2. Clique na aba "🗄️ Inserção no Banco"
3. Preencha:
   - Número CTE: 22350
   - Destinatário: EMPRESA EXEMPLO LTDA
   - Valor Total: 2500.00
   - Data Emissão: 01/08/2024
   - Placa Veículo: ABC-1234
4. Clique "🚀 Inserir CTE no Banco"
5. ✅ Sucesso!
```

### 📊 Exemplo 2: Analisar Dados CSV

```
1. Prepare seu arquivo CSV com colunas:
   - Número Cte
   - Destinatário - Nome
   - Total (valores em R$)
   - Data emissão Cte
   - Fatura
   - Data baixa

2. Na aba "📊 Dashboard Principal":
   - Upload do arquivo
   - Visualize métricas automáticas
   - Analise gráficos interativos

3. Observe variações de tempo:
   - Identifique gargalos
   - Melhore processos
```

### 🔄 Exemplo 3: Migrar Dados Existentes

```bash
# 1. Coloque seu CSV na pasta do sistema
# 2. Execute o comando de população
python popular_banco_postgresql.py

# 3. Acompanhe o processo:
✅ CSV carregado: arquivo.csv (encoding: cp1252)
✅ Dados processados: 1,234 registros
🔄 Inserindo dados no banco...
✅ 1,234 registros inseridos com sucesso
```

---

## 🚨 Solucionando Problemas

### ❌ Erro "titlefont"
**✅ JÁ CORRIGIDO** na versão atual do dashboard

### 🐘 PostgreSQL não conecta

```bash
# 1. Verificar se PostgreSQL está rodando
services.msc → PostgreSQL

# 2. Testar conexão manual
psql -h localhost -U postgres

# 3. Verificar configurações no .env
DB_HOST=localhost
DB_PASSWORD=sua_senha_correta
```

### 📦 Dependências faltando

```bash
# Reinstalar dependências
pip install -r requirements_postgresql.txt

# Ou individual
pip install streamlit pandas plotly psycopg2-binary
```

### 📄 CSV não carrega

**Formatos suportados:**
- ✅ Separador: `;` (ponto e vírgula)
- ✅ Encoding: `cp1252`, `utf-8`, `latin1`
- ✅ Valores: `R$ 1.500,00` (formato brasileiro)

### 🗄️ Tabela não existe

```python
# Execute o setup novamente
python setup_dashboard_postgresql.py

# Ou crie manualmente
python -c "
import psycopg2
conn = psycopg2.connect(host='localhost', user='postgres', password='sua_senha', database='dashboard_baker')
# ... criar tabela
"
```

---

## 📋 Workflows Recomendados

### 🎯 Workflow 1: Uso Diário

```
1. 🌅 Início do dia
   └── Acesse dashboard: http://localhost:8501

2. 📥 Recebeu novos CTEs?
   └── Use aba "Inserção no Banco"
   └── Preencha formulário
   └── Salve no PostgreSQL

3. 📊 Análise diária
   └── Aba "Dashboard Principal"
   └── Upload CSV atualizado
   └── Verifique métricas

4. 🎯 Fim do dia
   └── Export dados para backup
   └── Verifique CTEs em aberto
```

### 📈 Workflow 2: Análise Semanal

```
1. 📊 Consolidação
   └── Execute: python popular_banco_postgresql.py
   └── Importe todos CSVs da semana

2. 🔍 Análise de produtividade
   └── Verifique variações de tempo
   └── Identifique gargalos
   └── Compare com semana anterior

3. 📋 Relatórios
   └── Export dados do banco
   └── Gere relatórios para gestão
```

### 🔧 Workflow 3: Manutenção

```
1. 🧪 Testes mensais
   └── python teste_sistema_completo.py
   └── Verifique se tudo está OK

2. 💾 Backup
   └── pg_dump dashboard_baker > backup.sql
   └── Salve arquivos CSV

3. 🔄 Atualizações
   └── pip install --upgrade streamlit
   └── Verifique novas versões
```

---

## 🎓 Dicas Avançadas

### ⚡ Performance

```python
# Para grandes volumes de dados
# Use índices do PostgreSQL (já criados automaticamente)

# Configuração otimizada no .env
STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
STREAMLIT_SERVER_MAX_MESSAGE_SIZE=200
```

### 🔒 Segurança

```env
# Use senhas seguras no .env
DB_PASSWORD=SuaSenhaSegura123!@#

# Para produção, considere:
DB_HOST=servidor_dedicado
DB_USER=usuario_especifico
```

### 📊 Customização

```python
# Adicione suas próprias métricas no dashboard
# Edite: dashboard_baker_web_corrigido.py

def minha_metrica_customizada(df):
    # Sua lógica aqui
    return resultado
```

---

## 📞 Suporte

### 🆘 Problemas Comuns
- 📖 Consulte este guia primeiro
- 🧪 Execute `teste_sistema_completo.py`
- 📄 Verifique logs do terminal

### 🔧 Suporte Técnico
- 📧 **Email**: suporte@transpontual.com.br
- 📱 **WhatsApp**: (XX) XXXXX-XXXX
- 🌐 **Portal**: https://suporte.transpontual.com.br

### 💻 Desenvolvimento
- 🐛 **Reportar bugs**: Anexe `relatorio_testes_XXXXXXXX.txt`
- 💡 **Sugestões**: Descreva funcionalidade desejada
- 🔄 **Atualizações**: Verifique versões mais recentes

---

## 🎯 Resumo das Melhorias

### ✅ Correções Implementadas
- **🔧 Erro titlefont → title**: Plotly atualizado
- **🗄️ Nova aba PostgreSQL**: Inserção via formulário
- **📝 Interface completa**: Todos os campos do CSV
- **🔄 Integração total**: Sincronização entre CSV e banco

### 🆕 Novas Funcionalidades
- **💾 Persistência**: Dados salvos no PostgreSQL
- **📊 Visualização**: Tabelas interativas do banco
- **🧪 Testes**: Verificação automática do sistema
- **⚙️ Setup**: Instalação automática completa

### 🚀 Benefícios
- **⚡ Rapidez**: Interface web moderna
- **🔒 Segurança**: Dados no banco PostgreSQL
- **📈 Escalabilidade**: Suporta grandes volumes
- **🔧 Manutenibilidade**: Código organizado e documentado

---

*💰 Dashboard Baker - Sistema Financeiro Transpontual*  
*🎯 Guia Prático v2.0 - Tudo que você precisa saber*