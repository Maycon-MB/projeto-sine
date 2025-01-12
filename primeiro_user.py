import bcrypt
from database.connection import DatabaseConnection

# Conexão com o banco de dados
db = DatabaseConnection(
    dbname="projeto_sine",
    user="postgres",
    password="admin",  # Altere se necessário
    host="localhost"
)

def criar_primeiro_admin():
    usuario = "Maycon"
    email = "mayconbruno.dev@gmail.com"
    senha = "admin"  # Defina uma senha segura
    cidade = "Nilópolis"
    tipo_usuario = "master"

    # 🔍 Verifica se o admin já existe
    check_query = "SELECT id FROM usuarios WHERE usuario = %s OR email = %s;"
    existing_user = db.execute_query(check_query, (usuario, email), fetch_one=True)

    if existing_user:
        print(f"⚠️ Usuário '{usuario}' ou e-mail '{email}' já existe. ID: {existing_user['id']}")
        return

    # 🔒 Criptografa a senha
    senha = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

    # 📥 Insere o admin no banco
    insert_query = """
    INSERT INTO usuarios (usuario, senha, email, cidade, tipo_usuario)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id;
    """
    
    try:
        result = db.execute_query(insert_query, (usuario, senha, email, cidade, tipo_usuario), fetch_one=True)
        print(f"✅ Usuário admin criado com sucesso! ID: {result['id']}")
    except Exception as e:
        print(f"❌ Erro ao criar o admin: {e}")

# 🚀 Executa a criação do admin
criar_primeiro_admin()
