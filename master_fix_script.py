#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT MESTRE - Dashboard Baker v3.0
Resolve TODOS os problemas de sincronização e deploy
"""

import os
import sys
import subprocess
import time
import requests
from datetime import datetime

class MasterFixer:
    def __init__(self):
        self.issues_found = []
        self.fixes_applied = []
        self.github_repo = "barbosageovanni/dashboard-baker"
        self.streamlit_url = "https://dashboard-transpontual.streamlit.app/"
    
    def log(self, message, level="INFO"):
        """Log formatado com timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        icons = {
            "INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️",
            "ERROR": "❌", "ACTION": "🔧", "CRITICAL": "🚨"
        }
        print(f"[{timestamp}] {icons.get(level, 'ℹ️')} {message}")
    
    def check_environment(self):
        """Detecta se está rodando no Codespace ou localmente"""
        self.log("🔍 Detectando ambiente...", "ACTION")
        
        is_codespace = os.getenv('CODESPACES') == 'true'
        codespace_name = os.getenv('CODESPACE_NAME', 'N/A')
        
        if is_codespace:
            self.log(f"🌐 Executando no GitHub Codespace: {codespace_name}", "INFO")
        else:
            self.log("💻 Executando localmente", "INFO")
            
        return is_codespace
    
    def sync_with_github(self):
        """Sincroniza alterações com GitHub"""
        self.log("🔄 Sincronizando com GitHub...", "ACTION")
        
        try:
            # Pull latest changes
            result = subprocess.run(['git', 'pull', 'origin', 'main'], 
                                   capture_output=True, text=True, check=True)
            self.log("✅ Pull realizado com sucesso", "SUCCESS")
            
            # Check for local changes
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                   capture_output=True, text=True, check=True)
            
            if result.stdout.strip():
                self.log("📝 Alterações locais encontradas", "WARNING")
                
                # Add, commit and push
                subprocess.run(['git', 'add', '.'], check=True)
                commit_msg = f"🔄 Sync automático {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
                subprocess.run(['git', 'push', 'origin', 'main'], check=True)
                
                self.log("✅ Alterações enviadas para GitHub", "SUCCESS")
                self.fixes_applied.append("Git sincronizado")
            else:
                self.log("✅ Nenhuma alteração local pendente", "SUCCESS")
                
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"❌ Erro na sincronização: {e}", "ERROR")
            self.issues_found.append("Erro de sincronização Git")
            return False
    
    def verify_files(self):
        """Verifica arquivos essenciais"""
        self.log("📁 Verificando arquivos essenciais...", "ACTION")
        
        essential_files = {
            'dashboard_baker_web_corrigido.py': 'Arquivo principal do dashboard',
            'requirements.txt': 'Dependências Python',
            'system_check.py': 'Script de verificação'
        }
        
        all_files_ok = True
        
        for filename, description in essential_files.items():
            if os.path.exists(filename):
                size = os.path.getsize(filename) / 1024
                self.log(f"✅ {filename}: {size:.1f} KB", "SUCCESS")
            else:
                self.log(f"❌ {filename}: AUSENTE ({description})", "ERROR")
                self.issues_found.append(f"Arquivo {filename} ausente")
                all_files_ok = False
        
        return all_files_ok
    
    def test_supabase_connection(self):
        """Testa conexão Supabase com configurações locais"""
        self.log("🐘 Testando configuração Supabase...", "ACTION")
        
        # Verificar se .env existe
        if not os.path.exists('.env'):
            self.log("⚠️ Arquivo .env não encontrado - criando template", "WARNING")
            self.create_env_template()
            self.issues_found.append("Arquivo .env ausente")
            return False
        
        # Carregar .env
        self.load_env_file()
        
        # Verificar configurações obrigatórias
        required_vars = ['PGHOST', 'PGPASSWORD']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.log(f"❌ Variáveis ausentes no .env: {', '.join(missing_vars)}", "ERROR")
            self.issues_found.append("Configurações Supabase incompletas")
            return False
        
        try:
            import psycopg2
            
            config = {
                'host': os.getenv('PGHOST'),
                'database': os.getenv('PGDATABASE', 'postgres'),
                'user': os.getenv('PGUSER', 'postgres'),
                'password': os.getenv('PGPASSWORD'),
                'port': int(os.getenv('PGPORT', '5432')),
                'sslmode': 'require',
                'connect_timeout': 10
            }
            
            conn = psycopg2.connect(**config)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            
            self.log("✅ Conexão Supabase OK", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro Supabase: {str(e)[:50]}...", "ERROR")
            self.issues_found.append("Problemas de conexão Supabase")
            return False
    
    def check_streamlit_app(self):
        """Verifica status da app no Streamlit Cloud"""
        self.log("🌐 Verificando Streamlit Cloud...", "ACTION")
        
        try:
            response = requests.get(self.streamlit_url, timeout=30)
            
            if response.status_code == 200:
                self.log("✅ App Streamlit respondendo", "SUCCESS")
                
                # Verificar se o conteúdo está atualizado
                content = response.text
                if "Dashboard Financeiro Baker" in content:
                    self.log("✅ Conteúdo do dashboard detectado", "SUCCESS")
                    return True
                else:
                    self.log("⚠️ Conteúdo pode estar desatualizado", "WARNING")
                    self.issues_found.append("App Streamlit com conteúdo desatualizado")
                    return False
            else:
                self.log(f"❌ App retornou HTTP {response.status_code}", "ERROR")
                self.issues_found.append("App Streamlit não está respondendo")
                return False
                
        except requests.RequestException as e:
            self.log(f"❌ Erro ao acessar app: {str(e)[:50]}...", "ERROR")
            self.issues_found.append("Não foi possível acessar app Streamlit")
            return False
    
    def create_env_template(self):
        """Cria template .env"""
        template = """# Dashboard Baker - Configuração Supabase
PGHOST=db.xxxxx.supabase.co
PGDATABASE=postgres
PGUSER=postgres
PGPASSWORD=sua-senha-supabase
PGPORT=5432

SUPABASE_HOST=db.xxxxx.supabase.co
SUPABASE_DB=postgres
SUPABASE_USER=postgres
SUPABASE_PASSWORD=sua-senha-supabase
SUPABASE_PORT=5432
"""
        
        try:
            with open('.env', 'w', encoding='utf-8') as f:
                f.write(template)
            self.log("✅ Template .env criado", "SUCCESS")
            self.fixes_applied.append("Template .env criado")
        except Exception as e:
            self.log(f"❌ Erro ao criar .env: {e}", "ERROR")
    
    def load_env_file(self):
        """Carrega arquivo .env"""
        if os.path.exists('.env'):
            with open('.env', 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
    
    def generate_instructions(self):
        """Gera instruções finais"""
        instructions = f"""
🎯 PRÓXIMOS PASSOS MANUAIS - STREAMLIT CLOUD:

1. 🌐 Acesse: https://share.streamlit.io/
2. 🔍 Encontre sua app: dashboard-transpontual
3. ⚙️ Vá em Settings

4. 🔧 Verificar configurações:
   Repository: {self.github_repo}
   Branch: main
   Main file: dashboard_baker_web_corrigido.py

5. 🔑 Na seção Secrets, adicionar:
   PGHOST = "db.sua-url-supabase.supabase.co"
   PGDATABASE = "postgres"
   PGUSER = "postgres"
   PGPASSWORD = "sua-senha-supabase"
   PGPORT = "5432"

6. 🔄 Clicar em "Reboot app"

7. ⏳ Aguardar deploy completo

8. ✅ Testar: {self.streamlit_url}

💡 Se não funcionar: DELETE a app e RECRIE com as configurações acima.
"""
        
        print(instructions)
        
        # Salvar instruções
        with open('STREAMLIT_DEPLOY_INSTRUCTIONS.md', 'w', encoding='utf-8') as f:
            f.write(instructions)
        
        self.log("📋 Instruções salvas em STREAMLIT_DEPLOY_INSTRUCTIONS.md", "SUCCESS")
    
    def run_complete_diagnosis(self):
        """Executa diagnóstico e correções completas"""
        self.log("🚀 DASHBOARD BAKER v3.0 - DIAGNÓSTICO COMPLETO", "INFO")
        self.log("=" * 80, "INFO")
        
        # 1. Detectar ambiente
        is_codespace = self.check_environment()
        
        # 2. Sincronizar com GitHub
        self.log("\n🔄 FASE 1: SINCRONIZAÇÃO GITHUB", "ACTION")
        git_ok = self.sync_with_github()
        
        # 3. Verificar arquivos
        self.log("\n📁 FASE 2: VERIFICAÇÃO DE ARQUIVOS", "ACTION")
        files_ok = self.verify_files()
        
        # 4. Testar Supabase
        self.log("\n🐘 FASE 3: CONFIGURAÇÃO SUPABASE", "ACTION")
        supabase_ok = self.test_supabase_connection()
        
        # 5. Verificar Streamlit Cloud
        self.log("\n🌐 FASE 4: STREAMLIT CLOUD", "ACTION")
        streamlit_ok = self.check_streamlit_app()
        
        # 6. Gerar relatório final
        self.log("\n📊 RELATÓRIO FINAL", "INFO")
        self.log("=" * 50, "INFO")
        
        total_checks = 4
        passed_checks = sum([git_ok, files_ok, supabase_ok, streamlit_ok])
        
        results = {
            "Git/GitHub Sync": "✅" if git_ok else "❌",
            "Arquivos Essenciais": "✅" if files_ok else "❌", 
            "Supabase Config": "✅" if supabase_ok else "❌",
            "Streamlit Cloud": "✅" if streamlit_ok else "❌"
        }
        
        for check, status in results.items():
            self.log(f"{check}: {status}", "INFO")
        
        self.log(f"\n🎯 RESULTADO: {passed_checks}/{total_checks} verificações OK", "INFO")
        
        # Status final e ações
        if passed_checks == total_checks:
            self.log("\n🎉 SISTEMA 100% FUNCIONAL!", "SUCCESS")
            self.log(f"✅ Dashboard online: {self.streamlit_url}", "SUCCESS")
        elif passed_checks >= 3:
            self.log("\n⚠️ SISTEMA QUASE PRONTO - Ações manuais necessárias", "WARNING")
            self.generate_instructions()
        else:
            self.log("\n❌ PROBLEMAS CRÍTICOS ENCONTRADOS", "CRITICAL")
            self.log("🔧 Corrija os problemas e execute novamente", "ACTION")
        
        # Mostrar problemas e correções
        if self.issues_found:
            self.log(f"\n🚨 PROBLEMAS ({len(self.issues_found)}):", "WARNING")
            for issue in self.issues_found:
                self.log(f"  • {issue}", "WARNING")
        
        if self.fixes_applied:
            self.log(f"\n✅ CORREÇÕES APLICADAS ({len(self.fixes_applied)}):", "SUCCESS")
            for fix in self.fixes_applied:
                self.log(f"  • {fix}", "SUCCESS")
        
        return passed_checks >= 3

def main():
    """Função principal"""
    fixer = MasterFixer()
    success = fixer.run_complete_diagnosis()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())