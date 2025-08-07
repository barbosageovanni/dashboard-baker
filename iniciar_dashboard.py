#!/usr/bin/env python3
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
        print("\n👋 Dashboard encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
