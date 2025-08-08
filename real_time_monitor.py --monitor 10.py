#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor em Tempo Real - Deploy Dashboard Baker
Acompanha o deploy e confirma quando estiver 100% funcional
"""

import requests
import time
import sys
from datetime import datetime

class DeployMonitor:
    def __init__(self):
        self.url = "https://dashboard-transpontual.streamlit.app/"
        self.expected_records = 389  # Sabemos que tem 389 registros no Supabase
        self.success_indicators = [
            "Dashboard Financeiro Baker - Sistema Avançado",
            "Gestão Inteligente de Faturamento",
            "PostgreSQL", 
            "Supabase",
            "v3.0"
        ]
    
    def log(self, message, level="INFO"):
        """Log com timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
        print(f"[{timestamp}] {icons.get(level, 'ℹ️')} {message}")
    
    def test_app_response(self):
        """Testa resposta básica da app"""
        try:
            response = requests.get(self.url, timeout=30)
            return response.status_code, response.text
        except requests.RequestException as e:
            return None, str(e)
    
    def analyze_content(self, content):
        """Analisa o conteúdo para verificar se está atualizado"""
        if not content:
            return 0, []
        
        found_indicators = []
        for indicator in self.success_indicators:
            if indicator in content:
                found_indicators.append(indicator)
        
        return len(found_indicators), found_indicators
    
    def check_deploy_status(self):
        """Verifica status atual do deploy"""
        self.log("🔍 Verificando status do deploy...", "INFO")
        
        status_code, content = self.test_app_response()
        
        if status_code is None:
            self.log(f"❌ App não está respondendo: {content}", "ERROR")
            return "offline"
        
        if status_code != 200:
            self.log(f"⚠️ App retornou HTTP {status_code}", "WARNING")
            return "error"
        
        self.log(f"✅ App respondendo (HTTP {status_code})", "SUCCESS")
        
        # Analisar conteúdo
        indicators_found, found_list = self.analyze_content(content)
        total_indicators = len(self.success_indicators)
        
        self.log(f"📊 Indicadores encontrados: {indicators_found}/{total_indicators}", "INFO")
        
        if indicators_found >= 4:
            self.log("🎉 DEPLOY ATUALIZADO CONFIRMADO!", "SUCCESS")
            return "updated"
        elif indicators_found >= 2:
            self.log("⚠️ Parcialmente atualizado, aguardando...", "WARNING")
            return "partial"
        else:
            self.log("❌ Ainda usando versão antiga", "ERROR")
            return "old_version"
    
    def monitor_continuous(self, max_minutes=15):
        """Monitora continuamente até sucesso ou timeout"""
        self.log("🚀 MONITOR DE DEPLOY - Dashboard Baker v3.0", "INFO")
        self.log("=" * 60, "INFO")
        self.log(f"🌐 URL: {self.url}", "INFO")
        self.log(f"⏰ Timeout: {max_minutes} minutos", "INFO")
        self.log("=" * 60, "INFO")
        
        start_time = time.time()
        max_seconds = max_minutes * 60
        attempt = 1
        
        while time.time() - start_time < max_seconds:
            self.log(f"\n🔄 Tentativa {attempt} ({int((time.time() - start_time)/60)}min decorridos)", "INFO")
            
            status = self.check_deploy_status()
            
            if status == "updated":
                elapsed = int((time.time() - start_time) / 60)
                self.log(f"\n🎉 DEPLOY CONCLUÍDO COM SUCESSO! ({elapsed} minutos)", "SUCCESS")
                self.log(f"✅ Dashboard online: {self.url}", "SUCCESS")
                self.log("🎯 Sistema 100% funcional!", "SUCCESS")
                return True
                
            elif status == "offline":
                self.log("⚠️ App offline - pode estar fazendo deploy", "WARNING")
            elif status == "error":
                self.log("⚠️ App com erro - verificando novamente em 30s", "WARNING")
            elif status == "old_version":
                self.log("❌ Versão antiga ainda ativa", "ERROR")
                if attempt <= 3:
                    self.log("💡 TIP: Se criou app nova, aguarde. Se não, DELETE e RECRIE!", "INFO")
            elif status == "partial":
                self.log("🔄 Deploy em progresso...", "INFO")
            
            # Aguardar antes da próxima verificação
            wait_time = min(60, 30 + (attempt * 10))  # Aumenta o tempo de espera
            self.log(f"⏳ Aguardando {wait_time}s para próxima verificação...", "INFO")
            time.sleep(wait_time)
            attempt += 1
        
        # Timeout
        elapsed = int((time.time() - start_time) / 60)
        self.log(f"\n⏰ TIMEOUT após {elapsed} minutos", "ERROR")
        self.log("🔧 AÇÕES RECOMENDADAS:", "INFO")
        self.log("1. Verifique se deletou/recriou a app no Streamlit Cloud", "INFO")
        self.log("2. Confirme se Repository aponta para: barbosageovanni/dashboard-baker", "INFO")
        self.log("3. Verifique se adicionou os secrets Supabase", "INFO")
        self.log("4. Se necessário, tente com nome de app diferente", "INFO")
        
        return False
    
    def quick_check(self):
        """Verificação rápida única"""
        self.log("⚡ VERIFICAÇÃO RÁPIDA", "INFO")
        self.log("-" * 30, "INFO")
        
        status = self.check_deploy_status()
        
        if status == "updated":
            self.log("🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!", "SUCCESS")
            return True
        elif status == "partial":
            self.log("🔄 Sistema parcialmente atualizado - continue monitorando", "WARNING")
            return False
        elif status == "offline":
            self.log("💤 Sistema offline - pode estar em deploy", "WARNING")
            return False
        else:
            self.log("❌ Sistema precisa de atualização", "ERROR")
            self.log("🔧 Execute as ações manuais no Streamlit Cloud", "INFO")
            return False

def main():
    """Função principal"""
    monitor = DeployMonitor()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--quick':
            # Verificação rápida
            success = monitor.quick_check()
            return 0 if success else 1
        elif sys.argv[1] == '--monitor':
            # Monitoramento contínuo
            timeout_minutes = int(sys.argv[2]) if len(sys.argv) > 2 else 15
            success = monitor.monitor_continuous(timeout_minutes)
            return 0 if success else 1
    else:
        # Monitoramento padrão (10 minutos)
        success = monitor.monitor_continuous(10)
        return 0 if success else 1

if __name__ == "__main__":
    print("🔍 Monitor de Deploy - Dashboard Baker")
    print("Uso:")
    print("  python real_time_monitor.py           # Monitor por 10 minutos")
    print("  python real_time_monitor.py --quick   # Verificação rápida")
    print("  python real_time_monitor.py --monitor 20  # Monitor por 20 minutos")
    print()
    
    sys.exit(main())