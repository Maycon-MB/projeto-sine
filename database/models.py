from database.connection import get_connection

def criar_usuario(nome, email, senha, is_admin=False):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO usuarios (nome, email, senha, is_admin)
        VALUES (%s, %s, %s, %s)
        """,
        (nome, email, senha, is_admin)
    )
    conn.commit()
    cursor.close()
    conn.close()

def listar_usuarios():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email, is_admin FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return usuarios
