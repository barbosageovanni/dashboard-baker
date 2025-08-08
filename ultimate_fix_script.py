#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT FINAL - Dashboard Baker v3.0
Diagnóstico + Instruções + Monitor + Verificação automática
"""

import requests
import time
import sys
import re
from datetime import datetime

class UltimateFixer:
    def __init__(self):
        self.url = "https://dashboard-transpontual.streamlit.app/"
        self.github_repo = "barbosageovanni/dashboard-baker"
        self.expected_indicators = [
            "Dashboard Financeiro Baker - Sistema Avançado",
            "Gestão Inteligente de Faturamento", 
            "PostgreSQL",
            "v3.0",
            "389"
        ]
    
    def print_header(self, title, icon="🎯"):
        """Imprime cabeçalho formatado"""
        print(f"\n{icon} {title}")
        print("=" * (len(title) + 4))
    
    def log(self, message, level="INFO"):
        """Log formatado"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "CRITICAL": "🚨"}
        print(f"[{timestamp}] {icons.get(level, 'ℹ️')} {message}")
    
    def diagnose_current_app(self):
        """Diagnóstico detalhado da app atual"""
        self.print_header("DIAGNÓSTICO DA APP ATUAL", "🔍")
        
        try:
            response = requests.get(self.url, timeout=30)
            content = response.text
            
            self.log(f"Status HTTP: {response.status_code}", "SUCCESS" if response.status_code == 200 else "ERROR")
            self.log(f"Tamanho do conteúdo: {len(content):,} caracteres", "INFO")
            
            # Contar indicadores da versão nova
            found_indicators = []
            for indicator in self.expected_indicators:
                if indicator in content:
                    found_indicators.append(indicator)
            
            score = len(found_indicators)
            total = len(self.expected_indicators)
            
            self.log(f"Indicadores da v3.0 encontrados: {score}/{total}", 
                    "SUCCESS" if score >= 4 else "WARNING" if score >= 2 else "ERROR")
            
            # Mostrar detalhes
            for indicator in self.expected_indicators:
                status = "✅" if indicator in content else "❌"
                print(f"   {status} {indicator}")
            
            return score, total, content
            
        except Exception as e:
            self.log(f"Erro ao acessar app: {e}", "ERROR")
            return 0, len(self.expected_indicators), ""
    
    def show_streamlit_instructions(self):
        """Mostra instruções específicas para Streamlit Cloud"""
        self.print_header("INSTRUÇÕES STREAMLIT CLOUD", "📱")
        
        instructions = """
🚨 SUA APP ESTÁ USANDO VERSÃO ANTIGA - AÇÃO NECESSÁRIA:

📍 ACESSE: https://share.streamlit.io/

🗑️ DELETAR APP ATUAL:
   1. Encontre: "dashboard-transpontual"
   2. Clique nos 3 pontinhos (⋯)
   3. Escolha "Delete app"
   4. Confirme a exclusão

➕ CRIAR APP NOVA:
   5. Clique "New app"
   6. Repository: barbosageovanni/dashboard-baker
   7. Branch: main
   8. Main file: dashboard_baker_web_corrigido.py
   9. App URL: dashboard-transpontual

🔑 CONFIGURAR SECRETS:
   10. Settings > Secrets
   11. Cole EXATAMENTE:

PGHOST = "db.lijtncazuwnbydeqtoyz.supabase.co"
PGDATABASE = "postgres"
PGUSER = "postgres" 
PGPASSWORD = "SEQAg17334"
PGPORT = "5432"

⏳ AGUARDAR: 3-8 minutos para deploy completo
        """
        
        print(instructions)
        
        # Salvar instruções em arquivo
        with open("STREAMLIT_INSTRUCTIONS.txt", "w", encoding="utf-8") as f:
            f.write(instructions)
        
        self.log("Instruções salvas em: STREAMLIT_INSTRUCTIONS.txt", "SUCCESS")
    
    def monitor_until_success(self, max_minutes=15):
        """Monitora até sucesso ou timeout"""
        self.print_header(f"MONITORAMENTO POR {max_minutes} MINUTOS", "🔄")
        
        start_time = time.time()
        attempt = 1
        
        while time.time() - start_time < (max_minutes * 60):
            elapsed_min = int((time.time() - start_time) / 60)
            
            self.log(f"Tentativa {attempt} ({elapsed_min}min decorridos)", "INFO")
            
            score, total, content = self.diagnose_current_app()
            
            if score >= 4:
                self.log("🎉 SUCESSO! App atualizada detectada!", "SUCCESS")
                self.log(f"Dashboard funcionando: {self.url}", "SUCCESS") 
                return True
            elif score >= 2:
                self.log("Deploy parcial - aguardando conclusão...", "WARNING")
            elif score == 0:
                self.log("Versão antiga ainda ativa", "ERROR")
                if attempt <= 3:
                    self.log("💡 Se ainda não fez: DELETE e RECRIE a app!", "WARNING")
            
            # Esperar mais tempo entre tentativas conforme progresso
            wait_seconds = 60 if score >= 2 else 90
            self.log(f"Aguardando {wait_seconds}s para próxima verificação...", "INFO")
            time.sleep(wait_seconds)
            attempt += 1
        
        # Timeout
        self.log("⏰ TIMEOUT - App não atualizou no tempo esperado", "ERROR")
        return False
    
    def run_complete_flow(self):
        """Executa o fluxo completo"""
        self.print_header("DASHBOARD BAKER v3.0 - CORREÇÃO FINAL", "🚀")
        
        print(f"🌐 URL da app: {self.url}")
        print(f"📁 Repository: {self.github_repo}")
        print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. Diagnóstico inicial
        initial_score, total, _ = self.diagnose_current_app()
        
        # 2. Decidir ação baseada no score
        if initial_score >= 4:
            self.log("🎉 APP JÁ ESTÁ ATUALIZADA!", "SUCCESS")
            self.log("Sistema funcionando corretamente", "SUCCESS")
            return True
        
        elif initial_score >= 2:
            self.log("Deploy parcial detectado - monitorando...", "WARNING")
            return self.monitor_until_success(10)
        
        else:
            self.log("🚨 APP USANDO VERSÃO ANTIGA", "CRITICAL")
            self.show_streamlit_instructions()
            
            # Perguntar se quer monitorar
            print("\n" + "="*50)
            print("🤔 PRÓXIMOS PASSOS:")
            print("A. Execute as instruções acima no Streamlit Cloud")
            print("B. Depois execute novamente este script para monitorar")
            print("OU")
            print("C. Digite 'monitor' para monitorar agora (se já fez os passos)")
            
            choice = input("\nDigite 'monitor' para monitorar ou Enter para sair: ").strip().lower()
            
            if choice == 'monitor':
                print("\n🔄 Iniciando monitoramento...")
                return self.monitor_until_success(15)
            else:
                print("\n💡 Execute as instruções e rode o script novamente!")
                return False
    
    def quick_check(self):
        """Verificação rápida"""
        self.print_header("VERIFICAÇÃO RÁPIDA", "⚡")
        
        score, total, _ = self.diagnose_current_app()
        
        if score >= 4:
            self.log("🎉 SISTEMA 100% FUNCIONAL!", "SUCCESS")
            return True
        elif score >= 2:
            self.log("Sistema parcialmente atualizado", "WARNING")
            return False
        else:
            self.log("Sistema precisa de atualização", "ERROR")
            return False

