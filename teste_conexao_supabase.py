import psycopg2

# Credenciais do Supabase
HOST = "db.lijtncazuwnbydeqtoyz.supabase.co"
DBNAME = "postgres"
USER = "postgres"
PASSWORD = "Mariaana953@7334"
PORT = 5432
SSLMODE = "require"

try:
    print("🔄 Tentando conectar ao banco Supabase...")
    conn = psycopg2.connect(
        host=HOST,
        dbname=DBNAME,
        user=USER,
        password=PASSWORD,
        port=PORT,
        sslmode=SSLMODE
    )
    print("✅ Conexão bem-sucedida!")
    
    # Teste simples: pegar versão do Postgres
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print("📦 Versão do Postgres:", version[0])
    
    cur.close()
    conn.close()
    print("🔌 Conexão fechada com sucesso.")

except Exception as e:
    print("❌ Erro ao conectar:", e)
