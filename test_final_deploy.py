import requests
import time

def test_final_deploy():
    url = "https://dashboard-transpontual.streamlit.app/"
    print("🧪 Testando deploy final...")
    
    for i in range(5):
        try:
            response = requests.get(url, timeout=30)
            content = response.text
            
            # Verificar indicadores de versão atualizada
            updated_indicators = [
                "Dashboard Financeiro Baker - Sistema Avançado",
                "v3.0",
                "PostgreSQL",
                "389"  # Número de registros que sabemos que tem
            ]
            
            found = sum(1 for indicator in updated_indicators if indicator in content)
            
            print(f"Tentativa {i+1}/5:")
            print(f"  Status: {response.status_code}")
            print(f"  Indicadores encontrados: {found}/4")
            
            if found >= 3:
                print("✅ DEPLOY ATUALIZADO CONFIRMADO!")
                return True
            else:
                print("⚠️ Ainda carregando versão antiga...")
                time.sleep(60)  # Aguardar 1 minuto
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            time.sleep(30)
    
    print("❌ Deploy não atualizou - use OPÇÃO 1 (deletar/recriar)")
    return False

# Executar teste
test_final_deploy()