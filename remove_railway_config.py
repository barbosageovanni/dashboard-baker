import shutil
from datetime import datetime

def remove_railway_and_fix_structure():
    """Remove Railway e corrige estrutura do código"""
    
    # Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"dashboard_baker_web_corrigido.py.backup_remove_railway_{timestamp}"
    shutil.copy("dashboard_baker_web_corrigido.py", backup_name)
    print(f"✅ Backup criado: {backup_name}")
    
    # Ler arquivo
    with open('dashboard_baker_web_corrigido.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substituir a função carregar_configuracao_banco inteira
    new_function = '''def carregar_configuracao_banco():
    """Carrega configuração do banco com sistema de fallback inteligente - SEM RAILWAY"""
    
    if not PSYCOPG2_AVAILABLE:
        st.error("❌ psycopg2-binary não encontrado. Execute: pip install psycopg2-binary")
        st.stop()
    
    # Carregar variáveis de ambiente
    _carregar_dotenv()
    
    # Detectar e usar configuração adequada
    ambiente = _detectar_ambiente()
    
    if ambiente == 'supabase':
        config = _config_supabase()
        if _testar_conexao(config):
            return config
    
    elif ambiente == 'render':
        config = _config_render()
        if _testar_conexao(config):
            return config
    
    # Fallback para local
    return _config_local()'''

    # Encontrar e substituir a função atual
    import re
    
    # Padrão para encontrar a função carregar_configuracao_banco
    pattern = r'def carregar_configuracao_banco\(\):.*?(?=\n\ndef|\nclass|\n# =|$)'
    
    # Substituir a função
    content = re.sub(pattern, new_function, content, flags=re.DOTALL)
    
    # Remover função _config_railway
    railway_pattern = r'def _config_railway\(\):.*?(?=\n\ndef|\nclass|\n# =|$)'
    content = re.sub(railway_pattern, '', content, flags=re.DOTALL)
    
    # Atualizar função _detectar_ambiente para remover Railway
    new_detectar = '''def _detectar_ambiente():
    """Detecta ambiente atual - SEM RAILWAY"""
    if os.getenv('DATABASE_URL'):
        return 'render'
    elif os.getenv('SUPABASE_HOST') and os.getenv('SUPABASE_PASSWORD'):
        return 'supabase'
    else:
        return 'local\''''
    
    detectar_pattern = r'def _detectar_ambiente\(\):.*?(?=\n\ndef|\nclass|\n# =|$)'
    content = re.sub(detectar_pattern, new_detectar, content, flags=re.DOTALL)
    
    # Escrever arquivo corrigido
    with open('dashboard_baker_web_corrigido.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Railway removido e estrutura corrigida!")
    
    return True

if __name__ == "__main__":
    print("🔧 Removendo Railway e corrigindo estrutura...")
    
    if remove_railway_and_fix_structure():
        print("\n🔍 Verificando sintaxe após remoção do Railway...")
        
        # Verificar sintaxe
        import subprocess
        try:
            result = subprocess.run(['python', '-m', 'py_compile', 'dashboard_baker_web_corrigido.py'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ SUCESSO! Railway removido - sintaxe válida.")
            else:
                print(f"❌ Ainda há problemas: {result.stderr}")
        except Exception as e:
            print(f"❌ Erro ao verificar sintaxe: {e}")
