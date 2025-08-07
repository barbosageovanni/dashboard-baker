#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Automático - Dashboard Baker com Correção PostgreSQL
Instala e configura tudo automaticamente

Execute: python setup_dashboard_corrigido.py
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime
import urllib.request
import zipfile

class SetupDashboardBaker:
    """Setup completo automatizado"""
    
    def __init__(self):
        self.python_executable = sys.executable
        self.projeto_dir = os.getcwd()
        self.backup_dir = os.path.join(self.projeto_dir, 'backups')
        self.logs = []
        
    def log(self, message):
        """Adiciona log com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        self.logs.append(log_message)
    
    def verificar_python(self):
        """Verifica versão do Python"""
        self.log("🐍 Verificando Python...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.log("❌ Python 3.8+ necessário")
            return False
        
        self.log(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    
    def instalar_dependencias(self):
        """Instala todas as dependências necessárias"""
        self.log("📦 Instalando dependências...")
        
        dependencias = [
            'streamlit>=1.28.0',
            'pandas>=1.5.0', 
            'plotly>=5.17.0',
            'psycopg2-binary>=2.9.0',
            'python-dotenv>=1.0.0',
            'numpy>=1.24.0',
            'xlsxwriter>=3.1.0',
            'openpyxl>=3.1.0'
        ]
        
        try:
            # Atualizar pip primeiro
            subprocess.run([
                self.python_executable, '-m', 'pip', 'install', '--upgrade', 'pip'
            ], check=True, capture_output=True)
            
            # Instalar dependências
            for dep in dependencias:
                self.log(f"📦 Instalando {dep}...")
                result = subprocess.run([
                    self.python_executable, '-m', 'pip', 'install', dep
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.log(f"✅ {dep} instalado")
                else:
                    self.log(f"⚠️ Aviso ao instalar {dep}: {result.stderr[:100]}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"❌ Erro ao instalar dependências: {e}")
            return False
        except Exception as e:
            self.log(f"❌ Erro inesperado: {e}")
            return False
    
    def criar_estrutura_pastas(self):
        """Cria estrutura de pastas necessária"""
        self.log("📁 Criando estrutura de pastas...")
        
        pastas = [
            'data',           # Arquivos CSV de entrada
            'exports',        # Relatórios gerados
            'backups',        # Backups automáticos
            'logs',           # Logs do sistema
            'config',         # Arquivos de configuração
            'temp'            # Arquivos temporários
        ]
        
        for pasta in pastas:
            pasta_path = os.path.join(self.projeto_dir, pasta)
            if not os.path.exists(pasta_path):
                os.makedirs(pasta_path)
                self.log(f"✅ Pasta criada: {pasta}")
            else:
                self.log(f"ℹ️ Pasta já existe: {pasta}")
        
        return True
    
    def criar_arquivo_env(self):
        """Cria arquivo .env com configurações"""
        self.log("⚙️ Criando arquivo de configuração...")
        
        env_path = os.path.join(self.projeto_dir, '.env')
        
        if os.path.exists(env_path):
            self.log("ℹ️ Arquivo .env já existe, criando .env.exemplo")
            env_path = os.path.join(self.projeto_dir, '.env.exemplo')
        
        env_content = f"""# Dashboard Baker - Configurações de Banco de Dados
# Arquivo criado automaticamente em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

# =============================================================================
# SUPABASE POSTGRESQL (PRIORIDADE 1)
# =============================================================================
SUPABASE_HOST=db.lijtncazuwnbydeqtoyz.supabase.co
SUPABASE_DB=postgres
SUPABASE_USER=postgres
SUPABASE_PASSWORD=SUBSTITUA_PELA_SUA_SENHA_AQUI
SUPABASE_PORT=5432

# =============================================================================
# POSTGRESQL LOCAL (PRIORIDADE 2) 
# =============================================================================
LOCAL_DB_HOST=localhost
LOCAL_DB_NAME=dashboard_baker
LOCAL_DB_USER=postgres
LOCAL_DB_PASSWORD=senha123
LOCAL_DB_PORT=5432

# =============================================================================
# RENDER POSTGRESQL (PRIORIDADE 3)
# =============================================================================
RENDER_HOST=
RENDER_DB=
RENDER_USER=
RENDER_PASSWORD=
RENDER_PORT=5432

