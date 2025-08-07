#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correção Específica para Conexão Supabase
Diagnostica e corrige problemas de conectividade com Supabase PostgreSQL

Execute: python fix_supabase_connection.py
"""

import os
import socket
import psycopg2
import time
from datetime import datetime
import subprocess
import sys

class FixSupabase:
    """Diagnóstico e correção para problemas Supabase"""
    
    def __init__(self):
        self.supabase_host = "db.lijtncazuwnbydeqtoyz.supabase.co"
        self.supabase_port = 5432
        self.resultados = {}
    
    def teste_conectividade_rede(self):
        """Testa conectividade básica de rede"""
        print("🌐 Testando conectividade de rede...")
        
        try:
            # Teste de resolução DNS
            import socket
            ip = socket.gethostbyname(self.supabase_host)
            print(f"✅ DNS OK: {self.supabase_host} → {ip}")
            self.resultados['dns'] = True
            
            # Teste de ping
            if os.name == "nt":  # Windows
                ping_cmd = f"ping -n 1 {self.supabase_host}"
            else:  # Linux/Mac
                ping_cmd = f"ping -c 1 {self.supabase_host}"
            
            result = subprocess.run(ping_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Ping OK: Servidor acessível")
                self.resultados['ping'] = True
            else:
                print("❌ Ping FALHOU: Possível problema de rede/firewall")
                self.resultados['ping'] = False
            
            # Teste de porta TCP
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            result = sock.connect_ex((ip, self.supabase_port))
            sock.close()
            
            if result == 0:
                print(f"✅ Porta {self.supabase_port} ABERTA")
                self.resultados['porta'] = True
            else:
                print(f"❌ Porta {self.supabase_port} FECHADA ou BLOQUEADA")
                self.resultados['porta'] = False
                
        except socket.gaierror:
            print("❌ DNS FALHOU: Não foi possível resolver o hostname")
            self.resultados['dns'] = False
        except Exception as e:
            print(f"❌ Erro de rede: {e}")
            self.resultados['rede'] = False
    
    def teste_credenciais_supabase(self):
        """Testa diferentes combinações de credenciais"""
        print("\n🔐 Testando credenciais Supabase...")
        
        # Possíveis combinações de credenciais
        credenciais_teste = [
            {
                'host': self.supabase_host,
                'database': 'postgres',
                'user': 'postgres',
                'password': os.getenv('SUPABASE_PASSWORD', ''),
                'port': 5432,
                'sslmode': 'require'
            },
            # Outras variações comuns
            {
                'host': self.supabase_host,
                'database': 'postgres',
                'user': 'postgres.lijtncazuwnbydeqtoyz',  # Formato alternativo
                'password': os.getenv('SUPABASE_PASSWORD', ''),
                'port': 5432,
                'sslmode': 'require'
            }
        ]
        
        for i, cred in enumerate(credenciais_teste, 1):
            if not cred['password']:
                print(f"⚠️ Teste {i}: Senha não configurada")
                continue
                
            print(f"🔍 Teste {i}: {cred['user']}@{cred['host']}")
            
            try:
                conn = psycopg2.connect(**cred)
                cursor = conn.cursor()
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                cursor.close()
                conn.close()
                
                print(f"✅ SUCESSO! Conectado com credenciais do teste {i}")
                print(f"📊 PostgreSQL: {version[:50]}...")
                self.resultados['auth'] = True
                return cred
                
            except psycopg2.OperationalError as e:
                error_msg = str(e)
                if "authentication failed" in error_msg:
                    print(f"❌ Teste {i}: Credenciais inválidas")
                elif "Cannot assign requested address" in error_msg:
                    print(f"❌ Teste {i}: Problema de rede (endereço)")
                elif "Connection refused" in error_msg:
                    print(f"❌ Teste {i}: Conexão recusada")
                else:
                    print(f"❌ Teste {i}: {error_msg[:80]}...")
                    
            except Exception as e:
                print(f"❌ Teste {i}: Erro - {str(e)[:80]}...")
        
        print("❌ Todos os testes de credenciais falharam")
        self.resultados['auth'] = False
        return None
    
    def verificar_configuracao_local(self):
        """Verifica configuração local do sistema"""
        print("\n🖥️ Verificando configuração local...")
        
        # Verificar bibliotecas Python
        try:
            import psycopg2
            print(f"✅ psycopg2 instalado: v{psycopg2.__version__}")
        except ImportError:
            print("❌ psycopg2 NÃO instalado")
            print("💡 Execute: pip install psycopg2-binary")
            return False
        
        # Verificar arquivo .env
        if os.path.exists('.env'):
            print("✅ Arquivo .env encontrado")
            
            with open('.env', 'r') as f:
                env_content = f.read()
                
            if 'SUPABASE_PASSWORD' in env_content:
                if os.getenv('SUPABASE_PASSWORD'):
                    print("✅ SUPABASE_PASSWORD configurado")
                else:
                    print("❌ SUPABASE_PASSWORD vazio ou não carregado")
            else:
                print("❌ SUPABASE_PASSWORD não encontrado no .env")
        else:
            print("❌ Arquivo .env não encontrado")
            return False
        
        # Verificar proxy/firewall
        http_proxy = os.getenv('HTTP_PROXY') or os.getenv('http_proxy')
        https_proxy = os.getenv('HTTPS_PROXY') or os.getenv('https_proxy')
        
        if http_proxy or https_proxy:
            print(f"⚠️ Proxy detectado: HTTP={http_proxy}, HTTPS={https_proxy}")
            print("💡 Proxies podem bloquear conexões PostgreSQL")
        else:
            print("✅ Nenhum proxy detectado")
        
        return True
    
    def gerar_solucoes(self):
        """Gera soluções baseadas nos resultados dos testes"""
        print("\n" + "="*50)
        print("💡 SOLUÇÕES RECOMENDADAS")
        print("="*50)
        
        if not self.resultados.get('dns', True):
            print("\n🌐 PROBLEMA DE DNS:")
            print("• Verifique sua conexão com a internet")
            print("• Tente usar DNS público: 8.8.8.8, 1.1.1.1")
            print("• Execute: nslookup db.lijtncazuwnbydeqtoyz.supabase.co")
        
        if not self.resultados.get('ping', True):
            print("\n🔥 PROBLEMA DE FIREWALL/REDE:")
            print("• Desative temporariamente o firewall para teste")
            print("• Verifique se seu provedor bloqueia porta 5432")
            print("• Use VPN se estiver em rede corporativa")
            print("• Teste de outra rede (mobile hotspot)")
        
        if not self.resultados.get('porta', True):
            print("\n🚪 PROBLEMA DE PORTA:")
            print("• Porta 5432 está bloqueada")
            print("• Configure firewall para permitir saída na porta 5432")
            print("• Teste com telnet: telnet db.lijtncazuwnbydeqtoyz.supabase.co 5432")
        
        if not self.resultados.get('auth', True):
            print("\n🔐 PROBLEMA DE CREDENCIAIS:")
            print("• Verifique senha no painel Supabase:")
            print("  1. Acesse https://supabase.com/dashboard")
            print("  2. Vá em Settings → Database")
            print("  3. Copie as credenciais corretas")
            print("• Atualize arquivo .env com senha correta")
            print("• Verifique se não expirou o token/senha")
        
        print("\n🔄 ALTERNATIVAS:")
        print("• Use PostgreSQL local temporariamente")
        print("• Considere Railway, Render ou outro provedor")
        print("• Configure túnel SSH se disponível")
        
        print("\n📝 CONFIGURAÇÃO ALTERNATIVA:")
        print("Crie arquivo 'config_local.py' com:")
        print("""
