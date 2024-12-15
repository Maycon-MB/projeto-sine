from database.connection import DatabaseConnection

class CurriculoModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS curriculos (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100),
            idade INT,
            telefone VARCHAR(20),
            escolaridade VARCHAR(50)
        );
        """
        self.db.execute_query(query)

    def fetch_all_curriculos(self, nome=None, escolaridade=None, idade_min=None, idade_max=None):
        query = "SELECT * FROM curriculos WHERE 1=1"
        params = []

        if nome:
            query += " AND nome ILIKE %s"
            params.append(f"%{nome}%")
        if escolaridade:
            query += " AND escolaridade = %s"
            params.append(escolaridade)
        if idade_min:
            query += " AND idade >= %s"
            params.append(idade_min)
        if idade_max:
            query += " AND idade <= %s"
            params.append(idade_max)

        return self.db.execute_query(query, tuple(params), fetch_all=True)

    def insert_curriculo(self, nome, idade, telefone, escolaridade):
        query = """
        INSERT INTO curriculos (nome, idade, telefone, escolaridade)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
        """
        return self.db.execute_query(query, (nome, idade, telefone, escolaridade), fetch_one=True)