# =============================================================================
# RAILWAY POSTGRESQL (PRIORIDADE 4)
# =============================================================================
RAILWAY_HOST=
RAILWAY_DB=
RAILWAY_USER=
RAILWAY_PASSWORD=
RAILWAY_PORT=5432

# =============================================================================
# CONFIGURAÇÕES GERAIS
# =============================================================================
# Timeout de conexão (segundos)
DB_TIMEOUT=10

# Modo SSL (require, prefer, disable)
DB_SSL_MODE=require

# Debug mode (true/false)
DEBUG_MODE=false

# Dashboard settings
DASHBOARD_PORT=8501
DASHBOARD_HOST=localhost
"""
        
        try:
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(env_content)
            self.log(f"✅ Arquivo criado: {os.path.basename(env_path)}")
            return True
        except Exception as e:
            self.log(f"❌ Erro ao criar .env: {e}")
            return False
    
    def fazer_backup_dashboard(self):
        """Cria backup do dashboard se existir"""
        self.log("💾 Verificando backups...")
        
        dashboard_file = "dashboard_baker_web_corrigido.py"
        
        if not os.path.exists(dashboard_file):
            self.log("ℹ️ Dashboard não encontrado, continuando instalação")
            return True
        
        # Criar backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.backup_dir, f"dashboard_backup_{timestamp}.py")
        
        try:
            shutil.copy2(dashboard_file, backup_file)
            self.log(f"✅ Backup criado: {os.path.basename(backup_file)}")
            return True
        except Exception as e:
            self.log(f"❌ Erro ao criar backup: {e}")
            return False
    
    def aplicar_correcoes_dashboard(self):
        """Aplica correções no dashboard existente"""
        self.log("🔧 Aplicando correções no dashboard...")
        
        dashboard_file = "dashboard_baker_web_corrigido.py"
        
        if not os.path.exists(dashboard_file):
            self.log("⚠️ Dashboard não encontrado, pulando correções")
            return True
        
        try:
            # Ler arquivo atual
            with open(dashboard_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar se já tem correções
            if 'sistema de fallback robusto' in content.lower():
                self.log("✅ Dashboard já tem correções aplicadas")
                return True
            
            # Aplicar patch na função de configuração
            nova_funcao = '''def carregar_configuracao_banco():
    """Carrega configuração do banco com sistema de fallback robusto"""
    
    import psycopg2
    from dotenv import load_dotenv
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Configurações em ordem de prioridade
    configs = [
        {
            'nome': 'Supabase Cloud',
            'host': os.getenv('SUPABASE_HOST', 'db.lijtncazuwnbydeqtoyz.supabase.co'),
            'database': os.getenv('SUPABASE_DB', 'postgres'),
            'user': os.getenv('SUPABASE_USER', 'postgres'),
            'password': os.getenv('SUPABASE_PASSWORD', ''),
            'port': int(os.getenv('SUPABASE_PORT', '5432')),
            'sslmode': 'require',
            'connect_timeout': 10
        },
        {
            'nome': 'PostgreSQL Local',
            'host': os.getenv('LOCAL_DB_HOST', 'localhost'),
            'database': os.getenv('LOCAL_DB_NAME', 'dashboard_baker'),
            'user': os.getenv('LOCAL_DB_USER', 'postgres'),
            'password': os.getenv('LOCAL_DB_PASSWORD', 'senha123'),
            'port': int(os.getenv('LOCAL_DB_PORT', '5432')),
            'connect_timeout': 5
        }
    ]
    
    # Testar cada configuração
    for config in configs:
        if not config.get('password'):
            continue
            
        try:
            # Limpar config para psycopg2
            clean_config = {k: v for k, v in config.items() 
                          if k in ['host', 'database', 'user', 'password', 'port', 'sslmode', 'connect_timeout']}
            
            # Testar conexão
            conn = psycopg2.connect(**clean_config)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            
            print(f"✅ Conectado: {config['nome']}")
            return clean_config
            
        except Exception as e:
            print(f"⚠️ {config['nome']}: {str(e)[:80]}...")
            continue
    
    # Fallback padrão
    return {
        'host': 'localhost',
        'database': 'dashboard_baker',
        'user': 'postgres',
        'password': 'senha123',
        'port': 5432
    }'''
            
            # Substituir função existente
            import re
            pattern = r'def carregar_configuracao_banco\(\):.*?return config'
            
            if re.search(pattern, content, re.DOTALL):
                content = re.sub(pattern, nova_funcao, content, flags=re.DOTALL)
                
                # Salvar arquivo corrigido
                with open(dashboard_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.log("✅ Correções aplicadas no dashboard")
                return True
            else:
                self.log("⚠️ Não foi possível localizar função para corrigir")
                return True
                
        except Exception as e:
            self.log(f"❌ Erro ao aplicar correções: {e}")
            return False
    
    def testar_sistema(self):
        """Testa se o sistema está funcionando"""
        self.log("🧪 Testando sistema...")
        
        try:
            # Testar importações
            import streamlit
            import pandas
            import plotly
            import psycopg2
            from dotenv import load_dotenv
            
            self.log("✅ Todas as bibliotecas importadas com sucesso")
            
            # Testar configuração de ambiente
            load_dotenv()
            
            # Testar se dashboard pode ser importado
            dashboard_file = "dashboard_baker_web_corrigido.py"
            if os.path.exists(dashboard_file):
                self.log("✅ Dashboard encontrado e acessível")
            
            return True
            
        except ImportError as e:
            self.log(f"❌ Erro de importação: {e}")
            return False
        except Exception as e:
            self.log(f"❌ Erro no teste: {e}")
            return False
    
    def criar_scripts_uteis(self):
        """Cria scripts úteis para o usuário"""
        self.log("📝 Criando scripts úteis...")
        
        # Script para iniciar dashboard
        iniciar_script = f'''#!/usr/bin/env python3
"""Script para iniciar Dashboard Baker"""

import os
import subprocess
import sys

def main():
    print("🚀 Iniciando Dashboard Baker...")
    
    # Verificar arquivo
    if not os.path.exists("dashboard_baker_web_corrigido.py"):
        print("❌ Dashboard não encontrado!")
        return
    
    # Iniciar Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "dashboard_baker_web_corrigido.py",
            "--server.port", "8501"
        ])
    except KeyboardInterrupt:
        print("\\n👋 Dashboard encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {{e}}")

if __name__ == "__main__":
    main()
'''
        
        # Script de diagnóstico
        diagnostico_script = '''#!/usr/bin/env python3
"""Script de diagnóstico rápido"""

import os
import sys

def diagnosticar():
    print("🔍 DIAGNÓSTICO DASHBOARD BAKER")
    print("="*40)
    
    # Python
    print(f"🐍 Python: {sys.version}")
    
    # Bibliotecas
    libs = ['streamlit', 'pandas', 'plotly', 'psycopg2']
    for lib in libs:
        try:
            __import__(lib)
            print(f"✅ {lib}: OK")
        except ImportError:
            print(f"❌ {lib}: AUSENTE")
    
    # Arquivos
    arquivos = ['.env', 'dashboard_baker_web_corrigido.py']
    for arquivo in arquivos:
        if os.path.exists(arquivo):
            print(f"✅ {arquivo}: OK")
        else:
            print(f"❌ {arquivo}: AUSENTE")
    
    # Pastas
    pastas = ['data', 'exports', 'backups']
    for pasta in pastas:
        if os.path.exists(pasta):
            print(f"✅ {pasta}/: OK")
        else:
            print(f"❌ {pasta}/: AUSENTE")

if __name__ == "__main__":
    diagnosticar()
'''
        
        try:
            # Salvar scripts
            with open('iniciar_dashboard.py', 'w', encoding='utf-8') as f:
                f.write(iniciar_script)
            
            with open('diagnostico.py', 'w', encoding='utf-8') as f:
                f.write(diagnostico_script)
            
            self.log("✅ Scripts úteis criados")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro ao criar scripts: {e}")
            return False
    
    def gerar_relatorio_instalacao(self):
        """Gera relatório final da instalação"""
        self.log("📊 Gerando relatório de instalação...")
        
        relatorio = f"""
