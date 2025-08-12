#!/bin/bash

clear

echo "🚀 DASHBOARD FINANCEIRO BAKER v3.0"
echo "================================"
echo ""
echo "🔄 Iniciando sistema..."
echo ""

# Verificar se arquivo existe
if [ ! -f "dashboard_baker_web_corrigido.py" ]; then
    echo "❌ Arquivo dashboard_baker_web_corrigido.py não encontrado!"
    echo ""
    echo "💡 Certifique-se que este script está na mesma pasta do dashboard"
    exit 1
fi

echo "✅ Arquivo dashboard encontrado"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não está instalado"
    echo ""
    echo "💡 Instale Python3: sudo apt install python3 python3-pip"
    exit 1
fi

echo "✅ Python disponível"
echo ""

# Verificar Streamlit
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "❌ Streamlit não está instalado"
    echo ""
    echo "🔧 Instalando Streamlit..."
    pip3 install streamlit
    
    if [ $? -ne 0 ]; then
        echo "❌ Falha na instalação do Streamlit"
        exit 1
    fi
fi

echo "✅ Streamlit disponível"
echo ""

# Executar dashboard
echo "🌐 Iniciando Dashboard Baker..."
echo ""
echo "⚠️  IMPORTANTE:"
echo "   • Mantenha este terminal aberto"
echo "   • Dashboard abrirá no navegador"
echo "   • Para parar: Pressione Ctrl+C"
echo ""
echo "🌐 Acesse: http://localhost:8501"
echo ""

python3 -m streamlit run dashboard_baker_web_corrigido.py

echo ""
echo "👋 Dashboard encerrado."
