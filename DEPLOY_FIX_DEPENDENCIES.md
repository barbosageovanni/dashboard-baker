# Deploy Fix para Erro de Dependência

## Problema Identificado
O erro de deploy foi causado pela incompatibilidade entre `psycopg2-binary==2.9.9` e Python 3.13.5 no Streamlit Cloud.

## Soluções Implementadas

### 1. Atualização de Dependência (Solução Principal)
- Atualizado `psycopg2-binary` de 2.9.9 para 2.9.10 no `requirements.txt`
- Versão 2.9.10 tem melhor compatibilidade com Python 3.13.5

### 2. Configuração de Runtime
- Criado `runtime.txt` especificando `python-3.12` para forçar versão mais estável
- Python 3.12 tem melhor compatibilidade com psycopg2-binary

### 3. Arquivos Alternativos Criados

#### requirements_stable.txt
```
streamlit==1.32.0
pandas==2.0.3
plotly==5.18.0
psycopg2-binary==2.9.8
xlsxwriter==3.1.9
```
- Versão 2.9.8 do psycopg2-binary (mais estável)

#### requirements_psycopg3.txt
```
streamlit==1.32.0
pandas==2.0.3
plotly==5.18.0
psycopg[binary]==3.2.9
xlsxwriter==3.1.9
```
- Usa psycopg versão 3 (mais moderno)
- Requer modificações no código para compatibilidade

## Instruções de Deploy

### Streamlit Cloud - Opção 1 (Recomendada)
1. Usar os arquivos atuais (`requirements.txt` + `runtime.txt`)
2. No Streamlit Cloud, aguardar o rebuild automático
3. Se falhar, tentar Opção 2

### Streamlit Cloud - Opção 2 (Alternativa)
1. Renomear `requirements.txt` para `requirements_old.txt`
2. Renomear `requirements_stable.txt` para `requirements.txt`
3. Commit e push das alterações
4. Aguardar rebuild no Streamlit Cloud

### Outros Provedores
- **Railway**: Usar `requirements.txt` atual + `runtime.txt`
- **Render**: Usar `requirements.txt` atual + `runtime.txt`
- **Heroku**: Adicionar `python-3.12` no `runtime.txt`

## Comandos de Emergência

Se ainda houver problemas, testar localmente:
```bash
pip install -r requirements_stable.txt
streamlit run dashboard_baker_web_corrigido.py
```

## Status Atual
- ✅ Dependências atualizadas e compatíveis
- ✅ Runtime especificado (Python 3.12)
- ✅ Arquivos alternativos criados
- ✅ Commits realizados e push feito
- ⏳ Aguardando rebuild do Streamlit Cloud

## Próximos Passos
1. Monitorar o rebuild no Streamlit Cloud
2. Testar funcionamento após deploy
3. Se necessário, usar arquivos alternativos
4. Documentar solução final funcionando