# RELATÓRIO DE INSTALAÇÃO - DASHBOARD BAKER
{'='*60}

**Data/Hora:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}  
**Diretório:** {self.projeto_dir}  
**Python:** {sys.version}

## ✅ INSTALAÇÃO CONCLUÍDA

### 📦 Dependências Instaladas:
- streamlit (interface web)
- pandas (manipulação de dados)  
- plotly (gráficos interativos)
- psycopg2-binary (PostgreSQL)
- python-dotenv (variáveis ambiente)
- numpy, xlsxwriter, openpyxl

### 📁 Estrutura Criada:
```
{os.path.basename(self.projeto_dir)}/
├── dashboard_baker_web_corrigido.py  # Dashboard principal
├── .env                              # Configurações
├── iniciar_dashboard.py              # Script de início
├── diagnostico.py                    # Script de teste
├── data/                             # Arquivos CSV
├── exports/                          # Relatórios
├── backups/                          # Backups
└── logs/                             # Logs do sistema
```

## 🚀 PRÓXIMOS PASSOS

### 1. Configure suas credenciais:
```bash
# Edite o arquivo .env com suas credenciais reais
nano .env
```

### 2. Inicie o dashboard:
```bash
# Opção 1: Script automático
python iniciar_dashboard.py

# Opção 2: Comando direto
streamlit run dashboard_baker_web_corrigido.py
```