config = {
    'host': 'localhost',
    'database': 'dashboard_baker',
    'user': 'postgres', 
    'password': 'senha123',
    'port': 5432
}
""")
    
    def criar_config_fallback(self):
        """Cria configuração de fallback local"""
        
        config_fallback = '''# Configuração de fallback - PostgreSQL Local
# Use este arquivo se Supabase não funcionar

import os

def get_database_config():
    """Retorna configuração do banco local"""
    
    # Primeiro, tenta Supabase se credenciais disponíveis
    supabase_password = os.getenv('SUPABASE_PASSWORD')
    
    if supabase_password:
        supabase_config = {
            'host': 'db.lijtncazuwnbydeqtoyz.supabase.co',
            'database': 'postgres',
            'user': 'postgres',
            'password': supabase_password,
            'port': 5432,
            'sslmode': 'require',
            'connect_timeout': 10
        }
        
        # Testar conexão Supabase
        try:
            import psycopg2
            conn = psycopg2.connect(**supabase_config)
            conn.close()
            print("✅ Usando Supabase PostgreSQL")
            return supabase_config
        except:
            print("⚠️ Supabase falhou, usando PostgreSQL local")
    
    # Fallback para PostgreSQL local
    local_config = {
        'host': 'localhost',
        'database': 'dashboard_baker',
        'user': 'postgres',
        'password': 'senha123',
        'port': 5432
    }
    
    print("✅ Usando PostgreSQL local")
    return local_config
'''
        
        try:
            with open('config_fallback.py', 'w', encoding='utf-8') as f:
                f.write(config_fallback)
            print("\n✅ Arquivo config_fallback.py criado!")
            print("💡 Importe este arquivo no dashboard se necessário")
        except Exception as e:
            print(f"❌ Erro ao criar config_fallback.py: {e}")
    
    def executar_diagnostico_completo(self):
        """Executa diagnóstico completo"""
        
        print("🔍 DIAGNÓSTICO SUPABASE POSTGRESQL")
        print("="*50)
        print(f"Host: {self.supabase_host}")
        print(f"Porta: {self.supabase_port}")
        print(f"Timestamp: {datetime.now()}")
        print()
        
        # 1. Verificar configuração local
        if not self.verificar_configuracao_local():
            print("❌ Configuração local inválida, parando diagnóstico")
            return
        
        # 2. Testar conectividade
        self.teste_conectividade_rede()
        
        # 3. Testar credenciais (só se rede OK)
        if self.resultados.get('dns', False) and self.resultados.get('porta', False):
            credenciais_funcionais = self.teste_credenciais_supabase()
            
            if credenciais_funcionais:
                print("\n🎉 PROBLEMA RESOLVIDO!")
                print("✅ Conexão Supabase funcionando")
                return credenciais_funcionais
        
        # 4. Gerar soluções
        self.gerar_solucoes()
        
        # 5. Criar fallback
        self.criar_config_fallback()
        
        return None

def main():
    """Função principal"""
    
    # Carregar .env se existir
    if os.path.exists('.env'):
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            # Carregar manualmente se python-dotenv não disponível
            with open('.env', 'r') as f:
                for linha in f:
                    linha = linha.strip()
                    if linha and not linha.startswith('#') and '=' in linha:
                        chave, valor = linha.split('=', 1)
                        os.environ[chave] = valor
    
    # Executar diagnóstico
    fix_supabase = FixSupabase()
    resultado = fix_supabase.executar_diagnostico_completo()
    
    if resultado:
        print("\n✅ Use estas credenciais no seu dashboard:")
        for key, value in resultado.items():
            if key != 'password':
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: {'*' * len(str(value))}")
    else:
        print("\n❌ Problema não resolvido automaticamente")
        print("📞 Entre em contato com suporte Supabase se problema persistir")

if __name__ == "__main__":
    main()