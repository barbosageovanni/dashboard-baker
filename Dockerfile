FROM python:3.11-slim

WORKDIR /app

# Instalar depend�ncias do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos
COPY requirements.txt .
COPY dashboard_baker_web_corrigido.py .
COPY inicializar_banco_deploy.py .
COPY .streamlit/ .streamlit/

# Instalar depend�ncias Python
RUN pip3 install -r requirements.txt

# Expor porta
EXPOSE 8501

# Verificar sa�de da aplica��o  
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Executar aplica��o
ENTRYPOINT ["streamlit", "run", "dashboard_baker_web_corrigido.py", "--server.port=8501", "--server.address=0.0.0.0"]