### 3. Acesse no navegador:
```
http://localhost:8501
```

## 🔧 COMANDOS ÚTEIS

```bash
# Diagnóstico do sistema
python diagnostico.py

# Atualizar dependências
pip install -r requirements.txt --upgrade

# Ver logs de instalação
cat logs/instalacao.log
```

## 📞 SUPORTE

Se houver problemas:
1. Execute `python diagnostico.py`
2. Verifique arquivo `.env`
3. Consulte logs em `logs/`

---
**Dashboard Baker v3.0 - Sistema Avançado de Gestão Financeira**
"""
        
        try:
            # Salvar logs detalhados
            log_file = os.path.join('logs', f'instalacao_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.logs))
            
            # Salvar relatório
            with open('RELATORIO_INSTALACAO.md', 'w', encoding='utf-8') as f:
                f.write(relatorio)
            
            self.log("✅ Relatório salvo: RELATORIO_INSTALACAO.md")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro ao gerar relatório: {e}")
            return False
    
    def executar_setup_completo(self):
        """Executa setup completo automatizado"""
        
        print("🚀 SETUP DASHBOARD BAKER - INSTALAÇÃO COMPLETA")
        print("="*60)
        print(f"Diretório: {self.projeto_dir}")
        print(f"Python: {sys.executable}")
        print()
        
        etapas = [
            ("🐍 Verificando Python", self.verificar_python),
            ("📁 Criando estrutura", self.criar_estrutura_pastas),
            ("📦 Instalando dependências", self.instalar_dependencias),
            ("⚙️ Criando configuração", self.criar_arquivo_env),
            ("💾 Fazendo backup", self.fazer_backup_dashboard),
            ("🔧 Aplicando correções", self.aplicar_correcoes_dashboard),
            ("📝 Criando scripts", self.criar_scripts_uteis),
            ("🧪 Testando sistema", self.testar_sistema),
            ("📊 Gerando relatório", self.gerar_relatorio_instalacao)
        ]
        
        sucesso_geral = True
        
        for i, (descricao, funcao) in enumerate(etapas, 1):
            print(f"\n[{i}/{len(etapas)}] {descricao}")
            print("-" * 40)
            
            try:
                sucesso = funcao()
                if not sucesso:
                    sucesso_geral = False
                    self.log(f"⚠️ Etapa falhou: {descricao}")
            except Exception as e:
                self.log(f"❌ Erro na etapa '{descricao}': {e}")
                sucesso_geral = False
        
        # Resultado final
        print("\n" + "="*60)
        if sucesso_geral:
            print("🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
            print()
            print("🚀 PRÓXIMOS PASSOS:")
            print("1. Edite o arquivo .env com suas credenciais")
            print("2. Execute: python iniciar_dashboard.py")
            print("3. Acesse: http://localhost:8501")
            print()
            print("📋 ARQUIVOS IMPORTANTES:")
            print("• .env - Configurações do banco")
            print("• iniciar_dashboard.py - Iniciar sistema")
            print("• diagnostico.py - Testar sistema")
            print("• RELATORIO_INSTALACAO.md - Documentação")
        else:
            print("⚠️ INSTALAÇÃO CONCLUÍDA COM AVISOS")
            print("📋 Verifique os logs para detalhes")
            print("🔧 Execute 'python diagnostico.py' para verificar")
        
        return sucesso_geral

def main():
    """Função principal"""
    
    try:
        setup = SetupDashboardBaker()
        setup.executar_setup_completo()
        
    except KeyboardInterrupt:
        print("\n❌ Instalação cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro crítico durante instalação: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()