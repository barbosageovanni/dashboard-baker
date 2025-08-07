FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
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

# Instalar dependências Python
RUN pip3 install -r requirements.txt

# Expor porta
EXPOSE 8501

# Verificar saúde da aplicação  
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Executar aplicação
ENTRYPOINT ["streamlit", "run", "dashboard_baker_web_corrigido.py", "--server.port=8501", "--server.address=0.0.0.0"]
