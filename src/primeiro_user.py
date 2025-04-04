import bcrypt
from database.connection import DatabaseConnection

# Conexão com o banco de dados
db = DatabaseConnection(
    dbname="railway",
    user="postgres",
    password="uWPKHDpcpasSjFargPviuNZXpgBXqpxT",
    host="shuttle.proxy.rlwy.net",
    port='31029'
)

def buscar_cidade_id(cidade_nome):
    """
    Busca o ID da cidade pelo nome na tabela 'cidades'.
    """
    query = "SELECT id FROM cidades WHERE nome = %s;"
    result = db.execute_query(query, (cidade_nome.upper(),), fetch_one=True)
    if not result:
        raise ValueError(f"Cidade '{cidade_nome}' não encontrada no banco de dados.")
    return result['id']

def criar_primeiro_usuario():
    usuario = "MAYCON"
    email = "mayconbruno.dev@gmail.com"
    senha = "admin"  # Defina uma senha segura
    cidade = "Nilópolis"

    # 🔍 Verifica se o usuario já existe
    check_query = "SELECT id FROM usuarios WHERE usuario = %s OR email = %s;"
    existing_user = db.execute_query(check_query, (usuario.upper(), email), fetch_one=True)

    if existing_user:
        print(f"⚠️ Usuário '{usuario}' ou e-mail '{email}' já existe. ID: {existing_user['id']}")
        return

    # 🔒 Criptografa a senha
    senha = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

    try:
        # 🔎 Busca o ID da cidade
        cidade_id = buscar_cidade_id(cidade)

        # 📥 Insere o usuario no banco
        insert_query = """
        INSERT INTO usuarios (usuario, senha, email, cidade_id)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
        """
        result = db.execute_query(insert_query, (usuario.upper(), senha, email, cidade_id), fetch_one=True)
        print(f"✅ Usuário criado com sucesso! ID: {result['id']}")
    except ValueError as ve:
        print(f"❌ Erro: {ve}")
    except Exception as e:
        print(f"❌ Erro ao criar o usuario: {e}")

# 🚀 Executa a criação do admin
criar_primeiro_usuario()