def main():
    """Função principal"""
    fixer = UltimateFixer()
    
    print("🎯 ULTIMATE FIX SCRIPT - Dashboard Baker v3.0")
    print("Modo de uso:")
    print("  python ultimate_fix_script.py           # Fluxo completo")
    print("  python ultimate_fix_script.py --quick   # Verificação rápida")
    print("  python ultimate_fix_script.py --monitor # Apenas monitorar")
    print()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--quick':
            success = fixer.quick_check()
            return 0 if success else 1
        elif sys.argv[1] == '--monitor':
            success = fixer.monitor_until_success(15)
            return 0 if success else 1
    
    # Fluxo completo
    success = fixer.run_complete_flow()
    
    # Resultado final
    if success:
        print("\n" + "="*60)
        print("🎉 MISSÃO CUMPRIDA!")
        print("✅ Dashboard Baker v3.0 está 100% funcional")
        print(f"🌐 Acesse: {fixer.url}")
        print("📊 Sistema pronto para uso em produção")
        print("="*60)
        return 0
    else:
        print("\n" + "="*60)
        print("⚠️ AÇÃO MANUAL NECESSÁRIA")
        print("🔧 Execute as instruções no Streamlit Cloud")
        print("📱 Depois rode: python ultimate_fix_script.py --monitor")
        print("="*60)
        return 1

if __name__ == "__main__":
    sys.exit(main())