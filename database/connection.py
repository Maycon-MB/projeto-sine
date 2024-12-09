import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="seu_banco",
        user="seu_usuario",
        password="sua_senha",
        host="localhost",
        port=5432
    )
