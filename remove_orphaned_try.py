import shutil
from datetime import datetime

def remove_orphaned_try():
    # Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"dashboard_baker_web_corrigido.py.backup_remove_try_{timestamp}"
    shutil.copy("dashboard_baker_web_corrigido.py", backup_name)
    print(f"✅ Backup criado: {backup_name}")
    
    # Ler arquivo
    with open('dashboard_baker_web_corrigido.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Remover a linha 406 que contém 'try:' órfão
    if len(lines) > 405 and lines[405].strip() == 'try:':
        lines.pop(405)  # Remove linha 406 (índice 405)
        print("✅ Removido 'try:' órfão da linha 406")
        
        # Corrigir indentação das linhas subsequentes
        # Remover indentação extra das linhas 407-412 (agora 406-411)
        corrections = []
        for i in range(405, min(len(lines), 415)):
            line = lines[i]
            if line.startswith('        '):  # 8 espaços
                lines[i] = line[4:]  # Remover 4 espaços
                corrections.append(f"Corrigida indentação da linha {i+1}")
            elif line.startswith('    ') and i > 405:  # 4 espaços, mas não linha vazia
                if line.strip():  # Se não é linha vazia
                    lines[i] = line  # Manter como está
        
        print(f"✅ {len(corrections)} correções de indentação aplicadas")
    
    # Escrever arquivo corrigido
    with open('dashboard_baker_web_corrigido.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Arquivo corrigido!")

if __name__ == "__main__":
    print("🔧 Removendo try órfão...")
    
    remove_orphaned_try()
    
    print("\n🔍 Verificando sintaxe...")
    
    # Verificar sintaxe
    import subprocess
    try:
        result = subprocess.run(['python', '-m', 'py_compile', 'dashboard_baker_web_corrigido.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ SUCESSO! Try órfão removido - sintaxe válida.")
        else:
            print(f"❌ Ainda há problemas: {result.stderr}")
    except Exception as e:
        print(f"❌ Erro ao verificar sintaxe: {e}")
