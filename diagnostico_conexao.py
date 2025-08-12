#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico de Conexão PostgreSQL/Supabase
Identifica problemas de conectividade e sugere soluções
"""

import os
import sys
import socket
import json
from datetime import datetime

def carregar_env():
    """Carrega variáveis do arquivo .env"""
    env_vars = {}
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                if linha and not linha.startswith('#') and '=' in linha:
                    chave, valor = linha.split('=', 1)
                    valor = valor.strip().strip('"').strip("'")
                    env_vars[chave] = valor
                    os.environ[chave] = valor
    return env_vars

def testar_conectividade_basica(host, port=5432):
    """Testa conectividade TCP básica"""
    try:
        sock = socket.create_connection((host, port), timeout=10)
        sock.close()
        return True, "Conectividade TCP OK"
    except socket.timeout:
        return False, "Timeout - Porta pode estar bloqueada"
    except socket.gaierror:
        return False, "Erro DNS - Host não encontrado"
    except ConnectionRefusedError:
        return False, "Conexão recusada - Serviço inativo"
    except Exception as e:
        return False, f"Erro: {str(e)}"

def testar_psycopg2():
    """Testa se psycopg2 está instalado e funcionando"""
    try:
        import psycopg2
        return True, f"psycopg2 versão: {psycopg2.__version__}"
    except ImportError:
        return False, "psycopg2-binary não instalado"
    except Exception as e:
        return False, f"Erro: {str(e)}"

def testar_conexao_postgresql(config):
    """Testa conexão PostgreSQL com diferentes configurações"""
    try:
        import psycopg2
        
        # Tenta diferentes configurações SSL
        ssl_modes = ['require', 'prefer', 'allow', 'disable']
        
        for ssl_mode in ssl_modes:
            try:
                test_config = config.copy()
                test_config['sslmode'] = ssl_mode
                test_config['connect_timeout'] = 30
                
                conn = psycopg2.connect(**test_config)
                cursor = conn.cursor()
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                cursor.close()
                conn.close()
                
                return True, f"Conexão OK com sslmode={ssl_mode}, PostgreSQL: {version[:50]}..."
                
            except Exception as e:
                if ssl_mode == ssl_modes[-1]:  # Último modo, retorna erro
                    return False, f"Falhou com todos os SSL modes. Último erro: {str(e)}"
                continue
                
    except ImportError:
        return False, "psycopg2-binary não disponível"
    except Exception as e:
        return False, f"Erro geral: {str(e)}"

def detectar_ambiente():
    """Detecta o ambiente de execução"""
    if 'CODESPACE_NAME' in os.environ:
        return "GitHub Codespaces"
    elif 'RAILWAY_ENVIRONMENT' in os.environ:
        return "Railway"
    elif 'RENDER' in os.environ:
        return "Render"
    elif 'DYNO' in os.environ:
        return "Heroku"
    elif os.path.exists('/.dockerenv'):
        return "Docker Container"
    else:
        return "Ambiente Local"

def diagnosticar():
    """Executa diagnóstico completo"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE CONEXÃO POSTGRESQL/SUPABASE")
    print("=" * 60)
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Detectar ambiente
    ambiente = detectar_ambiente()
    print(f"🌍 Ambiente: {ambiente}")
    print()
    
    # Carregar variáveis
    print("📂 Carregando variáveis de ambiente...")
    env_vars = carregar_env()
    
    supabase_vars = {k: v for k, v in env_vars.items() if k.startswith('SUPABASE')}
    if supabase_vars:
        print("✅ Variáveis Supabase encontradas:")
        for k, v in supabase_vars.items():
            valor_exibido = "***" if "password" in k.lower() else v
            print(f"   {k}={valor_exibido}")
    else:
        print("❌ Nenhuma variável Supabase encontrada")
    print()
    
    # Testar psycopg2
    print("🐍 Testando psycopg2...")
    pg_ok, pg_msg = testar_psycopg2()
    print(f"{'✅' if pg_ok else '❌'} {pg_msg}")
    print()
    
    # Testar conectividade básica
    host = env_vars.get('SUPABASE_HOST')
    if host:
        print(f"🔌 Testando conectividade TCP com {host}:5432...")
        tcp_ok, tcp_msg = testar_conectividade_basica(host)
        print(f"{'✅' if tcp_ok else '❌'} {tcp_msg}")
        print()
        
        # Testar conexão PostgreSQL
        if pg_ok and tcp_ok:
            print("🐘 Testando conexão PostgreSQL...")
            config = {
                'host': host,
                'database': env_vars.get('SUPABASE_DB', 'postgres'),
                'user': env_vars.get('SUPABASE_USER', 'postgres'),
                'password': env_vars.get('SUPABASE_PASSWORD'),
                'port': int(env_vars.get('SUPABASE_PORT', '5432'))
            }
            
            if config['password']:
                db_ok, db_msg = testar_conexao_postgresql(config)
                print(f"{'✅' if db_ok else '❌'} {db_msg}")
            else:
                print("❌ SUPABASE_PASSWORD não encontrada")
        print()
    else:
        print("❌ SUPABASE_HOST não encontrado")
        print()
    
    # Recomendações
    print("💡 RECOMENDAÇÕES:")
    print("-" * 60)
    
    if ambiente == "GitHub Codespaces":
        print("⚠️  GitHub Codespaces pode ter restrições de rede para bancos externos")
        print("✅ Solução 1: Use para desenvolvimento local apenas")
        print("✅ Solução 2: Deploy direto no Streamlit Cloud/Railway")
        print("✅ Solução 3: Use simulação de dados para desenvolvimento")
    
    if not pg_ok:
        print("📦 Execute: pip install psycopg2-binary")
    
    if host and not tcp_ok:
        print("🔥 Problemas de conectividade detectados:")
        print("   • Firewall pode estar bloqueando porta 5432")
        print("   • Ambiente pode ter restrições de rede")
        print("   • Considere usar pooling de conexão ou proxy")
    
    if not supabase_vars:
        print("📝 Configure as variáveis de ambiente no .env:")
        print("   SUPABASE_HOST=seu_host.supabase.co")
        print("   SUPABASE_PASSWORD=sua_senha")
    
    print()
    print("🚀 PARA DEPLOY EM PRODUÇÃO:")
    print("-" * 60)
    print("✅ Streamlit Cloud: Funciona perfeitamente com Supabase")
    print("✅ Railway: Conexão estável com PostgreSQL")
    print("✅ Render: Suporte nativo para PostgreSQL")
    print("⚠️  Heroku: Funciona mas pode ter limitações")
    print()
    
    return {
        'ambiente': ambiente,
        'psycopg2_ok': pg_ok,
        'tcp_ok': tcp_ok if host else False,
        'supabase_vars': bool(supabase_vars),
        'timestamp': datetime.now().isoformat()
    }

def main():
    """Função principal"""
    resultado = diagnosticar()
    
    # Salvar resultado
    with open('diagnostico_resultado.json', 'w', encoding='utf-8') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    
    print("💾 Resultado salvo em: diagnostico_resultado.json")
    print()
    
    # Sugestão final
    if resultado['ambiente'] == "GitHub Codespaces":
        print("🎯 SOLUÇÃO RECOMENDADA PARA CODESPACES:")
        print("1. Use modo de desenvolvimento com dados simulados")
        print("2. Faça deploy direto no Streamlit Cloud para produção") 
        print("3. Configure as secrets no Streamlit Cloud, não no Codespaces")
    
if __name__ == "__main__":
    main()
