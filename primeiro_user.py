import bcrypt
from database.connection import DatabaseConnection

# Conexão com o banco de dados
db = DatabaseConnection(
    dbname="projeto_sine",
    user="postgres",
    password="teste",  # Altere se necessário
    host="192.168.1.213"
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

def criar_primeiro_admin():
    usuario = "MAYCON"
    email = "mayconbruno.dev@gmail.com"
    senha = "admin"  # Defina uma senha segura
    cidade = "Nilópolis"
    tipo_usuario = "master"

    # 🔍 Verifica se o admin já existe
    check_query = "SELECT id FROM usuarios WHERE usuario = %s OR email = %s;"
    existing_user = db.execute_query(check_query, (usuario.upper(), email.upper()), fetch_one=True)

    if existing_user:
        print(f"⚠️ Usuário '{usuario}' ou e-mail '{email}' já existe. ID: {existing_user['id']}")
        return

    # 🔒 Criptografa a senha
    senha = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

    try:
        # 🔎 Busca o ID da cidade
        cidade_id = buscar_cidade_id(cidade)

        # 📥 Insere o admin no banco
        insert_query = """
        INSERT INTO usuarios (usuario, senha, email, cidade_id, tipo_usuario)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
        """
        result = db.execute_query(insert_query, (usuario.upper(), senha, email.upper(), cidade_id, tipo_usuario), fetch_one=True)
        print(f"✅ Usuário admin criado com sucesso! ID: {result['id']}")
    except ValueError as ve:
        print(f"❌ Erro: {ve}")
    except Exception as e:
        print(f"❌ Erro ao criar o admin: {e}")

# 🚀 Executa a criação do admin
criar_primeiro_admin()
