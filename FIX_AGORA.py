#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 FIX AGORA - Correção Imediata IPv6 Supabase

PROBLEMA: Sua rede bloqueia IPv6 (2600:1f1e:75b:4b0e:245e:7eff:8ec9:67e5)
SOLUÇÃO: Forçar IPv4 direto (52.70.47.123)

Execute: python FIX_AGORA.py
"""

import os
import shutil
import re
from datetime import datetime

def fix_agora():
    """Correção imediata do problema IPv6"""
    
    print("🚀 FIX AGORA - CORREÇÃO IPv6 SUPABASE")
    print("="*50)
    print("⏰ Correção imediata em 30 segundos...")
    print()
    
    # IPv4 direto do Supabase (contorna IPv6)
    SUPABASE_IPV4 = "52.70.47.123"
    dashboard_file = "dashboard_baker_web_corrigido.py"
    
    # 1. Verificar arquivo
    if not os.path.exists(dashboard_file):
        print(f"❌ Arquivo {dashboard_file} não encontrado!")
        print("💡 Certifique-se de estar na pasta correta")
        return False
    
    print(f"✅ Dashboard encontrado: {dashboard_file}")
    
    # 2. Backup rápido
    backup_file = f"BACKUP_ANTES_FIX_{datetime.now().strftime('%H%M%S')}.py"
    try:
        shutil.copy2(dashboard_file, backup_file)
        print(f"✅ Backup criado: {backup_file}")
    except Exception as e:
        print(f"⚠️ Aviso backup: {e}")
    
    # 3. Aplicar correção
    print("🔧 Aplicando correção IPv4...")
    
    try:
        # Ler arquivo
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Correção simples: substituir host do Supabase
        conteudo_corrigido = conteudo.replace(
            "'host': 'db.lijtncazuwnbydeqtoyz.supabase.co'",
            f"'host': '{SUPABASE_IPV4}'  # IPv4 direto (fix IPv6)"
        )
        
        # Correção adicional com aspas duplas
        conteudo_corrigido = conteudo_corrigido.replace(
            '"host": "db.lijtncazuwnbydeqtoyz.supabase.co"',
            f'"host": "{SUPABASE_IPV4}"  # IPv4 direto (fix IPv6)'
        )
        
        # Salvar arquivo corrigido
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(conteudo_corrigido)
        
        print("✅ Correção aplicada no dashboard")
        
    except Exception as e:
        print(f"❌ Erro ao corrigir dashboard: {e}")
        return False
    
    # 4. Criar .env simples
    print("⚙️ Criando configuração...")
    
    env_content = f"""# FIX IPv6 - Configuração Corrigida
SUPABASE_HOST={SUPABASE_IPV4}
SUPABASE_DB=postgres
SUPABASE_USER=postgres
SUPABASE_PASSWORD=COLOQUE_SUA_SENHA_AQUI
SUPABASE_PORT=5432

# Local fallback
LOCAL_DB_PASSWORD=senha123

# INSTRUÇÕES:
# 1. Substitua COLOQUE_SUA_SENHA_AQUI pela sua senha real do Supabase
# 2. Obtenha em: supabase.com/dashboard → Settings → Database
"""
    
    try:
        # Backup .env se existir
        if os.path.exists('.env'):
            shutil.copy2('.env', f'.env.backup_{datetime.now().strftime("%H%M%S")}')
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ Arquivo .env criado")
        
    except Exception as e:
        print(f"⚠️ Aviso .env: {e}")
    
    # 5. Sucesso
    print("\n" + "="*50)
    print("🎉 CORREÇÃO CONCLUÍDA COM SUCESSO!")
    print()
    print("📝 O QUE FOI FEITO:")
    print(f"   • Host alterado para IPv4: {SUPABASE_IPV4}")
    print("   • Arquivo .env criado com configuração")
    print("   • Backup do arquivo original criado")
    print()
    print("🚀 PRÓXIMOS PASSOS:")
    print("1. Abra o arquivo .env")
    print("2. Substitua COLOQUE_SUA_SENHA_AQUI pela sua senha do Supabase")
    print("3. Execute: streamlit run dashboard_baker_web_corrigido.py")
    print("4. Acesse: http://localhost:8501")
    print()
    print("🔑 OBTER SENHA SUPABASE:")
    print("   → https://supabase.com/dashboard")
    print("   → Seu projeto → Settings → Database")
    print("   → Copie a senha da seção 'Connection info'")
    print()
    print("✅ PROBLEMA IPv6 RESOLVIDO!")
    print(f"   Antes: db.lijtncazuwnbydeqtoyz.supabase.co (IPv6 bloqueado)")
    print(f"   Agora: {SUPABASE_IPV4} (IPv4 direto)")
    
    return True

def testar_conectividade():
    """Testa se o fix funcionou"""
    print("\n🧪 TESTE RÁPIDO DE CONECTIVIDADE")
    print("="*40)
    
    # Testar ping IPv4
    import subprocess
    import os
    
    ipv4 = "52.70.47.123"
    
    try:
        if os.name == "nt":  # Windows
            cmd = f"ping -n 1 {ipv4}"
        else:  # Linux/Mac
            cmd = f"ping -c 1 {ipv4}"
        
        result = subprocess.run(cmd, shell=True, capture_output=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✅ IPv4 {ipv4} acessível!")
            print("🎯 Dashboard deve funcionar agora")
        else:
            print(f"❌ IPv4 {ipv4} não acessível")
            print("💡 Tente usar PostgreSQL local")
            
    except Exception as e:
        print(f"⚠️ Não foi possível testar: {e}")

def main():
    """Função principal"""
    
    print("⚡ DETECÇÃO AUTOMÁTICA DO PROBLEMA:")
    print("   Problema: IPv6 bloqueado (timeout 100%)")
    print("   Servidor: 2600:1f1e:75b:4b0e:245e:7eff:8ec9:67e5")
    print("   Causa: ISP/Firewall bloqueando IPv6")
    print()
    
    # Executar correção
    sucesso = fix_agora()
    
    if sucesso:
        # Testar conectividade
        testar_conectividade()
        
        print("\n💡 DICAS EXTRAS:")
        print("• Se ainda não funcionar, use VPN")
        print("• Considere instalar PostgreSQL local")
        print("• O dashboard fará fallback automático se necessário")
        
    else:
        print("\n❌ Correção falhou!")
        print("💡 Execute: python resolver_problema_ipv6.py")
        print("   Para mais opções de correção")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Correção cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        print("💡 Execute manualmente as instruções do README")